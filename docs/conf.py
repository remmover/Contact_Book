import sys
import os

sys.path.append(os.path.abspath('..'))
project = 'Rest API'
copyright = '2023, Remover'
author = 'Remover'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'nature'
html_static_path = ['_static']
