# Partial-to-fundamental attribution H1 — 2026-09-11

**Rejected on the frozen local-chord gate.** H1 obtains 144/144 final synthetic
keys but only **84/96 missing-fundamental local chords**, below the required
89/96. No detector is retained, ported or promoted. No music corpus was opened,
and `VERSION` stays `1.0.1`. All six prior real-audio transfer rejections remain.

Protocol commit `edfbded` precedes implementation and evaluation. Instrument
source: `0182c99c3d8fe7a1810c03f5413ca66d34946bdf`; baseline:
`6cd9fa45779058aa8b36057180d2e8b9adfebd4b`. See the
[frozen protocol](APTA-1.1-KEY-PARTIAL-ATTRIBUTION-PROTOCOL.md) and
[public result, resource and validation JSON](../../evidence/1.1/key-partial-attribution-h1-20260911.json).

## Method and evidence boundary

The unchanged coverage export supplies 576 one-second windows from 144
I-IV-V-I progressions, covering all 24 keys and six conditions. This is already
observed synthetic development evidence, not fresh acceptance evidence.

H1 fits the same 36 octave-resolved FFT energy cells with a fixed dictionary
of 108 patterns: pure tone, fundamental plus h=2,3,4, and h=2,3,4 alone, for
each candidate MIDI 48..83. All weights are fixed by h^-2 and the existing
four-sample box response. No stimulus metadata reaches the fitting function.
Up to six greedy column selections each receive 32 cyclic nonnegative
coordinate sweeps. Recovered fundamental-equivalent energy then uses the
unchanged mean-log compression, ordered folding/accumulation and C selector.

The dictionary's timbres deliberately match the synthetic families. The result
therefore cannot demonstrate generalization even where it matches every final
key. This is approximate bounded fitting; convergence or unique source
identification was never a gate or an achieved claim.

## Complete decision matrix

All comparisons use the prior **mean-log** baselines, with unchanged ranking
and confidence. Local counts use the local chord as truth, including major V
in minor progressions; first/final counts use the progression's global key.

| Condition | Narrow local /96 | Dense local /96 | H1 local /96 | H1 first /24 | Narrow final /24 | Dense final /24 | H1 final /24 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Clean | 96 | 96 | 96 | 24 | 24 | 24 | 24 |
| +1/3 semitone | 45 | 96 | 94 | 23 | 8 | 24 | 24 |
| Fixed noise | 96 | 96 | 96 | 24 | 24 | 24 | 24 |
| -1/3 semitone | 47 | 96 | 96 | 24 | 12 | 24 | 24 |
| Fundamental plus harmonics | 96 | 96 | 96 | 24 | 24 | 24 | 24 |
| Missing fundamental | 89 | 66 | **84** | 21 | 24 | 22 | 24 |
| Total | 469 | 546 | 562 | 140 | 116 | 142 | 144 |

| Scope and baseline | Fixes | Breaks | Changed verdicts | H1 exact matches |
|---|---:|---:|---:|---:|
| Local vs narrow | 105 | 12 | 117 | 562/576 |
| Local vs dense | 19 | 3 | 22 | 562/576 |
| First vs narrow | 26 | 3 | 29 | 140/144 |
| First vs dense | 8 | 1 | 9 | 140/144 |
| Final vs narrow | 28 | 0 | 28 | 144/144 |
| Final vs dense | 2 | 0 | 2 | 144/144 |

The missing-fundamental local errors are all in the minor progression group:
major group 48/48, minor group 36/48. Each of the 12 errors chooses the relative
major (tonic three semitones above the expected minor chord), with confidence
32..42. Against narrow evidence that condition has seven fixes and 12 breaks;
against dense it has 19 fixes and one break. H1 also introduces two local
errors in the +1/3 condition. These are recorded despite correct final keys.

All reported local, first and final groups have zero confidence>=75 errors
and zero new confident errors. Synthetic confidence safety does not reverse
the 17 new confident errors in the rejected MTG comparison.

## Frozen gate decision

| Gate | Result | Outcome |
|---|---|---|
| First five conditions each final 24/24 | 120/120 | Pass |
| No final break vs dense | 0 | Pass |
| Missing-fundamental final 24/24 | 24/24 | Pass |
| Missing-fundamental local >=89/96 | **84/96** | **Fail** |
| No final break vs narrow | 0 | Pass |
| No new confident error vs either baseline | 0 in every group | Pass |
| Overall local no decrease vs dense | 546 -> 562/576 | Pass |
| Dictionary <=32 KiB | 31,104 bytes | Pass |
| Named numeric workspace <=64 KiB | Upper accounting 38,988 bytes | Pass |
| <=6 columns, <=672 coordinate updates/window | Max 6 and 672 | Pass |
| Attribution CPU <=60 seconds/576 windows | 2.230958 s; replay 2.305628 s | Pass |

The gates are conjunctive. **H1 is rejected**, even though its final aggregate
is perfect. No iteration, dictionary, order, confidence, label or threshold was
changed after seeing the matrix. The prescribed identity replay is the only
repeat, and no second variant was evaluated.

