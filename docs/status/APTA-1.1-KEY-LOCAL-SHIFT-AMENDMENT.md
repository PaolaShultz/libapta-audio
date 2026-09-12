# R1 pre-evaluation amendment — 2026-09-12

Original protocol commit: `c88b57d`. This amendment is recorded after unit-test
implementation but before instrument freeze and before any R1 bank evaluation.
No bank scores or recovery results have been observed.

The original +/-0.375 Hz seed errors exactly coincide with the 1/32 Hz search
grid. They would permit perfect recovery by the coarse grid and would not
exercise local interpolation. Replace the two seed errors with **-0.37 and
+0.37 Hz**, which lie off the grid. All supports, source waveforms, amplitudes,
phases, 48-case count, estimator construction, budgets and gates are unchanged.
This is a design correction before evaluation, not a response to scientific
failure. Read this amendment together with the immutable original protocol.
