# Implementation status

Start with [`APTA-ROADMAP-STATUS.md`](APTA-ROADMAP-STATUS.md), the current
whole-project release and validation boundary.

Active post-1.0 development:

- [`APTA-1.1-ALGORITHM-IMPLEMENTATION-PLAN.md`](APTA-1.1-ALGORITHM-IMPLEMENTATION-PLAN.md)
  — ordered implementation plan for the remaining beat-lattice, downbeat, key,
  acceptance, physical-hardware and release-freeze work.
- [`APTA-1.1-DEVELOPMENT-STATUS.md`](APTA-1.1-DEVELOPMENT-STATUS.md) — the
  task-by-task implementation boundary. Tasks 5 (tempo/grid ensemble fresh-set
  acceptance) and 6 (calibrated confidence acceptance and integration) closed
  on 2026-08-25; meter/downbeat candidate work is deprioritized upstream at
  beat-lattice quality per native trace evidence.
- [`APTA-1.1-METER-DOWNBEAT-VALIDATION.md`](APTA-1.1-METER-DOWNBEAT-VALIDATION.md)
  — development corpora, three rejected downbeat-phase candidates with root
  cause, the native meter-trace tool, and the trace analysis that bounds
  bar-phase accuracy at lattice quality.
- [`APTA-1.1-KEY-BLIND-REVIEW.md`](APTA-1.1-KEY-BLIND-REVIEW.md) — exact source
  re-decode, two-listener key review, free-service screens, OpenKeyScan
  automated triage and the fail-closed boundary for the spent FMAK split.
- [`APTA-1.1-KEY-DISAGREEMENT-TOPOLOGY.md`](APTA-1.1-KEY-DISAGREEMENT-TOPOLOGY.md)
  — frozen report-only 22-case procedure; results and the next contrast-trace
  boundary are recorded in the final section of the key blind-review report.
- [`APTA-1.1-KEY-CONTRAST-TRACE.md`](APTA-1.1-KEY-CONTRAST-TRACE.md)
  — synthetic per-window energy/compression trace, unchanged native decisions,
  observed major-mode contrast loss and the next gain-sensitivity boundary.
- [`APTA-1.1-KEY-GAIN-RESULT.md`](APTA-1.1-KEY-GAIN-RESULT.md)
  — fixed four-gain synthetic diagnostic, exact raw-energy scaling, observed
  gain-dependent mode decisions and the next energy-normalization boundary.
- [`APTA-1.1-FINAL-DJ-CORPUS-STATUS.md`](APTA-1.1-FINAL-DJ-CORPUS-STATUS.md) —
  dated private-corpus snapshots, the independently verified formal rejection,
  and the remaining accuracy boundary.

Stage S9 — APTA 1.0:

- [`S9-FREEZE-AUDIT.md`](S9-FREEZE-AUDIT.md) — contractual gap analysis and
  original blocker inventory.
- [`S9-P1-NORMATIVE-SCOPE-STATUS.md`](S9-P1-NORMATIVE-SCOPE-STATUS.md) —
  normative authority, profile and scope freeze.
- [`S9-P2-API-ABI-STATUS.md`](S9-P2-API-ABI-STATUS.md) — stable version model,
  API/ABI compatibility, layout and exported-symbol freeze.
- [`S9-P3-CONTAINER-V1-STATUS.md`](S9-P3-CONTAINER-V1-STATUS.md) — stable
  container-version-1 registry and canonical fixture authority.
- [`S9-P6-INTEROPERABILITY-STATUS.md`](S9-P6-INTEROPERABILITY-STATUS.md) —
  independent producer/consumer exchange and platform evidence boundary.
- [`S9-P7-SECURITY-CAMPAIGN.md`](S9-P7-SECURITY-CAMPAIGN.md) — frozen fuzz
  inventory, reproducible ASan/UBSan campaign and security review.
- [`S9-P8-RC-FREEZE.md`](S9-P8-RC-FREEZE.md) — accepted `1.0.0-rc.1`
  candidate, frozen manifests and retained release evidence.
- [`S9-P9-RELEASE.md`](S9-P9-RELEASE.md) — stable 1.0 identity, finalization
  boundary and `v1.0.0` publication workflow.
- [`../roadmap/APTA-1.0-WORK-ORDER.md`](../roadmap/APTA-1.0-WORK-ORDER.md) —
  ordered P0–P9 implementation and release gates.

Earlier stage and milestone evidence snapshots:

- [`M2-WAVEFORM-PROCESSING-STATUS.md`](M2-WAVEFORM-PROCESSING-STATUS.md)
- [`S4-TEMPO-LOCAL-GRID-STATUS.md`](S4-TEMPO-LOCAL-GRID-STATUS.md)
- [`S5-REFERENCE-DESKTOP-TOOLS-STATUS.md`](S5-REFERENCE-DESKTOP-TOOLS-STATUS.md)
- [`S6-GLOBAL-GRID-DYNAMIC-TEMPO-STATUS.md`](S6-GLOBAL-GRID-DYNAMIC-TEMPO-STATUS.md)
- [`S7-ESP-IDF-PORT-STATUS.md`](S7-ESP-IDF-PORT-STATUS.md)
- [`S8-WINDOWS-PORT-STATUS.md`](S8-WINDOWS-PORT-STATUS.md)
- [`PHASE4-INDEPENDENT-TEMPO-CORPUS-STATUS.md`](PHASE4-INDEPENDENT-TEMPO-CORPUS-STATUS.md)
- [`PHASE5-TEMPO-GENERALIZATION-STATUS.md`](PHASE5-TEMPO-GENERALIZATION-STATUS.md)
- [`PHASE6-MULTIBAND-ONSET-STATUS.md`](PHASE6-MULTIBAND-ONSET-STATUS.md)
- [`PHASE7-P4-BOUNDED-REFRESH-STATUS.md`](PHASE7-P4-BOUNDED-REFRESH-STATUS.md)

Snapshot test totals and “next stage” sections apply to the commit and CI run
named by each document. They do not override the current release status.

- [`P10-1.0.1-COHERENCE.md`](P10-1.0.1-COHERENCE.md) — maintained documentation, metadata and release-automation coherence patch.

- [`P11-REPOSITORY-UX.md`](P11-REPOSITORY-UX.md) — public examples, quick-start documentation and contributor onboarding.

- [`P12-SECURITY-DOCUMENTATION.md`](P12-SECURITY-DOCUMENTATION.md) — security automation, immutable workflow dependencies and future release provenance.

- [`P13-ECOSYSTEM-DISTRIBUTION.md`](P13-ECOSYSTEM-DISTRIBUTION.md) — standalone ESP-IDF component packaging, registry metadata and exact-tag publication controls.
