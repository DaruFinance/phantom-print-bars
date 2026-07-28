"""Synthetic print generator: a controlled-ground-truth stand-in for the licensed
tape, so the whole pipeline runs end to end for a reader who has no data.

The efficient price is a random walk with no predictable component (the edge-free
null). Executable prints land at/inside a spread around the efficient price;
phantom prints (odd lots and off-exchange prints, injected at a controllable rate)
land OUTSIDE the spread, widening the naive wick without being reachable by a
marketable order. Nothing here is a result; it is a null/positive-control fixture.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .bars import COND_PRIOR_REF, COND_FORM_T


def synth_prints(symbol: str, n_bars: int = 400, prints_per_bar: int = 20,
                 spread_bp: float = 5.0, phantom_rate: float = 0.4,
                 phantom_bp: float = 40.0, seed: int = 0) -> pd.DataFrame:
    """One symbol's print stream. `phantom_rate` = fraction of bars that carry an
    injected phantom extreme; `phantom_bp` = how far outside the spread it sits."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(0, spread_bp / 2, n_bars) / 1e4
    mid = 100.0 * np.exp(np.cumsum(steps))                 # efficient price per bar
    rows = []
    for b in range(n_bars):
        m = mid[b]
        half = m * spread_bp / 1e4 / 2
        # executable prints: at/inside the NBBO, round lots, regular condition
        for _ in range(prints_per_bar):
            px = m + rng.uniform(-half, half)
            rows.append((symbol, b, px, int(rng.integers(1, 10) * 100), "N", 0, True))
        # injected phantom prints on a fraction of bars: outside the spread, unreachable
        if rng.random() < phantom_rate:
            side = 1 if rng.random() < 0.5 else -1
            px = m * (1.0 + side * phantom_bp / 1e4)
            if rng.random() < 0.5:              # odd lot on an exchange venue
                rows.append((symbol, b, px, int(rng.integers(1, 99)), "N",
                             1 << 0, False))    # COND_ODD_LOT, not at NBBO
            else:                               # off-exchange late/benchmark "D" print
                rows.append((symbol, b, px, int(rng.integers(1, 10) * 100), "D",
                             COND_PRIOR_REF if rng.random() < 0.5 else COND_FORM_T, False))
    df = pd.DataFrame(rows, columns=["symbol", "interval", "price", "size",
                                     "exchange", "cond", "at_nbbo"])
    return df


def synth_panel(n_symbols: int = 12, seed: int = 12345, **kw) -> pd.DataFrame:
    """A panel of `n_symbols` independent synthetic symbol streams."""
    rng = np.random.default_rng(seed)
    return pd.concat(
        [synth_prints(f"S{k:02d}", seed=int(rng.integers(0, 1 << 30)), **kw)
         for k in range(n_symbols)],
        ignore_index=True,
    )
