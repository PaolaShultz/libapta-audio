# APTA 1.1 development status

- **Branch:** `1.1.0` — the branch ref is authoritative for the current development head; this document intentionally does not mirror a mutable head SHA.
- **Last DSP/serialization qualification baseline:** `d17c3671ff5318d58847643537d7e0da7667e262` (native key/meter CLI integration and MTRD/grid fixes).
- **Current qualification-tooling baseline at this audit:** `2953401f6ee46fcf966f0b384364e510b974bf4e` (privacy-safe corpus runner plus canonical corpus preparation/labeling); its PR exact-head CI, Security, native all-feature smoke, corpus preparation/labeling, tempo and confidence workflows passed.
- **Release status:** development; no `v1.1.0` release claim. `VERSION` remains `1.0.1`.

## Current boundary

The 2026-09-12 **two-experiment search checkpoint is complete**: S2 passes
16/16 new quadratic/tone cases and S3 passes 36/36 new paired clean/40 dB/20 dB
cases. All terminate within the frozen budget and deterministic replay passes.
Retain unchanged S2 only as a bounded numerical reference for an offline
end-to-end key candidate; supplied tone count and local frequency neighborhoods
remain major assumptions. No complete key candidate or release gate is accepted.
The next deliverable is a frozen PCM-to-key pipeline design and implementation
with seed discovery, unknown component selection, harmonic attribution,
confidence and whole-pipeline cost, followed by independent development evidence.
The agreed two experiments are spent: do not start another solver-only probe.
See the [decision](APTA-1.1-KEY-TWO-EXPERIMENT-CHECKPOINT.md),
[S2 result](APTA-1.1-KEY-QUADRATIC-SEARCH-RESULT.md) and
[S3 result](APTA-1.1-KEY-SEARCH-FINAL-CHECK-RESULT.md).

The 2026-09-12 S1 search-termination screen is **rejected overall**: all eight
new tone cases and six/eight quadratics pass, while two high-curvature-ratio
quadratics explicitly exhaust the evaluation budget. Keeping poll step after
improvement fixes four tone and three quadratic results versus R2, with zero
accuracy breaks. Finite poll resolution is not a global convergence guarantee.
Its subsequent S2 direction and S3 noise screens are complete as recorded above;
they do not rewrite this historical rejection.
No production/corpus change. See
[`APTA-1.1-KEY-SEARCH-CONVERGENCE-RESULT.md`](APTA-1.1-KEY-SEARCH-CONVERGENCE-RESULT.md).

The 2026-09-12 R3 noise/unequal-amplitude screen is **rejected**: 30/36 pass,
including only 8/12 new clean cases, 10/12 at 40 dB and 12/12 at 20 dB under
different noise-specific tolerances. All failures concern unequal-amplitude
close tones. True-frequency fits remain feasible, exposing a bounded-search
limitation rather than proving unavoidable ambiguity. Its subsequent S1
termination diagnostic above is now complete and rejected under its full bank.
Numerical controls and replay pass; no production/corpus change. See
[`APTA-1.1-KEY-NOISE-ROBUSTNESS-RESULT.md`](APTA-1.1-KEY-NOISE-ROBUSTNESS-RESULT.md).

The 2026-09-12 R2 independent two-tone refinement screen passes 32/32 recovery
cases and six constraint stresses. Maximum sorted frequency error is 5.067e-9
Hz on noiseless synthetic signals; 742 search candidates reject for amplitude.
Over-budget sources yield poor admissible fits, never successful reconstruction.
Tone count and local seed neighborhoods remain supplied. The subsequent R3
noise/unequal-amplitude screen above is complete and rejected.
No music applicability, native port or C3 rescue is claimed. See
[`APTA-1.1-KEY-INDEPENDENT-SHIFT-RESULT.md`](APTA-1.1-KEY-INDEPENDENT-SHIFT-RESULT.md).

The 2026-09-12 R1 bounded common-frequency refinement screen passes 48/48
synthetic cases with supplied tone count/spacing. Maximum shift error is
9.278e-8 Hz, with 48 reconstruction fixes and zero breaks. A raw-matrix rank
guard and explicit synthetic amplitude budget replace unconstrained acceptance;
none of the 2832 bank candidates triggers rejection, so active-constraint
behavior is covered only by targeted tests in R1. Its subsequent R2 independent
per-tone screen above now passes a new analytic bank and constraint stresses.
No music applicability, C3 rescue or native port is claimed. See
[`APTA-1.1-KEY-LOCAL-SHIFT-RESULT.md`](APTA-1.1-KEY-LOCAL-SHIFT-RESULT.md).

