# Local quadratic direction screen S2 — frozen 2026-09-12

Baseline `f7d0e7018de6fbab4bad85f9a03b01b0a922355f`. This is experiment one
of the two-experiment decision checkpoint. Freeze protocol before instrument,
instrument before runs. No tuning to old S1/R3 cases and no predecessor edits.

## Single local-search change

Keep S1's 9x9 [-0.5,+0.5]^2 grid, eight clipped poll neighbors, strict score
improvement, initial poll step 0.0625 and halve-only-after-failed-poll schedule.
Add a local quadratic direction derived from those same neighbors. With the
current center fixed, fit score differences to columns [u,v,u^2/2,u*v,v^2/2],
where [u,v]=(neighbor-center)/step. Use all valid neighbors and least squares
with rcond=sqrt(float64 epsilon). Require rank five and finite coefficients.
Build symmetric Hessian [[c2,c3],[c3,c4]]; require its smallest eigenvalue
>sqrt(epsilon)*largest absolute eigenvalue. Otherwise skip the modeled direction
and use the ordinary poll candidates only. No eigenvalue clipping/regularization.

Proposed physical displacement is -step*solve(H,[c0,c1]). Limit its infinity
norm to 0.125 by uniform scaling, then try clipped center+displacement*2^-j,
j=0..15, stopping at the first valid score strictly better than center. Compare
that trial with all poll candidates; take the lowest strictly improved score,
lexicographic ties. On improvement retain poll step, otherwise halve. Equal
scores do not move center. The surrogate alone never accepts a step; actual
fit evaluations decide. Invalid constraints remain invalid, never penalized
into a numerical score. No derivative of the tone model or true values is used.

Before each cycle reserve the worst-case 24 evaluations (eight polls+16 line
trials); if it would exceed 2049, report budget_exhausted. No partial cycle.
Stop poll_resolved only after a complete cycle without improvement at step
<=2^-24. It means finite sampled resolution, not global convergence. Track
all modeled directions, skips, trials, actual score changes and terminations.
No valid grid means no_valid_grid. Best-so-far remains diagnostic on exhaustion.

## New independent bank

Eight strictly convex quadratics: centers [0.137,-0.263] and [-0.317,0.229],
each with identity curvature and 19-degree rotated diag(1,k), k=64,1024,16384.
Require poll_resolved, max coordinate error <=1e-4 and score <=1e-8 in all eight.

Eight noiseless tone cases: supports [329.37,783.49] and [587.13,587.83] Hz;
total amplitude .40, low/high ratios 4 and 1/4, two phases each, seed errors
[-.27,+.31] Hz. Phases SHA256 ASCII `apta-s2-20260912|support|phase|component`,
first eight bytes big-endian/2^64 *2*pi. C1 synthesis/float32 average-four;
unchanged R1 fit, rank/weak floor, synthetic amplitude budget and independent
column/prediction checks. Require poll_resolved, sorted frequency error <=1e-4,
per-tone amplitude error <=1e-4, residual <=1e-10, and no regression versus
unchanged S1 search on the same signal beyond 1e-12. True-frequency oracle
controls must meet reconstruction/amplitude gates. Sort amplitude with frequency.

All sixteen gates conjunctive; full matrix completes on scientific failure,
instrument failure stops. No threshold, line budget or surrogate change after
results. If rejected, close the checkpoint with a direction decision rather
than a follow-up rescue. No music or changed-optimizer old R3/S1 replay.

## Verification and resources

Pin S1/R1/R2/O1 dependencies. Replay S1's original eight quadratic outcomes
identically and O1's 24 rows identically. Run S1 as baseline on all new cases.
Run targeted model/direction/budget tests and all unchanged related tests,
plus existing three native coverage probes. No new full native or P4 claim.
Full control+screen CPU <=300 seconds; <=2049 objective evaluations per S2
search and <=1 MiB per raw tone matrix+inverse. Keep all R1 numerical gates.
Clean source archive, NumPy float64, OPENBLAS_NUM_THREADS=1; once plus byte
replay of deterministic summary/trace, timing separate. Publish source/input
hashes, every bank result, fixes/breaks, resources and termination accounting.
Production resource delta zero; no production flags/API/VERSION/corpus changes.
