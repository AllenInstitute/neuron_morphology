# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sys
import os
import subprocess as sp


def get_version():
    version_path = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ), 
        "neuron_morphology",
        "VERSION.txt"
    )
    with open(version_path, "r") as version_file:
        return version_file.read().strip()


# -- Project information -----------------------------------------------------

project = 'neuron morphology'
copyright = '2020, allen institute for brain science'
author = 'allen institute for brain science'

version = get_version()
release = version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc', 
    'sphinx.ext.viewcode', 
    'sphinx.ext.autosummary', 
    'numpydoc'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# additional options
html_show_sphinx = False # TODO: alabaster seems to be ignoring this directive

master_doc = "index"

autodoc_mock_imports = ["allensdk"]


# setup
def run_apidoc(*a):
    parent = os.path.dirname(__file__)
    grandparent = os.path.dirname(parent)
    package = os.path.join(grandparent, "neuron_morphology")

    sys.path = [grandparent] + sys.path
    sp.check_call([
        "sphinx-apidoc",
        "-e",
        "-o",
        parent,
        "--force",
        package
    ])


def setup(app):
    app.connect("builder-inited", run_apidoc)

