# -*- coding: utf-8 -*-

"""Top-level package for neuron_morphology."""

import os
from logging.config import fileConfig


version_path = os.path.join(os.path.dirname(__file__), "VERSION.txt")
with open(version_path, "r") as version_file:
    __version__ = version_file.read().strip()


fileConfig(os.path.join(
    os.path.dirname(__file__), 
    'logging_config.ini')
)
