"""A small set of structural strategy families that trade against bar extremes.

These are the shapes a path-dependent intraday backtest exercises: a breakout
that references the prior bar's high, and a protective stop that references the
bar low. Both touch the bar extremes, which is exactly where phantom prints live,
so their in-sample performance depends on whether the bars are naive or clean.

A strategy consumes the *selection* bars (naive under Arm N, clean under Arm C)
to decide when it would have entered/exited, but its realised PnL is always
scored on the *clean* (executable) bars, because a live order can only fill at an
executable price. This split is the whole experiment.

Positions are long-only for simplicity; a trade opens on a breakout of the prior
high and closes on either a stop below the entry or a fixed maximum hold.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .cost import CostModel


def _bars_arrays(bars: pd.DataFrame, prefix: str):
    return (bars[f"{prefix}_open"].to_numpy(float),
            bars[f"{prefix}_high"].to_numpy(float),
            bars[f"{prefix}_low"].to_numpy(float),
            bars[f"{prefix}_close"].to_numpy(float))


def breakout_trades(bars: pd.DataFrame, lookback: int, stop_bp: float,
                    max_hold: int, sel_prefix: str, cost: CostModel):
    """Run the breakout on `sel_prefix` bars (naive or clean) for the ENTRY/EXIT
    decisions, but realise each closed trade's return on the CLEAN bars.

    Returns an array of per-trade net returns in basis points.
    """
    so, sh, sl, sc = _bars_arrays(bars, sel_prefix)     # selection bars
    co, ch, cl, cc = _bars_arrays(bars, "clean")        # execution truth
    n = len(bars)
    roll_high = pd.Series(sh).shift(1).rolling(lookback).max().to_numpy()
    trades = []
    i = 0
    rt = cost.round_trip_bp()
    while i < n - 1:
        thr = roll_high[i]
        if not np.isfinite(thr) or not (sh[i] > thr):
            i += 1
            continue
        # Entry at the breakout threshold, scored on the executable bar.
        entry = thr
        stop = entry * (1.0 - stop_bp / 1e4)
        exit_px = None
        j = i + 1
        end = min(n - 1, i + max_hold)
        while j <= end:
            if cl[j] <= stop:                # executable low pierces the stop
                exit_px = stop
                break
            j += 1
        if exit_px is None:
            exit_px = cc[min(j, n - 1)]      # time exit at the executable close
        ret_bp = (exit_px / entry - 1.0) * 1e4 - rt
        trades.append(ret_bp)
        i = j + 1
    return np.asarray(trades, dtype=float)


def sharpe(returns_bp: np.ndarray) -> float:
    r = np.asarray(returns_bp, dtype=float)
    r = r[np.isfinite(r)]
    if r.size < 3 or r.std(ddof=1) == 0:
        return 0.0
    return float(r.mean() / r.std(ddof=1))


# Knob grids the walk-forward tunes in-sample (structural shape fixed, knobs tunable).
KNOB_GRID = [
    {"lookback": lb, "stop_bp": sb, "max_hold": mh}
    for lb in (5, 10, 20)
    for sb in (15, 30, 60)
    for mh in (10, 30)
]
