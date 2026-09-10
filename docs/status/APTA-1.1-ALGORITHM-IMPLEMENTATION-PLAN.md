# APTA 1.1 algorithm and release implementation plan

- **Plan baseline:** `4f21c2c2e1d03bb16686671a368f273a034b403e`
- **Development branch:** `1.1.0`
- **Plan status:** active
- **Stable package authority:** `1.0.1`; do not bump version metadata while
  any frozen 1.1 blocker remains open

## Objective

Close the remaining APTA 1.1 release blockers without tuning against formal
holdouts or reusing the rejected 60-track corpus as fresh acceptance evidence.
The engineering order is beat-lattice evidence, downbeat/bar phase, musical
key, integrated candidate qualification, one-shot holdouts, a new final corpus,
physical ESP32-P4 evidence, and release freeze.

Tempo/grid ensemble and calibrated BPM confidence are already accepted. Meter
already passes the rejected final corpus gate. The unresolved algorithmic
deficits are key accuracy and beat-lattice/downbeat phase.

## Non-negotiable boundaries

- The frozen final gates and correctness definitions do not change after
  observing candidate results.
- The existing 60-track musician-verified corpus is development evidence only.
  Its official rejection remains immutable.
- Ballroom and ASAP development partitions may be used during design. Their
  formal holdouts stay unopened until the complete candidate is frozen.
- A future final acceptance corpus contains at least 48 newly and independently
  verified tracks not used for candidate selection.
- Every experiment starts with a recorded hypothesis, exact baseline revision,
  build flags, evidence source, resource expectation, no-regression veto and
  stop condition.
- Experimental code remains opt-in. Default builds and stable 1.0 behavior must
  remain unchanged until promotion is justified.
- Do not grow `apta_internal_onset_bin_t` beyond its 16-byte ceiling. New
  temporal evidence must use bounded scratch/state or derived evidence so the
  dominant S6 allocation does not spill from the intended memory class.
- Private audio, filenames, paths, mappings and staging labels never enter the
  repository.

## Baselines to preserve

The official rejected 60-track result is key 15/60, meter 58/60, downbeat 5/60
and beatgrid 4/60. Subsequent development baselines are:

- KP profiles plus log-compressed key evidence: 20/60;
- opt-in harmonic projection: 22/60, two fixes, zero breaks and zero
  high-confidence key errors;
- opt-in three-band downbeat: 7/60, two fixes and zero breaks;
- cached S4 top-three period oracle: 49/60 versus 40/60 for the selected period.

These values are comparison aids, not acceptance claims.

## Work package 0 — freeze the development harness

**Status:** complete at `a7ed0de6666dbff8a3eb0ac047a2cb26098a11b0`; see
`APTA-1.1-WP0-DEVELOPMENT-HARNESS.md`.

**Purpose:** make every later candidate directly comparable.

Implementation:

1. Record a clean default and all-current-experiments build at the plan
   baseline.
2. Retain machine-readable baseline outputs for the spent DJ corpus and open
   Ballroom/ASAP development partitions.
3. Extend the existing key/meter traces only where required to expose
   per-window or per-lattice evidence; keep traces behind development flags.
4. Add one comparison report that reports per family: fixes, breaks, changed
   verdicts, exact accuracy, high-confidence errors, execution failures and
   resource delta.

Verification and exit:

- default Werror suite and current opt-in Werror suite pass;
- sanitizer suite passes for the enabled experimental paths;
- repeated baseline runs produce identical verdicts and hashes;
- reports contain only opaque track IDs.

## Work package 1 — new transient/onset evidence

**Status:** exhausted after ten frozen iterations; no onset candidate retained.
Transient-lattice iterations 1 through 8, spectral-flux I9 and complex-phase
deviation I10 are rejected. I10 tested a genuinely new phase-evolution axis but
its 40.4% median host runtime overhead exceeded the pre-registered 35% ceiling
before any development corpus trace was captured. The
privacy-safe spent-DJ trace diagnostic at revision
`fb6c2e13bfe5a2ff9b71fe3c96dd4d30f05a955e` shows useful causal-harmonic phase
evidence but does not authorize promotion. I8's new within-bin peak-to-mean
statistic also failed external transfer. The frozen production multiband onset
path remains the default. Formal holdouts remain unopened. See
`APTA-1.1-WP1-COMPLEX-DEVIATION-I10-EXPERIMENT.md`.

