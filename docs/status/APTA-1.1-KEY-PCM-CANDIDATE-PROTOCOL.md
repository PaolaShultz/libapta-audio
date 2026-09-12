# E1 offline PCM-to-key candidate — frozen 2026-09-12

Baseline `3245ecfdb87a4fe07b4ecc7c68e601088aa4d8a5`. Commit this design before
implementation and the instrument before bank execution. E1 is one complete
offline candidate, not S4 or a rescue of any rejected experiment. No production
C/API/state/VERSION changes. Python CLI is explicit opt-in; any later native
implementation requires its own disabled build option and measured contract.

## Hypothesis and fixed pipeline

Continuous spectral peak discovery before harmonic attribution may preserve
detuned fundamental evidence lost by fixed pitch-cell projection. H1 used 36
already-folded energies; this pipeline retains observed frequencies until after
attribution. No claim that this hypothesis explains all real-music errors.

Input only mono finite float PCM at 48 kHz, magnitude <=1. Process complete
nonoverlapping 48000-sample windows; report and ignore trailing partial samples.
Do not accept labels, true frequencies, seeds or component counts in extraction.
Use Hann window, 65536-point real FFT, local maxima from 65 through 4200 Hz;
retain at most 60 peaks at least 1% of the largest in-band magnitude. Refine
each peak by three-point log-magnitude parabola, clamped +/-0.5 bins, and retain
its bin magnitude. Sort ties by ascending frequency; no fitted tuning offset.

For each observed peak generate candidate fundamentals peak/h, h=1..4, within
65..1047 Hz. For each candidate match the nearest observed peak to each of its
first four harmonics, within 20 cents; require a fundamental match or at least
two matched upper harmonics. A peak can appear once per candidate. Fit the
nonnegative amplitude pattern 1/h to available magnitudes, capped so subtraction
cannot make any matched magnitude negative. Select the candidate with greatest
actual squared-residual reduction; ties prefer lower frequency. Subtract it
and regenerate candidates from the fixed peak frequencies with current residual
magnitudes, at most 12 selections, stopping once residual squared energy is
<=1% of original or no positive reduction exists. No S2 search on this path:
its oracle-seeded two-dimensional grid cannot satisfy this unknown-count design.

Deposit each selected amplitude squared into nearest MIDI pitch class, then
normalize each nonzero window's chroma to sum 1 and accumulate equally. Use
unchanged native C chroma selector for key, ranked candidates and confidence;
confidence is uncalibrated for this representation and must be evaluated, not
interpreted as probability. Silence yields unavailable. Diagnostic comparator
folds the same detected peak magnitudes squared directly with identical
normalization/selector. This comparator isolates attribution; it is NOT full
production PCM extraction. Real development later requires actual production
CLI comparison on identical PCM and independent transfer before native work.

## Frozen first pipeline screen

New synthetic bank: all 24 tonic/mode pairs, four conditions pure, full harmonic,
missing fundamental and detuned full harmonic. Eight one-second chords per clip:
root offsets [0,7,5,0,5,7,7,0], minor/major tonic and subdominant triads, dominant
always major. MIDI root 48+tonic+offset, intervals [0,third,7]; add root octave
below on odd windows (unknown count varies). Partials pure={1}, full={1,2,3,4},
missing={2,3,4}; amplitude per note/h is .12/(note_count*h). Detuned case uses
+.23 semitone on even windows, -.19 on odd. Per-component phase SHA256 ASCII
`apta-e1-20260912|tonic|mode|condition|window|note_index|h`, first 8 bytes big-endian
divided by 2^64 times 2*pi. Generate float64, round once to float32. Labels and
component construction are evaluator-only. No old waveform or music accessed.

All gates conjunctive: >=18/24 final exact keys in EACH condition, >=9/12 in
each mode/condition, zero final correct-to-incorrect breaks versus direct-peak
comparator, no new confidence>=75 errors versus that comparator, and <=5%
high-confidence errors overall. Report every final output, fixes/breaks,
unavailable results, selected-count range and confidence. These are synthetic
smoke gates only, not proof of transfer. On scientific failure record all rows
and stop E1; no threshold/harmonic/profile sweep or changed fixture rescue.

Extraction plus selector CPU <=60 seconds for 768 windows on single-thread WSL;
measure generator/test time separately. Explicit simultaneously-live numeric
arrays <=8 MiB/window by conservative accounting; report measured process peak
RSS including interpreter separately. This is offline host feasibility, not a
P4 budget. No unbounded cross-window buffers in extraction. CLI streams WAV
PCM16 mono/stereo (average stereo), checks 48 kHz, and returns no source paths.

Validation: malformed/nonfinite/rate rejection, silence, streaming/trailing
accounting, gain invariance, nonnegative residual and monotonic objective,
deterministic summary replay; unchanged default/candidate/sanitizer C selector
identity. Pin source and all imported helpers/native binary hashes. Source
archive at committed revision; two bank executions only, timing separate.

## Next gate if this passes

Freeze a disjoint development-music manifest and complete production comparison
before reading candidate results: exact key >=75%, each mode non-regressing,
zero new high-confidence errors, <=5% high-confidence errors, and measured
runtime/RAM limits. Audit available unspent development material first; absence
of suitable evidence blocks transfer, not permission to open formal holdouts.
WP6/WP7 final fresh >=48-track musician-labelled corpus, beat/downbeat work,
physical P4 and release freeze remain separate outstanding gates.
