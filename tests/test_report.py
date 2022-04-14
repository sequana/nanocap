import pytest
from pathlib import Path

from sequana_pipelines.nanocap import create_report
from sequana_pipelines.nanocap.src.report import get_results
from . import test_dir


def test_get_results():
    working_dir = test_dir / "resources"
    results = get_results("sequence", "raw", working_dir)
    assert "N16961chr2" in results
    assert results["N16961chr2"]["read_count"] == 10
    assert results["N16961chr2"]["DOC"] == "1141.076"


def test_create_report(tmpdir):
    working_dir = test_dir / "resources"
    report = "nanocap.html"
    create_report(report, "sequence", working_dir)
    assert Path(report).exists()
