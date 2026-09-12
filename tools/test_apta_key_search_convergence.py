# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_search_convergence as c


class ConvergenceTests(unittest.TestCase):
    def test_budget_is_not_convergence(self):
        result,trace=c.search(lambda x:dict(score=float(np.sum((x-[.173,-.287])**2))),budget=89)
        self.assertEqual(result['status'],'budget_exhausted')
        self.assertEqual(result['evaluations'],89)
        self.assertFalse(c.eligible(result['status'],True))

    def test_step_and_polls(self):
        result,trace=c.search(c.quadratic([.173,-.287],1))
        self.assertEqual(result['status'],'poll_resolved')
        for previous,current in zip(trace['polls'],trace['polls'][1:]):
            self.assertEqual(current['step'],previous['step'] if previous['improved'] else previous['step']/2)
        self.assertFalse(trace['polls'][-1]['improved'])
        self.assertLessEqual(trace['polls'][-1]['step'],c.MIN_STEP)

    def test_flat_ties(self):
        result,trace=c.search(lambda x:dict(score=1.))
        self.assertEqual(result['best']['shifts_hz'],[-.5,-.5])
        self.assertEqual(result['status'],'poll_resolved')
        self.assertFalse(any(p['improved'] for p in trace['polls']))
        self.assertFalse(c.eligible(result['status'],False))

    def test_all_invalid(self):
        result,_=c.search(lambda x:dict(score=None))
        self.assertEqual(result['status'],'no_valid_grid')
        self.assertEqual(result['evaluations'],81)

    def test_bounds(self):
        result,trace=c.search(lambda x:dict(score=float(np.sum((x-[1.,-1.])**2))))
        self.assertEqual(result['best']['shifts_hz'],[.5,-.5])
        self.assertTrue(all(all(-.5<=v<=.5 for v in p['shifts_hz']) for p in trace['calls']))

    def test_known_quadratic(self):
        q=c.quadratic([.173,-.287],256)
        self.assertEqual(q(np.array([.173,-.287]))['score'],0.)
        self.assertGreater(q(np.array([.174,-.287]))['score'],0.)

    def test_invalid(self):
        with self.assertRaises(ValueError): c.search(lambda x:dict(score=np.nan))
        with self.assertRaises(ValueError): c.search(lambda x:dict(score=0.),budget=80)


if __name__=='__main__': unittest.main()
