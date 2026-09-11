#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_identifiability as d


class IdentifiabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = d.h.dictionary()

    def test_physical_normalization(self):
        unit, norms, response = self.model
        physical = unit * norms
        np.testing.assert_allclose(np.diag(physical[:, ::3]), response, rtol=1e-15)
        np.testing.assert_allclose(np.linalg.norm(physical, axis=0), norms, rtol=1e-15)
        self.assertTrue(np.array_equal(physical[:, 107], np.zeros(36)))

    def test_pure_witness_reconstructs(self):
        energy = np.arange(36, dtype=float) * 100
        coefficients = d.pure_witness(energy, self.model)
        np.testing.assert_allclose((self.model[0] * self.model[1]) @ coefficients, energy, atol=1e-12)
        np.testing.assert_allclose(d.fundamentals(coefficients, self.model), energy, atol=1e-12)

    def test_zero_column_can_hide_nonzero_fundamental(self):
        coefficients = np.zeros(108)
        coefficients[107] = 810000
        self.assertEqual(np.linalg.norm((self.model[0] * self.model[1]) @ coefficients), 0)
        self.assertGreater(d.fundamentals(coefficients, self.model)[35], 0)

    def test_duplicate_columns_same_spectrum(self):
        info = d.h.dictionary_info(self.model)
        self.assertTrue(info['duplicate_column_pairs'])
        for a, b in info['duplicate_column_pairs']:
            np.testing.assert_array_equal(self.model[0][:, a], self.model[0][:, b])

    def test_pair_equality_and_replay(self):
        for meta in ((0, 0, 0, 1), (3, 1, 4, 2), (11, 1, 5, 3)):
            known, pure, pair = d.witness_pair(meta, self.model)
            known2, pure2, pair2 = d.witness_pair(meta, self.model)
            np.testing.assert_array_equal(known, known2)
            np.testing.assert_array_equal(pure, pure2)
            self.assertEqual(pair, pair2)
            self.assertLessEqual(max(pair['equality_relative_errors']), 1e-12)
        self.assertTrue(pair['invisible_known_columns'])
        with self.assertRaises(ValueError):
            d.witness_pair((0, 0, 1, 1), self.model)

    def test_support_orthogonal_and_empty(self):
        columns = np.eye(36, 3)
        energy = np.zeros(36)
        energy[:4] = [3, 4, 5, 6]
        weights, objective = d.solve_support(energy, columns)
        np.testing.assert_array_equal(weights, [3, 4, 5])
        self.assertEqual(objective, 36)
        weights, objective = d.solve_support(np.zeros(36), columns)
        np.testing.assert_array_equal(weights, [0, 0, 0])
        self.assertEqual(objective, 0)

    def test_support_nonnegative_boundary(self):
        columns = np.zeros((36, 3))
        columns[:2, 0] = [1, 1]
        columns[:2, 1] = [1, 2]
        energy = np.zeros(36)
        energy[0] = 1
        weights, objective = d.solve_support(energy, columns)
        np.testing.assert_allclose(weights, [0.5, 0, 0], atol=1e-15)
        self.assertAlmostEqual(objective, 0.5)

    def test_rank_deficient_support_and_replay(self):
        columns = np.zeros((36, 3))
        columns[0, :2] = 1
        energy = np.zeros(36)
        energy[0] = 7
        weights, objective = d.solve_support(energy, columns)
        self.assertEqual(objective, 0)
        self.assertTrue((weights >= 0).all())
        np.testing.assert_array_equal(columns @ weights, energy)
        repeated, objective2 = d.solve_support(energy, columns)
        np.testing.assert_array_equal(weights, repeated)
        self.assertEqual(objective, objective2)

    def test_strict_comparison_boundary(self):
        self.assertFalse(d.strict_improvement(1e-12, 0, 1))
        self.assertTrue(d.strict_improvement(2e-12, 0, 1))
        self.assertFalse(d.strict_improvement(0, 1, 1))

    def test_invalid_input(self):
        for energy in (np.zeros(12), np.full(36, np.nan), np.full(36, np.inf), np.full(36, -1)):
            with self.assertRaises(ValueError):
                d.solve_support(energy, np.eye(36, 3))
            with self.assertRaises(ValueError):
                d.pure_witness(energy, self.model)
        with self.assertRaises(ValueError):
            d.solve_support(np.zeros(36), np.zeros((36, 4)))
        with self.assertRaises(ValueError):
            d.fundamentals(np.zeros(36), self.model)


if __name__ == '__main__':
    unittest.main()
