# Coherent frequency-hypothesis screen C1 — 2026-09-12

**Complete: 256/256 new unknown-phase observations pass both frozen gates.**
The coherent model's maximum correct-family normalized squared residual is
`3.3088157169422225e-16`; the minimum wrong-family residual is
`0.10573718934861323`. On the same new phase bank, unchanged F2 passes 255/256.
All 256 original F2 rows and eight original F1 rows replay exactly first.

This supports only **supplied-frequency discrimination** on the four fixed
synthetic fixtures. Frequencies are given, amplitudes/phases are fitted, and
no notes or keys are discovered. No production candidate is retained or ported;
H1 and F2 remain rejected at their original scopes. No music or holdout is
opened, and production source/API/confidence/`VERSION` (`1.0.1`) are unchanged.

Protocol commit `ebdb9fe` preceded instrument source
`80577eb4e777ca0528998b3113f93424f7ec8e13` and matrix execution. Baseline:
`1622027e64251e5b15e6630b9d64bf2157d59ac9`. See the
[frozen protocol](APTA-1.1-KEY-COHERENT-PROTOCOL.md) and
[public results, phase provenance and validation](../../evidence/1.1/key-coherent-c1-20260912.json).

## Fixed experiment and interpretation

Four unique ideal spectra are retained in the previous first-occurrence order.
Both known-harmonic and pure-alternative sources have 32 new independent phase
realizations per fixture: 256 observations. SHA256 phase construction uses
the preregistered `apta-c1-20260912` prefix, distinct from F2. Duration, source
amplitudes/frequencies, 48-kHz source rounding and ordered float32 four-sample
averaging are unchanged. No phase search, tuning, noise, duration or timbre
sweep is performed.

Each hypothesis consists of unit sine and cosine waves at its supplied
frequencies, averaged in float64 and transformed by the same rectangular,
unpadded one-second FFT. Only bins 128..1016 Hz inside the original C3–B5
range are retained: 889 complex observations become 1,778 real coordinates.
The known hypothesis includes all nine physical partials, including those
outside the range whose leakage enters the observed bins. The alternative
has four or five pure frequencies. No measured out-of-range bin is used.

Columns are normalized and one thin SVD/pseudoinverse is computed for each
hypothesis using frozen `rcond=1e-12`. Real sine/cosine coefficients express
unknown amplitude and phase. The fitter receives the observed complex vector
and matrix, never generating phases, amplitudes or family labels. It uses
unconstrained least squares, with no harmonic-amplitude or model-size penalty.

Unlike F2, C1 retains both phase information **and cell totals**, and uses a
different residual objective. A gain cannot be attributed solely to phase.
The larger known hypothesis also has more degrees of freedom; both generating
families are therefore reported separately. Correct-frequency near-exact
reconstruction is expected in this matching synthetic model and is not evidence
of robustness to frequency estimation error or real instrument spectra.

## Complete new-bank results

Both frozen gates must pass per observation: correct-family squared residual
divided by observed in-range squared norm <=1e-10, and wrong-family residual
greater than correct-family residual +1e-6.

| Fixture | Generating family | C1 pass /32 | Frozen F2 pass /32 | Max correct residual | Minimum wrong residual |
|---|---|---:|---:|---:|---:|
| 0 | Known harmonics | 32 | 31 | 3.193e-16 | 0.191619450 |
| 0 | Pure alternative | 32 | 32 | 2.479e-16 | 0.105737189 |
| 1 | Known harmonics | 32 | 32 | 3.039e-16 | 0.198088246 |
| 1 | Pure alternative | 32 | 32 | 2.492e-16 | 0.105943744 |
| 2 | Known harmonics | 32 | 32 | 3.309e-16 | 0.215963527 |
| 2 | Pure alternative | 32 | 32 | 2.505e-16 | 0.112066328 |
| 3 | Known harmonics | 32 | 32 | 3.203e-16 | 0.220194359 |
| 3 | Pure alternative | 32 | 32 | 2.542e-16 | 0.110491168 |

Fixture representatives remain `[5,1,5,2]`, `[6,1,5,2]`, `[7,1,5,2]`,
`[8,1,5,2]`. Phase origin is zero for the new bank. These are four deliberately
constructed alternatives, not 256 independent songs. No general phase-invariant
proof or musical-key acceptance follows from the finite bank.

There is one improved spectral-family verdict versus F2 on this new bank and
zero regressions. F2's failure is fixture 0, known family, realization 15:
its correct reference distance is 0.345870575 versus wrong 0.343969304.
C1 gives correct residual `3.028422470963472e-16` versus wrong
`0.22506029577110295`. The historical F2 result remains 252/256 on its own
original bank; its four failures are not replaced by the new-bank count.

## Matrix conditioning and host resources

| Fixture | Hypothesis | Matrix shape | Retained rank | Condition number | Matrix + pseudoinverse bytes |
|---|---|---|---:|---:|---:|
| 0 | Known | 1778 x 18 | 18 | 37.423 | 512064 |
| 0 | Pure | 1778 x 10 | 10 | 1.004 | 284480 |
| 1 | Known | 1778 x 18 | 18 | 114.688 | 512064 |
| 1 | Pure | 1778 x 10 | 10 | 1.004 | 284480 |
| 2 | Known | 1778 x 18 | 18 | 632.748 | 512064 |
| 2 | Pure | 1778 x 8 | 8 | 1.003 | 227584 |
| 3 | Known | 1778 x 18 | 18 | 2594.800 | 512064 |
| 3 | Pure | 1778 x 8 | 8 | 1.002 | 227584 |

