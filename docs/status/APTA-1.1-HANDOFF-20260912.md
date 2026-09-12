# Development handoff — paused at user request, 2026-09-12

## Resume in the correct checkout

- Active workspace: `D:\AI\LIBAPTA\libapta-audio-dsp-20260904`.
- Branch: `agent/dsp-takeover-20260904`.
- Last complete implementation/evidence checkpoint before this handoff:
  `33cab2d1b2f6d95837fc3968c9c7fc3a299ee224`, pushed and remote SHA verified.
- Main nested checkout `D:\AI\LIBAPTA\libapta-audio` is separate; do not move
  research work there or infer its branch state from this document.
- Existing untracked `output/` is unrelated and deliberately untouched.
- No experiment, service, background goal or automatic follow-up is running.
- User asked to save and pause. Do not run new experiments during this handoff.

At next session read this file, `APTA-1.1-DEVELOPMENT-STATUS.md`,
`APTA-1.1-KEY-JOINT-PCM-PROTOCOL.md` and `APTA-1.1-KEY-JOINT-PCM-RESULT.md`.
Apply the local libapta-dsp-development skill and repository instructions;
verify worktree/status/HEAD before edits. Prior narrow commit/push authorization
persists; preserve unrelated files and verify remote SHA after publication.

## What is completed

The two-experiment local-search limit is exhausted: S2 16/16 and S3 36/36
passed with replay. S2 is only a supplied-two-tone numerical reference, not
unknown-count discovery or a production key detector. No further S4 solver
microexperiment chain was agreed.

E1 implemented a complete PCM-to-key path but was rejected: 85/96 versus
direct peaks 76/96, 20 fixes, 11 breaks, two new high-confidence errors.
Its greedy harmonic allocation remains frozen and rejected.

The user then explicitly requested considered design and internet research
before implementation. E2 replaced greedy allocation with joint regularized
NNLS. Research rationale and primary-source links are in its protocol.

- E2 protocol commit: `2a02d2a`.
- Instrument: `3ca838a87d0c044e987d06125bc1a5e1efd27aa6`.
- Implementation: `tools/apta_key_joint_pcm.py`.
- Frozen evaluator: `tools/apta_key_joint_pcm_screen.py`.
- Tests: `tools/test_apta_key_joint_pcm.py` plus unchanged E1/coverage tests.
- Public evidence: `evidence/1.1/key-joint-pcm-e2-20260912.json`.

E2 is rejected: 126/144 versus direct peaks 130/144, three fixes, seven breaks,
zero high-confidence errors. Five breaks are numerically invalid whole-clip
abstentions; two remain on numerically valid clips. Do not describe this as
a clean algorithmic test or an accepted replacement. Missing family 17/24,
unequal-amplitude family 14/24; both fail their frozen group gates.

Eight focused/inherited tests and 11 coverage tests per each of three existing
native probes pass. All 288 selector requests agree across those binaries.
Two full reports are byte-identical. CLI silence/trailing smoke passes. No full
native rebuild or P4 validation was performed. Pipeline CPU 5.558624/5.465741 s;
numeric workspace bound 13027872 bytes, host RSS 86908/85992 KiB.

## Exact first next-development action

Resolve why the unchanged NNLS call can return a result that fails independent
projected KKT validation. Start from the recorded five failures and inspect
the numerical interface/solver behavior, not another musical parameter sweep.
Distinguish a checker error, integration error and solver failure before choosing
a correction; a SciPy defect has NOT been established.

The fixed objective is `||Ax-b||² + 1e-3||x||²`, x>=0; columns have unit L2
norm, ridge is implemented with augmented rows. `nnls(maxiter=30*n)` is used.
KKT limit is 1e-8 with active threshold x>1e-10. Failed KKT values:
1.538732e-5, 1.261330e-5, 4.075896e-2, 5.159003e-7, 1.514960e-7.
Coefficients are finite/nonnegative and objectives improve on zero in all five.
Original report `max_kkt` describes successful solves only; consult its
`failure_inspection` for rejected values. Four failing windows are missing-
fundamental cases, one is detuned. The exact rows are in the saved inspection.

Do not edit the frozen E2 result, weaken thresholds, change ridge/iterations,
substitute a solver or rerun the bank to overwrite rejection. A justified
implementation correction must have its own recorded revision and independent
validation while preserving E2. Numerical repair alone does not close the two
valid-solve regressions; address attribution separately with fresh evidence.
No music-transfer run is warranted yet.

## Artifacts and reproduction context

Ignored local artifacts remain under `build/key-joint-e2-20260912/`: source.tar,
run.sh, result/repeat JSON and resources, test/probe logs, stderr, CLI smoke,
inspect_failures.py, failure-inspection.json and publisher. Corresponding clean
WSL source: `/home/daniel/apta-joint-e2-20260912/source`.

Small exact execution/inspection scripts and failure values are additionally
tracked in `evidence/1.1/repro/key-joint-e2-20260912/`, matching the public
artifact hashes. They preserve original absolute paths; they are provenance,
not portable installers. Do not launch run.sh casually: it would run the whole
bank and existing output files are protected against overwrite. Reconstruct
the source archive with `git archive 3ca838a87d0c044e987d06125bc1a5e1efd27aa6`
if needed. Keep old outputs and create separate paths for any justified work.

Runtime used: WSL Ubuntu, NumPy 2.5.2, SciPy 1.18.1,
OPENBLAS_NUM_THREADS=1. Existing native probes are under
`/home/daniel/apta-coverage-20260910/{default,candidate,sanitize}/tests/apta_key_chroma_probe`;
verify their hashes against public evidence before reuse. Rebuild if unavailable;
never imply a reused probe is a fresh full native build.

## Release boundaries

Production source/API/flags/VERSION remain unchanged, version 1.0.1. All work
above is offline synthetic diagnostic evidence. No new music, formal holdout,
fresh acceptance corpus or physical device was accessed. Transferable key and
beat/downbeat algorithms, independent final >=48-track acceptance, physical P4
validation and release freeze/package/tag remain open. Old observed/spent audio
must not become fresh evidence after tuning.
