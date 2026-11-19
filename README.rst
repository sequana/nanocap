This is the **nanocap** pipeline from the `Sequana <https://sequana.readthedocs.org>`_ project

.. image:: https://badge.fury.io/py/sequana-nanocap.svg
     :target: https://pypi.python.org/pypi/sequana_nanocap

.. image:: https://github.com/sequana/nanocap/actions/workflows/main.yml/badge.svg
   :target: https://github.com/sequana/nanocap/actions/

.. image:: https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg
    :target: https://pypi.python.org/pypi/sequana
    :alt: Python 3.11 | 3.12

.. image:: http://joss.theoj.org/papers/10.21105/joss.00352/status.svg
   :target: http://joss.theoj.org/papers/10.21105/joss.00352
   :alt: JOSS (journal of open source software) DOI



:Overview: Adaptive-sampling nanopore quality control. Maps long reads onto a reference (raw and fastp-filtered), computes per-base coverage with ``sequana_coverage``, and aggregates the results in a ``summary.html`` entry point and a MultiQC report.
:Input: A directory of single-end FastQ files (``*.fastq.gz``) and a reference FASTA.
:Output: ``summary.html`` (main entry point), per-sample HTML coverage reports (raw + filtered), a combined ``nanocap.html`` per sample, and a global MultiQC report.
:Status: production
:Citation: Cokelaer et al, (2017), 'Sequana': a Set of Snakemake NGS pipelines, Journal of Open Source Software, 2(16), 352, JOSS DOI doi:10.21105/joss.00352


Installation
~~~~~~~~~~~~

Install the pipeline with pip::

    pip install sequana_nanocap --upgrade

You also need the tools listed in the Requirements section below. The easiest
way to get them is the bundled conda environment::

    conda env create -f environment.yml
    conda activate nanocap

Apptainer images referenced in ``config.yaml`` are an alternative to installing
the tools locally — pass ``--apptainer-prefix <dir>`` to ``sequana_nanocap``
(see Usage).


Usage
~~~~~

::

    sequana_nanocap --help
    sequana_nanocap --input-directory DATAPATH --reference-file reference.fa

This creates a working directory with the Snakemake workflow and a generated
``config.yaml``. The reference file is copied into the ``references/``
sub-directory of the working directory (for book keeping) and the pipeline uses
that copy. Launch the pipeline with::

    cd nanocap
    bash nanocap.sh     # local run (bash, not sh — pipefail is a bashism)

To run with apptainer containers (no local tool install needed)::

    sequana_nanocap --input-directory DATAPATH \
                    --reference-file reference.fa \
                    --apptainer-prefix ~/.sequana/apptainers
    cd nanocap
    bash nanocap.sh

If you are familiar with Snakemake, you can edit the generated files and invoke
Snakemake directly::

    snakemake -s nanocap.rules --configfile config.yaml --cores 4 --stats stats.txt


Requirements
~~~~~~~~~~~~

This pipeline requires the following executables:

- fastp
- graphviz
- minimap2
- multiqc
- samtools
- sequana_coverage (ships with ``sequana``)

All of them can be installed via conda using the bundled ``environment.yml``,
or pulled on demand via the apptainer images declared in ``config.yaml``.

.. image:: https://raw.githubusercontent.com/sequana/nanocap/master/sequana_pipelines/nanocap/dag.png


Details
~~~~~~~

For each input FastQ the pipeline runs two branches in parallel:

1. **raw** — map reads to the reference with ``minimap2`` (``-ax map-ont``),
   sort with ``samtools``, index, compute per-base depth with ``samtools depth``,
   run ``sequana_coverage`` for ROI detection.
2. **filtered** — same flow, after quality/length filtering with ``fastp``
   (defaults: ``-q 0 -e 9 -l 1000``).

A per-sample ``{sample}/nanocap.html`` page aggregates both coverage reports
(with a link back to ``summary.html``), and a top-level
``multiqc/multiqc_report.html`` combines the fastp and sequana_coverage outputs
across all samples.

Once the pipeline is finished, open ``summary.html`` in the working directory.
This is the main entry point. It follows the standard Sequana report layout and
contains:

- an overview with the (relative) path to the reference and a link to the
  MultiQC report;
- a per-sample table: number of reads before and after fastp filtering,
  percentage of reads kept, number of mapped alignments (raw and filtered), and
  links to the Nanocap, fastp and sequana_coverage (raw and filtered) reports;
- the workflow (DAG), with links to the Snakemake and configuration files;
- the dependencies and the command used to set up the pipeline.


Rules and configuration details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is the `latest documented configuration file <https://raw.githubusercontent.com/sequana/nanocap/master/sequana_pipelines/nanocap/config.yaml>`_
to be used with the pipeline. Each rule used in the pipeline may have a section
in the configuration file.


Changelog
~~~~~~~~~

========= ====================================================================
Version   Description
========= ====================================================================
0.6.0     * Add ``summary.html``, the main entry point of the analysis, created
            with the standard Sequana report layout (header, sidebar, DAG,
            config file, dependencies, command, footer). It contains a
            per-sample table (reads before/after fastp, percentage kept, mapped
            alignments) with links to the Nanocap, fastp and sequana_coverage
            reports, and a link to the MultiQC report. It is created in the
            ``onsuccess`` section, which now also calls ``manager.teardown()``
            and ``manager.onerror()`` on failure.
          * Per-sample ``nanocap.html`` reports now use a Sequana-like
            header/footer (logo, versions, citation) and a link back to
            ``summary.html``.
          * The ``--reference-file`` is now copied into the ``references/``
            directory of the working directory when initiating the pipeline;
            the pipeline uses this copy.
          * Declare ``pysam`` explicitly as a dependency (used by the BAM
            metrics).
          * Tests: new tests for the summary, the reference copy and the
            version; tests no longer write in the current directory.
          * CI: remove the unused ``[testing]`` extra, use ``actions/cache@v4``,
            stop echoing the coveralls token, and check that ``summary.html`` is
            created in the apptainer workflow.
0.5.0     * Migrate packaging from ``setup.py`` to Poetry (``pyproject.toml``).
          * Replace ``pkg_resources`` with ``importlib.metadata`` in
            ``__init__.py``.
          * Drop ``click_completion``; use ``rich_click``.
          * Convert all rules from ``wrapper:`` directives to
            ``shell: manager.get_shell(...)`` (minimap2, samtools_depth,
            sequana_coverage, multiqc).
          * ``fastp`` rule uses the new ``fastp/run`` v2 shell template which
            supports both single-end and paired-end via ``params.out2``.
          * Add ``sequana_coverage`` section to ``config.yaml`` / ``schema.yaml``
            with the parameters required by the shell template (chunksize,
            thresholds, mixture models, ...).
          * Refresh apptainer URLs: ``sequana_tools_26.1.14`` for
            minimap2+samtools, ``sequana_coverage_0.18.0``,
            ``multiqc_1.27.0``.
          * Add ``localrules: rulegraph, dot2svg, multiqc``.
          * Redirect ``samtools index`` stdout/stderr to ``{log}``.
          * Convert ``mem: "8G"/"16G"`` strings to integer ``mem_mb: 8000/16000``
            resources (avoids snakemake string-mangling).
          * CI: ``micromamba-shell``, ``generate-run-shell: true``, PyPI via
            ``poetry build`` on Python 3.11.
0.3.0     * refactoring to use click
0.2.0     * add containers
          * Fix tests adding the missing index
          * add workflow for apptainer
0.1.0     **First release.**
========= ====================================================================
