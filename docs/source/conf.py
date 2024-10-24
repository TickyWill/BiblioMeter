"""
Technical Documentation: Sphinx configuration file
"""

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

BiblioMeter_path = os.path.dirname(os.path.normpath(os.path.abspath("..")))

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath(BiblioMeter_path))
sys.path.insert(0, os.path.abspath(BiblioMeter_path + "/bmfuncts"))
sys.path.insert(0, os.path.abspath(BiblioMeter_path + "/bmgui"))


project = 'BiblioMeter'
copyright = '2021, BiblioMeter team, Liten, Leti, CEA'
author = 'Amal CHABLI, François BERTIN, Ludovic DESMEUZES, Baptiste REFALO'
release = '5.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    #'myst_parser',
]
source_suffix = [".rst", ".md"]

templates_path = ['_templates']
exclude_patterns = ['.ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = 'BM-logo_doc.ico'

show_authors = True
