import sys
import os

# Додайте шлях до кореневої директорії проекту
sys.path.insert(0, os.path.abspath('../..'))

project = 'Contact project'
copyright = '2024, Oleksandr Skuz'
author = 'Oleksandr Skuz'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
