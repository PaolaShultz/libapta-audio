# Within-cell frequency structure F1 — 2026-09-11

**Complete: all eight fixed-reference pairs satisfy the frozen fine-structure
separation criterion.** After independently normalizing each occupied cell's
power distribution, distance to the alternative is 0.238..0.516, versus
1.76e-9..3.59e-9 to the known-source float64 reference. The criterion passes
8/8 at the existing one-second, 12-kHz, unpadded 1-Hz FFT resolution.

This supports retaining within-cell information for these four distinct ideal
spectra and their eight fixed-phase windows. It is not phase robustness,
source uniqueness, a new detector, key-accuracy improvement or music acceptance.
H1 remains rejected. No production source, API, confidence, version or corpus
was changed; `VERSION` remains `1.0.1`.

Protocol commit `db5559e` preceded instrument commit
`64379ebf78d8e7f0804ae53653c3382f47ac4b8a` and execution. Baseline:
`31d3d9245a919d0db53a01abe6e9eaec8a068878`. See the
[frozen protocol](APTA-1.1-KEY-WITHIN-CELL-PROTOCOL.md) and
[public aggregate/validation/resource record](../../evidence/1.1/key-within-cell-f1-20260911.json).

## Fixed comparison

Only the eight previously published <=6-column ambiguity pairs are used.
Actual observations are the unchanged exported C float PCM. The known-source
reference recreates the three missing-fundamental notes with h=2,3,4, including
out-of-range partials. The alternative recreates the published pure-tone
coefficient vector at nominal cell-center frequencies. Both use the original
absolute-frame sine phase, with no phase fitting, sweep, padding or new window.

The prior equal-energy result concerned an **ideal additive cell model**.
These actual finite-window waveform references have different coarse cell
totals: normalized coarse L1 is 0.00297..0.09135. Consequently this experiment
does not establish that coarse evidence alone cannot distinguish these actual
references. Its narrower question is whether separation remains after those
cell-total differences are deliberately removed. It does.

For every positive-energy ideal cell, each actual/reference rFFT power vector
is normalized to unit sum inside that cell. The L1 distances are averaged
using the already published ideal cell-energy proportions. Independent positive
rescaling of cell totals cannot affect this score; a dedicated test verifies
that invariance. All FFT bins outside C3–B5 are excluded from the score.

`Dtrue` is actual C PCM versus the known-source float64 reference; `Dalt` is
actual C PCM versus the alternative. Every pair must satisfy
`Dalt > 100*Dtrue + 1e-9`. Dtrue measures reconstruction/rounding discrepancy,
not realistic noise, unknown phase or a statistical confidence interval.

## Complete eight-pair result

IDs are `[global tonic, global mode, condition, window]`, with major=0/minor=1.
The repeats of local chords account for four distinct ideal spectra, not eight
independent musical examples.

| ID | Dtrue | Dalt | Required margin | Coarse actual/alternative L1 | Pass |
|---|---:|---:|---:|---:|---|
| [5,1,5,2] | 2.467e-9 | 0.305995 | 2.477e-7 | 0.043937 | Yes |
| [6,1,5,2] | 2.056e-9 | 0.419141 | 2.066e-7 | 0.002967 | Yes |
| [7,1,5,2] | 1.994e-9 | 0.397340 | 2.004e-7 | 0.026053 | Yes |
| [8,1,5,2] | 2.845e-9 | 0.516096 | 2.855e-7 | 0.028405 | Yes |
| [10,1,5,1] | 3.121e-9 | 0.256280 | 3.131e-7 | 0.091354 | Yes |
| [10,1,5,4] | 3.586e-9 | 0.237807 | 3.596e-7 | 0.012772 | Yes |
| [11,1,5,1] | 2.327e-9 | 0.465196 | 2.337e-7 | 0.073039 | Yes |
| [11,1,5,4] | 1.761e-9 | 0.384834 | 1.771e-7 | 0.067006 | Yes |

The first pair illustrates information discarded by cell integration. Its
missing-fundamental source contains a third harmonic at 699.245642 Hz and a
second harmonic at 698.456463 Hz in the same MIDI-77 cell. The pure alternative
represents that cell at 698.456463 Hz. In the actual fixed-phase FFT the peak
bin is 699 Hz, versus 698 Hz for the alternative. Another occupied cell contains
the third harmonic at 831.547893 Hz, versus nominal center 830.609395 Hz.

