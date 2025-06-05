import streamlit as st
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os

# Path to built-in reference files (place your .wav or .mp3 files in this folder)
REFERENCE_DIR = "reference_audio"

# Ensure reference directory exists
os.makedirs(REFERENCE_DIR, exist_ok=True)

st.title("Piano Performance Comparator")

# List available reference files (now supports .wav and .mp3)
reference_files = [f for f in os.listdir(REFERENCE_DIR) if f.lower().endswith(('.wav', '.mp3'))]

if not reference_files:
    st.warning(f"No reference files found in '{REFERENCE_DIR}'. Please add .wav or .mp3 files to this folder.")
else:
    reference_choice = st.selectbox("Select a reference performance:", reference_files)
    user_file = st.file_uploader("Upload your performance (.wav or .mp3):", type=["wav", "mp3"])

    if reference_choice and user_file:
        # Load reference audio
        ref_path = os.path.join(REFERENCE_DIR, reference_choice)
        ref_y, ref_sr = librosa.load(ref_path, sr=None)
        # Load user audio
        user_y, user_sr = librosa.load(user_file, sr=None)

        # --- Performance optimizations ---
        # Use mono audio and downsample to 22050 Hz for faster processing
        target_sr = 22050
        if ref_sr != target_sr:
            ref_y = librosa.resample(ref_y, orig_sr=ref_sr, target_sr=target_sr)
            ref_sr = target_sr
        if user_sr != target_sr:
            user_y = librosa.resample(user_y, orig_sr=user_sr, target_sr=target_sr)
            user_sr = target_sr

        # Shorten audio to first 60 seconds for quick analysis
        max_duration = 60
        ref_y = ref_y[:target_sr * max_duration]
        user_y = user_y[:target_sr * max_duration]

        # --- User-friendly scoring and feedback ---
        # Onset detection (timing accuracy) with higher resolution and backtracking
        onset_hop = 512  # Slightly higher hop for speed
        ref_onsets = librosa.onset.onset_detect(y=ref_y, sr=ref_sr, units='time', hop_length=onset_hop, backtrack=True)
        user_onsets = librosa.onset.onset_detect(y=user_y, sr=user_sr, units='time', hop_length=onset_hop, backtrack=True)

        # --- Fix DTW input for onset alignment ---
        # Onset arrays must be 2D (1, N) and (1, M) for DTW
        ref_onsets_2d = np.atleast_2d(ref_onsets)
        user_onsets_2d = np.atleast_2d(user_onsets)
        D, wp = librosa.sequence.dtw(ref_onsets_2d, user_onsets_2d, metric='euclidean')
        # For timing error, align by DTW path
        aligned_ref = ref_onsets[wp[:, 0]]
        aligned_user = user_onsets[wp[:, 1]]
        timing_error = np.mean(np.abs(aligned_ref - aligned_user)) if len(aligned_ref) > 0 else 0

        # Chroma features (pitch correctness) with moderate time resolution
        chroma_hop = 512
        ref_chroma = librosa.feature.chroma_cqt(y=ref_y, sr=ref_sr, hop_length=chroma_hop)
        user_chroma = librosa.feature.chroma_cqt(y=user_y, sr=user_sr, hop_length=chroma_hop)
        # Pad to same length
        min_frames = min(ref_chroma.shape[1], user_chroma.shape[1])
        ref_chroma = ref_chroma[:, :min_frames]
        user_chroma = user_chroma[:, :min_frames]
        # Pad chroma features to the same number of frames (columns)
        if ref_chroma.shape[1] < user_chroma.shape[1]:
            pad_width = user_chroma.shape[1] - ref_chroma.shape[1]
            ref_chroma = np.pad(ref_chroma, ((0,0),(0,pad_width)), mode='constant')
        elif user_chroma.shape[1] < ref_chroma.shape[1]:
            pad_width = ref_chroma.shape[1] - user_chroma.shape[1]
            user_chroma = np.pad(user_chroma, ((0,0),(0,pad_width)), mode='constant')
        # Now both chroma arrays have the same shape (K, N)
        # DTW on chroma for better pitch alignment
        chroma_D, chroma_wp = librosa.sequence.dtw(ref_chroma, user_chroma, metric='cosine')
        chroma_similarity = 1 - chroma_D[-1, -1] / chroma_wp.shape[0]

        # --- User-friendly scoring ---
        # Score out of 100, weighted: 60% pitch, 40% timing
        pitch_score = max(0, min(100, chroma_similarity * 100))
        timing_score = max(0, min(100, 100 - timing_error * 50))  # 0.02s error = -1pt
        overall_score = round(0.6 * pitch_score + 0.4 * timing_score, 1)

        st.markdown(f"### 🎹 Your Performance Score: **{overall_score}/100**")
        st.progress(int(overall_score))
        st.write(f"Pitch Score: {pitch_score:.1f}/100 | Timing Score: {timing_score:.1f}/100")

        # Friendly feedback
        if overall_score > 90:
            st.success("Excellent! Your performance is very close to the reference.")
        elif overall_score > 75:
            st.info("Good job! Some small improvements possible.")
        elif overall_score > 50:
            st.warning("Keep practicing! Timing or pitch could be improved.")
        else:
            st.error("Significant differences detected. Try to match the reference more closely.")

        # Display results
        st.subheader("Timing Accuracy (Onset Alignment)")
        fig, ax = plt.subplots()
        ax.plot(ref_onsets, np.zeros_like(ref_onsets), 'o', label='Reference Onsets')
        ax.plot(user_onsets, np.ones_like(user_onsets), 'o', label='User Onsets')
        for i, (r, u) in enumerate(zip(ref_onsets, user_onsets)):
            ax.plot([r, u], [0, 1], 'k--', alpha=0.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Reference', 'User'])
        ax.set_xlabel('Time (s)')
        ax.legend()
        st.pyplot(fig)
        st.write(f"**Average onset timing error:** {timing_error:.3f} seconds (lower is better)")

        st.subheader("Pitch Correctness (Chroma Similarity, DTW)")
        fig2, ax2 = plt.subplots()
        img = librosa.display.specshow(np.abs(ref_chroma - user_chroma), y_axis='chroma', x_axis='time', ax=ax2)
        fig2.colorbar(img, ax=ax2)
        ax2.set_title('Chroma Difference (Reference vs User)')
        st.pyplot(fig2)
        st.write(f"**Chroma similarity score (DTW):** {chroma_similarity:.3f} (closer to 1 is better)")

        # DTW path plot for chroma
        st.subheader("Chroma DTW Path")
        fig3, ax3 = plt.subplots()
        ax3.imshow(chroma_D, origin='lower', cmap='gray_r', interpolation='nearest', aspect='auto')
        ax3.plot(chroma_wp[:, 1], chroma_wp[:, 0], color='lime', label='DTW Path')
        ax3.set_xlabel('User Chroma Frame')
        ax3.set_ylabel('Reference Chroma Frame')
        ax3.set_title('Chroma DTW Cost Matrix and Path')
        ax3.legend()
        st.pyplot(fig3)

        # Simple score
        score = max(0, 100 * chroma_similarity - 10 * timing_error)
        st.success(f"Overall Score: {score:.1f}/100")

        # --- Improved Piano note extraction and display (Do Re Mi) ---
        NOTE_NAMES_SOLFEGE = ['do', 'do#', 're', 're#', 'mi', 'fa', 'fa#', 'sol', 'sol#', 'la', 'la#', 'si']
        def chroma_to_notes_solfege(chroma, sr, hop_length, threshold=0.3, min_note_length=3):
            notes = []
            prev_idx = None
            count = 0
            for i in range(chroma.shape[1]):
                idx = np.argmax(chroma[:, i])
                val = chroma[idx, i]
                if val > threshold:
                    if idx == prev_idx:
                        count += 1
                    else:
                        if prev_idx is not None and count >= min_note_length:
                            notes.append(NOTE_NAMES_SOLFEGE[prev_idx])
                        prev_idx = idx
                        count = 1
                else:
                    if prev_idx is not None and count >= min_note_length:
                        notes.append(NOTE_NAMES_SOLFEGE[prev_idx])
                    prev_idx = None
                    count = 0
            # Add last note if it was long enough
            if prev_idx is not None and count >= min_note_length:
                notes.append(NOTE_NAMES_SOLFEGE[prev_idx])
            return notes

        ref_notes = chroma_to_notes_solfege(ref_chroma, ref_sr, chroma_hop, threshold=0.3, min_note_length=3)
        user_notes = chroma_to_notes_solfege(user_chroma, user_sr, chroma_hop, threshold=0.3, min_note_length=3)

        st.markdown('---')
        st.markdown('#### Reference Audio Notes:')
        st.code(' '.join(ref_notes), language='')
        st.markdown('#### Uploaded Audio Notes:')
        st.code(' '.join(user_notes), language='')
        st.markdown('---')

        st.caption("Analysis uses high-resolution onset detection and DTW on chroma features for super-accurate timing and pitch comparison. For best results, use clean solo piano recordings of the same piece.")
