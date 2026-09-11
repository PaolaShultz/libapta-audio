# Tonal evidence identifiability I1 — frozen 2026-09-11

Baseline `220f203759d54ea9c98a2fe843b0646eda757998`. Report-only diagnosis of
the rejected H1 representation, not another fitter or detector. Freeze this
protocol before implementation and commit the instrument before execution.
No production changes, H1 changes, confidence/profile changes, music access,
new timbre/threshold sweep or acceptance claim.

## Questions and fixed evidence

H1 gives all 144 final synthetic keys but misses 12 local missing-fundamental
minor chords (relative-major selections). Exact duplicate dictionary columns
were recorded, without proving that they explain these misses. Distinguish:

1. Equal evidence caused by range truncation, and whether it changes pitch
   class rather than only octave/timbre.
2. Explicit nonnegative combinations with identical retained spectral energy
   but different intended fundamental/chord evidence.
3. Whether a feasible fit on the known source-note support has lower residual
   than the fixed H1 output. Such a witness proves that H1 did not attain the
   best residual even on that available support; the converse proves nothing
   about global optimality or unique fundamentals.

Use only the previously pinned 576 coverage PCM windows, coverage reports and
H1 reports. Imports must match their recorded SHA256. Reuse H1's unchanged
108-column dictionary, coverage FFT/oracle/compression and the same pinned
C selectors. Stimulus metadata is permitted only to construct explicitly
labeled diagnostic witnesses; it must never become an estimator input.

## Fixed witnesses

Reconstruct physical (unnormalized) dictionary columns from H1 unit columns
and their stored norms. Map coefficient vectors to fundamental energy by
summing coefficients per MIDI and multiplying by the box response squared.
This mapping also represents invisible source notes whose dictionary column
is zero; H1 cannot infer their amplitudes from those zero columns.

For all 108 single columns report: zero/nonzero, original norm, exact duplicate
pairs, and whether each pair has the same pitch class or a different one.
No numerical near-duplicate threshold or approximate uniqueness claim.

For exactly the 288 windows in nominal clean, fundamental-plus-harmonics and
missing-fundamental conditions (0,4,5), construct two coefficient witnesses:

- Known-source witness: three physical columns for the known note pitches and
  family, each with coefficient `(12000*0.15/2)^2 = 810000`. Report any entirely
  invisible note; do not delete it from the intended fundamental vector.
- Pure-component witness: represent the exact same ideal 36-cell energy using
  the 36 pure-tone dictionary columns, with each coefficient equal to that
  cell energy divided by its pure-column box response squared.

Require each witness spectrum to equal the frozen ideal component oracle and
the other witness within relative L2 `1e-12*max(1,||oracle||2)`. This equality
concerns the ideal dictionary/cell model, not actual finite-window FFTs,
waveforms, detuned partials, injected noise or real songs. Do not claim identical
PCM. Count active physical columns, including invisible nonzero sources, and
report whether both witnesses meet H1's six-column cardinality cap. No sparsity
penalty or least-component preference is introduced.

Feed both witnesses' fundamental energy through unchanged mean-log, folding
and the actual C selector for **local windows only**. Report known-chord match,
tonic/mode errors, changed verdicts and confidence by condition and mode.
Differences prove non-unique fundamental/key interpretation in the stated
model, not that the ambiguous alternative is the true source. Verify against
the existing component-oracle mean-log local results for the pure witness.

## Known-support fit comparison

For all 576 actual dense spectra, choose only the three known note/family
columns (pure for conditions 0..3, full for 4, missing for 5). Keep their nominal
frequencies unchanged even for +/-1/3 detuning. On this label-selected support,
enumerate all eight active subsets including the empty subset. Use float64
least squares, discard a subset if any coefficient < -1e-12, clamp remaining
roundoff-negative coefficients to zero, and keep the smallest actual squared
residual. Ties use subset order. Zero columns are allowed. No global 108-column
refit, extra H1 iterations or dictionary change.

Require finite/nonnegative candidate coefficients and actual reconstruction.
This oracle-support result is a feasible diagnostic witness, not a deployable
prediction. Count a strict residual improvement only if the normalized squared
residual reduction exceeds `1e-12*max(1,||input||2^2)`. Report other cases as
no strict improvement; do not infer global optimality. Cross-tabulate with all
14 H1 local errors and with the 12 missing-fundamental errors. Preserve their
original verdicts rather than reranking a refitted H1 candidate.

## Correctness, costs and stop rules

- Verify pinned sources, exports, prior reports, C probes and production
  binaries/objects before interpretation. Input order/length and FFT tolerance
  gates are inherited unchanged from the coverage tool.
- Reconstruct every H1 spectrum/residual from its recorded selected columns and
  weights; require recorded residual-relative norm agreement within `1e-12`.
- Test zero/duplicate columns, physical/unit normalization, pure witnesses,
  invisible notes, nonnegative support solves (including rank deficiency),
  invalid inputs, comparator tolerance and deterministic replay.
- Exactly 288 witness pairs, 576 support comparisons and 576 local C requests;
  default/I1 selector equality and complete report replay are required.
- Host-only dictionary/linear algebra; no production CPU/RAM/state delta.
  Record single-thread process CPU and first-call traced peak separately from
  deterministic reports. Stop as an instrument/resource failure if analysis
  exceeds 120 process CPU seconds. This is not an ESP32-P4 budget.

Any correctness failure stops interpretation until repaired with its history
preserved; do not relax tolerances. No candidate retention/acceptance decision
is possible from this diagnostic. End with exact witnesses, scope limits, a
source-pinned report and one justified next research boundary. H1 remains
rejected regardless of the outcome, and all corpus/holdout seals remain intact.
