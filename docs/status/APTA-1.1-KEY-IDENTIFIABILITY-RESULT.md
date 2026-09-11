# Tonal evidence identifiability — 2026-09-11

**Diagnostic complete: the retained ideal cell model permits different
fundamental/key interpretations. H1 remains rejected.** There are 30
missing-fundamental window pairs with equal ideal spectral energy and different
local key interpretations; eight pairs (four distinct spectra) satisfy H1's
six-column cap on both sides. A known-note support fit improves the actual
FFT residual in **0/576** windows, including **0/14** H1 local errors.

These are ideal-model counterexamples and labeled diagnostic fits, not a new
detector, a convergence proof, identical PCM or a real-song causal claim.
Production source, profiles, confidence, public API and `VERSION` (`1.0.1`)
remain unchanged. No music corpus or holdout was accessed.

Protocol commit `e70185c` preceded instrument commit
`3d5d005b18ff688f9edf33dbbbdf2e3f859ac320` and all matrix runs. Baseline:
`220f203759d54ea9c98a2fe843b0646eda757998`. See the
[frozen protocol](APTA-1.1-KEY-IDENTIFIABILITY-PROTOCOL.md) and the
[public aggregate with eight explicit witnesses](../../evidence/1.1/key-identifiability-20260911.json).

## What was held fixed

The experiment imports the unchanged H1 dictionary and coverage FFT, mean-log
compression, folding and native C selectors. Inputs are the pinned 576 PCM
windows, prior coverage details and original H1 coefficients/verdicts. No H1
fit, threshold, iteration count or verdict was changed.

For the 288 nominal clean/full-harmonic/missing-fundamental windows, two physical
coefficient vectors are constructed: the three known source notes with the
known harmonic family, and pure tones that reproduce each occupied spectral
cell. Both yield the same ideal cell-energy vector, within the frozen numerical
tolerance. Each coefficient vector implies its own fundamental evidence;
that inferred evidence, after identical processing, can yield a different C
key selection. The C selector itself is deterministic: it receives different
fundamental chroma, not two conflicting decisions on the same chroma.

The known-source witness uses stimulus metadata by design and is not available
to an estimator. Its pure-tone alternative replaces physical partial locations
inside a cell by that cell's nominal equal-tempered center, matching the cell
integral rather than the actual waveform or unintegrated spectrum.

## Exact-model ambiguity

| Condition | Window pairs | Known-source chord matches | Pure-component chord matches | Different interpretations | Both <=6 columns | Different interpretations with both <=6 |
|---|---:|---:|---:|---:|---:|---:|
| Clean | 96 | 96 | 96 | 0 | 96 | 0 |
| Fundamental plus harmonics | 96 | 96 | 96 | 0 | 19 | 0 |
| Missing fundamental | 96 | 96 | 66 | 30 | 53 | **8** |

All 30 differences are joint tonic/mode errors relative to the known chord;
none reaches confidence 75. Eight window pairs satisfy the six-column cap and
contain no invisible source note. Repeated chords across the fixed progression
give four distinct counterexample spectra; these are not eight independent
musical examples. All eight imply minor versus relative major.

One explicit example is stimulus ID `[5,1,5,2]`: the IV chord of the synthetic
F-minor missing-fundamental progression. The known physical sources are MIDI
58,61,65 (B-flat, D-flat, F), each using h=2,3,4 with coefficient 810,000.
The alternative uses five pure-tone sources, all inside the same retained
C3–B5 range:

| Alternative pure-tone MIDI | Physical coefficient | Resulting cell energy |
|---|---:|---:|
| 70 | 202500.00000000003 | 201559.1774115013 |
| 73 | 202500.0 | 201170.46737174015 |
| 77 | 292497.86868898483 | 289453.94257651846 |
| 80 | 89996.98290971133 | 88674.69010193134 |
| 82 | 50625.0 | 49689.242808058654 |

The same five cell energies arise from the three missing-fundamental sources;
relative spectrum discrepancy is `1.5931201937337162e-16`. The known-source
fundamental interpretation selects B-flat minor (confidence 48); the pure-tone
interpretation selects D-flat major (confidence 32). All coefficients, occupied
cells and top-three scores for this and the other seven pairs are public.
No uniqueness preference based on fewer notes was added.

The dictionary also contains **26 exact duplicate normalized-column pairs**,
all sharing pitch class. Those pairs concern octave/timbre ambiguity and do
not by themselves prove the observed minor/relative-major confusion. Separately,
12 dictionary columns are completely out of range. Four missing-fundamental
windows contain a known source note with such a zero column (the fifth of
the V chord in the two highest-root progressions, for both modes). Its amplitude
cannot be recovered from a zero column in this ideal retained-range model.
These four windows are distinct from the eight <=6-column key counterexamples.

## Known-support residual comparison

For each actual dense spectrum, the diagnostic supplies the three known
note/family columns at their unchanged nominal frequencies. It enumerates all
eight active subsets and keeps the feasible nonnegative fit with lowest actual
squared residual. This is label-selected diagnostic information, not a global
108-column solver or a replacement H1 candidate.

Strict improvement requires normalized squared residual reduction greater
than `1e-12`. H1 residuals are independently reconstructed from its original
recorded coefficients. The comparison does not rank new keys or alter H1.