The 2026-09-12 C3 observable frequency-uncertainty screen is **rejected**:
50/1024 perturbed cases pass, with zero family/outcome changes from C2.
Analytic removal of invisible columns eliminates the rounded unphysical
amplitudes but leaves all 32 nearest-Hz reversals. Quarter-Hz rankings remain
correct while reconstruction fails; noninteger fits still admit large physical
coefficients. All 1280 rows/40 models complete without abstention and numerical
controls pass. The subsequent R1 numerical common-shift screen above now
passes its bounded analytic bank; independently erroneous component frequencies
remain untested. No production/corpus change. See
[`APTA-1.1-KEY-OBSERVABLE-FREQUENCY-RESULT.md`](APTA-1.1-KEY-OBSERVABLE-FREQUENCY-RESULT.md).

The 2026-09-12 O1 numerical observability instrument passes its independent
24-case bank: 12 ready fits, four exact invisible cases and eight weak-component
abstentions. Analytic columns preserve structural zeros and prevent their
normalization into fit directions; the precision guard is not a physical
amplitude or noise model. O1 did not recompute C2 family verdicts. Its separately
preregistered follow-up C3 above is now complete and rejected.
No production/corpus change. See
[`APTA-1.1-KEY-OBSERVABILITY-RESULT.md`](APTA-1.1-KEY-OBSERVABILITY-RESULT.md).

The 2026-09-12 C2 frequency-uncertainty screen is **rejected**: only 50/1024
perturbed cases pass both gates. Quarter-Hz perturbations preserve all 768
family rankings but exceed the frozen 10% reconstruction ceiling; nearest-Hz
rounding produces 32 reversals and 206 reconstruction failures. Rounded
out-of-range columns expose normalization of near-roundoff energy, yielding
unphysical fitted coefficients, so those reversals are not a clean physical
ambiguity measure. Exact C1 controls remain 256/256 and all source signals are
unchanged. The subsequent O1 numerical instrument screen above addresses
structural zeros and weak-component abstention; frequency robustness remains
unproven. No production/corpus change. See
[`APTA-1.1-KEY-FREQUENCY-UNCERTAINTY-RESULT.md`](APTA-1.1-KEY-FREQUENCY-UNCERTAINTY-RESULT.md).

The 2026-09-12 C1 coherent supplied-frequency screen passes 256/256 new-phase
observations, versus unchanged F2 255/256 on that same bank. Correct-family
residual is at most 3.309e-16; wrong-family residual is at least 0.105737.
All old F2/F1 controls replay exactly. Frequencies are supplied, phases and
amplitudes fitted; this is not note discovery or key accuracy. No frontend is
retained or ported. Its separately frozen frequency-uncertainty screen above
is now complete and rejected. Production/corpus and H1/F2 boundaries remain. See
[`APTA-1.1-KEY-COHERENT-RESULT.md`](APTA-1.1-KEY-COHERENT-RESULT.md).

The 2026-09-11 F2 unknown-phase screen **rejects the phase-marginal scoring
construction**: 252/256 pass, but four harmonic observations prefer the wrong
reference; the rule required 256/256. Original F1 rows replay 8/8 exactly,
instrument/resource checks pass, and no production/corpus changes occur.
F1 remains a fixed-phase finding, not robust frontend evidence. This motivated
the separately preregistered C1 diagnostic above; F2 was not optimized. See
[`APTA-1.1-KEY-PHASE-ROBUSTNESS-RESULT.md`](APTA-1.1-KEY-PHASE-ROBUSTNESS-RESULT.md).

The 2026-09-11 F1 within-cell diagnostic is complete: all eight fixed-phase
counterexample windows (four distinct ideal spectra) remain distinguishable
after each cell's total energy is removed. Fine distance to the alternative is
0.238..0.516 versus 1.76e-9..3.59e-9 to the known-source reference; all eight
pass the frozen margin. Actual coarse totals also differ, so this does not
prove that only fine evidence separates the waveforms. H1 stays rejected and
no frontend is retained. The separately preregistered phase screen above is
now complete and rejects its phase-marginal construction. See
[`APTA-1.1-KEY-WITHIN-CELL-RESULT.md`](APTA-1.1-KEY-WITHIN-CELL-RESULT.md).

