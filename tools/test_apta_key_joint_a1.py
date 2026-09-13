# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_joint_a1 as a1


class A1Tests(unittest.TestCase):
    def test_linear_mass_and_octave_folding(self):
        c=a1.amplitude_chroma([220.,440.,330.],[1.,.5,.25])
        self.assertAlmostEqual(c[9],1.5/1.75)
        self.assertAlmostEqual(c[4],.25/1.75)
        self.assertAlmostEqual(c.sum(),1.)

    def test_preserves_solver_and_gain_order_invariance(self):
        f=np.array([211.,317.,422.,634.,844.,951.]);a=np.array([.3,.2,.15,.2,.075,.05])
        c,d=a1.attribute(f,a);_,nd=a1.n1.attribute(f,a)
        self.assertEqual(d,nd);self.assertEqual(d['status'],'ready')
        other,od=a1.attribute(f[::-1],a[::-1]*.3)
        np.testing.assert_allclose(c,other,atol=1e-12)
        self.assertFalse(a1.attribute([],[])[0].any())
        self.assertEqual(a1.attribute([9000],[1])[1]['status'],'no_candidates')
        with self.assertRaises(ValueError):a1.attribute([200],[-1])


if __name__=='__main__':unittest.main()
