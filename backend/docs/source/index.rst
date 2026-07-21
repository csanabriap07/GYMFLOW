.. Gymflow documentation master file, created by
   sphinx-quickstart on Fri Jul 17 11:59:03 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentación de Gymflow
========================

Documentación del backend de Gymflow, organizada por módulo (``auth``,
``checkin``, ``members``, ``membership``, ``reports``). Cada función y
clase documentada indica a qué Historia de Usuario, Requerimiento
Funcional/No Funcional o Regla de Negocio del análisis del proyecto
pertenece.

.. toctree::
   :maxdepth: 2
   :caption: Módulos:

   modules

Índices y tablas
================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Cómo se genera esta documentación
==================================

Se genera con `Sphinx <https://www.sphinx-doc.org/>`_, el generador de
documentación estándar para proyectos Python (el mismo que usan Django,
Flask y NumPy), a partir de los docstrings que ya viven en el código
fuente. No es un documento aparte que se pueda desactualizar: si el código
cambia, basta con volver a correr ``sphinx-build`` para regenerar todo.

Extensiones habilitadas en ``conf.py``:

``sphinx.ext.autodoc``
   Recorre los módulos del backend e inserta automáticamente la firma y el
   docstring de cada función/clase en la página correspondiente.

``sphinx.ext.napoleon``
   Permite escribir los docstrings en formato Google (secciones ``Args``,
   ``Returns``, ``Raises``) en vez de reStructuredText a mano; Napoleon los
   traduce a la tabla de parámetros que se ve en cada función.

``sphinx.ext.viewcode``
   Agrega el enlace "[fuente]" que lleva al código resaltado de cada
   función documentada.

El tema visual es `sphinx_rtd_theme
<https://sphinx-rtd-theme.readthedocs.io/>`_ (Read the Docs), que da la
barra lateral de navegación y el buscador.

