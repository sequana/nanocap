import importlib.metadata

version = importlib.metadata.version("sequana-nanocap")

from .src import create_report, create_summary
