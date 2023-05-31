"""Utils rules"""

rule rulegraph:
    input:
        MAIN_SNAKEFILE
    output:
        "rulegraph/rulegraph.dot",
    params:
        mapper = {"multiqc": "../multiqc/multiqc_report.html"},
        configname = "config.yml",
        required_local_files = ["schema.yml", "rules"]
    wrapper:
        f"{wrapper_version}/wrappers/rulegraph"


rule dot2svg:
    input:
        "rulegraph/rulegraph.dot"
    output:
        ".sequana/rulegraph.svg"
    container:
        config['apptainers']['graphviz']
    shell:
        """dot -Tsvg {input} -o {output}"""
