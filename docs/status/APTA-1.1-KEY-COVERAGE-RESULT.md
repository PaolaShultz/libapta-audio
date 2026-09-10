# Tonal coverage and native ranking diagnostic — 2026-09-10

**Complete: synthetic coverage contribution supported; no candidate retained.**
Protocol commit `0ef7e6f` preceded instrumentation and every matrix run.
Instrument source is `c54fe694e79efac378e0904d7f5d3c2e44daa6f1`;
production baseline is `c81ab373bc554ed1df58d548aeb8377bcaf629f6`.
This completes the authorized diagnostic step 1. Production source, selector,
confidence, public API and `VERSION` (`1.0.1`) are unchanged. Both mean-key
options stay off. No music corpus or formal holdout was accessed.

## Scope and method

The frozen [protocol](APTA-1.1-KEY-COVERAGE-PROTOCOL.md) compares 144 synthetic
I-IV-V-I progressions: 24 tonic/mode combinations, six conditions, four seconds
at 48 kHz each. The C exporter records the exact 12,000 float four-sample
averages per second plus all 36 native coefficients. Each binary has 576
records and 27,740,168 bytes, accounting for 27,648,000 source samples.

The dense diagnostic sums squared magnitudes of a float64 rectangular 1-Hz
rFFT in 36 geometric semitone cells (C3–B5). The component oracle uses the
known synthesized partials and their box-average response in that same range;
it ignores finite-window leakage/cross terms, float rounding and injected
noise. It is ideal component knowledge, not an exact FFT target. A separate
fundamental oracle gives equal weight to the three intended chord tones,
even when their fundamentals are absent. Its results are compared with each
compression baseline; the fundamental oracle itself is not compressed.

