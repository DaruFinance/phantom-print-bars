"""Pollute-and-verify: the walk-forward procedure itself must not leak.

The test runs the legitimate walk-forward on a fixture and confirms its
out-of-sample Sharpe is modest, then runs a deliberately-polluted variant that
tunes the knobs by peeking at the out-of-sample window (a look-ahead), and
confirms the pollution is DETECTED as a strictly, materially higher out-of-sample
Sharpe. Tuning on the OOS window can only inflate its own OOS score, so the
polluted procedure dominates the clean one; if the clean procedure ever matched
the polluted one, that would be the signature of a leak in the harness.
"""
import numpy as np

from phantombars.bars import build_bars
from phantombars.cost import CostModel
from phantombars.strategies import KNOB_GRID, breakout_trades, sharpe
from phantombars.synth import synth_prints


def _wfo(bars, pollute: bool, is_len=120, oos_len=60):
    """Clean WFO tunes on IS; the polluted variant tunes on the OOS window itself."""
    cost = CostModel()
    n = len(bars)
    oos = []
    start = 0
    while start + is_len + oos_len <= n:
        is_b = bars.iloc[start:start + is_len]
        oos_b = bars.iloc[start + is_len:start + is_len + oos_len]
        tune_on = oos_b if pollute else is_b       # <-- the injected look-ahead
        best, best_s = KNOB_GRID[0], -np.inf
        for k in KNOB_GRID:
            s = sharpe(breakout_trades(tune_on, sel_prefix="clean", cost=cost, **k))
            if s > best_s:
                best_s, best = s, k
        oos.append(sharpe(breakout_trades(oos_b, sel_prefix="clean", cost=cost, **best)))
        start += oos_len
    return float(np.nanmean(oos))


def test_pollution_is_detected():
    # An active fixture (enough breakouts trigger for the knob search to bite),
    # with no predictable edge in the efficient price.
    bars = build_bars(synth_prints("NULL", n_bars=2000, prints_per_bar=30,
                                    phantom_rate=0.5, seed=7))
    clean_oos = _wfo(bars, pollute=False)
    leaked_oos = _wfo(bars, pollute=True)
    # Tuning on the OOS window strictly dominates tuning on the IS window; the leak
    # manufactures a materially higher out-of-sample Sharpe. That separation is the
    # detectable signature the harness must expose.
    assert leaked_oos > clean_oos + 0.1, (
        f"pollution not detected: leaked={leaked_oos:.3f} clean={clean_oos:.3f}")
