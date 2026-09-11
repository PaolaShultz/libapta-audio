# Within-cell phase screen F2 — frozen 2026-09-11

Baseline `ce4a491f414e0d284eca0f43e9ae8b2621e8d0f6`. One finite synthetic
phase-robustness screen, not a detector, phase-invariant proof or music test.
Commit protocol before instrument and instrument before matrix execution.
Production code, confidence, version, H1/F1 instruments and corpus seals stay
unchanged. No phase-bank expansion, score/threshold rescue or second variant.

## Fixed fixtures and unknown-phase observations

Use the four distinct ideal spectra represented by the eight published
identifiability counterexamples, preserving first occurrence order. Retain
each representative's known/pure component amplitudes and frequencies from
F1. Deduplicate only by exact published `nonzero_spectrum`; no labels are
corrected. Revalidate all eight original F1 rows against their pinned report.

For each fixture and each source family (known harmonics or pure alternative),
generate exactly **32** realizations with independent component phases. Frame
origin is zero for this new phase experiment. Include out-of-range known
partials, as in F1. No gain, timbre, tuning, duration, window, padding or noise
variation. This yields 4*2*32 = **256** observations; neither family is favored.

For fixture index f, family s (`known`/`pure`), realization r=0..31 and component
index j in the frozen F1 order, hash the ASCII string
`apta-f2-20260911|f|s|r|j` with SHA256. Read the first eight bytes as unsigned
big-endian integer u and set phase `2*pi*(u/2^64)`. Publish hashes/phases.
Independent phases per harmonic are a bounded stress test, not a model of
all real instruments or correlated harmonic phases.

Synthesize the 48-kHz float64 component sum in frozen order, round each source
sample once to float32, then use the original ordered float32 four-sample
average. Compare with float64 averaging of the unrounded sum; require relative
L2 and max absolute error <=1e-6. Actual scored observations use the float32
averages. Require finite inputs/outputs and inherit F1/coverage FFT checks.

## Single phase-marginal reference construction

Build one fixed reference power spectrum per family per fixture. For each
component separately, synthesize amplitude-scaled sine and cosine at 48 kHz,
average four samples in float64, and compute the unpadded 12-kHz/1-Hz rFFT.
Its reference power is `0.5*(abs(FFT(sine))^2+abs(FFT(cosine))^2)`. Sum these
component powers. This is the phase-marginal power for independent uniform
component phases in this linear finite-window model. It is **not** an assertion
that cell-normalized scores equal expected scores or are phase-invariant.

Use the existing F1 fine-distance function unchanged: each occupied cell is
normalized separately, with fixed published ideal cell weights. Thus neither
observation cell totals nor known phases enter scoring. Both reference families
are supplied only as diagnostic hypotheses, not discovered notes/chords.

For each observation record distance to its generating family's reference
(`Dcorrect`) and the other family (`Dwrong`). The frozen screen passes only
if **every one of 256** observations satisfies `Dwrong > Dcorrect + 1e-6`.
Report ties/failures in each direction and fixture, signed margins, minima,
medians, all individual scores and phase provenance. Zero tolerance for a
misordering in this small screen; no new confidence or native key ranking.

If any observation fails, reject this phase-marginal scoring construction as
the next frontend basis. Keep F1's fixed-phase result intact, but do not call
the construction robust. Do not optimize phases or parameters against failures.
Even a complete pass permits only a separately frozen broader synthetic
representation/cost experiment, not a C port, music split or acceptance claim.

## Instrument and resource gates

- Verify pinned F1, coverage/H1 sources, exported PCM and witness files; all
  eight original F1 rows must replay exactly before new interpretation.
- Exactly four unique fixtures, eight reference spectra, 256 observations,
  32 observations/family/fixture and deterministic aggregate/detail replay.
- Analytic test: single-component power averaged over quadrature phases equals
  the sine/cosine reference; for two components, a complete quadrature product
  cancels cross terms. Test ordered phase hashing, family separation, replay,
  score/margin boundaries, cell-gain invariance and invalid inputs.
- Parseval <=1e-12 and selected direct Fourier sums <=1e-9 scaled, unchanged.
  Scores finite in [0,2], phase values finite in [0,2*pi), source rounding
  errors <=1e-6. Stop on instrument failure without relaxing tolerances.
- Single-thread full analysis process CPU <=60 seconds. Record first reference
  traced peak separately; host cost only, zero production CPU/RAM/state delta.
- No overwrite; commit source before execution, run once plus one identity
  replay, record all result/source/protocol/input/output/log hashes.

End with the frozen decision, phase-bank scope limits and one justified next
boundary. H1 and all six music transfer attempts remain rejected; holdouts,
independent development music and physical P4 acceptance are not opened here.
