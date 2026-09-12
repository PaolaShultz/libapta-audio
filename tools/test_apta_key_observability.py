# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_observability as o


class ObservabilityTests(unittest.TestCase):
    def test_geometric_integral(self):
        np.testing.assert_array_equal(o.geometric([0, 1, -1, 12000, -12000]), [12000, 0, 0, 12000, 12000])

    def test_geometric_fractional(self):
        offsets = [0.125, -0.75, 1+2**-28]
        direct = np.array([np.exp(2j*np.pi*r*np.arange(o.N)/o.N).sum() for r in offsets])
        np.testing.assert_allclose(o.geometric(offsets), direct, atol=1e-10, rtol=1e-10)

    def test_structural_zero(self):
        np.testing.assert_array_equal(o.raw_pair(1200), np.zeros((1778, 2)))
        model, info = o.build_model([1200.])
        self.assertIsNone(model)
        self.assertEqual(info['status'], 'abstain_empty')
        with self.assertRaises(ValueError):
            o.fit(np.ones(1778), model)

    def test_near_grid_no_snapping(self):
        model, info = o.build_model([1200.+2**-40])
        self.assertEqual(info['structural_zero_components'], [])
        self.assertEqual(info['weak_components'], [0])
        self.assertEqual(info['status'], 'abstain_weak')
        self.assertIsNone(model)

    def test_floor_inclusive(self):
        self.assertTrue(o.weak_pair([o.FLOOR, 1.]))
        self.assertFalse(o.weak_pair([np.nextafter(o.FLOOR, np.inf), 1.]))

    def test_mixed_null_amplitude(self):
        model, info = o.build_model([440., 1200.])
        self.assertEqual(info['status'], 'ready')
        # Independent waveform contains an unobservable component with nonzero amplitude.
        phase = 2*np.pi*np.arange(48000)/48000
        wave = .3*np.sin(440*phase)+.2*np.cos(440*phase)+.4*np.sin(1200*phase)
        obs = o.c.real_vector(np.fft.rfft(o.c.p.f.average_four(wave, np.float64)))
        result = o.fit(obs, model)
        self.assertLess(result['normalized_squared_residual'], 1e-10)
        np.testing.assert_allclose(result['physical_sine_cosine_coefficients'][:2], [.3, .2], atol=1e-10)
        self.assertEqual(result['physical_sine_cosine_coefficients'][2:], [None, None])

    def test_weak_abstains_whole_model(self):
        model, info = o.build_model([440., 1200.+2**-40])
        self.assertIsNone(model)
        self.assertEqual(info['status'], 'abstain_weak')

    def test_duplicate_rank_abstention(self):
        model, info = o.build_model([440., 440.])
        self.assertIsNone(model)
        self.assertEqual(info['status'], 'abstain_rank')

    def test_visible_grid(self):
        raw = o.raw_pair(440.)
        self.assertEqual(np.count_nonzero(np.linalg.norm(raw.reshape(2, 889, 2), axis=(0, 2))), 1)
        np.testing.assert_allclose(raw, o.independent_pair(440.), atol=1e-8)

    def test_invalid(self):
        for frequency in [0, -1, 6000, np.inf, np.nan]:
            with self.assertRaises(ValueError):
                o.build_model([frequency])
        with self.assertRaises(ValueError):
            o.build_model([])


if __name__ == '__main__':
    unittest.main()
