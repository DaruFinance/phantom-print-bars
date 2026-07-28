"""Structural invariants of bar construction (Proposition 1 and the decomposition)."""
import numpy as np
import pandas as pd

from phantombars import build_bars, prevalence, decompose_sources
from phantombars.bars import COND_ODD_LOT
from phantombars.synth import synth_prints


def test_proposition_1_inflation_nonnegative():
    """The executable set is a subset of all prints, so the naive high is weakly
    above the executable high and the naive low weakly below: inflation >= 0."""
    prints = synth_prints("X", n_bars=300, phantom_rate=0.5, seed=1)
    bars = build_bars(prints)
    assert (bars["naive_high"] >= bars["clean_high"] - 1e-9).all()
    assert (bars["naive_low"] <= bars["clean_low"] + 1e-9).all()
    assert (bars["inflation"] >= -1e-9).all()          # sign-definite


def test_phantom_delta_is_the_injected_print():
    """A single odd-lot print above the executable high sets the naive high by
    exactly its displacement."""
    rows = [
        ("X", 0, 100.00, 200, "N", 0, True),
        ("X", 0, 100.05, 300, "N", 0, True),
        ("X", 0, 100.20, 50, "N", COND_ODD_LOT, False),   # phantom high, +0.15
        ("X", 0, 99.90, 100, "N", 0, True),
    ]
    prints = pd.DataFrame(rows, columns=["symbol", "interval", "price", "size",
                                         "exchange", "cond", "at_nbbo"])
    b = build_bars(prints).iloc[0]
    assert abs(b["clean_high"] - 100.05) < 1e-9
    assert abs(b["naive_high"] - 100.20) < 1e-9
    assert abs(b["phantom_high"] - 0.15) < 1e-9


def test_prevalence_rises_with_phantom_rate():
    low = prevalence(build_bars(synth_prints("A", phantom_rate=0.1, seed=2)))
    high = prevalence(build_bars(synth_prints("A", phantom_rate=0.8, seed=2)))
    assert high > low


def test_decomposition_shares_sum_to_one_and_nonneg():
    d = decompose_sources(synth_prints("A", n_bars=300, phantom_rate=0.6, seed=3))
    assert all(v >= -1e-9 for v in d.values())
    assert abs(sum(d.values()) - 1.0) < 1e-6
