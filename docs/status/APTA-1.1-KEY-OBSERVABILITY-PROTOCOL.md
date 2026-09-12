# Projected-tone numerical observability O1 — frozen 2026-09-12

Baseline: `cd57f1cd9b0ed81cd5a45412181b6c7de828e716`. This protocol precedes
implementation and evaluation. C1/C2 and their rejected/limited conclusions
remain immutable. This is a numerical instrument screen, not a family or key
accuracy experiment; no music, new phase bank, frequency estimation or native
production change is authorized by this screen.

## Hypothesis and construction

Analytic finite geometric sums can preserve structural zeros of a one-second
tone outside retained bins without normalizing waveform/FFT roundoff into fit
directions. Retain the C1 48 kHz origin, four-sample box average, 12,000 samples,
889 positive FFT bins (128..1016), and real/imaginary stacking.

For a complex source tone, box response is H(f)=mean(exp(i*2*pi*f*m/48000)),
m=0..3. Its bin k coefficient is H(f)*S(f-k), where
S(r)=sum(n=0..11999, exp(i*2*pi*r*n/12000)). Use the expm1 quotient with the
numerator argument reduced modulo one cycle. For exactly integral r, explicitly
return 12000 when r is a multiple of 12000, otherwise zero. Combine positive
and negative source frequencies into sine/cosine columns. Validate 0<f<6000.

Exactly integral frequencies outside 128..1016 have two structural zero
columns: omit their pair, report physical coefficients as null/unidentifiable,
never as inferred zero amplitude. No epsilon rounds frequencies to integers.
For all other pairs, if either column norm <=6000*sqrt(float64 epsilon),
abstain from the entire model. This conservative numerical guard is fixed from
precision and the 12000/2 unit-tone scale; it is not an audibility, noise or
physical amplitude bound. For retained pairs use C1 normalization and SVD cutoff
1e-12; abstain on rank deficiency as well. Empty support also abstains. No fit
may return a family score for an abstaining model. Large amplitudes in other
ill-conditioned models are not ruled out by this guard.

## Independent analytic bank and gates

Evaluate single frequencies 0.5, 127, 128, 440, 1016, 1017, 2048, 5999 Hz;
plus 127 and 1017 Hz each offset by both signs of 2^-4, 2^-16, 2^-28, 2^-40 Hz
(24 cases total). These are chosen from transform boundaries and binary
precision, independently of the C2 family verdicts. Compare analytic raw columns
with an independently synthesized float64 sine/cosine -> average-four -> FFT
path; L2 discrepancy/6000 must be <=1e-10 per column. Exactly invisible grid
cases must be bitwise zero analytically. Exact visible grid cases must have
only their expected bin and the box-response coefficient within 1e-10 scaled
error. Near-grid tones must never be tagged structural zeros.

For each ready model fit independently synthesized sin+0.5*cos PCM. Require
normalized squared residual <=1e-10 and independent least-squares prediction
discrepancy <=1e-10. Report fitted amplitude error, but make no universal
amplitude-recovery claim near the floor. Weak cases must abstain. Unit tests
also cover mixed visible/invisible support, all-invisible support, duplicate
frequency rank deficiency, invalid inputs, exact and near-integer geometric
sums, finite output and the inclusive floor boundary.

All gates are conjunctive; on instrument failure stop without changing formula,
floor, bank or tolerances to rescue it. Report the failure under this protocol.
Preserve old sources and run the relevant C1/C2 and predecessor Python tests.
No new native code implies no new native build/physical qualification claim.
Do not compute revised C2 family verdicts during O1.

## Resources and reproducibility

Freeze instrument commit before evaluating the bank in a clean WSL source
archive, NumPy float64, OPENBLAS_NUM_THREADS=1. CPU <=30 seconds for the bank,
matrix+pseudoinverse <=1 MiB per model. Production RAM/state/CPU delta is zero.
Run once and repeat for byte-identical deterministic JSON; timing is separate.
Publish tool/dependency hashes, exact instrument revision, complete 24-case
numerical/abstention metrics, tests and resource results. Retain a bounded
follow-up decision: only if O1 passes, separately preregister reevaluation of
frequency uncertainty using the new instrument; no automatic C2 rescue or port.
