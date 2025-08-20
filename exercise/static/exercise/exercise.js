document.addEventListener('DOMContentLoaded', () => {
    setupAudioHandlers();
    setupSongSelection();
    initInitialUIState();
    handleServerResult();
    const selectedInput = document.getElementById('selectedExerciseInput');
    if (selectedInput && selectedInput.value) {
        const exerciseId = selectedInput.value;
        // find card and mark selected
        const card = document.querySelector(`.song-card[data-exercise-id="${exerciseId}"]`);
        if (card) {
            // simulate clicking the select button to reuse logic
            const btn = card.querySelector('.select-btn');
            if (btn) btn.click();
        }
    }
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
    // const referenceInput = document.getElementById('id_reference_audio');
    // const referenceUploadCard = document.getElementById('referenceUploadCard');
    // const referenceFileName = document.getElementById('referenceFileName');
    // referenceInput.addEventListener('click', function(e) {
    //     e.stopPropagation();
    // });
    // referenceUploadCard.onclick = function() {
    //     referenceInput.value = null;
    //     referenceInput.click();
    // };
    // referenceInput.addEventListener('change', function(e) {
    //     if (e.target.files.length > 0) {
    //         // AJAX upload
    //         const file = e.target.files[0];

    //         const formData = new FormData();
    //         formData.append('reference_audio', file);
    //         fetch('/exercise/ajax/upload_reference/', {
    //             method: 'POST',
    //             headers: { 'X-CSRFToken': getCSRFToken() },
    //             body: formData
    //         })
    //         .then(res => res.json())
    //         .then(data => {
    //             if (data.success) {
    //                 // Create new song card
    //                 const songLibrary = document.querySelector('.song-library');
    //                 const card = document.createElement('div');
    //                 card.className = 'song-card';
    //                 card.setAttribute('data-ref', data.filename);
    //                 card.innerHTML = `
    //                     <div class="song-info">
    //                         <h3>${data.filename.length > 15 ? data.filename.slice(0, 15) + '...' : data.filename}</h3>
    //                         <p>فایل مرجع</p>
    //                     </div>
    //                     <button type="button" class="select-btn">انتخاب</button>
    //                 `;
    //                 songLibrary.insertBefore(card, document.getElementById('referenceUploadCard'));
    //                 // Add event listener for selection
    //                 card.querySelector('.select-btn').addEventListener('click', function(e) {
    //                     e.preventDefault();
    //                     document.querySelectorAll('.song-card').forEach(c => c.classList.remove('selected-song'));
    //                     card.classList.add('selected-song');
    //                     document.getElementById('selectedReferenceInput').value = data.filename;
    //                     const referenceAudioPlayer = document.getElementById('referenceAudioPlayer');
    //                     if (referenceAudioPlayer) {
    //                         referenceAudioPlayer.src = `/media/reference_audio/${data.filename}`;
    //                         referenceAudioPlayer.load();
    //                     }
    //                 });
    //             } else {
    //                 referenceFileName.textContent = 'خطا در بارگذاری';
    //             }
    //         })
    //         .catch(() => {
    //             referenceFileName.textContent = 'خطا در بارگذاری';
    //         });
    //     } else {
    //         referenceFileName.textContent = '';
    //     }
    // });

    const uploadBoxref = document.getElementById('refUpload');
    const fileInputref = document.getElementById('id_reference_audio');
    const userFileNameref = document.getElementById('referenceFileName');

    // Prevent default click event on file input
    fileInputref.addEventListener('click', function(e) {
        e.stopPropagation();
    });

    // Remove the onclick attribute from uploadBox to prevent double dialog
    uploadBoxref.onclick = null;

    uploadBoxref.addEventListener('click', function(e) {
        fileInputref.value = null; // Reset so same file can be re-uploaded
        fileInputref.click();
    });
    uploadBoxref.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadBoxref.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
    });
    uploadBoxref.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadBoxref.style.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--input-border').trim();
    });
    uploadBoxref.addEventListener('drop', function(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('audio/')) {
            fileInputref.files = files;
            fileInputref.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
    fileInputref.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            userFileNameref.textContent = e.target.files[0].name;
            handleAudioFileref(e.target.files[0]);
        } else {
            userFileNameref.textContent = '';
        }
    });
}

