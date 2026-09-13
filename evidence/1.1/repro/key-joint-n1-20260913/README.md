# E2-N1 / E2-A1 reproduction

Start at `docs/status/APTA-1.1-HANDOFF-20260913.md` in the repository root.

- Five `.npz` archives preserve PCM, peaks, normalized target, unit columns,
  norms, ridge augmentation, original coefficients, and diagnostic BVLS output.
  Names are `family-fixture_tonic-mode-window`; expected E2 tonic is fixture-1
  modulo 12. `reduced.npz` is a standalone 74x20 augmented numerical case,
  with no PCM/generator dependency. It is deletion-reduced, not globally minimal.
- `reduce.py --output NEW_PATH` reconstructs that deterministic reduction using
  the pinned environment. Do not execute with a tracked output path.
- `a1-fresh-manifest.json` was committed before any fresh detector evaluation.
  All 1152 hashes are disjoint from the E2 report.
- `run.sh ABSOLUTE_NEW_OUTPUT_DIR ABSOLUTE_NATIVE_CHROMA_PROBE` installs a local
  NumPy 2.5.2 / SciPy 1.18.1 environment with uv, builds the separately patched
  kernel, reconstructs all numerical cases, runs 27 tests and evaluates each
  fixed instrument/bank twice. Requires Linux, a C compiler, `patch`, `uv`, and
  an already verified native probe. It never modifies installed SciPy, builds
  production, or opens music. Single-thread BLAS is mandatory.
- The supplied probe may be the reused review Release probe at
  `/home/shome/p/libapta-audio-review/release-build/tests/apta_key_chroma_probe`.
  Its hash is pinned in the public result. Passing the same path three times to
  the historical evaluator is single-probe reuse, not three-build identity.
- Full reports and attribution traces are preserved as deterministic gzip JSON
  in this directory. Use Python `gzip.open(path, 'rt')` or `gzip -dc` to inspect.
  Both compressed and original-byte hashes are in the public summary.
- Report `source_commit` is the instrument checkpoint, with source-file hashes
  authoritative for exact instruments. A reconstruction from a later docs-only
  commit has different provenance metadata but must preserve scientific rows.

Original Windows/WSL E2 scripts and rejected results remain untouched in the
adjacent `key-joint-e2-20260912` directory. No local output is an acceptance corpus.
