# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'dserver'
copyright = '2024, Tjelvar S. G. Olsson, Johannes L. Hörmann, Lars Pastewka, Luis Yanes, Matthew Hartley'
author = 'Tjelvar S. G. Olsson, Johannes L. Hörmann, Lars Pastewka, Luis Yanes, Matthew Hartley'

import dtool_lookup_server
version = dtool_lookup_server.__version__
release = dtool_lookup_server.__version__

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

# spell check with sphinxcontrib.spelling
spelling_lang = 'en_US'
spelling_show_suggestions = True