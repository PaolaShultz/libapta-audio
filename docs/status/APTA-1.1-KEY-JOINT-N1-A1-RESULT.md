# E2-N1 numerical repair and E2-A1 attribution result — 2026-09-13

**Numerical blocker resolved in N1. A1 passes the frozen synthetic gates only.**
Original E2 remains rejected and byte-for-byte unchanged. No production promotion,
music transfer, holdout access, physical test, release change or push occurred.

The user authorized Implement-mode continuation. Fructal Cap Design preserves
frozen evidence and gates through distinct revisions; the historical “stop E2”
protects that experiment rather than preventing a new correction.

## Demonstrated numerical cause

All five recorded failures reconstruct under NumPy 2.5.2 / SciPy 1.18.1 with
OPENBLAS_NUM_THREADS=1. All PCM hashes, matrices, target/column normalization,
ridge augmentation and original returned coefficients match exactly. The local
host is Linux, Python 3.13.13; this reproduces the original package versions and
numerical values, not the old Windows/WSL machine image. The review environment's
NumPy 2.5.3 was inspected but not used for the primary experiments.

The error is in the solver workspace, not the projected KKT checker or APTA's
integration. The augmented residual gradient agrees with Gram-plus-ridge and
extended-precision calculations; inputs remain unchanged. A separately compiled
unmodified SciPy kernel reproduces the wheel's coefficients and returned rnorm
exactly. Independent BVLS reference solves satisfy the original objective/gates.

In [SciPy v1.18.1 nnls.c](https://github.com/scipy/scipy/blob/v1.18.1/scipy/optimize/src/nnls.c),
`dlarfgp` overwrites the prospective column's tail before the positivity test.
When `ztest<=0`, the rejected column's pivot is restored, but its overwritten tail
is not. Subsequent transformations can use that corrupted column. Tiny sign
roundoff triggers rejection; the resulting error need not be tiny. In the largest
case, reported rnorm is 0.09993481710205436, but the returned coefficients give
0.11553995259048136, and projected KKT is 0.04075896. This is a demonstrated defect
in this specific source/kernel path; no upstream issue was filed and no claim is
made about other SciPy versions. A tested Givens-output-alias change did not repair
these cases; it is not part of N1.

N1 saves/restores the entire prospective column segment on rejection, using
caller-owned scratch. Accepted-column logic, active-set solver, ridge 1e-3,
maxiter=30*n, x>1e-10 active threshold, KKT<=1e-8 and objective gate are unchanged.
The upstream kernel/license and narrow patch are vendored under
`tools/experimental/nnls_n1/`; the isolated host library is explicitly loaded via
APTA_NNLS_N1_LIBRARY. Installed SciPy and production C/builds are untouched.
There is no retry, BVLS fallback, clipping, threshold relaxation or budget tuning.

| Family, fixture tonic, mode, window | Original KKT | N1 KKT |
| --- | ---: | ---: |
| missing, 9, major, 4 | 1.538732080346066e-5 | 1.5592097789762435e-16 |
| missing, 10, major, 4 | 1.261330056069470e-5 | 1.6360610782806262e-16 |
| missing, 8, minor, 6 | 4.075896179334614e-2 | 1.2521179839491970e-16 |
| missing, 11, minor, 1 | 5.159002873753719e-7 | 2.8888566885876266e-16 |
| detuned, 11, minor, 7 | 1.514959776223872e-7 | 1.1720225484568303e-16 |

Expected E2 tonic is fixture tonic minus one modulo 12. All five complete array
cases and a standalone deletion-reduced 74x20 numerical case are preserved.
The reduction is reproducible, not a globally minimal counterexample. The
[numerical report](../../evidence/1.1/repro/key-joint-n1-20260913/numerical-cause.json)
contains both gradients, coefficients, objective/residual checks, reference solves,
source/library hashes and environment/build metadata.

N1 passes all 1152 E2 windows (max KKT 5.053466325954936e-16). The largest coefficient
change on previously valid windows is 3.46771352843699e-18. Four abstentions become
correct keys; missing fixture 11/minor becomes a valid but wrong relative-major
selection. N1 therefore scores 130/144, not 131/144, and remains algorithmically
rejected. The native direct comparator and every PCM hash match the old report.

## Attribution mechanisms and bounded A1

The [complete evaluation-only trace](../../evidence/1.1/repro/key-joint-n1-20260913/attribution-complete.json.gz)
covers all 24 unequal cases, the two original valid-solve regressions and all five
repaired clips. It records peak frequencies/amplitudes, true-partial matches,
true-note candidate coverage, all fitted allocations, chroma and native rankings.
Supplied-note diagnostics never enter either instrument.

**Observed missing-family mechanism:** fixture 2/major and 4/major retain every
true-note candidate within 20 cents, yet select their expected tonic in minor.
Their unrestricted fits allocate to extra harmonic/octave explanations and
unevenly weight true sources. Restricting the diagnostic fit to true-note support
restores major in both, at a *higher* objective. The newly exposed fixture 11/minor
also has full true-note coverage; known-support fitting restores its key.
Thus successful optimization of this magnitude surrogate is not source recovery.
For example, fixture 2/major window 1 assigns physical amplitude about .596 to
MIDI 61 and .511 to non-source MIDI 66, while true root MIDI 54 is suppressed;
its unrestricted objective .01733 beats known-support .12466.
Partials can share discovered peaks; coherent phase interference, peak merging
and the fixed envelope are plausible contributors. This trace does not uniquely
decompose those causes or establish physical identifiability.

**Observed unequal-family mechanism:** true-note candidates survive except the
61.735-Hz lower root in fixture 0's two bass windows (outside the fixed 65-Hz
range). That boundary cannot explain failures across the other tonics. All 12
ideal unequal-major source-amplitude sequences become minor after exact squared
folding and native selection. Known-support fitting also gives 0/12 major;
equal-source diagnostic folding gives 12/12. N1's unrestricted fit happens to get
two major keys right. Squaring/aggregation and native-profile sensitivity therefore
remain a distinct mechanism even with perfect source identities.

