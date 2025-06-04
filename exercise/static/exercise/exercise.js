document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
    setupAudioHandlers();
    setupSongSelection();
});

// Initialize all charts using Chart.js
function initializeCharts() {
    try {
        // Validate canvas elements
        const canvasElements = {
            timing: document.getElementById('timingCanvas'),
            note: document.getElementById('noteCanvas'),
            progress: document.getElementById('progressCanvas')
        };

        // Check if all canvas elements exist
        Object.entries(canvasElements).forEach(([type, element]) => {
            if (!element) {
                throw new Error(`Canvas element for ${type} chart not found`);
            }
        });

        // Get the accent color from CSS variables
        const accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();

        // Initialize Timing Precision Chart
        try {
            const timingCtx = canvasElements.timing.getContext('2d');
            new Chart(timingCtx, {
                type: 'line',
                data: {
                    labels: ['۰ث', '۵ث', '۱۰ث', '۱۵ث', '۲۰ث', '۲۵ث', '۳۰ث'],
                    datasets: [{
                        label: 'دقت زمان‌بندی',
                        data: [95, 87, 92, 88, 90, 85, 89],
                        borderColor: accentColor,
                        tension: 0.4,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing timing chart:', error);
        }

        // Initialize Note Accuracy Chart
        try {
            const noteCtx = canvasElements.note.getContext('2d');
            new Chart(noteCtx, {
                type: 'bar',
                data: {
                    labels: ['دو', 'ر', 'می', 'فا', 'سل', 'لا', 'سی'],
                    datasets: [{
                        label: 'دقت نت‌ها',
                        data: [92, 88, 95, 85, 90, 87, 93],
                        backgroundColor: accentColor,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing note chart:', error);
        }

        // Initialize Progress Timeline Chart
        try {
            const progressCtx = canvasElements.progress.getContext('2d');
            new Chart(progressCtx, {
                type: 'line',
                data: {
                    labels: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه'],
                    datasets: [{
                        label: 'پیشرفت کلی',
                        data: [75, 78, 80, 79, 85, 83, 88],
                        borderColor: accentColor,
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(49, 130, 206, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing progress chart:', error);
        }
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

// Setup audio upload and visualization
function setupAudioHandlers() {
    const uploadBox = document.getElementById('practiceUpload');
    const fileInput = uploadBox.querySelector('input[type="file"]');

    uploadBox.addEventListener('click', () => fileInput.click());
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
    });

    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadBox.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--input-border').trim();
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('audio/')) {
            handleAudioFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleAudioFile(e.target.files[0]);
        }
    });
}

// Handle the uploaded audio file
function handleAudioFile(file) {
    // TODO: Implement audio file processing and visualization
    console.log('Audio file uploaded:', file.name);
}

// Setup song selection functionality
function setupSongSelection() {
    const selectButtons = document.querySelectorAll('.select-btn');
    selectButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const songCard = e.target.closest('.song-card');
            const songTitle = songCard.querySelector('h3').textContent;
            const composer = songCard.querySelector('p').textContent;
            console.log('Selected song:', songTitle, 'by', composer);
            // TODO: Implement song selection logic
        });
    });
}