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
##############################################################################
from itertools import takewhile

import pandas as pd
import pysam


COLNAMES = ["ctg", "start", "end", "mapq", "read_name", "read_length"]


class BamMetrics:
    """Read bam file, compute basic metrics and create some plot"""

    def __init__(self, filename):
        with pysam.AlignmentFile(filename) as bam_in:
            reads_info = [
                (
                    align.reference_name,
                    align.reference_start,
                    align.reference_end,
                    align.mapq,
                    align.query_name,
                    align.infer_read_length(),
                )
                for align in takewhile(lambda x: not x.is_unmapped, bam_in)  # take only mapped reads
            ]
        self.df = pd.DataFrame(reads_info, columns=COLNAMES)
        self.df.set_index('ctg', inplace=True)

    def get_metrics_per_chr(self):
        """Return dict with basic metrics"""
        iter_chr = ((ctg, self.df.loc[ctg]) for ctg in self.df.index.unique())
        return {
            ctg: {
                "read_count": len(subdf.read_name.unique()),
                "mean_length": f"{subdf.read_length.mean():.2f}",
                "median_length": int(subdf.read_length.median())
            } for ctg, subdf in iter_chr
        }
