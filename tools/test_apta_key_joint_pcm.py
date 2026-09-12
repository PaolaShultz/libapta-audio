# SPDX-License-Identifier: Apache-2.0
import unittest
from unittest.mock import patch
import numpy as np
import apta_key_joint_pcm as j


class JointPcmTests(unittest.TestCase):
    def test_silence_invalid_empty_model(self):
        self.assertFalse(j.attribute([],[])[0].any())
        self.assertEqual(j.attribute([9000],[1])[1]['status'],'no_candidates')
        for f,a in (([0],[1]),([100],[float('nan')]),([100],[-1])):
            with self.assertRaises(ValueError):j.attribute(f,a)
        self.assertLess(j.NUMERIC_BOUND,16*1024**2)

    def test_full_missing_models_preserve_absence(self):
        for f,a in (([200,400,600,800],[1,.5,1/3,.25]),([400,600,800],[.5,1/3,.25])):
            c,d=j.attribute(f,a)
            self.assertEqual(d['status'],'ready');self.assertLessEqual(d['kkt'],1e-8)
            self.assertAlmostEqual(float(c.sum()),1.)
        kept,matrix,norms=j.model(np.array([400.,600.,800.]),np.array([.5,1/3,.25]))
        index=int(np.argmin(abs(kept-200)))
        self.assertFalse(np.array_equal(matrix[:,3*index+1],matrix[:,3*index+2]))

    def test_overlap_order_and_gain(self):
        f=np.array([211.,317.,422.,634.,844.,951.]);a=np.array([.3,.2,.15,.2,.075,.05])
        c,d=j.attribute(f,a);other,od=j.attribute(f[::-1],a[::-1]*.25)
        np.testing.assert_allclose(c,other,atol=1e-10)
        self.assertEqual(d['status'],'ready');self.assertLessEqual(d['kkt'],1e-8)

    def test_kkt_detects_wrong_solution_and_solver_failure(self):
        self.assertGreater(j.optimality(np.eye(2),np.ones(2),np.zeros(2)),.9)
        x,obj,kkt=j.solve(np.eye(2),np.array([1.,-1.]))
        np.testing.assert_allclose(x,[1/(1+j.RIDGE),0],atol=1e-12)
        with patch.object(j,'nnls',side_effect=RuntimeError('budget')):
            c,d=j.attribute([200.],[1.])
            self.assertFalse(c.any());self.assertEqual(d['status'],'solver_failed')


if __name__=='__main__':unittest.main()
