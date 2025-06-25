Changelog
=========


1.16.4 (2025-06-25)
-------------------

- Renamed `TransitionBatchActionForm.getAvailableTransitionsVoc` to
  `TransitionBatchActionForm.get_available_transitions_voc`.
  [gbastien]
- Moved `LabelsBatchActionForm` can change labels computation to
  `LabelsBatchActionForm._can_change_labels` so it is easy to override.
  [gbastien]

1.16.3 (2025-05-08)
-------------------

- Updated is_permitted function to check multiple permissions.
  [chris-adam]

1.16.2 (2025-02-28)
-------------------

- Overrided `Form.__call__` to not render if request reponse status
  is 204 (No content) as it is already the case when response status is 302 or
  the portal message is not displayed after faceted refresh because
  it was already displayed on the closing form.
  [gbastien]
- Added Attributes in modified call to specify which attribute has been modified.
  [cadam, sgeulette]
- Corrected typo
  [sgeulette]

1.16.1 (2025-02-03)
-------------------

- Check again `self.do_apply` in `BaseBatchActionForm.handleApply` to avoid
  nasty behaviors.
  [gbastien]

1.16.0 (2024-12-19)
-------------------

- Overrided `ContactBaseBatchActionForm.available` method to handle anonymous
  search correctly.
  [sgeulette]

1.15 (2024-04-10)
-----------------

- Import `safe_encode` from `imio.pyutils` instead `imio.helpers`.
  [gbastien]
- Check `available` in `update` instead in `handleApply` so form is not
  displayed at all if user have not access.
  [gbastien]

1.14 (2023-09-04)
-----------------

- In `BaseARUOBatchActionForm._apply`, return the elements that were actually
  updated so it may be used when overriding the base view.
  [gbastien]
- Avoided exception when a field value is None and we want to get a list or set
  [sgeulette]

1.13 (2023-07-12)
-----------------

- Added `BaseARUOBatchActionForm`, a class factorizing the action that
  `add/remove/update/overwrite` values on an attribute of an object
  (originally used for the `LabelsBatchActionForm`) so it is easier to reuse
  for other similar actions. `LabelsBatchActionForm` is now based on that
  `BaseARUOBatchActionForm`.
  [gbastien]
- Activated `delete-batch-action` for zope admin
  [sgeulette]

1.12 (2023-06-27)
-----------------

- Added action to `Update WF role mappings`.
  Moved `available_permission` functionality from `ContactBaseBatchActionForm`
  to `BaseBatchActionForm` so it is available for any action.
  Added `BaseBatchActionForm.available_for_zope_admin` that makes an action
  only available to the Zope admin.
  [gbastien]
- Make `UpdateWFRoleMappingsActionForm` use
  `imio.helpers.workflow.update_role_mappings_for`.
  [gbastien]

1.11 (2022-05-06)
-----------------

- Avoided exception when referer url contains non ascii char.
  [sgeulette]

1.10 (2022-02-10)
-----------------

- Corrected UnicodeDecodeError on transition title.
  [sgeulette]

1.9 (2021-12-06)
----------------

- Checked permission on context (in ContactBaseBatchActionForm).
  [sgeulette]

1.8 (2021-07-16)
----------------

- Highlight message about number of elements that will be updated
  by the action on the popup.
  [gbastien]

1.7 (2021-07-16)
----------------

- Adapted code to be able to display several tables on same page
  (and so several batchactions viewlets):

  - Added possibility to define the name of the `CheckBoxColumn`
    (still `select_item` by default);
  - Introduce idea of section for the viewlet and the batch actions so it is
    possible to display different actions on different viewlets or different
    views of same context.

  [gbastien]
- Added method `BaseBatchActionForm._final_update` called when every other
  `update` methods have been called.
  [gbastien]
- Added `BaseBatchActionForm.apply_button_title` attribute to formalize
  management of `apply` button title, that will be `Apply` by default but that
  may be changed to fit the current batch action.
  [gbastien]
- Added `DeleteBatchActionForm` a delete elements batch action.
  [gbastien]
- Require `plone.formwidget.masterselect<2.0.0` as it is only for `Plone5.2+/Py3`.
  [gbastien]

1.6 (2020-12-21)
----------------

- After action applied, do not reload the entire page,
  just reload the current faceted results.
  [gbastien]
- Use `CheckBoxFieldWidget` instead `SelectFieldWidget` to manage labels to
  (un)select in `LabelsBatchActionForm` to avoid manipulation with
  `CTRL+click` for selection. Adapted and rationalized translations.
  [gbastien]
- Add a `collective.fingerpointing` entry when applying action to know
  which action was applied on how much elements.
  [gbastien]

1.5 (2020-04-23)
----------------

- Make sure elements are treated in received `uids` order. Need to rely on
  `imio.helpers` to use `content.uuidsToCatalogBrains(ordered=True)`.
  [gbastien]

1.4 (2019-11-25)
----------------

- Added view to change labels. (button is not added)
  [sgeulette]
- Added base view to change a collective.contact.widget field.
  [sgeulette]

1.3 (2019-05-16)
----------------

- Moved method `browser.views.brains_from_uids` to `utils`, added helper method
  `utils.listify_uids` that turns the data uids that is a string with each UID
  separated by a comma into a real python list.
  [gbastien]
- Display number of elements affected by action in the batch action form description.
  [gbastien]

1.2 (2019-03-08)
----------------

- Added weight attribute on batch action forms to order them.
  [sgeulette]
- Improved brains_from_uids
  [sgeulette]
- Added utils method
  [sgeulette]

1.1 (2018-08-31)
----------------

- Don't apply changes if form errors
  [sgeulette]

1.0 (2018-06-20)
----------------

- Moved js variables to `collective.eeafaceted.z3ctable`.
  [gbastien]

0.7 (2018-06-06)
----------------

- Render batch action form in overlay by default, but otherwise with form 'overlay' attribute set to False.
  [sgeulette]

0.6 (2018-01-06)
----------------

- Added condition on apply button.
  [sgeulette]
- Added _update_widgets method
  [sgeulette]

0.5 (2018-01-05)
----------------

- Some changes to made it working with a simple z3c.table.
  [sgeulette]

0.4.1 (2017-12-01)
------------------

- Fixed english po file.
  [gbastien]

0.4 (2017-12-01)
----------------

- Added `collective_eeafaceted_batchactions_js_variables.js` that allows to
  translate the `no_selected_items` message.
  [gbastien]

0.3 (2017-11-30)
----------------

- Renamed `BatchActionForm` to `BaseBatchActionForm` to show that it is the base
  form to inherit from to build new batch action.  Make it inherit from
  `Form` instead `EditForm`.
  [gbastien]
- Refactored the way form is updated and applied : two methods are there to be
  overrided : `_update` that is called in the `update` process and `_apply` that
  is called by `handleApply`.  This way it is easy to build an new action
  without having to think about basic default behavior.
  [gbastien]
- In the `TransitionBatchActionForm`, sort selectable transitions alphabetically.
  [gbastien]

0.2 (2017-11-24)
----------------

- Use `getMultiAdapter` instead `restrictedTraverse` when getting the form
  in the viewlet to speed up things.
  [gbastien]
- Added attribute `button_with_icon` to a batch action, if set to True,
  a particular CSS class is added to the button so it can be skinned
  with an icon easily.
  [gbastien]
- Register a `batch_actions.css` resource for basic styling.
  [gbastien]

0.1 (2017-11-23)
----------------

- Initial release.
  [IMIO]