**Hypothesis:** the existing single-step broadband/per-band rise loses transient
shape and local contrast. A bounded multi-timescale onset representation can
separate true periodic attacks from filter tails and sustained energy, exposing
the correct lag/phase more consistently.

Proposed implementation boundary:

- add an opt-in `APTA_ENABLE_EXPERIMENTAL_TRANSIENT_LATTICE` path;
- derive fast-rise, slow local floor, band balance and local peak/refractory
  evidence from the existing bounded band-energy timeline;
- write the candidate novelty into bounded refresh scratch rather than growing
  the 16-byte onset-bin type;
- preserve the current production flux and selector as the baseline path;
- expose privacy-safe onset trace fields needed for offline comparison;
- add synthetic fixtures covering impulses, sustained tones, syncopation,
  kick/snare alternation, off-beat hats, silence and bounded ring rollover.

Initial retain/reject criterion:

- retain only if it produces at least five net period/phase fixes with at most
  one break on the spent DJ set and shows a positive transfer on both open
  Ballroom and ASAP development partitions;
- reject immediately for a default-behavior change, operational failure,
  onset-bin growth, high-confidence safety regression or negative transfer on
  either independent development partition.

## Work package 2 — temporal beat-lattice tracker

**Status:** closed without promotion after three pre-registered temporal
hypotheses. The unweighted continuity path and strict-majority selector failed
external-development transfer. WP2-I3 kept the exact ordered top three and
tested beat-to-beat onset-path continuity within the frozen 0.10-beat phase
tolerance. It improved Ballroom period 9/40 to 12/40 and joint phase 7/40 to
9/40, but ASAP period remained 2/40, joint remained 0/40 and phase regressed
1/40 to 0/40. It was therefore rejected before the spent-DJ trace or native
implementation. Production retains frozen full-window S4 rank zero, and formal
holdouts remain unopened; see `APTA-1.1-WP2-BEAT-PATH-I3.md`.

The separately frozen 2026-09-04 coverage audit confirms that distinct local
score peaks do not solve the missing-period problem: ASAP top-three coverage
remains 2/40 and Ballroom falls from 17/40 to 12/40 with no fixes and five
breaks. Removing the prior does not improve top-ten coverage either. These
are cached diagnostic coverage counts, not selected/refined-grid accuracy.
No native selector changed; see `APTA-1.1-LATTICE-COVERAGE-AUDIT.md`.

**Hypothesis:** one global autocorrelation/phase choice cannot represent tracks
whose transient reliability changes over time. Tracking a small bounded family
of lag/phase hypotheses over consecutive windows can recover a stable lattice
without selecting isolated high-scoring aliases.

Proposed implementation boundary:

- reuse S4's bounded top candidates and the new novelty signal;
- score a fixed small number of lag/phase states across consecutive windows;
- include bounded transition penalties for implausible tempo/phase jumps while
  preserving legitimate S6 dynamic-tempo behavior;
- publish only through the existing S4/S6 grid contracts; do not introduce a
  new public result or wire format;
- keep production candidate ordering and serialization invariants intact;
- add deterministic tests for half/double time, phase drift, tempo changes,
  short evidence, final refresh, rollover and cancellation.

Promotion checkpoint:

- selected period approaches the existing top-three oracle without trading
  correct selections away: target at least 47/60 period-correct on the spent
  set, no more than two period breaks, and positive external-development
  transfer;
- grid confidence must not become more optimistic on wrong results;
- CPU, workspace and result-pool deltas are measured against the P4 profile.

If the top-three oracle itself remains below the development target after the
new onset evidence, return to work package 1 rather than adding selector rules.

## Work package 3 — meter and downbeat on the stabilized lattice

