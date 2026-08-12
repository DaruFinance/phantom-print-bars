# phantom-print-bars

Replication code for **"Prices That Never Existed: Phantom Prints in OHLC Bars
and the Selection Fidelity of Backtests."**

A printed trade on the US consolidated tape reports that a transaction happened,
not that an order could have traded there. Odd lots, off-exchange (FINRA/TRF)
prints, and condition-coded trades are inaccessible to a marketable order, priced
off the current market, or excluded by the exchanges from the official high, low,
and last. A bar built by running a raw maximum and minimum over all prints
reintroduces exactly the prints the exchanges suppress, so its high sits above the
executable high and its low below the executable low. This repository implements
the two bar constructions the paper compares and the selection-fidelity experiment
that measures what the difference costs a backtest.

The paper's headline numbers were computed on a licensed tape that cannot be
redistributed (see [Data availability](#data-availability)). This repository
therefore ships:

* the **method**, source-agnostic and inspectable (`phantombars/`);
* a **synthetic fixture** so the whole pipeline runs with no licensed data
  (`phantombars/synth.py`, `examples/run_synthetic.py`);
* the **committed result artifacts**, the scripts that regenerate the paper's figures,
  tables and headline for a reader who does not hold the data, and a results inventory
  mapping every reported number to the artifact it comes from (`reproduce/`);
* the **locked analysis plan** and its SHA-256 (`preregistration/`);
* a **test suite** including a pollute-and-verify no-leak check (`tests/`).

## Install

```bash
pip install -e .          # or: pip install -r requirements.txt
```

Python 3.9+; depends only on numpy, pandas, scipy, matplotlib, pyarrow, pytest.

## Reproduce the paper (no licensed data needed)

```bash
python reproduce/print_headline.py     # headline numbers from committed results.json
python reproduce/print_tables.py       # the paper's data tables (prevalence, decomposition, fidelity, intrabar)
python reproduce/verify_headline.py    # recomputes the primary endpoint from strategy_metrics.parquet
python reproduce/make_figures.py       # regenerates every data-driven figure into reproduce/figs/
```

`verify_headline.py` is the reproducibility check behind the primary endpoint: it
recomputes both arms' rank-IC from the per-strategy table and exits non-zero unless it
matches the stored result. `reproduce/README.md` is the results inventory and figure
provenance, one row per reported number.

## Smoke test (about 15 seconds, no licensed data)

```bash
python examples/run_synthetic.py
```

Generates a panel of synthetic symbols with injected phantom prints, builds naive
and executable bars, and runs the two-arm selection experiment end to end. Selecting
on clean bars is more faithful to executable out-of-sample performance than selecting
on naive bars, so the printed fidelity gap is positive: this confirms the core
mechanism on controlled ground truth. Magnitudes are fixture-specific, not the
paper's numbers. It runs unchanged from PowerShell.

## Tests

```bash
pytest -q
```

Covers Proposition 1 (the naive range weakly bounds the executable range, so the
inflation is sign-definite), the source decomposition, the fidelity metrics and
their determinism, and a **pollute-and-verify** test that injects a look-ahead
into the walk-forward and confirms it is detected.

## Pre-registration

`preregistration/analysis-plan-locked.md` is the analysis plan as frozen before the
full-universe run: universe, bar constructions, walk-forward, corpus, the primary
endpoint, the pre-specified constants and the robustness sweep declared in advance. It
also lists what was added after the freeze and what was dropped from the plan.
`preregistration/LOCK_HASHES.md` carries its SHA-256 and the freeze timeline.

## Layout

```
phantombars/
  bars.py         naive (union) vs executable (TRADE-NB) OHLC + prevalence + decomposition
  cost.py         the cost model (half-spread + commission, round-trip)
  strategies.py   structural breakout/bracket families that trade against bar extremes
  wfo.py          rolling walk-forward, the two arms (select on naive vs clean; score on clean)
  fidelity.py     rank-IC, greedy de-duplication, effective-N block bootstrap
  synth.py        synthetic print generator (controlled ground truth, no data needed)
reproduce/        committed result artifacts, regeneration scripts, results inventory
preregistration/  locked analysis plan + lock hashes
tests/            structural, fidelity, and no-leak tests
examples/         end-to-end synthetic demonstration
```

## Method in one paragraph

`bars.build_bars` takes a print stream (price, size, exchange, sale-condition
bitmask, an at-NBBO flag, and a bar key) and returns, per interval, both the
**naive** bar (max/min over all prints) and the **executable** bar (max/min over
the at-or-inside-NBBO subset). The executable set is a subset of all prints, so the
naive high is weakly above the executable high and the naive low weakly below; the
phantom range inflation is therefore non-negative on every bar. Every filter uses
only print-time information, so the cleaning carries no look-ahead. The walk-forward
tunes each strategy's knobs in-sample on one bar set and always evaluates
out-of-sample on the executable bars, because a live order can only fill at an
executable price.

## Determinism

Seeds are fixed (`SEED = 12345`); the bootstrap replication count is fixed; figure
and headline outputs are pure functions of the committed artifacts. Every artifact is
digest-pinned in `reproduce/MANIFEST.sha256`, verifiable with `sha256sum -c`.

## Data availability

The results in the paper are computed on a licensed, professional-grade US equity
tape (tick-level trades with per-print sale-condition flags and a trade-at-NBBO
event). That data is obtained under provider terms and **cannot be redistributed**,
so it is not included in this repository and cannot be regenerated from this
repository alone. What is provided instead, so the work is reproducible by a reader
who does not hold the data:

* **Committed result artifacts** (`reproduce/`), including a per-strategy metrics table
  (`strategy_metrics.parquet`, one row per strategy) alongside the result JSONs. Every
  headline number, data table and data-driven figure in the paper regenerates from these;
  `reproduce/README.md` maps each one to its artifact. They contain aggregated statistics
  only, no raw prints.
* **A synthetic fixture** (`phantombars/synth.py`) that generates a controlled print
  stream with injectable phantom prints, so the full pipeline (bars -> walk-forward
  -> fidelity) runs end to end with no licensed data (`examples/run_synthetic.py`).

### Bringing your own data

`phantombars.bars.build_bars` is source-agnostic. Supply a `pandas.DataFrame` of
prints with the columns documented in `phantombars/bars.py`:

| column     | meaning |
|------------|---------|
| `price`    | trade price (> 0) |
| `size`     | share/contract quantity |
| `exchange` | reporting venue (`"D"`/`"FINRA"` for off-exchange/TRF) |
| `cond`     | sale-condition bitmask (0 = regular way; see `COND_*` constants) |
| `at_nbbo`  | True iff the print executed at or inside the prevailing NBBO |
| `interval` | the bar key (e.g. a minute timestamp) |

The `at_nbbo` flag is the executable (trade-at-NBBO) condition. If your vendor
supplies the NBBO at print time instead, set `at_nbbo = (bid <= price <= ask)`. It
must be a print-time quantity so the cleaning stays causal (no look-ahead). The
official OHLC published by the exchanges is **not** the same object: it drops odd
lots and condition-coded prints but retains regular-way off-exchange prints that
printed outside the NBBO. The executable bar here anchors to the NBBO and is strictly
tighter.

## Citation

If you use this code, please cite the paper. See [`LICENSE`](LICENSE) for terms.
