This is is the **nanocap** pipeline from the `Sequana <https://sequana.readthedocs.org>`_ project

:Overview: Adaptive sampling from nanopore quality control
:Input: A set of fastq file.
:Output: HTML reports to assess adaptive sampling experiment.
:Status: draft
:Citation: Cokelaer et al, (2017), ‘Sequana’: a Set of Snakemake NGS pipelines, Journal of Open Source Software, 2(16), 352, JOSS DOI doi:10.21105/joss.00352


Installation
~~~~~~~~~~~~

To install this package::

    pip install sequana_nanocap


Usage
~~~~~

::

    sequana_nanocap --help
    sequana_nanocap --input-directory DATAPATH 

This creates a directory with the pipeline and configuration file. You will then need 
to execute the pipeline::

    cd nanocap
    sh nanocap.sh  # for a local run

This launch a snakemake pipeline. If you are familiar with snakemake, you can 
retrieve the pipeline itself and its configuration files and then execute the pipeline yourself with specific parameters::

    snakemake -s nanocap.smk -c config.yml --cores 4 --stats stats.txt

Or use `sequanix <https://sequana.readthedocs.io/en/master/sequanix.html>`_ interface.

Requirements
~~~~~~~~~~~~

This pipelines requires the following executable(s):

- fastp
- minimap2
- samtools
- sequana


.. image:: https://raw.githubusercontent.com/sequana/nanocap/master/sequana_pipelines/nanocap/dag.png


Details
~~~~~~~~~

This pipeline runs nanocap in parallel on the input fastq files (paired or not). A brief sequana summary report is also produced.


Rules and configuration details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is the `latest documented configuration file <https://raw.githubusercontent.com/sequana/nanocap/master/sequana_pipelines/nanocap/config.yaml>`_
to be used with the pipeline. Each rule used in the pipeline may have a section in the configuration file. 

Changelog
~~~~~~~~~

========= ====================================================================
Version   Description
========= ====================================================================
0.1.0     **First release.**
========= ====================================================================


