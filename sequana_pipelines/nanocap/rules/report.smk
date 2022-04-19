rule nanocap_report:
    input:
        expand("{{sample}}/{kind}/sequana_coverage/sequana_coverage.html", kind=["raw", "filtered"])
    output:
        "{sample}/nanocap.html"
    run:
        from sequana_pipelines.nanocap import create_report

        create_report(output[0], wildcards.sample, '.')


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
