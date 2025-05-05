document.addEventListener('DOMContentLoaded', () => {
    // Initialize map
    initMap();

    // Form validation and submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleFormSubmit);
    }
});

function initMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Example coordinates for Tehran
    const tehran = [35.6892, 51.3890];

    // Initialize the map
    const map = L.map('map').setView(tehran, 15);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Add a marker for the location
    L.marker(tehran)
        .addTo(map)
        .bindPopup('پیانوت - تهران')
        .openPopup();
}

async function handleFormSubmit(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        subject: document.getElementById('subject').value,
        message: document.getElementById('message').value
    };

    if (!validateForm(formData)) return;

    try {
        // Here you would typically send the form data to your backend
        // For now, we'll just simulate a successful submission
        await simulateFormSubmission(formData);
        showSuccessMessage();
        resetForm();
    } catch (error) {
        showErrorMessage();
    }
}

function validateForm(data) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!data.name.trim()) {
        showError('لطفاً نام خود را وارد کنید');
        return false;
    }
    
    if (!emailRegex.test(data.email)) {
        showError('لطفاً یک ایمیل معتبر وارد کنید');
        return false;
    }
    
    if (!data.subject.trim()) {
        showError('لطفاً موضوع پیام را وارد کنید');
        return false;
    }
    
    if (!data.message.trim()) {
        showError('لطفاً پیام خود را وارد کنید');
        return false;
    }
    
    return true;
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger mt-3';
    alertDiv.textContent = message;
    
    const form = document.getElementById('contactForm');
    form.insertAdjacentElement('afterbegin', alertDiv);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

function showSuccessMessage() {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success mt-3';
    alertDiv.textContent = 'پیام شما با موفقیت ارسال شد';
    
    const form = document.getElementById('contactForm');
    form.insertAdjacentElement('afterbegin', alertDiv);
    
    setTimeout(() => alertDiv.remove(), 3000);
}

function resetForm() {
    document.getElementById('contactForm').reset();
}

async function simulateFormSubmission(formData) {
    return new Promise((resolve) => {
        setTimeout(resolve, 1000);
    });
}