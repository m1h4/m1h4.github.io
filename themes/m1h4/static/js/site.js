(() => {
    const toggle = document.getElementById('menu-toggle');
    const navigation = document.getElementById('main-navigation');
    if (toggle && navigation) {
        document.documentElement.classList.add('js');
        const expand = (open) => {
            toggle.setAttribute('aria-expanded', String(open));
            navigation.classList.toggle('visible', open);
        };
        toggle.addEventListener('click', () => expand(toggle.getAttribute('aria-expanded') !== 'true'));
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
                expand(false);
                toggle.focus();
            }
        });
        window.matchMedia('(min-width: 701px)').addEventListener('change', () => expand(false));
    }

    const appearance = document.getElementById('appearance');
    if (appearance) {
        appearance.value = document.documentElement.dataset.theme || 'system';
        appearance.closest('label').hidden = false;
        appearance.addEventListener('change', () => {
            if (appearance.value === 'system') delete document.documentElement.dataset.theme;
            else document.documentElement.dataset.theme = appearance.value;
            try {
                if (appearance.value === 'system') localStorage.removeItem('appearance');
                else localStorage.setItem('appearance', appearance.value);
            } catch (_) { /* The selection still applies for this visit. */ }
        });
    }

    const links = Array.from(document.querySelectorAll('[data-gallery]'));
    if (!links.length || typeof HTMLDialogElement === 'undefined' || !HTMLDialogElement.prototype.showModal) return;
    const dialog = document.createElement('dialog');
    dialog.className = 'photo-dialog';
    dialog.setAttribute('aria-labelledby', 'photo-title');
    dialog.innerHTML = '<div class="dialog-toolbar"><h2 id="photo-title"></h2><button type="button" class="dialog-close" autofocus>Close ×</button></div><img class="dialog-image" alt=""><div class="dialog-bottom"><a class="original-link">Open original image ↗</a><div class="dialog-controls"><button type="button" class="previous" aria-label="Previous photo">←</button><span class="photo-count" role="status" aria-live="polite" aria-atomic="true"></span><button type="button" class="next" aria-label="Next photo">→</button></div></div>';
    document.body.append(dialog);
    const photo = dialog.querySelector('img');
    const title = dialog.querySelector('h2');
    const count = dialog.querySelector('.photo-count');
    const original = dialog.querySelector('.original-link');
    let index = 0;
    let opener;
    const showPhoto = (next) => {
        index = (next + links.length) % links.length;
        const link = links[index];
        title.textContent = link.dataset.title;
        count.textContent = (index + 1) + ' / ' + links.length;
        photo.alt = link.querySelector('img').alt;
        photo.width = Number(link.dataset.width);
        photo.height = Number(link.dataset.height);
        photo.src = link.href;
        original.href = link.href;
    };
    links.forEach((link, position) => {
        link.setAttribute('aria-label', 'Enlarge: ' + link.dataset.title);
        link.setAttribute('aria-haspopup', 'dialog');
        link.addEventListener('click', (event) => {
            if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            opener = link;
            showPhoto(position);
            dialog.showModal();
            document.documentElement.classList.add('gallery-open');
        });
    });
    dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.querySelector('.previous').addEventListener('click', () => showPhoto(index - 1));
    dialog.querySelector('.next').addEventListener('click', () => showPhoto(index + 1));
    dialog.addEventListener('keydown', (event) => {
        if (event.key === 'Tab') {
            const controls = dialog.querySelectorAll('button, a[href]');
            const first = controls[0];
            const last = controls[controls.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            event.preventDefault();
            showPhoto(index + (event.key === 'ArrowRight' ? 1 : -1));
        }
    });
    dialog.addEventListener('click', (event) => {
        if (event.target === dialog) {
            const bounds = dialog.getBoundingClientRect();
            if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
        }
    });
    dialog.addEventListener('close', () => {
        document.documentElement.classList.remove('gallery-open');
        if (opener) opener.focus();
    });
})();
