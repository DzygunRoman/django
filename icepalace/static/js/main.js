document.addEventListener('DOMContentLoaded', function() {
    // Добавляем активный класс к текущему пункту меню
    const currentUrl = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentUrl) {
            link.parentElement.classList.add('active');
        }
    });

    // Для выпадающего меню категорий
    if (currentUrl.includes('/products/')) {
        const dropdownToggle = document.querySelector('.dropdown-toggle');
        if (dropdownToggle) {
            dropdownToggle.parentElement.classList.add('active');
        }
    }
});