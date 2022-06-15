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
""" Nanocap pipeline"""

from sequana_pipetools.snaketools import PipelineManagerDirectory, FileFactory, modules

shell.executable('bash')
configfile: "config.yml"
wrapper_version = "main"

manager = PipelineManagerDirectory('nanocap', config, schema="schema.yml")
input_directory = config.get('input_directory', '.')
input_pattern = config.get('input_pattern', '*.fastq.gz')
ff = FileFactory(os.path.join(input_directory, input_pattern))
manager.samples = {sample: [file] for sample, file in zip(ff.filenames, ff.realpaths)}

rule nanocap:
    input:
        expand("{sample}/nanocap.html", sample=manager.samples),
        "multiqc/multiqc_report.html",
        ".sequana/rulegraph.svg"

include: "rules/common.smk"
include: "rules/filtered_mapping.smk"
include: "rules/raw_mapping.smk"
include: "rules/report.smk"
include: "rules/utils.smk"
