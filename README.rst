.. image:: https://github.com/IMIO/collective.eeafaceted.batchactions/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/IMIO/collective.eeafaceted.batchactions/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/IMIO/collective.eeafaceted.batchactions/badge.png?branch=master
  :target: https://coveralls.io/r/IMIO/collective.eeafaceted.batchactions?branch=master

.. image:: http://img.shields.io/pypi/v/collective.eeafaceted.batchactions.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/collective.eeafaceted.batchactions

==================================
collective.eeafaceted.batchactions
==================================

This package gives the possibility to define batch actions on elements displayed in a eea.facetednavigation dashboard

* `Source code @ GitHub <https://github.com/IMIO/collective.eeafaceted.batchactions>`_
* `Releases @ PyPI <http://pypi.python.org/pypi/collective.eeafaceted.batchactions>`_
* `Continuous Integration @ Travis-CI <http://travis-ci.org/IMIO/collective.eeafaceted.batchactions>`_

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
