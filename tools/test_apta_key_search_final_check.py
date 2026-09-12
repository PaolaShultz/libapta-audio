# SPDX-License-Identifier: Apache-2.0
import unittest
import numpy as np
import apta_key_search_final_check as f


class FinalCheckTests(unittest.TestCase):
    def test_new_seed_domains_and_pairing(self):
        _,a=f.observation(0,0,4,'clean');_,b=f.observation(0,0,4,'40db')
        _,old=f.n.observation(0,0,4,'40db')
        self.assertEqual(a['clean_source_sha256'],b['clean_source_sha256'])
        self.assertEqual(a['noise_uint32_sha256'],b['noise_uint32_sha256'])
        self.assertNotEqual(old['phase_sha256'],b['phase_sha256'])
        self.assertNotEqual(old['noise_uint32_sha256'],b['noise_uint32_sha256'])
        self.assertAlmostEqual(b['achieved_band_snr_db'],40.)

    def test_budget_cannot_pass(self):
        row=dict(condition='clean',true_frequencies_hz=[500.,501.],true_amplitudes=[.2,.2],oracle_residual_ceiling=1e-10)
        result=dict(status='budget_exhausted',best=dict(shifts_hz=[0.,0.],amplitudes=[.2,.2],score=0.))
        a=f.assess(result,np.array([500.,501.]),row,dict(score=.1))
        self.assertTrue(a['accuracy_pass']);self.assertFalse(a['screen_pass'])
        result['status']='poll_resolved'
        self.assertTrue(f.assess(result,np.array([500.,501.]),row,dict(score=.1))['screen_pass'])

    def test_no_candidate(self):
        a=f.assess(dict(status='no_valid_grid',best=None),np.array([500.,501.]),{},dict(score=None))
        self.assertFalse(a['screen_pass']);self.assertTrue(a['abstained'])


if __name__=='__main__':unittest.main()
