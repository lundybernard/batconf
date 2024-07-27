# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
import os

sys.path.insert(0, os.path.abspath('../../batconf/'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BatConf'
copyright = '2024, Lundy Bernard, Lauren Moore'
author = 'Lundy Bernard, Lauren Moore'
release = '0.1.8'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

master_doc = 'index'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "*test.py",
    "batconf/*/tests/",
    ".ipynb_checkpoints/*",
    "notebooks/try_pandera.ipynb",
]

autoclass_content = "both"

autodoc_default_options = {
    "undoc-members": False,
}

# sphinx-autodoc-typehints options
set_type_checking_flag = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
