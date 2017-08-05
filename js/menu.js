function toggleMenu() {
    var elements = document.getElementsByClassName('nav-primary');
    if (elements[0].classList.contains('visible') ) {
        elements[0].classList.remove('visible')
    } else {
        elements[0].classList.add('visible')
    }
}