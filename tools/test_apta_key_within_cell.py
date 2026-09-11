#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_within_cell as f


class WithinCellTests(unittest.TestCase):
    def test_identity_and_gain_invariance(self):
        a = np.arange(1, 6002, dtype=float)
        ideal = np.arange(1, 37, dtype=float)
        score, _ = f.fine_distance(a, a, ideal)
        self.assertEqual(score, 0)
        b = a.copy()
        cells = f.c.cell_indices(np.arange(6001))
        for cell in range(36):
            b[cells == cell] *= 2 ** (cell % 6)
        score, _ = f.fine_distance(a, b, ideal)
        self.assertEqual(score, 0)

    def test_shape_difference_with_equal_cell_energy(self):
        ideal = np.zeros(36)
        ideal[0] = 1
        a, b = np.zeros(6001), np.zeros(6001)
        a[130], b[131] = 1, 1
        score, _ = f.fine_distance(a, b, ideal)
        self.assertEqual(score, 2)

    def test_ordered_float32_average(self):
        source = np.tile(np.array([1e8, 1, -1e8, 1], dtype=float), 12000)
        np.testing.assert_array_equal(f.average_four(source, np.float32), np.full(12000, 0.25))
        np.testing.assert_array_equal(f.average_four(source, np.float64), np.full(12000, 0.5))

    def test_reference_replay(self):
        example = dict(id=[0, 0, 5, 1], known_nonzero_coefficients=[dict(midi=48, family=2, coefficient=810000)],
                       pure_nonzero_coefficients=[dict(midi=60, family=0, coefficient=202500)])
        for kind in ('known', 'pure'):
            first, components = f.reference(example, kind)
            second, components2 = f.reference(example, kind)
            np.testing.assert_array_equal(first, second)
            self.assertEqual(components, components2)
            self.assertTrue(np.isfinite(first).all())
        with self.assertRaises(ValueError):
            f.reference(example, 'other')

    def test_invalid_and_silence(self):
        for a in (np.zeros(6001), np.zeros(3), np.full(6001, np.nan), np.full(6001, -1)):
            with self.assertRaises(ValueError):
                f.fine_distance(a, np.ones(6001), np.ones(36))
        with self.assertRaises(ValueError):
            f.fine_distance(np.ones(6001), np.ones(6001), np.zeros(36))
        with self.assertRaises(ValueError):
            f.average_four(np.zeros(12000), np.float32)

    def test_fft_and_margin(self):
        source = np.sin(2*np.pi*440*np.arange(12000)/12000)
        power, _, parseval, direct = f.checked_power(source)
        self.assertEqual(int(np.argmax(power)), 440)
        self.assertLessEqual(parseval, 1e-12)
        self.assertLessEqual(direct, 1e-9)
        self.assertFalse(f.supports(0, 1e-9))
        self.assertTrue(f.supports(0, 2e-9))
        self.assertFalse(f.supports(0.01, 0.5))


if __name__ == '__main__':
    unittest.main()
