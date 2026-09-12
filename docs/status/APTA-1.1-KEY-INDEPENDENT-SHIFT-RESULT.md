# Independent two-tone refinement R2 — 2026-09-12

**R2 passes all 32 recovery cases and all six constraint stresses.** Maximum
sorted frequency error is 5.066340236226097e-9 Hz on this noiseless synthetic
bank. Recovery has 32 reconstruction fixes, zero breaks and zero abstentions.
The bounded search activates amplitude rejection for 742 candidates.

Protocol `a711a9b` precedes instrument
`ddcb07d6ec20e93ba17955f50b537695775cf390` and both runs. Baseline:
`c8c44fa2f33a4aa1a61496a1fa807a98d75d70e1`. See the
[frozen protocol](APTA-1.1-KEY-INDEPENDENT-SHIFT-PROTOCOL.md) and
[complete public results](../../evidence/1.1/key-independent-shift-r2-20260912.json).

## What changed

The two frequencies can move independently within supplied +/-0.5 Hz seed
neighborhoods. Search evaluates a 9x9 Cartesian grid followed by 24 fixed
eight-neighbor pattern levels with halved steps: 273 evaluations per search.
It retains the best valid evaluated point with lexicographic ties. There is
no restart, adaptive budget, global optimality claim or frequency extrapolation.

R1's fit is imported unchanged: raw O1 analytic columns, full-rank SVD cutoff
sqrt(float64 epsilon), O1 weak-column floor and sum of tone amplitudes <=1.
Candidates exceeding that synthetic amplitude contract are rejected; their
coefficients are neither clipped nor refit on the constraint boundary. This
is not constrained least squares or a physical amplitude rule for music.

Tone count and local seed neighborhoods remain supplied. The true interval
is not supplied to search. Accuracy uses sorted recovered frequencies so
permutations of the two tones are equivalent. The bank includes seed-order
inversion for one close-tone error vector.

## Recovery and constraints

Supports are [311.23,733.61] and [512.19,512.79] Hz, each with total amplitude
0.20 or 0.80 split equally between tones, four hash-derived phases and error
vectors [-0.31,+0.27] and [+0.29,-0.33] Hz. The 32 recovery cases represent
16 unique waveforms, with independent 48 kHz synthesis and float32 average-four
observations. All true-frequency oracle controls pass as well.

| Recovery group | Passes | Maximum frequency error | Maximum residual | Maximum amplitude error |
|---|---:|---:|---:|---:|
| Widely separated tones | 16/16 | 4.172307e-9 Hz | 2.755608e-16 | 3.021844e-10 |
| Tones separated by 0.6 Hz | 16/16 | 5.066340e-9 Hz | 2.407262e-16 | 4.244808e-9 |
| Frozen limits | 32/32 required | <=1e-4 Hz | <=1e-10 | <=1e-4 |

All results also satisfy the no-regression residual gate against valid seed
fits. These small errors describe this exact noiseless instrument test; they
are not a precision estimate for songs, noise or time-varying pitches.

Four stress searches use the wide support and total amplitude 1.40, outside
the declared source contract. All true-frequency fits reject for amplitude.
The searches each return an admissible but poor fit, with residuals
0.4117524, 0.4119123, 0.4122331 and 0.4118358. None passes the 1e-10
reconstruction gate. This is expected stress behavior, not four frequency
recoveries or four whole-search abstentions. A usable estimator must assess
fit quality; returning a candidate alone is not successful reconstruction.

Two fixed-model stresses also pass: [512,512+2^-32] Hz rejects for rank and
[1200+2^-40] Hz rejects for weak columns. These are candidate-level checks,
not end-to-end searches on arbitrary nearly coincident sources.

Across 36 searches, 9828 candidates are evaluated: 9086 ready and 742 rejected
for amplitude. Of those rejections, 516 occur in over-budget stress searches
and 226 during valid-source recovery searches. Maximum rejected total fitted
amplitude is 22.721926; maximum valid total is 0.9999999999456213. Maximum raw
condition number across search candidates is 55.186321. No search candidate
triggers rank/weak rejection; those paths are exercised by the fixed stresses.

## Numerical checks and reproducibility

- R1's 48 original rows and nested O1's 24 rows replay identically. All
  predecessor sources and input/dependency hashes remain pinned.
- Every evaluated model uses R1's independent time-domain/FFT column check:
  maximum column L2 error/6000 is 3.6369861511350997e-13, below 1e-10.
- Every valid fit has independent least-squares prediction verification:
  maximum discrepancy is 1.3667511508167651e-14, below 1e-10. All source
  float32/double relative rounding checks pass <=1e-6.
- Eight new search/accounting tests and 71 unchanged diagnostic tests pass.
  Eleven coverage tests pass against each reused default Release, I1 Release
  and sanitizer probe. No new full native build/CTest or physical P4 evidence
  is claimed.
- Summary and full candidate traces replay byte-identically; stderr is empty.
  Full control+screen CPU is 59.437199 seconds and 60.114812 on replay, below
  the frozen 300-second bound. Largest matrix+pseudoinverse is 113792 bytes,
  below 1 MiB/model. This excludes interpreter/trace storage and is not a P4
  memory or real-time performance budget.
- Runs use a clean archive of the instrument revision, WSL Ubuntu, NumPy 2.5.2,
  OPENBLAS_NUM_THREADS=1. Public evidence includes all recovery/stress rows,
  aggregate rejection metrics, source/input/artifact hashes, tests and timings.
  Local candidate traces and scripts are in `build/key-independent-shift-20260912/`.

Reproduce from the frozen revision:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/apta_key_independent_shift.py \
  --r1-evidence evidence/1.1/key-local-shift-r1-20260912.json \
  --o1-evidence evidence/1.1/key-observability-o1-20260912.json \
  --source-commit ddcb07d6ec20e93ba17955f50b537695775cf390 \
  --output-prefix /tmp/apta-r2
```

## Next boundary

Next separately preregister a robustness screen with additive noise and
unequal tone amplitudes, retaining explicit source-budget assumptions and
accounting for incorrect estimates, poor reconstruction and abstentions.
Noise requires its own justified residual/error criteria before evaluation;
do not retrofit R2's noiseless precision claim or tune against C3 outcomes.
Unknown tone count, seed discovery, harmonic model mismatch and music transfer
remain later, separate problems. C3 remains rejected; no frontend is promoted.

Production sources, predecessor tools, API/confidence, flags and VERSION have
an empty diff from baseline. Production RAM/state/CPU delta is zero, VERSION
stays 1.0.1, no music or holdout is accessed and WP6/WP7/P4/release gates remain
closed. Unrelated untracked `output/` is excluded from commits.