**Status:** closed without default promotion. The bounded three-band phase path
adds four correct downbeats with zero breaks across 140 already-open tracks but
remains far below the 80% external-development target because the upstream
lattice did not qualify. Production meter/downbeat remains unchanged and both
formal holdouts remain unopened.

**Hypothesis:** once beat period and phase are reliable, bar phase can be chosen
from the temporal pattern of low/mid/high accents rather than from a single
aggregate onset sequence.

Implementation:

- retain the existing 3/4 versus 4/4 contract;
- score bar-position evidence over multiple consecutive bars;
- distinguish low-frequency pulse evidence from mid/high backbeat and off-beat
  evidence;
- allow an override only when its margin and temporal consistency satisfy a
  predeclared gate;
- preserve the exact MTRD-to-refined-grid ordinal/Q32 binding;
- extend focused meter/downbeat regressions and the trace taxonomy.

Exit criterion:

- meter remains at or above its existing development baseline;
- downbeat demonstrates a large, transferable gain rather than a small local
  patch: target at least 80% on each open development family before a holdout is
  considered;
- no meter/downbeat high-confidence safety regression and no grid-period break
  caused by the bar-phase path.

## Work package 4 — adaptive harmonic key evidence

**Status:** six transfer attempts are rejected without opening the formal
holdout; the fifth evaluation closed 2026-09-04 and the sixth mean-normalized
I1 evaluation closed 2026-09-10. I1 improved 27/96 -> 37/96 but failed
absolute/per-mode accuracy and introduced 17 high-confidence errors; see
`APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md`. Harmonic-HPCP moved
21/96 to 22/96 on balanced GiantSteps-MTG
development evidence. On a separate 48-major/48-minor development split,
centered correlation moved production from 22/96 to 28/96 with 11 fixes and
five breaks and balanced both modes at 14/48, but remained far below 70% and
introduced 52 new high-confidence errors. That split is spent and the
centered path is diagnostic-only. The exact hashes, resource-neutral result
and fail-closed decision are recorded in
`APTA-1.1-WP4-CENTERED-KEY-CORRELATION-PROTOCOL.md`.
On a genuinely disjoint 96-track, class-balanced FMAK split, bounded temporal
chord-state voting moved production from 20/96 to 38/96 with 24 fixes and six
breaks and repaired much of the major-mode collapse. It was nevertheless
rejected at 41.7% major, 37.5% minor and 36 new high-confidence errors. The
split is spent, the formal holdout remains unopened, and the immutable result
is recorded in `APTA-1.1-WP4-FMAK-TEMPORAL-CHORD-KEY-PROTOCOL.md`.
On a second 96-track class-balanced FMAK selection with zero overlap, soft
equal-window aggregation of all 24 profile scores reduced production from
18/96 to 17/96, with one fix, two breaks and zero new high-confidence errors.
It failed the total, per-mode, improvement and fixes-greater-than-breaks gates;
that split is also spent and the immutable result is recorded in
`APTA-1.1-WP4-FMAK-TEMPORAL-PROFILE-KEY-PROTOCOL.md`.
The next disjoint 72-track FMAK split tested equal three-probe semitone-band
integration instead of another profile or temporal rule. Default 14/72 became
15/72, with major 0/36, minor 15/36, three fixes, two breaks and one new
high-confidence error. Total/per-mode/safety gates failed despite full software
passes; that split is now spent. The pre-registered protocol and immutable
outcome are in `APTA-1.1-WP4-FMAK-SEMITONE-BAND-KEY-PROTOCOL.md`.

The follow-up synthetic diagnostic at `b9c50df` passes all 24 ideal-profile and
triad identities but reproduces the mode collapse through the native PCM path.
Independent score calculations match all native top-three decisions. Before
another representation experiment, compare extraction with an independent
high-precision resonator/decimator reference to distinguish numerical defects
from leakage/compression/folding effects. Do not treat this as permission to
revive rejected centered correlation. Exact scope/results are recorded in
`APTA-1.1-KEY-MODE-DIAGNOSTIC.md`.

