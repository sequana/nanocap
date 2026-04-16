"""Utils rules"""

rule rulegraph:
    input:
        MAIN_SNAKEFILE
    output:
        "rulegraph/rulegraph.dot",
    params:
        mapper = {"multiqc": "../multiqc/multiqc_report.html"},
        configname = "config.yaml",
        required_local_files = ["schema.yaml", "rules"]
    run:
        manager.get_run("rulegraph/run", "v1")(input, output, params)


rule dot2svg:
    input:
        "rulegraph/rulegraph.dot"
    output:
        ".sequana/rulegraph.svg"
    container:
        config['apptainers']['graphviz']
    shell:
        manager.get_shell("graphviz/dot2svg", "v1")
