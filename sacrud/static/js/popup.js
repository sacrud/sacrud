$(function() {
    $(document).on('click', '.action_button', function () {
        // $('.popup').css('display', 'table');
        // $('.popup').css('position', 'absolute');
        $('.popup').show();
    });

    $(document).on('click', '.popup-inner__content-link-text', function () {
        $('.popup').hide();
    });

    $(document).on('click', '.popup-button__item', function () {
        var status = $(this).data('status');
        if (status == 'cancel') {
            $('.popup').hide();
        } else if (typeof options != "undefined") {
            $(options.input_selected_action).val(status);
            $('#sacrud-form').submit();
        }
    });

    // $(document).on('click', function (e) {
    //     if (!($(e.target).closest('.popup-inner').length) && $('.popup').is(':visible')) {
    //         $('.popup').hide();
    //     }
    // });
});
