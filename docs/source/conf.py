# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import subprocess
import sys
from datetime import datetime


sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../batconf'))

from diagram_config_comp import create_config_diagram


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BatConf'
current_year = datetime.now().year
copyright = f'{current_year}, Lundy Bernard, Lauren Moore'
author = 'Lundy Bernard, Lauren Moore'
release = '0.1.8'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

master_doc = 'index'
html_logo = '_static/batconf-logo.png'
html_favicon = '_static/batconf-favicon.png'


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinxext.opengraph',
    'sphinx_autodoc_typehints',
    'myst_parser',
    'sphinx_design',
]

templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '*test.py',
    'batconf/*/tests/',
    '.ipynb_checkpoints/*',
    'notebooks/try_pandera.ipynb',
]

autoclass_content = 'both'

autodoc_default_options = {
    'undoc-members': False,
}

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# sphinx-autodoc-typehints options
set_type_checking_flag = True
always_document_param_types = True

# This config value must be a dictionary of external sites, mapping unique
# short alias names to a base URL and a prefix.
# See http://sphinx-doc.org/ext/extlinks.html
_repo = 'https://github.com/lundybernard/batconf/'
extlinks = {
    'commit': (_repo + 'commit/%s', 'commit %s'),
    'gh-file': (_repo + 'blob/main/%s', '%s'),
    'gh-link': (_repo + '%s', '%s'),
    'issue': (_repo + 'issues/%s', 'issue #%s'),
    'pull': (_repo + 'pull/%s', 'pull request #%s'),
    'pypi': ('https://pypi.org/project/%s/', '%s'),
    'wikipedia': ('https://en.wikipedia.org/wiki/%s', '%s'),
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']


# -- Options for OGP social preview ------------------------------------------
if rtd_canon_url := os.getenv('READTHEDOCS_CANONICAL_URL', False):
    print(f'rtd_canon_url={rtd_canon_url}')
    ogp_site_url = rtd_canon_url


def run_apidoc(app):
    source_dir = os.path.abspath(os.path.dirname(__file__))
    package_dir = os.path.join(source_dir, '../../batconf')
    output_dir = os.path.join(
        source_dir, 'reference'
    )  # Reference within "source"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    subprocess.check_call(
        ['sphinx-apidoc', '--output-dir', output_dir, package_dir]
    )


def setup(app):
    create_config_diagram()
    app.connect('builder-inited', run_apidoc)