All columns remain retained at the fixed SVD cutoff. Rank and conditioning are
reported, not used to select another solver. The largest matrix+pseudoinverse
is 512,064 bytes, below the frozen 1 MiB host limit; this is a **per-model**
bound, not the full experiment's resident memory. Eight models are retained
by the report tool. First-matrix incremental traced peak is 2,808,456 bytes,
including its construction/SVD temporaries but excluding other models/reports.
Neither measurement is a P4 feasibility claim.

Process CPU is 4.240451 seconds, replay 4.019728 seconds, below 60 seconds;
this includes the old F2/F1 controls and report preparation, but excludes final
JSON writing. Single-thread WSL Ubuntu/NumPy 2.5.2 is used with
`OPENBLAS_NUM_THREADS=1`. Production CPU/RAM/state delta is zero.

## Correctness and provenance

- Eight new tests pass: exact sine/cosine and unknown-phase recovery, mixed
  close/out-of-range frequencies, absent-frequency residual, dependent-column
  rank handling, no generating metadata in the fitter, new hash-bank identity,
  margin/reconstruction boundaries, invalid inputs and replay.
- Six phase, six F1, ten identifiability and eight H1 regression tests pass
  unchanged. Eleven coverage tests pass separately against each reused default
  Release/Werror, I1 Release/Werror and I1 Debug ASan/UBSan native probe. These
  are focused host/diagnostic checks, not a new full CTest/build/P4 qualification.
- All 256 original F2 score/phase records and eight F1 controls replay exactly;
  source and input hashes match their pinned records before interpretation.
- First observations from both families/fixture are fitted to both hypotheses
  and checked against `numpy.linalg.lstsq` at the same rcond. Maximum normalized
  prediction discrepancy is `6.524943908605252e-15`, below `1e-10`.
- Maximum Parseval discrepancy is `1.935966130825505e-15` (limit `1e-12`);
  maximum direct Fourier discrepancy is `1.2045610293978816e-11` (limit `1e-9`).
- Maximum source-rounding relative error is `4.071541342145201e-8`, absolute
  `4.7485698595473025e-8`, both below `1e-6`. Coefficients, phases and scores
  are finite and all 256 records/eight matrices complete.
- Aggregate and detailed reports replay byte-identically; stderr is empty in
  both runs. Timing is recorded separately. No instrument failure or protocol
  threshold/rcond/phase change occurred after seeing the matrix.

The public JSON retains every observation's residuals, phases/hashes, frozen
F2 comparison, group metrics, matrix ranks/singular values and source/protocol/
archive/input/output/log hashes. Local
`build/key-coherent-20260912/result-detail.json` records unit-column and physical
sine/cosine coefficients for both hypotheses and independent-fit checks.
No private audio/mappings or native key reranking are involved.

## Reproduction

Extract `80577eb4e777ca0528998b3113f93424f7ec8e13` into a clean Linux source
directory. Retain/reproduce the pinned coverage export and prior identifiability,
F1/F2 public evidence. Set `source`, `coverage` and `native` to those directories
and use a fresh output prefix. Output overwrite and input/source drift fail.

```sh
export OPENBLAS_NUM_THREADS=1
for name in coherent phase_robustness within_cell identifiability partial_attribution; do
  python3 -m unittest discover -s "$source/tools" -p "test_apta_key_$name.py" -v
done
for b in default candidate sanitize; do
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 APTA_COVERAGE_PROBE="$native/$b/tests/apta_key_chroma_probe" python3 -m unittest discover -s "$source/tools" -p test_apta_key_coverage_diagnostic.py -v
done
python3 "$source/tools/apta_key_coherent.py" --samples "$coverage/default.bin" --witnesses "$source/evidence/1.1/key-identifiability-20260911.json" --f1-evidence "$source/evidence/1.1/key-within-cell-f1-20260911.json" --f2-evidence "$source/evidence/1.1/key-phase-f2-20260911.json" --source-commit 80577eb4e777ca0528998b3113f93424f7ec8e13 --output-prefix result
```

Repeat once with prefix `repeat` and compare aggregate/detail JSON exactly;
resource timing may differ. The actual run script and source archive are hashed
in the public record.

## Next boundary

Preregister a **frequency-uncertainty screen** for the coherent representation
before any note-discovery algorithm or native implementation. Exact supplied
frequencies are its strongest unresolved assumption. Freeze the frequency-error
construction, evidence bank, gates and resource bounds before execution;
do not fit offsets or thresholds against this C1 result. No such screen is
run here, and this pass does not choose an estimator or justify a C port.

Unknown timbre/noise/polyphony and discovery of the competing hypotheses remain
outside this experiment. F2/H1 and all six music-transfer rejections remain;
independent development, unopened WP6/WP7, physical ESP32-P4 acceptance and
release freeze retain their existing gates.
