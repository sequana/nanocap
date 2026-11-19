import subprocess

import yaml

from sequana_pipelines.nanocap import version

from . import test_dir


def _run(args):
    return subprocess.run(args, capture_output=True, text=True)


def test_standalone_subprocess(tmp_path):
    input_dir = test_dir / "resources"
    workdir = tmp_path / "nanocap"
    cmd = ["sequana_nanocap", "--input-directory", str(input_dir), "--working-directory", str(workdir), "--force"]
    assert _run(cmd).returncode == 0
    for name in ("config.yaml", "nanocap.rules", "nanocap.sh", "schema.yaml"):
        assert (workdir / name).exists()


def test_reference_is_copied_in_working_directory(tmp_path):
    input_dir = test_dir / "resources"
    reference = test_dir / "resources" / "vibrio.fa"
    workdir = tmp_path / "nanocap"
    cmd = [
        "sequana_nanocap",
        "--input-directory",
        str(input_dir),
        "--reference-file",
        str(reference),
        "--working-directory",
        str(workdir),
        "--force",
    ]
    assert _run(cmd).returncode == 0

    copied = workdir / "references" / "vibrio.fa"
    assert copied.exists()
    assert copied.read_text() == reference.read_text()

    with open(workdir / "config.yaml") as fin:
        config = yaml.safe_load(fin)
    # the pipeline must use the copy (absolute path: rulegraph runs from a sub-directory)
    assert config["reference"] == str(copied)


def test_version():
    result = _run(["sequana_nanocap", "--version"])
    assert result.returncode == 0
    assert version in result.stdout + result.stderr
