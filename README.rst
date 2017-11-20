.. image:: https://travis-ci.org/collective/collective.eeafaceted.batchactions.svg?branch=master
   :target: https://travis-ci.org/collective/collective.eeafaceted.batchactions

.. image:: https://coveralls.io/repos/collective/collective.eeafaceted.batchactions/badge.png?branch=master
  :target: https://coveralls.io/r/collective/collective.eeafaceted.batchactions?branch=master


==================================
collective.eeafaceted.batchactions
==================================

This package gives the possibility to define batch actions on elements displayed in a eea.facetednavigation dashboard

* `Source code @ GitHub <https://github.com/collective/collective.eeafaceted.batchactions>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/collective.eeafaceted.batchactions>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/collective/collective.eeafaceted.batchactions>`_

How it works
============

This will display BrowserViews registered for `collective.eeafaceted.batchactions.interfaces.IBatchActionsMarker` or
an interface subclassing it at the bottom of a eea.facetednavigation dashboard.

Using a `collective.eeafaceted.z3ctable` `CheckBoxColumn`, you will be able to select elements to tigger the batch action on.

Batch actions are overridable from a faceted navigation container to another if necessary.


Installation
============

To install `collective.eeafaceted.batchactions` you simply add ``collective.eeafaceted.batchactions``
to the list of eggs in your buildout, run buildout and restart Plone.
Then, install `collective.eeafaceted.batchactions` using the Add-ons control panel.
