rule raw_mapping:
    input:
        fastq = get_raw_data,
        reference = config["reference"]
    output:
        sorted = "{sample}/raw/mapping/{sample}.sorted.bam"
    params:
        options = config["minimap2"]["options"]
    threads:
        config["minimap2"]["threads"]
    resources:
        **config["raw_mapping"]["resources"]
    container:
        config["apptainers"]["minimap2"]
    shell:
        manager.get_shell("minimap2/align", "v1")


rule raw_index:
    input:
        "{sample}/raw/mapping/{sample}.sorted.bam"
    output:
        "{sample}/raw/mapping/{sample}.sorted.bam.bai"
    log:
        "{sample}/log/raw_index.log"
    container:
        config["apptainers"]["samtools"]
    shell:
        """
        samtools index {input} >{log} 2>&1
        """


rule raw_depth:
    input:
        bam = "{sample}/raw/mapping/{sample}.sorted.bam",
        bai = "{sample}/raw/mapping/{sample}.sorted.bam.bai"
    output:
        "{sample}/raw/depth/{sample}.bed"
    log:
        "{sample}/log/raw_depth.log"
    params:
        options = ""
    container:
        config["apptainers"]["samtools"]
    shell:
        manager.get_shell("samtools_depth/run", "v1")


rule raw_coverage:
    input:
        bed = "{sample}/raw/depth/{sample}.bed",
        fasta = config["reference"]
    output:
        "{sample}/raw/sequana_coverage/sequana_coverage.html"
    log:
        "{sample}/log/raw_coverage.log"
    params:
        annotation = config["sequana_coverage"]["annotation_file"],
        circular = config["sequana_coverage"]["circular"],
        chunksize = config["sequana_coverage"]["chunksize"],
        double_threshold = config["sequana_coverage"]["double_threshold"],
        gc_window_size = config["sequana_coverage"]["gc_window_size"],
        high_threshold = config["sequana_coverage"]["high_threshold"],
        low_threshold = config["sequana_coverage"]["low_threshold"],
        mixture_models = config["sequana_coverage"]["mixture_models"],
        options = config["sequana_coverage"]["options"],
        output_directory = "{sample}/raw/sequana_coverage",
        window_size = config["sequana_coverage"]["window_size"]
    container:
        config["apptainers"]["sequana_coverage"]
    shell:
        manager.get_shell("sequana_coverage/run", "v1")
