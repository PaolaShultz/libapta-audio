# Independent two-tone refinement R2 — frozen 2026-09-12

Baseline `c8c44fa2f33a4aa1a61496a1fa807a98d75d70e1`. Freeze protocol before
implementation and instrument before evaluation. No music or C3 family rerun.

Hypothesis: a bounded two-dimensional search can recover independently wrong
frequency seeds under R1's unchanged raw-column fit, full-rank cutoff,
observability floor and synthetic sum-amplitude <=1 contract. Import R1 fit
unchanged, including independent column/least-squares checks. Tone count two
and two local seed neighborhoods are supplied; relative interval is no longer
supplied exactly. This is not note discovery, global optimization, constrained
least squares or an established amplitude model for music.

## Search fixed before outcomes

Each component shift lies in [-0.5,+0.5] Hz independently. Evaluate a 9x9
Cartesian grid, ascending lexicographic order, step 0.125 Hz. Invalid fits have
no score. If no valid grid point exists, abstain. Otherwise retain the lowest
score with lexicographic ties. Starting step 0.0625 Hz, perform 24 pattern
levels: evaluate the eight neighbors around the retained point, clip each axis
to bounds, retain the best among previous point and new valid neighbors, then
halve step. No cache, restart, early convergence, extra sweeps or extrapolation.
Maximum 81+24*8=273 fit evaluations per search. Coordinate identities follow
the seeds; accuracy compares sorted frequencies, since tone permutations are
equivalent. Search does not receive ground truth or amplitudes.

## New synthetic bank and gates

Two supports: [311.23,733.61] and [512.19,512.79] Hz. For each use total source
amplitude 0.20 and 0.80, divided equally, four phase combinations, and seed
error vectors [-0.31,+0.27], [+0.29,-0.33] Hz. There are 32 recovery cases and
16 waveforms. Phases use SHA256 ASCII
`apta-r2-20260912|support_index|phase_index|component_index`, first eight bytes
big-endian/2^64 *2*pi. Use C1's 48 kHz float64 synthesis and average-four
float32 observations unchanged. Float32/double relative rounding <=1e-6.

All 32 recovery cases must have a valid result, maximum sorted frequency error
<=1e-4 Hz, normalized squared residual <=1e-10, per-tone amplitude error <=1e-4,
and residual no worse than a valid seed fit by more than 1e-12. Evaluate true
frequencies as separate oracle controls; all must pass reconstruction/amplitude
gates. Report failures separately, retain abstentions in the denominator.

Four additional amplitude-stress searches use support 0, its four phase
combinations, total amplitude 1.40 and seed errors [-0.31,+0.27]. True-frequency
fit must reject for amplitude. Search may abstain or return a poor admissible
fit, but must never return a result with residual <=1e-10. Do not count those
expected rejections as frequency-recovery successes or require all candidates
to reject. This source exceeds the declared synthetic contract; it is not a
claim about valid normalized music.

Two fixed-model numerical stresses (no search) use a nonzero observation from
0.2*sin(2*pi*512*t): fit [512,512+2^-32] must reject rank; fit [1200+2^-40]
must reject weak columns. This demonstrates candidate rejection, not robust
inference for arbitrary nearly coincident physical sources. Six stress gates
and 32 recovery gates are conjunctive. Complete the frozen matrix on scientific
failure without method/gate rescue. An instrument-validation failure stops.

## Validation, costs, publication

Replay R1's 48 rows and nested O1's 24 rows identically; pin tool/dependency
and evidence hashes. Every new fit imports R1's analytic FFT comparison
(<=1e-10 column L2/6000), independent least-squares prediction check (<=1e-10),
raw SVD sqrt(float64 epsilon) cutoff and 1 MiB matrix+inverse limit unchanged.
Run new search/accounting tests plus unchanged diagnostics and reused native
coverage probes. No new full native build or physical-device claim.

Full control+screen CPU <=300 seconds; max 273 evaluations/search and
1 MiB/model. These are host diagnostic budgets, production RAM/state/CPU delta
zero. Clean instrument archive, WSL NumPy float64, OPENBLAS_NUM_THREADS=1;
one run and byte-identical deterministic summary/detail replay, timing separate.
Publish all rows, stress outcomes, candidate rejection reasons, scores, source
hashes, search/resource counts and exact instrument revision. No production
flags/version/API changes; corpus/holdout and release gates remain closed.
Any next method requires its own preregistration, not tuning this frozen search.
