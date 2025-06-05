from django.shortcuts import render
from users.forms import UserSignupForm
from .forms import AudioUploadForm
from django.http import JsonResponse
import os
import librosa
import numpy as np

REFERENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'notes', 'media', 'reference_audio')
os.makedirs(REFERENCE_DIR, exist_ok=True)

def exercise_view(request):
    signup_form = UserSignupForm()
    result = None
    audio_form = AudioUploadForm(request.POST or None, request.FILES or None)
    reference_files = [f for f in os.listdir(REFERENCE_DIR) if f.lower().endswith(('.wav', '.mp3'))]
    if request.method == 'POST' and audio_form.is_valid():
        # Handle reference audio upload
        ref_file = audio_form.cleaned_data.get('reference_audio')
        if ref_file:
            ref_path = os.path.join(REFERENCE_DIR, ref_file.name)
            with open(ref_path, 'wb+') as dest:
                for chunk in ref_file.chunks():
                    dest.write(chunk)
            reference_files.append(ref_file.name)
        # Handle user audio upload and analysis
        user_file = audio_form.cleaned_data.get('user_audio')
        selected_ref = request.POST.get('selected_reference')
        if user_file and selected_ref:
            ref_path = os.path.join(REFERENCE_DIR, selected_ref)
            # --- Analysis logic from app.py ---
            try:
                ref_y, ref_sr = librosa.load(ref_path, sr=None)
                user_y, user_sr = librosa.load(user_file, sr=None)
                target_sr = 22050
                if ref_sr != target_sr:
                    ref_y = librosa.resample(ref_y, orig_sr=ref_sr, target_sr=target_sr)
                    ref_sr = target_sr
                if user_sr != target_sr:
                    user_y = librosa.resample(user_y, orig_sr=user_sr, target_sr=target_sr)
                    user_sr = target_sr
                max_duration = 60
                ref_y = ref_y[:target_sr * max_duration]
                user_y = user_y[:target_sr * max_duration]
                onset_hop = 512
                ref_onsets = librosa.onset.onset_detect(y=ref_y, sr=ref_sr, units='time', hop_length=onset_hop, backtrack=True)
                user_onsets = librosa.onset.onset_detect(y=user_y, sr=user_sr, units='time', hop_length=onset_hop, backtrack=True)
                ref_onsets_2d = np.atleast_2d(ref_onsets)
                user_onsets_2d = np.atleast_2d(user_onsets)
                D, wp = librosa.sequence.dtw(ref_onsets_2d, user_onsets_2d, metric='euclidean')
                aligned_ref = ref_onsets[wp[:, 0]]
                aligned_user = user_onsets[wp[:, 1]]
                timing_error = np.mean(np.abs(aligned_ref - aligned_user)) if len(aligned_ref) > 0 else 0
                chroma_hop = 512
                ref_chroma = librosa.feature.chroma_cqt(y=ref_y, sr=ref_sr, hop_length=chroma_hop)
                user_chroma = librosa.feature.chroma_cqt(y=user_y, sr=user_sr, hop_length=chroma_hop)
                min_frames = min(ref_chroma.shape[1], user_chroma.shape[1])
                ref_chroma = ref_chroma[:, :min_frames]
                user_chroma = user_chroma[:, :min_frames]
                if ref_chroma.shape[1] < user_chroma.shape[1]:
                    pad_width = user_chroma.shape[1] - ref_chroma.shape[1]
                    ref_chroma = np.pad(ref_chroma, ((0,0),(0,pad_width)), mode='constant')
                elif user_chroma.shape[1] < ref_chroma.shape[1]:
                    pad_width = ref_chroma.shape[1] - user_chroma.shape[1]
                    user_chroma = np.pad(user_chroma, ((0,0),(0,pad_width)), mode='constant')
                chroma_D, chroma_wp = librosa.sequence.dtw(ref_chroma, user_chroma, metric='cosine')
                chroma_similarity = 1 - chroma_D[-1, -1] / chroma_wp.shape[0]
                pitch_score = max(0, min(100, chroma_similarity * 100))
                timing_score = max(0, min(100, 100 - timing_error * 50))
                overall_score = round(0.6 * pitch_score + 0.4 * timing_score, 1)
                result = {
                    'overall_score': overall_score,
                    'pitch_score': pitch_score,
                    'timing_score': timing_score,
                    'timing_error': timing_error,
                    'chroma_similarity': chroma_similarity,
                    # Chart.js data:
                    'ref_onsets': ref_onsets.tolist(),
                    'user_onsets': user_onsets.tolist(),
                    'ref_chroma': ref_chroma.tolist(),
                    'user_chroma': user_chroma.tolist(),
                }
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
