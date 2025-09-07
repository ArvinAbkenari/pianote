from django.shortcuts import render, redirect
from users.forms import UserSignupForm
from .forms import AudioUploadForm, ExerciseCreateForm
from django.http import JsonResponse
import os
import librosa
import numpy as np
from users.views import session_login_required
from scipy.spatial.distance import cosine
from scipy.signal import butter, filtfilt
from .models import Exercise
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import io
from django.utils import timezone


REFERENCE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'notes',
    'media',
    'reference_audio'
)
os.makedirs(REFERENCE_DIR, exist_ok=True)


# ---------- New logic functions ----------


def preprocess_audio(y, sr, target_sr=22050):
    if y.ndim > 1:
        y = librosa.to_mono(y)
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr

    def butter_bandpass(lowcut, highcut, fs, order=4):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    b, a = butter_bandpass(80, 4000, sr)
    y = filtfilt(b, a, y)
    y, _ = librosa.effects.trim(y, top_db=20)
    y = librosa.util.normalize(y)
    max_len = 60000
    if len(y) < max_len:
        y = np.pad(y, (0, max_len - len(y)))
    else:
        y = y[:max_len]
    return y, sr


def extract_pitch(y, sr):
    y, sr = preprocess_audio(y, sr)
    pitches = librosa.yin(
        y,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7')
    )
    voiced_flag = pitches > 0
    return pitches, voiced_flag


def extract_energy(y, frame_length=2048, hop_length=512):
    return librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]


def extract_advanced_features(y, sr):
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    tonnetz_feat = librosa.feature.tonnetz(
        y=librosa.effects.harmonic(y),
        sr=sr
    )
    return {
        'mfccs': np.mean(mfccs, axis=1),
        'chroma': np.mean(chroma, axis=1),
        'contrast': np.mean(contrast, axis=1),
        'tonnetz': np.mean(tonnetz_feat, axis=1)
    }


def load_and_extract_features(file_path):
    y, sr = librosa.load(file_path, sr=None)
    pitches, voiced_flag = extract_pitch(y, sr)
    energy = extract_energy(y)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    advanced = extract_advanced_features(y, sr)
    return {
        'y': y,
        'sr': sr,
        'pitches': pitches,
        'voiced_flag': voiced_flag,
        'energy': energy,
        'tempo': tempo,
        'mfccs': advanced['mfccs'],
        'chroma': advanced['chroma'],
        'contrast': advanced['contrast'],
        'tonnetz': advanced['tonnetz']
    }


def pitch_histogram(pitches, bins=36):
    pitches = pitches[np.isfinite(pitches) & (pitches > 0)]
    midi = librosa.hz_to_midi(pitches)
    hist, _ = np.histogram(midi, bins=bins, range=(21, 108))
    hist = hist / np.sum(hist) if np.sum(hist) > 0 else hist
    return hist


def evaluate_performance(ref_feats, stu_feats):
    results = {}
    # similarity features
    mfcc_sim = float(1 - cosine(ref_feats['mfccs'], stu_feats['mfccs']))
    chroma_sim = float(1 - cosine(ref_feats['chroma'], stu_feats['chroma']))
    contrast_sim = float(
        1 - cosine(ref_feats['contrast'], stu_feats['contrast'])
    )
    tonnetz_sim = float(1 - cosine(ref_feats['tonnetz'], stu_feats['tonnetz']))
    # pitch
    ref_hist = pitch_histogram(ref_feats['pitches'])
    stu_hist = pitch_histogram(stu_feats['pitches'])
    pitch_sim = float(1 - cosine(ref_hist, stu_hist))
    pitch_score = round(float(pitch_sim * 100), 2)
    results['pitch_score'] = pitch_score
    # tempo
    ref_tempo = float(ref_feats['tempo'])
    stu_tempo = float(stu_feats['tempo'])
    # Calculate percentage difference relative to reference tempo
    tempo_diff = abs(ref_tempo - stu_tempo)
    tempo_diff_percentage = (tempo_diff / ref_tempo) * 100
    # Use sigmoid-like scoring that's more sensitive to small differences
    # but more forgiving for larger differences
    tempo_score = 100 * (1 / (1 + (tempo_diff_percentage / 15)**2))
    results['tempo_score'] = round(float(tempo_score), 2)
    results['tempo_diff'] = round(float(tempo_diff), 2)
    results['tempo_diff_percentage'] = round(float(tempo_diff_percentage), 2)
    # energy
    energy_score = float(
        max(
            0,
            100 - abs(
                float(np.mean(ref_feats['energy'])) -
                float(np.mean(stu_feats['energy']))
            ) * 1000
        )
    )
    results['energy_score'] = round(float(energy_score), 2)
    # similarity avg
    sim_total = float(
        (mfcc_sim + chroma_sim + contrast_sim + tonnetz_sim) / 4
    )
    sim_score = round(float(sim_total * 100), 2)
    results['similarity_score'] = sim_score
    # final weighted
    final_score = float(
        (0.5 * pitch_score) +
        (0.15 * tempo_score) +
        (0.15 * energy_score) +
        (0.2 * sim_score)
    )
    results['overall_score'] = round(float(final_score), 2)
    return results


# ---------- Django views ----------


