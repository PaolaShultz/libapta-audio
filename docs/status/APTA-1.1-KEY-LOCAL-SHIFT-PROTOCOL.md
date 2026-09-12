# Bounded local common-frequency shift R1 — frozen 2026-09-12

Baseline `0f82a398fab4e05f153edc4e2e6b68ef14512ad1`. Commit this protocol
before implementation, then freeze instrument before bank evaluation. R1 is
a standalone numerical prerequisite, not note discovery, a C3 retry or a
production candidate. No C1/C2/C3 family scores or music are evaluated here.

## Hypothesis and explicit signal contract

For supplied one/two-tone relative spacing, bounded one-dimensional refinement
can recover a common frequency error while refusing numerically unstable or
amplitude-inadmissible fits. Unknown phase and amplitudes are fit. Relative
spacing and tone count are supplied oracle information; independently erroneous
component frequencies, arbitrary partial structure and music remain out of scope.

Use unchanged O1 analytic raw sine/cosine columns and retained FFT bins.
Use physical columns without per-column normalization. Thin SVD pseudoinverse
uses cutoff sqrt(float64 epsilon)*largest singular value: require full rank
and every column norm > O1 FLOOR, otherwise reject the whole candidate.
Structural zero columns cause rejection here, not O1's omission, since R1
requires every supplied tone to be identifiable. Require sum over tone pairs
of hypot(sine coefficient, cosine coefficient) <=1. This is a declared
synthetic source-amplitude budget, not inferred from peak PCM, not a general
music law and not a constrained least-squares solver. An unconstrained optimum
outside the budget is rejected, not clipped or refit on the boundary. No valid
candidate means abstention; reject zero/nonfinite observations and invalid input.

## Fixed search and independent bank

For seed frequencies, search one common shift in [-0.5,+0.5] Hz. Evaluate 33
uniform points (step 1/32), ties prefer lower shift. If all fail, abstain.
Bracket the best grid point by its neighbors, clipped at endpoints; perform
24 golden-section updates with two initial interior evaluations. Retain the
best valid evaluated point including the grid; no extrapolation, adaptive
budget or extra starts. At most 59 evaluations/search. Also evaluate supplied
seed directly as a before-refinement baseline, and true frequencies separately
as an oracle control (neither steers search).

Frozen supports: [233.17], [233.17,587.41], [440.13,440.63] Hz. These are new
analytic fixtures, unrelated to C3 verdicts; third support probes close tones.
For each support use total source amplitudes 0.05 and 0.20, split equally among
tones; four independent phases, each SHA256 ASCII
`apta-r1-20260912|support_index|phase_index|component_index`, first eight bytes
big-endian divided by 2^64 times 2*pi. Initial common errors are -0.375,+0.375
Hz. This gives 48 cases (24 unique waveforms). Synthesize at 48 kHz, float64,
absolute frame origin zero, average-four to scored float32 PCM as in C1.

All 48 must return valid estimates with |estimated common shift+seed error|
<=1e-5 Hz, normalized squared residual <=1e-10, maximum per-tone amplitude
error <=1e-5, and score no worse than the valid seed baseline (1e-12 tolerance).
All oracle controls must pass residual/amplitude gates. Any abstention remains
in the denominator and fails this screen. Report whole-bank fixes/breaks in
reconstruction vs seed, search evaluations, rejected-candidate reasons, physical
amplitudes and raw condition numbers. Complete this single matrix on scientific
failure; do not rescue it by thresholds, phases, supports or search changes.

## Instrument gates, resources and scope

For every evaluated valid-frequency model compare raw columns to independent
time-domain synthesis/FFT; max column L2 error/6000 <=1e-10. Verify valid fit
predictions via independent np.linalg.lstsq with the same raw cutoff at <=1e-10.
Check source average-four float32 vs float64 relative error <=1e-6. Unit tests
cover budget rejection, exact-inclusive budget, rank/weak rejection, silence,
nonfinite inputs, fixed search bounds/evaluation cap, all-invalid abstention,
endpoints, flat ties, and deterministic phase generation. Replay O1's 24 rows
identically and run unchanged diagnostic and reused native coverage tests.

Expected host CPU <=120 seconds for the full bank including independent raw
checks and O1 replay. Per-model raw matrix+pseudoinverse <=1 MiB. Use clean
instrument source archive, WSL NumPy float64, OPENBLAS_NUM_THREADS=1; once plus
byte-identical deterministic report replay, timing separate. Instrument gate
failure stops without method changes. Publish exact source/dependency hashes,
all rows, scientific and numerical gates, resources and limitations.

Production CPU/RAM/state delta zero, no native source/flag/version changes,
no new full native build/P4 evidence, no music or holdout access. A passing R1
would support only this bounded common-shift instrument and declared source
budget. Independent per-component refinement requires a later protocol and
amplitude/identifiability model; no automatic C3 rescue or frontend promotion.
