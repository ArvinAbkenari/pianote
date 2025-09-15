import streamlit as st
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os

# Path to built-in reference files
REFERENCE_DIR = "reference_audio"

# Ensure reference directory exists
os.makedirs(REFERENCE_DIR, exist_ok=True)

st.title("Piano Performance Comparator")

# List available reference files
reference_files = [
    f for f in os.listdir(REFERENCE_DIR) 
    if f.lower().endswith(('.wav', '.mp3'))
]

if not reference_files:
    st.warning(
        f"No reference files found in '{REFERENCE_DIR}'. "
        "Please add .wav or .mp3 files to this folder."
    )
else:
    reference_choice = st.selectbox(
        "Select a reference performance:", reference_files
    )
    user_file = st.file_uploader(
        "Upload your performance (.wav or .mp3):", type=["wav", "mp3"]
    )

    if reference_choice and user_file:
        # Load audio files
        ref_path = os.path.join(REFERENCE_DIR, reference_choice)
        ref_y, ref_sr = librosa.load(ref_path, sr=None)
        user_y, user_sr = librosa.load(user_file, sr=None)

        # --- Performance optimizations ---
        target_sr = 22050
        if ref_sr != target_sr:
            ref_y = librosa.resample(
                ref_y, orig_sr=ref_sr, target_sr=target_sr
            )
            ref_sr = target_sr
        if user_sr != target_sr:
            user_y = librosa.resample(
                user_y, orig_sr=user_sr, target_sr=target_sr
            )
            user_sr = target_sr

        max_duration = 60
        ref_y = ref_y[:target_sr * max_duration]
        user_y = user_y[:target_sr * max_duration]

        # --- Timing Analysis (Onset Detection) ---
        onset_hop = 512
        ref_onsets = librosa.onset.onset_detect(
            y=ref_y, sr=ref_sr, units='time',
            hop_length=onset_hop, backtrack=True
        )
        user_onsets = librosa.onset.onset_detect(
            y=user_y, sr=user_sr, units='time',
            hop_length=onset_hop, backtrack=True
        )

        # --- DTW for Onset Alignment ---
        ref_onsets_2d = np.atleast_2d(ref_onsets)
        user_onsets_2d = np.atleast_2d(user_onsets)
        D, wp = librosa.sequence.dtw(
            ref_onsets_2d, user_onsets_2d, metric='euclidean'
        )
        aligned_ref = ref_onsets[wp[:, 0]]
        aligned_user = user_onsets[wp[:, 1]]
        timing_error = np.mean(np.abs(aligned_ref - aligned_user)) if len(
            aligned_ref) > 0 else 0

        # --- Pitch Analysis (Chroma Features) ---
        chroma_hop = 512
        ref_chroma = librosa.feature.chroma_cqt(
            y=ref_y, sr=ref_sr, hop_length=chroma_hop
        )
        user_chroma = librosa.feature.chroma_cqt(
            y=user_y, sr=user_sr, hop_length=chroma_hop
        )

        min_frames = min(ref_chroma.shape[1], user_chroma.shape[1])
        ref_chroma = ref_chroma[:, :min_frames]
        user_chroma = user_chroma[:, :min_frames]

        if ref_chroma.shape[1] < user_chroma.shape[1]:
            pad_width = user_chroma.shape[1] - ref_chroma.shape[1]
            ref_chroma = np.pad(
                ref_chroma, ((0, 0), (0, pad_width)), mode='constant'
            )
        elif user_chroma.shape[1] < ref_chroma.shape[1]:
            pad_width = ref_chroma.shape[1] - user_chroma.shape[1]
            user_chroma = np.pad(
                user_chroma, ((0, 0), (0, pad_width)), mode='constant'
            )

        chroma_D, chroma_wp = librosa.sequence.dtw(
            ref_chroma, user_chroma, metric='cosine'
        )
        chroma_similarity = 1 - chroma_D[-1, -1] / chroma_wp.shape[0]

        # --- Scoring ---
        pitch_score = max(0, min(100, chroma_similarity * 100))
        timing_score = max(0, min(100, 100 - timing_error * 50))
        overall_score = round(0.6 * pitch_score + 0.4 * timing_score, 1)

        st.markdown(
            f"### 🎹 Your Performance Score: **{overall_score}/100**"
        )
        st.progress(int(overall_score))
        st.write(
            f"Pitch Score: {pitch_score:.1f}/100 | "
            f"Timing Score: {timing_score:.1f}/100"
        )

        # --- Feedback ---
        if overall_score > 90:
            st.success(
                "Excellent! Your performance is very close to the reference."
            )
        elif overall_score > 75:
            st.info("Good job! Some small improvements possible.")
        elif overall_score > 50:
            st.warning("Keep practicing! Timing or pitch could be improved.")
        else:
            st.error(
                "Significant differences detected. "
                "Try to match the reference more closely."
            )

        # --- Visualizations ---
        st.subheader("Timing Accuracy (Onset Alignment)")
        fig, ax = plt.subplots()
        ax.plot(
            ref_onsets, np.zeros_like(ref_onsets), 
            'o', label='Reference Onsets'
        )
        ax.plot(
            user_onsets, np.ones_like(user_onsets), 
            'o', label='User Onsets'
        )
        for i, (r, u) in enumerate(zip(ref_onsets, user_onsets)):
            ax.plot([r, u], [0, 1], 'k--', alpha=0.5)
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Reference', 'User'])
        ax.set_xlabel('Time (s)')
        ax.legend()
        st.pyplot(fig)
        st.write(
            f"**Average onset timing error:** {timing_error:.3f} seconds "
            "(lower is better)"
        )

        st.subheader("Pitch Correctness (Chroma Similarity, DTW)")
        fig2, ax2 = plt.subplots()
        img = librosa.display.specshow(
            np.abs(ref_chroma - user_chroma),
            y_axis='chroma',
            x_axis='time',
            ax=ax2
        )
        fig2.colorbar(img, ax=ax2)
        ax2.set_title('Chroma Difference (Reference vs User)')
        st.pyplot(fig2)
        st.write(
            f"**Chroma similarity score (DTW):** {chroma_similarity:.3f} "
            "(closer to 1 is better)"
        )

        st.subheader("Chroma DTW Path")
        fig3, ax3 = plt.subplots()
        ax3.imshow(
            chroma_D, origin='lower', cmap='gray_r',
            interpolation='nearest', aspect='auto'
        )
        ax3.plot(
            chroma_wp[:, 1], chroma_wp[:, 0], 
            color='lime', label='DTW Path'
        )
        ax3.set_xlabel('User Chroma Frame')
        ax3.set_ylabel('Reference Chroma Frame')
        ax3.set_title('Chroma DTW Cost Matrix and Path')
        ax3.legend()
        st.pyplot(fig3)

        score = max(0, 100 * chroma_similarity - 10 * timing_error)
        st.success(f"Overall Score: {score:.1f}/100")


