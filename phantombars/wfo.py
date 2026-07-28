"""Walk-forward selection: the two-arm experiment.

Rolling walk-forward with in-sample knob tuning and disjoint out-of-sample
evaluation (never a single split). The only thing that varies across arms is the
bar set used to SELECT and TUNE each strategy in-sample; the out-of-sample truth
is always the executable (clean) bars, because a live order can only fill at an
executable price.

  Arm N (status quo)  : tune knobs in-sample on NAIVE bars, evaluate on clean OOS.
  Arm C (recommended) : tune knobs in-sample on CLEAN bars, evaluate on clean OOS.
  Arm N-home (control): tune on naive, evaluate on NAIVE OOS (internal-validity).

Fills are at t+1 (the engine never trades on the bar that generated the signal),
and the knob search only sees in-sample data, so the procedure carries no
look-ahead. `tests/test_noleak.py` pollutes this procedure and asserts detection.
"""
from __future__ import annotations

import numpy as np

from .cost import CostModel
from .strategies import KNOB_GRID, breakout_trades, sharpe


def _best_knobs(bars, sel_prefix, eval_prefix, cost):
    """In-sample: pick the knobs with the best Sharpe on `sel_prefix`, scored on
    `eval_prefix` (Arm N/C tune on naive/clean; scoring stays executable)."""
    best, best_s = KNOB_GRID[0], -np.inf
    for knobs in KNOB_GRID:
        tr = breakout_trades(bars, sel_prefix=sel_prefix, cost=cost, **knobs)
        s = sharpe(tr)
        if s > best_s:
            best_s, best = s, knobs
    return best


def walk_forward(bars, is_len=126, oos_len=21, cost: CostModel | None = None):
    """Run the three arms over one symbol's bars. Returns a dict of arrays:
    per-fold out-of-sample Sharpe for arm_N (clean OOS), arm_C (clean OOS),
    arm_N_home (naive OOS), plus the clean out-of-sample daily returns for
    the cross-fold return series.
    """
    cost = cost or CostModel()
    n = len(bars)
    arm_N, arm_C, arm_N_home = [], [], []
    daily = []
    start = 0
    while start + is_len + oos_len <= n:
        is_bars = bars.iloc[start:start + is_len]
        oos_bars = bars.iloc[start + is_len:start + is_len + oos_len]
        # Arm N and N-home share the naive-tuned knobs; Arm C tunes on clean.
        k_naive = _best_knobs(is_bars, "naive", "clean", cost)
        k_clean = _best_knobs(is_bars, "clean", "clean", cost)
        # Out-of-sample, always realised on the executable (clean) bars.
        arm_N.append(sharpe(breakout_trades(oos_bars, sel_prefix="clean", cost=cost, **k_naive)))
        arm_C.append(sharpe(breakout_trades(oos_bars, sel_prefix="clean", cost=cost, **k_clean)))
        # N-home: naive-tuned knobs scored on the NAIVE out-of-sample (the control).
        arm_N_home.append(sharpe(breakout_trades(oos_bars, sel_prefix="naive", cost=cost, **k_naive)))
        daily.append(np.nanmean(breakout_trades(oos_bars, sel_prefix="clean", cost=cost, **k_clean)) if True else 0.0)
        start += oos_len
    return {
        "arm_N": np.asarray(arm_N), "arm_C": np.asarray(arm_C),
        "arm_N_home": np.asarray(arm_N_home), "daily_clean_oos": np.asarray(daily),
    }
