rule fastp:
    input:
        sample = get_raw_data
    output:
        trimmed = "{sample}/fastp/{sample}.fastq.gz",
        html = "{sample}/fastp/{sample}.html",
        json = "{sample}/fastp/{sample}.json"
    params:
        options = config["fastp"]["options"]
    log:
        "{sample}/log/fastq.log"
    threads:
        config["fastp"]["threads"]
    wrapper:
        f"{wrapper_version}/wrappers/fastp"


rule filtered_mapping:
    input:
        fastq = "{sample}/fastp/{sample}.fastq.gz",
        reference = config["reference"]
    output:
        sorted = "{sample}/filtered/mapping/{sample}.sorted.bam"
    params:
        options = config["minimap2"]["options"]
    log:
        "{sample}/log/filtered_mapping.log"
    threads:
        config["minimap2"]["threads"]
    wrapper:
        f"{wrapper_version}/wrappers/minimap2"


rule filtered_depth:
    input:
        "{sample}/filtered/mapping/{sample}.sorted.bam"
    output:
        "{sample}/filtered/depth/{sample}.bed"
    log:
        "{sample}/log/filtered_depth.log"
    wrapper:
        f"{wrapper_version}/wrappers/samtools_depth"


rule filtered_coverage:
    input:
        bed = "{sample}/filtered/depth/{sample}.bed",
        fasta = config["reference"]
    output:
        "{sample}/filtered/sequana_coverage/sequana_coverage.html"
    wrapper:
        f"{wrapper_version}/wrappers/sequana_coverage"
