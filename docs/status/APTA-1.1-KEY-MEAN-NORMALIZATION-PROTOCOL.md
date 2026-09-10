# Mean-energy normalization candidate — frozen 2026-09-10

Baseline `fbe965bf5d89f52b92413d2fd3d4568dd54dde22`. Prior gain diagnostics
show exact gain-squared raw-energy scaling but gain-dependent compressed
decisions. This single candidate changes only energy scale before compression.
Its protocol precedes code and execution. No corpus or formal holdout is used.

## Formula and boundaries

For each completed window in the default one-probe, 36-bin frontend:

1. Compute the existing resonator energies, mapping negative/nonfinite values
   to zero exactly as the baseline does. Let P be their maximum.
2. If P is zero, contribute zero for all bins. Still complete/reset the window
   under the existing lifecycle; silence does not erase previous evidence.
3. Otherwise compute S = sum(E[i]/P), in ascending bin order using float.
4. Add logf(1 + (E[i]/P) * (36/S)) to the existing octave-folded accumulator.

P avoids overflow when summing raw energies and also supports positive
subnormal input energies. S is in [1,36]; normalization requires no arbitrary
floor, fitted gain, exponent or compression strength. This is division by
window mean expressed safely, with the dimension 36 fixed by bin count.
No tuning of this formula follows observation. The profiles, score ordering,
confidence, cumulative aggregation, window length and sample generation stay
unchanged. All-zero evidence yields no key under the existing selector rule.

Use opt-in `APTA_ENABLE_EXPERIMENTAL_MEAN_NORMALIZED_KEY=ON`; reject combinations
with semitone-band, harmonic/HPCP, centered, temporal-chord, temporal-profile or
spectral key-trace experiments. The synthetic observer remains supported.
Production defaults, public API/ABI, session/result-pool layout and wire format
must remain unchanged. One 36-float local buffer (144 bytes) is allowed; no
post-prepare allocation or retained window history. Maximum measured extra
stack for the key window path is 192 bytes. If retained by the synthetic gate,
measure seven interleaved default/candidate 120-second key-feed benchmark pairs:
median candidate/default CPU ratio must not exceed 1.15. This is host-only
cost evidence, not a complete-path/P4 resource qualification.

## Frozen synthetic retain/reject gates

Use the existing fixed four-window generator and exactly the four previously
registered gains (1/16, 1/4, 1, 2), all 24 keys, clean/detuned/noisy conditions.
Compare against the pinned default gain-1 report. Require:

- identical tonic/mode/confidence/candidate scores at every gain, for every
  corresponding PCM row; raw-energy scaling and observer reconstruction pass;
- at least 9/12 clean-major final matches and at least 11/12 clean-minor final
  matches at every gain;
- across all 72 final progressions, strictly more fixes than breaks versus
  baseline gain 1, and no decrease in minor matches in any of the three
  conditions;
- zero newly high-confidence (>=75) final stimulus mismatches against that
  baseline; confidence must not be rescued by changing its formula;
- default analyzer/key-object identity, no default layout/resource change,
  Release/Werror tests and candidate ASan/UBSan coverage;
- dedicated silence, invalid-energy, extreme finite/subnormal, power-of-two
  scaling and bounded-normalization tests. Reject unsupported flag combinations.

Individual IV/V windows are descriptive and not scored as global-key errors.
Synthetic success permits only retention for a separately defined independent
development comparison. Failure closes this exact candidate; do not sweep
neighboring normalization constants, profiles or confidence thresholds, and do
not open spent FMAK reports or holdouts to rescue it. Record source/binary/report
hashes and every gate, including unexecuted cost/transfer gates after rejection.
