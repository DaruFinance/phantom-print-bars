"""Bar construction: naive vs executable OHLC from a print (trade) stream.

This is the central method of the paper. Given a stream of trade prints, each
carrying a price, a size, an exchange tag and sale-condition flags, we build two
OHLC bars per interval:

  * naive bar    -- max/min/first/last over ALL prints (what a practitioner who
                    ignores condition codes builds by running a max and a min over
                    the raw tape).
  * executable   -- built over the marketable-reachable subset only: prints
    (clean) bar    executed at or inside the prevailing NBBO ("TRADE-NB"), i.e.
                    the prices a marketable order could actually have reached.

The naive bar is the UNION of all prints; the executable bar is a strict subset.
Hence (Proposition 1) the naive high is weakly above the executable high and the
naive low weakly below, so the phantom range inflation is >= 0 on every bar.

No data source is assumed. The caller supplies a DataFrame of prints with the
columns below; the eligibility test is pure per-print condition logic, so it
carries no look-ahead.

Required print columns
----------------------
price      : float, trade price (> 0)
size       : int,   share/contract quantity
exchange   : str,   reporting venue ("D" / "FINRA" == off-exchange TRF)
cond       : int,   sale-condition bitmask (0 == regular way); see COND_* below
at_nbbo    : bool,  True iff the print executed at or inside the prevailing NBBO
interval   : hashable, the bar key (e.g. a minute timestamp)

`at_nbbo` is the executable (TRADE-NB) flag. If a vendor gives you the NBBO at
print time instead, set at_nbbo = (bid <= price <= ask). It must be a
print-time quantity so the cleaning stays causal.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Sale-condition bits that make a print INELIGIBLE to set the official high/low/last
# (the exchanges suppress these from official OHLC; a naive bar reintroduces them).
COND_ODD_LOT = 1 << 0           # volume-eligible only
COND_AVG_PRICE = 1 << 1         # ".W" computed average, not a market print
COND_PRIOR_REF = 1 << 2         # ".P" priced as of an earlier time
COND_DERIVATIVE = 1 << 3        # VWAP / benchmark formula price
COND_FORM_T = 1 << 4            # ".T" pre/post market
COND_OUT_OF_SEQ = 1 << 5        # late / out-of-time-sequence report
INELIGIBLE_MASK = (COND_AVG_PRICE | COND_PRIOR_REF | COND_DERIVATIVE
                   | COND_FORM_T | COND_OUT_OF_SEQ)

ODD_LOT_MAX = 100               # a fill under a round lot is an odd lot
TRF_TAGS = frozenset({"D", "FINRA", "TRF"})

_OHLC = ["open", "high", "low", "close", "n", "volume"]


def _ohlc(g: pd.DataFrame) -> pd.Series:
    """First/max/min/last of price + count + summed size for one bar's prints."""
    p = g["price"].to_numpy()
    return pd.Series({
        "open": p[0], "high": p.max(), "low": p.min(), "close": p[-1],
        "n": len(p), "volume": int(g["size"].sum()),
    })


def is_executable(prints: pd.DataFrame) -> pd.Series:
    """Marketable-reachable mask: at/inside the NBBO. This is the TRADE-NB subset."""
    return prints["at_nbbo"].astype(bool)


def is_odd_lot(prints: pd.DataFrame) -> pd.Series:
    return prints["size"] < ODD_LOT_MAX


def is_off_exchange(prints: pd.DataFrame) -> pd.Series:
    return prints["exchange"].isin(TRF_TAGS)


def is_ineligible_condition(prints: pd.DataFrame) -> pd.Series:
    return (prints["cond"].to_numpy() & INELIGIBLE_MASK) != 0


def build_bars(prints: pd.DataFrame) -> pd.DataFrame:
    """Build naive and executable OHLC bars from a print stream.

    Returns one row per interval with columns:
      naive_{open,high,low,close,n,volume}, clean_{...},
      phantom_high  = naive_high - clean_high  (>= 0),
      phantom_low   = clean_low  - naive_low   (>= 0),
      inflation     = phantom_high + phantom_low (>= 0).
    """
    prints = prints.sort_values("interval", kind="stable")
    naive = (prints.groupby("interval", sort=True).apply(_ohlc, include_groups=False)
             .add_prefix("naive_"))
    ex = prints[is_executable(prints)]
    clean = (ex.groupby("interval", sort=True).apply(_ohlc, include_groups=False)
             .add_prefix("clean_"))
    out = naive.join(clean, how="left")
    # The executable bar is a subset of the naive bar, so naive extremes bound it.
    out["clean_high"] = out["clean_high"].fillna(out["naive_high"])
    out["clean_low"] = out["clean_low"].fillna(out["naive_low"])
    out["phantom_high"] = out["naive_high"] - out["clean_high"]
    out["phantom_low"] = out["clean_low"] - out["naive_low"]
    out["inflation"] = out["phantom_high"] + out["phantom_low"]
    return out.reset_index()


def range_inflation_bp(bars: pd.DataFrame) -> np.ndarray:
    """Phantom range inflation per bar in basis points of the clean close."""
    px = bars["clean_close"].to_numpy(dtype=float)
    px = np.where(px > 0, px, np.nan)
    return bars["inflation"].to_numpy(dtype=float) / px * 1e4


def prevalence(bars: pd.DataFrame) -> float:
    """Fraction of bars whose naive extreme differs from the executable one."""
    affected = (bars["naive_high"] > bars["clean_high"]) | (bars["naive_low"] < bars["clean_low"])
    return float(affected.mean())


def decompose_sources(prints: pd.DataFrame) -> dict:
    """Attribute the excess-above-executable range inflation to print sources by a
    nested cascade (order-dependent attribution, as the paper states): odd-lot ->
    off-exchange 'D' -> other ineligible -> residual bounce. Returns the share of
    total inflation contributed at each step."""
    prints = prints.sort_values("interval", kind="stable")
    base = build_bars(prints)[["interval", "clean_high", "clean_low"]].set_index("interval")

    def excess(sub: pd.DataFrame) -> pd.Series:
        b = build_bars(sub).set_index("interval")
        hi = np.maximum(b["naive_high"] - base["clean_high"].reindex(b.index), 0.0)
        lo = np.maximum(base["clean_low"].reindex(b.index) - b["naive_low"], 0.0)
        return (hi + lo).reindex(base.index).fillna(0.0)

    full = excess(prints)
    ex_odd = excess(prints[~is_odd_lot(prints)])
    ex_odd_trf = excess(prints[~is_odd_lot(prints) & ~is_off_exchange(prints)])
    ex_all = excess(prints[~is_odd_lot(prints) & ~is_off_exchange(prints)
                           & ~is_ineligible_condition(prints)])
    odd = float(np.maximum(full - ex_odd, 0).sum())
    trf = float(np.maximum(ex_odd - ex_odd_trf, 0).sum())
    inelig = float(np.maximum(ex_odd_trf - ex_all, 0).sum())
    bounce = float(np.maximum(ex_all, 0).sum())
    tot = odd + trf + inelig + bounce or 1.0
    return {"oddlot": odd / tot, "trf": trf / tot,
            "inelig": inelig / tot, "bounce": bounce / tot}
