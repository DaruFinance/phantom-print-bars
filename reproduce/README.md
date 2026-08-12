# Results inventory and figure provenance

Every number and every data-driven figure in the paper, with the committed artifact it
comes from and the command that regenerates it. All artifacts here are aggregated
analysis output. The licensed tape they were computed from is not redistributable and
is not in this repository.

```bash
python reproduce/print_headline.py     # headline numbers
python reproduce/print_tables.py       # the paper's data tables
python reproduce/verify_headline.py    # recompute the primary endpoint from the strategy table
python reproduce/make_figures.py       # figures into reproduce/figs/
```

## Artifacts

| File | Contents | Scope |
|---|---|---|
| `results.json` | selection-fidelity headline, bootstraps, deflated Sharpe, BH-FDR, replication ratio, selection value | full universe, 7,232 strategies |
| `strategy_metrics.parquet` | one row per strategy: in-sample and out-of-sample Sharpe under both arms, fill counts, family | full universe, 7,232 rows |
| `prevalence_fixed.json` | phantom-affected-bar share and range inflation, by year and by price band, plus the source decomposition | full universe, 1.46bn bars, 2007 to 2026 |
| `fig_scatter.json` | per-strategy points behind the fidelity scatter | uncorrelated subset |
| `fig3_equity.json` | top-decile basket equity curves under both arms | full universe |
| `results_futures.json` | two-arm CME futures control | 5 roots, 2023 |
| `per_root_phantom.json` | futures phantom-affected-bar share by root | 5 roots, 2023 |
| `futures_print_types.json` | dropped-print type counts on the futures tape | representative-day sample |
| `placebo.json` | three-arm random-print-drop placebo | eight-name development panel |
| `intrabar.json` | tick-resolved intrabar fill ambiguity, pooled and per stop/target cell | nine symbol-days |
| `fig_intrabar.json` | per-cell series behind the intrabar figure | nine symbol-days |

## Artifact digests

`MANIFEST.sha256` carries the SHA-256 of every artifact in this directory. Verify with:

```bash
cd reproduce && sha256sum -c MANIFEST.sha256
```

## Figure provenance

| Paper figure | Artifact | Regenerated as |
|---|---|---|
| Fig 1, the phantom candle | none, hand-drawn schematic | not reproduced |
| Fig 2a, prevalence by year with the odd-lot share | `prevalence_fixed.json` | `figs/fig4_prevalence_heatmap.png` |
| Fig 2b, median range inflation by price band | `prevalence_fixed.json` | `figs/fig5_magnitude_dist.png` |
| Fig 3, stacked attribution by print source | `prevalence_fixed.json` | `figs/fig6_decomposition.png` |
| Fig 4a, in-sample rank against clean out-of-sample | `results.json`, `fig_scatter.json` | `figs/fig2_replication_scatter.png` |
| Fig 4b, top-decile realized equity | `fig3_equity.json` | `figs/fig3_topN_equity.png` |
| Fig 5, intrabar ambiguity, tick-resolved | `intrabar.json`, `fig_intrabar.json` | `figs/fig7_intrabar.png` |

Output filenames keep their original numbering from the analysis stage and do not track
the paper's figure numbers. The mapping above is the authority.

## Number inventory

| Paper location | Quantity | Artifact | Key |
|---|---|---|---|
| Abstract, §6 | 42.3% of bars phantom-affected | `prevalence_fixed.json` | `global_stats.prevalence` |
| §6 | median 3.4bp, p99 55.8bp range inflation | `prevalence_fixed.json` | `global_stats` |
| §6, Table 2 | prevalence by year, 2007 to 2026 | `prevalence_fixed.json` | `by_year` |
| §6 | prevalence and magnitude by price band | `prevalence_fixed.json` | `by_price_bucket` |
| §7, Table 4, Fig 3 | 76.3 / 18.4 / 4.7 / 0.7 source split | `prevalence_fixed.json` | `decomposition` |
| §8, Table 5 | rank-IC 0.9948 and 0.9987, gap +0.0039 | `results.json` | `APPROACH_C` |
| §8, Table 5 | block bootstrap CI [0.0025, 0.0093], p < 0.001 | `results.json` | `APPROACH_C.gap_cluster_boot` |
| §8, Table 5 | i.i.d. diagnostic CI [0.0036, 0.0043] | `results.json` | `APPROACH_C.gap_iid7232_boot_DIAGNOSTIC` |
| §8 | uncorrelated subset 0.9729 against 0.9925, p = 0.06 | `results.json` | `RANK_IC_*`, `RANK_IC_GAP_BOOT` |
| §8 | internal-validity control, Arm N against its own out-of-sample 0.991 | `results.json` | `RANK_IC_N_HOME` |
| §8 | family-clustered gap +0.020, CI [0, 0.062], p = 0.12 | `results.json` | `RANK_IC_GAP_FAMILY_CLUSTERED` |
| §8 | deflated Sharpe zero in both arms | `results.json` | `DSR_ARM_N`, `DSR_ARM_C` |
| §8 | PBO not defined on the uncorrelated set | `results.json` | `PBO_ARM_N`, `PBO_ARM_C` are null |
| §8 | top-decile realized clean out-of-sample Sharpe, both arms | `results.json` | `PROFIT` |
| §8 | replication ratio, medians 1.11 and 1.07 | `results.json` | `REPL_ARM_N`, `REPL_ARM_C` |
| §5.6 | 85% inflated, 15% deflated in-sample | `strategy_metrics.parquet` | `verify_headline.py` |
| §10 | naive and clean trade at parity, 1.006x fills | `strategy_metrics.parquet` | `verify_headline.py` |
| §8 | edge-free: no positive out-of-sample Sharpe | `strategy_metrics.parquet` | `verify_headline.py` |
| §9, Fig 5 | 3.15% ambiguous, 0.51bp convention gap, tick truth at 0.444 | `intrabar.json` | `OVERALL` |
| §9 | 18.2% ambiguous at 5bp by 5bp, at most 0.5% at 20bp or wider | `fig_intrabar.json` | `cells` |
| §11, Table 7 | futures gap −0.00011, p = 0.076, N = 441 | `results_futures.json` | top level |
| §11 | 0.80% of futures bars phantom-affected, by root | `per_root_phantom.json` | `per_root`, `aggregate` |
| §11 | away-market prints are 99.6% of drops on CL, 98% on GC | `futures_print_types.json` | `per_root` |
| §12, Table 8 | placebo 0.558 against naive 0.913 and clean 0.998 | `placebo.json` | `rank_ic_*` |

## Numbers not backed by an artifact here

These are computed by the tape-side stage, which cannot be published, from a per-strategy
daily return matrix too large to commit. The paper reports them in full and they are
reproducible by a holder of the licensed tape.

* Table 6, the de-duplication sweep over threshold and ranking key.
* §10, the sub-period rank-IC gap by calendar year.
* §10, the cost-multiplier stress at 3x and 5x.
* §10, the round-lot redefinition change of −1.8 percentage points.
* §6, the bootstrap confidence intervals on prevalence.
