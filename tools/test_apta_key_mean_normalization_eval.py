# SPDX-License-Identifier: Apache-2.0
import copy
import math
import unittest
import apta_key_mean_normalization_eval as candidate


def finals():
    return [dict(kind='pcm_cumulative',window=4,condition=c,stimulus_mode=m,stimulus_tonic=t,
                 selected_mode=m,selected_tonic=t,confidence=50)
            for c in range(3) for m in range(2) for t in range(12)]


class CandidateTests(unittest.TestCase):
    def test_mean_formula_and_scale_invariance(self):
        for raw in ([1.]*36,[0.]*35+[1.],[float(i+1) for i in range(36)]):
            reference=candidate.expected_compression(raw)
            for shift in (-8,-4,0,2):
                self.assertEqual(reference,candidate.expected_compression([math.ldexp(v,shift) for v in raw]))
        self.assertEqual(candidate.expected_compression([1.]*36),[math.log(2.)]*36)
        self.assertEqual(candidate.expected_compression([0.]*35+[1.])[-1],math.log(37.))

    def test_minor_regression_veto_even_with_net_fixes(self):
        base=finals(); rows=copy.deepcopy(base)
        for r in base[:12]: r['selected_mode']=1
        rows[12]['selected_tonic']=7
        metrics=candidate.final_metrics(rows,base)
        self.assertEqual((metrics['fixes'],metrics['breaks']),(12,1))
        self.assertTrue(metrics['gates']['fixes_exceed_breaks'])
        self.assertFalse(metrics['gates']['minor_preserved_each_condition'])

    def test_new_confident_error_veto(self):
        base=finals(); rows=copy.deepcopy(base)
        rows[0].update(selected_mode=1,confidence=75)
        self.assertEqual(candidate.final_metrics(rows,base)['new_high_confidence_mismatches'],1)

    def test_no_gain_rescue_for_confidence_or_score_drift(self):
        rows=finals(); changed=copy.deepcopy(rows); changed[0]['confidence']+=1
        self.assertNotEqual(candidate.gain_identity(rows),candidate.gain_identity(changed))

    def test_gates_pass_for_improvement_without_breaks(self):
        rows=finals(); base=copy.deepcopy(rows)
        for r in base[:4]: r['selected_mode']=1
        self.assertTrue(all(candidate.final_metrics(rows,base)['gates'].values()))

    def test_incomplete_or_invalid_vectors_rejected(self):
        with self.assertRaises(ValueError): candidate.final_metrics([],[])
        for raw in ([0.]*36,[float('nan')]*36,[-1.]*36,[1.]*35):
            with self.assertRaises(ValueError): candidate.expected_compression(raw)


if __name__=='__main__': unittest.main()