// Setup song selection and audio playback
function setupSongSelection() {
    const songCards = document.querySelectorAll('.song-card');
    const selectBtns = document.querySelectorAll('.select-btn');
    const selectedReferenceInput = document.getElementById('selectedReferenceInput');
    const referenceAudioPlayer = document.getElementById('referenceAudioPlayer');
    const refUpload = document.getElementById('refUpload');
    const practiceUpload = document.getElementById('practiceUpload');
    const metricsArea = document.getElementById('metricsArea');

    // when exercise selected, fetch metrics and render chart via global helpers
    async function fetchAndRenderMetrics(exerciseId) {
        try {
            const res = await fetch(`/exercise/ajax/metrics/${exerciseId}/`);
            const data = await res.json();
            if (!data.success) {
                console.warn('metrics fetch failed', data);
                return;
            }
            const metrics = data.metrics || [];
            const labels = metrics.map(m => m.createdAt ? new Date(m.createdAt).toLocaleString() : '');
            const pitch = metrics.map(m => Number(m.pitch_score) || 0);
            const tempo = metrics.map(m => Number(m.tempo_score) || 0);
            const energy = metrics.map(m => Number(m.energy_score) || 0);
            const finalS = metrics.map(m => Number(m.final_score) || 0);
            if (!metrics.length) {
                // hide performance metrics and clear chart
                const perf = document.getElementById('performanceMetrics');
                if (perf) perf.style.display = 'none';
                updateGlobalChart([], [], [], [], []);
            } else {
                // show and populate latest metric
                const perf = document.getElementById('performanceMetrics');
                if (perf) perf.style.display = '';
                const latest = metrics[metrics.length - 1];
                // update metric cards
                const overallEl = document.getElementById('overallScoreValue');
                const pitchEl = document.getElementById('pitchScoreValue');
                const tempoEl = document.getElementById('tempoScoreValue');
                const energyEl = document.getElementById('energyScoreValue');
                if (overallEl) overallEl.textContent = latest.final_score ?? latest.overall_score ?? '0';
                if (pitchEl) pitchEl.textContent = latest.pitch_score ?? '0';
                if (tempoEl) tempoEl.textContent = latest.tempo_score ?? latest.tempo_diff_percentage ?? '0';
                if (energyEl) energyEl.textContent = latest.energy_score ?? '0';
                updateGlobalChart(labels, pitch, tempo, energy, finalS);
            }
        } catch (err) {
            console.error('failed to load metrics', err);
        }
    }

    songCards.forEach((card, idx) => {
        const btn = card.querySelector('.select-btn');
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            // Remove highlight from all
            songCards.forEach(c => c.classList.remove('selected-song'));
            // Highlight this card
            card.classList.add('selected-song');
            // show upload boxes and metrics
            if (refUpload) refUpload.style.display = '';
            if (practiceUpload) practiceUpload.style.display = '';
            if (metricsArea) metricsArea.style.display = '';
            // show practice section and analyze button
            const practiceSection = document.getElementById('practiceSection');
            const analyzeBtn = document.getElementById('analyzeBtn');
            if (practiceSection) practiceSection.style.display = '';
            if (analyzeBtn) analyzeBtn.style.display = '';

            const exerciseId = card.getAttribute('data-exercise-id');
            const selectedExerciseInput = document.getElementById('selectedExerciseInput');
            if (selectedExerciseInput) selectedExerciseInput.value = exerciseId || '';
            if (exerciseId) {
                fetchAndRenderMetrics(exerciseId);
            }
        });
    });
}