The 2026-09-11 identifiability diagnostic is complete: eight window pairs
(four distinct ideal spectra) admit different minor/relative-major fundamental
interpretations while both use <=6 columns and retain identical 36-cell energy.
The 26 duplicate single-column pairs preserve pitch class and alone do not
explain those mode errors. A known-note support fit improves the actual H1
residual in 0/576 windows, including 0/14 local errors; this is not a global
optimality proof. H1 remains rejected. This motivated the fixed-reference
within-cell diagnostic above, now complete without selecting a frontend.
Production bytes and corpus seals are unchanged. See
[`APTA-1.1-KEY-IDENTIFIABILITY-RESULT.md`](APTA-1.1-KEY-IDENTIFIABILITY-RESULT.md).

The 2026-09-11 harmonic-attribution H1 follow-up is **rejected** under its
frozen synthetic gate: final keys reach 144/144, but missing-fundamental local
chords reach only 84/96 versus required >=89/96. All 12 misses select the
relative major for a minor chord. No new confident errors occur, host resource
and instrument checks pass, and production bytes are unchanged. No music was
opened. This motivated the separately preregistered identifiability diagnostic
above, now complete; H1 was not retuned. See
[`APTA-1.1-KEY-PARTIAL-ATTRIBUTION-RESULT.md`](APTA-1.1-KEY-PARTIAL-ATTRIBUTION-RESULT.md).

The 2026-09-10 synthetic tonal-coverage diagnostic is complete. At +/-1/3
semitone, dense cell energy has lower normalized error and, with the unchanged
mean normalization/selector, restores both conditions to 24/24. It also breaks
two missing-fundamental progressions (24/24 -> 22/24); even the known-component
oracle reaches only 21/24 there. No candidate is retained. Production analyzer
and key-object bytes, all 720 old rows per build, and the release/corpus
boundaries are unchanged. This motivated the separately preregistered H1
experiment above, which is now complete and rejected. See
[`APTA-1.1-KEY-COVERAGE-RESULT.md`](APTA-1.1-KEY-COVERAGE-RESULT.md).

The reusable 1.1 infrastructure, native meter/key implementation and complete desktop qualification path are in place. Tempo/grid and confidence acceptance evidence is retained. WP5 closed at `cfb811a96af4202f266d58fc8a74e484b189cf59` as a software-qualified, byte-stable production baseline after rejected experiments were retired, but it is not algorithmically eligible for WP6. The independent 60-track final DJ attempt is formally rejected, leaving a transferable replacement algorithm, physical ESP32-P4 measurements and final release freeze as the active blockers. Formal ASAP/Ballroom/GiantSteps holdouts and a new final corpus remain unopened.

