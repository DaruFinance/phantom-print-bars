"""Recompute the headline from the per-strategy metrics table and check it against results.json.

This is the reproducibility check behind the paper's primary endpoint: the rank-IC of each
arm is recomputed from strategy_metrics.parquet (one row per strategy, aggregated over the
walk-forward) rather than read from the stored result. Exits non-zero on any mismatch.
"""
import json
import os
import sys

import pandas as pd
from scipy import stats as ss

HERE = os.path.dirname(__file__)
TOL = 1e-9


def main():
    d = pd.read_parquet(os.path.join(HERE, "strategy_metrics.parquet"))
    stored = json.load(open(os.path.join(HERE, "results.json")))["APPROACH_C"]

    arm_n = float(ss.spearmanr(d["naive_is"], d["clean_oos"]).correlation)
    arm_c = float(ss.spearmanr(d["clean_is"], d["clean_oos"]).correlation)
    gap = arm_c - arm_n
    inflated = float((d["naive_is"] > d["clean_is"]).mean())
    fills = float(d["naive_is_ntr"].sum() / d["clean_is_ntr"].sum())

    checks = [
        ("rank-IC Arm N", arm_n, stored["rank_ic_arm_n_all"]),
        ("rank-IC Arm C", arm_c, stored["rank_ic_arm_c_all"]),
        ("fidelity gap", gap, stored["gap_all"]),
    ]
    print(f"{'quantity':<16}{'recomputed':>14}{'stored':>14}{'delta':>12}")
    print("-" * 56)
    ok = True
    for name, got, want in checks:
        ok &= abs(got - want) < TOL
        print(f"{name:<16}{got:>14.10f}{want:>14.10f}{got - want:>12.2e}")

    print()
    print(f"strategies                {len(d):>10,}")
    print(f"families                  {d['family'].nunique():>10}")
    print(f"in-sample Sharpe inflated {inflated * 100:>9.1f}%   (deflated {100 - inflated * 100:.1f}%)")
    print(f"naive/clean in-sample fills{fills:>9.3f}x")
    print(f"best clean-OOS Sharpe     {d['clean_oos'].max():>10.4f}")
    print(f"median clean-OOS Sharpe   {d['clean_oos'].median():>10.4f}")
    print(f"fraction positive         {(d['clean_oos'] > 0).mean():>10.4f}")
    print()
    print("PASS: recomputed headline matches the stored artifact" if ok else "FAIL: mismatch")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
