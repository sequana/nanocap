rule raw_mapping:
    input:
        fastq = get_raw_data,
        reference = config["reference"]
    output:
        sorted = "{sample}/raw/mapping/{sample}.sorted.bam"
    log:
        "{sample}/log/raw_mapping.log"
    params:
        options = config["minimap2"]["options"]
    threads:
        config["minimap2"]["threads"]
    wrapper:
        f"{wrapper_version}/wrappers/minimap2"

rule raw_depth:
    input:
        "{sample}/raw/mapping/{sample}.sorted.bam"
    output:
        "{sample}/raw/depth/{sample}.bed"
    log:
        "{sample}/log/raw_depth.log"
    wrapper:
        f"{wrapper_version}/wrappers/samtools_depth"


rule raw_coverage:
    input:
        bed = "{sample}/raw/depth/{sample}.bed",
        fasta = config["reference"]
    output:
        "{sample}/raw/sequana_coverage/sequana_coverage.html"
    wrapper:
        f"{wrapper_version}/wrappers/sequana_coverage"
