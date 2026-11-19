#  This file is part of Sequana software
#
#  Copyright (c) 2016-2022 - Sequana Dev Team (https://sequana.readthedocs.io)
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  Website:       https://github.com/sequana/sequana
#  Website:       https://github.com/sequana/nanocap
#  Documentation: http://sequana.readthedocs.io
#  Documentation: https://github.com/sequana/nanocap/README.rst
##############################################################################
import base64
import glob
import importlib.metadata
import json
import os
from contextlib import ExitStack
from pathlib import Path

import pysam
from jinja2 import Environment, PackageLoader

from sequana_pipelines.nanocap import version
from sequana_pipelines.nanocap.src.bam import BamMetrics


def create_report(report_name, sample_name, nanocap_dir="."):
    """Create Nanocap report for one sample
    :param str report_name: nanocap report name.
    :param str sample_name: sample name.
    :param str nanocap_dir: nanocap working directory.
    """
    tab_header = [("contig", "Contig"), ("read_count", "Read Count"), ("DOC", "Depth"), ("median_length", "Median Length")]
    results_per_kind = {kind: get_results(sample_name, kind, nanocap_dir) for kind in ("raw", "filtered")}
    # create nanocap report
    env = Environment(loader=PackageLoader("sequana_pipelines.nanocap.src", "templates"))
    template = env.get_template("nanocap.html")
    report_output = template.render(
        version=version,
        sample=sample_name,
        key_header=tab_header,
        **get_sequana_layout(),
        **results_per_kind,
    )
    with open(report_name, "w") as fout:
        print(report_output, file=fout)


SEQUANA_CITATION = (
    "Cokelaer et al. (2017) 'Sequana': a Set of Snakemake NGS pipelines. Journal of Open Source Software, 2(16), 352.",
    "10.21105/joss.00352",
)


def get_sequana_layout():
    """Return the variables used by the templates to draw the Sequana header and footer."""
    logo = Path(__file__).parent / "templates" / "sequana_logo.png"
    try:
        sequana_version = importlib.metadata.version("sequana")
    except importlib.metadata.PackageNotFoundError:
        sequana_version = "?"
    return {
        "logo_b64": base64.b64encode(logo.read_bytes()).decode("utf-8"),
        "sequana_version": sequana_version,
        "citation": SEQUANA_CITATION,
    }


def get_basic_metrics(sample, kind, nanocap_dir):
    """Get basic metrics from filtered or raw bam file
    :param str sample: sample name.
    :param str kind: raw or filtered data.
    :param str nanocap_dir: nanocap working directory.
    :return dict: basic metrics per contig.
    """
    bamfile = f"{nanocap_dir}/{sample}/{kind}/mapping/{sample}.sorted.bam"
    bam = BamMetrics(bamfile)
    return bam.get_metrics_per_chr()


def get_results(sample, kind, nanocap_dir):
    """Get basic metrics and sequana results.
    :param str sample: sample name.
    :param str kind: raw or filtered data.
    :param str nanocap_dir: nanocap working directory.
    :return dict: basic metrics and sequana coverage per contig.
    """
    # Get basics metrics results
    basic_metrics = get_basic_metrics(sample, kind, nanocap_dir)

    # Get sequana coverage results
    sequana_report = f"{nanocap_dir}/{sample}/{kind}/sequana_coverage/*/sequana_summary_coverage.json"
    # iter over sequana json file
    iter_json = (sequana_file for sequana_file in glob.iglob(sequana_report))
    with ExitStack() as stack:
        files = [stack.enter_context(open(sequana_file)) for sequana_file in iter_json]
        iter_json_file = (
            (Path(json_file.name).resolve().parent / "coverage.png", json.load(json_file)) for json_file in files
        )
        results = {
            json_obj["data"]["chrom_name"]: {
                "DOC": f"{json_obj['data']['DOC']:.3f}",
                "BOC": f"{json_obj['data']['BOC']:.3f}",
                "cov_image": base64.b64encode(coverage_plot.read_bytes()).decode("utf-8"),
                **basic_metrics[json_obj["data"]["chrom_name"]],
            }
            for coverage_plot, json_obj in iter_json_file
        }
    return results


def _fmt(value):
    """Format an integer with thousands separator, or return NA."""
    return f"{value:,}" if isinstance(value, int) else "NA"


