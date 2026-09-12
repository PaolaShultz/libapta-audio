# Projected-tone numerical observability O1 — 2026-09-12

**The numerical instrument screen passes all frozen gates.** Of 24 analytic
bank cases, 12 support fitting, four are structurally invisible and eight are
too weak for normalization under the fixed precision guard. Abstentions are
expected instrument behavior, not correct family selections. No C2 family
verdict was recomputed and C2 remains rejected.

Protocol commit `848a100` preceded instrument
`4ee65030686d9f79b875c1639b6e3752d7b3e394` and bank evaluation. Baseline:
`cd57f1cd9b0ed81cd5a45412181b6c7de828e716`. See the
[frozen protocol](APTA-1.1-KEY-OBSERVABILITY-PROTOCOL.md) and
[complete 24-case evidence and validation record](../../evidence/1.1/key-observability-o1-20260912.json).

## Behavior and evidence

The separate Python instrument computes sine/cosine FFT columns using finite
geometric sums and the original four-sample box response. It retains C1's
889 bins and real/imaginary evidence space. Exact integer-cycle zeros are
preserved before normalization; no tolerance snaps near-integer frequencies
onto the grid. Structurally invisible pairs are omitted, with their physical
coefficients reported as null/unidentifiable rather than inferred zero.

For nonzero pairs, either column at or below `6000*sqrt(float64 epsilon)`
causes the entire model to abstain. Empty support and rank deficiency also
abstain. This is a conservative numerical precision rule, not an audibility
threshold, an amplitude prior or a guarantee of physical identifiability.
Other nearly dependent models can still produce large physical coefficients;
O1 does not solve every conditioning or source-inference problem.

| Independent bank group | Count | Outcome |
|---|---:|---|
| 0.5 Hz plus visible grid 128, 440, 1016 Hz | 4 | Ready |
| Invisible grid 127, 1017, 2048, 5999 Hz | 4 | Empty-support abstention; exact zero columns |
| Around 127/1017 Hz, both signs of 2^-4 and 2^-16 Hz | 8 | Ready |
| Around 127/1017 Hz, both signs of 2^-28 and 2^-40 Hz | 8 | Weak-component abstention; never tagged structural zero |

All comparisons use independently synthesized float64 time-domain waves,
average-four and FFT. All ready cases additionally fit independently generated
sin+0.5*cos PCM. No phase/frequency bank or tolerance changed after results.

| Gate/measurement | Result | Frozen limit |
|---|---:|---:|
| Maximum analytic/FFT column L2 error divided by 6000 | 1.9611988199440614e-13 | <=1e-10 |
| Visible-grid analytic coefficient error | 0 | <=1e-10 |
| Maximum ready-case normalized squared fit residual | 3.468457693763189e-18 | <=1e-10 |
| Independent least-squares prediction discrepancy | 1.0350433439692648e-15 | <=1e-10 |
| Maximum amplitude error on ready cases | 4.067799985740805e-9 | Report only |
| Bank CPU / repeat CPU | 0.080298 / 0.077933 seconds | <=30 seconds each |
| Maximum bank matrix+pseudoinverse storage | 56,896 bytes | <=1 MiB/model |

The storage figure covers each single-tone bank model, not total interpreter
memory or an ESP32-P4 budget. Mixed-support and duplicate-frequency behavior
is checked by unit tests, not a comprehensive multitone conditioning screen.

## Verification and reproducibility

Ten new unit tests pass, covering exact/nonintegral geometric sums, visible
and invisible bins, near-grid behavior, inclusive floor boundary, whole-model
weak abstention, mixed support with a nonzero but unobservable source amplitude,
rank deficiency and invalid inputs. All 45 unchanged C2/C1/F2/F1/identifiability/
H1 tests pass. Eleven coverage tests pass against each reused default Release,
I1 Release and sanitizer native probe. There is no new native build, full
CTest run, corpus evaluation or physical-device evidence in O1.

The bank ran from a clean source archive of the instrument commit under WSL
Ubuntu, NumPy 2.5.2, `OPENBLAS_NUM_THREADS=1`. Deterministic JSON replay is
byte-identical; both stderr files are empty. The evidence records tool/import
hashes, archive/report/test-log hashes, exact revision, timings and all rows.
Local reproducibility material is under `build/key-observability-20260912/`.

From the instrument revision, the bank command is:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/apta_key_observability.py \
  --source-commit 4ee65030686d9f79b875c1639b6e3752d7b3e394 \
  --output-prefix /tmp/apta-o1
```

Production `src/`, `include/`, `VERSION` and all predecessor diagnostic sources
have an empty diff against the baseline. Production resource/state delta is
zero, no candidate flags are enabled, and VERSION remains 1.0.1. The unrelated
untracked `output/` directory remains excluded from commits.

## Next boundary

O1 resolves the specific roundoff-normalization failure in the new instrument
on its independent numerical bank. It does not demonstrate improved frequency
robustness or key accuracy. Next separately preregister a frequency-uncertainty
reevaluation with this instrument, accounting explicitly for abstentions and
preserving the C2 observations, perturbations and original rejection. Do not
choose a floor from family outcomes, relax reconstruction gates or open music
to rescue the screen. Frequency estimation remains a later step; no native
frontend is retained or ported and WP6/WP7/release gates remain closed.
