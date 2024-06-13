# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'dservercore'
copyright = '2024, Tjelvar S. G. Olsson, Johannes L. Hörmann, Lars Pastewka, Luis Yanes, Matthew Hartley'
author = 'Tjelvar S. G. Olsson, Johannes L. Hörmann, Lars Pastewka, Luis Yanes, Matthew Hartley'

import dservercore
version = dservercore.__version__
release = dservercore.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autosummary',
    'sphinxcontrib.spelling',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'show-inheritance': True,
    'inherited-members': True,
    'special-members': '__init__',
}

# spell check with sphinxcontrib.spelling
spelling_lang = 'en_US'
spelling_show_suggestions = True
