// Placeholder backend function for price estimation
function estimatePianoPrice({ brand, model, dimension, material }) {
    // Simulate backend logic
    // For demo: price = base + brand factor + material factor + dimension factor
    const brandFactors = { 'Yamaha': 2000, 'Steinway & Sons': 8000, 'Kawai': 1500, 'Fazioli': 10000, 'Bechstein': 7000, 'Other': 1000 };
    const materialFactors = { 'چوب افرا': 1000, 'چوب گردو': 1200, 'چوب راش': 900, 'فلز': 500, 'Other': 700 };
    const base = 5000;
    const brandVal = brandFactors[brand] || 1000;
    const materialVal = materialFactors[material] || 700;
    const dimVal = Math.max(0, Math.min(300, Number(dimension))) * 10;
    return base + brandVal + materialVal + dimVal;
}

// Demo data for charts
const chartData = {
    brands: [
        { brand: 'Steinway & Sons', price: 180000 },
        { brand: 'Fazioli', price: 150000 },
        { brand: 'Bechstein', price: 120000 },
        { brand: 'Yamaha', price: 90000 },
        { brand: 'Kawai', price: 85000 }
    ],
    materials: [
        { material: 'چوب افرا', avgPrice: 95000 },
        { material: 'چوب گردو', avgPrice: 110000 },
        { material: 'چوب راش', avgPrice: 80000 },
        { material: 'فلز', avgPrice: 60000 }
    ],
    dimensionVsPrice: [
        { dimension: 150, price: 90000 },
        { dimension: 180, price: 110000 },
        { dimension: 200, price: 130000 },
        { dimension: 220, price: 150000 },
        { dimension: 250, price: 170000 }
    ]
};

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('piano-form');
    const resultDiv = document.getElementById('result');
    const priceDiv = document.getElementById('estimated-price');
    const chartsSection = document.getElementById('charts-section');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const brand = document.getElementById('brand').value;
        const model = document.getElementById('model').value;
        const dimension = document.getElementById('dimension').value;
        const material = document.getElementById('material').value;
        // Call backend (placeholder)
        const price = estimatePianoPrice({ brand, model, dimension, material });
        priceDiv.textContent = price.toLocaleString('fa-IR') + ' تومان';
        resultDiv.style.display = 'block';
        chartsSection.style.display = 'block';
        renderCharts();
        // Scroll to result
        resultDiv.scrollIntoView({ behavior: 'smooth' });
    });
});

function renderCharts() {
    // Brand Bar Chart
    const brandCtx = document.getElementById('brandBarChart').getContext('2d');
    new Chart(brandCtx, {
        type: 'bar',
        data: {
            labels: chartData.brands.map(b => b.brand),
            datasets: [{
                label: 'گران‌ترین برندها (تومان)',
                data: chartData.brands.map(b => b.price),
                backgroundColor: [
                    '#6a11cb', '#2575fc', '#43cea2', '#f7971e', '#fd5c63'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
    // Material Pie Chart
    const materialCtx = document.getElementById('materialPieChart').getContext('2d');
    new Chart(materialCtx, {
        type: 'pie',
        data: {
            labels: chartData.materials.map(m => m.material),
            datasets: [{
                label: 'میانگین قیمت بر اساس جنس',
                data: chartData.materials.map(m => m.avgPrice),
                backgroundColor: [
                    '#43cea2', '#6a11cb', '#f7971e', '#fd5c63'
                ]
            }]
        },
        options: { responsive: true }
    });
    // Dimension vs Price Scatter Chart
    const dimCtx = document.getElementById('dimensionScatterChart').getContext('2d');
    new Chart(dimCtx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'ابعاد در مقابل قیمت',
                data: chartData.dimensionVsPrice.map(d => ({ x: d.dimension, y: d.price })),
                backgroundColor: '#2575fc',
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'ابعاد (سانتی‌متر)' } },
                y: { title: { display: true, text: 'قیمت (تومان)' }, beginAtZero: true }
            }
        }
    });
}