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
release = '6.0.0'
authors = 'Amal CHABLI, François BERTIN, Ludovic DESMEUZES, Baptiste REFALO'
copyright = '2021, BiblioMeter team, Liten, Leti, CEA'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]
source_suffix = [".rst", ".md"]

templates_path = ['_templates']
exclude_patterns = ['.ipynb_checkpoints']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

latex_elements = {
    'preamble': r'''
        \usepackage{titling}
        \pretitle{\begin{center}\Huge\bfseries}
        \posttitle{\par\end{center}\vskip 1em}
        \preauthor{\begin{center}\Large}
        \postauthor{\par\end{center}\vskip 1em}
        \predate{\begin{center}\large}
        \postdate{\par\end{center}\vskip 1em}
        \usepackage{graphicx}
        \usepackage{fancyhdr}
    ''',
    'maketitle': f'''
        \\begin{{titlepage}}
            \\begin{{center}}
                {{\\Huge \\textbf{{{project}}}}} \\\\
                \\vspace{{0.5cm}}
                {{\\large Version: {release}}} \\\\
                \\vspace{{1cm}}
                {{\\Large \\textbf{{Author(s): {authors}}}}} \\\\
                \\vspace{{0.5cm}}
                {{\\small \\textcopyright\\ {copyright}}}
            \\end{{center}}
        \\end{{titlepage}}
    '''
}
