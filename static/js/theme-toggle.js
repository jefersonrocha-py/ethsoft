function updateThemeIcon(isDarkMode) {
    var themeIcon = document.getElementById('theme-icon');
    var themeToggle = document.getElementById('theme-toggle');

    if (!themeIcon || !themeToggle) {
        console.error('Elementos theme-icon ou theme-toggle não encontrados.');
        return;
    }

    if (isDarkMode) {
        themeIcon.classList.replace('fa-moon', 'fa-sun');
        themeToggle.setAttribute('aria-label', 'Ativar modo claro');
    } else {
        themeIcon.classList.replace('fa-sun', 'fa-moon');
        themeToggle.setAttribute('aria-label', 'Ativar modo escuro');
    }
}

function toggleTheme() {
    var html = document.documentElement;
    var isDarkMode = html.classList.toggle('dark-theme');
    
    updateThemeIcon(isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
}

document.addEventListener('DOMContentLoaded', function () {
    // Aplicar o tema salvo após o DOM estar pronto
    (function applySavedTheme() {
        var savedTheme = localStorage.getItem('theme');
        var html = document.documentElement;
        
        if (savedTheme === 'dark') {
            html.classList.add('dark-theme');
        } else {
            html.classList.remove('dark-theme');
        }

        // Atualizar o ícone apenas se o elemento existir
        var themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            updateThemeIcon(savedTheme === 'dark');
        }
    })();

    // Adicionar o listener ao botão de alternância de tema
    var themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});