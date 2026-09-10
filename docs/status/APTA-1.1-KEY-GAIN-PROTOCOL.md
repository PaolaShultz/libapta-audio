# Frozen synthetic input-gain diagnostic — 2026-09-05

Source baseline: `1e3a151ed625b82c276b5117c498dfe64f301dd7`. This protocol
precedes implementation and execution. It follows the compression/contrast
observation and changes only PCM gain, not a detector parameter or label.

## Hypothesis and fixed design

Absolute resonator-energy `logf(1+energy)` changes chroma shape when the same
PCM changes level. If the raw energies scale by gain squared while the
compressed native tonic/mode decisions change, this isolates gain dependence
of the current compression/folding/scoring path on these synthetic stimuli.
It does not establish DJ accuracy, a general failure rate or a replacement.

- Reuse the exact 720-row generator/observer with the existing clean, detuned
  and noisy four-window progressions and all 24 ideal key identities.
- Fix four power-of-two gains before observation: 1/16, 1/4, 1 and 2
  (`gain_shift` -4, -2, 0 and 1). No intermediate levels or gain search.
- Scale the already-rounded float mixture using `ldexpf`; scale noise with
  the signal so SNR stays fixed. Require every sample to be finite, within
  [-1,1], and exactly recovered by the inverse binary gain. The maximum
  theoretical absolute sample at gain 2 is 0.94, so clipping is not needed.
- Add an explicit-build-only `apta_key_gain_diagnostic` target with the same
  bounded observer. Permit only the four fixed gain arguments; ordinary
  contrast/mode/reference tools and production library remain unchanged.
- Require gain 1 rows and trace fields to equal the pinned previous contrast
  reports exactly. The ideal vectors must be identical at every gain.
- Require all raw observed energies to equal gain-squared-scaled baseline
  float energies exactly after round-trip float parsing. Require diagnostic
  argmax on raw-folded vectors to be unchanged. Stop on failure rather than
  treating an extraction or stimulus change as compression evidence.
- For each gain/build/condition/mode report changed tonic+mode decisions,
  mode-only versus tonic changes, high-confidence output counts, and FINAL
  four-window matches against the synthetic progression identity. Intermediate
  IV/V window results are descriptive, not global-key errors. Report chroma
  min/mean and major/minor score margin using the existing summary definitions.
  Confidence observations are not a confidence-safety acceptance assessment.
- Analyze exactly the eight fixed default/band gain runs. No audio files,
  service requests, corpus labels, formal holdouts, normalization, profile
  change, confidence tuning or clipping is allowed.

## Verification and interpretation boundary

Default/band Release Werror; gain argument rejection before sample generation;
focused summary validation tests; deterministic replay of all eight reports;
band ASan/UBSan at all four gains; gain-1 identity; raw-energy scaling and
observer reconstruction checks; unchanged production analyzer/key object bytes.
The generator receives no new production flag, API, memory or installed symbol.
New counters and observer scratch live only in the test process. Record full
source/tool/binary/report hashes and actual worktree state; this is synthetic
diagnostic evidence even if its software checks pass.

If decisions are invariant, stop the gain hypothesis. If decisions change with
all stimulus/scaling checks passing, retain a separately preregistered
scale-normalization/contrast hypothesis for independent development evidence.
Do not select a preferred input gain, alter thresholds or implement a native
normalization rule from this diagnostic. Complete this bounded step before any
new representation experiment.
