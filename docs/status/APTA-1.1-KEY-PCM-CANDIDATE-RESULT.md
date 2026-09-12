# E1 PCM-to-key result — 2026-09-12

**Rejected.** The complete offline candidate returns 85/96 exact keys, versus
76/96 for direct folding of the same detected peaks, but introduces 11 breaks
and two new confidence>=75 errors. Aggregate improvement cannot override the
frozen no-regression veto. No transfer run or native port is authorized by E1.

Protocol `f467f6b` preceded instrument
`844dfe938fafe5f650fe012d67d06b3ceeb485e5` and both executions. See the
[protocol](APTA-1.1-KEY-PCM-CANDIDATE-PROTOCOL.md) and
[machine-readable evidence](../../evidence/1.1/key-pcm-candidate-e1-20260912.json).

| Condition | Major | Minor | Combined |
| --- | --- | --- | --- |
| Pure | 12/12 | 12/12 | 24/24 |
| Full harmonics | 12/12 | 12/12 | 24/24 |
| Missing fundamental | 12/12 | 1/12 | 13/24 |
| Detuned full harmonics | 12/12 | 12/12 | 24/24 |

Required >=18/24 per condition and >=9/12 per mode/condition fails for missing
fundamentals. All 11 breaks concern minor stimuli in that family: mode remains
minor but the selected tonic moves +8 semitones modulo 12. Two have confidence
77 and 78. Although 2/96 high-confidence errors is below the aggregate 5% cap,
both are new versus the comparator, failing the independent confidence veto.
There are 20 fixes and 11 breaks. This comparison isolates harmonic attribution
and resulting chroma in this pipeline; the comparator is not the production
PCM extractor. It does not establish the cause of real-audio errors.

The implementation consumes PCM without seeds, labels or known component count,
uses detected/interpolated spectral peaks and bounded harmonic attribution,
normalizes and accumulates window chroma, then invokes the unchanged native key
selector. Selected count ranges 3..12 across 768 windows; this is an algorithm
selection count, not evidence of exact physical source-count recovery. S2 is
not called: its two-tone grid remains a numerical reference only.

Extraction and one native-selector pass use 3.059865 CPU seconds, repeat
3.026551, versus the offline 60-second gate. Fixture generation and validation
probe repeats are excluded. Conservative numeric workspace reservation is
4733472 bytes versus 8 MiB; process peak RSS including Python is 41052/41132 KiB.
These are host screen figures, not P4 measurements or a production memory claim.

Four focused tests pass (invalid PCM, silence, peak discovery, gain, bounded
attribution, residual monotonicity and WAV rate/trailing behavior). Eleven
coverage tests pass on each reused default, candidate and sanitizer native
probe. All 192 final candidate/comparator selector requests agree across the
three binaries. Summary including per-window traces replays byte-identically;
stderr is empty. A complete CLI silence smoke returns unavailable, one window
and 17 trailing samples. No full native rebuild was needed or claimed.

Artifacts and exact command are in `build/key-pcm-e1-20260912/run.sh`; public
evidence pins archive, scripts, tests, output, imported source and probe hashes.
The CLI is `tools/apta_key_pcm_candidate.py --experimental-e1 --wav INPUT.wav
--probe NATIVE_PROBE`; it supports PCM16 48 kHz mono/stereo, reports incomplete
trailing samples, and does not output private source paths. It remains explicitly
experimental and rejected; its confidence is not calibrated for this frontend.

## Direction decision

Stop E1 unchanged. Do not adjust harmonic weights, match tolerances, profiles or
confidence using these 96 now-observed stimuli. In particular, do not enable a
fallback selected from this bank to erase its 11 breaks. Peak discovery and
streaming plumbing are implemented, but E1's destructive harmonic allocation
is not retained as an accepted tonal representation. A future complete design
must address competing fundamental explanations without treating the greedy
allocation as established truth, and establish fresh independent evidence.
That requires a separate design decision, not another automatic solver probe.

Production source, API, flags and VERSION remain unchanged (1.0.1); zero
production CPU/RAM/state delta. No corpus, holdout or physical P4 was accessed.
Transferable key and beat/downbeat algorithms, independent final acceptance,
physical-device validation and release freeze remain open.