That numerical follow-up is now complete at `f31d0e1`: effective and nominal
double Fourier references produce zero changed tonic/mode decisions in 576
PCM rows per build, despite small chroma differences. Arithmetic precision is
not a sufficient repair for these fixtures. The next candidate must address
tonal representation/contrast with a separately frozen protocol, not merely
switch all arithmetic to double or reopen rejected centered correlation. See
`APTA-1.1-KEY-EXTRACTION-REFERENCE.md` for the measured scope and limitations.

The subsequent source audit, independent blind review and automated-reference
screen are complete at `c5ef089`; see `APTA-1.1-KEY-BLIND-REVIEW.md`. Both
listeners agree on the nine selected FMAK disagreements. OpenKeyScan reaches
8/9 on that consensus subset and agrees with fixed Essentia on 50/72 spent
tracks; the suggested Librosa/Krumhansl implementation reaches only 4/9 and is
not worth scaling. The 22 OpenKeyScan/Essentia disagreements are the bounded
resume set for trace/error-family inspection. They may generate hypotheses but
must not be treated as ground truth, used to auto-relabel FMAK, or scored as a
promotion/acceptance set.

**Hypothesis:** the current global folded chroma is underdetermined on full
mixes. Combining tuning-aware harmonic salience with robust temporal evidence
can reduce neighbouring-key and relative/parallel-mode errors.

Implementation order:

1. **Complete 2026-09-05:** the frozen 22-case topology contains eight same-tonic
   mode swaps, six fourth/fifth relationships, three relative keys and five
   other cross-mode differences. Native minor selection is 70/72, including
   18/19 external-major agreements; only two disputed cases have two-listener
   consensus. See `APTA-1.1-KEY-BLIND-REVIEW.md` for limits and exact evidence.
2. **Complete 2026-09-05:** the separately frozen synthetic per-window contrast
   observer identifies loss after compression/folding: first clean major
   windows change from raw-folded 12/12 to native 7/12 default and 2/12 band.
   All original 720 rows per build and production analyzer/object hashes stay
   identical. See `APTA-1.1-KEY-CONTRAST-TRACE.md`. The frozen gain follow-up
   is also complete (2026-09-05 runs, 2026-09-10 verified report): changing
   gain alone changes clean-major default final matches from 12/12 at 1/16
   to 2/12 at 2, with exact gain-squared raw-energy scaling and unchanged raw
   argmax. See `APTA-1.1-KEY-GAIN-RESULT.md`. The subsequent frozen mean-energy
   candidate is **closed 2026-09-10, rejected on cost**: all synthetic gates
   pass (35 -> 56/72, 22 fixes/one break, no confident errors), but CPU ratio
   1.172285 >1.15 and stack +400 >192 bytes fail. See
   `APTA-1.1-KEY-MEAN-NORMALIZATION-RESULT.md`. The separately preregistered
   **cost I1 passes** with exact report/evaluator identity, +64 bytes stack,
   median CPU I1/default 0.997090 and I1/original 0.855793. All software
   matrices pass; see `APTA-1.1-KEY-MEAN-COST-I1-RESULT.md`. Its subsequent
   disjoint MTG comparison is **rejected**: 27/96 -> 37/96, 13 fixes/three
   breaks, major 11/48, minor 26/48 and 17 new high-confidence errors. See
   `APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md`. Next preregister a tonal-evidence
   diagnostic separating frequency coverage from ranking/confidence; do not
   retune normalization or confidence on the newly spent 96-track split.
   No fitted floor, gain workaround, parameter sweep or label rescue is justified.
3. Replace fixed global accumulation in an experimental path with bounded
   per-window normalization and robust/adaptive aggregation.
4. Improve harmonic salience from the retained octave-resolved spectrum while
   preventing low-frequency fifths and loud frames from dominating.
5. Evaluate continuous or finer tuning estimation only if it can reuse bounded
   evidence at acceptable CPU cost; the existing three-bank experiment remains
   diagnostic until its cost is justified.
6. Gate a candidate verdict by temporal agreement and calibrated separation;
   do not compare raw scores from differently shaped evidence spaces.
