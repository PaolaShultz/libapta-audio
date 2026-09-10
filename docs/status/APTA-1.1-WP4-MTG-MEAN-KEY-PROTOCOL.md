# WP4 MTG mean-normalized key — frozen development protocol

Frozen 2026-09-10 before selection audio access or new analyzer outputs.
Baseline repository revision: `fe20d6663720320f4e68a5b44c68aabfd701e716`.
Detector implementation: `a883dd6d0d50d4f463d8347352d75891d9005fba`.
I1 passed the synthetic identity and host-cost gates recorded in
`APTA-1.1-KEY-MEAN-COST-I1-RESULT.md`. This experiment tests transfer of that
unchanged detector to disjoint electronic-music previews. Poor synthetic
detuning performance (8/24) remains an explicit risk.

## Evidence, annotations and separation

Use the existing pinned GiantSteps-MTG annotation checkout
`fd7b8c584f7bd6d720d170c325a6d42c9bf75a6b` and original GiantSteps exclusion
checkout `6bcd492c825ac9b8597bc650a5f6fd18b6c43d2b`. Both must have clean
tracked files. The upstream [MTG repository](https://github.com/GiantSteps/giantsteps-mtg-key-dataset)
provides annotations, transport MD5 values and official preview/mirror URLs.
Published use of the 1,159 unambiguous confidence-2 annotations is described
in [the MIREX 2017 paper](https://www.music-ir.org/mirex/abstracts/2017/HS1.pdf).
These are fixed published development labels independent of APTA, not labels
inferred from detector agreement and not a new local two-listener verification.
No final manual-verification or release claim follows from this experiment.
Audio stays local, uses only the existing dataset transport, and is never
redistributed. The prior dataset-use boundary remains unchanged.

Reconstruct the original 96-track MTG development selection and reserved
48-track holdout using the unchanged canonical selector. Require its full seal
`1fadadc5e5df343558eeb476aa2346fc688bea6ebbc98a09a996a649be3b0146`.
Exclude both selections by ID and transport MD5, plus all 604 original
GiantSteps transport MD5 values (covering its spent centered-key subset).
The pinned eligible inventory has 1,159 records; 1,015 remain after the
96+48 ID exclusions, minimum 16 per class before checksum exclusion.

For each of 24 tonic/mode classes, sort remaining candidates by SHA-256 of
`apta-1.1-mtg-mean-key-v1:track:<source_id>` (ID as tie-breaker) and take exactly
four. Sort the final selection by tonic, mode and ID. Require 96 unique IDs
and transport MD5 values, 48 major/48 minor and zero reserved/spent overlap.
If quotas or identity checks fail, stop; do not change seed or backfill after
transport, labeling or analysis failures. Commit the selection tool, tests,
and public preflight seal before downloading selected audio.

Before analysis, compare canonical audio digests against the five spent key
sets (MTG, original GiantSteps, and all three FMAK splits), the spent ASAP
development audio and the former final DJ corpus. Also check PCM content
hashes with sample geometry so container differences cannot hide duplicates.
Do not read any reserved holdout audio or outputs. Report the scope plainly:
ID/checksum/PCM separation does not establish artist or composition separation.
No automatic relabeling, replacement tracks or result-dependent exclusions.

## Execution and frozen gates

Reuse canonical downloader, canonicalizer, FINAL exporter and scorer from
`tools/apta_1_1_giantsteps_key_validation.py`; add a dedicated wrapper enforcing
this selection, seals, development-only scope and checks. Freeze new labels
and manifest before analysis. Canonical input is metadata-free 48 kHz stereo
PCM16, ordered by opaque full-WAV-derived identity. Rehash all inputs and
validate all run outputs/mappings before scoring. Missing/unfinished/invalid
outputs are execution failures, never removed from the denominator.

Build D (no experimental key flag) and C (both MEAN_NORMALIZED_KEY and
MEAN_NORMALIZED_KEY_COST_I1 ON) from the same clean committed archive. Require
analyzer hashes identical to the I1 evidence, thereby preserving exact
detector implementation, and use the same inspector, `--features all`,
manifest and `SOURCE_DATE_EPOCH=1788998400`. Preserve all I1 software/resource
evidence and run the new wrapper tests before corpus access.

Every gate is conjunctive:

- all 96 recordings complete and identities/exclusions/geometry pass;
- exact tonic-and-mode accuracy >=70% (at least 68/96);
- major and minor each >=60% (at least 29/48 each);
- strictly higher total accuracy and fixes exceeding breaks against D;
- neither mode loses correct results relative to D;
- zero new wrong predictions at confidence >=75;
- high-confidence errors <=5% of all tracks (at most 4/96);
- unchanged detector/default bytes and retained software/host-cost gates pass.

Record total/per-mode/per-class results, relation error families, fixes,
breaks, changed verdicts and confidence errors with exact identities. Any
failed gate rejects this detector for this transfer experiment and spends
the selected split; do not tune normalization, tuning compensation, profiles,
aggregation, confidence or thresholds against it. Transport failure blocks
execution without authorizing substitute tracks or a partial success claim.

A full pass retains the exact detector for later explicitly frozen validation.
This wrapper cannot materialize a holdout and never grants WP6/WP7 or final
acceptance eligibility. Physical P4/full-path resource work and transferable
lattice/downbeat algorithms remain separate blockers. VERSION stays 1.0.1.

## Metadata-only preflight seal

Before any new audio download, the selector and eight host tests pass. The
96-track selection seal is
`87c4764ddeb667ce5acee85cfeba0a6a9bc23f987438af8cfc064b60218601ab`.
The [public preflight](../../evidence/1.1/mtg-mean-key-preflight-20260910.json)
records 48/48 mode balance, four per class and zero reserved/spent ID or
transport-checksum overlap. The new split contains no formal holdout entries.
