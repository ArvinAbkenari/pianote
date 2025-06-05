document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    setupAudioHandlers();
    setupSongSelection();
});

// Initialize all charts using Chart.js
function initializeCharts() {
    // Chart.js rendering for timing and chroma charts if data is available
    let chartData = null;
    try {
        chartData = JSON.parse(document.getElementById('chartjsResultData').textContent);
    } catch (e) {}
    if (chartData) {
        // Timing chart
        const timingCanvas = document.getElementById('timingCanvas');
        if (timingCanvas && chartData.ref_onsets && chartData.user_onsets) {
            timingCanvas.width = timingCanvas.parentElement.offsetWidth;
            timingCanvas.height = 220;
            new Chart(timingCanvas.getContext('2d'), {
                type: 'scatter',
                data: {
                    datasets: [
                        {
                            label: 'Onsets مرجع',
                            data: chartData.ref_onsets.map(x => ({x, y: 0})),
                            backgroundColor: '#43cea2',
                            pointRadius: 7,
                            pointHoverRadius: 10,
                        },
                        {
                            label: 'Onsets شما',
                            data: chartData.user_onsets.map(x => ({x, y: 1})),
                            backgroundColor: '#fd5c63',
                            pointRadius: 7,
                            pointHoverRadius: 10,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {display: true, position: 'top', labels: {font: {size: 16}}},
                        title: {display: true, text: 'مقایسه زمان‌بندی اجرا', font: {size: 18}}
                    },
                    layout: {padding: 10},
                    scales: {
                        y: {
                            min: -0.5, max: 1.5,
                            ticks: {callback: v => v === 0 ? 'مرجع' : v === 1 ? 'شما' : '', font: {size: 15}},
                            grid: {color: '#eee'}
                        },
                        x: {title: {display: true, text: 'زمان (ثانیه)', font: {size: 15}}, grid: {color: '#eee'}}
                    }
                }
            });
        }
        // Chroma chart (difference heatmap)
        const noteCanvas = document.getElementById('noteCanvas');
        if (noteCanvas && chartData.ref_chroma && chartData.user_chroma) {
            noteCanvas.width = noteCanvas.parentElement.offsetWidth;
            noteCanvas.height = 220;
            // Calculate chroma diff
            const chromaDiff = chartData.ref_chroma.map((row, i) => row.map((v, j) => Math.abs(v - chartData.user_chroma[i][j])));
            // Render as a bar chart for each chroma bin (mean diff per bin)
            const chromaLabels = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
            const chromaMeans = chromaDiff.map(row => row.reduce((a, b) => a + b, 0) / row.length);
            new Chart(noteCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: chromaLabels,
                    datasets: [{
                        label: 'میانگین اختلاف کرما',
                        data: chromaMeans,
                        backgroundColor: chromaLabels.map((_, i) => `hsl(${i*30}, 70%, 60%)`),
                        borderRadius: 8,
                        barPercentage: 0.8,
                        categoryPercentage: 0.7,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {display: false},
                        title: {display: true, text: 'اختلاف نت‌ها (کرما)', font: {size: 18}}
                    },
                    layout: {padding: 10},
                    scales: {
                        y: {beginAtZero: true, title: {display: true, text: 'اختلاف', font: {size: 15}}, grid: {color: '#eee'}, ticks: {font: {size: 14}}},
                        x: {ticks: {font: {size: 14}}, grid: {color: '#eee'}}
                    }
                }
            });
        }
    }
}

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
            referenceFileName.textContent = e.target.files[0].name;
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
        });
    });
}

// Handle audio file processing and visualization
function handleAudioFile(file) {
    const fileURL = URL.createObjectURL(file);
    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.src = fileURL;
    audioPlayer.play();

    // TODO: Add audio processing and visualization logic
}