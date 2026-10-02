# Ephaptic Aβ-to-C-fiber crosstalk and multi-fiber spatial summation

Model, simulations and analysis for the study of whether action potentials in myelinated Aβ
afferents can excite an unmyelinated C-fiber through a shared, restricted extracellular
compartment.

**Author:** Mina Saied Attia Rizk (New Cairo STEM School, Cairo, Egypt)

This repository holds everything needed to reproduce and check the study: the model, the
experiment, figure and table scripts, the regression tests, and every simulation output behind
the figures, tables and quoted numbers.

## The model in one paragraph

A CRRSS Aβ axon (10 nodes, 1 mm apart) and a 1-µm C-fiber share an extracellular compartment of
cross-section *A*<sub>e</sub> = 16.4 µm² along a 5-mm focal lesion; outside the lesion the fibers
lie in grounded bulk fluid. *n* synchronously stimulated Aβ fibers (2 × threshold, applied outside
the lesion) load the compartment. Because *n* fibers sharing *A*<sub>e</sub> are equivalent to one
fiber in *A*<sub>e</sub>/*n*, *n* is also a statement about the extracellular cross-section per
fiber. The C-fiber has classical Hodgkin–Huxley kinetics (Phase 1) or a phenomenological
Nav1.8/Nav1.9 membrane (Phase 2); everything else is identical between the two. Intracellular and
extracellular potentials are advanced **together** by backward Euler in one banded solve
(Δz = 5 µm, Δt = 1 µs), and every endpoint is shown to converge under refinement.

## Reproduce

```bash
pip install -r requirements.txt

python run_all.py          # every experiment, figure and table (about 2-3 h on 4 cores)
python run_all.py --figures  # figures and tables only, from the stored results/data
python run_all.py --only e03 e05   # selected experiments, then figures and tables
python -m pytest -q        # regression and invariant tests (about 3 min)
```

`EPHAPTIC_WORKERS` sets the number of parallel processes. One experiment, `e08_jitter`, is faster
with a single process and `run_all.py` runs it that way: its matrix is large enough that each time
step streams the whole LU factor from memory, so extra workers only contend for bandwidth.

## Layout

```
src/ephaptic/          the model
  params.py            every parameter, as dataclasses: Abeta, C-fiber cable, HH, NavC,
                       compartment, protocol.  Nothing is defined anywhere else.
  kinetics.py          CRRSS, Hodgkin-Huxley and Nav1.8/Nav1.9 rate functions
  membranes.py         membrane objects (gates, conductances)
  model.py             the monolithic implicit solver, exact steady states, the Abeta
                       threshold, and the lagged scheme kept for comparison
  openloop.py          isolated C-fiber driven by a prescribed u_e (safety factor,
                       strength-duration curves)
  metrics.py           the endpoints (propagating C-fiber AP, depolarization, Abeta conduction)
src/experiments/       e01-e14, one script per experiment, each writing results/data/*.csv
src/figures/           one script per figure, reading results/data
src/build_tables.py    every table and every number quoted in the manuscript, from results/data
src/build_manifest.py  writes docs/MANIFEST.md
results/data/          all simulation outputs, each with a .meta.json recording the exact
                       parameter set of the run that produced it
results/figures/       Fig. 1-8 and Fig. S1-S3 at 300 dpi
results/tables/        the manuscript tables as markdown, and numbers.json: every quoted
                       number with the key the manuscript refers to it by
tests/                 regression and invariant tests
run_all.py             regenerates everything
```

## Checking a number in the paper

`docs/MANIFEST.md` maps every data file, figure, table and number to the script that produces it
and the raw output it reads. Each quoted number is in `results/tables/numbers.json` under a
readable key, computed from `results/data` by `src/build_tables.py`; nothing in the manuscript is
typed by hand. Each CSV's `.meta.json` records the parameter set of the run that wrote it.

## What the tests check

`tests/test_model.py` covers the parameter sets against the values stated in the manuscript, the
physical current balance of the compartment, the error of the lagged coupling scheme and the
time-step robustness of the monolithic one, agreement between the explicit and
conductance-implicit treatments of the ionic currents, the per-fiber cross-section scaling, the
exact resting state, and regeneration of stored results.

## License

MIT (`LICENSE`).