7. Prepare a legally usable independent key-development set before promotion.

Retain/reject criterion:

- retain an iteration only when it has positive net fixes on the spent set,
  zero new high-confidence errors and a clear gain on the independent
  key-development set;
- do not approach a formal holdout until exact key accuracy is at least 70% on
  independent development evidence and the remaining error taxonomy shows a
  plausible path to the frozen 75% gate;
- measure resonator work, refresh cost and key-analysis state growth for every
  retained candidate.

## Work package 5 — integrated release candidate

**Status:** closed as a software-qualified baseline at
`cfb811a96af4202f266d58fc8a74e484b189cf59`; not algorithmically eligible for
WP6. Rejected experimental branches were retired, retained diagnostics pass
their focused matrix, and the exact default Release, sanitizer, analyzer-hash
and resource evidence is green. Because WP1 through WP4 promoted no candidate
and the retained production metrics miss their transfer gates, the formal
holdouts remain unopened. See `APTA-1.1-WP5-INTEGRATION-AUDIT.md`.

Combine only retained lattice, downbeat and key candidates. Remove superseded
experimental branches and keep one auditable candidate path.

Required verification:

- default and candidate Werror matrices;
- ASan/UBSan candidate matrix;
- unit, integration, serialization, ABI/layout and package tests;
- clean corpus analyzer/export/evaluator round trip;
- explicit fixes/breaks and confidence-safety reports;
- workspace, result-pool, stack/state and CPU comparison;
- no changes to stable 1.0 semantics, frozen acceptance thresholds or private
  evidence boundaries.

The integrated candidate may proceed only when all open development sets show
transfer and no unresolved operational or safety regression remains.

## Work package 6 — one-shot formal holdouts

Freeze source, flags, parameters and tests before opening any holdout. Run each
formal Ballroom/ASAP holdout once and record a retain/reject decision. A failed
holdout returns the candidate to development with that holdout considered
spent; it must not become an iterative tuning set.

Proceed only if meter/downbeat/lattice transfer remains strong and the complete
regression matrix is green. A key holdout follows the same rule once a suitable
independent key protocol has been frozen.

## Work package 7 — new final DJ acceptance corpus

Follow `APTA-1.1-QUALIFICATION-RUNBOOK.md` exactly:

1. select and canonicalize at least 48 genuinely new tracks;
2. obtain independent musician verification without showing APTA output;
3. freeze opaque IDs, canonical WAV hashes and labels;
4. build the exact clean candidate and record analyzer/inspector hashes;
5. run anonymous `--features all` analysis once;
6. export completed FINAL results;
7. execute the unchanged frozen evaluator and retain the complete report.

All final gates are conjunctive: key >=75%, meter >=95%, downbeat >=90%,
beatgrid >=90%, beat-period error <=1%, cyclic downbeat error <=0.10 beat, and
no more than 5% high-confidence errors per family at confidence >=75.

Any failed gate rejects the candidate. Do not tune against that corpus.

## Work package 8 — physical ESP32-P4 evidence (parallel track)

**Status:** in progress; v1.3 diagnostic passed, qualifying harness open. The
2026-08-29 readiness remediation is complete at
`0fe1c22e44e759db3675a289e859b14a085c31e0`: the exact ESP-IDF 6.0.2 image,
PSRAM/32,768-frame profile, 12-feature example and 12-feature capacity probe all
verify. Revision `18ade2ed13da23585d9ee10826056c83e3ded9a1` selects the
supported early-P4 path, and its metadata-verified image was normally flashed
to the v1.3 board on COM4. Boot, 32 MiB PSRAM test and the complete diagnostic
feature sweep passed. This is physical diagnostic evidence, not the qualifying
USB/audio run; exact results and the remaining boundary are frozen in
`APTA-1.1-WP8-READINESS-AUDIT.md`.

This work can start as soon as hardware is available and should run in parallel
with algorithm development, then be repeated for the exact integrated
candidate if its binary or memory profile changes.

