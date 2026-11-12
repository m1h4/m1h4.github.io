(() => {
    const appearance = document.getElementById('appearance');
    const sources = document.querySelectorAll('[data-theme-source]');
    const updatePictures = () => {
        const theme = document.documentElement.dataset.theme;
        for (const source of sources) {
            source.media = theme === 'dark' ? 'all' : theme === 'light' ? 'not all' : '(prefers-color-scheme: dark)';
        }
    };
    updatePictures();
    if (!appearance) return;
    appearance.value = document.documentElement.dataset.theme || 'system';
    appearance.closest('label').hidden = false;
    appearance.addEventListener('change', () => {
        if (appearance.value === 'system') delete document.documentElement.dataset.theme;
        else document.documentElement.dataset.theme = appearance.value;
        updatePictures();
        try {
            if (appearance.value === 'system') localStorage.removeItem('appearance');
            else localStorage.setItem('appearance', appearance.value);
        } catch (_) { /* The selection still applies for this visit. */ }
    });
})();
