# Coherent frequency-hypothesis screen C1 — frozen 2026-09-12

Baseline `1622027e64251e5b15e6630b9d64bf2157d59ac9`. One synthetic diagnostic
of supplied frequency hypotheses under unknown phases. No note discovery,
key detector, production port, corpus access or release change. Commit protocol
before implementation and instrument before execution. H1/F1/F2 remain frozen;
F2 is not tuned or rehabilitated by this result.

## Question and fixed phase bank

F2's average-power reference reverses four of 256 observations. Test whether
retaining the complex FFT and fitting sine/cosine coefficients for each supplied
frequency can distinguish the same two families with unknown component phases.
This changes both evidence and score relative to F2: do not attribute a gain
solely to phase or claim cell-total invariance of the new score.

Use the same four unique ideal spectra in prior witness first-occurrence order.
Keep frequencies/amplitudes/one-second duration/48-kHz float32 source and
ordered four-sample averaging unchanged. Both known-harmonic and pure families
are evaluated, 32 realizations each: exactly **256 new observations**.
For component j, fixture f, family s and realization r use SHA256 of ASCII
`apta-c1-20260912|f|s|r|j`, first eight bytes unsigned big-endian u, phase
`2*pi*(u/2^64)`. This is a new deterministic development phase bank; no seed,
phase count, noise, timbre, tuning, gain or length variation is allowed.

Replay all 256 old F2 scores/phases and eight F1 controls exactly from the pinned
instruments before interpreting the new results. Run frozen F2 references on
the new bank too, reporting reversals descriptively; do not change F2.

## Coherent representation and fit

For each fixture/family build sine and cosine unit-amplitude 48-kHz waves at
every supplied component frequency, in frozen component order. Include the
known family's out-of-range components, as in its physical generator. Average
four samples in float64, compute the rectangular 12-kHz/12000-sample rFFT and
retain only bins in the original C3–B5 geometric range. No padding, new window,
frequency refinement, harmonic weighting or measured out-of-range FFT bins.

Stack real and imaginary parts of each retained complex column to form a real
matrix. Normalize each column to unit L2; reject a zero/nonfinite column. Compute
one thin SVD per family, retaining singular values >`1e-12*smax`. Use its fixed
pseudoinverse to fit unconstrained real sine/cosine coefficients to each observed
complex FFT. The fitter receives only the observation and the supplied matrix,
never generating phases/family labels or amplitudes. Coefficients can express
any amplitude/phase; no amplitude prior, sparsity penalty or family-size penalty.
Record retained rank, singular values, condition number, coefficient values and
reconstruction residual. No claim of unique fundamental interpretation.

Score each hypothesis by squared complex residual divided by observed in-range
complex squared norm. This retains coherent cross terms and cell totals, unlike
F2. A larger hypothesis has more degrees of freedom; the bidirectional screen
and per-family results must expose this limitation, not hide it in a total.
The supplied family frequencies are ideal diagnostic knowledge, not estimated
from observations. Out-of-range component leakage can contribute to the fit.

## Frozen screen and validity gates

Every observation must satisfy both:

- correct-family normalized squared residual <=`1e-10`;
- wrong-family residual > correct-family residual + `1e-6`.

All 256 must pass. A failure rejects this construction for the next research
stage; no solver/rcond/frequency/phase-bank/threshold rescue. A full pass supports
only a separately preregistered frequency-uncertainty test before any discovery
algorithm, C port or music split. Never turn supplied-hypothesis discrimination
into key accuracy or formal confidence.

Correctness before interpretation:

- Pinned F2/F1/coverage/H1 sources, PCM and witness hashes; old scores replay.
- Exactly four fixtures/eight fitted matrices/256 new observations, with 32 per
  generating family per fixture and deterministic complete report replay.
- Inherit FFT Parseval <=1e-12, direct sums <=1e-9 scaled, source float rounding
  relative/max absolute <=1e-6, finite phases in [0,2*pi), finite coefficients
  and scores. Record all matrix dimensions and rank cutoffs unchanged.
- Recompute residual from fitted columns, not by subtracting projection norms.
  Compare coefficients/residual against independent `numpy.linalg.lstsq` with
  the same rcond for the first observation in each family/fixture: reconstructed
  prediction difference <=`1e-10*max(1,||observation||2)`.
- Unit tests: exact sine/cosine and mixed-frequency recovery, unknown phase,
  absent-frequency residual, dependent columns/rank handling, invalid/zero
  inputs, hash ordering and independence from F2, score boundaries and replay.
- Single-thread process CPU <=60 seconds, largest matrix plus pseudoinverse
  numeric storage <=1 MiB. Report first-matrix traced peak separately, including
  SVD temporary overhead. No P4 resource claim; production CPU/RAM/state delta zero.

Commit before matrix, run once plus one identity replay, publish all score and
phase provenance with exact hashes and costs. Stop on correctness failure,
preserve its history, never relax tolerance. No production/API/version changes
or music/holdout access. End with the bounded decision and one next boundary;
all prior detector and music transfer rejections remain in force.
