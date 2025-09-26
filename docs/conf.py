# Configuration file for the Sphinx documentation builder.
#
# For the full list of options, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

# Add the parent directory (project root) to sys.path so autodoc can find your code
sys.path.insert(0, os.path.abspath('..'))
# Make sure Sphinx can find all your modules
sys.path.insert(0, os.path.abspath('../src'))    # main source code
sys.path.insert(0, os.path.abspath('../src/gui'))
sys.path.insert(0, os.path.abspath('../src/models'))
sys.path.insert(0, os.path.abspath('../src/persistence'))
sys.path.insert(0, os.path.abspath('../src/validation'))
sys.path.insert(0, os.path.abspath('../db'))
sys.path.insert(0, os.path.abspath('../tests'))


# -- Project information -----------------------------------------------------

project = 'School_Management_System'
copyright = '2025, Tamara_Fakih_&Lynn_Ariss'
author = 'Tamara_Fakih_&Lynn_Ariss'
release = '1.0.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
# These extensions enable autodoc, source code linking, and Google/Numpy-style docstrings.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and directories to ignore.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here, relative to this directory.
# They are copied after the builtin static files, so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