## Validation and implementation cost

- Eight new H1 tests pass: silence, isolated full/missing/pure patterns,
  mixtures, scaling and replay, no input mutation or metadata dependency,
  duplicate/disabled columns, bounded fitting, invalid inputs and gate vetoes.
- The existing 11 coverage tests pass separately against pinned default
  Release/Werror, I1 Release/Werror and I1 Debug ASan/UBSan native probes.
  These are reused native builds, not new full CTest/build-matrix claims.
- Every prior recorded default/I1 native executable and production key object
  hash is reverified, including the analyzer. Coverage tool/input/detail/report
  hashes match their frozen record. There are no production C/API edits.
- All 1,152 local/cumulative selector responses match between default and I1.
  Full detailed reports and deterministic aggregates replay byte-identically.
  Both run stderr files are empty. Timing is stored separately from identity.
- The unchanged FFT checks pass: maximum Parseval discrepancy
  `1.9324009725613172e-15` (limit `1e-12`); direct Fourier scaled discrepancy
  `2.3886985673487236e-12` (limit `1e-9`).
- Maximum residual reconstruction discrepancy is `1.4346826963272782e-16`
  and maximum scaled coordinate-objective increase is
  `1.1445923072610459e-16`, both below `1e-12`. Output is finite/nonnegative.
- Relative residual norm has median `0.003060949` and max `0.024014977`.
  Maximum scaled coordinate optimality violation is `0.012688456`; this
  explicitly does not establish convergence of the bounded solver.
- There are 12 disabled columns and 26 exact equal-column pairs after range
  truncation and normalization. These demonstrate dictionary ambiguities,
  but do not establish that they caused the observed chord errors.
- The first-window allocation replay measures 10,184 bytes of incremental
  Python/NumPy traced peak, excluding the prebuilt model. This is one allocation
  sample, not a full-process or all-window maximum. The separate named-array
  bound is 38,988 bytes. Neither is a P4 memory measurement.
- Production CPU/RAM/state delta is zero. The host fit costs about 2.23 CPU
  seconds for 576 windows, excluding FFT, selector calls and reporting; it is
  single-threaded with `OPENBLAS_NUM_THREADS=1`, under WSL Ubuntu/NumPy 2.5.2.

Raw local artifacts are in `build/key-partial-attribution-20260911/`:
`result-detail.json` contains each recovered spectrum, selected columns,
residual diagnostics, chroma, top-three keys/scores and confidence;
`result.json` and `result-resource.json` separate deterministic measurements
from runtime/allocation. Repeats, test logs, source archive and all hashes are
recorded in the public evidence JSON. These inputs require no private audio.

## Reproduction

Extract source commit `0182c99c3d8fe7a1810c03f5413ca66d34946bdf` to a clean
Linux source directory. Reproduce or retain the exact coverage artifacts and
native probes using [the prior result](APTA-1.1-KEY-COVERAGE-RESULT.md); H1
refuses mismatching hashes. Set `old`, `native` and `source` to those directories
and use a fresh output prefix. The actual run script and source archive are
hashed in the evidence record.

```sh
export OPENBLAS_NUM_THREADS=1
export ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
export UBSAN_OPTIONS=halt_on_error=1
python3 -m unittest discover -s "$source/tools" -p test_apta_key_partial_attribution.py -v
for b in default candidate sanitize; do
  APTA_COVERAGE_PROBE="$native/$b/tests/apta_key_chroma_probe" python3 -m unittest discover -s "$source/tools" -p test_apta_key_coverage_diagnostic.py -v
done
python3 "$source/tools/apta_key_partial_attribution.py" --samples "$old/default.bin" --coverage-detail "$old/detail.json" --coverage-summary "$old/summary.json" --validation "$source/evidence/1.1/key-coverage-validation-20260910.json" --probe "$native/default/tests/apta_key_chroma_probe" --i1-probe "$native/candidate/tests/apta_key_chroma_probe" --source-commit 0182c99c3d8fe7a1810c03f5413ca66d34946bdf --output-prefix result
```

Repeat only with output prefix `repeat`, then compare `result.json` and
`result-detail.json` with their repeat counterparts. Resource files may differ
in timing. Preserve every gate result; a failed gate is not permission to tune.

## Next boundary

H1 is closed. The next justified step is a **separately preregistered
identifiability diagnostic**: determine whether distinct fundamental/partial
configurations can be distinguished in the retained 36-cell evidence before
changing a fitter. Separate range/cell ambiguity from bounded fitting error
without modifying H1's dictionary, iterations or decision rules. The observed
relative-major errors and duplicate columns motivate that question, but neither
proves its answer. No such follow-up is executed in this result.

The causal scope remains synthetic: recovering plausible fundamental evidence
and accumulating four chords can give perfect final keys while losing local
minor identity. It does not establish the cause of remaining real-song errors.
WP6/WP7, new independent development evidence, P4 physical acceptance and final
release freeze remain open under their existing gates.
