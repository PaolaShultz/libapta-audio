# SPDX-License-Identifier: Apache-2.0
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from scipy.optimize import nnls, lsq_linear
import apta_key_joint_n1 as n1
import apta_key_joint_pcm as e2
import test_apta_key_joint_pcm as inherited

CASES=Path(__file__).resolve().parents[1]/'evidence/1.1/repro/key-joint-n1-20260913'


class N1InheritedTests(inherited.JointPcmTests):
    def setUp(self):
        self.binding=patch.object(inherited,'j',n1);self.binding.start()
    def tearDown(self):self.binding.stop()


class N1NumericalTests(unittest.TestCase):
    def check_solution(self,A,b,x):
        g=np.asarray(A,dtype=np.longdouble).T@(np.asarray(A,dtype=np.longdouble)@x-b)
        residual=float(np.max(np.where(x>1e-10,abs(g),np.maximum(-g,0)),initial=0))
        self.assertLessEqual(residual,1e-8)
        self.assertTrue(np.isfinite(x).all() and (x>=0).all())
        reference=lsq_linear(A,b,bounds=(0,np.inf),method='bvls',tol=1e-12,max_iter=30*A.shape[1])
        self.assertLessEqual(n1.optimality(A,b,reference.x),1e-8)
        np.testing.assert_allclose(x,reference.x,atol=2e-10,rtol=2e-10)

    def test_recorded_and_reduced_failures(self):
        for file in sorted(CASES.glob('*.npz')):
            with self.subTest(file=file.name):
                d=np.load(file);A=d['augmented'];b=d['rhs'];before=A.copy();target=b.copy()
                old,_=nnls(A,b,maxiter=30*A.shape[1])
                self.assertGreater(e2.optimality(A,b,old),1e-8)
                x,r=n1.nnls(A,b,maxiter=30*A.shape[1]);self.check_solution(A,b,x)
                self.assertAlmostEqual(r,np.linalg.norm(A@x-b),places=13)
                np.testing.assert_array_equal(A,before);np.testing.assert_array_equal(b,target)

    def test_seeded_strictly_convex_and_boundary_cases(self):
        rng=np.random.default_rng(20260913)
        for n in (1,3,12,60,180):
            for sparse in (False,True):
                A=rng.normal(size=(n,n))
                if sparse:A=np.where(abs(A)>.8,A,0.)
                A=np.vstack((A,np.sqrt(n1.RIDGE)*np.eye(n)));b=np.r_[rng.normal(size=n),np.zeros(n)]
                x,_=n1.nnls(A,b,maxiter=30*n);self.check_solution(A,b,x)
        A=np.eye(3)
        np.testing.assert_array_equal(n1.nnls(A,-np.ones(3),maxiter=90)[0],np.zeros(3))
        np.testing.assert_array_equal(n1.nnls(A,np.zeros(3),maxiter=90)[0],np.zeros(3))
        with self.assertRaises(RuntimeError):n1.nnls(A,np.ones(3),maxiter=1)
        for a,b in ((A,[1]),(A,[1,2,np.nan]),(np.zeros((1,181)),[1])):
            with self.assertRaises(ValueError):n1.nnls(a,b,maxiter=90)


if __name__=='__main__':unittest.main()
