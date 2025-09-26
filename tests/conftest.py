"""
:module: docs.sys_path_setup
:synopsis: Add project root to ``sys.path`` so Sphinx can import the codebase.

This tiny helper prepends the repository root to Python's import path. It's
useful when building docs so ``autodoc`` can import modules without installing
the package.

Notes
-----
- This is a quick lab-style workaround. In a real project, you'd probably
  install the package in editable mode (``pip install -e .``) instead.
"""

import sys, pathlib

# figure out the project root (.. from this file)
ROOT = pathlib.Path(__file__).resolve().parents[1]

# stick the root at the *front* so our local modules win over site-packages
# (yes, a bit hacky, but gets Sphinx imports working fast for the lab)
sys.path.insert(0, str(ROOT))