@session_login_required
def exercise_view(request):
    exercises = Exercise.objects.filter(
        deleteFlag=False,
        user_id=request.user
    )
    signup_form = UserSignupForm()
    result = None
    audio_form = AudioUploadForm(request.POST or None, request.FILES or None)
    create_form = ExerciseCreateForm()

    reference_files = []  # now just the uploaded files
    selected_ex_id = None

    if request.method == 'POST' and audio_form.is_valid():
        ref_file = audio_form.cleaned_data.get('reference_audio')
        user_file = audio_form.cleaned_data.get('user_audio')

        if ref_file:
            reference_files.append(ref_file.name)
        if ref_file and user_file:
            try:
                # Load reference audio in memory
                ref_bytes = io.BytesIO(ref_file.read())
                ref_y, ref_sr = librosa.load(ref_bytes, sr=None)
                ref_feats = load_and_extract_features_from_array(ref_y, ref_sr)

                # Load user audio in memory
                user_bytes = io.BytesIO(user_file.read())
                stu_y, stu_sr = librosa.load(user_bytes, sr=None)
                stu_feats = load_and_extract_features_from_array(stu_y, stu_sr)

                result = evaluate_performance(ref_feats, stu_feats)

                # Persist metrics to the selected exercise if provided
                selected_ex_id = request.POST.get('selected_exercise') or \
                    request.POST.get('selectedExercise') or None
                if selected_ex_id:
                    try:
                        ex = Exercise.objects.get(
                            id=selected_ex_id,
                            user_id=request.user,
                            deleteFlag=False
                        )
                        # add_metrics expects createdDate and scores
                        createdDate = None
                        # try to get createdAt from result or use now
                        if isinstance(result, dict) and result.get('createdAt'):
                            createdDate = result.get('createdAt')
                        if not createdDate:
                            createdDate = timezone.now()
                        # map values
                        pitch = result.get('pitch_score') or \
                            result.get('pitch') or 0
                        tempo = result.get('tempo_score') or \
                            result.get('tempo') or 0
                        energy = result.get('energy_score') or \
                            result.get('energy') or 0
                        final = result.get('overall_score') or \
                            result.get('final_score') or 0
                        ex.add_metrics(pitch, tempo, energy, final, createdDate)
                    except Exercise.DoesNotExist:
                        # ignore if exercise not found or not authorized
                        pass

            except Exception as e:
                result = {'error': str(e)}

    return render(request, "exercise/exercise.html", {
        "form": signup_form,
        "audio_form": audio_form,
        "reference_files": reference_files,
        "result": result,
        "exercises": exercises,
        "create_form": create_form,
        "selected_exercise": selected_ex_id
    })


def load_and_extract_features_from_array(y, sr):
    pitches, voiced_flag = extract_pitch(y, sr)
    energy = extract_energy(y)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    advanced = extract_advanced_features(y, sr)
    return {
        'y': y,
        'sr': sr,
        'pitches': pitches,
        'voiced_flag': voiced_flag,
        'energy': energy,
        'tempo': tempo,
        'mfccs': advanced['mfccs'],
        'chroma': advanced['chroma'],
        'contrast': advanced['contrast'],
        'tonnetz': advanced['tonnetz']
    }


def ajax_upload_reference_audio(request):
    if request.method == 'POST' and request.FILES.get('reference_audio'):
        ref_file = request.FILES['reference_audio']
        ref_path = os.path.join(REFERENCE_DIR, ref_file.name)
        with open(ref_path, 'wb+') as dest:
            for chunk in ref_file.chunks():
                dest.write(chunk)
        return JsonResponse({'success': True, 'filename': ref_file.name})
    return JsonResponse({'success': False}, status=400)


def ajax_exercise_metrics(request, exercise_id):
    """
    Return JSON metrics for a specific exercise
    belonging to the logged-in user.
    """
    if request.method != 'GET':
        return JsonResponse(
            {'success': False, 'error': 'GET required'},
            status=400
        )
    try:
        ex = Exercise.objects.get(
            id=exercise_id,
            deleteFlag=False,
            user_id=request.user
        )
    except Exercise.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'exercise not found'},
            status=404
        )

    metrics = ex.metrics or []
    normalized = []
    for m in metrics:
        normalized.append({
            'pitch_score': m.get('pitch_score') or
            m.get('pitch') or m.get('pitchScore'),
            'tempo_score': m.get('tempo_score') or
            m.get('tempo') or m.get('tempoScore'),
            'energy_score': m.get('energy_score') or
            m.get('energy') or m.get('energyScore'),
            'final_score': m.get('final_score') or
            m.get('overall_score') or
            m.get('finalScore') or
            m.get('overallScore'),
            'createdAt': m.get('createdAt') or
            m.get('created_at') or
            m.get('createdAt') or ''
        })

    try:
        normalized.sort(key=lambda x: x.get('createdAt') or '')
    except Exception:
        pass

    return JsonResponse({'success': True, 'metrics': normalized})


def exercise_create(request):
    if request.method == 'POST':
        form = ExerciseCreateForm(request.POST)
        if form.is_valid():
            ex = form.save(commit=False)
            user = request.user
            ex.user = user
            ex.save()
            messages.success(request, "تمرین با موفقیت ایجاد شد.")
        else:
            messages.error(request, "لطفاً عنوان تمرین را وارد کنید.")
    return redirect('exercise')


@session_login_required
@csrf_exempt
def exercise_delete(request, exercise_id):
    if request.method != 'POST':
        return JsonResponse(
            {'success': False, 'error': 'POST required'},
            status=400
        )
    try:
        ex = Exercise.objects.get(
            id=exercise_id,
            user_id=request.user,
            deleteFlag=False
        )
        ex.deleteFlag = True
        ex.save()
        return JsonResponse({'success': True})
    except Exercise.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'not found'},
            status=404
        )
