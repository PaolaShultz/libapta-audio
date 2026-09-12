# E2 joint PCM candidate — frozen 2026-09-12

Baseline `66a7c5f134b1bc31f81c0a953ef2ee0dec876b11`. User requested considered
design/research before implementation. Apply libapta-dsp-development discipline:
commit protocol before code, code before new bank; no production/API/version
change, no old-waveform rescue, no parameter sweep after outcomes.

## Design review and evidence

E1 selects a model, subtracts it irreversibly, and caps its coefficient by the
smallest matched partial. Missing harmonics are omitted from that model rather
than represented explicitly; overlapping peaks influence later selections.
Its 11 new errors are confirmed, but no unique causal decomposition of those
errors or real-music errors has been established.

Klapuri (ISMIR 2006), sections 2.4–2.5, discusses cancellation versus joint
estimation and the detection-order/cost tradeoff:
https://archives.ismir.net/ismir2006/paper/000125.pdf
This motivates joint estimation, not copying that paper's objective or learned
parameters. E2 is an independently specified regularized NNLS surrogate, not a
Klapuri reproduction. SciPy documents NNLS and active-set/KKT solution:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html
Installed SciPy 1.18.1 is offline-only; no new embedded dependency.

Reject a larger beam of E1 greedy paths: it keeps the same clipped model and
adds combinatorial cost. Defer learned instrument dictionaries/temporal models:
they require independent training evidence currently outside this bounded step.
Keep E1 peak discovery, window normalization, accumulation and native selector
unchanged to isolate joint attribution. S2 remains a numerical reference only.

## Frozen joint model

Input E1's <=60 frequency/magnitude peaks. Normalize magnitudes to L2 norm 1
for fitting. Form peak/h candidates, h=1..4, range 65..1047 Hz. Rank each by
sum of matched magnitudes/h within 20 cents, ties ascending frequency. Greedily
retain candidates at least 20 cents apart, at most 60; sort retained frequencies.
This is bounded data-derived shortlisting, not a proof every true F0 survives.

For each retained frequency make three columns: pure {1}, full {1,2,3,4}, and
missing {2,3,4}, with amplitude weights 1/h. Match nearest observed peak within
20 cents. For an unmatched predicted partial use a shared absent-peak row keyed
by round(60*log2(f/65)), target zero. Shared rows avoid per-column duplicate
penalties for the same absent-frequency bin. These zeros are a censored-peak
surrogate, not proof of physical silence; peaks below E1's threshold are lost.
At most 60 observed+240 absent rows and 180 columns. Normalize columns to L2=1.

Solve min(x>=0) ||Ax-b||² + 1e-3||x||² by augmenting A with sqrt(1e-3)I and
SciPy nnls(maxiter=30*n). Positive ridge supplies a unique regularized solution,
not unique physical fundamentals; it is a fixed modelling prior, not tuned
confidence. Keep all fitted contributions, recovering physical coefficient
x/column_norm, sum three types per fundamental, square that sum into E1 chroma.
No irreversible harmonic subtraction, hard source-count oracle or confidence
rewrite. Native confidence remains uncalibrated for this new representation.

Require nonnegative finite coefficients, objective <= zero-solution objective
+1e-10, and scaled projected KKT residual <=1e-8: max absolute gradient on
x>1e-10, max negative gradient on the remainder, scaled by max(1,||A'b||inf).
RuntimeError/nonconvergence yields unavailable for the whole clip and fails
the instrument gate; do not silently substitute E1/direct peaks. Log residual,
objective, KKT, shortlisted frequencies and coefficients for auditing. Bound
numeric workspace conservatively <=16 MiB; report process peak RSS separately.
Single-thread WSL pipeline CPU <=120 s for this bank, including NNLS and one
native candidate/comparator selection, excluding fixture generation/replay.
No P4 feasibility claim. CLI streams PCM16 48 kHz via explicit --experimental-e2.

## Fresh complete pipeline bank and stop

144 eight-window clips: 24 keys times six families pure/full/missing/detuned/
unequal/steep. New root progression [0,5,0,7,5,0,7,0], root MIDI 47+tonic
+offset (expected tonic is (tonic+11)%12). Tonic/subdominant mode as label,
dominant major; triads [0,third,7], add root octave below in windows 2 and 5.
Full partials 1..4, missing 2..4, pure 1 only. Default amplitude .12/(count*h).
Unequal weights per note [1,.5,.25,.75] normalized to sum1 times .12/h;
steep uses .12/(count*h^1.7). Detuned shifts +.17 semitone even windows, -.27
odd; all others nominal. SHA256 phase domain
`apta-e2-20260912|tonic|mode|family|window|note_index|h`, first 8 bytes big-endian
/2^64*2*pi. Float64 synthesis, one float32 rounding. No E1 bank is rerun/tuned.

Compare E2 and direct-peak folding on these identical new signals with the
unchanged native selector. All scientific gates conjunctive: >=18/24 each
family, >=9/12 each family/mode, zero correct-to-incorrect breaks, zero new
confidence>=75 errors, <=5% high-confidence errors overall, <=5% unavailable.
All numerical/resource gates also mandatory. No production-comparator claim:
actual production CLI/music transfer remains a subsequent separately frozen
step ONLY on pass. On any failure record all 144 rows and stop E2 unchanged.

Tests: silence/malformed inputs, full/missing isolated models, simultaneous
overlap, input-order invariance, gain invariance, projected KKT checks including
rejection, empty candidates, clipping/rate/trailing handling via inherited tests.
Pin helper/source/probe hashes, default/candidate/sanitizer selector identity,
clean archive, full deterministic report replay once, timing separate. No old
instrument edits, formal holdout access, new acceptance corpus or release claim.
