# WP4 MTG mean-normalized key — independent development rejected

The unchanged mean-normalized I1 detector is **rejected** on the newly sealed
96-track GiantSteps-MTG development split. Exact accuracy improves from
27/96 to 37/96, but fails the >=70% total, >=60% per-mode and both confidence
safety gates. The synthetic/resource pass remains valid at its stated scope;
it does not establish usable key accuracy or confidence on real music.

Analysis and scoring used clean source
`9e7328c5b2f4ddf85c6aed55aeb8c67fd81fcac7`, with detector implementation
`a883dd6d0d50d4f463d8347352d75891d9005fba`. The
[protocol](APTA-1.1-WP4-MTG-MEAN-KEY-PROTOCOL.md) was committed before audio
access; its selection tool, eight tests and public seal were committed before
download. No formula, profile, confidence threshold, label or selected track
changed after freezing. The split is now spent. No holdout was opened.

## Frozen outcome

| Metric | Default | Mean-normalized I1 | Candidate gate |
|---|---:|---:|---|
| Exact key | 27/96 (28.125%) | 37/96 (38.542%) | FAIL: >=70% / at least 68 |
| Major | 1/48 (2.083%) | 11/48 (22.917%) | FAIL: >=60% / at least 29 |
| Minor | 26/48 (54.167%) | 26/48 (54.167%) | FAIL: >=60% / at least 29 |
| Wrong key at confidence >=75 | 2/96 (2.083%) | 19/96 (19.792%) | FAIL: <=5% / at most 4 |
| New high-confidence errors | — | 17 | FAIL: zero |

There are **13 fixes, three breaks and 34 changed verdicts**. Total accuracy
improves by 10/96 (10.417 percentage points), fixes exceed breaks and neither
mode loses correct results in aggregate. Those three passing gates cannot
override the failed absolute and confidence-safety gates. Preserved minor
counts do not imply identical correct tracks.

The frozen scorer's relation categories change as follows:

| Error family | Default | I1 |
|---|---:|---:|
| Exact | 27 | 37 |
| Same-tonic opposite mode | 31 | 21 |
| Relative key | 1 | 7 |
| Fifth relationship | 8 | 7 |
| Other | 29 | 24 |

Normalization reduces some same-tonic mode errors but leaves substantial
tonic/mode errors and increases confident wrong outputs. This observation
does not establish detuning, modulation or label error as the cause. Do not
repair the result by lowering confidence, choosing a gain, tuning profiles or
changing the normalization formula on these 96 tracks.

## Independence and label boundary

Selection reconstructed the original MTG 96-development/48-holdout seal,
excluded both sets and every original GiantSteps transport checksum, and
selected four tracks per tonic/mode class from previously unused MTG records.
The new selection seal is
`87c4764ddeb667ce5acee85cfeba0a6a9bc23f987438af8cfc064b60218601ab`.
Mode balance is 48/48. All selected source IDs and transport checksums are
unique and disjoint from the excluded inventories.

All selected audio downloads matched upstream MD5 before canonicalization.
The 48 kHz stereo PCM16 WAVs were hashed and frozen before analysis. Full-WAV
and PCM-plus-geometry hashes have zero overlap with 556 verified prior
recordings: MTG 96, original GiantSteps 96, FMAK 96+96+72, ASAP development 40,
and the former final DJ corpus 60. Only the ASAP development rows were read
for audio comparison; reserved holdout audio was not accessed. All 96 new PCM
hashes are unique. This establishes the checked recording-ID/byte separation,
not artist or composition independence across different excerpts.

