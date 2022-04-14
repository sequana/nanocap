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
import json
from contextlib import ExitStack
from pathlib import Path

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
        key_header=tab_header,
        **results_per_kind
    )
    with open(report_name, "w") as fout:
        print(report_output, file=fout)


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
