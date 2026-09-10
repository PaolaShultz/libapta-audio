# Mean-energy normalization — rejected on resource gates

The exact candidate at `3fc7421f2cb184ac2ba31c02df2390268a24fe57` passes
the frozen synthetic screen but fails both host resource limits. It is closed
and is not eligible for an independent development run or promotion. The
normalization hypothesis has useful synthetic evidence; this implementation
does not meet its preregistered cost contract.

The [protocol](APTA-1.1-KEY-MEAN-NORMALIZATION-PROTOCOL.md) was frozen before
execution against baseline `fbe965bf5d89f52b92413d2fd3d4568dd54dde22`.
The candidate divides each one-probe window's bin energies by their mean,
using peak-scaled arithmetic, before the existing log compression. It preserves
profiles, confidence, window generation and cumulative aggregation. It remains
off by default behind `APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY` solely
for reproduction. No corpus or formal holdout was opened.

## Synthetic findings

At each gain (1/16, 1/4, 1, 2), final matches are:

| Condition | Baseline major /12 | Candidate major /12 | Baseline minor /12 | Candidate minor /12 |
|---|---:|---:|---:|---:|
| Clean | 4 | 12 | 11 | 12 |
| Detuned | 0 | 2 | 6 | 6 |
| Noisy | 3 | 12 | 11 | 12 |

Across 72 final progressions, matches increase from **35 to 56**, with
**22 fixes, one break and 31 changed verdicts**. The single break is the
detuned tonic-1 minor stimulus, selected as tonic-9 major at confidence 56.
Minor counts are preserved in each condition even though individual cases
change. There are 24 high-confidence final outputs and zero stimulus
mismatches among them; the baseline gain-1 report has no high-confidence
final outputs. These are synthetic stimulus identities, not real-song labels.

All six synthetic gates pass: gain invariance, clean major >=9/12, clean
minor >=11/12, fixes exceeding breaks, minor counts preserved per condition,
and zero newly high-confidence errors. Every corresponding normalized
PCM row, score, confidence and observer value is identical across gains.
Each run checks 13,824,000 exactly reversible input samples, 288 windows,
gain-squared raw-energy scaling and bit-identical accumulator reconstruction.
Each Release report reproduces byte for byte; all four ASan/UBSan reports
equal their Release counterparts. There are 720 rows per report.

The detuned condition remains weak (8/24 final matches). Gain invariance
does not establish tuning robustness, independent transfer or calibrated
confidence on music.

## Resource veto

The prescribed seven sequential default/candidate pairs each feed 120 seconds
of deterministic samples into `apta_key_feed_benchmark`. They use `clock()`
CPU time and exclude signal generation from the timed interval. No other
experiment or build was running during these pairs.

| Pair | Default CPU ms | Candidate CPU ms | Candidate/default |
|---|---:|---:|---:|
| 1 | 24.384 | 28.585 | 1.1723 |
| 2 | 24.748 | 29.772 | 1.2030 |
| 3 | 25.326 | 28.525 | 1.1263 |
| 4 | 37.647 | 28.898 | 0.7676 |
| 5 | 24.554 | 28.611 | 1.1652 |
| 6 | 24.563 | 28.854 | 1.1747 |
| 7 | 26.120 | 40.299 | 1.5428 |

The median paired ratio is **1.172285**, exceeding the **1.15** limit.
These short host timings vary substantially; they do not predict P4 timing.
The registered set was not repeated or filtered to obtain a pass.

GCC 13.3 Release `-fstack-usage` reports 80 bytes for the default feed
function, 432 bytes for the candidate feed function and 48 bytes for its
compression helper. Disassembly confirms the nested helper call. The
compiler-accounted window path therefore grows from 80 to 480 bytes:
**+400 bytes**, exceeding the **+192-byte** limit. The accounting excludes
external callers and common libm internals; it is not a whole-program stack
bound. Objects compiled with stack reporting are byte-identical to the
respective measured production objects. The 144-byte source array alone
understates the compiler's actual stack cost.

Session storage remains **11,824 bytes**, delta zero; the test-only observer
uses 476 bytes. There is no new retained history or allocation. Production
default analyzer and key-object hashes exactly match the pinned baseline,
including an independent rebuild from the clean source archive.

## Software verification and reproduction

From the committed source archive on WSL Ubuntu x86-64, GCC 13.3:

- default Release/Werror: **118/118** CTest tests;
- candidate Release/Werror: **119/119**, including mean-normalization unit tests;
- candidate Debug/ASan/UBSan/Werror: **116/116**;
- frozen evaluator unit tests: **6/6**;
- all six incompatible key option combinations rejected at configure time;
- four candidate diagnostic runs and four exact repeats;
- four sanitizer diagnostic runs, identical to Release.

The native tests cover zero/silent windows, preservation of earlier evidence,
NaN/infinity/negative energies, uniform and one-hot minimum subnormal/maximum
finite energies, exact binary scaling and bounded output. The complete native
suites also exercise ABI/layout, result publication and serialization. These
counts describe this configuration, not the historical WP5 matrix.

Configure a clean archive of the pinned commit with
`-DCMAKE_BUILD_TYPE=Release -DAPTA_WARNINGS_AS_ERRORS=ON` for default, and
add `-DAPTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON` for candidate. For
sanitizers use Debug plus `-DAPTA_ENABLE_SANITIZERS=ON`. Build the normal
targets, then explicitly build `apta_key_gain_diagnostic` and
`apta_key_feed_benchmark`; run `ctest --output-on-failure` in each build.

Run the candidate diagnostic with `--json --gain-shift SHIFT` for exactly
`-4`, `-2`, `0`, `1`, keeping reports under fresh names
`candidate-shiftN.json`. The gain-1 baseline report is pinned by SHA-256 in
the evaluator; it is reproducible from the preceding gain experiment.

```powershell
python -m unittest discover -s tools -p test_apta_key_mean_normalization_eval.py -v
python tools/apta_key_mean_normalization_eval.py --reports build/key-mean-normalized-20260910 --baseline build/key-gain-20260905/default-shift0.json --output build/key-mean-normalized-20260910/new-evaluation.json
```

The [public evidence](../../evidence/1.1/key-mean-normalization-20260910.json)
records exact source/protocol/evaluator/binary/report hashes, all gate values,
individual cost pairs, stack functions, the broken case and compiler/CPU
identity. Full reports, disassembly, stack files and command-launcher scripts
remain in ignored `build/key-mean-normalized-20260910/`. Cost reproduction
uses seven sequential default-then-candidate benchmark pairs with argument
`120`; stack reproduction recompiles `apta_key.c` with the corresponding
CMake `flags.make` options plus `-fstack-usage`, verifies object identity,
and inspects `objdump -dr` for the nested call.

## Next boundary

Do not promote this implementation, repeat the cost set to rescue its result,
or tune normalization constants/profiles/confidence against the synthetic
screen. A separate implementation-cost experiment can be preregistered to
reduce temporary storage and hot-path overhead while requiring identical
normalized evidence and decisions to this pinned candidate. Its resource
protocol must be frozen before implementation; use longer timed host batches
to reduce the observed timing noise. Preserve this failed measurement.

Only a separately qualified implementation may proceed to a preregistered,
disjoint independent key-development comparison. Tuning robustness remains
an explicit limitation. Physical P4 timing/stack/USB/audio evidence, WP6/WP7
eligibility and all final 1.1 release gates remain open. `VERSION` stays 1.0.1.
