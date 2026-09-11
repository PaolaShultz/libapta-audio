# Within-cell frequency structure F1 — frozen 2026-09-11

Baseline `31d3d9245a919d0db53a01abe6e9eaec8a068878`. Report-only diagnostic,
not a frontend, fitter, key selector or acceptance experiment. Commit protocol
and then instrument before execution. H1, production source, profiles,
confidence, version, corpus/holdout seals and all earlier rejections stay fixed.

## Fixed question and inputs

Do the existing one-second/12-kHz/1-Hz FFT power samples distinguish the eight
published <=6-column counterexample pairs (four distinct ideal spectra) after
discarding differences in each semitone cell's total energy? Use only those
eight IDs in `key-identifiability-20260911.json` and their exact exported float
PCM from the pinned 576-window coverage binary. No additional pitch, phase,
duration, window, zero-padding, gain or noise sweep.

The prior equality was in an ideal summed component-energy model. Do not assume
that actual finite-window spectra have equal cell totals. Measure and report
their coarse difference separately; within-cell normalization must remove this
difference from the fine-structure comparison.

## Fixed signal references

Construct two synthetic float64 time-domain references at 48 kHz, using the
same absolute sample-frame phase as the original C generator:

- Known-source reference: the three published missing-fundamental sources,
  h=2,3,4, amplitude 0.15/h, including their out-of-range partials just as the
  original C stimulus. Preserve source-note then harmonic summation order.
- Published alternative: the nonzero pure-tone coefficients from the exact
  counterexample, each at its nominal equal-tempered MIDI frequency with
  amplitude `2*sqrt(coefficient)/12000`. Sum in ascending MIDI order. These
  are fixed diagnostic reference phases, not fitted or phase-robust models.

Box-average each consecutive four samples in float64. Also independently
round the known-source 48-kHz sum to float32 and reproduce the ordered four
float32 additions/division. Compare that result with the actual exported C
samples: relative L2 <=1e-6 and maximum absolute discrepancy <=1e-6. This
checks reconstruction despite host transcendental-library differences; do not
assert bit identity or replace the actual C samples for the observation.

Apply the same rectangular rFFT without padding to actual C PCM, known-source
float64 and alternative float64 references. Retain only the original C3–B5
geometric semitone cells. No out-of-range FFT bin enters a score. Finite-window
leakage from out-of-range components can still enter this range; state this
limitation and do not attribute all separation solely to third-partial offsets.

## Fixed coarse and fine measurements

Report normalized L1 over the 36 integrated cell energies for actual versus
both references, and the relative cell-energy totals. For fine structure,
use only cells with positive ideal energy in that published witness. Normalize
the rFFT power samples within each such cell to unit sum. Compute the L1
distance between these within-cell distributions and average it with fixed
weights equal to the witness ideal cell energy divided by its ideal total.
All weights come from the already published example, not observed class labels
or a fitted detector. Require a positive finite power sum in every used cell.
This score is invariant to independent positive rescaling of cell totals.

Let Dtrue be this fine distance between actual C PCM and known-source float64,
and Dalt the fine distance to the published alternative. Support retention of
fine structure for these fixed references only if **all eight** satisfy
`Dalt > 100*Dtrue + 1e-9`. Otherwise record partial/absent support and do not
change the margin. Dtrue is a reconstruction/rounding reference discrepancy,
not a noise model, formal statistical confidence or a bound on unknown phases.

Record per-cell distributions, distances, peak-bin locations, ideal weights,
partial nominal frequencies and offsets from cell centers. Report each ID and
the number of distinct ideal spectra so repeated chords do not inflate evidence.
No native key reranking, candidate retention or real-song inference.

## Correctness, resource and stop gates

- Verify protocol/source, coverage export and published witness hashes. Use the
  unchanged coverage FFT checks (Parseval <=1e-12; direct sums <=1e-9 scaled).
- Exactly eight complete records, unique IDs in their published order, four
  distinct ideal spectra; finite waveforms, powers and scores in [0,2].
- Reconstruct both physical ideal cell vectors and verify their equality to
  the published spectrum within relative L2 1e-12 before waveform analysis.
- Test identical spectra, cell-gain invariance, changed within-cell shape,
  silence/invalid shapes, ordered float32 averaging and reference replay.
- Deterministic aggregate/detail replay; no overwritten output. Stop on
  correctness failure, preserving history and never relaxing tolerances.
- Single-thread full analysis process CPU <=30 seconds; report first-reference
  traced peak separately. Host-only allocation and runtime, zero production
  CPU/RAM/state change, no P4 feasibility claim.

End with exact source/input/output hashes, all eight measurements, interpretation
limits and one next boundary. Even complete support only justifies a separately
preregistered robustness check before selecting a new evidence representation.
Unknown phase/timbre/noise and the broader ambiguity of the dictionary remain
unresolved. No such sweep is executed here.
