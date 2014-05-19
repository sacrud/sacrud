$(function() {

    var options = {
        'tr_selected_class': 'table-tr-selected-class',
        'state_disable_class': 'toolbar-button__item_state_disable',
        'all_checkboxes_button': '#selected_all_item',
        'table_checkboxes': 'input[name="selected_item"]',
        'table_checkboxes_checked': 'input[name="selected_item"]:checked',
        'input_selected_action': 'input[name="selected_action"]',
        'div_action_button': '.action_button',
    };


    $('table > tbody').selectable({
        // filter: ':not(td)',
        filter: 'tr',
        cancel: 'a, input',
        selected: function (event, ui) {
            $(ui.selected).addClass(options.tr_selected_class);
            $(ui.selected).find(options.table_checkboxes).prop('checked', true).change();
            $(options.all_checkboxes_button).prop('checked', false);
            // console.log(ui.selected);
            // console.log($(this).data('uiSelectable').selectees.filter('.ui-selected'));
        },
        unselected: function (event, ui) {
            $(ui.unselected).removeClass(options.tr_selected_class);
            $(ui.unselected).find(options.table_checkboxes).prop('checked', false).change();
        },
    });

    function change_buttons () {
        if ($(options.table_checkboxes_checked).length) {
            $('.'+options.state_disable_class).removeClass(options.state_disable_class);
        } else {
            $(options.div_action_button).addClass(options.state_disable_class);
            $(options.all_checkboxes_button).prop('checked', false);
        }
    }

    function check_checkbox (checkbox) {
        var $parent_tr = checkbox.parents('.sacrud-grid-content-grid__body-row');
        if (checkbox.prop('checked')) {
            $parent_tr.addClass(options.tr_selected_class);
            $parent_tr.addClass('ui-selected');
        } else {
            $parent_tr.removeClass(options.tr_selected_class);
            $parent_tr.removeClass('ui-selected');
        }
    }

    $(options.table_checkboxes_checked).each(function (){
        check_checkbox($(this));
    });

    change_buttons();

    $(document).on('change', options.table_checkboxes , function () {
        check_checkbox($(this));
        change_buttons();
    });

    $(document).on('click', '.'+options.state_disable_class , function (event) {
        event.stopImmediatePropagation();
    });

    $(document).on('change', options.all_checkboxes_button , function () {
        $(options.table_checkboxes).prop('checked', $(this).prop('checked')).change();
    });

    $(document).on('click', options.div_action_button, function () {
        $(options.input_selected_action).val($(this).data('status'));
        $('#sacrud-form').submit();
    });
});
