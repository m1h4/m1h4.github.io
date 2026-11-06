(() => {
    const toggle = document.getElementById('menu-toggle');
    const navigation = document.getElementById('main-navigation');
    if (!toggle || !navigation) return;

    document.documentElement.classList.add('js');
    const setExpanded = (expanded) => {
        toggle.setAttribute('aria-expanded', String(expanded));
        navigation.classList.toggle('visible', expanded);
    };

    toggle.addEventListener('click', () => {
        setExpanded(toggle.getAttribute('aria-expanded') !== 'true');
    });
    navigation.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
            setExpanded(false);
            toggle.focus();
        }
    });
    window.matchMedia('(min-width: 601px)').addEventListener('change', () => setExpanded(false));
})();
