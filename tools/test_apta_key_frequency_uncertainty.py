#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import copy
import hashlib
import unittest

import numpy as np
import apta_key_frequency_uncertainty as u


class UncertaintyTests(unittest.TestCase):
    def test_exact_and_no_mutation(self):
        source = [dict(frequency_hz=440.3, amplitude=0.15)]
        snapshot = copy.deepcopy(source)
        result, _ = u.perturb(source, 'exact', 0, 'known')
        self.assertEqual(result, snapshot)
        result[0]['frequency_hz'] = 500
        self.assertEqual(source, snapshot)

    def test_quarter_shifts(self):
        source = [dict(frequency_hz=440.3), dict(frequency_hz=1108.7)]
        for name, shift in (('minus-quarter-hz', -0.25), ('plus-quarter-hz', 0.25)):
            result, provenance = u.perturb(source, name, 0, 'known')
            self.assertEqual([r['frequency_hz'] for r in result], [440.3+shift, 1108.7+shift])
            self.assertTrue(all(r['offset_hz'] == shift for r in provenance))

    def test_independent_hash_and_replay(self):
        source = [dict(frequency_hz=440.3)]
        digest = hashlib.sha256(b'apta-c2-20260912|0|known|0').digest()
        result, provenance = u.perturb(source, 'independent-quarter-hz', 0, 'known')
        self.assertEqual(provenance[0]['sign_sha256'], digest.hex())
        self.assertEqual(result[0]['frequency_hz'], 440.3+(0.25 if digest[0]&1 else -0.25))
        self.assertEqual((result, provenance), u.perturb(source, 'independent-quarter-hz', 0, 'known'))

    def test_nearest_hz_ties(self):
        source = [dict(frequency_hz=v) for v in (440.49, 440.5, 440.51, 1108.0)]
        result, provenance = u.perturb(source, 'nearest-hz', 0, 'pure')
        self.assertEqual([r['frequency_hz'] for r in result], [440, 441, 441, 1108])
        self.assertEqual(provenance[1]['offset_hz'], 0.5)

    def test_shifted_fit_and_fixed_phase_source(self):
        source = [dict(frequency_hz=440.3, amplitude=0.15)]
        snapshot = copy.deepcopy(source)
        angles, hashes = u.c.phases(0, 'known', 0, 1)
        pcm, _, _ = u.c.p.observation(source, angles)
        observed = u.c.real_vector(np.fft.rfft(pcm.astype(float)))
        exact, _ = u.c.build_model(source)
        shifted, _ = u.perturb(source, 'plus-quarter-hz', 0, 'known')
        approximate, _ = u.c.build_model(shifted)
        true_fit = u.c.fit(observed, exact, verify=True)
        wrong_fit = u.c.fit(observed, approximate, verify=True)
        self.assertLess(true_fit['normalized_squared_residual'], 1e-10)
        self.assertGreater(wrong_fit['normalized_squared_residual'], 0.01)
        self.assertEqual(source, snapshot)
        np.testing.assert_array_equal(pcm, u.c.p.observation(source, u.c.phases(0, 'known', 0, 1)[0])[0])
        self.assertEqual(hashes, u.c.phases(0, 'known', 0, 1)[1])

    def test_separate_gate_boundaries(self):
        self.assertTrue(u.gates(0.10, 0.2)['screen_pass'])
        self.assertFalse(u.gates(0.10001, 0.2)['screen_pass'])
        self.assertTrue(u.gates(0.10001, 0.2)['discrimination_pass'])
        self.assertTrue(u.gates(1e-10, 0.2, exact=True)['screen_pass'])
        self.assertFalse(u.gates(2e-10, 0.2, exact=True)['screen_pass'])
        self.assertFalse(u.gates(0, 1e-6)['discrimination_pass'])
        self.assertFalse(u.gates(0.09, 0.08)['discrimination_pass'])

    def test_invalid_constructions(self):
        for condition in ('bad', ''):
            with self.assertRaises(ValueError):
                u.perturb([dict(frequency_hz=440)], condition, 0, 'known')
        for frequency in (np.nan, np.inf, -1, 0.1):
            with self.assertRaises(ValueError):
                u.perturb([dict(frequency_hz=frequency)], 'minus-quarter-hz', 0, 'known')
        with self.assertRaises(ValueError):
            u.perturb([], 'exact', 0, 'known')


if __name__ == '__main__':
    unittest.main()
