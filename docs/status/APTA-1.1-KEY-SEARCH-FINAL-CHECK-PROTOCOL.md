# Final search checkpoint S3 — frozen 2026-09-12

Baseline `13b779ab1f492f4b7e765983cf1399ee8ad07ae8`. This is experiment TWO
and LAST in the authorized search checkpoint. S2 has passed 16/16. No S2,
R1, R2, R3 or S1 source changes; after this result make a direction decision.

Use unchanged S2 search with <=2049 evaluations and explicit termination;
unchanged R1 fit and its synthetic amplitude/rank/observability rules. Compare
unchanged R2 search on the same new observations as a diagnostic baseline.
No changed-search replay of the failed R3 signals and no tuned parameters.

## New paired bank and frozen criteria

Supports [349.23,830.41] and [622.17,622.87] Hz, total amplitude .40, low/high
ratios 1,4,1/4 and two phases. Seeds [-.31,+.27] Hz. Clean/40 dB/20 dB observed
band SNR conditions produce 36 searches on 12 underlying tone waveforms.
Phases SHA256 ASCII `apta-s3-phase-20260912|support|phase|component`, first
eight bytes big-endian/2^64 *2*pi. Noise SHAKE256 ASCII
`apta-s3-noise-20260912|support|phase`, 48000 little-endian uint32 values mapped
to (u+.5)/2^32-.5 then demeaned. Noise and phase seeds are new and do not
reuse R3. Share raw noise across ratios/levels for paired comparisons.

Use R3's declared construction: 48 kHz float64 tones/noise, scale noise by
retained-band vector norm to requested SNR, then float32 average-four. Retain
R3's 1e-12 relative noise energy scaling and 1e-6 relative/absolute rounding
gates. SNR is observed-band aggregate, not per-tone, Gaussian or recorded noise.
Reuse R3's amplitude-ratio helper and SNR scaler; implement new seed domains
without changing old generator sources.

S2 must return poll_resolved AND pass R3's frozen condition-specific accuracy
and residual criteria in all 36 cases: clean <=1e-4 Hz, absolute amplitude
<=1e-4, residual <=1e-10; 40 dB <=.02 Hz, relative amplitude <=.10; 20 dB
<=.10 Hz, relative amplitude <=.50. Noisy residual ceiling remains
1.10*||observed-clean_double||^2/||observed||^2+1e-10. It uses oracle noise
only for evaluation and is not deployable confidence. Require no regression
against valid seed fit >1e-12. Sort amplitudes together with frequency.
True-frequency oracle fits are reported separately. Exhaustion/no-valid-grid
are failed rows with best-so-far retained for diagnostic accuracy only.

Report accuracy, termination, amplitude and residual failures separately;
R2-vs-S2 fixes/breaks use identical condition-specific gates on each signal.
Paired clean/noisy pass changes must not be called same-threshold accuracy
improvements. Record residual-pass-but-inaccurate cases and search cost.

All gates conjunctive. Scientific failure completes the single bank; no
surrogate/search/SNR/threshold rescue or third experiment. On pass, retain S2
only as a bounded numerical reference for a future complete key candidate.
On failure, stop optimizing this search track and change approach. Either way,
write a concrete checkpoint decision connecting the result to end-to-end key
development, unknown-component/seed discovery and native cost, not another
chain of local-search microexperiments.

## Verification and limits

Pin S2 dependencies and R3 helpers. Replay all S2 eight known quadratic outputs
identically and O1's 24 rows identically. Full S2 tone replay is already retained
in its result and is not repeated here. Run new seed/termination/comparison
tests, all unchanged related tests and existing three native probes. Every
new fit inherits R1's independent FFT/prediction gates. No full native/P4 claim.

Clean instrument archive, WSL NumPy float64, OPENBLAS_NUM_THREADS=1; one run
plus deterministic summary/detail byte replay, timing separate. Full bank
and controls CPU <=300 seconds each run; model matrix+inverse <=1 MiB,
S2 <=2049 evaluations/search. Report cost excluding interpreter/trace storage.
No production/corpus/holdout/API/VERSION changes or release claim.
