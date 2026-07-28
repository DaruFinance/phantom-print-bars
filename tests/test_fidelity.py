"""Fidelity metrics: rank-IC behaviour and bootstrap determinism."""
import numpy as np

from phantombars.fidelity import (cluster_gap_boot, effective_blocks,
                                  greedy_dedup, spearman_ic)


def test_spearman_ic_perfect_and_null():
    x = np.arange(50.0)
    assert spearman_ic(x, x) > 0.999
    rng = np.random.default_rng(0)
    assert abs(spearman_ic(rng.normal(size=200), rng.normal(size=200))) < 0.2


def test_greedy_dedup_shrinks_correlated_corpus():
    rng = np.random.default_rng(1)
    base = rng.normal(size=(1, 300))
    # 40 near-duplicates of one series -> should collapse to ~1 block
    R = np.repeat(base, 40, axis=0) + rng.normal(0, 1e-3, (40, 300))
    sel = greedy_dedup(R, rank_key=np.arange(40), tau=0.5)
    assert len(sel) <= 3


def test_cluster_bootstrap_is_deterministic():
    rng_a = np.random.default_rng(12345)
    rng_b = np.random.default_rng(12345)
    R = np.random.default_rng(0).normal(size=(30, 200))
    reps = greedy_dedup(R, np.arange(30), tau=0.6)
    blocks = effective_blocks(R, reps)
    xn = np.random.default_rng(2).normal(size=30)
    xc = xn + 0.05
    y = np.random.default_rng(3).normal(size=30)
    fn = lambda pool: (spearman_ic(xn[pool], y[pool]), spearman_ic(xc[pool], y[pool]))
    a = cluster_gap_boot(blocks, fn, rng_a, n_boot=500)
    b = cluster_gap_boot(blocks, fn, rng_b, n_boot=500)
    assert a == b            # same seed -> bit-identical
