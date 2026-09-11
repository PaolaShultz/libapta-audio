# Within-cell phase screen F2 — 2026-09-11

**Rejected: 252/256 observations pass; four prefer the wrong reference.**
The frozen rule required every observation to rank its generating family's
reference closer by more than 1e-6. All four failures have negative margins,
not merely positive margins below tolerance. This phase-marginal construction
is not retained as the next frontend basis. F1's fixed-phase finding remains
valid, H1 stays rejected, and no new detector or native key result is produced.

Protocol commit `a774e2b` preceded instrument source
`e9ad4a750b931cf7ede3f79d2285c44b9ced62e6` and the matrix. Baseline:
`ce4a491f414e0d284eca0f43e9ae8b2621e8d0f6`. See the
[frozen protocol](APTA-1.1-KEY-PHASE-ROBUSTNESS-PROTOCOL.md) and
[public aggregate with every score, phase and hash](../../evidence/1.1/key-phase-f2-20260911.json).

## Fixed experiment

Four distinct ideal spectra are deduplicated from the eight prior ambiguity
pairs, in first-occurrence order. For each fixture, both the known harmonic
source and pure-tone alternative are synthesized in 32 deterministic phase
realizations, giving 256 observations. Component amplitudes/frequencies and
the one-second/48-kHz source/12-kHz averaged FFT remain fixed. Phases are
independent for each component and hashed from fixture/family/realization/
component indices with the frozen SHA256 seed string. There is no phase fit,
additional bank, gain/noise/timbre sweep or retuning.

Each observation rounds its source sum to float32 and uses the native ordered
four-sample average. Each reference instead sums individual component powers
averaged over sine and cosine quadratures. This gives the independent-uniform-
phase marginal **power** of that linear model. It does not make the normalized
within-cell score phase-invariant or equal to an expected score. F1's cell
normalization and fixed ideal weights are reused unchanged. Both candidate
frequency families are supplied as diagnostic hypotheses, not detected notes.

The score is `Dwrong - Dcorrect`, where correct means the family that generated
that synthetic observation. This is spectral-family discrimination; no new
mol/dur accuracy, native key confidence or music acceptance is measured.

## Complete group results

Fixture representatives are the prior IDs `[5,1,5,2]`, `[6,1,5,2]`,
`[7,1,5,2]`, `[8,1,5,2]`. Each now uses frame origin zero and its new independent
phases; the original F1 phase results are replayed separately as controls.

| Fixture | Generating family | Pass /32 | Fail | Minimum signed margin | Median margin |
|---|---|---:|---:|---:|---:|
| 0 | Known harmonics | **28** | **4** | **-0.005911744** | 0.153876678 |
| 0 | Pure alternative | 32 | 0 | 0.205457960 | 0.213299408 |
| 1 | Known harmonics | 32 | 0 | 0.340117520 | 0.416041742 |
| 1 | Pure alternative | 32 | 0 | 0.418159704 | 0.418419896 |
| 2 | Known harmonics | 32 | 0 | 0.317070969 | 0.361476384 |
| 2 | Pure alternative | 32 | 0 | 0.376646096 | 0.378976053 |
| 3 | Known harmonics | 32 | 0 | 0.149828706 | 0.268332458 |
| 3 | Pure alternative | 32 | 0 | 0.313868207 | 0.319675726 |

Thus the harmonic observations pass 124/128 and pure alternatives 128/128.
The four failures all occur in fixture 0, the B-flat-minor missing-fundamental
source family. Its closest components share a cell, but this experiment does
not isolate one component or prove which interference term causes each error.

| Realization | Dcorrect | Dwrong | Signed margin |
|---|---:|---:|---:|
| 5 | 0.336140117 | 0.335246175 | -0.000893942 |
| 10 | 0.338128400 | 0.332216657 | -0.005911744 |
| 21 | 0.214039860 | 0.212265486 | -0.001774373 |
| 30 | 0.257004146 | 0.255732257 | -0.001271889 |

The sine/cosine reference construction itself passes analytic quadrature
tests, including cancellation of two-component cross terms over a complete
quadrature product. Nevertheless, a finite coherent observation need not be
closest to its own averaged-power reference after cell normalization. The
four measured reversals refute the frozen screen for this construction.
They do not prove that within-cell evidence in general cannot distinguish
unknown-phase sources, or that every phase-aware model would fail.

