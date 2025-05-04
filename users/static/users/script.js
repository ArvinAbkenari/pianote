$(document).ready(function() {
    // Theme toggle functionality
    const themeToggle = $('.theme-toggle');
    const moonIcon = 'bi-moon-fill';
    const sunIcon = 'bi-sun-fill';

    // Sheet music filtering functionality
    $('.filter-list a').on('click', function(e) {
        e.preventDefault();
        const filterSection = $(this).closest('.filter-section');
        filterSection.find('a').removeClass('active');
        $(this).addClass('active');

        // Here you can add actual filtering logic
        // For now, just adding visual feedback
        const filterType = filterSection.find('h4').text();
        const filterValue = $(this).text();
        console.log(`Filtering ${filterType} by: ${filterValue}`);
    });

    // Sheet card hover animation
    $('.sheet-card').hover(
        function() { $(this).addClass('hover'); },
        function() { $(this).removeClass('hover'); }
    );

    function updateLogo() {
        const currentSrc = $(".navbar-brand img").attr("src");
        if ($("html").attr("data-theme") === "dark") {
            $(".navbar-brand img").attr("src", currentSrc.replace("logo.svg", "logo-dark.svg"));
        } else {
            $(".navbar-brand img").attr("src", currentSrc.replace("logo-dark.svg", "logo.svg"));
        }
    }

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        $('html').attr('data-theme', 'dark');
        themeToggle.find('i').removeClass(moonIcon).addClass(sunIcon);
    }
    updateLogo(); // Ensure logo updates on page load

    // Handle theme toggle click
    themeToggle.on('click', function() {
        const html = $('html');
        const icon = $(this).find('i');
        
        if (html.attr('data-theme') === 'dark') {
            html.removeAttr('data-theme');
            icon.removeClass(sunIcon).addClass(moonIcon);
            localStorage.setItem('theme', 'light');
        } else {
            html.attr('data-theme', 'dark');
            icon.removeClass(moonIcon).addClass(sunIcon);
            localStorage.setItem('theme', 'dark');
        }
        updateLogo(); // Update logo when theme changes
    });

    // Smooth scrolling for navigation links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this).attr('href');
        $('html, body').animate({
            scrollTop: $(target).offset().top - 70
        }, 800);
    });

    // Counter animation for statistics
    function animateCounter(element) {
        const target = parseInt($(element).text());
        $({ count: 0 }).animate({ count: target }, {
            duration: 2000,
            easing: 'swing',
            step: function() {
                $(element).text(Math.floor(this.count).toLocaleString('fa-IR'));
            },
            complete: function() {
                $(element).text(target.toLocaleString('fa-IR'));
            }
        });
    }

    // Start counter animation when element comes into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    $('.counter').each(function() {
        observer.observe(this);
    });

    // Sticky header behavior
    let lastScroll = 0;
    $(window).scroll(function() {
        const currentScroll = $(this).scrollTop();
        if (currentScroll > lastScroll && currentScroll > 100) {
            $('.sticky-top').addClass('scrolled');
        } else {
            $('.sticky-top').removeClass('scrolled');
        }
        lastScroll = currentScroll;
    });

    // FAQ Accordion custom behavior
    $('.accordion-button').on('click', function() {
        const isCollapsed = $(this).hasClass('collapsed');
        $('.accordion-button').not(this).addClass('collapsed');
        if (!isCollapsed) {
            $(this).removeClass('collapsed');
        }
    });

    // Add hover effect to social icons
    $('.social-icons a').hover(
        function() { $(this).addClass('hover'); },
        function() { $(this).removeClass('hover'); }
    );

    document.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

});