rule multiqc:
    input:
        requested_output(manager)
    output:
        "multiqc/multiqc_report.html"
    params:
        options = config["multiqc"]["options"],
        config_file = config["multiqc"]["config_file"],
        modules = config["multiqc"]["modules"]
    log:
        "multiqc/multiqc.log"
    wrapper:
        f"{wrapper_version}/wrappers/multiqc"
