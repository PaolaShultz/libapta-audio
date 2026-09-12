# S2 local quadratic search — 2026-09-12

**Experiment 1/2 passes 16/16:** eight new known quadratics and eight new
noiseless two-tone cases. All terminate `poll_resolved`, with four combined
fixes versus S1 and zero breaks. This finite termination criterion is not
a global convergence certificate or musical-key acceptance.

Protocol `a95a640` preceded instrument
`142d6026351843d4d904bca729fcb2ddcf2b66f7` and all runs. See the
[protocol](APTA-1.1-KEY-QUADRATIC-SEARCH-PROTOCOL.md),
[public evidence](../../evidence/1.1/key-quadratic-search-s2-20260912.json) and
[two-experiment checkpoint](APTA-1.1-KEY-TWO-EXPERIMENT-CHECKPOINT.md).

S2 adds quadratic directions inferred from the existing poll neighborhood,
uses them only when the local model has full rank and positive curvature,
and verifies improvement with actual objective evaluations. It preserves S1's
failed-poll step reduction and explicit exhausted-budget state. Neither source
truth nor derivatives of the tone model steer the search.

All known quadratics, including curvature ratios 16384 at 19-degree rotation,
reach their represented exact center, in 594..711 evaluations. All tones pass
frequency <=1e-4 Hz, amplitude <=1e-4 and residual <=1e-10, with maximum
frequency error 5.214929e-9 Hz, amplitude error 5.950388e-10 and residual
2.496513e-16. Tone searches use 800..954 evaluations, below 2049. Tone-count
and seed-neighborhood oracle information remains; there is no discovery claim.

S1's original eight quadratic outputs and O1's 24 numerical rows replay
identically. Five new tests and 93 unchanged diagnostic tests pass; 11 coverage
tests pass against each reused default Release, I1 Release and sanitizer
probe. Summary and full traces replay byte-identically; stderr is empty.
Maximum analytic column error is 3.734556e-13 and independent least-squares
prediction error 3.165648e-15, both below 1e-10. Largest matrix+inverse is
113792 bytes, below 1 MiB/model. CPU and replay timing below 300 seconds are
recorded in public validation. No full native rebuild or P4 result is claimed.

Clean instrument archives run on WSL/NumPy 2.5.2 with OPENBLAS_NUM_THREADS=1.
Local traces/scripts are in `build/key-quadratic-search-20260912/`; public
evidence records their hashes and all bank results. Reproduce with
`tools/apta_key_quadratic_search.py --s1-evidence evidence/1.1/key-search-convergence-s1-20260912.json --o1-evidence evidence/1.1/key-observability-o1-20260912.json --source-commit 142d6026351843d4d904bca729fcb2ddcf2b66f7 --output-prefix /tmp/apta-s2`.

This passing prerequisite authorizes only the second, final checkpoint
experiment: unchanged S2 on a new paired noise/unequal-amplitude bank under
a separately frozen protocol. No old failed waveform is reused to tune S2.
After that result, make the direction decision rather than another diagnostic
extension. Production source, flags/API/VERSION and predecessor instruments
are unchanged; no corpus/holdout is accessed, production resource delta zero.
