# Tonal coverage diagnostic — frozen 2026-09-10

Baseline `c81ab373bc554ed1df58d548aeb8377bcaf629f6`. This is step 1 only:
a synthetic, report-only diagnosis. No detector, corpus, holdout, production
source, public API, confidence formula or release metadata is changed.

## Questions and fixed matrix

The earlier double-Fourier reference at the same 36 frequencies changed no
native verdict. This experiment separates frequency coverage from compression,
octave folding, cumulative aggregation and native profile ranking.

Reuse the actual C float PCM from `tests/bench/key_mode_diagnostic.c`, all
24 tonic/mode stimuli and the same four-chord I-IV-V-I progression, at 48 kHz.
Preserve the first three conditions exactly (clean, +1/3 semitone, fixed noise).
In the new explicit-only target add exactly three conditions:

3. -1/3 semitone, otherwise clean;
4. clean fundamentals plus harmonics h=2,3,4 with each component amplitude
   0.15/h, in addition to each note's existing 0.15 fundamental;
5. the same harmonics h=2,3,4 without the fundamental.

Phases use the existing absolute sample frame for every component. No gains,
windows, noise strengths, probe counts or harmonic weights are swept. This
gives 144 progressions, 576 one-second windows and 1,296 native rows (144
ideal-vector rows plus 1,152 PCM window/cumulative rows). The first three
conditions must reproduce all 720 previous rows in each build exactly.

Export the exact float four-sample averages consumed by the native resonators,
plus the native float coefficients. One record contains tonic/mode/condition/
window uint32 values, 36 coefficients and 12,000 float samples. Format is
little-endian IEEE binary32 with magic APTCOV01; refuse unsupported hosts or
overwrite. Require 576 records and 27,648,000 source samples per run.
Export default and I1 separately; sample/coefficient binaries must be identical.

## Fixed reference representations

Use NumPy float64 rFFT on each exported 12,000-sample window: rectangular,
no zero padding, one-Hz spacing at the effective 12 kHz rate. Integrate squared
FFT magnitudes over 36 non-overlapping cells whose geometric edges are MIDI
47.5 through 83.5 (C3 through B5 centres). No per-cell width correction,
harmonic weighting, tuning estimation or out-of-range folding is allowed.
The integral has a different bandwidth/noise response from point sampling;
it is a diagnostic counterfactual, not a proposed production frontend.

Compare three 36-bin evidence sources:

- actual native narrow-probe raw energies from the existing observer;
- dense one-Hz FFT cell energy;
- ideal component-energy oracle, built only from the known C stimulus notes,
  harmonics and amplitudes within the same 36-cell range, including the
  four-sample box-average amplitude response. For each component use
  (12000*A*response/2)^2 in its cell. This ideal oracle ignores finite-window
  cross terms/leakage, float rounding and noise; it is not an exact DFT target.

Also form a fundamental-only pitch-class oracle (three equal note weights,
even in the missing-fundamental condition). It describes intended chord
membership rather than observed spectral energy. Do not subtract harmonics
or infer labels from a detector.

For each spectral source apply both existing transforms separately:
logf(1+E), and the exact frozen float window-mean normalization then logf.
Preserve native float bin-by-bin accumulation order. Use the same host libm
logf and require reconstructed native default/I1 cumulative chroma bit identity.
Feed reference chroma through the actual unchanged C selector, not a Python
reimplementation of confidence/ranking. Report top three keys/scores and
confidence for each local window and final progression. Local IV/V windows
are compared with their local chord, not the progression's global key.

## Fixed measurements and interpretation

Record per-condition and per-mode final matches, local-chord matches, tonic
versus mode errors, changed verdicts, fixes/breaks and new confidence>=75
stimulus mismatches versus narrow evidence under the same compression.
Record normalized 36-bin L1 distance to ideal component energy, energy-capture
ratio to that oracle, and fraction of known component energy inside the range.
Compare first-window and final results to expose aggregation effects. Keep
the oracle and dense references separate: perfect component knowledge is
not achievable extraction, and a matching chord is not real-song key truth.

Support a coverage contribution only if dense cell evidence has lower median
normalized L1 distance to the component oracle for both +/-1/3 conditions.
Decision/ confidence improvements or regressions remain descriptive; no
reference is retained as a detector from this experiment. If better energy
coverage still fails chord/key decisions or increases confident errors, record
that limitation rather than selecting a threshold/profile/window rescue.

## Instrument correctness and stop gates

- rFFT Parseval relative discrepancy <=1e-12 per window; selected integer-bin
  complex coefficients checked against independent direct sine/cosine sums
  (bins 131,220,440), error <=1e-9*max(1,coefficient magnitude).
- Analytic silence, impulse and an integer-bin tone validate FFT/cell mapping;
  test exact cell boundaries and out-of-range exclusion. Reject malformed,
  truncated, nonfinite, reordered or incomplete exported inputs.
- All old 720 rows per build unchanged, all new runs replay identically,
  I1 ASan/UBSan export/report equal Release, and every selector result obtained
  from the unchanged native function. All 576 narrow cumulative vectors per
  build must reconstruct bit-identically before interpreting reference results.
- Default and I1 analyzer/key-object hashes unchanged. Relevant Release/Werror
  diagnostic builds, I1 sanitizer runs and host parser/scoring tests pass.
- Production CPU/RAM/state delta is zero. The host export buffer and FFT work
  are diagnostic costs, with no P4 feasibility or algorithm acceptance claim.

Any instrument, provenance or identity failure stops interpretation until
correctness is restored; preserve failures and do not relax limits. Commit
protocol and instrument before executing the matrix. Record source/tool/build/
input/report hashes and exact commands. End with a causal scope statement and
one justified next research boundary, without opening any music corpus.