[A1's hypothesis/protocol](APTA-1.1-KEY-JOINT-A1-PROTOCOL.md) was committed before
its implementation and before fresh generation. The single candidate folds
nonnegative fitted *amplitude mass* directly, rather than squared amplitudes,
then uses the unchanged per-window normalization, accumulation and native selector.
Everything through the N1 solution is identical. The stated risk was increased
relative influence of weak spurious explanations. No exponent sweep, changed
objective, new dictionary, oracle, confidence adjustment or post-result tuning
was performed. This is a salience-representation correction, not proof of repaired
physical harmonic allocation.

## Separate regression and fresh results

| Instrument and bank | Exact keys | Direct peaks | Fixes / breaks vs direct | Fixes / breaks vs N1 | High-confidence errors | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Frozen E2, historical bank | 126/144 | 130/144 | 3 / 7 | — | 0 | Rejected, numerical and scientific |
| N1, E2 regression bank | 130/144 | 130/144 | 3 / 3 | — | 0 | Numerical pass; scientific rejection |
| A1, E2 regression bank | 143/144 | 130/144 | 13 / 0 | 13 / 0 | 0 | Regression gates pass |
| N1, fresh bank | 138/144 | 132/144 | 10 / 4 | — | 2 | Numerical pass; scientific rejection |
| A1, fresh bank | 144/144 | 132/144 | 12 / 0 | 6 / 0 | 0 | Frozen synthetic gates pass |

A1 E2-bank families: pure/full/missing/detuned/steep 24/24 each, unequal 23/24
(major 11/12, minor 12/12). The remaining error is unequal fixture tonic 5,
expected tonic 4/major, selected tonic 4/minor, confidence 65. It was already
wrong in both N1 and direct peaks. Both original valid-solve mode regressions and
the newly exposed regression are fixed in A1. The fresh A1 bank has 12/12 for
every family/mode. All numerical, availability, no-regression, confidence and
resource gates pass for A1, including the additional no-break-vs-N1 constraint.
N1's two fresh high-confidence errors underline that numerical repair alone
cannot support algorithm acceptance.

The fresh generator changes root/register, progression, bass placement, detuning
and phase domain according to the frozen protocol. Its full 1152-PCM hash manifest
was committed before any detector execution; it is disjoint from E2. This is still
related synthetic-family generalization, not an independent musical corpus or
formal holdout. Both banks are now spent; do not tune against them.

## Verification, resources and provenance

- N1 protocol `e9db26f` preceded instrument `76aa1e2` and the N1 bank.
- A1 protocol/diagnostic `2051899` preceded instrument/generator `7de02b3`;
  manifest `e039532` preceded every fresh detector evaluation.
- All four instrument/bank reports replay byte-identically. A clean detached
  checkout at evidence checkpoint `aec654e` rebuilt the same kernel hash and
  ran the saved reproduction script successfully; scientific rows and gates
  match the original reports exactly. Provenance commit metadata differs as expected.
- 27 focused/inherited/coverage tests pass. Eight N1/A1 tests pass with the
  experimental kernel built under ASan/UBSan. Leak detection is disabled for the
  Python host; no process-leak or full-native sanitizer claim is made.
- N1 CLI silence: unavailable, one processed window, 17 trailing samples,
  empty stderr. The unchanged inherited WAV tests cover malformed/rate/clipping.
- Original-pass/replay pipeline CPU seconds: N1 regression 4.160091/4.117914;
  N1 fresh 4.030760/4.066706; A1 regression 3.088709/3.068387;
  A1 fresh 4.138058/4.067136. All <120 s. Generation and replay verification
  are outside the pipeline clock; extraction plus one native selector pass is inside.
- Conservative numeric workspace: N1 13,031,712 bytes; A1 13,031,808 bytes,
  both below 16 MiB. Full-process RSS is separate (primary paired runs
  87,036–139,060 KiB). These are Linux host measurements, not embedded limits.
- The review Release chroma probe was reused and hashed. All old 288 native
  selections were verified against the original E2 report; the current run does
  not claim the old default/candidate/sanitizer three-binary identity. No broad
  review or full native build was repeated.
- Production source, public API, CMake/defaults, VERSION 1.0.1, old instrument
  files, original E2 report/repro/protocol/result and historical rejection files
  are unchanged. No corpus, device, service or release action occurred.

The [public summary](../../evidence/1.1/key-joint-n1-a1-20260913.json) pins full
compressed reports, source and artifact hashes, replay and resource records.
The [reproduction directory](../../evidence/1.1/repro/key-joint-n1-20260913/README.md)
contains the portable local-output runner. Follow the
[new canonical handoff](APTA-1.1-HANDOFF-20260913.md) for the remaining boundary.
