# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_local_shift as r


class LocalShiftTests(unittest.TestCase):
    def test_budget_inclusive(self):
        self.assertTrue(r.amplitude_valid([1., 0.]))
        self.assertFalse(r.amplitude_valid([np.nextafter(1., np.inf), 0.]))
        self.assertFalse(r.amplitude_valid([.6, 0., .5, 0.]))

    def test_amplitude_reject_not_clip(self):
        raw = r.o.independent_pair(300.)
        result = r.fit(raw @ [1.2, .2], [300.])
        self.assertEqual(result['status'], 'amplitude')
        self.assertIsNone(result['score'])
        self.assertGreater(result['amplitudes'][0], 1.)

    def test_weak_and_rank(self):
        self.assertEqual(r.factor(np.zeros((1778, 2)))[1], 'weak')
        pair = r.o.raw_pair(300.)
        self.assertEqual(r.factor(np.column_stack([pair, pair]))[1], 'rank')

    def test_invalid_observations(self):
        for observation in (np.zeros(1778), np.full(1778, np.nan), np.ones(3)):
            with self.assertRaises(ValueError):
                r.fit(observation, [300.])
        with self.assertRaises(ValueError):
            r.fit(np.ones(1778), [6000.])

    def test_search_budget_and_bounds(self):
        best, calls = r.search(lambda x: dict(score=(x-.12345)**2, status='ready'))
        self.assertEqual(len(calls), 59)
        self.assertLess(abs(best['shift_hz']-.12345), 1e-5)
        self.assertTrue(all(-.5 <= c['shift_hz'] <= .5 for c in calls))

    def test_endpoints_and_ties(self):
        for target in (-.5, .5):
            best, _ = r.search(lambda x: dict(score=(x-target)**2))
            self.assertEqual(best['shift_hz'], target)
        best, _ = r.search(lambda x: dict(score=1.))
        self.assertEqual(best['shift_hz'], -.5)

    def test_all_invalid(self):
        best, calls = r.search(lambda x: dict(score=None))
        self.assertIsNone(best)
        self.assertEqual(len(calls), 33)

    def test_partial_invalid(self):
        best, _ = r.search(lambda x: dict(score=(x-.2)**2 if x > 0 else None))
        self.assertLess(abs(best['shift_hz']-.2), 1e-5)

    def test_phase_identity(self):
        a, hashes = r.phases(0, 0, 2)
        b, repeated = r.phases(0, 0, 2)
        np.testing.assert_array_equal(a, b)
        self.assertEqual(hashes, repeated)
        self.assertNotEqual(hashes[0], hashes[1])
        self.assertTrue(np.all((a >= 0) & (a < 2*np.pi)))


if __name__ == '__main__':
    unittest.main()
