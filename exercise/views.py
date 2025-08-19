from django.shortcuts import render
from users.forms import UserSignupForm
from .forms import AudioUploadForm
from django.http import JsonResponse
import os
import librosa
import numpy as np
from users.views import session_login_required
from scipy.spatial.distance import cosine
from scipy.signal import butter, filtfilt
import tempfile

REFERENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'notes', 'media', 'reference_audio')
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
    pitches = librosa.yin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    voiced_flag = pitches > 0
    return pitches, voiced_flag

def extract_energy(y, frame_length=2048, hop_length=512):
    return librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

def extract_advanced_features(y, sr):
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    tonnetz_feat = librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr)
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
    mfcc_sim = 1 - cosine(ref_feats['mfccs'], stu_feats['mfccs'])
    chroma_sim = 1 - cosine(ref_feats['chroma'], stu_feats['chroma'])
    contrast_sim = 1 - cosine(ref_feats['contrast'], stu_feats['contrast'])
    tonnetz_sim = 1 - cosine(ref_feats['tonnetz'], stu_feats['tonnetz'])
    # pitch
    ref_hist = pitch_histogram(ref_feats['pitches'])
    stu_hist = pitch_histogram(stu_feats['pitches'])
    pitch_sim = 1 - cosine(ref_hist, stu_hist)
    pitch_score = round(pitch_sim * 100, 2)
    results['pitch_score'] = pitch_score
    # tempo
    tempo_diff = abs(float(ref_feats['tempo']) - float(stu_feats['tempo']))
    tempo_score = max(0, 100 - tempo_diff * 8)
    results['tempo_score'] = round(tempo_score, 2)
    results['tempo_diff'] = round(float(tempo_diff), 2)
    # energy
    energy_score = max(0, 100 - abs(np.mean(ref_feats['energy']) - np.mean(stu_feats['energy'])) * 1000)
    results['energy_score'] = round(energy_score, 2)
    # similarity avg
    sim_total = (mfcc_sim + chroma_sim + contrast_sim + tonnetz_sim) / 4
    sim_score = round(sim_total * 100, 2)
    results['similarity_score'] = sim_score
    # final weighted
    final_score = (0.5 * pitch_score) + (0.15 * tempo_score) + (0.15 * energy_score) + (0.2 * sim_score)
    results['overall_score'] = round(final_score, 2)
    return results

# ---------- Django views ----------

@session_login_required
def exercise_view(request):
    signup_form = UserSignupForm()
    result = None
    audio_form = AudioUploadForm(request.POST or None, request.FILES or None)
    reference_files = [f for f in os.listdir(REFERENCE_DIR) if f.lower().endswith(('.wav', '.mp3'))]

    if request.method == 'POST' and audio_form.is_valid():
        ref_file = audio_form.cleaned_data.get('reference_audio')
        if ref_file:
            ref_path = os.path.join(REFERENCE_DIR, ref_file.name)
            with open(ref_path, 'wb+') as dest:
                for chunk in ref_file.chunks():
                    dest.write(chunk)
            reference_files.append(ref_file.name)

        user_file = audio_form.cleaned_data.get('user_audio')
        selected_ref = request.POST.get('selected_reference')
        if user_file and selected_ref:
            ref_path = os.path.join(REFERENCE_DIR, selected_ref)
            try:
                # save uploaded user audio safely
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    for chunk in user_file.chunks():
                        tmp.write(chunk)
                    user_path = tmp.name

                # extract features
                ref_feats = load_and_extract_features(ref_path)
                stu_feats = load_and_extract_features(user_path)

                result = evaluate_performance(ref_feats, stu_feats)
                # cleanup temp file
                os.unlink(user_path)

            except Exception as e:
                result = {'error': str(e)}

    return render(request, "exercise/exercise.html", {
        "form": signup_form,
        "audio_form": audio_form,
        "reference_files": reference_files,
        "result": result
    })

def ajax_upload_reference_audio(request):
    if request.method == 'POST' and request.FILES.get('reference_audio'):
        ref_file = request.FILES['reference_audio']
        ref_path = os.path.join(REFERENCE_DIR, ref_file.name)
        with open(ref_path, 'wb+') as dest:
            for chunk in ref_file.chunks():
                dest.write(chunk)
        return JsonResponse({'success': True, 'filename': ref_file.name})
    return JsonResponse({'success': False}, status=400)
