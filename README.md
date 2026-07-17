# Ephaptic Aβ-to-C-Fiber Crosstalk: Simulation Code

This is the complete simulation and manuscript-generation codebase for the
closed-loop core-conductor study of ephaptic crosstalk between a myelinated
Aβ fiber and a C-fiber nociceptor, described in the accompanying paper
`ephaptic_crosstalk_paper_IEEE.docx`.

## Directory structure

```
requirements.txt              Python dependencies (numpy, scipy, matplotlib, Pillow)

phase1_classical_hh/          Phase 1: classical Hodgkin-Huxley C-fiber baseline
  ephaptic_model.py              Core constants, Aβ (CRRSS) kinetics, geometry, r_e(w_cleft)
  validate_single_fibers.py      IMEX cable solver; isolated Aβ / C-fiber validation
  coupled_model.py               Closed-loop two-fiber ephaptic model (classical HH C-fiber)
  experiment1_single_pulse.py    Cleft-width sweep, single A\u03b2 pulse (paper Sec. III-B)
  experiment_summation.py        Temporal summation sweep (paper Sec. III-E)
  positive_control.py            Direct C-fiber stimulation control (paper Sec. III-A)
  sensitization_bias_sweep.py    Bias-current sensitization sweep (paper Sec. III-C)
  sensitization_bias_sweep_plot.py   Plots the above
  artifact_timing_check.py       Stronger-coupling numerical-artifact timing check (Sec. III-F)

phase2_nav18_nav19/           Phase 2: Nav1.8/Nav1.9 nociceptor-realistic C-fiber
  ephaptic_model.py              (same as Phase 1 copy; Aβ side is unchanged across phases)
  validate_single_fibers.py      (same as Phase 1 copy)
  nav_kinetics.py                Nav1.8/Nav1.9 gating kinetics (paper Sec. II-E)
  tune_point.py                  Point-neuron rheobase tuning used to set conductance densities
  navc_cable.py                  Full-cable Nav1.8/1.9 C-fiber model + propagation validation
  coupled_navc_model.py          Closed-loop model with Phase-2 C-fiber, incl. multi-fiber
                                  bundle formulation (n_abeta parameter; paper Sec. II-F, III-I)

## How to run

### Python simulations (Phases 1 and 2)

```bash
pip install -r requirements.txt

cd phase1_classical_hh
python3 experiment1_single_pulse.py       # cleft-width sweep, classical HH C-fiber
python3 experiment_summation.py           # temporal summation sweep
python3 positive_control.py               # direct C-fiber stimulation control

cd ../phase2_nav18_nav19
python3 navc_cable.py                     # Nav1.8/1.9 rheobase + propagation validation
python3 -c "from coupled_navc_model import run_coupled_navc; \
            print(run_coupled_navc(w_cleft=200e-9, T=2e-3, n_abeta=1)['spiked'])"



## Study narrative (what each phase established)

1. **Phase 1 (classical HH C-fiber).** Single-pulse crosstalk, tonic sensitization
   (bias current and a uniform HH-kinetics voltage shift), and temporal summation were
   all tested across a 20 nm - 5 µm cleft-width range. None produced an ectopic C-fiber
   spike under physiologically-calibrated coupling. A stronger-coupling stress test
   produced apparent spikes that were identified as a numerical artifact (delayed onset,
   duration-dependent, geometry-independent), not genuine crosstalk.

2. **Phase 2 (Nav1.8/Nav1.9 C-fiber).** The classical Na⁺ conductance was replaced with
   literature-derived Nav1.8 (slow, depolarized activation/inactivation) and Nav1.9
   (persistent, hyperpolarized-activating) kinetics to address the objection that a
   classical-HH nociceptor model is simply the wrong biology. Getting continuous
   propagation required substantially higher Nav1.8 density than the classical model
   needed (slower kinetics reduce the safety factor for unmyelinated conduction).
   Single-pair crosstalk still failed under every condition, though sensitization behaved
   qualitatively differently (a genuine graded stable window before depolarization block,
   rather than classical HH's immediate bifurcation into spontaneous firing).

3. **Multi-fiber bundle.** The model was extended to n synchronously-active Aβ fibers
   sharing one extracellular compartment with a single C-fiber (by symmetry, one Aβ
   cable is simulated and its contribution to the shared field is scaled by n). An
   apparent positive result at n=5 was caught as the same numerical-artifact signature
   from Phase 1 and rejected. After re-calibrating the extracellular regularization
   constant and re-verifying with the same timing/duration/geometry-independence checks,
   spatial summation across up to n=25 verified-stable fibers produced a genuine,
   substantial depolarization trend (~8 mV) that no single-fiber-pair mechanism
   approached, without crossing threshold within the numerically trustworthy range.

Full quantitative results, all cited literature, and the complete discussion are in the
manuscript itself.

## Dependencies

- Python 3.10+, numpy, scipy, matplotlib, Pillow (see `requirements.txt`)
