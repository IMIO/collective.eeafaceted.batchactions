*** Settings ***
Documentation  collective.eeafaceted.batchactions keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.1 syntax (FOR ... END; shared with the Plone 4.3 environment, RF 3.2.2).
...            The folder /folder gets the faceted navigation with the faceted-table-items layout
...            (collective.eeafaceted.z3ctable: every row is selected on load) and, when given, a batch
...            actions marker interface (remote keyword "Enable faceted table" of testing.py).
...            Default eea criterion: portal type Page.
...            Selectors: eea.facetednavigation, collective.eeafaceted.z3ctable, z3c.form ids and this package.
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${FOLDER}  folder
${MARKER}  collective.eeafaceted.batchactions.interfaces.IBatchActionsMarker
# also shows no-overlay-transition-batch-action (testing.zcml)
${NO_OVERLAY_MARKER}  collective.eeafaceted.batchactions.testing.IRobotBatchActionsMarker
${ACTIONS}  css=#batch-actions
${TABLE}  css=#faceted_table
${SELECT_ALL}  css=#select_unselect_items
${PUBLISH}  Reviewer publishes content


*** Keywords ***
Set up the site
    [Documentation]  As in an iA.Docs site: faceted table, actions panel column, masterselect widgets
    Open test browser
    # the table overflows under the right column (select all checkbox) in a narrower window
    Set window size  1920  1200
    Enable autologin as  Manager
    Apply profile  collective.eeafaceted.z3ctable:default
    Apply profile  imio.actionspanel:default
    Apply profile  plone.formwidget.masterselect:default

Create a faceted table folder
    [Documentation]  /folder with the pages @{titles}, faceted table, providing ${marker} unless empty
    [Arguments]  ${marker}  @{titles}
    Create content  type=Folder  id=${FOLDER}  title=Folder
    Enable faceted table  /${FOLDER}  ${marker}
    ${uid}=  Path to uid  /${PLONE_SITE_ID}/${FOLDER}
    FOR  ${title}  IN  @{titles}
        Create content  type=Document  container=${uid}  title=${title}
    END

Open the folder
    [Arguments]  ${hash}=${EMPTY}
    Go to  ${PLONE_URL}/${FOLDER}${hash}
    The table is loaded

The table is loaded
    Wait until page contains element  ${TABLE}
    Wait until element is not visible  css=.faceted-lock-overlay

Mark the page
    [Documentation]  A flag in the window, lost when the page is reloaded
    Execute javascript  window.robotPageMark = true;

The page was not reloaded
    ${marked}=  Execute javascript  return window.robotPageMark === true;
    Should be true  ${marked}

Log in as the Zope admin
    [Documentation]  The site owner of the Zope root (delete-batch-action is available_for_zope_admin)
    Log in with the login form  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}

Row checkbox
    [Arguments]  ${title}
    [Return]  xpath=//table[@id="faceted_table"]//tr[td[contains(@class, "td_cell_Title")][normalize-space()="${title}"]]//input[@name="select_item"]

Select the rows
    [Documentation]  Only the rows of @{titles} selected
    [Arguments]  @{titles}
    Unselect every row
    FOR  ${title}  IN  @{titles}
        ${checkbox}=  Row checkbox  ${title}
        Select checkbox  ${checkbox}
    END

Unselect every row
    [Documentation]  The header checkbox toggles every row; rows are all selected on load
    ${checked}=  Get element count  css=#faceted_table input[name="select_item"]:checked
    Run keyword if  ${checked}  Click element  ${SELECT_ALL}
    Page should not contain element  css=#faceted_table input[name="select_item"]:checked

Click the batch action
    [Arguments]  ${name}
    Click button  css=#${name}-but

The batch action is shown
    [Documentation]  Button ${name}-but under the faceted table, labelled ${label}
    [Arguments]  ${name}  ${label}
    Element should be visible  css=#viewlet-bottom-above-nav #batch-actions #${name}-but
    Element attribute value should be  css=#${name}-but  value  ${label}

The batch action is not shown
    [Arguments]  ${name}
    Page should not contain element  css=#${name}-but

No batch action is shown
    Page should contain element  ${TABLE}
    Page should not contain element  ${ACTIONS}

The alert says
    [Arguments]  ${message}
    ${text}=  Handle alert  ACCEPT
    Should be equal  ${text}  ${message}

The modal says
    [Arguments]  ${text}
    Element should contain  ${MODAL}  ${text}

The modal does not say
    [Arguments]  ${text}
    Element should not contain  ${MODAL}  ${text}

Select the transition
    [Documentation]  In the modal or on the form page
    [Arguments]  ${transition}
    Select from list by label  css=#form-widgets-transition  ${transition}

Apply the form page
    Click button  css=#form-buttons-apply

The state is
    [Documentation]  State column of the row of ${title}
    [Arguments]  ${title}  ${state}
    Wait until element contains
    ...  xpath=//table[@id="faceted_table"]//tr[td[contains(@class, "td_cell_Title")][normalize-space()="${title}"]]/td[contains(@class, "td_cell_review_state")]
    ...  ${state}

The table lists
    [Arguments]  @{titles}
    ${count}=  Get length  ${titles}
    Wait until keyword succeeds  10s  0.5s  The table has rows  ${count}
    FOR  ${title}  IN  @{titles}
        Element should contain  ${TABLE}  ${title}
    END

The table has rows
    [Arguments]  ${count}
    ${rows}=  Get element count  css=#faceted_table tbody td.td_cell_Title
    Should be equal as integers  ${rows}  ${count}

The location is
    [Arguments]  ${url}
    Wait until keyword succeeds  10s  0.5s  Location should be  ${url}

Choose the batch action
    [Documentation]  "Batch action choice" of an add/remove/replace/overwrite form, by label
    [Arguments]  ${label}
    ${select}=  Modal element  form-widgets-action_choice
    Select from list by label  ${select}  ${label}

The value fields shown are
    [Documentation]  removed_values and added_values fields of an add/remove/replace/overwrite form: True or False
    [Arguments]  ${removed}  ${added}
    ${removed_field}=  Modal element  formfield-form-widgets-removed_values
    ${added_field}=  Modal element  formfield-form-widgets-added_values
    Run keyword if  ${removed}  Wait until element is visible  ${removed_field}
    ...  ELSE  Wait until element is not visible  ${removed_field}
    Run keyword if  ${added}  Wait until element is visible  ${added_field}
    ...  ELSE  Wait until element is not visible  ${added_field}
