#
#  This file is part of Sequana software
#
#  Copyright (c) 2021-2022 - Sequana Dev Team (https://sequana.readthedocs.io)
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  Website:       https://github.com/sequana/sequana
#  Documentation: http://sequana.readthedocs.io
#  Contributors:  https://github.com/sequana/sequana/graphs/contributors
##############################################################################
import sys
import os
import argparse



import rich_click as click
from sequana_pipetools import SequanaManager
from sequana_pipetools.options import *

NAME = "nanocap"




help = init_click(
    NAME,
    groups={
        "Pipeline Specific": [
            "--reference-file",
        ],
    },
)


@click.command(context_settings=help)
@include_options_from(ClickInputOptions, add_input_readtag=False)
@include_options_from(ClickSnakemakeOptions, working_directory=NAME)
@include_options_from(ClickSlurmOptions)
@include_options_from(ClickGeneralOptions)
@click.option("--reference-file", type=click.Path(dir_okay=False, file_okay=True), 
    help="reference file (fasta format) to map reads onto")
def main(**options):

    if options["from_project"]:
        click.echo("--from-project Not yet implemented")
        sys.exit(1)

    # the real stuff is here
    manager = SequanaManager(options, NAME)
    manager.setup()

    # aliases
    options = manager.options
    cfg = manager.config.config

    # fill the config file with input parameters
    cfg.input_pattern = options.input_pattern
    cfg.input_directory = os.path.abspath(options.input_directory)
    if options.exclude_pattern:
        cfg.exclude_pattern = options.exclude_pattern
    cfg.reference = ""
    if options.reference_file:
        # copy the reference in the working directory for book keeping. The pipeline uses the copy.
        # abspath is required: the rulegraph rule runs snakemake from a sub-directory.
        import shutil

        reference_file = os.path.abspath(options.reference_file)
        manager.exists(reference_file)
        references_directory = os.path.join(os.path.abspath(manager.workdir), "references")
        os.makedirs(references_directory, exist_ok=True)
        shutil.copy(reference_file, references_directory)
        cfg.reference = os.path.join(references_directory, os.path.basename(reference_file))

    # finalise the command and save it; copy the snakemake. update the config
    # file and save it.
    manager.teardown(check_input_files=False)


if __name__ == "__main__":
    main()
