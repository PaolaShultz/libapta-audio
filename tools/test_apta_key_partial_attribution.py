#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import inspect
import unittest

import numpy as np
import apta_key_partial_attribution as h


class AttributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = h.dictionary()

    def test_dictionary_bounds_and_truncation(self):
        matrix, norms, response = self.model
        self.assertEqual(matrix.shape, (36, 108))
        self.assertTrue(np.isfinite(matrix).all() and (matrix >= 0).all())
        np.testing.assert_allclose(np.linalg.norm(matrix[:, norms > 0], axis=0), 1, atol=1e-15)
        self.assertTrue((response > 0).all())
        info = h.dictionary_info(self.model)
        self.assertEqual(info['dictionary_bytes'], 31104)
        self.assertLessEqual(info['named_numeric_workspace_bound_bytes'], 65536)
        self.assertTrue(info['duplicate_column_pairs'])
        self.assertIn(107, info['disabled_columns'])
        self.assertEqual(norms[107], 0)

    def test_silence(self):
        energy, fit = h.attribute(np.zeros(36), self.model)
        self.assertEqual(energy.sum(), 0)
        self.assertEqual(fit['selected'], [])
        self.assertEqual(fit['coordinate_updates'], 0)

    def test_isolated_pure_full_missing(self):
        for index in (0, 1, 2, 36, 37, 38, 105, 106):
            matrix, norms, _ = self.model
            energy, fit = h.attribute(matrix[:, index] * norms[index] * 100, self.model)
            self.assertLess(fit['residual_relative_norm'], 1e-10)
            self.assertTrue(np.isfinite(energy).all() and (energy >= 0).all())
            # Upper-range duplicate templates do not identify a unique source.
            if index < 3:
                self.assertEqual(int(np.argmax(energy)), 0)

    def test_mixture_fit_objective_and_bounds(self):
        matrix, norms, _ = self.model
        source = sum(matrix[:, i] * norms[i] * amplitude
                     for i, amplitude in ((1, 100), (14, 70), (21, 80)))
        energy, fit = h.attribute(source, self.model)
        self.assertGreater(energy.sum(), 0)
        self.assertLess(fit['residual_relative_norm'], 1)
        self.assertLessEqual(fit['max_objective_increase_scaled'], 1e-12)
        self.assertLessEqual(fit['residual_identity_error'], 1e-12)
        self.assertLessEqual(len(fit['selected']), 6)
        self.assertLessEqual(fit['coordinate_updates'], 672)

    def test_scale_replay_and_no_input_mutation(self):
        source = np.arange(1, 37, dtype=float)
        before = source.copy()
        energy, fit = h.attribute(source, self.model)
        repeated, repeated_fit = h.attribute(source, self.model)
        scaled, _ = h.attribute(source * 16, self.model)
        np.testing.assert_array_equal(source, before)
        np.testing.assert_array_equal(energy, repeated)
        self.assertEqual(fit, repeated_fit)
        np.testing.assert_allclose(scaled, energy * 16, rtol=1e-12, atol=1e-12)

    def test_no_metadata_dependency(self):
        self.assertEqual(list(inspect.signature(h.attribute).parameters), ['energy', 'model'])
        body = inspect.getsource(h.attribute)
        for name in ('tonic', 'mode', 'condition', 'window', 'expected', 'oracle'):
            # 'model' is the fixed dictionary, not the stimulus mode.
            import re
            self.assertIsNone(re.search(r'\b' + name + r'\b', body))

    def test_invalid_inputs(self):
        for source in (np.zeros(12), np.zeros((1, 36)), np.full(36, np.nan),
                       np.full(36, np.inf), np.full(36, -1)):
            with self.assertRaises(ValueError):
                h.attribute(source, self.model)

    def test_gate_vetoes(self):
        def passing():
            return [dict(mode='all', condition=c, scope=scope, baseline=baseline,
                         count=96 if scope == 'local' else 24,
                         matches=96 if scope == 'local' else 24,
                         fixes=0, breaks=0, new_high_confidence_errors=0)
                    for c in h.coverage.CONDITIONS for scope in ('local', 'first', 'final')
                    for baseline in ('narrow', 'dense')]
        self.assertTrue(all(h.scientific_gates(passing()).values()))
        for change, field in ((dict(condition='clean', scope='final', matches=23), 'first_five_final_24'),
                              (dict(condition='missing-fundamental', scope='final', matches=23), 'missing_final_24'),
                              (dict(condition='missing-fundamental', scope='local', matches=88), 'missing_local_at_least_89'),
                              (dict(condition='noise', scope='first', new_high_confidence_errors=1), 'no_new_high_confidence_errors'),
                              (dict(condition='noise', scope='final', breaks=1), 'no_final_break_vs_dense'),
                              (dict(condition='noise', scope='local', breaks=1), 'overall_local_no_decrease_vs_dense')):
            rows = passing()
            row = next(r for r in rows if r['condition'] == change['condition'] and r['scope'] == change['scope']
                       and r['baseline'] == 'dense')
            row.update(change)
            self.assertFalse(h.scientific_gates(rows)[field])
        with self.assertRaises(ValueError):
            h.scientific_gates([])


if __name__ == '__main__':
    unittest.main()
