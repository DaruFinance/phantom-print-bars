"""Print the paper's headline numbers from the committed full-universe result JSON.

Runs for any reader (the licensed tape is not needed): every headline number in
the paper is reproducible from results.json + prevalence_fixed.json here.
"""
import json
import os

HERE = os.path.dirname(__file__)


def main():
    r = json.load(open(os.path.join(HERE, "results.json")))
    pv = json.load(open(os.path.join(HERE, "prevalence_fixed.json")))
    A = r["APPROACH_C"]
    g = pv["global_stats"]
    d = pv["decomposition"]

    print("PRICES THAT NEVER EXISTED -- full-universe headline (committed artifacts)")
    print("=" * 68)
    print(f"Universe            : {r['N_STRATEGIES_RAW']:,} strategies, "
          f"{r['N_DEDUP']} mutually uncorrelated")
    print(f"Prevalence (07-26)  : {g['prevalence']*100:.1f}% of bars phantom-affected "
          f"(median {g['med_bp']:.1f} bp, p99 {g['p99_bp']:.1f} bp)")
    print(f"Decomposition       : odd-lot {d['oddlot']*100:.0f}%, off-exch \"D\" "
          f"{d['trf']*100:.0f}%, other {d['inelig']*100:.0f}%, bounce {d['residual_bounce']*100:.0f}%")
    print("-" * 68)
    print(f"rank-IC  Arm N       : {A['rank_ic_arm_n_all']:.4f}")
    print(f"rank-IC  Arm C       : {A['rank_ic_arm_c_all']:.4f}")
    print(f"fidelity gap (all)   : {A['gap_all']:+.4f}  "
          f"[effective-N cluster boot: {A['gap_cluster_boot']['ci_lo']:+.4f}, "
          f"{A['gap_cluster_boot']['ci_hi']:+.4f}], p={A['gap_cluster_boot']['p']:.4g}")
    print(f"  (i.i.d. diagnostic : p={A['gap_iid7232_boot_DIAGNOSTIC']['p']:.4g} -- "
          "anticonservative, shown only to size the overstatement)")
    print(f"deduped gap (N={r['N_DEDUP']})   : {r['RANK_IC_GAP']:+.4f}  "
          f"(clean {r['RANK_IC_ARM_C']:.4f} vs naive {r['RANK_IC_ARM_N']:.4f})")
    print("-" * 68)
    P = r["PROFIT"]
    print(f"Edge-free           : best clean-OOS Sharpe {P['best_clean_oos_sharpe']:.2f}, "
          f"fraction positive {P['frac_clean_oos_positive']:.3f}")
    print(f"Selection value     : Arm N {P['armN_topdecile_clean_oos_sharpe']:.3f} vs "
          f"Arm C {P['armC_topdecile_clean_oos_sharpe']:.3f} top-decile clean-OOS Sharpe")
    print("=" * 68)
    print("Deployment penalty is a proved consequence (Theorem 3), evaluated at these"
          " parameters -- see the paper; no profit is claimed on this edge-free tape.")


if __name__ == "__main__":
    main()
