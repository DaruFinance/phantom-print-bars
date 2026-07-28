"""phantombars -- executable OHLC bar construction and the selection-fidelity
experiment from "Prices That Never Existed" (phantom-print contamination in
backtests).

The paper's headline numbers were computed on a licensed tape that cannot be
redistributed; see DATA.md. This package ships the method (leak-free), a
synthetic fixture so the pipeline runs without that data, and, under reproduce/,
the committed result artifacts and a script that regenerates the paper figures
for a reader who does not hold the data.
"""
from .bars import build_bars, decompose_sources, prevalence, range_inflation_bp
from .cost import CostModel
from .fidelity import (cluster_gap_boot, effective_blocks, greedy_dedup,
                       spearman_ic, top_decile)
from .wfo import walk_forward

__all__ = [
    "build_bars", "prevalence", "decompose_sources", "range_inflation_bp",
    "CostModel", "walk_forward", "spearman_ic", "greedy_dedup",
    "effective_blocks", "cluster_gap_boot", "top_decile",
]
__version__ = "1.0.0"
