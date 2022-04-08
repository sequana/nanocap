import os
import subprocess
import sys

import sequana_pipelines.nanocap.main as m

from . import test_dir


def test_standalone_subprocess(tmpdir):
    input_dir = test_dir / 'resources'
    cmd = ["sequana_nanocap", "--input-directory", str(input_dir), "--working-directory", str(tmpdir), "--force"]
    subprocess.call(cmd)


def _test_standalone_script(tmpdir):
    input_dir = test_dir / 'resources'
    sys.argv = ["test", "--input-directory", str(input_dir), "--working-directory", str(tmpdir), "--force"]
    m.main()


def test_version():
    cmd = ["sequana_nanocap", "--version"]
    subprocess.call(cmd)
