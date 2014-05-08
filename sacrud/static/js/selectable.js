$(function() {
    $('table > tbody').selectable({
        // filter: ':not(td)',
        filter: 'tr',
        cancel: 'a',
        selected: function(event, ui) {
            $(ui.selected).addClass('table-tr-selected-class');
            // console.log(ui.selected);
            // console.log($(this).data('uiSelectable').selectees.filter('.ui-selected'));
        },
        unselected: function(event, ui) {
            $(ui.unselected).removeClass('table-tr-selected-class');
        },
        // create: function(event, ui) {},
        // start: function(event, ui) {},
        // selecting: function(event, ui) {},
        // stop: function(event, ui) {},
    });
});
