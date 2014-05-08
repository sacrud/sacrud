$(function() {
    $('.sortable').sortable({
        connectWith: '.sortable',
        placeholder: 'widget_placeholder',
        revert: true,
        /*
        start: function(event, ui) {
        },
        stop: function(event, ui) {
        },
        change: function(event, ui) {
        },
        receive: function(event, ui) {
        },
        */
    }).disableSelection();

    $(document).on('sortstart', '.sortable', function(event, ui) {
        $('.widget_placeholder').append(ui.item.html());
        // $('.widget_placeholder').append(ui.item.context.outerHTML);
    });
});
