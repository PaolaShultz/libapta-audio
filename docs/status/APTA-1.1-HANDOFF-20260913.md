# DSP handoff — numerical blocker resolved, synthetic A1 retained, 2026-09-13

## Resume here

Owning checkout: `/home/shome/p/libapta-audio`; intended branch
`agent/dsp-takeover-20260904`. Verify live Git state and applicable instructions.
This handoff supersedes the pause/next-action guidance in the preserved
`APTA-1.1-HANDOFF-20260912.md`. No push occurred or is authorized by this handoff.
The prior broad review remains `/home/shome/p/libapta-audio-review/REVIEW.md`;
do not repeat it or mix its unrelated findings into this DSP continuation.

Read [N1/A1 result](APTA-1.1-KEY-JOINT-N1-A1-RESULT.md),
[N1 protocol](APTA-1.1-KEY-JOINT-N1-PROTOCOL.md),
[A1 protocol](APTA-1.1-KEY-JOINT-A1-PROTOCOL.md), and
[public evidence](../../evidence/1.1/key-joint-n1-a1-20260913.json).
DEVELOPMENT-STATUS and ALGORITHM-IMPLEMENTATION-PLAN provide wider context.
No repository-specific AGENTS.md or installed libapta-dsp-development skill was
found in this checkout/session; the current global instructions and explicit
owner authorization governed this work. Fructal Cap Design was used in Implement
mode to preserve frozen evidence and acceptance gates while enabling a new revision.

## Resolved and retained

**Numerical cause is established.** In SciPy 1.18.1's NNLS kernel, rejection of
a trial Householder column restores its pivot but leaves a mutated tail. All
five original PCM hashes/failing KKT values reproduce with NumPy 2.5.2,
SciPy 1.18.1, single-thread OpenBLAS. Unmodified compiled source reproduces the
wheel exactly. Independent residual/Gram/extended-precision checks and BVLS
confirm solver workspace corruption, not an APTA checker/integration error.

**N1 is a verified offline numerical repair.** The separately vendored kernel
adds only caller-owned save/restore scratch on rejection. All five KKT values
fall below 3e-16; all 1152 E2 windows pass, with previously valid coefficients
unchanged to <3.5e-18. Objective, ridge, active threshold, KKT, solver/budget,
fail-closed behavior and original E2 files are preserved. Original E2 remains
rejected history. N1 alone is not accepted: 130/144 regression keys with three
breaks, and 138/144 fresh keys with four breaks and two high-confidence errors.

**A1 is retained only as a synthetic candidate.** One preregistered change folds
fitted physical amplitudes linearly into chroma; solver/model/selector remain
unchanged. It passes all fixed gates on 143/144 E2 regression cases and 144/144
separately frozen fresh cases, with no breaks versus direct peaks or N1 and no
high-confidence errors. Every family/mode passes. Both banks now are spent.
Do not perform adjacent weight/exponent/dictionary/confidence sweeps on them.

## What remains

- Physical harmonic attribution is not established. Known-note diagnostics
  restore the original missing-mode regressions at a higher objective, exposing
  mismatch between optimum surrogate fit and source identity. A1 improves the
  final salience representation; it does not resolve coherent interference,
  peak merging or physical identifiability.
- One spent regression error remains: unequal fixture tonic 5/major, expected
  tonic 4/major, selected tonic 4/minor, confidence 65. It is not a new break.
- Native confidence is uncalibrated for N1/A1. Fresh evidence is limited to
  related synthetic families, not music, an independent final corpus or device.
- Production key transfer, beat/downbeat transfer, formal holdouts, >=48-track
  final acceptance, physical P4 and release qualification remain open. VERSION
  stays 1.0.1; production C/API/defaults remain unchanged.
- The current task is complete. No new experiment or transfer run is queued.
  A future owner-authorized step must first freeze its own independent protocol
  and source/resource/acceptance boundary. Do not reopen numerical diagnosis or
  repeat the completed broad native review as a planning prerequisite.

## Reproduction and validation

`tools/apta_key_joint_n1.py` is the explicit repaired instrument;
`tools/apta_key_joint_a1.py` is the fixed amplitude-folding candidate.
`tools/experimental/nnls_n1/` owns upstream source/license and the small patch.
`tools/build_apta_nnls_n1.py` builds an isolated Linux host library, leaving
installed SciPy untouched. `APTA_NNLS_N1_LIBRARY` explicitly selects its absolute
path. BVLS exists only in diagnosis/tests, never as fallback. The adapter is
bounded to E2 matrices; no generic/platform/embedded NNLS API is promised.

Use [reproduction instructions](../../evidence/1.1/repro/key-joint-n1-20260913/README.md)
with a new output directory. Full numerical arrays, reduced case, compressed
complete reports, attribution traces and fresh PCM manifest are tracked there.
The saved runner was tested from clean detached checkpoint `aec654e`, rebuilding
an identical kernel and reproducing every scientific row/gate. Primary outputs
and logs remain in ignored `build/e2-repair-20260913/`; old outputs are untouched.
A single early replay carrying an accidentally truncated source SHA was excluded
as invalid metadata; the correctly pinned replay and clean reproduction pass.

27 focused/inherited/coverage tests pass; eight new-path tests pass with the
experimental kernel under ASan/UBSan (Python leak detection disabled). All four
bank reports replay byte-identically. N1 CLI silence/trailing smoke passes.
Pipeline CPU 3.07–4.17 s in primary paired runs (<120 s); numeric workspace about
13.03 MB (<16 MiB); process RSS is separately recorded. Reused review Release
native probe/hash, not a new full build or three distinct probes. No physical
resource or production-readiness claim.