Labels are the pinned dataset's published single-key confidence-2 annotations,
independent of APTA. Their use is documented in the
[MIREX paper](https://www.music-ir.org/mirex/abstracts/2017/HS1.pdf) and they
are distributed in the [MTG repository](https://github.com/GiantSteps/giantsteps-mtg-key-dataset).
No new local two-listener review was performed. This is independent development
evidence against those published labels, not a manually verified final DJ
acceptance corpus. No external-detector agreement was used for relabeling.

## Execution and software evidence

Both analyzers were rebuilt from one clean archive, Release/Werror, with
`SOURCE_DATE_EPOCH=1788998400` and `--features all`. The default has neither
key experiment enabled; I1 enables both
`APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON` and
`APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY_COST_I1=ON`.
Analyzer bytes exactly match the preceding I1 evidence, preserving the frozen
detector. Both runs used the same default inspector and immutable manifest.

- Default Release/Werror: 118/118 native tests.
- I1 Release/Werror: 119/119 native tests.
- New selection/scoring wrapper: 8/8 tests.
- Exact native I1 sanitizer 116/116 and resource evidence are retained from
  the preceding experiment; this task changes only host tooling/documents.
- Both analyses completed 96/96; all 192 output hashes and both mappings were
  verified, and the canonical exporter required FINAL results.
- No execution failures, replacements, shortened denominator or partial pass.

Whole-run wall times were about 222 and 224 seconds with concurrent analysis
and input validation; these are provenance observations, not performance
qualification. The I1 host stack/CPU result remains +64 bytes and near-default
key-feed cost. No physical P4 or full-path resource qualification occurred.

| Artifact | SHA-256 |
|---|---|
| Prepared manifest | `aab31e965171f0a8a83f11b8818a791928fb8b3896979ae4ea3dafd73ff065b4` |
| Default analyzer | `0e7999efb61734f656b846d5542617454c5a0789224531c071d0f8555512383a` |
| I1 analyzer | `07bc09506799a17347d7fc2dae8e2630a101c3af2ab8fc876bf239ca58a17f77` |
| Shared inspector | `22f8f3e85a177a034157a265e4e9cf6e1ea03151f90310dd854b3fee07d8e084` |
| Default report | `40c0c01b7f43c79fda6af022bba8e3e731b2bd89aef101408d12e4c7f4c55021` |
| I1 report | `912d9c5e070e9e540625b4aa883cbf2bb10a193b229eb38759aaafcd819f4478` |

The [public result](../../evidence/1.1/mtg-mean-key-result-20260910.json)
includes every gate, per-class aggregates, source/tool/protocol identities,
manifest/label/mapping/output-run hashes and exclusion evidence. Audio, source
IDs, private paths, labels and per-track reports remain in ignored
`build/mtg-mean-key-20260910/`. Neither private data nor audio is committed.

## Reproduction and next action

The dedicated wrapper supports `preflight`, `exclusions`, `prepare`, `run`,
`evaluate` and `compare`; use `--help` for their explicit arguments. It reuses
the canonical GiantSteps transport, WAV conversion, FINAL exporter and scorer.
`prepare` checks the public selection seal; `run` requires exact analyzer
bytes, epoch and fresh output; `evaluate` verifies run/mapping/output hashes
before scoring. No command can prepare a holdout.

```powershell
python -m unittest discover -s tools -p test_apta_1_1_mtg_mean_key_development.py -v
python tools/apta_1_1_mtg_mean_key_development.py compare --baseline build/mtg-mean-key-20260910/default-report-private.json --candidate build/mtg-mean-key-20260910/candidate-report-private.json --output build/mtg-mean-key-20260910/new-comparison.json
```

This transfer experiment is complete and rejected. Keep both mean-normalized
options disabled by default and retain the implementation only for exact
reproduction. The earlier resource-retention decision does not authorize any
further validation of this rejected detector.

The next useful step is a separately preregistered tonal-evidence diagnostic,
starting with synthetic measurements that distinguish frequency coverage from
mode ranking and confidence behavior. It must add information to explain the
remaining deficit, not optimize thresholds or normalization against this spent
split. No new detector or causal explanation is selected by this report.
Any successor requires genuinely disjoint development evidence before a
formal holdout. WP6/WP7, physical P4 and final release gates remain open;
VERSION stays 1.0.1.
