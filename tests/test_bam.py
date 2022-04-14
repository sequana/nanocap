#  This file is part of Sequana software
#
#  Copyright (c) 2016-2022 - Sequana Dev Team (https://sequana.readthedocs.io)
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  Website:       https://github.com/sequana/sequana
#  Website:       https://github.com/sequana/nanocap
#  Documentation: http://sequana.readthedocs.io
#  Documentation: https://github.com/sequana/nanocap/README.rst
from sequana_pipelines.nanocap.src.bam import BamMetrics
from . import test_dir


def test_get_metrics_per_chr():
    bamfile = test_dir / "resources" / "sequence.bam"
    bam = BamMetrics(bamfile)
    basic_metrics = bam.get_metrics_per_chr()
    assert "N16961chr2" in basic_metrics
    assert basic_metrics["N16961chr2"]["read_count"] == 10
