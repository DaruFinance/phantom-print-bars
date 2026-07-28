"""Reproduce the paper's data tables from the committed full-universe artifacts.

Runs for any reader (the licensed tape is not needed): every table below is a pure
function of results.json + prevalence_fixed.json in this directory.
"""
import json
import os

HERE = os.path.dirname(__file__)


def _rule(w=68):
    print("-" * w)


def main():
    r = json.load(open(os.path.join(HERE, "results.json")))
    pv = json.load(open(os.path.join(HERE, "prevalence_fixed.json")))

    print("Table: phantom-affected-bar prevalence by year (full universe)")
    _rule()
    print(f"{'year':>6} {'bars':>14} {'prevalence':>11} {'median bp':>10} {'odd-lot share':>14}")
    for row in pv["by_year"]:
        print(f"{row['year']:>6} {row['n_bars']:>14,} {row['prevalence']*100:>10.1f}% "
              f"{row['med_bp']:>10.2f} {row['oddlot_share']:>14.2f}")
    print()

    print("Table: prevalence by price bucket")
    _rule()
    print(f"{'bucket':>10} {'bars':>14} {'prevalence':>11} {'median bp':>10}")
    for row in pv["by_price_bucket"]:
        print(f"{row['bucket']:>10} {row['n_bars']:>14,} {row['prevalence']*100:>10.1f}% "
              f"{row['med_bp']:>10.2f}")
    print()

    d = pv["decomposition"]
    print("Table: range-inflation decomposition by print source")
    _rule()
    print(f"  odd-lot            {d['oddlot']*100:>6.1f}%")
    print(f"  off-exchange \"D\"    {d['trf']*100:>6.1f}%")
    print(f"  other ineligible   {d['inelig']*100:>6.1f}%")
    print(f"  residual bounce    {d['residual_bounce']*100:>6.1f}%")
    print()

    A = r["APPROACH_C"]
    cb = A["gap_cluster_boot"]
    print("Table: selection fidelity (rank-IC, Arm N naive-tuned vs Arm C clean-tuned)")
    _rule()
    print(f"{'corpus':>22} {'N':>7} {'Arm N':>8} {'Arm C':>8} {'gap':>9} {'p':>8}")
    # Gap shown as the difference of the reported (4-dp) rank-ICs, matching the paper;
    # the bootstrap CI/p below are computed on the full-precision gap.
    gap_all_disp = round(A["rank_ic_arm_c_all"], 4) - round(A["rank_ic_arm_n_all"], 4)
    print(f"{'all strategies':>22} {r['N_STRATEGIES_RAW']:>7,} "
          f"{A['rank_ic_arm_n_all']:>8.4f} {A['rank_ic_arm_c_all']:>8.4f} "
          f"{gap_all_disp:>+9.4f} {cb['p']:>8.4g}")
    gb = r["RANK_IC_GAP_BOOT"]
    print(f"{'uncorrelated subset':>22} {r['N_DEDUP']:>7,} "
          f"{r['RANK_IC_ARM_N']:>8.4f} {r['RANK_IC_ARM_C']:>8.4f} "
          f"{r['RANK_IC_GAP']:>+9.4f} {gb['p']:>8.4g}")
    print(f"  cluster bootstrap CI (all): [{cb['ci_lo']:+.4f}, {cb['ci_hi']:+.4f}] "
          f"over {A['n_eff_blocks']} correlation blocks")


if __name__ == "__main__":
    main()
