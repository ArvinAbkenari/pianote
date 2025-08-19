document.addEventListener('DOMContentLoaded', () => {
    setupAudioHandlers();
    setupSongSelection();
});


// Setup audio upload and visualization
function setupAudioHandlers() {
    const uploadBox = document.getElementById('practiceUpload');
    const fileInput = document.getElementById('id_user_audio');
    const userFileName = document.getElementById('userFileName');

    // Prevent default click event on file input
    fileInput.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Remove the onclick attribute from uploadBox to prevent double dialog
    uploadBox.onclick = null;

    uploadBox.addEventListener('click', function(e) {
        fileInput.value = null; // Reset so same file can be re-uploaded
        fileInput.click();
    });
    uploadBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadBox.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
    });
    uploadBox.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadBox.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--input-border').trim();
    });
    uploadBox.addEventListener('drop', function(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('audio/')) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            userFileName.textContent = e.target.files[0].name;
            handleAudioFile(e.target.files[0]);
        } else {
            userFileName.textContent = '';
        }
    });

    // Reference upload
    const referenceInput = document.getElementById('id_reference_audio');
    const referenceUploadCard = document.getElementById('referenceUploadCard');
    const referenceFileName = document.getElementById('referenceFileName');
    referenceInput.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    referenceUploadCard.onclick = function() {
        referenceInput.value = null;
        referenceInput.click();
    };
    referenceInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            // AJAX upload
            const file = e.target.files[0];
            referenceFileName.textContent = file.name;
            const formData = new FormData();
            formData.append('reference_audio', file);
            fetch('/exercise/ajax/upload_reference/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Create new song card
                    const songLibrary = document.querySelector('.song-library');
                    const card = document.createElement('div');
                    card.className = 'song-card';
                    card.setAttribute('data-ref', data.filename);
                    card.innerHTML = `
                        <div class="song-info">
                            <h3>${data.filename.length > 15 ? data.filename.slice(0, 15) + '...' : data.filename}</h3>
                            <p>فایل مرجع</p>
                        </div>
                        <button type="button" class="select-btn">انتخاب</button>
                    `;
                    songLibrary.insertBefore(card, document.getElementById('referenceUploadCard'));
                    // Add event listener for selection
                    card.querySelector('.select-btn').addEventListener('click', function(e) {
                        e.preventDefault();
                        document.querySelectorAll('.song-card').forEach(c => c.classList.remove('selected-song'));
                        card.classList.add('selected-song');
                        document.getElementById('selectedReferenceInput').value = data.filename;
                        const referenceAudioPlayer = document.getElementById('referenceAudioPlayer');
                        if (referenceAudioPlayer) {
                            referenceAudioPlayer.src = `/media/reference_audio/${data.filename}`;
                            referenceAudioPlayer.load();
                        }
                    });
                } else {
                    referenceFileName.textContent = 'خطا در بارگذاری';
                }
            })
            .catch(() => {
                referenceFileName.textContent = 'خطا در بارگذاری';
            });
        } else {
            referenceFileName.textContent = '';
        }
    });
}

// Setup song selection and audio playback
function setupSongSelection() {
    const songCards = document.querySelectorAll('.song-card');
    const selectBtns = document.querySelectorAll('.select-btn');
    const selectedReferenceInput = document.getElementById('selectedReferenceInput');
    const referenceAudioPlayer = document.getElementById('referenceAudioPlayer');

    songCards.forEach((card, idx) => {
        const btn = card.querySelector('.select-btn');
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            // Remove highlight from all
            songCards.forEach(c => c.classList.remove('selected-song'));
            // Highlight this card
            card.classList.add('selected-song');
            // Set hidden input value
            selectedReferenceInput.value = card.getAttribute('data-ref');
            // Set reference audio player src
            if (referenceAudioPlayer) {
                referenceAudioPlayer.src = `/media/reference_audio/${card.getAttribute('data-ref')}`;
                referenceAudioPlayer.load();
            }
        });
    });
}

// Handle audio file processing and visualization
function handleAudioFile(file) {
    const fileURL = URL.createObjectURL(file);
    const userAudioPlayer = document.getElementById('userAudioPlayer');
    if (userAudioPlayer) {
        userAudioPlayer.src = fileURL;
        userAudioPlayer.load();
    }

    // TODO: Add audio processing and visualization logic
}

// Helper to get CSRF token from cookie
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    return cookieValue;
}