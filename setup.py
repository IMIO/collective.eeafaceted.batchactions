# -*- coding: utf-8 -*-
"""Installer for the collective.eeafaceted.batchactions package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = read("README.rst") + "\n\n" + read("CHANGES.rst")

setup(
    name="collective.eeafaceted.batchactions",
    version="2.0.0.dev0",
    description="This package provides batch actions for eea.facetednavigation dashboard",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="faceted navigation batch actions table",
    author="IMIO",
    author_email="dev@imio.be",
    url="https://github.com/IMIO/collective.eeafaceted.batchactions",
    download_url="https://pypi.org/project/collective.eeafaceted.batchactions",
    license="GPL V2",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Plone",
        "plone.base",
        "setuptools",
        "collective.eeafaceted.z3ctable>=2.0",
        "imio.actionspanel",
        "imio.helpers",
        "imio.pyutils",
        "plone.formwidget.masterselect",
    ],
    extras_require={
        "test": [
            "plone.app.contenttypes",
            "plone.app.dexterity",
            "plone.app.testing",
            "plone.app.relationfield",
            "plone.app.robotframework",
            "collective.contact.core",
            "collective.contact.widget",
            "collective.labels",
        ],
        "develop": [
            "zest.releaser",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
