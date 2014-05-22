 $(function() {
    $(document).on('click', '.action_button', function () {
        $('.popup').css('display', 'table');
        $('.popup').css('position', 'absolute');
        // $('.popup').find('select[tourshcooltrainingfield=""]').val($(this).attr('data-event'))
        // return false;
    });

    $(document).on('click', '.popup-inner__content-delete-cancel, .popup-inner__content-link-text', function () {
        $('.popup').hide();
    });

    // $(document).on('click', function (e) {
    //     if (!($(e.target).closest('.popup-inner').length) && $('.popup').is(':visible')) {
    //         $('.popup').hide();
    //     }
    // });
});