## Gates and validation

| Gate | Result | Outcome |
|---|---|---|
| All observations: Dwrong > Dcorrect +1e-6 | 252/256; four reversed | **Fail** |
| Four fixtures, eight references, 32 observations/family | 256 complete observations | Pass |
| Original F1 rows unchanged | 8/8 exact replay | Pass |
| Source rounding relative/absolute <=1e-6 | Max 4.0512e-8 / 4.6792e-8 | Pass |
| Parseval <=1e-12 | Max 1.9243e-15 | Pass |
| Direct Fourier scaled error <=1e-9 | Max 1.7895e-12 | Pass |
| Complete aggregate/detail repeat | Byte-identical | Pass |
| Host process CPU <=60 s | 2.148045 s; replay 2.278337 s | Pass |

The failure is preserved. No phase optimization, new weighting, threshold,
seed, realization count or candidate was tried after observing it. The only
repeat was the preregistered deterministic replay.

- Six new phase tests pass, including exact phase-hash ordering/family
  separation, single/two-component quadrature identities, float observation
  replay, score cell-gain invariance, margin boundaries and invalid input.
- Six unchanged F1, ten identifiability and eight H1 regression tests pass.
  Eleven coverage tests pass against each reused default Release/Werror,
  I1 Release/Werror and I1 Debug ASan/UBSan native probe. No full new native
  build/CTest or physical P4 qualification is claimed.
- Pinned F1, coverage/H1 source hashes, PCM and witness records verify. Every
  original F1 row replays exactly before the new matrix. Both stderr files
  are empty; scores/phases are finite and all observation records complete.
- Phase arrays and their SHA256 derivation hashes are published for every
  observation. Resource timing is separate from deterministic report identity.
- First-reference incremental traced peak is 1,876,464 bytes, excluding
  component records and full reports. This is a single host allocation sample,
  not a total/P4 memory budget. Production CPU/RAM/state delta is zero.
- Environment: WSL Ubuntu, NumPy 2.5.2, `OPENBLAS_NUM_THREADS=1`.

The public JSON contains all 256 scores/phases/hashes, group margins, source/
protocol/archive/input/output/log hashes and resources. Local
`build/key-phase-robustness-20260911/result-detail.json` retains all eight
reference power spectra and each observation's per-cell comparisons.
Production source, API, confidence and `VERSION` (`1.0.1`) are unchanged;
no private music or mapping was accessed.

## Reproduction

Extract instrument commit `e9ad4a750b931cf7ede3f79d2285c44b9ced62e6` into a
clean Linux source directory. Retain/reproduce the pinned coverage export,
identifiability witnesses and F1 evidence. Set `source`, `coverage` and `native`
to those directories and use a fresh output prefix.

```sh
export OPENBLAS_NUM_THREADS=1
for name in phase_robustness within_cell identifiability partial_attribution; do
  python3 -m unittest discover -s "$source/tools" -p "test_apta_key_$name.py" -v
done
for b in default candidate sanitize; do
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 APTA_COVERAGE_PROBE="$native/$b/tests/apta_key_chroma_probe" python3 -m unittest discover -s "$source/tools" -p test_apta_key_coverage_diagnostic.py -v
done
python3 "$source/tools/apta_key_phase_robustness.py" --samples "$coverage/default.bin" --witnesses "$source/evidence/1.1/key-identifiability-20260911.json" --f1-evidence "$source/evidence/1.1/key-within-cell-f1-20260911.json" --source-commit e9ad4a750b931cf7ede3f79d2285c44b9ced62e6 --output-prefix result
```

Repeat once with prefix `repeat`, then compare aggregate/detail JSON exactly.
Resource files may differ in time. The run script and source archive hashes
are recorded publicly; no private audio is required.

## Next boundary

F2 is closed. The next justified research direction is a **coherent harmonic
representation that explicitly retains relative phase**, assessed under a
separate preregistration and a new deterministic phase bank frozen before its
implementation. The purpose is to model the terms that average power discards,
not to optimize F2's phases/weights against these four failures. This report
does not choose a solver, run that follow-up or claim it will succeed.

F1's fixed-phase separation remains evidence only at its stated scope. F2 does
not authorize a production port or opening music. H1, all six transfer
rejections, spent-data seals, unopened WP6/WP7, P4 physical acceptance and final
release freeze retain their existing status.
