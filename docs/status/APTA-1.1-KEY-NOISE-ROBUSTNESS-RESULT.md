# Two-tone noise/amplitude robustness R3 — 2026-09-12

**R3 is rejected: 30/36 cases pass the frozen combined gates.** Four new
noiseless cases and two 40 dB cases fail. Every failure concerns the 0.6 Hz
tone pair with unequal amplitudes. Thus the limitation appears before noise
is added; R2's passing equal-amplitude bank did not establish general recovery.

Protocol `edf2fe3` precedes instrument
`8275a96d003fee73fd1292ae280ec8ade6263d45` and both runs. Baseline:
`948da5344c642e2a99d11acf72fbea90cf7e3cf9`. See the
[frozen protocol](APTA-1.1-KEY-NOISE-ROBUSTNESS-PROTOCOL.md) and
[complete public evidence](../../evidence/1.1/key-noise-robustness-r3-20260912.json).

## Fixed experiment and complete outcome

R2 search and R1 fit are imported unchanged. Tone count and two local seed
neighborhoods remain supplied; each component has its own frequency correction.
New supports are [277.31,659.47] and [523.17,523.77] Hz. Total tone amplitude
is 0.40, with low/high tone ratios 1, 4 and 1/4, two phase realizations and
seed errors [-0.31,+0.27] Hz. Twelve clean waveforms are each evaluated clean,
at 40 dB and at 20 dB observed-band SNR.

Noise is deterministic uniform pseudorandom noise, added at 48 kHz before
float32 average-four. The raw noise realization is shared across amplitude
ratios and levels for each support/phase. SNR is calibrated on the 889 retained
FFT bins, not on the full waveform or the weaker tone alone. This is not
Gaussian, colored, nonstationary or recorded background noise.

| Condition | Passes /12 | Frequency failures | Amplitude failures | Residual failures | Max frequency error | Max relative amplitude error |
|---|---:|---:|---:|---:|---:|---:|
| Clean | 8 | 4 | 3 | 4 | 0.03375001 Hz | 0.08356583 |
| 40 dB | 10 | 2 | 0 | 2 | 0.03375001 Hz | 0.08221240 |
| 20 dB | 12 | 0 | 0 | 0 | 0.04933593 Hz | 0.14869765 |

Gate failures overlap. All 36 return a candidate and improve or preserve
the seed residual: no abstentions or no-regression failures occur. Every
one of the 9828 search candidates is admissible; no amplitude/rank/weak
rejection accounts for these six failures.

Clean gates remain frequency <=1e-4 Hz, absolute amplitude <=1e-4 and residual
<=1e-10. The noisy engineering requirements are frequency <=0.02/0.10 Hz and
relative amplitude <=0.10/0.50 at 40/20 dB. The noise residual ceiling uses
1.10 times the known perturbation energy fraction plus 1e-10. It is an oracle
evaluation criterion, not deployable confidence or a physical noise estimator.

The 12/12 at 20 dB does **not** mean noise improves estimation: its tolerances
are looser and its largest observed frequency/amplitude errors are higher.
There are six noisy-versus-clean combined pass transitions and zero reverse
transitions under these condition-specific criteria; these are not six
same-threshold accuracy fixes. No residual-pass row violates its condition's
frequency or amplitude criteria, which is only a finite-bank observation.

## Failure location and known feasible reconstructions

All wide-pair cases and all equal-amplitude close-pair cases pass. The close
pair produces these failures:

| Low/high amplitude ratio | Phase | Condition | Frequency error | Search residual | True-frequency fit residual |
|---|---:|---|---:|---:|---:|
| 4 | 0 | Clean | 0.0004687575 Hz | 4.476238e-9 | 2.376970e-16 |
| 4 | 1 | Clean | 0.004375007 Hz | 2.118799e-7 | 2.306028e-16 |
| 1/4 | 0 | Clean | 0.03375001 Hz | 2.304256e-5 | 2.378110e-16 |
| 1/4 | 1 | Clean | 0.03375001 Hz | 1.258747e-5 | 2.279897e-16 |
| 1/4 | 0 | 40 dB | 0.03375001 Hz | 1.196587e-4 | 9.957618e-5 |
| 1/4 | 1 | 40 dB | 0.03375001 Hz | 1.167006e-4 | 9.973387e-5 |

The true-frequency fits are feasible and far better than the returned fits
in the failed clean cases, with the same observation and fit constraints.
This establishes a limitation of the frozen bounded search on these cases;
it does not establish an unavoidable spectral ambiguity or a physical
resolution limit. No alternative optimizer, extra pattern levels, restart,
step change, phase selection or tolerance adjustment was tried after failure.

## Validation and resources

- Original R2 recovery rows 32/32 and stress rows 6/6 replay identically,
  including nested R1 48 rows and O1 24 rows. Old source/input hashes are pinned.
- Every new candidate uses unchanged analytic column checks and independent
  least-squares prediction verification. Maximum column L2 error/6000 is
  3.5262726909901587e-13 and maximum prediction discrepancy is
  4.0642398731348165e-15, both below 1e-10.
- Float64 noise energy scaling and float32/double rounding pass the frozen
  1e-12 relative energy and 1e-6 rounding checks. Source/noise/observed hashes,
  scales, achieved band SNR and oracle ceilings are recorded per row.
- Seven new tests and 79 unchanged diagnostic tests pass. Eleven coverage
  tests pass against each reused default Release, I1 Release and sanitizer
  probe. No new full native build, CTest or physical P4 qualification is claimed.
- Largest per-model matrix+pseudoinverse is 113792 bytes, below 1 MiB.
  Search uses 273 evaluations/case. Interpreter/trace storage is excluded;
  these host figures are not a real-time or physical-device budget.
- Deterministic summary and complete candidate traces repeat byte-identically;
  both stderr files are empty. Full control+screen CPU is 104.599552 seconds
  and 103.958388 on replay, below the frozen 300-second limit each.

The clean instrument archive runs on WSL Ubuntu, NumPy 2.5.2,
OPENBLAS_NUM_THREADS=1. Local traces and run scripts are under
`build/key-noise-robustness-20260912/`; public evidence includes their hashes
and the final replay/timing validation record.

From the frozen instrument revision:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/apta_key_noise_robustness.py \
  --r2-evidence evidence/1.1/key-independent-shift-r2-20260912.json \
  --r1-evidence evidence/1.1/key-local-shift-r1-20260912.json \
  --o1-evidence evidence/1.1/key-observability-o1-20260912.json \
  --source-commit 8275a96d003fee73fd1292ae280ec8ade6263d45 \
  --output-prefix /tmp/apta-r3
```

## Next boundary

Next separately preregister a local-search convergence diagnostic before
further noise or music claims. It must distinguish exhausted search budget
from a sufficiently minimized residual, retain explicit amplitude constraints
and validate on independent analytic cases. R3 does not choose a replacement
optimizer or authorize tuning its fixed pattern schedule against these six
failures. Residual evaluation with oracle noise remains diagnostic-only;
unknown component count, seed discovery and music transfer remain unresolved.

Production source, predecessor tools, VERSION, flags and API/confidence
behavior have no changes; production RAM/state/CPU delta is zero and VERSION
remains 1.0.1. No music/holdout was accessed. R3 and C3 remain rejected, no
frontend is promoted, and WP6/WP7/P4/release gates stay closed. Unrelated
untracked `output/` remains excluded from commits.
