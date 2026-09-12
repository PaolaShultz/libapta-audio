# Observable frequency-uncertainty screen C3 — frozen 2026-09-12

Baseline: `360c0c460d03438dd237cb9d5101109ecc5a0d2b`. Freeze this protocol
before implementation and the instrument before evaluation. C2 remains a
rejected historical screen; O1 is only numerical instrument evidence.

## Hypothesis and single changed axis

Replace only C2's coherent model builder/fitter with the unchanged O1 analytic
builder/fitter. This removes normalization of structural roundoff and makes
weak/empty/rank-deficient model abstentions explicit. Hypothesis: the resulting
frequency-error measurements are numerically interpretable under O1's bounded
observability checks. This does not assume frequency robustness will pass.

Use all 256 unchanged C1/C2 observations: four fixtures, two source families,
32 phases. Import C2's exact, -0.25 Hz, +0.25 Hz, independently signed 0.25 Hz,
and nearest-Hz supplied-frequency conditions unchanged. There are 1280 rows,
1024 perturbed rows and 40 models. No new signal, amplitude, phase, frequency
search, noise, frequency-error magnitude, prior or corpus access. This is
already observed synthetic development evidence, not independent transfer.

O1's structural-zero omission, null physical amplitudes, inclusive numerical
floor 6000*sqrt(float64 epsilon), rank veto and C1 SVD cutoff remain unchanged.
Do not change any predecessor source. No native candidate or production flags.

## Gates and abstention accounting

If either hypothesis abstains, the row has no selected family and no ranking
result; it fails the combined screen and stays in the denominator. Report
correct/alternative/both abstention counts and reasons separately. Never choose
the remaining ready model by default. A ready correct model may still report
its reconstruction status when the alternative abstains. An unavailable
reconstruction is null, not a measured reconstruction failure.

When both models are ready, preserve C2's gates: wrong residual > correct
residual +1e-6 AND correct normalized squared residual <=0.10 for perturbed
cases (<=1e-10 for exact control). Rank reversals, margin ties, measured
reconstruction failures, abstentions and combined failures are separate counts.
Require all 256 exact controls to pass; all 1024 perturbed cases must pass for
the finite screen to pass. Count fixes/breaks in ranking and combined verdict
against C2, including abstentions as nonpassing. These are family-fit outcomes,
not musical-key/confidence safety metrics. No confidence output exists here.

## Instrument validation and resources

Pin O1/C2 tools and their input/dependency hashes. Replay O1's full 24-case
numerical bank identically and all original C2 rows bit-for-bit, including its
nested C1/F2/F1 controls. Before new scoring, check every supplied raw O1 column
against independent time-domain sine/cosine -> box-average -> FFT: per-column
L2 error/6000 <=1e-10. Omitted columns must be exactly zero. This is a numerical
comparison; it does not establish physical amplitude identifiability.

Regenerate sources with the original phase function and generator. All PCM
hashes, phase hashes and rounding metrics must match C2 for every row.
For exact-frequency new fits, both residuals must differ from C2 by <=1e-10;
bit identity is not expected from an analytic construction. Verify each ready
fit with independent least squares at <=1e-10 prediction discrepancy. Report
physical coefficient maxima, null counts, ranks, normalized condition numbers
and active column norms; these do not prove global physical identifiability.

Run from a clean archive of the instrument revision, WSL/NumPy float64,
OPENBLAS_NUM_THREADS=1. Full control+screen process CPU <=120 seconds,
matrix+pseudoinverse <=1 MiB/model; report timings separately. Run once and
repeat; deterministic summary/detail JSON must match byte-for-byte. Run focused
new accounting tests and unchanged O1/C2/C1/F2/F1/identifiability/H1 tests plus
coverage tests with the reused native probes. No new native build or P4 claim.

On instrument gate failure, stop without changing the method or tolerances.
For scientific gates, complete the single frozen matrix and publish the failure
without adaptive follow-ups, fitted floors or threshold rescue. Publish all
rows/model metadata and aggregate changes, exact revisions/hashes/resources.
Production CPU/RAM/state delta is zero, VERSION remains 1.0.1, and private
corpora/holdouts stay closed. Any frequency estimator requires a later separate
protocol; this screen does not select or authorize a production frontend.