| Work item | Status | Delivered boundary |
|---|---|---|
| 1. APTA 1.1 result model | Complete | Feature bits, key/meter/quality views, initializers, accessors and 32/64-bit layout evidence |
| 2. External result builder | Complete | Bounded validated deep-copy import, provenance, all current feature setters and immutable finalization |
| 3. Container DJ sections | Complete | Deterministic `MKEY`, `MTRD`, `CONF` read/write, strict validation, golden fixture and frozen-reader compatibility |
| 4. Streaming container I/O | Complete | Output/input callbacks, bounded serialization, selective parsing, caller scratch and buffer equivalence |
| 5. Tempo/grid ensemble | **Accepted 2026-08-25** | Relation-aware recovery plus confidence-gated close-candidate arbitration and dominant S6 segment-family selection passed all five frozen gates on a formal 48-track owner-supplied fresh set (exact within 1% 25 -> 29, zero broken selections, no safety regressions); historical 188-row regression clean; see [`APTA-1.1-TEMPO-ENSEMBLE-EVALUATION.md`](APTA-1.1-TEMPO-ENSEMBLE-EVALUATION.md) |
| 6. Confidence calibration contract | Complete | Deterministic isotonic fitting/evaluation protocol and data-separation gate; **production model accepted and integrated 2026-08-25** — `isotonic-pav-clamped-v1` (model ID 1867860160) passed both frozen gates on a 48-row untouched holdout (Brier 0.179 -> 0.152, ECE 0.282 -> 0.198, high-confidence errors preserved at zero) and now publishes an optional BPM quality record; see [`APTA-1.1-CONFIDENCE-CALIBRATION-PROTOCOL.md`](APTA-1.1-CONFIDENCE-CALIBRATION-PROTOCOL.md) |
| 7. Native meter/downbeat | Complete implementation / no promoted lattice candidate | Bounded 3/4 vs 4/4 plumbing is complete. A conservative opt-in 3-band phase experiment adds four correct downbeats with zero breaks across 140 already-open development tracks, but absolute accuracy remains far below the release gate. Three temporal-lattice selectors are rejected. The 2026-09-04 coverage diagnostic found no benefit from distinct local-peak selection (ASAP 2/40 unchanged; Ballroom 17/40 -> 12/40); no native selector changed. See [`APTA-1.1-LATTICE-COVERAGE-AUDIT.md`](APTA-1.1-LATTICE-COVERAGE-AUDIT.md). Both formal holdouts remain closed |
| 8. Native musical key | Sixth transfer candidate rejected | Mean-normalized I1 passes synthetic and host-cost gates but fails disjoint MTG development: 27/96 -> 37/96, major 1/48 -> 11/48, minor unchanged 26/48, and 17 new high-confidence errors. All 192 native outputs completed and validated. The 96-track selection is spent; both experimental options stay disabled and the formal 48-track holdout remains unopened. The prior five attempts remain rejected. See [`APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md`](APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md) |
| 9. Progressive publication | Complete implementation | Provisional -> stable -> final generations with retained-result immutability verified end to end |
| 10. ESP32-P4 CI/capacity | Complete CI/layout evidence | ESP-IDF 6.0.2 `esp32p4` firmware build plus deterministic 30-minute bounded-capacity probe |
| 11. Final DJ acceptance contract | Complete | Frozen fresh-corpus evaluator and thresholds for key, meter, downbeat, grid and high-confidence safety |
| 12. Qualification execution path | Complete infrastructure | Canonical WAV preparation, local labeling, privacy-preserving freeze, anonymous native `--features all` analysis, FINAL-only export and frozen acceptance scoring |
| 13. WP5 integrated baseline | **Software-qualified / algorithm gate failed** | Exact clean Release 121/121, ASan/UBSan 116/116 and retained-diagnostics focused 8/8 pass; default analyzer bytes and P4 capacity are unchanged, but no WP1-WP4 candidate qualified for promotion or WP6 |

The public development guide is [`../api/APTA-API-1.1-DEVELOPMENT.md`](../api/APTA-API-1.1-DEVELOPMENT.md), the DJ wire contract is [`../../specification/APTA-1.1-DJ-SECTIONS.md`](../../specification/APTA-1.1-DJ-SECTIONS.md), streaming behavior is [`../file-format/APTA-STREAMING-IO-1.1.md`](../file-format/APTA-STREAMING-IO-1.1.md), final corpus scoring is frozen in [`APTA-1.1-DJ-ACCEPTANCE-PROTOCOL.md`](APTA-1.1-DJ-ACCEPTANCE-PROTOCOL.md), and the operational qualification sequence is [`APTA-1.1-QUALIFICATION-RUNBOOK.md`](APTA-1.1-QUALIFICATION-RUNBOOK.md).

The ordered engineering sequence for closing the remaining algorithm,
acceptance, hardware and freeze blockers is
[`APTA-1.1-ALGORITHM-IMPLEMENTATION-PLAN.md`](APTA-1.1-ALGORITHM-IMPLEMENTATION-PLAN.md).

The 2026-09-04 synthetic key-mode diagnostic confirms correct selector rotation
and mode identity on all 24 ideal profiles/triads, but reproduces the major-mode
collapse through native PCM (clean four-chord major progressions: default 4/12,
semitone-band 0/12). The common-floor/raw-cosine interaction is consistent with
these observations; extractor numerical correctness and real-song causality
remain unproven. No detector was changed or promoted. See
[`APTA-1.1-KEY-MODE-DIAGNOSTIC.md`](APTA-1.1-KEY-MODE-DIAGNOSTIC.md).

The follow-up independent Fourier/double extraction reference changes no
tonic/mode decision in 576 PCM rows per build, for either effective-native or
nominal-double frequencies/averaging. Numerical precision alone therefore does
not repair the synthetic collapse; representation contrast remains the next
research boundary. This is not a general proof of extractor correctness or
real-song causality. See
[`APTA-1.1-KEY-EXTRACTION-REFERENCE.md`](APTA-1.1-KEY-EXTRACTION-REFERENCE.md).

