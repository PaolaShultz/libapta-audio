# S3 final search checkpoint — 2026-09-12

**Experiment 2/2 passes 36/36.** Unchanged S2 passes every accuracy and
termination gate on new clean/noisy two-tone signals. All searches return
`poll_resolved`; none exhaust the budget or abstain. This closes the agreed
search series. Retain S2 as a bounded numerical reference for an end-to-end
candidate, as specified in the [decision](APTA-1.1-KEY-TWO-EXPERIMENT-CHECKPOINT.md).

Protocol `e17671a` preceded instrument
`e39279b4a2ccb5f96897c04505361088b8480738` and the first run. See the
[protocol](APTA-1.1-KEY-SEARCH-FINAL-CHECK-PROTOCOL.md) and
[public evidence](../../evidence/1.1/key-search-final-check-s3-20260912.json).

| Condition | Combined passes | Maximum frequency error | Maximum relative amplitude error |
| --- | --- | --- | --- |
| Clean | 12/12 | 2.395268e-9 Hz | 2.916331e-9 |
| 40 dB | 12/12 | 0.001803119 Hz | 0.002908717 |
| 20 dB | 12/12 | 0.018302170 Hz | 0.028055264 |

Clean frequency/absolute amplitude/residual gates are 1e-4 Hz, 1e-4 and
1e-10. Noisy frequency/relative amplitude gates are .02 Hz/.10 at 40 dB
and .10 Hz/.50 at 20 dB. Each noisy residual passes its frozen oracle ceiling
of 1.1 times observed noise-energy fraction plus 1e-10. These condition-specific
thresholds do not imply better accuracy with noise. No seed-fit regression,
residual-pass-but-inaccurate result or paired clean/noisy pass change occurs.
The identical-condition comparison with R2 records one fix and zero breaks;
R2 does not have S2's explicit termination certificate.

Maximum search cost is 887 evaluations versus the 2049 limit. Matrix plus
inverse storage is 113792 bytes/model versus 1 MiB; interpreter, trace storage
and whole-pipeline state are excluded. Bank plus controls takes 197.027275 CPU
seconds and repeat 193.297547, each below 300. This diagnostic timing includes
independent fit checks and comparisons; it is not a P4 runtime estimate.
Maximum analytic-column and independent prediction errors are 3.826338e-13
and 3.795550e-15, both below 1e-10.

Three new tests plus 98 unchanged diagnostic tests pass. Eleven coverage tests
pass against each reused default, candidate and sanitizer native probe. S2's
eight quadratic outputs and O1's 24 rows replay identically. Full summary and
detail files match byte-for-byte on the repeat; both stderr files are empty.
No full native rebuild is claimed. The clean instrument archive runs under
WSL Ubuntu, NumPy 2.5.2, OPENBLAS_NUM_THREADS=1. Local artifacts, test logs and
the exact invocation are in `build/key-search-final-check-20260912/`; their
hashes and per-row results are recorded in public evidence.

Reproduce from the instrument revision with
`tools/apta_key_search_final_check.py --s2-evidence evidence/1.1/key-quadratic-search-s2-20260912.json --r3-evidence evidence/1.1/key-noise-robustness-r3-20260912.json --o1-evidence evidence/1.1/key-observability-o1-20260912.json --source-commit e39279b4a2ccb5f96897c04505361088b8480738 --output-prefix /tmp/apta-s3`.

Tone count, local seed neighborhoods, synthetic amplitude budget and evaluation
noise oracle remain supplied. Finite poll resolution is not global convergence.
The 2D search has no demonstrated unknown-count, multi-tone, music, confidence
or real-time transfer. Production source/API/flags/VERSION and predecessor
instruments are unchanged; production resource delta is zero. No corpus or
holdout was accessed, no physical P4 evidence was produced, and no complete
key candidate or 1.1 release is accepted.
