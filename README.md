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
redistributed (see [`DATA.md`](DATA.md)). This repository therefore ships:

* the **method**, source-agnostic and inspectable (`phantombars/`);
* a **synthetic fixture** so the whole pipeline runs with no licensed data
  (`phantombars/synth.py`, `examples/run_synthetic.py`);
* the **committed result artifacts** and a script that regenerates the paper's
  figures and headline for a reader who does not hold the data (`reproduce/`);
* a **test suite** including a pollute-and-verify no-leak check (`tests/`).

## Install

```bash
pip install -e .          # or: pip install -r requirements.txt
```

Python 3.9+; depends only on numpy, pandas, scipy, matplotlib, pytest.

## Reproduce the paper (no licensed data needed)

```bash
python reproduce/print_headline.py     # headline numbers from committed results.json
python reproduce/make_figures.py       # regenerates figures 2-6 into reproduce/figs/
```

Every headline number in the paper is reproducible from the committed
`reproduce/results.json` + `reproduce/prevalence_fixed.json`.

## Run the mechanism on synthetic data

```bash
python examples/run_synthetic.py
```

Generates a panel of synthetic symbols with injected phantom prints, builds naive
and executable bars, and runs the two-arm selection experiment. Selecting on clean
bars is more faithful to executable out-of-sample performance than selecting on
naive bars. Magnitudes are fixture-specific, not the paper's numbers.

## Tests

```bash
pytest -q
```

Covers Proposition 1 (the naive range weakly bounds the executable range, so the
inflation is sign-definite), the source decomposition, the fidelity metrics and
their determinism, and a **pollute-and-verify** test that injects a look-ahead
into the walk-forward and confirms it is detected.

## Layout

```
phantombars/
  bars.py         naive (union) vs executable (TRADE-NB) OHLC + prevalence + decomposition
  cost.py         the cost model (half-spread + commission, round-trip)
  strategies.py   structural breakout/bracket families that trade against bar extremes
  wfo.py          rolling walk-forward, the two arms (select on naive vs clean; score on clean)
  fidelity.py     rank-IC, greedy de-duplication, effective-N block bootstrap
  synth.py        synthetic print generator (controlled ground truth, no data needed)
reproduce/        committed result artifacts + figure/headline regeneration
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
and headline outputs are pure functions of the committed artifacts.

## Citation

If you use this code, please cite the paper. See [`DATA.md`](DATA.md) for data
access and [`LICENSE`](LICENSE) for terms.
