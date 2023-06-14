# -*- coding: utf-8 -*-

import sys, os
import sphinx_rtd_theme
#import sphinx_pdj_theme
#import sphinx_material


sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))

extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc'
]

autodoc_default_flags = ['members', 'undoc-members', 'private-members', 'show-inheritance'] 
html_theme = 'sphinx_rtd_theme'
todo_include_todos = False
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = []
add_function_parentheses = True
add_module_names = True

project = u'VoiceLab'
copyright = u'2023, David R Feinberg'

version = '2.2.0'
release = '2.2.0'


html_title = "VoiceLab: Automated Reproducible Acoustic Analysis"
html_favicon = 'favicon.ico'
html_static_path = ['../_static', '../_static/images', '../_images']
html_domain_indices = False
html_use_index = False
html_show_sphinx = False
htmlhelp_basename = 'VoiceLab'
html_show_sourcelink = False

html_theme_options = {
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': False,
    'titles_only': False
}


