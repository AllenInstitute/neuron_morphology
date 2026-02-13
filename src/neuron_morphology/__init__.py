# -*- coding: utf-8 -*-

"""Top-level package for neuron_morphology."""

import os
from logging.config import fileConfig
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("neuron_morphology")
except PackageNotFoundError:
    # package is not installed
    __version__ = "uninstalled"

fileConfig(os.path.join(
    os.path.dirname(__file__),
    'logging_config.ini')
)
