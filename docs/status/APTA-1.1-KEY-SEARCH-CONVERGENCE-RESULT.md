# Search termination diagnostic S1 — 2026-09-12

**The conjunctive S1 screen is rejected: 14/16 cases pass.** All eight new
tone cases pass, including four that unchanged R2 search misses. Six of eight
quadratics pass; the two with condition number 4096 exhaust the 2049-evaluation
budget while still inaccurate. They are explicitly reported `budget_exhausted`,
not `poll_resolved`.

Protocol `f0d88ec` precedes instrument
`ab851aba8e12b0a0c5240dec7d7146835ed957ab` and both runs. Baseline:
`03b5c9f158cf7be94141c4dca4e0e3e3c4ab233d`. See the
[frozen protocol](APTA-1.1-KEY-SEARCH-CONVERGENCE-PROTOCOL.md) and
[complete public results](../../evidence/1.1/key-search-convergence-s1-20260912.json).

## Changed step schedule and explicit termination

S1 retains R2's 9x9 grid, independent +/-0.5 bounds and eight clipped poll
directions. It keeps the step after a strict improvement and halves it only
after a complete unsuccessful poll. Equal scores never move the center.
Termination requires an unsuccessful poll at step <=2^-24, or reports exhausted
budget before a further full poll could exceed 2049 evaluations. No extra
starts, extrapolation, derivatives, fitted floors or partial polls are used.

`poll_resolved` means only that the eight tested neighbors at the final scale
do not improve the objective. It does not certify stationarity, a global
minimum, accurate parameters or acceptable reconstruction. Accuracy and
termination are scored separately. No resolved-but-inaccurate result occurs
in this finite bank; that is not a general guarantee. Neither exhausted case
passes the accuracy gates either.

## Known quadratic objectives

Two centers are tested with identity curvature and 27-degree rotated curvature
ratios 16, 256 and 4096. Each strictly convex quadratic has a known unique
in-box minimum. These ratios describe objective geometry, not the condition
number of a tone fit matrix.

| Center | Curvature ratio | S1 evaluations | Max coordinate error | Termination |
|---|---:|---:|---:|---|
| [0.173,-0.287] | 1 | 401 | 2.193451e-8 | poll_resolved |
| [0.173,-0.287] | 16 | 425 | 2.193451e-8 | poll_resolved |
| [0.173,-0.287] | 256 | 897 | 9.727478e-8 | poll_resolved |
| [0.173,-0.287] | 4096 | 2049 | 0.03146777 | budget_exhausted |
| [-0.219,0.341] | 1 | 377 | 2.050400e-8 | poll_resolved |
| [-0.219,0.341] | 16 | 417 | 2.050400e-8 | poll_resolved |
| [-0.219,0.341] | 256 | 905 | 1.010895e-7 | poll_resolved |
| [-0.219,0.341] | 4096 | 2049 | 0.05748926 | budget_exhausted |

The six resolved cases meet coordinate <=1e-4 and objective <=1e-8. Relative
to R2 accuracy on this bank, three quadratics are fixed and none broken. The
remaining narrow, rotated objectives need more efficient search than this
frozen axis/diagonal poll rule supplies under its budget. S1 does not justify
increasing the budget after seeing the failures.

## Independent tone bank

Supports [293.27,698.43] and [466.21,466.91] Hz use total amplitude 0.40,
ratios 4 and 1/4 and two hash-derived phase realizations each. Seeds have
independent errors [-0.29,+0.33] Hz. All eight sources are new noiseless
analytic cases, not the failed R3 waveforms. R1's raw fit, rank/weak guards,
synthetic amplitude budget and independent numerical verification are unchanged.

All eight true-frequency oracle controls and S1 reconstructions pass. S1 fixes
all four close-tone cases missed by R2 on this bank, preserving its four wide
tone successes. No-regression score checks pass in all eight cases. These
four fixes plus the three quadratic fixes give seven accuracy fixes and zero
breaks in the complete bank; this does not repair the historical R3 verdict.

| Tone measurement | Result | Frozen limit |
|---|---:|---:|
| Combined tone passes | 8/8 | 8/8 |
| Maximum sorted frequency error | 3.790855e-7 Hz | <=1e-4 Hz |
| Maximum amplitude error | 6.801499e-8 | <=1e-4 |
| Maximum normalized residual | 2.561061e-15 | <=1e-10 |
| Wide-pair evaluations | 369 each | <=2049 |
| Close-pair evaluations | 617..921 | <=2049 |

The previous R2 search always used 273 evaluations. The improvement here costs
more evaluations, and none of these host diagnostic counts establishes a P4
real-time budget. Tone count and nearby seeds remain supplied; no discovery,
noise robustness or musical-key acceptance is demonstrated.

## Validation and reproducibility

Seven new tests and 86 unchanged diagnostic tests pass. Eleven coverage tests
pass against each reused default Release, I1 Release and sanitizer probe.
R1's 48 rows and nested O1's 24 rows replay identically. R2's source is pinned
and used unchanged as the independent-bank baseline; no changed-optimizer R3
rerun was performed. Every tone candidate retains independent analytic-column
and least-squares checks. Public evidence reports their maxima, the 1 MiB
per-model storage check, source/input hashes and all result rows.

The instrument runs from a clean archive on WSL Ubuntu, NumPy 2.5.2,
OPENBLAS_NUM_THREADS=1. The complete candidate/poll trace is retained locally
under `build/key-search-convergence-20260912/`; public validation records its
hash and checks every step transition and full-poll budget. Matrix storage
excludes interpreter and traces; no full native build/CTest or P4 evidence is
claimed.

Summary and complete candidate/poll traces replay byte-identically; stderr is
empty and all recorded step transitions satisfy the frozen schedule. Full
control+screen CPU is 45.858551 seconds, replay 46.085946, below 300 seconds.
Largest matrix+pseudoinverse is 113792 bytes. Maximum analytic column error
is 3.5846433488288157e-13 and independent prediction discrepancy is
4.140850367118533e-15, both below 1e-10.

Reproduce from the frozen instrument revision:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/apta_key_search_convergence.py \
  --r2-evidence evidence/1.1/key-independent-shift-r2-20260912.json \
  --r1-evidence evidence/1.1/key-local-shift-r1-20260912.json \
  --o1-evidence evidence/1.1/key-observability-o1-20260912.json \
  --source-commit ab851aba8e12b0a0c5240dec7d7146835ed957ab \
  --output-prefix /tmp/apta-s1
```

## Next boundary

Keep the explicit distinction between budget exhaustion, finite poll resolution
and accuracy. Next separately preregister a local-search method that can adapt
its directions to correlated parameters, with the same explicit resource and
termination accounting, and validate it on independent known objectives before
further noise/musical claims. This result selects no replacement method and
does not authorize tuning S1 on its two failed quadratics or R3 failures.

Production sources, all predecessor tools, API/confidence, flags and VERSION
have no changes. RAM/state/CPU production delta is zero, VERSION stays 1.0.1,
no corpus/holdout is accessed and WP6/WP7/P4/release gates remain closed. No
frontend is promoted. Unrelated untracked `output/` is excluded from commits.