// Global chart helpers — used both for AJAX metrics and server-returned single result
let globalMetricsChart = null;
function hexToRgba(hex, alpha) {
    if (!hex) return `rgba(0,0,0,${alpha})`;
    const clean = hex.replace('#', '').trim();
    const bigint = parseInt(clean.length === 3 ? clean.split('').map(c => c + c).join('') : clean, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function getCSSVar(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name);
    return (v && v.trim()) || fallback;
}

function isDarkMode() {
    const t = document.documentElement.getAttribute('data-theme');
    return t === 'dark';
}

function ensureGlobalChart() {
    const canvas = document.getElementById('metricsChart');
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    if (globalMetricsChart) return globalMetricsChart;

    const textColor = getCSSVar('--text-primary', '#2D3436');
    const subText = getCSSVar('--text-secondary', '#4A5568');
    const cardBg = getCSSVar('--card-bg', '#FFFFFF');
    const accent = getCSSVar('--accent-color', '#3182CE');

    globalMetricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'دقت نت‌ها', data: [], borderColor: accent, backgroundColor: hexToRgba(accent, 0.08), tension: 0.3, pointRadius: 3, pointHoverRadius: 6, fill: true },
                { label: 'دقت زمان‌بندی', data: [], borderColor: '#38A169', backgroundColor: hexToRgba('#38A169', 0.08), tension: 0.3, pointRadius: 3, pointHoverRadius: 6, fill: true },
                { label: 'دقت صدا', data: [], borderColor: '#E53E3E', backgroundColor: hexToRgba('#E53E3E', 0.08), tension: 0.3, pointRadius: 3, pointHoverRadius: 6, fill: true },
                { label: 'امتیاز نهایی', data: [], borderColor: '#805AD5', backgroundColor: hexToRgba('#805AD5', 0.08), tension: 0.3, pointRadius: 3, pointHoverRadius: 6, fill: true }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: textColor,
                        font: { family: 'Vazirmatn, system-ui, -apple-system, sans-serif', size: 13 }
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode() ? '#0f1724' : '#fff',
                    titleColor: textColor,
                    bodyColor: getCSSVar('--text-primary', '#2D3436'),
                    borderColor: hexToRgba(subText, 0.12),
                    borderWidth: 1,
                    callbacks: {
                        label: function (ctx) {
                            const v = Number(ctx.parsed.y || 0).toFixed(1);
                            return `${ctx.dataset.label}: ${v}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: { display: true, text: 'زمان', color: textColor, font: { family: 'Vazirmatn', size: 12 } },
                    ticks: { color: subText, font: { family: 'Vazirmatn' } },
                    grid: { color: hexToRgba(subText, 0.06) }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: subText,
                        font: { family: 'Vazirmatn' },
                        callback: function (v) { return v + '%'; }
                    },
                    grid: { color: hexToRgba(subText, 0.04) }
                }
            }
        }
    });

    // style container card (metricsArea is canvas parent)
    try {
        const parent = canvas.parentElement;
        if (parent) {
            parent.style.background = cardBg;
            parent.style.padding = '1rem';
            parent.style.borderRadius = '12px';
            parent.style.boxShadow = getCSSVar('--card-shadow', '0 8px 24px rgba(0,0,0,0.08)');
        }
    } catch (e) {
        // ignore styling errors
    }

    return globalMetricsChart;
}

// Apply current theme colors to an existing chart (called on theme toggle)
function applyThemeToChart(chart) {
    const ch = chart || globalMetricsChart;
    if (!ch) return;

    const textColor = getCSSVar('--text-primary', '#2D3436');
    const subText = getCSSVar('--text-secondary', '#4A5568');
    const accent = getCSSVar('--accent-color', '#3182CE');
    const cardBg = getCSSVar('--card-bg', '#FFFFFF');

    // Map dataset colors (keep same logical ordering)
    const colors = [accent, '#38A169', '#E53E3E', '#805AD5'];

    ch.data.datasets.forEach((ds, idx) => {
        const hex = colors[idx] || accent;
        ds.borderColor = hex;
        ds.backgroundColor = hexToRgba(hex, 0.08);
        ds.pointBackgroundColor = hexToRgba(hex, 1);
    });

    // Update axis/legend/tooltip colors
    if (!ch.options) ch.options = {};
    if (!ch.options.plugins) ch.options.plugins = {};

    if (ch.options.plugins.legend && ch.options.plugins.legend.labels) {
        ch.options.plugins.legend.labels.color = textColor;
        ch.options.plugins.legend.labels.font = { family: 'Vazirmatn, system-ui, -apple-system, sans-serif', size: 13 };
    }

    if (ch.options.plugins.tooltip) {
        ch.options.plugins.tooltip.backgroundColor = isDarkMode() ? '#0f1724' : '#ffffff';
        ch.options.plugins.tooltip.titleColor = textColor;
        ch.options.plugins.tooltip.bodyColor = getCSSVar('--text-primary', '#2D3436');
        ch.options.plugins.tooltip.borderColor = hexToRgba(subText, 0.12);
    }

    if (ch.options.scales) {
        if (ch.options.scales.x) {
            if (!ch.options.scales.x.ticks) ch.options.scales.x.ticks = {};
            ch.options.scales.x.ticks.color = subText;
            if (!ch.options.scales.x.title) ch.options.scales.x.title = {};
            ch.options.scales.x.title.color = textColor;
        }
        if (ch.options.scales.y) {
            if (!ch.options.scales.y.ticks) ch.options.scales.y.ticks = {};
            ch.options.scales.y.ticks.color = subText;
        }
        // grid colors
        if (ch.options.scales.x.grid) ch.options.scales.x.grid.color = hexToRgba(subText, 0.06);
        if (ch.options.scales.y.grid) ch.options.scales.y.grid.color = hexToRgba(subText, 0.04);
    }

    // style parent container to match current theme
    try {
        const canvas = document.getElementById('metricsChart');
        if (canvas && canvas.parentElement) {
            const parent = canvas.parentElement;
            parent.style.background = cardBg;
            parent.style.boxShadow = getCSSVar('--card-shadow', '0 8px 24px rgba(0,0,0,0.08)');
            parent.style.color = textColor;
        }
    } catch (e) {
        // ignore
    }

    ch.update();
}

// Observe theme toggles on <html data-theme="..."> and update chart live
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver((mutations) => {
        for (const m of mutations) {
            if (m.type === 'attributes' && m.attributeName === 'data-theme') {
                // delay slightly to allow CSS var transition
                setTimeout(() => applyThemeToChart(), 80);
            }
        }
    });
    try {
        observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    } catch (e) {
        // ignore if observe not allowed
    }
}

function updateGlobalChart(labels, pitch, tempo, energy, finalS) {
    const chart = ensureGlobalChart();
    if (!chart) return;
    chart.data.labels = labels || [];
    chart.data.datasets[0].data = pitch || [];
    chart.data.datasets[1].data = tempo || [];
    chart.data.datasets[2].data = energy || [];
    chart.data.datasets[3].data = finalS || [];
    chart.update();
}

function handleServerResult() {
    // If server provided `result`, Django rendered it via json_script with id chartjsResultData
    const jsonEl = document.getElementById('chartjsResultData');
    if (!jsonEl) return;
    let result = {};
    try {
        result = JSON.parse(jsonEl.textContent || jsonEl.innerText || '{}');
    } catch (e) {
        console.warn('failed to parse server result', e);
        return;
    }
    // show performance metrics area
    const perf = document.getElementById('performanceMetrics');
    if (perf) perf.style.display = '';
    const metricsArea = document.getElementById('metricsArea');
    if (metricsArea) metricsArea.style.display = '';
    // create single-point chart from result
    const label = result.createdAt ? new Date(result.createdAt).toLocaleString('fa-IR') : new Date().toLocaleString('fa-IR');
    const labels = [label];
    const pitch = [Number(result.pitch_score) || Number(result.pitch) || 0];
    const tempo = [Number(result.tempo_score) || Number(result.tempo) || 0];
    const energy = [Number(result.energy_score) || Number(result.energy) || 0];
    const finalS = [Number(result.overall_score) || Number(result.final_score) || 0];
    updateGlobalChart(labels, pitch, tempo, energy, finalS);
}

function initInitialUIState() {
    const refUpload = document.getElementById('refUpload');
    const practiceUpload = document.getElementById('practiceUpload');
    const metricsArea = document.getElementById('metricsArea');
    // hide by default (already hidden inline), ensure JS-enforced
    if (refUpload) refUpload.style.display = 'none';
    if (practiceUpload) practiceUpload.style.display = 'none';
    if (metricsArea) metricsArea.style.display = 'none';
}

// Handle audio file processing and visualization
function handleAudioFile(file) {
    const fileURL = URL.createObjectURL(file);
    const userAudioPlayer = document.getElementById('userAudioPlayer');
    const userAudioWave = document.getElementById('userAudioWave');
    if (userAudioPlayer) {
        userAudioPlayer.src = fileURL;
        userAudioPlayer.load();
        userAudioPlayer.style.display = '';
    }
    if (userAudioWave) {
        userAudioWave.src = fileURL;
        userAudioWave.load();
        userAudioWave.style.display = '';
    }

}

function handleAudioFileref(file) {
    const fileURL = URL.createObjectURL(file);
    const refAudioPlayer = document.getElementById('refAudioPlayer');
    const refAudioWave = document.getElementById('refAudioWave');
    if (refAudioPlayer) {
        refAudioPlayer.src = fileURL;
        refAudioPlayer.load();
        refAudioPlayer.style.display = '';
    }
    if (refAudioWave) {
        refAudioWave.src = fileURL;
        refAudioWave.load();
        refAudioWave.style.display = '';
    }
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