#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import os
import struct
import subprocess
import unittest

import numpy as np
import apta_key_coverage_diagnostic as d


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = np.zeros(576, dtype=d.DTYPE)
        cls.records["metadata"] = d.metadata()
        cls.data = b"APTCOV01" + cls.records.tobytes()

    def test_complete_export(self):
        self.assertEqual(len(d.parse_export(self.data)), 576)

    def test_bad_magic_length_truncation_extra(self):
        for data in (b"BADMAGIC" + self.data[8:], self.data[:-1], self.data + b"x", b"APTCOV01"):
            with self.assertRaises(ValueError):
                d.parse_export(data)

    def test_reordering_nonfinite_coefficient_drift(self):
        for field, value in (("metadata", 99), ("samples", np.nan),
                             ("samples", np.inf), ("coefficients", 3), ("coefficients", 0.5)):
            records = self.records.copy()
            records[field][1, 0] = value
            with self.assertRaises(ValueError):
                d.parse_export(b"APTCOV01" + records.tobytes())

    def test_cell_boundaries_and_outside(self):
        self.assertEqual(d.cell_indices(d.EDGES).tolist(), list(range(37)))
        self.assertEqual(d.cell_indices(np.nextafter(d.EDGES, -np.inf)).tolist(), list(range(-1, 36)))
        result = d.integrate(np.array([0, d.EDGES[0], d.EDGES[-1], 6000]), np.ones(4))
        self.assertEqual(result.sum(), 1)
        self.assertEqual(result[0], 1)

    def test_silence_and_impulse_fft(self):
        zero, p, f = d.spectrum(np.zeros(d.N))
        self.assertEqual((zero.sum(), p, f), (0, 0, 0))
        impulse = np.zeros(d.N)
        impulse[0] = 1
        energy, _, _ = d.spectrum(impulse)
        expected = d.integrate(np.arange(d.N // 2 + 1), np.ones(d.N // 2 + 1))
        np.testing.assert_array_equal(energy, expected)

    def test_integer_bin_tone(self):
        tone = np.sin(2 * np.pi * 440 * np.arange(d.N) / d.N)
        energy, _, _ = d.spectrum(tone)
        self.assertAlmostEqual(energy[d.cell_indices(440)], (d.N / 2) ** 2, places=6)
        self.assertLess(energy.sum() - energy.max(), 1e-12)

    def test_bad_fft(self):
        for samples in (np.zeros(3), np.full(d.N, np.nan)):
            with self.assertRaises(ValueError):
                d.spectrum(samples)

    def test_mean_scaling_and_fold_order(self):
        logf = d.logf_function()
        energy = np.arange(36, dtype=d.F)
        np.testing.assert_array_equal(d.compress(energy, "mean-log", logf),
                                      d.compress(energy * 16, "mean-log", logf))
        np.testing.assert_array_equal(d.compress(np.zeros(36), "mean-log", logf), np.zeros(36))
        compressed = d.compress(energy, "absolute-log", logf)
        result = d.fold_add(np.zeros(12, dtype=d.F), compressed)
        for p in range(12):
            self.assertEqual(result[p], d.F(d.F(compressed[p] + compressed[p + 12]) + compressed[p + 24]))

    def test_oracle_local_v_major_and_missing_fundamental(self):
        self.assertEqual(d.chord(0, 1, 2), (5, 1))
        self.assertEqual(d.chord(0, 1, 3), (7, 0))
        clean, fraction, fundamental = d.oracle(0, 1, 0, 1)
        missing, missing_fraction, missing_fundamental = d.oracle(0, 1, 5, 1)
        self.assertAlmostEqual(fraction, 1)
        self.assertGreater(missing_fraction, 0)
        np.testing.assert_array_equal(fundamental, missing_fundamental)
        self.assertEqual(fundamental.nonzero()[0].tolist(), [0, 3, 7])
        self.assertFalse(np.array_equal(clean, missing))

    def test_scoring_modes_tonics_confidence_and_alignment(self):
        def row(t, m, confidence):
            return dict(id=[0, 0, 0, 4], expected=[0, 0],
                        result=dict(available=True, tonic=t, mode=m, confidence=confidence))
        base = [row(0, 0, 90)] * 4
        rows = [row(0, 0, 90), row(1, 0, 75), row(0, 1, 74), row(1, 1, 76)]
        score = d.score_group(rows, base)
        self.assertEqual(score["matches"], 1)
        self.assertEqual([score[k] for k in ("tonic_only_errors", "mode_only_errors", "tonic_and_mode_errors")], [1, 1, 1])
        self.assertEqual(score["new_high_confidence_errors"], 2)
        self.assertEqual(score["breaks"], 3)
        self.assertEqual(d.score_group(base, rows)["fixes"], 3)
        rows[0]["id"][0] = 1
        with self.assertRaises(ValueError):
            d.score_group(rows, base)

    def test_native_probe_valid_silence_and_invalid(self):
        path = os.environ.get("APTA_COVERAGE_PROBE")
        self.assertIsNotNone(path, "set APTA_COVERAGE_PROBE to the built C probe")
        triad = np.zeros(12, dtype=d.F)
        triad[[0, 4, 7]] = 1
        results = d.query_probe(path, [(triad, 1), (np.zeros(12, dtype=d.F), 1)])
        self.assertTrue(results[0]["available"])
        self.assertEqual(results[1], {"available": False})
        self.assertEqual(len(results[0]["candidates"]), 3)
        for data in (b"x", triad.tobytes(), triad.tobytes() + struct.pack("<I", 0),
                     np.full(12, np.nan, dtype="<f4").tobytes() + struct.pack("<I", 1)):
            result = subprocess.run([path, "--binary"], input=data, capture_output=True)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
