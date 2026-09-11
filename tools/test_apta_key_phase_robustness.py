#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import hashlib
import itertools
import unittest
import numpy as np
import apta_key_phase_robustness as p


class PhaseTests(unittest.TestCase):
    def test_hash_order_replay_and_family(self):
        angles, hashes = p.phases(0, 'known', 0, 3)
        digest = hashlib.sha256(b'apta-f2-20260911|0|known|0|0').digest()
        self.assertEqual(hashes[0], digest.hex())
        self.assertEqual(angles[0], 2*np.pi*int.from_bytes(digest[:8], 'big')/2**64)
        other, other_hashes = p.phases(0, 'known', 0, 3)
        np.testing.assert_array_equal(angles, other)
        self.assertEqual(hashes, other_hashes)
        self.assertNotEqual(hashes, p.phases(0, 'pure', 0, 3)[1])
        self.assertNotEqual(hashes, p.phases(0, 'known', 1, 3)[1])
        self.assertTrue(((angles >= 0) & (angles < 2*np.pi)).all())

    def test_single_quadrature_average(self):
        components = [dict(frequency_hz=440.3, amplitude=0.15)]
        reference, _, _ = p.marginal_reference(components)
        powers = []
        for angle in (0, np.pi/2, np.pi, 3*np.pi/2):
            wave = p.f.average_four(p.component_wave(components[0], angle), np.float64)
            powers.append(np.abs(np.fft.rfft(wave))**2)
        self.assertLess(np.linalg.norm(np.mean(powers, axis=0)-reference)/np.linalg.norm(reference), 1e-12)

    def test_two_component_cross_terms_cancel(self):
        components = [dict(frequency_hz=698.456, amplitude=0.075), dict(frequency_hz=699.246, amplitude=0.05)]
        reference, _, _ = p.marginal_reference(components)
        powers = []
        for angles in itertools.product((0, np.pi/2, np.pi, 3*np.pi/2), repeat=2):
            samples = sum(p.component_wave(component, angle) for component, angle in zip(components, angles))
            wave = p.f.average_four(samples, np.float64)
            powers.append(np.abs(np.fft.rfft(wave))**2)
        self.assertLess(np.linalg.norm(np.mean(powers, axis=0)-reference)/np.linalg.norm(reference), 1e-12)

    def test_observation_float_replay(self):
        components = [dict(frequency_hz=831.5, amplitude=0.05)]
        first, relative, absolute = p.observation(components, [1.7])
        second, _, _ = p.observation(components, [1.7])
        self.assertEqual(first.dtype, np.float32)
        np.testing.assert_array_equal(first, second)
        self.assertLessEqual(relative, 1e-6)
        self.assertLessEqual(absolute, 1e-6)

    def test_score_cell_gain_invariance_and_margin(self):
        power = np.arange(1, 6002, dtype=float)
        scaled = power.copy()
        cells = p.f.c.cell_indices(np.arange(6001))
        for i in range(36):
            scaled[cells == i] *= 2**(i % 6)
        score, _ = p.f.fine_distance(power, scaled, np.ones(36))
        self.assertEqual(score, 0)
        self.assertFalse(p.passes(0, 1e-6))
        self.assertTrue(p.passes(0, 2e-6))
        self.assertFalse(p.passes(0.5, 0.4))

    def test_invalid(self):
        for args in ((0, 'bad', 0, 1), (0, 'known', 32, 1), (0, 'known', 0, 0)):
            with self.assertRaises(ValueError):
                p.phases(*args)
        with self.assertRaises(ValueError):
            p.observation([], [])
        with self.assertRaises(ValueError):
            p.component_wave(dict(frequency_hz=np.nan, amplitude=1), 0)
        with self.assertRaises(ValueError):
            p.marginal_reference([])


if __name__ == '__main__':
    unittest.main()
