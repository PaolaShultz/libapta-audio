# E2 researched joint PCM candidate — 2026-09-12

**Rejected implementation/screen; no transfer or production promotion.** E2
returns 126/144 exact keys versus direct peaks 130/144: three fixes, seven
breaks, zero high-confidence errors. Five breaks are numerical abstentions;
two remain on clips whose numerical gates pass. A failed instrument gate means
these counts are observations of this implementation, not a clean test of the
entire joint-attribution hypothesis.

Design/research protocol `2a02d2a` preceded instrument
`3ca838a87d0c044e987d06125bc1a5e1efd27aa6` and all matrix executions. See the
[protocol and research rationale](APTA-1.1-KEY-JOINT-PCM-PROTOCOL.md) and
[public result](../../evidence/1.1/key-joint-pcm-e2-20260912.json).

## Design implemented

Klapuri's [joint-estimation discussion](https://archives.ismir.net/ismir2006/paper/000125.pdf)
motivated evaluating multiple fundamentals together to avoid irreversible
detection-order cancellation. E2 implements its own regularized nonnegative
least-squares objective, using the documented
[SciPy NNLS interface](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html).
It does not reproduce Klapuri's objective, whitening or learned parameters.

Unchanged E1 peak discovery feeds a bounded candidate shortlist and pure/full/
missing-fundamental columns. A joint fit assigns overlapping evidence while
penalizing predicted-but-undetected partials in shared absent-peak rows. All
fitted contributions reach unchanged per-window chroma normalization and native
selection. Positive ridge ensures a unique regularized optimum, not unique
physical fundamentals. The zero targets represent censored peaks, not physical
silence. Fixed spectral envelopes and shortlist coverage remain assumptions.
The implementation does not modify E1 or invoke S2's oracle-seeded search.

## Frozen complete pipeline results

| New family | Major | Minor | Combined |
| --- | --- | --- | --- |
| Pure | 12/12 | 12/12 | 24/24 |
| Full harmonics | 12/12 | 12/12 | 24/24 |
| Missing fundamental | 7/12 | 10/12 | 17/24 |
| Detuned | 12/12 | 11/12 | 23/24 |
| Unequal note amplitudes | 2/12 | 12/12 | 14/24 |
| Steep harmonic decay | 12/12 | 12/12 | 24/24 |

Per-family >=18/24 and per-mode >=9/12 fail for missing and unequal families.
The zero-break gate fails. Confidence gates pass: zero high-confidence errors
and no new ones. Five unavailable clips (3.47%) pass the <=5% availability gate,
but cannot override the mandatory numerical gate. These 144 clips are distinct
from E1's 96; counts must not be compared as same-signal fixes versus E1.
The direct-peak comparator is not the production PCM extractor.

## Numerical failure preserved

Five of 1152 windows fail the projected KKT <=1e-8 gate. Exact same-input,
same-argument inspection (no solver substitution, clipping, iteration increase
or output rescue) gives KKT residuals 1.538732e-5, 1.261330e-5, 4.075896e-2,
5.159003e-7 and 1.514960e-7. All coefficients are finite/nonnegative and all
objectives improve on zero, so the independent optimality check is material.
The cause inside the solver is not established; do not call this confirmed
SciPy defect or floating-point roundoff. The largest residual is substantial.

Four affected windows are in missing-fundamental clips, one in detuned. Each
invalidates its entire clip as frozen. `max_kkt` in the original report covers
accepted solves only (5.053466e-16); the attached `failure_inspection` records
the rejected values explicitly. Both full executions produce identical reports,
including these failures. No clean algorithmic acceptance claim is possible.

## Verification and resources

Four new joint-model tests and four unchanged E1 tests pass. They cover invalid
and silent input, missing/full model distinction, overlap, order/gain invariance,
KKT rejection and simulated solver failure, plus inherited PCM/WAV boundaries.
Eleven coverage tests pass on each reused default, candidate and sanitizer probe;
all 288 final candidate/comparator selector requests agree across the three.
CLI silence smoke reports unavailable, one processed window and 17 trailing
samples. Full deterministic report replay passes; both stderr streams are empty.
No full native rebuild or physical P4 test is claimed.

Pipeline CPU is 5.558624 seconds (repeat 5.465741), under 120 seconds, including
one native selector pass and excluding generator/import time and verification
probe repeats. Conservative numeric workspace bound is 13027872 bytes under
16 MiB; process peak RSS including interpreter/libraries is 86908/85992 KiB.
SciPy 1.18.1, NumPy 2.5.2, WSL Ubuntu, OPENBLAS_NUM_THREADS=1. Host results do
not establish embedded timing or total memory. Public evidence pins source,
probes, archive and local scripts/logs under `build/key-joint-e2-20260912/`.

The implemented CLI is `tools/apta_key_joint_pcm.py --experimental-e2 --wav
INPUT.wav --probe NATIVE_PROBE`, supporting PCM16 48 kHz mono/stereo streaming.
It remains rejected/experimental, with uncalibrated native confidence for its
representation. Production/API/flags/VERSION stay unchanged; production resource
delta zero. No music, formal holdout, fresh acceptance corpus or device accessed.

## Decision and handoff

Stop E2 unchanged. Do not increase solver iterations, relax KKT, switch solvers,
change priors or retune the observed bank to turn this run into acceptance.
Before this architecture can be reconsidered, solver optimality must be resolved
in a separately justified implementation correction and the remaining attribution
regressions addressed with independent evidence. Neither task is completed here.
Even perfect solver output would not by itself close the two numerically valid
breaks or prove performance on music. No automatic follow-up experiment is queued.
Key transfer, beat/downbeat transfer, final fresh acceptance, physical P4 and
release freeze remain open.
