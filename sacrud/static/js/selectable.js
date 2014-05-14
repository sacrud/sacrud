$(function() {
    $('table > tbody').selectable({
        // filter: ':not(td)',
        filter: 'tr',
        cancel: 'a, input',
        selected: function(event, ui) {
            $(ui.selected).addClass('table-tr-selected-class');
            $(ui.selected).find('input[type="checkbox"]').prop('checked', true);
            // console.log(ui.selected);
            // console.log($(this).data('uiSelectable').selectees.filter('.ui-selected'));
        },
        unselected: function(event, ui) {
            $(ui.unselected).removeClass('table-tr-selected-class');
            $(ui.unselected).find('input[type="checkbox"]').prop('checked', false);
        },
        // create: function(event, ui) {},
        // start: function(event, ui) {},
        // selecting: function(event, ui) {},
        // stop: function(event, ui) {},
    });

    function check_checkbox (checkbox) {
        var $parent_tr = checkbox.parents('.sacrud-grid-content-grid__body-row');
        if (checkbox.prop('checked')) {
            $parent_tr.addClass('table-tr-selected-class');
            $parent_tr.addClass('ui-selected');
        } else {
            $parent_tr.removeClass('table-tr-selected-class');
            $parent_tr.removeClass('ui-selected');
        }
    }

    $(document).on('change', 'input[type="checkbox"]' , function (event) {
        check_checkbox($(this));
    });

    $('input[type="checkbox"]:checked').each(function(){
        check_checkbox($(this));
    });
});
