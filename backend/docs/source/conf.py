
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# core/config.py instancia Settings() al importar y exige estas variables de
# entorno; sin ellas autodoc no puede importar ningún módulo de la app.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "solo-para-generar-docs")
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Gymflow'
copyright = '2026, los seguidores de bodoque'
author = 'los seguidores de bodoque'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
     'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'
]

# Convención del proyecto: docstrings estilo Google (Args/Returns/Raises).
# Se desactiva el parseo NumPy para que Napoleon no intente adivinar el
# formato y las secciones se rendericen siempre igual.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = False
napoleon_use_ivar = True

# autodoc: solo documenta miembros públicos (sin "_") — los helpers privados
# no forman parte de la API que se muestra en la doc generada.
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