| First pair cell MIDI | Actual peak bin | Alternative peak bin | Within-cell L1 |
|---|---:|---:|---:|
| 70 | 466 Hz | 466 Hz | 0.002038 |
| 73 | 554 Hz | 554 Hz | 0.000547 |
| 77 | 699 Hz | 698 Hz | 0.568663 |
| 80 | 832 Hz | 831 Hz | 0.983925 |
| 82 | 932 Hz | 932 Hz | 0.035644 |

This is a concrete feature of these measured/reference distributions, not a
frequency estimator or a rule to infer fundamentals. Relative phases, coherent
cross terms, finite-window leakage and out-of-range partial leakage can also
affect the distributions. The experiment did not isolate their contributions
or prove that the third-harmonic offset alone explains every separation.

## Correctness and resource checks

- Six new F1 tests pass: identical spectra, cell-gain invariance, changed shape
  at equal cell totals, ordered float32 averaging, reference replay, invalid/
  silent scores, FFT checks and exact margin boundary.
- Ten identifiability and eight H1 tests pass unchanged. Eleven coverage tests
  pass against each reused default Release/Werror, I1 Release/Werror and
  I1 Debug ASan/UBSan native probe. No native code was edited or key reranked;
  this is not a new full build/CTest or physical-device qualification.
- Coverage export and imported coverage/H1 sources match their pinned hashes.
  All eight witnesses have unique ordered IDs and four distinct ideal spectra.
  Both physical coefficient vectors reproduce their published ideal spectrum
  within the frozen relative L2 tolerance of 1e-12.
- Known-source reconstruction followed by original ordered float32 averaging
  actually matches the exported C samples exactly in all eight windows here:
  relative L2 and maximum absolute discrepancy both zero. The protocol required
  only <=1e-6; no tolerance was tightened or generalized to other hosts.
- All 24 FFT computations pass: maximum Parseval discrepancy
  `1.3355548180719243e-15` (limit `1e-12`), maximum direct Fourier discrepancy
  `1.4694758622246425e-12` (limit `1e-9`). Powers and scores are finite.
- Complete aggregate and detail reports replay byte-identically. Both stderr
  files are empty; no scientific/correctness threshold was altered.
- Analysis CPU is 0.197883 seconds, replay 0.185854 seconds, below the 30-second
  host gate. First known-reference incremental traced peak is 1,539,864 bytes,
  excluding other retained arrays and the full report. This single-call host
  sample is not a total/P4 memory budget. Production CPU/RAM/state delta is zero.
- Runtime is WSL Ubuntu with NumPy 2.5.2 and `OPENBLAS_NUM_THREADS=1`.

The public JSON records all eight coarse/fine distances, ratios, reconstruction
errors, source/protocol/archive/input/output/log hashes and resources. Local
`build/key-within-cell-20260911/result-detail.json` contains the per-cell power
distributions, ideal weights, peak bins, all partial frequencies/offsets and
retained/out-of-range markers. No private audio or mappings are required.

## Reproduction

Extract `64379ebf78d8e7f0804ae53653c3382f47ac4b8a` into a clean Linux source
directory. Retain or reproduce the pinned coverage export and identifiability
witnesses from their result documents. Set `source`, `coverage` and `native`
to those directories. Use a fresh output prefix; overwrites are rejected.

```sh
export OPENBLAS_NUM_THREADS=1
for name in within_cell identifiability partial_attribution; do
  python3 -m unittest discover -s "$source/tools" -p "test_apta_key_$name.py" -v
done
for b in default candidate sanitize; do
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 APTA_COVERAGE_PROBE="$native/$b/tests/apta_key_chroma_probe" python3 -m unittest discover -s "$source/tools" -p test_apta_key_coverage_diagnostic.py -v
done
python3 "$source/tools/apta_key_within_cell.py" --samples "$coverage/default.bin" --witnesses "$source/evidence/1.1/key-identifiability-20260911.json" --source-commit 64379ebf78d8e7f0804ae53653c3382f47ac4b8a --output-prefix result
```

Repeat with prefix `repeat`, compare aggregate/detail JSON byte-for-byte, and
keep resource timing separate. The actual run script and source archive are
hashed in the public record.

## Next boundary

Preregister **phase robustness of within-cell evidence** on these fixed
alternatives before designing a frontend. The present separation relies on
explicit known phases; the next question is whether within-cell structure
still separates references when component phases are unknown. Freeze that
study's phase construction, score, resource bound and rejection rule before
execution. No phase sweep or new candidate is run here.

This result does not remove ambiguity for arbitrary timbre, noise, tuning,
polyphony or range truncation, and does not reverse H1 or any of the six music
transfer rejections. Independent development evidence, unopened WP6/WP7 gates,
physical ESP32-P4 acceptance and release freeze remain outstanding.
