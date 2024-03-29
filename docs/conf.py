# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

from pysjtu import __version__

sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'PySJTU'
copyright = '2020, LightQuantum'
author = 'LightQuantum'

# The full version, including alpha/beta/rc tags
release = __version__

language = 'en'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    # 'sphinx_autodoc_typehints',
    'sphinx.ext.coverage',
    'sphinx.ext.autosectionlabel',
]

autodoc_default_options = {
    "show-inheritance": True,
    "exclude-members": "Schema"
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

master_doc = 'index'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_book_theme'
html_theme_options = {
    "repository_url": "https://github.com/PhotonQuantum/pysjtu",
    "use_repository_button": True,
    "use_download_button": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['custom.css']

# -- Extension configuration -------------------------------------------------
# set_type_checking_flag = True
always_document_param_types = True
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented_params'
