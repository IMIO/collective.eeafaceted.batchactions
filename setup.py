# -*- coding: utf-8 -*-
"""Installer for the collective.eeafaceted.batchactions package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + '\n\n' + read('CHANGES.rst')

setup(
    name='collective.eeafaceted.batchactions',
    version='1.3',
    description="This package provides batch actions for eea.facetednavigation dashboard",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Python Zope Plone',
    author='IMIO',
    author_email='dev@imio.be',
    url='http://pypi.python.org/pypi/collective.eeafaceted.batchactions',
    license='GPL V2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.eeafaceted'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'setuptools',
        'collective.eeafaceted.z3ctable>=2.0',
    ],
    extras_require={
        'test': [
            'plone.app.dexterity',
            'plone.app.testing',
            'plone.app.relationfield',
            'plone.app.robotframework',
        ],
        'develop': [
            'zest.releaser',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
