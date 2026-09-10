# Mean-normalized key cost I1 — retained for independent development

The implementation at `a883dd6d0d50d4f463d8347352d75891d9005fba` passes
all preregistered identity, correctness and host-cost gates. It preserves the
original normalized candidate's reports byte for byte while reducing its
extra project stack from **400 to 64 bytes**. Median CPU time is **14.42%
lower** than the original normalized implementation, with a **0.997090**
ratio to default. This retains I1 for a separately defined independent
key-development comparison; it does not promote a production detector.

The [protocol](APTA-1.1-KEY-MEAN-COST-I1-PROTOCOL.md) was committed as
`c30736e` before code or measurement. The
[original rejection](APTA-1.1-KEY-MEAN-NORMALIZATION-RESULT.md) remains closed:
I1 is a distinct implementation experiment with an unchanged formula and a
new, longer timing protocol. No corpus, FMAK report or formal holdout was read.

## Change and identity

At a completed window, each resonator's q1 becomes dead after its own energy
is computed. I1 uses that existing array for raw and compressed energies,
then the existing lifecycle resets q1/q2 before the next sample. The cold
window work lives in `src/key/apta_key_mean_cost_i1.c`, outside the sample
feed translation unit. No local 36-float buffer, persistent field, allocation,
reciprocal approximation or arithmetic reordering is introduced.

Enable both `APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON` and
`APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY_COST_I1=ON`. The second option
requires the first. Default and the original normalization implementation
are preserved when I1 is off; their analyzer/key-object hashes are identical
to the preceding pinned builds. This is still an opt-in experiment.

All four fixed-gain reports (-4,-2,0,1), four repeats and four sanitizer
reports match the original candidate byte for byte. Each report contains
720 rows, 288 observed windows and 13,824,000 reversible PCM samples. The
frozen evaluator output is also byte-identical, including all six passing
synthetic gates. Consequently, every original limitation and metric remains:

- 56/72 final stimulus matches versus default 35/72;
- 22 fixes, one break and 31 changed verdicts;
- zero newly high-confidence mismatches, with 24 high-confidence finals;
- clean and noisy conditions each 24/24; detuned condition only 8/24;
- identical normalized evidence, scores and confidence at every fixed gain.

The lone break remains the detuned tonic-1 minor stimulus, selected as tonic-9
major at confidence 56. There are no new fixes, breaks or changed verdicts
relative to the original normalized implementation. These synthetic results
do not establish correctness or confidence safety on music.

## Host resource result

Clean WSL Ubuntu x86-64 GCC 13.3 Release/Werror builds used the unchanged
`apta_key_feed_benchmark`. Each D/R/C build received one excluded 120-second
input warmup. Seven triples then used 3600-second input signals, with the
registered rotating D/R/C, R/C/D, C/D/R order. D is default, R is original
normalization and C is I1. No task build or experiment ran concurrently.

| Triple | D CPU ms | R CPU ms | C CPU ms | C/D | C/R |
|---|---:|---:|---:|---:|---:|
| 1 | 736.229 | 856.310 | 732.824 | 0.995375 | 0.855793 |
| 2 | 728.083 | 864.526 | 730.380 | 1.003155 | 0.844833 |
| 3 | 749.310 | 853.781 | 743.296 | 0.991974 | 0.870593 |
| 4 | 736.464 | 859.257 | 731.296 | 0.992983 | 0.851079 |
| 5 | 737.355 | 875.757 | 735.777 | 0.997860 | 0.840161 |
| 6 | 749.545 | 865.933 | 747.364 | 0.997090 | 0.863074 |
| 7 | 734.500 | 856.988 | 742.353 | 1.010692 | 0.866235 |

Median C/D is **0.997090 <=1.15**; median C/R is **0.855793 <1.0**.
All 21 measured intervals exceed the 500 ms minimum (range 728.083–875.757
ms). Every sample is retained; no repeat, filtering or threshold adjustment
was applied. The near-unity C/D ratio means no material measured overhead,
not a claim of a meaningful speedup over default. These are host key-feed
CPU measurements, excluding decoding and full pipeline work.

GCC stack reporting and disassembly confirm:

| Project call path | Stack bytes |
|---|---:|
| Default feed (window work inlined) | 80 |
| Original feed + compression | 432 + 48 = 480 |
| I1 feed + in-place accumulation + compression | 80 + 16 + 48 = 144 |

I1 therefore adds **64 bytes**, below the **192-byte** limit and below the
original 400-byte delta. Compiling with `-fstack-usage` produces identical
object bytes. The accounting excludes external callers and common libm
internals; it is not a whole-program/P4 stack bound. Session storage remains
11,824 bytes, observer scratch 476 bytes, with zero new state or allocations.

## Software checks and reproduction

All configurations use the exact committed source archive on ext4:

- default Release/Werror: 118/118 native tests;
- original normalization Release/Werror: 119/119;
- I1 Release/Werror: 119/119;
- I1 Debug/ASan/UBSan/Werror: 116/116;
- unchanged frozen evaluator unit tests: 6/6;
- seven invalid configurations rejected (six incompatible key options and
  I1 without its required base option).

The expanded native normalization test covers a non-silent completed window,
q1/q2/decimation reset, and an immediately following silent window preserving
exact accumulated chroma. Existing invalid/extreme/subnormal/scaling tests,
ABI/layout, publication and serialization checks also pass.

Use a clean archive of the pinned source. Configure Release/Werror with
both experimental options for I1, only the base option for R and neither
for D; add Debug and `APTA_ENABLE_SANITIZERS=ON` for the I1 sanitizer build.
Build normal targets and explicitly build `apta_key_gain_diagnostic` and
`apta_key_feed_benchmark`. Run `ctest --output-on-failure` in each build.
Execute gain diagnostics with `--json --gain-shift N` for exactly the four
registered values and compare each output to the pinned original reports.

```powershell
python -m unittest discover -s tools -p test_apta_key_mean_normalization_eval.py -v
python tools/apta_key_mean_normalization_eval.py --reports build/key-mean-cost-i1-20260910 --baseline build/key-gain-20260905/default-shift0.json --output build/key-mean-cost-i1-20260910/new-evaluation.json
```

The [public evidence](../../evidence/1.1/key-mean-cost-i1-20260910.json)
retains source/protocol/binary/report identities, flags, compiler/CPU identity,
all measurements and gates. Full reports, CTest/configuration logs, disassembly,
stack records and exact launcher scripts remain under ignored
`build/key-mean-cost-i1-20260910/` (`run.py`, `resources.py`, `evidence.py`).
The protocol specifies the complete timing order; reproduce stack records by
compiling both key translation units with their CMake flags plus
`-fstack-usage`, requiring identical objects and inspecting nested calls.

## Next boundary

Preregister one disjoint independent key-development comparison for this exact
I1 detector before accessing its results. Establish the available, legally
usable development material and its separation from all spent splits and
formal holdouts, freeze labels/evaluator/absolute and per-mode safety gates,
then compare default and I1 without changing formula or confidence. Treat
poor detuning robustness as an unresolved transfer risk. Do not substitute
external-detector agreement for verified labels.

The implementation-cost task is complete. Independent transfer, physical
P4 memory/timing/USB/audio evidence, WP6/WP7 and final release gates remain
open; the default stays unchanged and VERSION remains 1.0.1.

The following [disjoint MTG development comparison](APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md)
has now rejected this detector: 37/96 exact versus default 27/96, with failed
absolute/per-mode gates and 17 new high-confidence errors. This supersedes
eligibility for further validation. The resource and identity findings above
remain valid at their recorded scope; no production promotion is authorized.