- flash the exact ESP-IDF 6.0.2 `esp32p4` build;
- run all release-target DJ features continuously for at least 1,800 seconds;
- collect real workspace/result-pool, heap/PSRAM, p99/max process latency,
  allocation, deadline, input-drop, thermal and USB/audio coexistence evidence;
- validate with `tools/apta_1_1_p4_hardware_evidence.py`;
- commit only the privacy-safe validated JSON evidence.

Synthetic or host-generated JSON cannot close this blocker.

## Work package 9 — release freeze and publication

Only after work packages 5 through 8 pass:

1. close the readiness evidence blockers and require `freeze-eligible`;
2. generate the pre-freeze snapshot from a clean exact checkout;
3. freeze final API/ABI/wire documents and deliberately update version metadata;
4. regenerate package and release evidence;
5. rerun the complete native/shared/ILP32/ESP-IDF/P4/fuzz/container/package
   matrix against the exact candidate;
6. review the exact tag commit, create `v1.1.0`, publish release artifacts and
   perform the guarded registry publication with owner credentials.

## Execution order and checkpoints

| Order | Work package | Decision checkpoint |
|---:|---|---|
| 1 | WP0 — harness | deterministic baseline and privacy-safe comparison |
| 2 | WP1 — onset evidence | >=5 net fixes, <=1 break, positive external transfer |
| 3 | WP2 — lattice tracker | >=47/60 spent-set period oracle approach and transfer |
| 4 | WP3 — downbeat | >=80% on each open development family, meter preserved |
| 5 | WP4 — key | >=70% independent development accuracy, safety clean |
| 6 | WP5 — integration | complete software/resource matrix green |
| 7 | WP6 — holdouts | one-shot transfer retain decision |
| 8 | WP7 — final corpus | every frozen DJ gate passes |
| parallel/final | WP8 — P4 hardware | validated exact-candidate physical evidence |
| last | WP9 — freeze/release | exact release matrix, tag and publication |

The ESP32-P4 control path is available on COM6 through the board's CH340 bridge.
The exact-head WP8 UAC build, metadata check, normal flash and boot passed on
the v1.3 target, but Windows did not enumerate the separate frozen USB-OTG UAC
endpoint, so the 1,800-second evidence clock correctly did not start. Six key
transfer attempts are closed and rejected without opening the formal holdout;
the fifth semitone-band candidate failed total/per-mode/safety gates on 72
development tracks (evaluation closed 2026-09-04).
The FMAK temporal chord-state candidate produced positive net fixes
but failed the frozen absolute, per-mode and confidence-safety gates; the
subsequent disjoint soft-profile candidate reduced exact accuracy despite zero
new high-confidence errors. Both splits are spent. None of the harmonic,
centered or temporal results authorizes neighboring parameter, confidence or
threshold rescues. The semitone-band split is also spent; a future front-end
candidate needs its own pre-registration and genuinely disjoint development
evidence, and must not reinterpret any rejected result.
The 2026-09-04 blind-review and automated-triage audit closes the corpus-mapping
question without changing that boundary. The 2026-09-05 frozen 22-case topology
follow-up is now complete and retains a mode/contrast diagnostic hypothesis.
The subsequent frozen per-window contrast observation is also complete and
locates synthetic loss after compression/folding with additional accumulation
loss. The bounded input-gain diagnostic is complete and confirms synthetic
gain dependence with unchanged raw-energy decisions. The mean-normalization
candidate passes the synthetic screen but its original implementation failed
the frozen CPU and stack limits. The separate cost I1 passes every
identity/software/resource gate, but its disjoint 96-track MTG development
comparison now rejects the detector: 37/96 exact and 17 new high-confidence
errors. The split is spent; preserve the original representation, confidence
and label seals. Resume with a separately preregistered tonal-evidence
diagnostic, not confidence or parameter rescue on this result. No specific
cause of the remaining real-audio errors has been established. Automated
agreements are not corrected truth.
WP6 and WP7 remain gated: WP5 proved the unchanged production baseline is
software-clean but not algorithmically eligible, so neither a formal holdout
nor a new final acceptance corpus may be opened until a complete transferable
candidate satisfies the WP1-WP4 development gates.
