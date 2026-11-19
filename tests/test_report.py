import json
from pathlib import Path

from sequana_pipelines.nanocap import create_report, create_summary, version
from sequana_pipelines.nanocap.src.report import (
    get_fastp_counts,
    get_mapped_count,
    get_results,
    get_software_versions,
    get_summary_table,
)

from . import test_dir


def test_get_results():
    working_dir = test_dir / "resources"
    results = get_results("sequence", "raw", working_dir)
    assert "N16961chr2" in results
    assert results["N16961chr2"]["read_count"] == 10
    assert results["N16961chr2"]["DOC"] == "1141.076"


def test_create_report(tmp_path):
    working_dir = test_dir / "resources"
    report = Path(tmp_path) / "nanocap.html"
    create_report(str(report), "sequence", working_dir)
    html = report.read_text()
    # sequana-like header/footer, link back to the main page
    assert "sequana-header" in html
    assert "sequana-footer" in html
    assert "../summary.html" in html
    assert "https://github.com/sequana/nanocap" in html
    assert f"(v{version})" in html


def _fake_run_directory(tmp_path, sample="sample1"):
    """Working directory with fastp json and BAM files (copied from the test resources)."""
    import shutil

    resources = test_dir / "resources"
    root = Path(tmp_path)
    (root / sample / "fastp").mkdir(parents=True)
    with open(root / sample / "fastp" / f"{sample}.json", "w") as fout:
        json.dump({"summary": {"before_filtering": {"total_reads": 200}, "after_filtering": {"total_reads": 50}}}, fout)
    for kind in ("raw", "filtered"):
        mapping = root / sample / kind / "mapping"
        mapping.mkdir(parents=True)
        shutil.copy(resources / "sequence.bam", mapping / f"{sample}.sorted.bam")
        shutil.copy(resources / "sequence.bam.bai", mapping / f"{sample}.sorted.bam.bai")
    return root


def test_get_fastp_counts(tmp_path):
    root = _fake_run_directory(tmp_path)
    assert get_fastp_counts("sample1", root) == (200, 50)
    assert get_fastp_counts("missing", root) == (None, None)


def test_get_mapped_count(tmp_path):
    root = _fake_run_directory(tmp_path)
    assert get_mapped_count("sample1", "raw", root) > 0
    assert get_mapped_count("missing", "raw", root) is None


def test_get_software_versions():
    config = {"apptainers": {"fastp": "https://x/fastp_1.0.1.img", "multiqc": "https://x/multiqc_1.27.0-zenodo1.img"}}
    assert get_software_versions(config) == [("fastp", "1.0.1"), ("multiqc", "1.27.0-zenodo1")]
    assert get_software_versions({}) == []


def test_get_summary_table(tmp_path):
    root = _fake_run_directory(tmp_path)
    html = get_summary_table(["sample1"], root)
    assert "sample1/nanocap.html" in html
    assert "sample1/fastp/sample1.html" in html
    assert "sample1/raw/sequana_coverage/sequana_coverage.html" in html
    assert "sample1/filtered/sequana_coverage/sequana_coverage.html" in html
    assert "25.0" in html  # 50 / 200
    # no fastp json for unknown samples
    assert "NA" in get_summary_table(["missing"], root)


def test_create_summary(tmp_path, monkeypatch):
    root = _fake_run_directory(tmp_path)
    (root / ".sequana").mkdir()
    (root / ".sequana" / "rulegraph.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>')
    monkeypatch.chdir(root)

    from sequana.utils import config as report_config

    report_config.output_dir = str(root)
    data = {"name": "nanocap", "rulegraph": ".sequana/rulegraph.svg", "pipeline_version": version}
    config = {"reference": str(root / "references" / "ref.fa"), "apptainers": {}}
    create_summary(data, ["sample1"], config, ".")

    html = (root / "summary.html").read_text()
    assert "sample1/nanocap.html" in html
    assert "multiqc/multiqc_report.html" in html
    # the reference is shown with a relative path
    assert "<code>references/ref.fa</code>" in html
    assert str(root) not in html.split("<code>")[1].split("</code>")[0]
