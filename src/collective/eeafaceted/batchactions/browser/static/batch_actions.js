collective_batch_actions = {};

collective_batch_actions.init_button = function () {

  if ( $(".faceted-table-results").length && $('.faceted-table-results')[0] == undefined ) {
    $('#batch-actions').hide();
  }

  $('.batch-action-but').click(function (e) {
    e.preventDefault();
    select_item_name = $(this).parents("div#batch-actions").data().select_item_name;
    var uids = selectedCheckBoxes(select_item_name);
    if (!uids.length) { alert(no_selected_items); return false;}
    var referer = document.location.href.replace('#','!').replace(/&/g,'@');
    var ba_form = $(this).parent()[0];
    var form_id = ba_form.id;
    if(typeof document.batch_actions === "undefined") {
        document.batch_actions = [];
    }
    if(document.batch_actions[form_id] === undefined) {
        document.batch_actions[form_id] = ba_form.action;
    }
    var uids_input = $(ba_form).find('input[name="uids"]');
    if (uids_input.length === 0) {
        uids_input = $('<input type="hidden" name="uids" value="" />');
        $(ba_form).append(uids_input);
    }
    uids_input.val(uids);
    ba_form.action = document.batch_actions[form_id] + '?referer=' + referer;
    if ($(ba_form).hasClass('do-overlay')) {
      collective_batch_actions.initializeOverlays(ba_form);
    }
    else {
      ba_form.submit();
    }

  });
};

collective_batch_actions.initializeOverlays = function (ba_form) {
    // Add batch actions popup
    $(ba_form).prepOverlay({
        api: true,
        subtype: 'ajax',
        closeselector: '[name="form.buttons.cancel"]',
        config: {
            onBeforeLoad : function (e) {
                submitFormHelper(this.form);
                return true;
            },
        }
    });
};
