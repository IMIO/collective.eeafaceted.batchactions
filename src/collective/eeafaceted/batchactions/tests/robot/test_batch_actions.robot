*** Settings ***
Documentation  Batch actions under the faceted table: buttons, selection alert, overlay forms, page forms.
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  batchactions.robot
Test Setup  Set up the site
Test Teardown  Close all browsers


*** Variables ***
# a faceted query that is not the default one (eea writes the default query in the hash on load)
${SORTED_QUERY}  c1=Document&b_start=0&sort_on=sortable_title&reversed=on


*** Test Cases ***
The batch actions are shown under the table of a marked folder
    Create a faceted table folder  ${MARKER}  Alpha  Bravo
    Open the folder
    The batch action is shown  transition-batch-action  Change state
    The batch action is shown  testing-aruo-batch-action  testing-aruo-batch-action-but
    # available_for_zope_admin: not for a site Manager
    The batch action is not shown  delete-batch-action
    The batch action is not shown  update-wf-role-mappings-batch-action

No batch action on an unmarked folder
    Create a faceted table folder  ${EMPTY}  Alpha  Bravo
    Open the folder
    No batch action is shown

A batch action without selected element shows an alert
    Create a faceted table folder  ${MARKER}  Alpha  Bravo
    Open the folder
    Unselect every row
    Click the batch action  transition-batch-action
    The alert says  Please select at least one element.
    The modal is closed

Change the state of the selected elements in the overlay
    Create a faceted table folder  ${MARKER}  Alpha  Bravo  Charlie
    Open the folder
    Select the rows  Alpha  Charlie
    Mark the page
    Click the batch action  transition-batch-action
    The modal is open
    The modal says  This action will affect 2 element(s).
    Select the transition  ${PUBLISH}
    Apply the modal
    The modal is closed
    The table is loaded
    The state is  Alpha  published
    The state is  Charlie  published
    The state is  Bravo  private
    The page was not reloaded

Cancel closes the overlay and changes nothing
    Create a faceted table folder  ${MARKER}  Alpha  Bravo
    Open the folder
    Click the batch action  transition-batch-action
    The modal is open
    Select the transition  ${PUBLISH}
    Cancel the modal
    The modal is closed
    Open the folder
    The state is  Alpha  private
    The state is  Bravo  private

The Zope admin deletes the selected elements
    Create a faceted table folder  ${MARKER}  Alpha  Bravo  Charlie
    Log in as the Zope admin
    Open the folder
    The batch action is shown  delete-batch-action  Delete
    The batch action is shown  update-wf-role-mappings-batch-action  Update WF role mappings
    Select the rows  Alpha  Bravo
    Click the batch action  delete-batch-action
    The modal is open
    The modal says  This action will affect 2 element(s).
    Apply the modal
    The modal is closed
    The table lists  Charlie

An action without overlay opens its form page and comes back to the faceted query
    [Documentation]  overlay = False: the form is posted, Apply redirects to the folder URL with its hash
    Create a faceted table folder  ${NO_OVERLAY_MARKER}  Alpha  Bravo
    Open the folder  \#${SORTED_QUERY}
    Select the rows  Bravo
    Click the batch action  no-overlay-transition-batch-action
    Wait until page contains element  css=#form-widgets-transition
    Page should contain  This action will affect 1 element(s).
    Select the transition  ${PUBLISH}
    Apply the form page
    The location is  ${PLONE_URL}/${FOLDER}\#${SORTED_QUERY}
    The table is loaded
    The state is  Bravo  published
    The state is  Alpha  private

The add/remove action choice shows the relevant value fields
    Create a faceted table folder  ${MARKER}  Alpha  Bravo
    Open the folder
    Click the batch action  testing-aruo-batch-action
    The modal is open
    # default: Add items
    The value fields shown are  ${False}  ${True}
    Choose the batch action  Remove items
    The value fields shown are  ${True}  ${False}
    Choose the batch action  Replace some items by others
    The value fields shown are  ${True}  ${True}
    Choose the batch action  Overwrite
    The value fields shown are  ${False}  ${True}

The add/remove form description is plain English
    [Documentation]  Known issue on Plone 4 (MIGRATION.md): the en msgstr of both warnings are empty,
    ...              the description ends with the raw msgids.
    [Tags]  plone4-bug
    Create a faceted table folder  ${MARKER}  Alpha  Bravo
    Open the folder
    Click the batch action  testing-aruo-batch-action
    The modal is open
    The modal says  This action will affect 2 element(s).
    The modal does not say  field_can_not_be_empty_warning
    The modal does not say  aruo_action_replace_warning
