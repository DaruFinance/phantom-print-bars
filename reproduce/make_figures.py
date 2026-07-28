"""Regenerate the paper figures from the committed full-universe artifacts.

Runs for any reader (no licensed tape needed). Reproduces figures 2-6 from the
small committed JSONs in this directory. fig1 (the phantom-candle schematic) and
the tick-resolved intrabar figure are not data-driven / not reproduced here.
Determinism: no randomness; output is a pure function of the committed JSONs.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(__file__)
FIGS = os.path.join(HERE, "figs")
os.makedirs(FIGS, exist_ok=True)

INK, MUTED = "#1d1d1f", "#6b6b70"
C_N, C_C, C_A = "#c0504d", "#3a6ea5", "#4f8a6d"
SRC = {"oddlot": "#3a6ea5", "trf": "#c0504d", "inelig": "#caa45b", "residual_bounce": "#6f6f74"}
plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.dpi": 200, "font.size": 11, "axes.edgecolor": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def _load(name):
    return json.load(open(os.path.join(HERE, name)))


def fig2(res, sc):
    nis, cis, cos = map(lambda k: np.array(sc[k], float), ("naive_is", "clean_is", "clean_oos"))
    rn = (-nis).argsort().argsort() + 1
    rc = (-cis).argsort().argsort() + 1
    fig, ax = plt.subplots(figsize=(6.6, 5.0))
    ax.scatter(rn, cos, s=42, c=C_N, alpha=0.8, label=f"Arm N (naive-IS) {res['RANK_IC_ARM_N']:.4f}")
    ax.scatter(rc, cos, s=42, c=C_C, alpha=0.8, marker="D", label=f"Arm C (clean-IS) {res['RANK_IC_ARM_C']:.4f}")
    ax.axhline(0, color=MUTED, lw=0.7, ls=":")
    ax.set_xlabel("in-sample rank (1 = best)"); ax.set_ylabel("clean out-of-sample Sharpe")
    ax.set_title(f"Selection fidelity (uncorrelated corpus N={len(nis)}; gap {res['RANK_IC_GAP']:+.4f})")
    ax.legend(loc="lower left", fontsize=9)
    fig.savefig(os.path.join(FIGS, "fig2_replication_scatter.png"), bbox_inches="tight")


def fig3(eq):
    x = np.arange(len(eq["dates"]))
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(x, eq["arm_N_equity"], color=C_N, lw=1.9, label="Arm N top decile")
    ax.plot(x, eq["arm_C_equity"], color=C_C, lw=1.9, ls=(0, (4, 2)), label="Arm C top decile")
    ax.axhline(0, color=MUTED, lw=0.7, ls=":")
    yrs = [d[:4] for d in eq["dates"]]
    ticks = [yrs.index(y) for y in sorted(set(yrs))[::2] if y in yrs]
    ax.set_xticks(ticks); ax.set_xticklabels([yrs[t] for t in ticks])
    ax.set_xlabel("out-of-sample date"); ax.set_ylabel("cumulative clean-OOS return (bp)")
    ax.set_title("Top-decile basket equity: both arms lose identically (edge-free)")
    ax.legend(loc="lower left", fontsize=9)
    fig.savefig(os.path.join(FIGS, "fig3_topN_equity.png"), bbox_inches="tight")


def fig4(pv):
    by = sorted(pv["by_year"], key=lambda r: r["year"])
    yrs = [r["year"] for r in by]
    prev = [100 * r["prevalence"] for r in by]
    odd = [r["oddlot_share"] or 0 for r in by]
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.bar(yrs, prev, color=C_C, alpha=0.85, width=0.7); ax.set_ylim(0, 100)
    ax.set_ylabel("phantom-affected bars (%)", color=C_C)
    ax2 = ax.twinx(); ax2.plot(yrs, odd, color=C_N, lw=2, marker="o", ms=4); ax2.set_ylim(0, 1)
    ax2.set_ylabel("odd-lot share of inflation", color=C_N); ax2.spines["top"].set_visible(False)
    ax.axvline(2013.5, color=INK, lw=1.2, ls=(0, (4, 2)))
    ax.text(2013.4, 92, "Dec 2013 onset", ha="right", va="top", fontsize=8.5)
    ax.set_xlabel("year"); ax.set_title("Phantom prevalence by year: the 2013 odd-lot onset")
    fig.savefig(os.path.join(FIGS, "fig4_prevalence_heatmap.png"), bbox_inches="tight")


def fig5(pv):
    order = ["<5", "5-20", "20-100", "100-500", "500+"]
    pb = {r["bucket"]: r for r in pv["by_price_bucket"]}
    med = [pb[b]["med_bp"] for b in order]; prev = [100 * pb[b]["prevalence"] for b in order]
    x = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(7.0, 4.4))
    ax.bar(x, med, color=C_A, alpha=0.85, width=0.6)
    for i, (mv, pvv) in enumerate(zip(med, prev)):
        ax.text(i, mv + 0.3, f"{mv:.1f} bp", ha="center", fontsize=9)
        ax.text(i, 0.4, f"{pvv:.0f}% aff.", ha="center", fontsize=8, color="white")
    ax.set_xticks(x); ax.set_xticklabels(["$<$5", "5-20", "20-100", "100-500", "500+"])
    ax.set_xlabel("price band ($)"); ax.set_ylabel("median range inflation (bp)")
    ax.set_title("Phantom magnitude by price band")
    fig.savefig(os.path.join(FIGS, "fig5_magnitude_dist.png"), bbox_inches="tight")


def fig6(pv):
    d = pv["decomposition"]
    order = ["oddlot", "trf", "inelig", "residual_bounce"]
    names = {"oddlot": "odd-lot 76%", "trf": 'off-exch "D" 18%', "inelig": "other 5%", "residual_bounce": "bounce 1%"}
    fig, ax = plt.subplots(figsize=(7.4, 2.4)); left = 0
    for s in order:
        v = d[s]; ax.barh(0, v, left=left, color=SRC[s], edgecolor="white", height=0.6)
        if v >= 0.03:
            ax.text(left + v / 2, 0, f"{v*100:.0f}%", ha="center", va="center",
                    color="white" if s != "inelig" else INK, fontweight="bold")
        left += v
    ax.set_xlim(0, 1); ax.set_yticks([]); ax.set_xlabel("share of total range inflation")
    ax.set_title("Phantom-print source decomposition (full universe)")
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=SRC[s]) for s in order],
              [names[s] for s in order], loc="upper center", bbox_to_anchor=(0.5, -0.35),
              ncol=4, fontsize=9, frameon=False)
    for sp in ("left", "top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(os.path.join(FIGS, "fig6_decomposition.png"), bbox_inches="tight")


def main():
    res, sc, pv, eq = _load("results.json"), _load("fig_scatter.json"), _load("prevalence_fixed.json"), _load("fig3_equity.json")
    fig2(res, sc); fig3(eq); fig4(pv); fig5(pv); fig6(pv)
    print(f"wrote 5 figures to {FIGS}/")


if __name__ == "__main__":
    main()
