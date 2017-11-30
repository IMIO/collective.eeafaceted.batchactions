Changelog
=========


0.3 (unreleased)
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