| Condition | Windows | H1 local errors | Known-support strict improvements | Improvements among H1 errors | Median H1 normalized squared residual | Median known-support residual |
|---|---:|---:|---:|---:|---:|---:|
| Clean | 96 | 0 | 0 | 0 | 0.000003295 | 0.000033458 |
| +1/3 semitone | 96 | 2 | 0 | 0 | 0.000015117 | 0.000471107 |
| Noise | 96 | 0 | 0 | 0 | 0.000003338 | 0.000034124 |
| -1/3 semitone | 96 | 0 | 0 | 0 | 0.000018132 | 0.000643982 |
| Harmonics | 96 | 0 | 0 | 0 | 0.000016187 | 0.000803226 |
| Missing fundamental | 96 | 12 | 0 | 0 | 0.000003933 | 0.000204951 |

Thus this fixed witness does **not** establish a lower-residual alternative
to H1 in any window. It also does not prove H1's global optimality: the oracle
support is restricted to three nominal columns, while H1 can use six columns
to explain finite-window leakage, detuning and model mismatch. What is observed
is that known source-note identity need not have the lowest spectral fitting
error under this model. More residual minimization alone is not justified as
the next route to correct local minor identity.

## Instrument validation and costs

- Ten new identifiability tests and eight unchanged H1 regression tests pass.
  Eleven coverage tests also pass against each of default Release/Werror,
  I1 Release/Werror and I1 Debug ASan/UBSan probes. Native builds are reused;
  no new full CTest/build or P4 qualification is claimed.
- Pinned coverage/H1 source files, PCM, detailed/aggregate reports, both native
  probes and every prior production binary/object hash verify unchanged.
- Exactly 288 witness pairs, 576 support comparisons and 576 local C requests
  complete. Default/I1 selector outputs agree; all 288 pure-witness local
  results match the previous component-oracle results, including top-three
  candidates/scores and confidence.
- Maximum witness equality error is `1.7026263256542928e-16`, below `1e-12`.
  Maximum discrepancy from recorded H1 relative residual is
  `5.160802341031001e-17`, below `1e-12`.
- Unchanged FFT checks pass: Parseval max `1.9324009725613172e-15` (limit
  `1e-12`), direct Fourier max `2.3886985673487236e-12` (limit `1e-9`).
- Complete aggregate/detail reports replay byte-identically; both stderr files
  are empty. No correctness failure or scientific threshold change occurred.
- Single-thread analysis uses 1.197256 process CPU seconds; replay 1.153214 s,
  both below 120 s. First support-call incremental traced peak is 13,716 bytes,
  excluding the prebuilt model and full reports. This is one allocation sample,
  not a whole-process/all-window peak or a P4 budget. Production CPU/RAM/state
  delta is zero. Runtime is WSL Ubuntu, NumPy 2.5.2, `OPENBLAS_NUM_THREADS=1`.

The public JSON contains source/protocol/archive/input/output/log hashes,
condition/mode groups, column inventory, eight compact counterexamples and
resource records. Local `build/key-identifiability-20260911/result-detail.json`
retains every witness coefficient vector and all 576 support comparisons,
including unchanged H1 results. No private audio or mappings are involved.

## Reproduction

Extract instrument commit `3d5d005b18ff688f9edf33dbbbdf2e3f859ac320` into
a clean Linux source directory. Retain or reproduce the pinned coverage and
H1 artifacts following their result documents. Set `source`, `coverage`, `h1`
and `native` to those directories. Use a fresh output prefix; overwrite and
hash mismatches are rejected.

```sh
export OPENBLAS_NUM_THREADS=1
python3 -m unittest discover -s "$source/tools" -p test_apta_key_identifiability.py -v
python3 -m unittest discover -s "$source/tools" -p test_apta_key_partial_attribution.py -v
for b in default candidate sanitize; do
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 APTA_COVERAGE_PROBE="$native/$b/tests/apta_key_chroma_probe" python3 -m unittest discover -s "$source/tools" -p test_apta_key_coverage_diagnostic.py -v
done
python3 "$source/tools/apta_key_identifiability.py" --samples "$coverage/default.bin" --coverage-detail "$coverage/detail.json" --h1-detail "$h1/result-detail.json" --h1-summary "$h1/result.json" --h1-evidence "$source/evidence/1.1/key-partial-attribution-h1-20260911.json" --probe "$native/default/tests/apta_key_chroma_probe" --i1-probe "$native/candidate/tests/apta_key_chroma_probe" --native-root "$native" --source-commit 3d5d005b18ff688f9edf33dbbbdf2e3f859ac320 --output-prefix result
```

Repeat with prefix `repeat` and compare aggregate/detail JSON byte-for-byte.
Timing stays in separate resource files. The actual run script and source
archive hashes are recorded in the evidence JSON.

## Next research boundary

Preregister a diagnostic retaining **within-cell frequency structure** from
the already available unintegrated FFT, before summing energy into semitone
cells. Test whether it can distinguish these fixed ideal-model alternatives
at the actual one-second resolution and float PCM precision. This changes the
evidence question, not H1's fitting iterations or a confidence threshold.
No such follow-up is executed here and no production frontend is selected.

Range truncation remains a separate observed limitation. These findings do not
prove that finer frequency information resolves every ambiguity or real-song
error. H1 stays rejected; all six transfer rejections, spent-data boundaries,
unopened WP6/WP7 gates, physical P4 acceptance and release freeze remain intact.