The source archive and all twelve targeted review WAVs were independently
re-decoded with exact full-file and PCM identity. Two listeners then agreed on
all nine FMAK disagreements. OpenKeyScan agreed with the first listener on
11/12 and the two-listener subset on 8/9; the suggested Librosa/Krumhansl
baseline reached only 5/12 and 4/9 and was stopped. On all 72 spent tracks,
OpenKeyScan agrees with fixed Essentia on 50 and leaves 22 disagreement cases
for optional diagnostic triage. These comparisons do not relabel FMAK, qualify
a native candidate or create acceptance evidence. Exact hashes, analyzer
identity and source-preservation checks are in
[`APTA-1.1-KEY-BLIND-REVIEW.md`](APTA-1.1-KEY-BLIND-REVIEW.md).

The 2026-09-05 report-only topology follow-up is complete: the 22 disagreements
contain eight same-tonic mode swaps, six same-mode fourth/fifth relationships,
three relative keys and five other cross-mode differences. Native APTA returns
minor on 70/72 tracks, including 18/19 cases where both external references
agree on major. Only two of the 22 have retained two-listener consensus, so
this is a diagnostic mode-asymmetry observation, not corrected truth. It
motivated the separately frozen contrast trace below before selecting a new
representation experiment. No candidate or holdout is promoted;
see the final section of `APTA-1.1-KEY-BLIND-REVIEW.md` and
[`APTA-1.1-KEY-DISAGREEMENT-TOPOLOGY.md`](APTA-1.1-KEY-DISAGREEMENT-TOPOLOGY.md).

That contrast trace is now complete on the fixed synthetic progressions. On
clean first major-chord windows the raw-folded counterfactual matches 12/12 in
both builds, while the unchanged compressed native result matches 7/12 default
and 2/12 band; four-window cumulative results remain 4/12 and 0/12. All original
720 diagnostic rows per build and production analyzer/key object hashes are
unchanged. This localizes an observed compression/contrast loss on synthetic
stimuli, not a real-song fix. It motivated the gain-sensitivity diagnostic
below before selecting one new normalization/contrast experiment. See
[`APTA-1.1-KEY-CONTRAST-TRACE.md`](APTA-1.1-KEY-CONTRAST-TRACE.md).

The fixed input-gain follow-up is complete (runs 2026-09-05, evidence verified
and documented 2026-09-10). Clean major final matches at gains 1/16, 1/4, 1 and
2 are default 12/12, 9/12, 4/12, 2/12 and band 11/12, 2/12, 0/12, 0/12.
Exact sample reversibility, raw-energy gain-squared scaling and unchanged raw
argmax confirm gain sensitivity in the synthetic compression/scoring path.
Production analyzer/object bytes remain unchanged. This motivated the frozen
per-window energy-normalization candidate below; see
[`APTA-1.1-KEY-GAIN-RESULT.md`](APTA-1.1-KEY-GAIN-RESULT.md).

The 2026-09-10 mean-energy normalization candidate passes all six synthetic
gates (35 -> 56/72 final matches, 22 fixes/one break, zero high-confidence
errors, identical normalized evidence at all four gains), but is **rejected
on resource gates**: median host CPU ratio 1.172285 exceeds 1.15 and extra
compiler-accounted stack is 400 bytes versus the 192-byte limit. Default
production bytes remain unchanged. Native default/candidate Release tests
pass 118/118 and 119/119; candidate ASan/UBSan passes 116/116. No independent
development set or holdout was opened. This rejection and the detuned weakness
(8/24) remain recorded; the separate cost-only follow-up is complete below.
See [`APTA-1.1-KEY-MEAN-NORMALIZATION-RESULT.md`](APTA-1.1-KEY-MEAN-NORMALIZATION-RESULT.md).

The separately preregistered **cost I1 passes** at
`a883dd6d0d50d4f463d8347352d75891d9005fba`: every gain report and the evaluator
remain byte-identical, while extra project stack falls to 64 bytes. Seven
longer host timing triples yield median I1/default 0.997090 and
I1/original-normalized 0.855793; every timed interval exceeds 500 ms. All
four software matrices pass (118/119/119 Release tests and 116 sanitizer
tests). This retained the implementation for the disjoint comparison below,
not promotion or WP6 eligibility. Both options stay off by default. See
[`APTA-1.1-KEY-MEAN-COST-I1-RESULT.md`](APTA-1.1-KEY-MEAN-COST-I1-RESULT.md).

