# Two-tone noise/amplitude robustness R3 — frozen 2026-09-12

Baseline `948da5344c642e2a99d11acf72fbea90cf7e3cf9`. Freeze protocol before
implementation and instrument before evaluation. Test unchanged R2 search and
R1 fit; no search, floor, rank, amplitude-budget or objective changes. This
is a synthetic development screen, not confidence calibration or music transfer.

## Factorial source bank

New supports [277.31,659.47] and [523.17,523.77] Hz. Total tone amplitude 0.40.
Low/high-frequency amplitude ratios 1, 4 and 1/4, split as total*q/(1+q) and
total/(1+q). Two phase realizations per support. SHA256 ASCII
`apta-r3-phase-20260912|support|phase|component`, first eight bytes big-endian
/2^64 *2*pi. One seed-error vector [-0.31,+0.27] Hz for all cases. The 12 clean
waveforms each receive clean, 40 dB and 20 dB conditions, giving 36 searches.
This isolates noise with paired sources and amplitude ratio in a fixed factorial
bank; it does not expand phase coverage sufficiently for a population claim.

Synthesize tones at 48 kHz float64, absolute origin zero, as in C1. Generate
one reproducible noise vector per support/phase using SHAKE256 ASCII
`apta-r3-noise-20260912|support|phase`, 48000 little-endian uint32 values,
map each to (u+0.5)/2^32-0.5 and subtract its sample mean. This is deterministic
uniform pseudorandom noise, not a claim of Gaussian/recorded/colored noise.
Use the same vector across ratios and SNRs. Average-four float64 and project
to R1's retained 889-bin complex spectrum. Scale raw 48 kHz noise so the ratio
of clean retained-vector norm to noise retained-vector norm equals 10^(SNR/20).
Thus SNR is explicitly measured in the observed band, not broadband waveform
SNR or per-tone SNR. Add noise before float32 average-four; do not clip PCM.

Require float32/double observation relative and max absolute error <=1e-6,
noise scaling relative SNR-energy ratio error <=1e-12 in float64, and finite
nonzero observations. Publish clean/noise/observed hashes, scale, achieved
band SNR, rounding errors, sorted frequency and associated amplitude errors.
The fit/search receives only observed FFT and seed frequencies; source truth,
ratio, SNR and noise vectors must not steer it.

## Predeclared evaluation gates

For each row require a valid result and residual no worse than a valid seed fit
by >1e-12. A missing fit fails and remains in the denominator. Match estimated
amplitudes to true tones by sorting estimated frequency (not amplitude).

Clean rows retain R2 gates: max frequency error <=1e-4 Hz, max absolute tone
amplitude error <=1e-4, normalized squared residual <=1e-10. Noisy rows use
explicit diagnostic precision requirements: at 40 dB frequency error <=0.02 Hz
and max per-tone relative amplitude error <=0.10; at 20 dB <=0.10 Hz and <=0.50.
These tolerances are engineering screen definitions, not derived confidence
intervals or sufficient musical-key accuracy.

For noisy rows the residual ceiling is 1.10 * ||observed_vector-clean_double_vector||^2
/||observed_vector||^2 +1e-10. The known clean signal is a feasible reference;
the 10% allowance is a fixed diagnostic numerical/search margin. This ceiling
uses oracle noise knowledge for evaluation only and is NOT a deployable
quality/confidence rule. Do not reuse the clean 1e-10 residual criterion on noise.

All 36 combined rows must pass. Report each accuracy, amplitude and residual
gate separately, abstentions, and noisy-versus-paired-clean combined changes.
Also count residual-pass rows with inaccurate frequencies or amplitudes;
these demonstrate why fit quality alone is not accuracy. True-frequency fits
are separate oracle controls: report them without requiring noisy coefficient
accuracy. Complete this frozen matrix on scientific failure without rescue.

## Instrument and resources

Pin R2/R1/O1 tools and evidence. Replay R2's 32 recovery and six stress rows,
nested R1 48 rows and O1 24 rows identically. Import R1 column/least-squares
validation unchanged. New tests cover ratio assignment, source/noise hashes,
SNR scaling, paired noise identity, sorted amplitude association, threshold
boundaries and abstention accounting. Run all related unchanged tests and
coverage tests using existing native probes; no new full native/P4 claim.

At most 273 evaluations/search; per-model matrix+inverse <=1 MiB; complete
control+screen CPU <=300 seconds. Clean instrument archive, WSL NumPy float64,
OPENBLAS_NUM_THREADS=1. Run once plus deterministic summary/detail byte replay;
timing separate. Instrument gate failure stops; no model/threshold amendment
after results. Publish all 36 rows, condition/ratio/support groups, input/tool
hashes, noise provenance, test/resource and numerical limits.

No production flags/source/API/version changes; RAM/state/CPU delta zero.
No music/holdouts, no C3 family optimization, no unknown-count discovery claim.
Any change motivated by this screen requires a new separately frozen protocol.
