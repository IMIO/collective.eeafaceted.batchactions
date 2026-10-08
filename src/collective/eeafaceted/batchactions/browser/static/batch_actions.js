collective_batch_actions = {};

collective_batch_actions.init_button = function () {

  if (typeof jQuery === "undefined") {
    // viewlet in the page itself: the plone bundle makes jQuery global asynchronously
    window.addEventListener("load", collective_batch_actions.init_button);
    return;
  }
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
        if (!$(ba_form).hasClass('custom-overlay')) {
          ba_form.submit();
        }
    }

  });
};

collective_batch_actions.initializeOverlays = function (ba_form) {
    // the form posted with the selected uids, shown in a Plone modal (pat-plone-modal)
    if (!$.fn.patPloneModal) {
        ba_form.submit();
        return;
    }
    $.post(ba_form.action, $(ba_form).serialize() + '&ajax_load=1', function (html) {
        var trigger = $('<a href="#" />').hide().appendTo('body');
        trigger.on('hidden.plone-modal.patterns', function () { trigger.remove(); });
        trigger.patPloneModal({
            html: html,
            automaticallyAddButtonActions: false,
            onRender: collective_batch_actions.ajaxApply
        });
        trigger.click();
    });
};

collective_batch_actions.ajaxApply = function (modal) {
    // Apply posted over ajax (ajax_load: the form answers 204), then the modal is closed and the faceted
    // table refreshed (or the returned file downloaded) by imio.helpers; its submitFormHelper only binds
    // input buttons, Plone 6 forms have button elements
    var form = $('.modal-body form', modal.$modal);
    $('#form-buttons-apply', form).on('click', function () {
        var data = form.serializeArray();
        data.push({name: this.name, value: this.value}, {name: 'ajax_load', value: true});
        $.ajax({
            type: 'POST',
            url: form.attr('action'),
            data: data,
            dataType: 'binary',
            responseType: 'arraybuffer',
            cache: false
        }).done(function (data, textStatus, request) {
            modal.hide();
            submitFormHelperOnsuccessDefault(data, textStatus, request);
        });
    });
};
