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

    $(".gnc-transaction-detail-button").click(function(){
        $($(this).attr("data-gnc-switch")).toggleClass("hidden");
        $(this).toggleClass("bi-chevron-up");
        $(this).toggleClass("bi-chevron-down");
    });
});

function transaction_recycle(description, value, postDate, contraAccounts) {
    $("input[form=add_transaction][name=description]").attr("value", description);
    $("input[form=add_transaction][name=value]").attr("value", value);
    $("select[form=add_transaction][name=contra_account_name]")[0].selectize .addItem(contraAccounts[0]);
}
