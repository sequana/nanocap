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
    resources:
        **config["fastp"]["resources"]
    container:
        config["apptainers"]["fastp"]
    wrapper:
        f"{manager.wrappers}/wrappers/fastp"



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
    resources:
        **config["filtered_mapping"]["resources"]
    container:
        config["apptainers"]["minimap2"]
    wrapper:
        f"{manager.wrappers}/wrappers/minimap2"


rule filtered_index:
    input:
        "{sample}/filtered/mapping/{sample}.sorted.bam"
    output:
        "{sample}/filtered/mapping/{sample}.sorted.bam.bai"
    container:
        config["apptainers"]["samtools"]
    shell:
        """
        samtools index {input}
        """


rule filtered_depth:
    input:
        "{sample}/filtered/mapping/{sample}.sorted.bam",
        "{sample}/filtered/mapping/{sample}.sorted.bam.bai"
    output:
        "{sample}/filtered/depth/{sample}.bed"
    log:
        "{sample}/log/filtered_depth.log"
    container:
        config["apptainers"]["samtools"]
    wrapper:
        f"{manager.wrappers}/wrappers/samtools_depth"


rule filtered_coverage:
    input:
        bed = "{sample}/filtered/depth/{sample}.bed",
        fasta = config["reference"]
    output:
        "{sample}/filtered/sequana_coverage/sequana_coverage.html"
    params:
        output_directory="{sample}/filtered/sequana_coverage",
        circular=True,
        window_size=20000
    container:
        config["apptainers"]["sequana"]
    wrapper:
        f"{manager.wrappers}/wrappers/sequana_coverage"
