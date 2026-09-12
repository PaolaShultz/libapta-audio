# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_noise_robustness as n


class NoiseTests(unittest.TestCase):
    def test_ratio(self):
        np.testing.assert_allclose(n.amplitudes(4),[.32,.08])
        np.testing.assert_allclose(n.amplitudes(.25),[.08,.32])
        with self.assertRaises(ValueError): n.amplitudes(0)

    def test_noise_replay(self):
        a,h = n.noise(0,0)
        b,k = n.noise(0,0)
        np.testing.assert_array_equal(a,b)
        self.assertEqual(h,k)
        self.assertNotEqual(h,n.noise(0,1)[1])
        self.assertLess(abs(np.mean(a)),1e-15)

    def test_snr_scale(self):
        a,b = np.array([3.,4.]),np.array([1.,2.])
        scale = n.scale_noise(a,b,20)
        self.assertAlmostEqual(np.dot(scale*b,scale*b)/np.dot(a,a),.01)

    def test_paired_source(self):
        _,a=n.observation(0,0,4,'clean')
        _,b=n.observation(0,0,4,'40db')
        _,c=n.observation(0,0,.25,'20db')
        self.assertEqual(a['clean_source_sha256'],b['clean_source_sha256'])
        self.assertEqual(a['noise_uint32_sha256'],c['noise_uint32_sha256'])
        self.assertNotEqual(a['observed_pcm_sha256'],b['observed_pcm_sha256'])
        self.assertAlmostEqual(b['achieved_band_snr_db'],40)
        self.assertAlmostEqual(c['achieved_band_snr_db'],20)

    def test_sorted_amplitude_association(self):
        row=dict(condition='clean',true_frequencies_hz=[500.,501.],true_amplitudes=[.08,.32],oracle_residual_ceiling=1e-10)
        best=dict(shifts_hz=[0.,0.],amplitudes=[.32,.08],score=0.)
        self.assertTrue(n.metrics(best,np.array([501.,500.]),row,dict(score=.1))['screen_pass'])

    def test_gate_boundaries(self):
        row=dict(condition='40db',true_frequencies_hz=[0.,1.],true_amplitudes=[1.,1.],oracle_residual_ceiling=.01)
        best=dict(shifts_hz=[.02,0.],amplitudes=[1.,1.],score=.01)
        self.assertTrue(n.metrics(best,np.array([0.,1.]),row,dict(score=.1))['screen_pass'])
        best['score']=np.nextafter(.01,np.inf)
        self.assertFalse(n.metrics(best,np.array([0.,1.]),row,dict(score=.1))['residual_pass'])

    def test_abstention_and_misleading_residual(self):
        row=dict(condition='20db',true_frequencies_hz=[0.,1.],true_amplitudes=[1.,1.],oracle_residual_ceiling=.1)
        a=n.metrics(None,np.array([0.,1.]),row,dict(score=None))
        best=dict(shifts_hz=[.3,0.],amplitudes=[1.,1.],score=.01)
        b=n.metrics(best,np.array([0.,1.]),row,dict(score=.1))
        result=n.aggregate([dict(**a,best=None),dict(**b,best=best)])
        self.assertEqual(result['count'],2)
        self.assertEqual(result['passes'],0)
        self.assertEqual(result['abstentions'],1)
        self.assertEqual(result['residual_pass_inaccurate'],1)


if __name__ == '__main__': unittest.main()
