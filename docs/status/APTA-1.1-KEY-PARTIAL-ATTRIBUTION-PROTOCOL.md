# Partial-to-fundamental attribution H1 — frozen 2026-09-11

Baseline `6cd9fa45779058aa8b36057180d2e8b9adfebd4b`. This is one host-only,
synthetic representation experiment, not a production detector or transfer
test. Commit this protocol before implementation, and the implementation
before matrix execution. No production C/API/confidence changes, new music,
holdout access, version change, parameter sweep or post-result rescue.

## Hypothesis and evidence

The coverage diagnostic's mean-normalized dense spectrum gets 142/144 final
keys, including 24/24 in each detuned condition, but missing fundamentals
regress from narrow 24/24 to dense 22/24 (local 89/96 -> 66/96). A bounded
partial attribution before octave folding may recover intended fundamental
evidence without changing native profiles, confidence or accumulation.

Reuse only the exact 576 exported windows and locked reports from
`key-coverage-validation-20260910.json`: same six conditions, 24 keys and four
chords. This is already observed synthetic development evidence; passing it
cannot establish generalization. Import the frozen FFT cells, float compression,
folding and native C selector wrapper from `apta_key_coverage_diagnostic.py`.
Do not read stimulus tonic/mode/condition/window in the attribution function.
Metadata and the fundamental oracle are for evaluation only.

## Single fixed representation

Input is the unchanged 36 nonnegative float64 FFT-cell energies C3–B5.
Build a fixed 36-by-108 dictionary in ascending candidate MIDI 48..83 order,
with these three column types per MIDI, in this order:

1. Pure fundamental, h={1}.
2. Fundamental plus partials, h={1,2,3,4}.
3. Missing fundamental, h={2,3,4}.

At nominal equal-tempered frequency f, deposit each partial h*f into the
same half-open geometric cell as the coverage diagnostic, weighted by
`box_response(h*f)^2 / h^2`. The response is the magnitude of the four-sample
48-kHz box average. Discard out-of-range partials, do not renormalize their
physical weights, and disable a column if it is entirely outside the range.
Normalize remaining columns to unit L2 for selection/solving, retaining their
original norms for recovering fundamental-equivalent energy. Missing columns
can be indistinguishable after truncation; report duplicate/zero columns and
do not add an octave prior or tie-breaking rescue.

Start coefficients at zero and residual at the input. Select up to **six**
distinct columns greedily: maximize the positive residual projection squared
onto a unit column; ties use dictionary order. Stop early only if no remaining
projection is positive. After each selection perform exactly **32** cyclic
coordinate-descent sweeps over selected columns in selection order, updating
each coefficient with `max(0, old + dot(column,residual)/dot(column,column))`
and updating the signed residual by the coefficient difference. No residual
clipping, convergence stopping, sparsity penalty, tuning estimate or learned
weights. This is bounded approximate nonnegative fitting, not a claim of a
unique/converged NNLS solution or a six-note limit in music.

Recover a 36-bin fundamental-equivalent energy vector by summing each fitted
coefficient divided by that column's original L2 norm into its candidate MIDI
bin, then multiplying by `box_response(f)^2`. Sum different selected column
types for the same candidate. Apply only the frozen mean-log float transform,
ordered octave folding, four-window accumulation and unchanged C selector.
The entire dictionary is independent of key/mode/chord labels. Its timbres
deliberately match the synthetic test families, limiting any positive result.

## Frozen gates and reporting

Every scientific/resource gate is conjunctive. If any fails, reject H1 for
further implementation and record the complete matrix once; no second variant.

- Preserve **24/24 final matches in each of the first five conditions**, hence
  both detuned directions and both modes; no break versus dense mean-log.
- Missing-fundamental final **24/24**, local **at least 89/96**, and no final
  break versus narrow mean-log. This repairs both dense final regressions while
  preserving the stronger prior local baseline.
- No new confidence>=75 mismatch versus either narrow or dense mean-log,
  separately for local, first-window and final decisions in each condition.
- Overall local matches must not decrease versus dense mean-log. Report every
  group's tonic/mode/joint errors, fixes, breaks, changes and confidence, plus
  first versus final aggregation. Report both baselines, not only the easier one.
- Maximum six selected columns and 672 coordinate updates per window
  (`32*(1+2+3+4+5+6)`). Dictionary storage <=32 KiB (36*108*8=31,104 bytes);
  persistent numeric work arrays <=64 KiB. Record host traced peak allocation
  separately, including Python overhead. Production CPU/RAM/state delta is zero.
- Single-thread host attribution process CPU <=60 seconds for all 576 windows,
  excluding FFT, native selector and report I/O. Record one timed matrix and one
  identity replay; timing is not included in deterministic report equality.
  This is a host-screen limit, not an ESP32-P4 feasibility claim or budget.

Before interpretation require: pinned input/tool/native-object hashes; previous
FFT tolerances unchanged; 576 correctly ordered records; finite nonnegative
outputs; residual equals input minus dictionary reconstruction within
`1e-12*max(1,||input||2)`; every coordinate update is non-increasing in squared
residual within `1e-12*max(1,||input||2^2)`; deterministic complete replay;
default/I1 native selector identity; malformed, nonfinite and wrong-shape input
rejection. Report residual norms and coordinate optimality violations as
diagnostics, not additional tuned stopping criteria.

Unit tests must cover silence, exact isolated full/missing/pure dictionary
columns, mixtures, scaling, no metadata dependency, duplicate/zero columns,
boundaries, finite resource bounds, replay and veto scoring. Do not demand a
unique fundamental label from mathematically duplicate columns. Reuse the
already hash-verified Werror native selector and run the existing coverage
tests against default/I1/sanitizer probes; any new production implementation
would require a separate native/resource protocol.

End with a source-pinned public aggregate, detailed local top-three reports,
hashes, gate decision and one justified next boundary. If H1 passes, it earns
only a separately preregistered timbre/polyphony robustness test before any C
port or independent music split. If rejected, preserve the failure and stop
this method; do not rescue its dictionary/iteration count/order against this
matrix. All six real-audio transfer rejections remain in force.