Both existing compression paths are evaluated on each spectral source. Every
reference chroma goes through the actual unchanged C selector. Local results
are recomputed from the window's compressed bins, not by subtracting two
rounded cumulative chroma vectors. The original native delta rows remain
preserved for the 720-row compatibility gate. Local IV/V results use the local
chord (the minor progression's V is major); final results use the global key.

## Coverage evidence

Values below are medians across 96 windows per condition. L1 is the distance
between normalized 36-bin energy vectors and the component oracle; capture is
raw total energy divided by in-range oracle energy. In-range fraction refers
to all known component energy before dropping components outside C3–B5.

| Condition | Narrow L1 | Dense L1 | Narrow capture | Dense capture | In-range component energy |
|---|---:|---:|---:|---:|---:|
| clean | 0.003341 | 0.017307 | 1.000580 | 0.999490 | 1.000000 |
| plus-third | 0.765511 | 0.049935 | 0.003013 | 0.997833 | 1.000000 |
| noise | 0.003231 | 0.017691 | 1.000281 | 0.999137 | 1.000000 |
| minus-third | 0.791062 | 0.053772 | 0.002731 | 0.999343 | 1.000000 |
| harmonics | 0.101849 | 0.029826 | 0.949066 | 0.999210 | 0.971499 |
| missing-fundamental | 0.334762 | 0.066990 | 0.800077 | 1.000769 | 0.903544 |

The preregistered coverage criterion passes in **both** detuned conditions.
Native capture falls to about 0.30% (+1/3) and 0.27% (-1/3), while dense capture
is about 99.8% and 99.9%. Dense normalized L1 is also much lower in both.
This is a synthetic sensitivity to energy between the fixed narrow probes.
Clean/noisy narrow energy has lower L1 than the dense reference, which carries
finite-window leakage and integrates a different noise bandwidth. Capture
slightly above one is possible; the oracle omits those effects.

## Decisions and remaining representation limits

Final exact tonic-and-mode matches; every cell has denominator 24.

| Condition | Absolute narrow | Absolute dense | Absolute component oracle | Mean narrow | Mean dense | Mean component oracle |
|---|---:|---:|---:|---:|---:|---:|
| clean | 15 | 12 | 24 | 24 | 24 | 24 |
| plus-third | 6 | 11 | 24 | 8 | 24 | 24 |
| noise | 14 | 12 | 24 | 24 | 24 | 24 |
| minus-third | 6 | 12 | 24 | 12 | 24 | 24 |
| harmonics | 21 | 14 | 24 | 24 | 24 | 24 |
| missing-fundamental | 18 | 13 | 13 | 24 | 22 | 21 |

The fundamental oracle is 24/24 in every condition and 96/96 for every local
chord group. That demonstrates selector compatibility with these ideal triads,
not an ability to infer the absent fundamentals from a real recording.

Under mean normalization, dense evidence yields 142/144 final matches versus
narrow 116/144: **28 fixes, two breaks, 30 changed verdicts**. The detuned cases
become 24/24 for each direction (12/12 major and 12/12 minor). Both breaks are
minor missing-fundamental progressions: dense gives major 12/12, minor 10/12.
Even the component oracle misses three of those 24 progressions (21/24),
despite knowing the full in-range partial energy exactly by construction.

Under absolute log compression, dense evidence gives 74/144 versus narrow
80/144: **16 fixes, 22 breaks, 56 changed verdicts**. On clean signals dense
falls from 15/24 to 12/24, with all 12 errors being mode-only; the component
oracle remains 24/24. Better coverage by itself therefore does not repair the
compression/folding/profile interaction. No parameter or confidence rescue
was tried.

There are **zero confidence>=75 stimulus mismatches** in every reported
local/first/final group, and therefore no new such mismatch. These easy,
constructed stimuli do not establish confidence safety on music and do not
reverse the rejected MTG result with 17 new confident errors.

Local / first-window / final match counts have denominators 96 / 24 / 24.

| Condition | Mean narrow local / first / final | Mean dense local / first / final | Mean component oracle local / first / final |
|---|---|---|---|
| clean | 96 / 24 / 24 | 96 / 24 / 24 | 96 / 24 / 24 |
| plus-third | 45 / 12 / 8 | 96 / 24 / 24 | 96 / 24 / 24 |
| noise | 96 / 24 / 24 | 96 / 24 / 24 | 96 / 24 / 24 |
| minus-third | 47 / 13 / 12 | 96 / 24 / 24 | 96 / 24 / 24 |
| harmonics | 96 / 24 / 24 | 96 / 24 / 24 | 96 / 24 / 24 |
| missing-fundamental | 89 / 20 / 24 | 66 / 13 / 22 | 66 / 13 / 21 |

Aggregation helps the missing-fundamental dense/component cases (13 first
matches become 22/21 final), but does not eliminate their errors. In detuned
narrow mean-normalized cases it reduces matches (12 -> 8 and 13 -> 12).
Thus neither accumulation nor known partial energy alone guarantees the
intended chord/key decision. The full aggregate JSON also separates tonic-only,
mode-only and joint errors, changes, fixes/breaks and confidence counts by mode.

## Instrument validation and provenance

- Default and I1 Release builds pass warnings-as-errors; I1 Debug runs with
  ASan/UBSan. Eleven host tests pass separately against all three native probes.
- All original 720 rows per build are identical; the separately generated
  original gain-zero reports remain byte-identical to their earlier baselines.
- Both 1,296-row reports replay byte-identically; the 576-record sample and
  coefficient binaries are identical across default, I1, repeats and sanitizer.
  The I1 sanitizer JSON is identical to Release and all stderr files are empty.
- All 576 native cumulative chroma vectors per build and every compressed bin
  reconstruct bit-identically using host `logf` and ordered float32 arithmetic.
- All 8,064 C selector requests match between default/I1; the 1,152 native
  cumulative selections, candidates, scores and confidence match their original
  C report rows exactly. Detailed and aggregate Python reports replay identically.
- Worst Parseval relative discrepancy is `1.9324009725613172e-15` (limit
  `1e-12`); worst direct sine/cosine coefficient scaled discrepancy is
  `2.3886985673487236e-12` (limit `1e-9`). Silence, impulse, integer-bin tone,
  exact cell edges and out-of-range exclusion pass. Malformed, truncated,
  reordered and nonfinite exports/probe inputs are rejected.
- Production analyzer, native key object and I1 cost object hashes are unchanged
  from the prior cost-I1 evidence. CPU/RAM/state change in production is zero;
  the 48,000-byte export sample buffer and NumPy FFT memory are host-only costs.
- No full CTest matrix or P4 measurement is newly claimed: this change affects
  only explicit diagnostic targets/tools, with production byte identity checked.

The environment is Ubuntu WSL x86-64, GCC 13.3.0, CMake 3.28.3 and NumPy 2.5.2.
Exact binary, source-archive, tool, input, output and log hashes are in the
[validation record](../../evidence/1.1/key-coverage-validation-20260910.json);
the [aggregate results](../../evidence/1.1/key-coverage-20260910.json) contain
the fixed matrix and all group scores. Local `build/key-coverage-20260910/`
holds raw exports, repeated reports and the 8,064-row detailed ranking report
with chroma, top-three keys/scores and confidence. No private audio or mappings
are needed to reproduce these artifacts.

Two orchestration corrections preceded interpretation: shell variable quoting
failed before configuration, so commands moved into a script file; an extra
hash check incorrectly demanded that the *edited test executable* remain
unchanged (its assertion line numbers changed). That check was corrected to
the frozen gates: identical original output rows and unchanged production
bytes. Both pass. No spectral tolerance, stimulus, scoring rule or scientific
gate changed after observing results.

## Reproduction

Extract `git archive c54fe694e79efac378e0904d7f5d3c2e44daa6f1` into a clean
Linux `source` directory. Use a fresh output directory: the C exporter and
Python writer refuse overwrite. Commands below run from the build parent.

```sh
cmake -S source -B default -DCMAKE_BUILD_TYPE=Release -DAPTA_WARNINGS_AS_ERRORS=ON
cmake -S source -B candidate -DCMAKE_BUILD_TYPE=Release -DAPTA_WARNINGS_AS_ERRORS=ON -DAPTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON -DAPTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY_COST_I1=ON
cmake -S source -B sanitize -DCMAKE_BUILD_TYPE=Debug -DAPTA_WARNINGS_AS_ERRORS=ON -DAPTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON -DAPTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY_COST_I1=ON -DAPTA_ENABLE_SANITIZERS=ON
for b in default candidate sanitize; do
  cmake --build "$b" --target apta_key_coverage_diagnostic apta_key_chroma_probe apta_key_gain_diagnostic apta_analyze -j 4
  APTA_COVERAGE_PROBE="$PWD/$b/tests/apta_key_chroma_probe" OPENBLAS_NUM_THREADS=1 python3 -m unittest discover -s source/tools -p test_apta_key_coverage_diagnostic.py -v
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 "$b/tests/apta_key_coverage_diagnostic" --json --samples "$b.bin" > "$b.json"
done
for b in default candidate; do
  "$b/tests/apta_key_gain_diagnostic" --json --gain-shift 0 > "$b-legacy.json"
  "$b/tests/apta_key_coverage_diagnostic" --json --samples "$b-repeat.bin" > "$b-repeat.json"
  cmp "$b.bin" "$b-repeat.bin"
  cmp "$b.json" "$b-repeat.json"
done
cmp default.bin candidate.bin
cmp candidate.bin sanitize.bin
cmp candidate.json sanitize.json
OPENBLAS_NUM_THREADS=1 python3 source/tools/apta_key_coverage_diagnostic.py --default-samples default.bin --i1-samples candidate.bin --default-report default.json --i1-report candidate.json --default-legacy default-legacy.json --i1-legacy candidate-legacy.json --probe "$PWD/default/tests/apta_key_chroma_probe" --i1-probe "$PWD/candidate/tests/apta_key_chroma_probe" --source-commit c54fe694e79efac378e0904d7f5d3c2e44daa6f1 --summary summary.json --detail detail.json
```

Repeat the last command with new output names and compare both reports. Match
the production binaries/objects and legacy gain-zero reports to the hashes in
the validation record. Do not reinterpret a run before every identity gate passes.

## Next research boundary

Preregister one bounded **harmonic-to-fundamental evidence representation**
experiment that preserves octave information until partial attribution, with
the existing ranking/confidence fixed. It must preserve the detuned coverage
gain while testing the missing-fundamental regressions against both narrow and
dense references. This result selects the question, not a frontend, harmonic
weight, threshold, resource budget or production candidate. Those must be
frozen before the next experiment; no new implementation is made here.

The causal statement is limited to these constructed signals: narrow frequency
coverage loses detuned evidence, and broader partial-energy coverage alone does
not ensure intended fundamental/key identity after compression and folding.
It does **not** establish the cause of remaining real-song errors. All six key
transfer rejections, spent-corpus boundaries, unopened WP6/WP7 gates and P4
physical acceptance requirements remain in force.
