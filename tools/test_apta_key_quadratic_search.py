# SPDX-License-Identifier: Apache-2.0
import itertools
import unittest
import numpy as np
import apta_key_quadratic_search as q


class QuadraticSearchTests(unittest.TestCase):
    def test_exact_local_model(self):
        center=np.array([0.,0.]); target=np.array([.03,-.02]); step=.0625
        objective=q.quad(target,128)
        row=dict(shifts_hz=center.tolist(),**objective(center))
        neighbors=[dict(shifts_hz=(step*np.array(d)).tolist(),**objective(step*np.array(d))) for d in itertools.product((-1,0,1),repeat=2) if d!=(0,0)]
        delta,status=q.direction(row,neighbors,step)
        self.assertEqual(status,'ready')
        np.testing.assert_allclose(delta,target,atol=1e-12)

    def test_model_rejects_flat(self):
        row=dict(shifts_hz=[0,0],score=1.)
        neighbors=[dict(shifts_hz=list(d),score=1.) for d in itertools.product((-1,0,1),repeat=2) if d!=(0,0)]
        self.assertEqual(q.direction(row,neighbors,1)[1],'curvature')
        self.assertEqual(q.direction(row,[],1)[1],'insufficient')

    def test_budget_reserves_cycle(self):
        result,trace=q.search(q.quad(np.array([.013,-.027]),2),budget=104)
        self.assertEqual(result['status'],'budget_exhausted')
        self.assertEqual(len(trace['calls']),81)

    def test_actual_descent_and_schedule(self):
        result,trace=q.search(q.quad(np.array([.013,-.027]),128))
        self.assertEqual(result['status'],'poll_resolved')
        self.assertLess(result['best']['score'],1e-8)
        for a,b in zip(trace['cycles'],trace['cycles'][1:]):
            self.assertEqual(b['step'],a['step'] if a['improved'] else a['step']/2)
        self.assertTrue(all(c['best_candidate']['score']<c['center']['score'] for c in trace['cycles'] if c['improved']))

    def test_flat_bounds_invalid(self):
        result,trace=q.search(lambda x:dict(score=1.))
        self.assertEqual(result['best']['shifts_hz'],[-.5,-.5])
        self.assertTrue(all(all(-.5<=v<=.5 for v in c['shifts_hz']) for c in trace['calls']))
        self.assertEqual(q.search(lambda x:dict(score=None))[0]['status'],'no_valid_grid')
        with self.assertRaises(ValueError):q.search(lambda x:dict(score=np.nan))


if __name__=='__main__':unittest.main()
