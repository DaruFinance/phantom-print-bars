# Locked analysis plan

Study: *Prices That Never Existed: A Universe-Scale Measurement of Phantom-Print
Contamination in Equity Backtests.*

## What this file is, and what it is not

This is a transcription of the analysis plan as it stood in the private research
repository at the design freeze, released so a third party can check the paper's
reported design against the design that was fixed before the full-universe compute
ran. The transcription was assembled on 2026-08-12 from the frozen source. Its
SHA-256, recorded in `LOCK_HASHES.md`, fixes this text from that date forward.

The evidence for the freeze date is the commit history of the private research
repository, not this file. The constants and the primary endpoint below sit in a
`PRE-SPECIFIED DEFAULTS` block that is byte-identical across commits `321dfd3`
(2026-06-26 16:07 UTC-3) and `174834a` (2026-06-30 12:49 UTC-3). The full-universe
run started on 2026-07-23 and its statistics stage finished on 2026-07-26, four
weeks after the last commit that could have touched the design. Post-lock additions
are listed in their own section below and are marked in the paper as confirmatory
rather than locked.

## Universe and window

* Universe: the US equity top 1,000 names by dollar volume, point-in-time,
  including delisted names. 998 names resolve over the tape.
* Prevalence and decomposition: the full tape, 2007 to 2026.
* Strategy experiment: the odd-lot era only, 2014-01-02 to 2026-07-24. Odd-lot
  executions were absent from the consolidated tape before December 2013, so the
  mechanism does not operate before then.
* Development panel, on which every design choice was fixed before the full
  universe was touched: NVDA, AAPL, TSLA (high-turnover, odd-lot-heavy), SPY, QQQ,
  SQQQ (off-exchange-heavy ETFs), BAC, F (low-priced), over 2021 to 2023.

## Bar construction

Both bar sets are built from one trades feed by filtering, never by comparing two
differently reconstructed vendor products.

* Naive bar: maximum and minimum over every print in the interval.
* Executable bar: maximum and minimum over the prints that executed at or inside
  the prevailing NBBO.
* Every filter uses print-time information only (the sale-condition bitmask and the
  NBBO carried with the trade), so the cleaning is causal.

## Strategy corpus

* Twelve structural families: SMA, EMA, MACD, RSI, STOCH and ATR, plus six ported
  structural families (volcomp, slope, roc_trend, breakout_trend, htf_break,
  session_mom).
* 7,232 parameter specifications over the declared grid: thresholds (1.0, 1.5, 2.0,
  2.5), lookbacks (50, 150, 300), stop fractions (0, 0.01, 0.02) and target
  fractions (0, 0.02, 0.04) of entry price.
* The unit of analysis is the strategy, defined as an equal-weight cross-symbol
  portfolio over the universe. It is not the symbol-strategy pair.
* Costs are charged round-trip on every fill: a modeled time-of-day half-spread
  plus a per-fill commission.

## Walk-forward and the two arms

* Rolling walk-forward, in-sample 126 trading days, out-of-sample 21 trading days.
* Arm N selects and tunes in-sample on naive bars. Arm C selects and tunes
  in-sample on executable bars.
* Both arms are scored out-of-sample on executable bars, because a live order can
  only fill at an executable price.
* An internal-validity control scores Arm N against its own naive out-of-sample.

## Primary endpoint

The rank-IC gap, Arm C minus Arm N, where rank-IC is the Spearman correlation
between the in-sample strategy ranking and the executable out-of-sample ranking.
Fixed up front and not retuned to enlarge the gap. A null, zero or reversed gap is
to be reported plainly as the finding.

## Pre-specified constants

| Constant | Value | Role |
|---|---|---|
| `TAU` | 0.50 | greedy de-correlation threshold, keep strategies with pairwise abs(corr) below it |
| `DEDUP_KEY` | `mean_is` | outcome-neutral ranking key, in-sample only, symmetric across arms |
| `IS_FLOOR` | 0.20 | replication-ratio tail guard, drops abs(IS Sharpe) below the floor |
| `TOP_DECILE` | 0.10 | selection-value cutoff, top 10% by in-sample metric under each arm |
| `N_BOOT` | 5000 | bootstrap replications |
| `SEED` | 12345 | fixed seed |
| `CLUSTER_DEF` | symbol | block-bootstrap cluster identifier at lock time |

## Robustness sweep, declared in advance

* De-duplication threshold swept over 0.3, 0.5, 0.7.
* De-duplication ranking key swept over `mean_is` and `n_trades`.
* Cost multiplier stress at 3x and 5x.

## Inference and reporting rules

* Significance is priced with a block bootstrap, never an i.i.d. bootstrap over
  correlated strategies. Any i.i.d. figure is reported as a diagnostic that shows
  how far independence would overstate precision.
* Multiple testing is handled at the assembly step: deflated Sharpe ratio, BH-FDR,
  and PBO via CSCV where the corpus supports it.
* Controls to be run through the identical pipeline: a random equal-count
  print-drop placebo, a two-arm CME futures cross-market control, the December 2013
  odd-lot tape onset, and the round-lot redefinition.
* A control that returns a null is reported as a null.

## Post-lock additions

These entered after the freeze and are confirmatory, not pre-registered. The paper
marks each one where it appears.

1. **Effective-N block bootstrap over correlation blocks.** The locked cluster unit
   was the symbol. The paper prices significance on roughly 20 correlation blocks
   instead, formed by assigning each strategy to its most-correlated de-duplicated
   representative. The change was made because the unit of analysis is the
   cross-symbol strategy, which leaves the symbol cluster undefined. It is the
   more conservative choice, and the locked i.i.d.-over-strategies alternative is
   reported alongside it as the anticonservative diagnostic.
2. **Family-clustered gap.** Clustering the gap by strategy family was added to test
   whether a signal-family mechanism explains the effect. It does not.
3. **Two-sided distortion measurement.** The split of the corpus into strategies
   whose in-sample Sharpe is inflated and deflated by phantom prints was measured
   after the freeze, in response to the observation that a sign-definite range
   bias does not imply a sign-definite backtest bias.
4. **The formal theory.** Proposition 1, Theorems 1 to 3, Corollary 2, Remark 4 and
   Proposition 2 were written after the empirical freeze. They carry the claims an
   edge-free universe cannot support by measurement, and the paper states that
   status wherever they appear.
5. **Tick-resolved intrabar measurement.** Run on nine symbol-days after the freeze
   to separate intrabar ordering from bar-extreme contamination.

## Deviations from the locked plan

PBO via CSCV is not reported. The de-duplicated corpus holds about 20 strategies,
too few configurations for the combinatorially symmetric split to run. The deflated
Sharpe ratio, which is zero for both arms, already delivers the edge-free
conclusion at the assembly step.
