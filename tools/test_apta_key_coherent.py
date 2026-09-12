#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import hashlib
import inspect
import unittest

import numpy as np
import apta_key_coherent as c


class CoherentTests(unittest.TestCase):
    def test_new_phase_hash_and_replay(self):
        angles, hashes = c.phases(0, 'known', 0, 3)
        digest = hashlib.sha256(b'apta-c1-20260912|0|known|0|0').digest()
        self.assertEqual(hashes[0], digest.hex())
        self.assertEqual(angles[0], 2*np.pi*(int.from_bytes(digest[:8], 'big')/2**64))
        repeated, repeated_hashes = c.phases(0, 'known', 0, 3)
        np.testing.assert_array_equal(angles, repeated)
        self.assertEqual(hashes, repeated_hashes)
        self.assertNotEqual(hashes, c.p.phases(0, 'known', 0, 3)[1])
        self.assertNotEqual(hashes, c.phases(0, 'pure', 0, 3)[1])

    def test_exact_sine_cosine_unknown_phase(self):
        components = [dict(frequency_hz=440.3, amplitude=0.15)]
        model, info = c.build_model(components)
        for phase in (0, np.pi/2, 1.73):
            wave = c.p.component_wave(components[0], phase)
            averaged = c.p.f.average_four(wave, np.float64)
            result = c.fit(c.real_vector(np.fft.rfft(averaged)), model, verify=True)
            self.assertLess(result['normalized_squared_residual'], 1e-20)
            np.testing.assert_allclose(result['physical_sine_cosine_coefficients'],
                                       [0.15*np.cos(phase), 0.15*np.sin(phase)], atol=1e-12)
        self.assertEqual(info['rank'], 2)

    def test_mixed_frequencies_and_float_rounding(self):
        components = [dict(frequency_hz=698.456, amplitude=0.075),
                      dict(frequency_hz=699.246, amplitude=0.05),
                      dict(frequency_hz=1108.731, amplitude=0.0375)]
        angles = [0.7, 2.9, 1.2]
        model, info = c.build_model(components)
        pcm, _, _ = c.p.observation(components, angles)
        observed = c.real_vector(np.fft.rfft(pcm.astype(float)))
        result = c.fit(observed, model, verify=True)
        self.assertLess(result['normalized_squared_residual'], 1e-10)
        expected = [v for component, phase in zip(components, angles)
                    for v in (component['amplitude']*np.cos(phase), component['amplitude']*np.sin(phase))]
        np.testing.assert_allclose(result['physical_sine_cosine_coefficients'], expected, atol=1e-6)
        self.assertEqual(info['rank'], 6)
        self.assertEqual(result, c.fit(observed, model, verify=True))

    def test_absent_frequency(self):
        model, _ = c.build_model([dict(frequency_hz=440, amplitude=1)])
        wave = c.p.component_wave(dict(frequency_hz=550, amplitude=0.2), 0.7)
        observed = c.real_vector(np.fft.rfft(c.p.f.average_four(wave, np.float64)))
        result = c.fit(observed, model, verify=True)
        self.assertGreater(result['normalized_squared_residual'], 0.99)

    def test_dependent_columns(self):
        raw = np.array([[1., 2.], [2., 4.], [3., 6.]])
        model = c.factor_matrix(raw)
        self.assertEqual(model['rank'], 1)
        result = c.fit(np.array([3., 6., 9.]), model, verify=True)
        self.assertLess(result['normalized_squared_residual'], 1e-20)

    def test_fitter_no_generating_metadata(self):
        self.assertEqual(list(inspect.signature(c.fit).parameters), ['observation', 'model', 'verify'])
        self.assertNotIn('generating_family', inspect.getsource(c.fit))
        self.assertNotIn('phases', inspect.getsource(c.fit))

    def test_margin_and_reconstruction_boundaries(self):
        self.assertTrue(c.passes(1e-10, 2e-6))
        self.assertFalse(c.passes(2e-10, 2e-6))
        self.assertFalse(c.passes(0, 1e-6))
        self.assertFalse(c.passes(0.1, 0.01))

    def test_invalid(self):
        for raw in (np.zeros((4, 2)), np.full((4, 2), np.nan), np.zeros(4)):
            with self.assertRaises(ValueError):
                c.factor_matrix(raw)
        model = c.factor_matrix(np.eye(3))
        for observation in (np.zeros(3), np.ones(4), np.full(3, np.inf)):
            with self.assertRaises(ValueError):
                c.fit(observation, model)
        with self.assertRaises(ValueError):
            c.real_vector(np.zeros(4))
        with self.assertRaises(ValueError):
            c.build_model([])
        with self.assertRaises(ValueError):
            c.phases(0, 'known', 32, 1)


if __name__ == '__main__':
    unittest.main()
