// Modal functionality for authentication
$(document).ready(function() {

    // Show modal when profile icon is clicked
    $('.profile-icon').on('click', function() {
        const modal = $('#authModal');
        modal.css('visibility', 'visible');
        modal.addClass('show');
        $('body').addClass('modal-open');
    });

    // Function to close modal
    function closeModal(modal) {
        modal.removeClass('show');
        $('body').removeClass('modal-open');
        setTimeout(() => {
            if (!modal.hasClass('show')) {
                modal.css('visibility', 'hidden');
            }
        }, 400);
    }

    // Close modal when clicking close button
    $('.close-modal').on('click', function(e) {
        e.stopPropagation();
        closeModal($('#authModal'));
    });

    // Close modal when clicking outside
    $('.auth-modal').on('click', function(e) {
        if (e.target === this) {
            closeModal($(this));
        }
    });

    // Tab switching functionality
    $('.tab-btn').on('click', function() {
        const tab = $(this).data('tab');
        $('.tab-btn').removeClass('active');
        $(this).addClass('active');
        $('.auth-form').removeClass('active');
        $(`#${tab}Form`).addClass('active');
    });

    // Update toast messages to Farsi and set background colors for success and failure
    function showToast(title, message, isSuccess) {
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');
        const signupToast = document.getElementById('signupToast');

        toastTitle.textContent = title;
        toastMessage.textContent = message;

        // Set background color based on success or failure
        if (isSuccess) {
            signupToast.classList.remove('text-bg-danger');
            signupToast.classList.add('text-bg-success');
        } else {
            signupToast.classList.remove('text-bg-success');
            signupToast.classList.add('text-bg-danger');
        }

        const bootstrapToast = new bootstrap.Toast(signupToast);
        bootstrapToast.show();
    }

    document.getElementById('signupForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            if (data.success) {
                showToast('موفقیت', 'ثبت نام با موفقیت انجام شد!', true);
                this.reset();
            } else {
                showToast('خطا', 'ثبت نام ناموفق: ' + data.error, false);
            }
        })
        .catch(error => {
            console.error('There was a problem with the signup request:', error);
            showToast('خطا', 'مشکلی در درخواست ثبت نام وجود داشت.', false);
        });
    });

    document.getElementById('signinForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(this);

        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(async response => {
            const data = await response.json();
            if (response.ok) {
                showToast('موفقیت', 'ورود با موفقیت انجام شد!', true);
                this.reset();
            } else {
                const errorMsg = data.error || Object.values(data.errors || {}).flat().join(', ') || 'رمز ورود یا نام کاربری اشتباه است!';
                showToast('خطا!', 'ورود ناموفق: ' + errorMsg, false);
            }
        })
        .catch(error => {
            console.error('There was a problem with the signin request:', error);
            showToast('خطا', 'مشکلی در درخواست ورود وجود داشت.', false);
        });
        
    });
});