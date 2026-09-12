# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_independent_shift as s


class IndependentShiftTests(unittest.TestCase):
    def test_independent_axes(self):
        target = np.array([.17, -.29])
        best, calls = s.search(lambda x: dict(score=float(np.sum((x-target)**2))))
        self.assertLess(max(abs(np.array(best['shifts_hz'])-target)), 1e-6)
        self.assertEqual(len(calls), 273)
        self.assertTrue(all(all(-.5 <= v <= .5 for v in c['shifts_hz']) for c in calls))

    def test_endpoints_ties(self):
        best, _ = s.search(lambda x: dict(score=float(np.sum((x-[-.5,.5])**2))))
        self.assertEqual(best['shifts_hz'], [-.5,.5])
        best, _ = s.search(lambda x: dict(score=1.))
        self.assertEqual(best['shifts_hz'], [-.5,-.5])

    def test_all_invalid(self):
        best, calls = s.search(lambda x: dict(score=None))
        self.assertIsNone(best)
        self.assertEqual(len(calls), 81)

    def test_partial_invalid(self):
        best, _ = s.search(lambda x: dict(score=float(np.sum((x-[.2,.3])**2)) if all(x > 0) else None))
        self.assertLess(max(abs(np.array(best['shifts_hz'])-[.2,.3])), 1e-6)

    def test_permutation_metric(self):
        best = dict(shifts_hz=[0,0], score=0., amplitudes=[.1,.1])
        result = s.recovery_metrics(best, np.array([501.,500.]), [500.,501.], .1, dict(score=.3))
        self.assertTrue(result['screen_pass'])
        self.assertFalse(s.recovery_metrics(None, np.array([1.,2.]), [1.,2.], .1, dict(score=None))['screen_pass'])

    def test_stress_not_recovery(self):
        self.assertTrue(s.amplitude_stress_pass(dict(status='amplitude'), None))
        self.assertTrue(s.amplitude_stress_pass(dict(status='amplitude'), dict(score=.1)))
        self.assertFalse(s.amplitude_stress_pass(dict(status='amplitude'), dict(score=1e-11)))

    def test_source_replay(self):
        a, provenance = s.source(0, 0, .2)
        b, replay = s.source(0, 0, .2)
        np.testing.assert_array_equal(a, b)
        self.assertEqual(provenance, replay)
        self.assertNotEqual(provenance['phase_sha256'][0], provenance['phase_sha256'][1])

    def test_invalid_objective(self):
        for value in (np.nan, -1.):
            with self.assertRaises(ValueError):
                s.search(lambda x: dict(score=value))


if __name__ == '__main__':
    unittest.main()
