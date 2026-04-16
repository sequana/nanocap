rule fastp:
    input:
        fastq = get_raw_data
    output:
        r1 = "{sample}/fastp/{sample}.fastq.gz",
        html = "{sample}/fastp/{sample}.html",
        json = "{sample}/fastp/{sample}.json"
    params:
        options = config["fastp"]["options"],
        adapters = config["fastp"].get("adapters", ""),
        out2 = ""
    log:
        "{sample}/log/fastp.log"
    threads:
        config["fastp"]["threads"]
    resources:
        **config["fastp"]["resources"]
    container:
        config["apptainers"]["fastp"]
    shell:
        manager.get_shell("fastp/run", "v2")



rule filtered_mapping:
    input:
        fastq = "{sample}/fastp/{sample}.fastq.gz",
        reference = config["reference"]
    output:
        sorted = "{sample}/filtered/mapping/{sample}.sorted.bam"
    params:
        options = config["minimap2"]["options"]
    threads:
        config["minimap2"]["threads"]
    resources:
        **config["filtered_mapping"]["resources"]
    container:
        config["apptainers"]["minimap2"]
    shell:
        manager.get_shell("minimap2/align", "v1")


rule filtered_index:
    input:
        "{sample}/filtered/mapping/{sample}.sorted.bam"
    output:
        "{sample}/filtered/mapping/{sample}.sorted.bam.bai"
    log:
        "{sample}/log/filtered_index.log"
    container:
        config["apptainers"]["samtools"]
    shell:
        """
        samtools index {input} >{log} 2>&1
        """


rule filtered_depth:
    input:
        bam = "{sample}/filtered/mapping/{sample}.sorted.bam",
        bai = "{sample}/filtered/mapping/{sample}.sorted.bam.bai"
    output:
        "{sample}/filtered/depth/{sample}.bed"
    log:
        "{sample}/log/filtered_depth.log"
    params:
        options = ""
    container:
        config["apptainers"]["samtools"]
    shell:
        manager.get_shell("samtools_depth/run", "v1")


rule filtered_coverage:
    input:
        bed = "{sample}/filtered/depth/{sample}.bed",
        fasta = config["reference"]
    output:
        "{sample}/filtered/sequana_coverage/sequana_coverage.html"
    log:
        "{sample}/log/filtered_coverage.log"
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
        output_directory = "{sample}/filtered/sequana_coverage",
        window_size = config["sequana_coverage"]["window_size"]
    container:
        config["apptainers"]["sequana_coverage"]
    shell:
        manager.get_shell("sequana_coverage/run", "v1")
