# Coherent frequency-uncertainty screen C2 — 2026-09-12

**Rejected under the frozen combined gates: only 50/1024 perturbed cases pass.**
Quarter-Hz errors preserve the correct family ranking in all 768 cases, but
every correct hypothesis leaves more than the allowed 10% residual energy.
Nearest-Hz rounding gives 32 family reversals and 206 residual-ceiling failures
in 256 cases; those counts overlap. Rounded out-of-range columns also expose
a numerical limitation of the unchanged C1 normalization, detailed below.

The exact control remains 256/256 and reproduces C1 scores bit-for-bit. C1's
supplied-exact-frequency result is not withdrawn. This experiment rejects the
finite frequency-error screen for that fixed construction; it does not measure
key accuracy, authorize a native port or select a frequency estimator.

Protocol `f75e349` preceded instrument
`f0698190f4f330d42629f67c8a16a2d8dcbc9fbc` and all runs. Baseline:
`8ae4e4ec8a4b9c713ea69653fd2e6e98ab5bb7c6`. See the
[frozen protocol](APTA-1.1-KEY-FREQUENCY-UNCERTAINTY-PROTOCOL.md) and
[public score, matrix and validation record](../../evidence/1.1/key-frequency-uncertainty-c2-20260912.json).

## Fixed experiment

All 256 existing C1 observations are reused, unchanged in waveform, float
rounding, amplitudes and phases. Only the supplied frequencies in both candidate
matrices change: exact, -0.25 Hz, +0.25 Hz, independent hash-selected +/-0.25 Hz
per component, and positive-frequency nearest-Hz rounding via `floor(f+0.5)`.
This yields 1280 cases and 40 matrices. Reusing the phase bank isolates frequency
hypothesis error; it is already observed synthetic development evidence.

The C1 matrix builder, retained bins, SVD cutoff `rcond=1e-12`, column
normalization, pseudoinverse and residual objective are imported unchanged.
No frequency search, amplitude prior, noise, tuning, phase-bank expansion or
solver adjustment was made. Source hashes match across all five conditions.

Perturbed cases require both wrong residual > correct residual +1e-6 and
correct residual <=0.10. That 10% diagnostic reconstruction ceiling was frozen
before coding; it is not a music/noise acceptance bound and does not replace
C1's exact-frequency <=1e-10 gate. Ranking failures and reconstruction failures
must be read separately.

## Complete condition results

| Supplied-frequency condition | Cases | Both gates pass | Ranking reversals | Residual-ceiling failures | Max correct residual | Minimum signed margin |
|---|---:|---:|---:|---:|---:|---:|
| Exact control | 256 | 256 | 0 | 0 | 3.309e-16 | 0.105737189 |
| All -0.25 Hz | 256 | 0 | 0 | 256 | 0.192940447 | 0.018912000 |
| All +0.25 Hz | 256 | 0 | 0 | 256 | 0.201238009 | 0.055020119 |
| Independent +/-0.25 Hz | 256 | 0 | 0 | 256 | 0.201715036 | 0.026728010 |
| Nearest Hz | 256 | 50 | 32 | 206 | 0.355728960 | -0.062157452 |

There are no margin ties. In the quarter-Hz cases, correct residual ranges are
0.11555..0.19294, 0.12392..0.20124 and 0.11776..0.20172 respectively. These
conditions therefore fail only the preregistered reconstruction ceiling, while
their family discrimination remains correct. Do not describe them as 768 wrong
source selections. Across all perturbed cases 992/1024 rankings remain correct;
974/1024 fail the combined screen, with 50 passing both gates.

The reconstruction cost is consistent with mismatch between a one-second
coherent template and supplied frequencies, but this finite screen does not
establish a universal frequency-error bound or an estimator precision target.
No smaller error was tried after seeing the failure.

## Nearest-Hz groups and numerical limitation

| Fixture | Generating family | Both gates pass /32 | Ranking reversals | Reconstruction failures | Median correct residual |
|---|---|---:|---:|---:|---:|
| 0 | Known harmonics | 0 | 0 | 32 | 0.245150431 |
| 0 | Pure alternative | 0 | 32 | 32 | 0.354155189 |
| 1 | Known harmonics | 18 | 0 | 14 | 0.098635091 |
| 1 | Pure alternative | 32 | 0 | 0 | 0.095812392 |
| 2 | Known harmonics | 0 | 0 | 32 | 0.147506577 |
| 2 | Pure alternative | 0 | 0 | 32 | 0.134285229 |
| 3 | Known harmonics | 0 | 0 | 32 | 0.290516192 |
| 3 | Pure alternative | 0 | 0 | 32 | 0.316532304 |

The 32 reversals all concern fixture 0's pure source, which the implemented
rounded fit ranks as the known-harmonic alternative. However, these nearest-Hz
results have an additional numerical qualification, anticipated in the protocol.

At integer frequencies outside the retained range, an ideal one-second FFT
has no retained-bin support from the isolated tone. The implemented wave/FFT
arithmetic leaves tiny remnants: known-family raw column norms reach
`1.369971390614671e-10`, compared with roughly 6000 for visible unit tones.
Normalizing these remnants to unit norm turns roundoff into freely fitted
directions. Physical sine/cosine coefficients then reach approximately
`2.6790380423378903e11` in magnitude. Those amplitudes are not meaningful
source reconstructions. All rounded models still report full normalized rank
and small condition numbers, illustrating why normalized rank alone does not
validate physical observability.

