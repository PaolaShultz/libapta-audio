# Search termination diagnostic S1 — frozen 2026-09-12

Baseline `03b5c9f158cf7be94141c4dca4e0e3e3c4ab233d`. Freeze protocol before
implementation and instrument before results. No R3 case replay with a changed
optimizer; preserve all prior tools and rejections. This new standalone
diagnostic changes only the pattern step schedule and termination accounting.

## Method and finite meaning of termination

Keep R2's 9x9 grid over [-0.5,+0.5]^2, lexicographic tie order and eight clipped
neighbor directions. Start step 0.0625. On a strictly lower valid score, move
to the best neighbor and retain step; on no strict improvement, retain center
and halve step. Equal scores never move center. After a complete non-improving
poll at step <=2^-24, terminate `poll_resolved`. This means only no improvement
at eight sampled feasible neighbors at that scale, NOT global convergence,
stationarity certification, accurate parameters or residual acceptance.

Maximum 2049 objective evaluations (81 grid plus 246 complete eight-neighbor
polls). If no grid candidate is valid, `no_valid_grid`; if another full poll
would exceed the budget, `budget_exhausted`. Preserve a best-so-far candidate
as diagnostic data but only `poll_resolved` is eligible for screen acceptance.
Report every poll's center, step, best neighbor and movement decision. No
partial poll, restart, extrapolation, derivative or tuned improvement floor.

## Independent analytic bank

Eight known quadratics q(x)=(x-t)^T A(x-t), with centers t=[0.173,-0.287] and
[-0.219,0.341]; for each, A=I and A=Q diag(1,k) Q^T for k=16,256,4096, Q a
27-degree rotation. Strict convexity gives a known unique in-box minimum.
Run unchanged R2 search and S1 separately. S1 must terminate poll_resolved,
max coordinate error <=1e-4 and objective <=1e-8 on all eight. Compare R2
accuracy without treating its fixed iteration count as a termination claim.
These are optimizer tests, not physical tone models.

Eight new noiseless tone cases: supports [293.27,698.43] and [466.21,466.91]
Hz, total amplitude 0.40 with low/high ratios 4 and 1/4, two phases each.
Phases from SHA256 ASCII `apta-s1-20260912|support|phase|component`, first eight
bytes big-endian/2^64 *2*pi. Seeds have errors [-0.29,+0.33] Hz. Source generation
uses unchanged C1 float64 48 kHz/average-four float32 path. R1 fit is unchanged,
including raw-rank cutoff, weak-column floor, sum-amplitude <=1 synthetic
contract and independent FFT/least-squares validation. No true values steer
either search. Evaluate R2 baseline, S1 and true-frequency oracle separately.

Require poll_resolved, maximum sorted frequency error <=1e-4 Hz, per-tone
absolute amplitude error <=1e-4 (matched by frequency), residual <=1e-10 and
no regression from a valid R2 score beyond 1e-12 on all eight tone cases.
All true-frequency oracle reconstructions/amplitudes must pass. Any budget
exhaustion remains in denominator and fails combined screen even if best-so-far
accuracy passes. Report accuracy failures separately from termination failures.
All sixteen analytic+tone gates conjunctive; complete the fixed bank and report
failure without changing budget, step rule, scale or tolerances.

## Controls and instrument gates

Replay R1's 48 rows and nested O1's 24 rows identically; pin all imported
sources including R2 and R1 against published evidence. No full R3 rerun is
needed for this independent schedule test. Unit tests verify same-step moves,
halving only on failed polls, tie behavior, bound clipping, all-invalid grid,
budget exhaustion, exact evaluation cap, acceptance excludes budget exhaustion,
and known quadratic construction. Tests do not assert universal convergence.
Run unchanged related Python tests and existing three native coverage probes.

Clean source archive, WSL NumPy float64, OPENBLAS_NUM_THREADS=1. Full diagnostic
CPU <=300 seconds, per-tone model matrix+inverse <=1 MiB; no production resource
delta. Once plus deterministic report/trace byte replay, timings separate.
Numerical/contract gate failure stops; scientific failure completes this matrix.
Publish all cases, termination/poll accounting, fixes/breaks, resources and hashes.
No production flag/API/version change, music access, P4 or release acceptance.
