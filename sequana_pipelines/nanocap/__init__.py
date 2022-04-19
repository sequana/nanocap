import pkg_resources

version = pkg_resources.require("sequana_nanocap")[0].version

from .src import create_report
