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
    resources:
        **config["raw_mapping"]["resources"]
    container:
        config["apptainers"]["minimap2"]
    wrapper:
        f"{manager.wrappers}/wrappers/minimap2"


rule raw_index:
    input:
        "{sample}/raw/mapping/{sample}.sorted.bam"
    output:
        "{sample}/raw/mapping/{sample}.sorted.bam.bai"
    container:
        config["apptainers"]["samtools"]
    shell:
        """
        samtools index {input}
        """


rule raw_depth:
    input:
        "{sample}/raw/mapping/{sample}.sorted.bam",
        "{sample}/raw/mapping/{sample}.sorted.bam.bai"
    output:
        "{sample}/raw/depth/{sample}.bed"
    log:
        "{sample}/log/raw_depth.log"
    container:
        config["apptainers"]["samtools"]
    wrapper:
        f"{manager.wrappers}/wrappers/samtools_depth"


rule raw_coverage:
    input:
        bed = "{sample}/raw/depth/{sample}.bed",
        fasta = config["reference"]
    output:
        "{sample}/raw/sequana_coverage/sequana_coverage.html"
    params:
        output_directory="{sample}/raw/sequana_coverage",
        circular=True,
        window_size=20000

    container:
        config["apptainers"]["sequana"]
    wrapper:
        f"{manager.wrappers}/wrappers/sequana_coverage"
