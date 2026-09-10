# Mean-normalized key cost I1 — frozen 2026-09-10

This is one implementation-cost experiment, not a new detector formula.
Baseline source is `f08ed6a84c561bcb7b92a66037c337b6e32a34c5`; original
mean-normalization source is `3fc7421f2cb184ac2ba31c02df2390268a24fe57`.
The preceding resource rejection (+400 bytes stack, CPU ratio 1.172285) remains
closed. Its synthetic reports and formula are immutable reference evidence.

## Hypothesis and single implementation change

The window-local 36-float array and the placement of the window work inside
the feed translation unit inflate the stack frame paid by the sample hot path.
At window completion, each resonator's q1/q2 is dead after its own energy is
computed and both arrays are reset before the next sample. Reuse q1 in place
for energy/compressed storage and put this rare window work in a separate
translation unit. Preserve the compression helper's exact float expressions,
sanitization, ascending accumulation order, logf, scores and confidence.
Do not change resonator update arithmetic, decimation or lifecycle semantics.

Use `APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY_COST_I1=ON`, requiring
`APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON`. Preserve both default and
original normalized implementations when the new option is off. No fast-math,
LTO, reciprocal approximation, global compiler override or fitted constant.
No new persistent state, heap allocation or local energy array. Expected
cost is a small cold-path call frame instead of the old hot-path spills.

## Identity and correctness gates

- All 720 rows of each of the four fixed gain reports (-4,-2,0,1), including
  raw and normalized observer values, must equal the original normalized
  reports byte for byte. Each run repeats exactly; ASan/UBSan equals Release.
- The frozen synthetic evaluator must reproduce all six passing gates and
  all metrics exactly: 56/72 finals, 22 fixes/one break, 31 changed verdicts,
  zero newly high-confidence mismatches. Detuned performance stays 8/24;
  it is a known limitation, not a parameter to optimize in this experiment.
- Default analyzer and key object remain byte-identical to the pinned default;
  the original normalized key object remains identical when COST_I1 is off.
- Full default and candidate Release/Werror CTest suites, candidate sanitizer
  suite, existing normalization edge tests and evaluator tests pass. Add
  lifecycle coverage for scratch reuse/reset and reject COST_I1 without its
  required base option. Existing six incompatible key-option checks still pass.
- Session/layout/pool sizes and allocation behavior remain unchanged.

## Frozen resource method and veto

Use clean x86-64 GCC 13.3 Release/Werror builds with identical compiler options
and no observer: default D, original normalization R, cost candidate C.
After identity/software checks pass, perform one 120-second-input warmup for
each D/R/C, excluded from measurement. Then exactly seven triples, each binary
fed **3600 seconds** of the existing deterministic benchmark signal:

1. D, R, C
2. R, C, D
3. C, D, R
4. D, R, C
5. R, C, D
6. C, D, R
7. D, R, C

Use benchmark clock() CPU milliseconds, with no concurrent task builds or
experiments. Require every measured interval >=500 ms; a shorter interval
makes this resource run inconclusive, not a pass. Keep every sample; no
outlier filtering, adaptive retries or selecting a preferred ordering.
Require median paired C/D <=1.15 and median paired C/R <1.0. This fresh,
longer measurement does not reinterpret the preceding seven short pairs.

Recompile relevant translation units with their CMake flags plus
`-fstack-usage`, verify unchanged object bytes, and inspect disassembly to
account for every nested project function on the window path. Exclude common
libm internals/external callers consistently with the baseline. Require extra
project stack <=192 bytes relative to D and strictly below the original
400-byte delta. These are host/compiler bounds, not physical P4 evidence.

Any identity, correctness or resource veto closes this exact I1 implementation;
do not tune it after observing the frozen gate results. If every gate passes,
retain only for a separately preregistered, disjoint independent development
comparison. No corpus, spent FMAK report, formal holdout or new final acceptance
set is accessed here. Do not promote or bump VERSION. Record exact source,
binary, protocol, report and resource identities in a public aggregate.
