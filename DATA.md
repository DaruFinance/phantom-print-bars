# Data availability

The results in the paper are computed on a licensed, professional-grade US equity
tape (tick-level trades with per-print sale-condition flags and a trade-at-NBBO
event). That data is obtained under provider terms and **cannot be
redistributed**, so it is not included in this repository and cannot be
regenerated from this repository alone.

What is provided instead, so the work is reproducible by a reader who does not
hold the data:

* **Committed result artifacts** (`reproduce/results.json`,
  `reproduce/prevalence_fixed.json`, `reproduce/fig_scatter.json`,
  `reproduce/fig3_equity.json`). Every headline number and every data-driven
  figure in the paper regenerates from these with `reproduce/print_headline.py`
  and `reproduce/make_figures.py`. They contain aggregated statistics only, no
  raw prints.
* **A synthetic fixture** (`phantombars/synth.py`) that generates a controlled
  print stream with injectable phantom prints, so the full pipeline
  (bars -> walk-forward -> fidelity) runs end to end with no licensed data
  (`examples/run_synthetic.py`).

## Bringing your own data

`phantombars.bars.build_bars` is source-agnostic. Supply a `pandas.DataFrame` of
prints with the columns documented in `phantombars/bars.py`:

| column   | meaning |
|----------|---------|
| `price`  | trade price (> 0) |
| `size`   | share/contract quantity |
| `exchange` | reporting venue (`"D"`/`"FINRA"` for off-exchange/TRF) |
| `cond`   | sale-condition bitmask (0 = regular way; see `COND_*` constants) |
| `at_nbbo`| True iff the print executed at or inside the prevailing NBBO |
| `interval` | the bar key (e.g. a minute timestamp) |

The `at_nbbo` flag is the executable (trade-at-NBBO) condition. If your vendor
supplies the NBBO at print time instead, set `at_nbbo = (bid <= price <= ask)`.
It must be a print-time quantity so the cleaning stays causal (no look-ahead).

The official OHLC published by the exchanges is **not** the same object: it drops
odd lots and condition-coded prints but retains regular-way off-exchange prints
that printed outside the NBBO. The executable bar here anchors to the NBBO and is
strictly tighter.
