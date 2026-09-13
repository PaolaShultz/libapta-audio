# E2-N1 numerical correction protocol — 2026-09-13

Authorized by the current owner request to resume E2 diagnosis and implementation.
The 2026-09-12 E2 code, evaluator, protocol, report and repro scripts remain frozen.
This is a separately versioned offline correction, not a reclassification of E2.
No production C/API/default/VERSION, music, hardware, holdout or release changes;
no push authorization. The old handoff's pause and push instructions are superseded
by the current request. Fructal Cap Design Implement preserves the evidence and
acceptance constraints while removing the blocked continuation path.

## Evidence before correction

In isolated NumPy 2.5.2 / SciPy 1.18.1, OPENBLAS_NUM_THREADS=1, all five recorded
PCM hashes and KKT values reproduce exactly. Inputs are not mutated. Augmented
residual gradients and unaugmented Gram-plus-ridge gradients agree within 2e-16.
Diagnostic BVLS solves meet the original KKT gate. Compiling upstream SciPy
v1.18.1 `scipy/optimize/src/nnls.c` against the wheel's BLAS reproduces returned
coefficients exactly. A rejected prospective column retains the `dlarfgp`
Householder tail; only its pivot is restored. Saving/restoring the entire trial
segment on rejection removes all five failures (KKT <3e-16). An output-alias
change at `dlartgp` was tested diagnostically and changes none of the five.
This supports a specific solver workspace defect, not a checker/integration fix.

Source: https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/src/nnls.c

## Frozen N1 implementation and evaluation

Vendor the upstream kernel with its license and provenance, and apply only a
caller-owned scratch segment save/restore for rejected trial columns. Keep the
same algorithm, objective, column normalization, ridge 1e-3, maxiter=30*n,
active threshold 1e-10 and KKT <=1e-8. No retry/fallback or coefficient clipping.
Expose it through a separately named experimental Python instrument. Compile
only a host diagnostic shared object; leave installed SciPy untouched. Fail
closed if the explicit artifact is missing or solving fails.

Preserve all five complete numerical inputs and a deterministic deletion-reduced
case. Compare gradients by residual, Gram plus ridge, and extended precision;
compare BVLS as a diagnostic reference. Add deterministic analytic/boundary and
seeded numerical cases, including iteration failure, rejection and immutability.
Run the original 144-clip bank twice as regression evidence through the unchanged
E2 evaluator with only its instrument binding replaced. Verify all 1152 PCM hashes,
all comparator selections, replay identity and unchanged successful E2 solutions
within numerical tolerance. The existing native review probe is reused and hashed;
that is not a new native build or original three-binary identity claim.
Record pipeline CPU <=120 s, numeric workspace <=16 MiB, process RSS separately.
All existing scientific and confidence gates remain conjunctive.

## Attribution diagnosis before any candidate

Trace the two valid missing-family mode regressions (fixture tonic 2 and 4,
mode 0), all unequal cases, and numerically repaired failures. Record discovered
peaks, true-note candidate coverage within 20 cents, fitted contributions and
chroma, and native output. Evaluation-only supplied-note amplitudes and
known-support fits may isolate mechanisms; never feed labels into the detector.
Distinguish coverage loss, wrong harmonic allocation, squaring/normalization and
native profile response. Numerical correctness alone is not detector acceptance.
Only if a bounded attribution correction is supported, freeze its hypothesis,
implementation and fresh disjoint synthetic protocol before implementing it.
No open-ended sweeps or observed-bank acceptance claims.
