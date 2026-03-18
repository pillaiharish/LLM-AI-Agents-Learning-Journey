document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const hamburger = document.getElementById('hamburger');
    const themeToggle = document.getElementById('theme-toggle');
    const navItems = document.querySelectorAll('.nav-item');
    const pages = document.querySelectorAll('.tool-page');

    // Theme
    const savedTheme = localStorage.getItem('devtools-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('devtools-theme', next);
    });

    // Navigation
    function navigateTo(page) {
        navItems.forEach(n => n.classList.toggle('active', n.dataset.page === page));
        pages.forEach(p => p.classList.toggle('active', p.id === `page-${page}`));
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            window.location.hash = `/${item.dataset.page}`;
        });
    });

    // Hash routing
    function handleHash() {
        const hash = window.location.hash.replace('#/', '').replace('#', '');
        const page = hash || 'token-calculator';
        navigateTo(page);
    }

    window.addEventListener('hashchange', handleHash);
    handleHash();

    // Mobile sidebar
    hamburger.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
    });

    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
    });

    // Logo click → home
    document.getElementById('sidebar-logo').addEventListener('click', () => {
        window.location.hash = '/token-calculator';
    });
});
