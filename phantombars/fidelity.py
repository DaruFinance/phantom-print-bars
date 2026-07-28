"""Selection-fidelity metrics: rank-IC, greedy de-duplication, effective-N bootstrap.

The primary endpoint is the rank information coefficient: the Spearman rank
correlation between the per-strategy in-sample Sharpe and the executable
out-of-sample Sharpe. Arm C minus Arm N is the deployment-fidelity gap.

Because strategies (cross-symbol portfolios of the same specification families)
are highly correlated, an i.i.d. bootstrap over them overstates precision. We
price significance at the effective number of independent bets: each strategy is
assigned to its most-correlated de-duplicated representative, forming a small
number of correlation blocks, and the block bootstrap resamples whole blocks.
"""
from __future__ import annotations

import numpy as np
from scipy import stats as ss


def spearman_ic(x: np.ndarray, y: np.ndarray) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3 or np.ptp(x[m]) == 0 or np.ptp(y[m]) == 0:
        return 0.0
    return float(ss.spearmanr(x[m], y[m]).correlation)


def greedy_dedup(returns: np.ndarray, rank_key: np.ndarray, tau: float = 0.5):
    """Keep a strategy only if its max |Pearson corr| (on OOS daily returns) to the
    already-selected set is below tau. Rank candidates by `rank_key` (higher first).
    Returns the indices of the mutually uncorrelated subset."""
    order = np.argsort(-np.nan_to_num(rank_key, nan=-1e18))
    Z = returns - returns.mean(1, keepdims=True)
    sd = Z.std(1, keepdims=True)
    Z = np.where(sd > 1e-12, Z / np.where(sd > 1e-12, sd, 1.0), 0.0)
    kept = []
    for i in order:
        if not kept:
            kept.append(i)
            continue
        c = np.abs(Z[i] @ Z[kept].T) / Z.shape[1]
        if c.max() < tau:
            kept.append(i)
    return np.array(sorted(kept))


def effective_blocks(returns: np.ndarray, reps: np.ndarray):
    """Assign every strategy to its most-correlated de-duplicated representative,
    forming correlation blocks. Returns {rep_index: member_indices}."""
    Z = returns - returns.mean(1, keepdims=True)
    sd = Z.std(1, keepdims=True)
    Z = np.where(sd > 1e-12, Z / np.where(sd > 1e-12, sd, 1.0), 0.0)
    sim = np.abs(Z @ Z[reps].T) / Z.shape[1]
    label = np.asarray(reps)[np.argmax(sim, axis=1)]
    return {int(r): np.where(label == r)[0] for r in np.unique(label)}


def cluster_gap_boot(blocks: dict, gap_fn, rng, n_boot=5000):
    """Block bootstrap of a gap statistic. `gap_fn(pool_indices) -> (stat_N, stat_C)`.
    Resamples whole blocks; returns (point, ci_lo, ci_hi, p) for stat_C - stat_N."""
    keys = list(blocks.keys())
    base_n, base_c = gap_fn(np.concatenate([blocks[k] for k in keys]))
    point = base_c - base_n
    draws = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.choice(keys, size=len(keys), replace=True)
        pool = np.concatenate([blocks[k] for k in pick])
        gn, gc = gap_fn(pool)
        draws[b] = gc - gn
    lo, hi = np.percentile(draws, [2.5, 97.5])
    p = 2.0 * min((draws <= 0).mean(), (draws >= 0).mean())
    return point, float(lo), float(hi), float(min(1.0, p))


def top_decile(x: np.ndarray, q: float = 0.10):
    x = np.asarray(x, float)
    k = max(1, int(q * np.isfinite(x).sum()))
    return np.argsort(-np.nan_to_num(x, nan=-1e18))[:k]
