# Observable frequency-uncertainty screen C3 — 2026-09-12

**Rejected: 50/1024 perturbed cases pass the frozen combined gates.** The
analytic O1 model removes structural roundoff directions, but changes no family
selection or combined pass/fail outcome versus C2. All 32 nearest-Hz reversals
remain. Quarter-Hz conditions preserve all 768 correct family rankings while
all 768 fail the 10% reconstruction ceiling. No model abstains in this bank.

Protocol `5ea1fc5` preceded instrument
`7825f4119377562dd2fbe1458c12d14464119e21` and both runs. Baseline:
`360c0c460d03438dd237cb9d5101109ecc5a0d2b`. See the
[frozen protocol](APTA-1.1-KEY-OBSERVABLE-FREQUENCY-PROTOCOL.md) and
[complete public evidence](../../evidence/1.1/key-observable-frequency-c3-20260912.json).

## Fixed comparison

Only the model construction and fit wrapper change: C2's waveform-generated
columns are replaced by the unchanged O1 analytic model, structural-zero
omission and weak/empty/rank abstention rules. C1 normalization and the 1e-12
SVD cutoff remain. Signals, float rounding, phases, source amplitudes, retained
bins, frequency perturbations and scoring thresholds remain frozen.

All 1280 observation rows and 40 models complete. A row would abstain if either
hypothesis could not be fit, remain in the denominator and fail the combined
screen. This accounting is unit-tested, but no such row occurs here. Omitting
an invisible component is not itself whole-model abstention when visible,
independent columns remain. O1's independent bank still includes and validates
weak/empty abstentions.

| Frequency condition | Both gates pass /256 | Ranking reversals | Reconstruction failures | Max correct residual | Minimum margin |
|---|---:|---:|---:|---:|---:|
| Exact control | 256 | 0 | 0 | 3.308816e-16 | 0.105737189 |
| All -0.25 Hz | 0 | 0 | 256 | 0.192940447 | 0.018912000 |
| All +0.25 Hz | 0 | 0 | 256 | 0.201238009 | 0.055020119 |
| Independent +/-0.25 Hz | 0 | 0 | 256 | 0.201715036 | 0.026728010 |
| Nearest Hz | 50 | 32 | 206 | 0.355728960 | -0.061334748 |

There are no ties, unavailable reconstructions or abstentions. Of 1024
perturbed observations, 992 have the correct ranking and 974 fail the combined
screen. The 32 reversals overlap reconstruction failures; they all occur for
fixture 0's pure generating source. Both ranking and combined outcome comparisons
against C2 have zero fixes and zero breaks, and zero changed family selections.
Residuals do change numerically; outcome identity does not mean score identity.

## What the numerical correction establishes

Nearest-Hz known-family models omit 3, 3, 4 and 4 invisible components for
fixtures 0..3, leaving ranks 12, 12, 10 and 10. Their normalized condition
numbers are approximately 1. Physical coefficients for omitted sine/cosine
terms are null/unidentifiable: 1792 null entries across both fits of all rounded
rows, not 1792 independent components. Rounded fitted nonnull coefficients
now have maximum magnitude 0.09006746, compared with C2's approximately
2.679e11 from roundoff directions.

The same 32 reversals persist after this correction, so structural roundoff
normalization alone did not cause those family outcomes. This is a bounded
observation about these supplied-frequency models, not a proof of unavoidable
physical ambiguity or a music accuracy estimate. C2's historical limitation
and rejection remain unchanged.

The correction also does **not** make every physical amplitude estimate valid:

| Condition | Largest absolute physical coefficient across both fits |
|---|---:|
| Exact | 545.712399 (maximum in a correct-family fit: 0.09008422) |
| -0.25 Hz | 2137.956729 |
| +0.25 Hz | 592.001493 |
| Independent +/-0.25 Hz | 2373.221040 |
| Nearest Hz | 0.09006746 |

Noninteger out-of-range tones retain real leakage into the observed band.
An unconstrained fit can amplify that leakage and combine correlated columns;
O1's numerical floor does not impose a source amplitude model. Known-family
normalized condition numbers reach 3171.86. The large coefficients are reported
as a remaining physical interpretation limitation, without introducing an
amplitude cap, pruning rule or threshold rescue after observing the result.

## Instrument checks and reproducibility

- Original O1 numerical rows replay identically 24/24. Original C2 rows replay
  bit-for-bit 1280/1280, including nested C1 256, F2 256 and F1 eight controls.
- Every new row has identical source PCM hash, phase hashes and rounding metrics
  to C2. New exact-condition scores pass 256/256; largest absolute residual
  difference from C2 is 9.96577820266964e-13, below 1e-10.
- Every supplied analytic column is checked against independent time-domain
  synthesis and FFT before new family scoring. Maximum L2 error/6000 is
  3.7680947297074843e-13, below 1e-10; omitted columns are exactly zero.
- Every ready fit is checked with independent least squares; maximum prediction
  discrepancy is 4.476761307992839e-14, below 1e-10. This checks arithmetic,
  not physical source identifiability.
- Seven new accounting/integrity tests and 55 unchanged diagnostic tests pass.
  Eleven coverage tests pass against each reused default Release, I1 Release
  and sanitizer native probe. No new native build, full CTest suite, music
  evaluation or P4 qualification is claimed.
- Summary and detailed fit JSON repeat byte-identically; both stderr files are
  empty. Full control+screen CPU is 20.535456 seconds and 25.690073 on replay,
  below 120 seconds each. Maximum matrix+pseudoinverse is 512064 bytes, below
  1 MiB/model; this excludes interpreter/report storage and is not a P4 budget.
- WSL Ubuntu, NumPy 2.5.2, OPENBLAS_NUM_THREADS=1; instrument executes from a
  clean source archive. Public evidence includes source/input/artifact hashes,
  complete model/row/group metrics, timings and test counts. Local detailed
  coefficient arrays and run script are in `build/key-observable-frequency-20260912/`.

Reproduce from the instrument revision with this command (supply the original
synthetic coverage export whose hash is pinned in the public evidence):

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/apta_key_observable_frequency.py \
  --samples /path/to/key-coverage-default.bin \
  --witnesses evidence/1.1/key-identifiability-20260911.json \
  --f1-evidence evidence/1.1/key-within-cell-f1-20260911.json \
  --f2-evidence evidence/1.1/key-phase-f2-20260911.json \
  --c1-evidence evidence/1.1/key-coherent-c1-20260912.json \
  --c2-evidence evidence/1.1/key-frequency-uncertainty-c2-20260912.json \
  --o1-evidence evidence/1.1/key-observability-o1-20260912.json \
  --source-commit 7825f4119377562dd2fbe1458c12d14464119e21 \
  --output-prefix /tmp/apta-c3
```

## Next boundary

The numerical correction is insufficient to make fixed inaccurate frequencies
robust. Next define a separately preregistered, bounded local frequency
refinement instrument and validate it first on an independent analytic tone
bank. That design must explicitly address physically unconstrained amplitudes
and near-dependent components before interpreting source reconstructions; O1
alone is insufficient. No estimator, amplitude prior or search parameters are
selected by C3. Do not select them by optimizing the 32 observed reversals,
relax the reconstruction ceiling or open music to rescue these results.

Production sources, predecessor tools, API/confidence behavior and VERSION
have no changes. No candidate flags are enabled; production CPU/RAM/state delta
is zero and VERSION remains 1.0.1. No corpus/holdout was accessed. WP6/WP7 and
release gates remain closed. The unrelated untracked `output/` is excluded
from commits.
