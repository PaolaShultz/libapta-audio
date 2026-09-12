# Bounded local common-frequency shift R1 — 2026-09-12

**All 48 cases pass the bounded common-shift screen.** Local refinement
recovers the supplied support's common frequency error with maximum error
9.277223039783067e-8 Hz. Reconstruction passes increase from 0/48 at the seed
and 0/48 on the coarse grid to 48/48 after refinement. There are no breaks
or abstentions. This is synthetic numerical evidence with supplied tone count
and relative spacing, not note discovery, music accuracy or C3 acceptance.

Protocol `c88b57d` and pre-evaluation amendment `e78902d` precede instrument
`2d0ee0984f58c44748603bcc3fde5e2051e2b8b8`. Baseline:
`0f82a398fab4e05f153edc4e2e6b68ef14512ad1`. See the
[protocol](APTA-1.1-KEY-LOCAL-SHIFT-PROTOCOL.md),
[pre-evaluation amendment](APTA-1.1-KEY-LOCAL-SHIFT-AMENDMENT.md) and
[complete public evidence](../../evidence/1.1/key-local-shift-r1-20260912.json).

The amendment changes initial errors from +/-0.375 to +/-0.37 Hz before any
bank evaluation. The original values coincided exactly with the search grid
and would not test interpolation. No scientific outcome prompted this change;
all other construction, source, budget and gate definitions remain frozen.

## Construction and scope

The new standalone Python instrument fits raw physical O1 sine/cosine columns
using SVD with relative cutoff sqrt(float64 epsilon), without column
normalization. Weak columns or rank deficiency reject the entire candidate.
An unconstrained fit whose sum of pairwise sine/cosine amplitude magnitudes
exceeds 1 is also rejected. This budget is an explicit synthetic source
contract; it is not deduced from peak PCM or established for music. Rejection
does not solve constrained least squares or clip coefficients at a boundary.

Search is one-dimensional: all supplied frequencies move together over
[-0.5,+0.5] Hz. It uses 33 uniform grid points followed by 24 golden-section
updates and retains the best valid evaluated point, with deterministic ties.
Every bank search uses the frozen maximum of 59 candidate evaluations. The
known true frequencies are evaluated separately as oracle controls and are
never passed to the search as targets.

The three supports are a single 233.17 Hz tone, separated tones 233.17/587.41
Hz and close tones 440.13/440.63 Hz. Each uses total source amplitude 0.05 or
0.20, divided equally among tones, four hash-derived phase combinations and
both initial errors. There are 48 cases but only 24 distinct waveforms. Tone
count and relative intervals are supplied oracle information. The bank has
no noise, drift, partial mismatch, unknown component count or independently
incorrect tone intervals.

## Frozen gates and measurements

| Measurement | Observed | Frozen requirement |
|---|---:|---:|
| Combined screen passes | 48/48 | 48/48 |
| Oracle reconstruction/amplitude controls | 48/48 | 48/48 |
| Largest common-shift error | 9.277223e-8 Hz | <=1e-5 Hz |
| Largest refined normalized squared residual | 2.862671e-14 | <=1e-10 |
| Largest per-tone amplitude error | 2.263212e-8 | <=1e-5 |
| Seed reconstruction fixes / breaks | 48 / 0 | No regression |
| Abstentions | 0 | 0 |
| Largest analytic/independent FFT column error divided by 6000 | 2.102600e-13 | <=1e-10 |
| Largest independent least-squares prediction discrepancy | 4.979200e-15 | <=1e-10 |
| CPU / repeat CPU | 12.192759 / 13.632862 seconds | <=120 each |
| Largest matrix+pseudoinverse | 113792 bytes | <=1 MiB/model |

All searches improve the valid seed fit. Seed residuals range from 0.0524901
to 0.3772602. The coarse grid itself has zero reconstructions below 1e-10,
so this bank does exercise refinement between grid points. These are errors
on fixed noiseless synthetic signals, not estimates of precision on real audio.

All 2832 search candidates are ready; none activates weak/rank/amplitude
rejection. The maximum raw condition number is 2.124295, including the 0.5 Hz
pair. Maximum total fitted amplitude is 0.262713, below the declared budget,
and maximum absolute candidate coefficient is 0.1999983. Therefore this bank
does not establish behavior when a constraint is active or components are
severely ill-conditioned. Budget/rank/weak rejection is covered by targeted
unit tests only; no robustness claim beyond these tests is made.

## Validation and reproducibility

Nine new tests cover the exact inclusive amplitude boundary, amplitude rejection
without clipping, weak/rank rejection, invalid/silent input, search cap/bounds,
endpoints, flat ties, partially/all-invalid searches and phase replay. All 62
unchanged diagnostic tests pass. Eleven coverage tests pass against each
reused default Release, I1 Release and sanitizer native probe. No new full
native build, CTest qualification or P4 measurement was performed.

O1's original 24 numerical rows replay identically. Every evaluated candidate
column is checked against independent time-domain synthesis and FFT. All
valid fits have independent least-squares verification. Source float32 versus
float64 average-four rounding passes its <=1e-6 relative gate. The deterministic
summary and full candidate trace replay byte-identically; stderr is empty.

Runs use a clean archive of the instrument revision, WSL Ubuntu, NumPy 2.5.2,
OPENBLAS_NUM_THREADS=1. Public evidence contains all 48 results, input/tool/
dependency hashes, trace aggregates, validation and resource records. Local
traces, scripts and test logs are in `build/key-local-shift-20260912/`; their
hashes are published. Report storage/interpreter memory is excluded from the
per-model storage metric, which is not a P4 budget.

From the frozen revision:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/apta_key_local_shift.py \
  --o1-evidence evidence/1.1/key-observability-o1-20260912.json \
  --source-commit 2d0ee0984f58c44748603bcc3fde5e2051e2b8b8 \
  --output-prefix /tmp/apta-r1
```

## Next boundary

R1 supports only bounded common-shift recovery with supplied spacing under
its synthetic amplitude contract. Next separately preregister independent
per-tone frequency refinement on a new analytic bank, with explicit evaluation
of active amplitude rejection, near-dependent tones and abstention accounting.
Do not carry the amplitude budget over to music as an established physical
rule, optimize the 32 C3 reversals or reopen a spent/formal corpus. C3 remains
rejected and no native frontend is selected or ported.

Production `src/`, `include/`, VERSION and all predecessor tools have an empty
diff from baseline. No candidate flags, API/confidence or production RAM/CPU/
state changes occur. VERSION stays 1.0.1; WP6/WP7/P4 and release gates remain
closed. The unrelated untracked `output/` directory remains excluded from commits.