That disjoint MTG comparison is now **complete and rejected**. Published
confidence-2 labels were frozen for 96 unused tracks (48/48 major/minor), with
zero ID/transport overlap and zero WAV/PCM overlap against 556 prior recordings.
Default/I1 exact results are 27/96 and 37/96 (13 fixes, three breaks, 34 changed
verdicts). Major improves 1/48 -> 11/48; minor remains 26/48. High-confidence
errors rise 2 -> 19, with 17 newly unsafe outputs. Total, per-mode and both
confidence-safety gates fail. No labels, thresholds or selected tracks were
changed; the split is spent and holdouts stay unopened. Next preregister a
tonal-evidence diagnostic that distinguishes frequency coverage from ranking
and confidence behavior; do not tune this detector against the spent split.
See [`APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md`](APTA-1.1-WP4-MTG-MEAN-KEY-RESULT.md).

## Implemented compatibility guarantees

- Existing `TEMP`, `LGRD`, `GGRD`, `REVN`, waveform and metadata semantics are unchanged by absence of the new optional sections.
- `MKEY`, `MTRD` and `CONF` follow the container-v1 optional-section evolution rule; frozen 1.0 consumers validate common framing and skip them.
- Canonical output is deterministic and reserved bytes are zero.
- Builder/parser enforce range, ordering, count, cross-feature and aggregate-allocation limits before publishing immutable results.
- MTRD integer downbeats bind to the same grid whole-frame component and ordinal. A non-zero Q32 grid remainder is valid because MTRD does not encode fractional frame bits.
- Streaming and buffer writers produce byte-identical canonical output for the same result/options.
- Meter and key use the established immutable-generation lifetime model.

These are development-branch guarantees backed by tests, not yet a tagged stable 1.1 compatibility promise.

## Native DJ qualification path

Native meter/downbeat and musical-key analysis publish through the same immutable result generations as waveform/tempo/grid features. Meter scoring may use quantized onset bins, but publication resolves the selected ordinal through the exact refined S4 grid Q32 period and stores that beat's whole-frame component in MTRD. Builder, writer and reader use the same whole-frame + ordinal contract for explicit, segmented and hybrid grids.

Musical-key ranking is performed at higher precision, then serialized `uint16_t` scores are forced strictly descending so quantization cannot turn a valid native result into an unserializable MKEY candidate list.

The desktop CLI path has an end-to-end Actions smoke test that executes real WAV analysis with `apta-analyze --features all` and requires serializable final `MKEY` and `MTRD` output through `apta-inspect`.

The qualification tooling then provides the full private-corpus path:

1. canonicalize local MP3/FLAC/WAV material to the frozen qualification WAV format;
2. label canonical WAV frame coordinates locally without remote scripts;
3. freeze labels into opaque SHA-256-derived IDs;
4. re-hash and exactly match the frozen manifest before analysis;
5. present only anonymous `track-<hash>.wav` names to `apta-analyze --features all`;
6. bind run metadata to exact source revision, analyzer hash, manifest hash, output hashes and mapping hash;
7. export only completed/FINAL native key, meter and selected beatgrid results;
8. run the pre-registered acceptance evaluator.

This closes the software-path gap between private source audio and the acceptance evaluator. A 60-track private corpus was selected, canonicalized and later verified in full by an independent musician without APTA output in the listening workbench. The recovered 60-row export deterministically reproduces the frozen labels hash. Evaluation of the retained exact-corpus analyzer results formally rejects the candidate: meter passes, while key, downbeat, beatgrid and key/grid confidence-safety gates fail. The dated preparation, reproducible hashes, corrected metrics and candidate deltas are recorded in [`APTA-1.1-FINAL-DJ-CORPUS-STATUS.md`](APTA-1.1-FINAL-DJ-CORPUS-STATUS.md).

A separate targeted protocol now freezes balanced development and untouched
holdout splits from ASAP and the real-audio Ballroom Rhythm Dataset. The first
development run shows that the conservative 4/4 prior does not generalize:
Ballroom 3/4 meter recall is 1/20 while 4/4 is 20/20, and downbeat is 6/40.
The failure is primarily upstream tempo-family selection: period is within 10%
on 17/20 common-time tracks and 0/20 triple-meter tracks. The holdouts remain
unopened. Exact methodology, hashes and the rejected multiband candidate are in
[`APTA-1.1-METER-DOWNBEAT-VALIDATION.md`](APTA-1.1-METER-DOWNBEAT-VALIDATION.md).

