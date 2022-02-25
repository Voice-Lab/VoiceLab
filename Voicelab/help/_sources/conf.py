# -*- coding: utf-8 -*-

import sys, os
import sphinx_rtd_theme

extensions = [
    'sphinx_rtd_theme',
]

html_theme = "sphinx_rtd_theme"

todo_include_todos = True
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = []
add_function_parentheses = True
#add_module_names = True
# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

project = u'VoiceLab'
copyright = u'2022, David R Feinberg'

version = ''
release = ''

# -- Options for HTML output ---------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = "VoiceLab: Automated Reproducible Acoustic Analysis"
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
html_domain_indices = False
html_use_index = False
html_show_sphinx = False
htmlhelp_basename = 'VoiceLab'
html_show_sourcelink = False
