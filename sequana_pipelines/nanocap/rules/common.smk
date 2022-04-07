"""Functions that define the pipeline path"""


def requested_output(manager):
    """Resolve all needed output knowing the user config."""
    output_list = [expand("{sample}/raw/sequana_coverage/sequana_coverage.html", sample=manager.samples)]
    output_list += [expand("{sample}/filtered/sequana_coverage/sequana_coverage.html", sample=manager.samples)]
    return output_list


def get_raw_data(wildcards):
    """Get raw data"""
    return manager.samples[wildcards.sample]