## ESP32-P4 qualification boundary

For 48 kHz / 30 minutes (`86,400,000` source frames), deterministic capacity evidence remains:

- overview columns: **2,637** below the 4,096 design ceiling;
- mutable S6 beat capacity: **3,072**;
- bounded immutable result slots: **2**;
- resident explicit beat records: **9,216** across mutable S6 + two result slots;
- minimum static workspace: **941,216 bytes**;
- recommended static workspace: **1,000,058 bytes**;
- bounded result pool: **537,104 bytes**;
- combined minimum: **1,478,320 bytes**.

At remediation revision `0fe1c22e44e759db3675a289e859b14a085c31e0`, the
corrected 12-feature capacity probe preserves every value above and the exact
ESP-IDF 6.0.2 build produces a 235,024-byte ESP32-P4 v3.1-v3.99 image with
PSRAM and the required 32,768-frame overview profile. Validator unit tests pass
8/8. Revision `18ade2ed13da23585d9ee10826056c83e3ded9a1` corrects the P4
revision profile and produces a normally flashable 233,056-byte v1.0-v1.99
image. Its diagnostic boot on the physical v1.3 board passed the 32 MiB PSRAM
test and full eight-second feature sweep with zero heap delta. This remains
diagnostic rather than qualifying evidence. The real 48 kHz USB/audio path,
1,800-second counters, thermals and final exact-candidate rerun remain open
under the frozen hardware-evidence contract.

## Frozen final DJ acceptance contract

The final evaluator pre-registers these gates:

- at least 48 fresh manually verified tracks;
- exact key accuracy >=75%;
- exact meter accuracy >=95%;
- downbeat phase accuracy >=90%;
- beatgrid accuracy >=90%;
- <=5% high-confidence errors per output family at confidence >=75;
- beat-period tolerance <=1%;
- cyclic downbeat phase tolerance <=0.10 beat.

Do not tune thresholds after examining fresh acceptance results. The old development corpus/holdout is not fresh evidence.

## Remaining blockers before `v1.1.0`

1. ~~Run the relation-aware tempo/grid candidate on genuinely fresh validation evidence and satisfy the frozen evaluation gates.~~ **Closed 2026-08-25** — accepted on a formal 48-track owner-supplied fresh set; all five frozen gates passed (exact within 1% 25 -> 29, zero broken selections, no safety regressions). See [`APTA-1.1-TEMPO-ENSEMBLE-EVALUATION.md`](APTA-1.1-TEMPO-ENSEMBLE-EVALUATION.md).
2. ~~Train calibrated confidence on a separate >=96-row training set and pass an untouched >=48-row disjoint holdout; only then integrate a production `APTA_FEATURE_CALIBRATED_QUALITY` model.~~ **Closed 2026-08-25** — the accepted model and privacy-safe holdout summary are retained under `evidence/1.1`.
3. Produce a transferable replacement candidate that first satisfies the open-development WP1-WP4 gates and one-shot WP6 holdouts, then passes every final key/meter/downbeat/grid/high-confidence gate on a newly verified >=48-track WP7 corpus. WP5 is software-clean but does not authorize either evidence set. The first independent 60-track attempt is frozen and formally rejected; it cannot be reused as fresh acceptance evidence after candidate tuning.
4. Collect physical ESP32-P4 memory/timing/USB/audio coexistence evidence on real hardware.
5. Freeze final 1.1 API/ABI/wire documents, deliberately update version metadata, regenerate release/package evidence, rerun the complete exact-candidate matrix, then tag/publish.

Pajoniiir application concerns such as scanning, catalog, playlists, USB transactions, playback scheduling, Rekordbox import wiring and UI remain outside this repository.

## Release discipline

The stable authority remains APTA 1.0 / package 1.0.1. The frozen 1.0 normative manifest and existing tags must not be rewritten. `VERSION` remains `1.0.1`; the `1.1.0` branch name is only a development-line name.

`release/1.1-readiness.json` is fail-closed: while any external evidence blocker is open, version/package/tag state must remain at the development boundary. Closing all blockers makes the candidate only `freeze-eligible`; it does not automatically release 1.1.
