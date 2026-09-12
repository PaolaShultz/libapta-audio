# Coherent frequency-uncertainty screen C2 — frozen 2026-09-12

Baseline `8ae4e4ec8a4b9c713ea69653fd2e6e98ab5bb7c6`. One synthetic sensitivity
screen on the frozen C1 observations. Commit protocol before instrument and
instrument before execution. No production/H1/F1/F2/C1 edits, music, frequency
search, fitted offsets, phase changes or post-result rescue.

## Fixed evidence and question

C1 passes 256/256 with exact supplied component frequencies. Hold all those
observations fixed: four fixtures, both source families, 32 phases each,
original float32 rounding and four-sample averaging. Change only the frequency
hypotheses supplied to the unchanged C1 fitter. This reuses observed synthetic
development data and is not a fresh generalization test.

Predeclare exactly these five conditions, in this order:

0. `exact`: unchanged frequencies; reproduce every original C1 score.
1. `minus-quarter-hz`: subtract 0.25 Hz from every hypothesis component.
2. `plus-quarter-hz`: add 0.25 Hz to every hypothesis component.
3. `independent-quarter-hz`: each component gets either -0.25 or +0.25 Hz.
   Hash ASCII `apta-c2-20260912|fixture|family|component`; the first digest
   byte's low bit selects plus when one, minus when zero. Publish hashes.
4. `nearest-hz`: round each frequency to `floor(f+0.5)` (positive-frequency
   nearest FFT-bin center, ties upward), a common coarse estimation model.

Offsets are applied to both correct and competing hypotheses, including
out-of-range components. Source waveforms/amplitudes/phases are never perturbed.
Keep source component order and preserve metadata only for evaluation. These
are finite error constructions at the existing 1-Hz FFT spacing, not an
exhaustive error bound, an estimator or a tunable magnitude sweep.

## Fit, score and frozen decision

Use C1's matrix builder, normalization, rcond=1e-12, pseudoinverse and complex
in-range squared residual unchanged. No rank/column/frequency rescue. Report
column norms, ranks, conditioning and coefficients, especially for rounded
out-of-range integer-frequency columns: their retained energy can approach
roundoff and normalization can expose numerical artifacts. Such cases do not
establish physical frequency information or usable amplitudes.

For every perturbed observation require both:

- wrong-family normalized squared residual > correct-family residual +1e-6;
- correct-family normalized squared residual <=0.10.

The second gate is a newly preregistered diagnostic 10% unexplained-energy
ceiling for imperfect frequency hypotheses, not the original exact C1 1e-10
reconstruction criterion or a music/noise acceptance limit. Preserve original
C1 checks on the exact condition separately. Report ranking failures separately
from residual-ceiling failures so a close correct ranking is not called a
classification error. All 1024 perturbed cases must pass to retain this fixed
construction for a later uncertainty-aware experiment. A single failure rejects
the claimed screen; record the complete frozen matrix once, do not reduce the
offsets, remove a condition or change the residual ceiling.

Report each condition/fixture/generating family: 32 observations, pass counts,
rank reversals, margin ties, reconstruction failures, median/max correct
residual, minimum margin and changed family verdict versus the exact baseline.
No native key reranking, confidence calibration or key-accuracy claim.

## Correctness and resources

- Pinned C1/F2/F1 evidence, coverage PCM, witnesses and imported source hashes.
  Replay all 256 original C1/F2-new-bank records, plus the old F2/F1 controls.
- Exactly 1280 observations (256 exact +1024 perturbed), 40 fitted matrices,
  five conditions, four fixtures, two families, 32 realizations each.
- New exact-condition coherent scores, phase hashes and source-rounding metrics
  must match C1 bit-for-bit. Every condition must use identical phase hashes and
  source observations for the matching fixture/family/realization.
- Inherit C1/coverage FFT checks, independent least-squares prediction check
  <=1e-10, finite coefficient/score and source-rounding gates unchanged.
- Tests: exact/no-mutation behavior, both quarter-Hz shifts, independent hash
  sign/replay, nearest-Hz ties, shifted-frequency fit mismatch, gate boundaries,
  fixed-phase reuse, invalid construction and exact C1 regression tests.
- Complete deterministic aggregate/detail replay, no overwritten outputs.
  Stop on instrument failure, preserving its history; never relax tolerances.
- Single-thread full process CPU <=120 seconds. Largest matrix+pseudoinverse
  <=1 MiB, as in C1. Record first perturbed-matrix traced peak separately;
  host-only cost, zero production CPU/RAM/state delta, no P4 feasibility claim.

Finish with source/input/protocol/output hashes, all gate results and one next
boundary. A pass is only finite sensitivity evidence; a failure motivates a
separately preregistered frequency-estimation question before a new fitter.
Neither outcome authorizes corpus/holdout access or a native detector port.
All prior rejections and release/P4 gates remain intact.
