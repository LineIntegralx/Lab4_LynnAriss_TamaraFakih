# Configuration file for the Sphinx documentation builder.

project = 'School Management System (Tkinter)'
author = 'Tamara Fakih'
copyright = '2025, Tamara Fakih'
release = '1.0.0'

# ---- Path setup ----
import os, sys
sys.path.insert(0, os.path.abspath('..'))       # project root
sys.path.insert(0, os.path.abspath('../src'))   # src packages: gui, models, ...
sys.path.insert(0, os.path.abspath('../db'))    # db modules

# If Tk imports break the build, mock them:
autodoc_mock_imports = ['tkinter', 'tkinter.ttk']

# ---- Extensions ----
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# ---- Autodoc options ----
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,         # show _methods
    'special-members': '__init__',   # show __init__ docstring
    'show-inheritance': True,
    # 'inherited-members': True,     # uncomment if you want inherited stuff too
}
autoclass_content = 'both'           # merge class + __init__ docstrings
add_module_names = False

# ---- Napoleon (Google/Sphinx style) ----
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_include_private_with_doc = True  # include private members if they have docs
# napoleon_include_special_with_doc = True  # optional: include dunder methods with docs

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
