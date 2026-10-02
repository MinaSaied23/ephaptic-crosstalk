<!-- Generated from docs/templates/README.tmpl.md by manuscript/build_manuscript.py; numbers come from results/data. Edit the template, not README.md. -->
# Ephaptic Aβ-to-C-fiber coupling in a focal nerve lesion

Code, data and manuscript for a closed-loop core-conductor study of whether action potentials in myelinated Aβ afferents can excite an unmyelinated C-fiber through a shared, restricted extracellular compartment.

**Author:** Mina Saied Attia Rizk (New Cairo STEM School, Cairo, Egypt)
**Status:** revision for the *Journal of Computational Neuroscience* after peer review. The model, the analysis and the manuscript were rebuilt: see [docs/RESPONSE_TO_REVIEWERS.md](docs/RESPONSE_TO_REVIEWERS.md) for the point-by-point reply, [CHANGELOG.md](CHANGELOG.md) for what changed and why, and [docs/MANIFEST.md](docs/MANIFEST.md) for the script and raw output behind every figure, table and number.

## Model in one paragraph

A CRRSS Aβ axon (10 nodes, 1 mm apart) and a 1-µm C-fiber share an extracellular compartment of cross-section *A*<sub>e</sub> = 16.4 µm² along a 5-mm focal lesion; outside the lesion the fibers lie in grounded bulk fluid. *n* synchronously stimulated Aβ fibers (2 × threshold, outside the lesion) load the compartment. Because *n* fibers sharing *A*<sub>e</sub> are equivalent to one fiber with *A*<sub>e</sub>/*n*, *n* is equivalently the extracellular cross-section per fiber (equivalent periaxonal gap *w*<sub>eq</sub>). The C-fiber has classical Hodgkin–Huxley kinetics (Phase 1) or a phenomenological Nav1.8/Nav1.9 membrane (Phase 2); everything else is identical between the two phases. Intracellular and extracellular potentials are advanced **together** (monolithic backward Euler, Δz = 5 µm, Δt = 1 µs), and every endpoint is shown to converge.

## Main results (production configuration)

| Quantity | Phase 2 (Nav1.8/1.9) | Phase 1 (HH) |
|---|---:|---:|
| Single-pair C-fiber depolarization | {{NavC_n1_dv2}} mV | {{HH_n1_dv2}} mV |
| *n* = 10 / 25 synchronous fibers | {{NavC_n10_dv}} / {{NavC_n25_dv}} mV | {{HH_n10_dv}} / {{HH_n25_dv}} mV |
| Largest depolarization (any *n*) | {{NavC_max_dv}} mV (*n* = {{NavC_max_dv_n}}) | {{HH_max_dv}} mV (*n* = {{HH_max_dv_n}}) |
| Aβ conduction through the lesion fails from | *n* = {{ab_fail_n}} (*w*<sub>eq</sub> ≈ {{ab_fail_weq}} nm) | same |
| Duration of the ephaptic depolarization (FWHM, *n* = 10) | {{fwhm_n10_us}} µs | – |
| Safety factor α\* (gain needed to fire), *n* = 25 | {{alpha_navc_n25}} | {{alpha_hh_n25}} |
| Attenuation by a 0.5-ms onset dispersion (*n* = 25) | {{jit_NavC_n25_att0p5}} % | {{jit_HH_n25_att0p5}} % |
| Propagating C-fiber AP | none | none |

- No C-fiber action potential occurred for *n* = 1–300, κ = 10⁶–10¹¹ m⁻², lesions of 1–7 mm, stimuli of 1.2–20 × threshold, 5-pulse trains at 50–400 Hz, or sensitizing bias currents up to the loss of resting stability.
- Faster gating alone (NavC τ<sub>m8</sub> down to 0.05 ms; HH up to 25 °C) changed the response by < {{kin_NavC_tau_m8_maxdev_pct}} %. APs appeared only when the whole Hodgkin–Huxley membrane was made faster (rates **and** conductances × ≥ {{kin_hh_speed_min}}, time constant at rest ≤ {{kin_hh_speed_min_tau}} ms) in a tight compartment; the Nav1.8/1.9 membrane never fired, at any speed, because its activation lies {{navc_m8_gap}} mV above rest.
- Version 1 reported a saturating multi-fiber response and a "−35 mV Nav1.8 threshold". Both were artifacts: of a lagged coupling scheme ({{lag_n25_dt2p5}} mV vs {{mono_n25_dt2p5}} mV converged at *n* = 25), of a 100-nA electrode inside the compartment, and of a threshold that was asserted rather than measured.

## Repository layout

```
src/ephaptic/          the model (single source of truth for all parameters)
  params.py            parameter dataclasses: Abeta, C-fiber cable, HH, NavC, compartment, protocol
  kinetics.py          CRRSS, HH and Nav1.8/1.9 rate functions
  membranes.py         membrane objects (gates, conductances)
  model.py             monolithic implicit solver, steady states, Abeta threshold, legacy lagged scheme
  openloop.py          isolated C-fiber driven by a prescribed u_e (safety factor, strength-duration)
  metrics.py           endpoints (propagating C-fiber AP, depolarization, Abeta conduction)
src/experiments/       e01-e13: one script per experiment, each writes results/data/eNN_*.csv (+ .meta.json)
src/figures/           one script per figure, reading results/data
src/build_tables.py    every manuscript table and quoted number, from results/data
results/data/          all simulation outputs
results/figures/       all figures (Fig. 1-8, S1-S2)
manuscript/sections/   manuscript sources (placeholders are filled from results at build time)
manuscript/            assembled manuscript (.md, .docx with native equations, .pdf preview), cover letter
tests/                 regression and invariant tests
run_all.py             regenerate everything
```

## Reproduce

```bash
pip install -r requirements.txt
python -m pytest -q                      # tests (~3 min; -m "not slow" for ~1 min)
python run_all.py                        # all experiments, figures and tables (~2-3 h on 4 cores)
python run_all.py --figures              # figures and tables only, from results/data
python manuscript/build_manuscript.py    # manuscript .md/.docx/.pdf, README, response letter
```

| Experiment | Script | Output | Manuscript |
|---|---|---|---|
| Positive controls | `e01_controls.py` | `e01_*.csv` | Fig. 3, Table 2 |
| Numerical verification | `e02_convergence.py`, `e02b_fast_variants.py` | `e02*.csv` | Fig. 2, Tables S1–S2 |
| Synchronous volleys | `e03_n_sweep.py` | `e03_n_sweep.csv` | Fig. 5, Table 3 |
| Per-fiber sleeve closure, scaling check | `e04_geometry.py` | `e04_geometry.csv`, `e04_mean_field.csv` | Fig. 5c |
| Extracellular leak κ | `e05_kappa.py` | `e05_kappa.csv` | Fig. 7a |
| C-fiber kinetics | `e06_kinetics.py` | `e06_kinetics.csv` | Fig. 7b |
| Strength–duration, safety factor | `e07_threshold.py` | `e07_*.csv` | Fig. 6, Table S5 |
| Temporal dispersion | `e08_jitter.py` | `e08_jitter*.csv` | Fig. 8a,b, Table S7 |
| Repetitive trains | `e09_trains.py` | `e09_trains.csv` | Fig. 8c |
| Sensitizing bias | `e10_bias.py` | `e10_*.csv` | Fig. 7c, Table S6 |
| Earlier full-length geometry | `e11_full_length.py` | `e11_full_length.csv` | Fig. S2, Table S8 |
| Lesion length, stimulus | `e12_lesion_stimulus.py` | `e12_lesion_stimulus.csv` | Fig. S3 |
| Waveforms for figures | `e13_waveforms.py` | `e13_waveforms.npz` | Figs. 3–4 |

## Citation

```bibtex
@unpublished{attiarizk2026ephaptic,
  title  = {Ephaptic A$\beta$-to-C-fiber crosstalk and multi-fiber spatial summation: a closed-loop core-conductor study with nociceptor-realistic channel kinetics},
  author = {Attia Rizk, Mina Saied},
  year   = {2026},
  note   = {Manuscript in preparation}
}
```

## License

MIT; see [LICENSE](LICENSE).
