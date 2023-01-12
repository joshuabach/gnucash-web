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

    var editTransactionModal = document.getElementById('edit-transaction');
    editTransactionModal.addEventListener('show.bs.modal', function (event) {
        // Button that triggered the modal
        var button = event.relatedTarget;

        $("input[form=edit_transaction][name=guid]")
            .attr("value", button.getAttribute('data-bs-transaction-guid'));
        $("input[form=edit_transaction][name=description]")
            .attr("value", button.getAttribute('data-bs-transaction-description'));
        $("input[form=edit_transaction][name=value]")
            .attr("value", button.getAttribute('data-bs-transaction-value'));
        $("input[form=edit_transaction][name=date]")
            .attr("value", button.getAttribute('data-bs-transaction-post-date'));

        editTransactionModal.reset = function() {
            // Reset classic form inputs
            document.getElementById('edit_transaction').reset();

            // Reset sign
            if (button.getAttribute('data-bs-transaction-sign') == "-1") {
                $("input#edit-transaction-sign-withdraw").attr('checked', true);
            } else {
                $("input#edit-transaction-sign-deposit").attr('checked', true);
            }

            // Reset selectize
            $("select[form=edit_transaction][name=contra_account_name]")[0]
                .selectize.addItem(button.getAttribute('data-bs-transaction-contra-account'));
        };

        editTransactionModal.reset();
    });
});

function transaction_recycle(description, value, postDate, contraAccount) {
    $("input[form=new_transaction][name=description]").attr("value", description);
    $("input[form=new_transaction][name=value]").attr("value", value);
    $("select[form=new_transaction][name=contra_account_name]")[0].selectize.addItem(contraAccount);
}