The 32 reversals are reproducible outputs of the **unchanged implementation**,
not a clean estimate of physical source ambiguity or evidence that those
out-of-range frequencies are observable. No column floor, pruning, amplitude
bound or solver rescue was added here. Quarter-Hz reconstruction failures
already reject the combined screen independently of the nearest-Hz cases.
The normalization issue must be addressed under a separate protocol before
using rounded templates as a reliable frequency-estimation baseline.

## Instrument gates, tests and costs

- Seven new tests pass: exact/no-mutation behavior, both signed shifts,
  independent hash sign/replay, nearest-Hz ties, shifted-frequency mismatch,
  source/phase reuse, separate gate boundaries and invalid constructions.
- Eight C1, six F2, six F1, ten identifiability and eight H1 tests pass unchanged.
  Eleven coverage tests pass against each reused default Release/Werror,
  I1 Release/Werror and I1 Debug ASan/UBSan probe. These are host/diagnostic
  regressions, not new full build/CTest or physical P4 qualification.
- All original 256 C1/F2-new-bank rows, original 256 F2 rows and eight F1 controls
  replay exactly. The newly computed exact-condition coherent residuals,
  phase hashes and rounding metrics also match C1 bit-for-bit.
- All 256 source PCM hashes match across all five conditions. No observation
  was altered along with its hypothesis. Imported sources/inputs are hash-pinned.
- Maximum independent least-squares prediction discrepancy is
  `2.2080277071275097e-14` (limit `1e-10`). This checks arithmetic consistency,
  not physical validity of near-zero normalized columns.
- Maximum Parseval error is `1.935966130825505e-15` (limit `1e-12`); direct
  Fourier error is `1.9581866470605895e-11` (limit `1e-9`). Scores/coefficient
  arrays are finite; floating source errors retain C1's passing limits.
- Complete aggregate/detail reports replay byte-identically, both stderr files
  are empty, and all 1280 rows/40 matrices complete. No correctness tolerance,
  error magnitude, rank cutoff or scientific gate was modified after results.
- Full analysis process CPU is 13.695243 seconds, replay 14.252492 seconds,
  below 120 seconds. Largest matrix+pseudoinverse is 512,064 bytes, below the
  1 MiB per-model bound. First perturbed matrix incremental traced peak is
  2,810,680 bytes, excluding other models/reports. Neither is a P4 memory budget.
- WSL Ubuntu/NumPy 2.5.2, `OPENBLAS_NUM_THREADS=1`. Production CPU/RAM/state
  delta is zero; no production source/API/confidence or `VERSION` change.

The public JSON includes condition/group gates, all 1280 scores and PCM/phase
hashes, supplied/original frequencies and independent-sign hashes, column norms,
ranks, numerical diagnostics and source/protocol/archive/input/output/log hashes.
Local `build/key-frequency-uncertainty-20260912/result-detail.json` retains all
physical/unit-column fit coefficients and independent-fit comparisons. No
private music, mappings, holdouts or native key reranking are involved.

## Reproduction

Extract `f0698190f4f330d42629f67c8a16a2d8dcbc9fbc` to a clean Linux source
directory. Retain/reproduce the pinned coverage export and prior public evidence.
Set `source`, `coverage` and `native` accordingly; use a fresh output prefix.

```sh
export OPENBLAS_NUM_THREADS=1
for name in frequency_uncertainty coherent phase_robustness within_cell identifiability partial_attribution; do
  python3 -m unittest discover -s "$source/tools" -p "test_apta_key_$name.py" -v
done
for b in default candidate sanitize; do
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 APTA_COVERAGE_PROBE="$native/$b/tests/apta_key_chroma_probe" python3 -m unittest discover -s "$source/tools" -p test_apta_key_coverage_diagnostic.py -v
done
python3 "$source/tools/apta_key_frequency_uncertainty.py" --samples "$coverage/default.bin" --witnesses "$source/evidence/1.1/key-identifiability-20260911.json" --f1-evidence "$source/evidence/1.1/key-within-cell-f1-20260911.json" --f2-evidence "$source/evidence/1.1/key-phase-f2-20260911.json" --c1-evidence "$source/evidence/1.1/key-coherent-c1-20260912.json" --source-commit f0698190f4f330d42629f67c8a16a2d8dcbc9fbc --output-prefix result
```

Repeat once with prefix `repeat`; compare aggregate/detail JSON exactly and
keep resource timing separate. The actual run script and source archive are
hashed publicly. No private audio is required.

## Next boundary

Before sub-bin frequency estimation, preregister a **numerically valid treatment
of unobservable frequency components** in the coherent representation. It must
avoid turning negligible projected energy into unrestricted fit directions,
with physical observability tests independent of these family verdicts. Freeze
the construction and veto before implementation; do not tune it to remove the
32 C2 reversals. C2 stays rejected with its original matrices and outputs intact.

This is a prerequisite for a later frequency-estimation experiment, not a new
detector proposal or a rerun of this screen. C1's exact-frequency pass, H1/F2
rejections, all six music-transfer rejections, spent-data seals, unopened WP6/
WP7, physical P4 acceptance and release freeze remain unchanged.