def get_fastp_counts(sample, nanocap_dir="."):
    """Return (reads before, reads after) fastp filtering, or (None, None) if unavailable."""
    path = Path(nanocap_dir) / sample / "fastp" / f"{sample}.json"
    try:
        with open(path) as fin:
            summary = json.load(fin)["summary"]
        return summary["before_filtering"]["total_reads"], summary["after_filtering"]["total_reads"]
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None, None


def get_mapped_count(sample, kind, nanocap_dir="."):
    """Return the number of mapped alignments in the sorted BAM file (from its index), or None."""
    bamfile = Path(nanocap_dir) / sample / kind / "mapping" / f"{sample}.sorted.bam"
    try:
        with pysam.AlignmentFile(str(bamfile)) as bam:
            return sum(x.mapped for x in bam.get_index_statistics())
    except (FileNotFoundError, OSError, ValueError):
        return None


def get_software_versions(config):
    """Return (tool, version) from the container names listed in the config file."""
    versions = []
    for tool, url in config.get("apptainers", {}).items():
        name = os.path.basename(url)
        name = name[: -len(".img")] if name.endswith(".img") else name
        versions.append((tool, name.split("_")[-1]))
    return versions


def get_summary_table(samples, nanocap_dir="."):
    """Return the HTML table with one row per sample (read counts and links to reports)."""
    link = '<a href="{0}">{1}</a>'
    rows = []
    for sample in samples:
        before, after = get_fastp_counts(sample, nanocap_dir)
        kept = f"{after / before * 100:.1f}" if before else "NA"
        cells = [
            f"<th scope='row'>{sample}</th>",
            f"<td>{_fmt(before)}</td>",
            f"<td>{_fmt(after)}</td>",
            f"<td>{kept}</td>",
            f"<td>{_fmt(get_mapped_count(sample, 'raw', nanocap_dir))}</td>",
            f"<td>{_fmt(get_mapped_count(sample, 'filtered', nanocap_dir))}</td>",
            "<td>" + link.format(f"{sample}/nanocap.html", "Nanocap") + "</td>",
            "<td>" + link.format(f"{sample}/fastp/{sample}.html", "fastp") + "</td>",
            "<td>" + link.format(f"{sample}/raw/sequana_coverage/sequana_coverage.html", "raw") + "</td>",
            "<td>" + link.format(f"{sample}/filtered/sequana_coverage/sequana_coverage.html", "filtered") + "</td>",
        ]
        rows.append("<tr>" + "".join(cells) + "</tr>")

    header = [
        "Sample",
        "Reads (raw)",
        "Reads (filtered)",
        "Kept (%)",
        "Mapped (raw)",
        "Mapped (filtered)",
        "Nanocap report",
        "fastp report",
        "Coverage (raw)",
        "Coverage (filtered)",
    ]
    thead = "<tr>" + "".join(f"<th class='text-center'>{h}</th>" for h in header) + "</tr>"
    return (
        "<div class='table-responsive'><table class='table table-striped table-sm text-center align-middle'>"
        f"<thead>{thead}</thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def create_summary(data, samples, config, nanocap_dir="."):
    """Create the Nanocap main entry point (summary.html) with the standard Sequana report layout
    (header, sidebar, workflow, config file, dependencies, footer).

    :param dict data: metadata returned by ``manager.getmetadata()``.
    :param list samples: sample names.
    :param dict config: config used by the pipeline.
    :param str nanocap_dir: nanocap working directory.
    """
    from sequana.modules_report.summary import SequanaReport
    from sequana.utils import config as report_config

    reference = config.get("reference", "")
    if reference:
        reference = os.path.relpath(reference, nanocap_dir)

    intro = f"""<div>
<h3>Overview</h3>
<p style="text-align:justify">Nanocap controls and cleans adaptive sampling nanopore sequencing data.
For each sample, reads are filtered with fastp, and both raw and filtered reads are mapped onto the reference
(<code>{reference}</code>) with minimap2. Coverage is then analysed with sequana_coverage.
A MultiQC report aggregating all samples is available <a href="multiqc/multiqc_report.html">here</a>.
Additional help can be found on the pipeline <a href="https://github.com/sequana/nanocap">home page</a>.</p>
</div>"""

    report_config.summary_sections = [
        {
            "name": "Samples",
            "anchor": "samples",
            "content": (
                "<p>Reads before and after fastp filtering, and number of mapped alignments (minimap2, from the BAM "
                "index) on raw and filtered reads. Links give access to the per-sample reports.</p>"
                + get_summary_table(samples, nanocap_dir)
            ),
        }
    ]
    SequanaReport(data, intro)
