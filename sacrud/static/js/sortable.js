$(function() {
    $('.sortable').sortable({
        connectWith: '.sortable',
        placeholder: 'widget_placeholder',
        revert: true,
        start: function(event, ui) {
            $('.widget_placeholder').append(ui.item.html());
            // $('.widget_placeholder').append(ui.item.context.outerHTML);
        },
        stop: function(event, ui) {
            var widget = ui.item.attr('name'),
                column = ui.item.parent().data('number'),
                position = $('.dashboard__column[data-number="'+column+'"]  .widget').index(ui.item),
                data = {'widget': widget, 'column': column, 'position': position};

            $.ajax({
                type: "POST",
                url: 'save_position',
                data: data,
                // success: function(result){
                // },
                // error: function (xhr, textStatus, errorThrown) {
                // }
            });
        },
        /*
        change: function(event, ui) {
        },
        receive: function(event, ui) {
        },
        */
    }).disableSelection();
});
