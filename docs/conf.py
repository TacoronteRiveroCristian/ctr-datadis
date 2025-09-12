"""Configuration file for Sphinx documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Project information
project = "ctr-datadis"
copyright = "2024, Cristian Tacoronte Rivero"
release = "0.1.3"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# HTML output options
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Autodoc options
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Napoleon options
napoleon_google_docstring = True
napoleon_numpy_docstring = True