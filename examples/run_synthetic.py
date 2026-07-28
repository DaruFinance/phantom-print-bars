"""End-to-end demonstration on synthetic data (no licensed tape required).

Generates a panel of synthetic symbols with injected phantom prints, builds naive
and executable bars, and runs the paper's two-arm selection experiment at demo
scale: each knob combination is a strategy, scored as a cross-symbol portfolio.

  Arm N : rank strategies by their in-sample Sharpe on NAIVE bars.
  Arm C : rank strategies by their in-sample Sharpe on CLEAN bars.
  Truth : each strategy's out-of-sample Sharpe on the CLEAN (executable) bars.

The fidelity gap is rank-IC(Arm C) minus rank-IC(Arm N): how much more faithfully
clean-bar selection predicts executable out-of-sample than naive-bar selection.
This reproduces the *mechanism* on controlled ground truth (a small illustrative
corpus). The magnitudes are fixture-specific, not the paper's full-universe
headline numbers -- those are in reproduce/ (run print_headline.py).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from phantombars.bars import build_bars, prevalence
from phantombars.fidelity import spearman_ic
from phantombars.strategies import KNOB_GRID, breakout_trades, sharpe
from phantombars.cost import CostModel
from phantombars.synth import synth_panel

SEED = 12345


def main():
    panel = synth_panel(n_symbols=30, seed=SEED, n_bars=1000, prints_per_bar=30,
                        phantom_rate=0.5)
    cost = CostModel()
    sym_bars = {s: build_bars(g) for s, g in panel.groupby("symbol")}
    print(f"prevalence (S00): {prevalence(sym_bars['S00']):.3f} of bars phantom-affected")

    # Each knob combination is a strategy, scored as a cross-symbol portfolio.
    naive_is, clean_is, clean_oos = [], [], []
    for knob in KNOB_GRID:
        n_is, c_is, c_oos = [], [], []
        for bars in sym_bars.values():
            half = len(bars) // 2
            isb, oob = bars.iloc[:half], bars.iloc[half:]
            n_is.append(sharpe(breakout_trades(isb, sel_prefix="naive", cost=cost, **knob)))
            c_is.append(sharpe(breakout_trades(isb, sel_prefix="clean", cost=cost, **knob)))
            c_oos.append(sharpe(breakout_trades(oob, sel_prefix="clean", cost=cost, **knob)))
        naive_is.append(np.nanmean(n_is))       # cross-symbol portfolio Sharpe
        clean_is.append(np.nanmean(c_is))
        clean_oos.append(np.nanmean(c_oos))

    naive_is, clean_is, clean_oos = map(np.array, (naive_is, clean_is, clean_oos))
    ic_n = spearman_ic(naive_is, clean_oos)     # Arm N: naive-IS -> clean-OOS
    ic_c = spearman_ic(clean_is, clean_oos)     # Arm C: clean-IS -> clean-OOS

    print("\n=== synthetic selection-fidelity demo ===")
    print(f" strategies (knob combos): {len(KNOB_GRID)} cross-symbol portfolios over 30 symbols")
    print(f" rank-IC  Arm N (naive-IS selection): {ic_n:+.4f}")
    print(f" rank-IC  Arm C (clean-IS selection): {ic_c:+.4f}")
    print(f" fidelity gap (Arm C - Arm N):        {ic_c - ic_n:+.4f}")
    print(" mechanism: naive bars inflate the breakout threshold, so naive-IS selection"
          " ranks strategies less faithfully to executable out-of-sample than clean-IS does.")


if __name__ == "__main__":
    main()
