# Key-search decision checkpoint — 2026-09-12

User-authorized limit: at most two further search experiments after S1, then
an explicit direction decision. No open-ended follow-up diagnostic chain.

1. S2: a separately frozen local quadratic direction model, tested on new
   known objectives and new noiseless two-tone signals, with explicit limits.
2. Only if S2 passes: a separately frozen paired noise/unequal-amplitude
   screen of unchanged S2 on new signals. If S2 fails, stop this search track
   and make the decision without spending the second experiment on a rescue.

After the checkpoint, state whether this search has sufficient bounded evidence
to serve as one component of a complete key candidate, or whether the approach
must change. Even two passes do not demonstrate seed discovery, unknown tone
count, harmonic attribution, real music, native cost or release eligibility.
Keep production and formal/spent corpus boundaries unchanged.

## Completed decision — 2026-09-12

Both authorized experiments are complete: S2 passes 16/16 and S3 passes 36/36.
Every search terminates `poll_resolved`; deterministic summary and trace replay
passes. See [S2](APTA-1.1-KEY-QUADRATIC-SEARCH-RESULT.md) and
[S3](APTA-1.1-KEY-SEARCH-FINAL-CHECK-RESULT.md). Historical S1 and R3 rejections
remain unchanged. The two-experiment allowance is exhausted; no S4 search
microexperiment is the next action.

**Decision: retain unchanged S2 as a bounded numerical reference component for
developing an offline end-to-end key candidate.** This is component viability
under supplied two-tone count and local seed neighborhoods, not retention of
a complete musical-key candidate. The evidence's `candidate_retained=false`
continues to describe that latter boundary.

The next deliverable is a frozen end-to-end candidate design and implementation
that consumes PCM without true-frequency or component-count inputs: spectral
seed discovery, bounded component selection/refinement, harmonic attribution,
temporal aggregation, key output and confidence/abstention. S2 can serve as a
two-component numerical reference; its 2D grid is not a scalable multi-tone or
real-time algorithm. Define whole-pipeline CPU/RAM limits before implementation,
including a rule to omit this component if it cannot meet them.

Success must be assessed at the pipeline output: reproducible unseen synthetic
mixtures with unknown count, then independent development music under frozen
fix/break, key accuracy and high-confidence-error gates. Compare unchanged
production and record full runtime/state cost. Freeze those evaluation gates
before seeing new outcomes; no new solver-only tuning sequence or spent-corpus
rescue. Formal holdouts and final >=48-track acceptance remain closed until
the complete candidate meets the existing development prerequisites.

Remaining release work still includes transferable key and beat-lattice/
downbeat candidates, independent acceptance, physical P4 validation and final
freeze/package/tag. Neither search result closes those gates or changes 1.0.1.
