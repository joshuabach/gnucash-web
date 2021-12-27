/*
 * Auto hide navbar on scroll down, show on scroll up.
 * Taken from: https://bootstrap-menu.com/detail-autohide.html
 */
document.addEventListener("DOMContentLoaded", function(){
    navbar = document.getElementById('navbar');

    var last_scroll_top = 0;
    window.addEventListener('scroll', function() {
        let scroll_top = window.scrollY;
        if(scroll_top < last_scroll_top) {
            navbar.classList.remove('scrolled-down');
            navbar.classList.add('scrolled-up');
        }
        else {
            navbar.classList.remove('scrolled-up');
            navbar.classList.add('scrolled-down');
        }
        last_scroll_top = scroll_top;
    });
});
