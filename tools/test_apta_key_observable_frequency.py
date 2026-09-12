# SPDX-License-Identifier: Apache-2.0
import hashlib
import unittest
import numpy as np
import apta_key_observable_frequency as s


def row(correct, wrong, old_pass=True):
    return dict(**s.decision(correct, wrong, 'known'), c2_discrimination_pass=old_pass,
                c2_screen_pass=old_pass, c2_selected_family='known' if old_pass else 'pure')


class ObservableFrequencyTests(unittest.TestCase):
    def test_no_default_winner(self):
        for correct, wrong in [(None, .8), (.01, None), (None, None)]:
            result = s.decision(correct, wrong, 'known')
            self.assertIsNone(result['selected_family'])
            self.assertIsNone(result['discrimination_pass'])
            self.assertFalse(result['screen_pass'])

    def test_unavailable_not_reconstruction_failure(self):
        result = s.aggregate([row(None, .8), row(.2, None), row(None, None)])
        self.assertEqual(result['count'], 3)
        self.assertEqual(result['abstentions'], 3)
        self.assertEqual(result['both_abstentions'], 1)
        self.assertEqual(result['reconstruction_failures'], 1)
        self.assertEqual(result['reconstruction_unavailable'], 2)
        self.assertEqual(result['measured_rankings'], 0)
        self.assertIsNone(result['min_margin'])

    def test_frozen_gate_boundaries(self):
        self.assertTrue(s.decision(.10, .3, 'known')['screen_pass'])
        self.assertFalse(s.decision(np.nextafter(.10, np.inf), .3, 'known')['screen_pass'])
        self.assertFalse(s.decision(0., 1e-6, 'known')['discrimination_pass'])
        self.assertTrue(s.decision(1e-10, .3, 'known', True)['screen_pass'])
        self.assertFalse(s.decision(1e-9, .3, 'known', True)['screen_pass'])

    def test_reversal_tie_and_family_identity(self):
        self.assertEqual(s.decision(.5, .1, 'pure')['selected_family'], 'known')
        self.assertEqual(s.decision(.1, .5, 'pure')['selected_family'], 'pure')
        self.assertEqual(s.decision(.1, .1, 'pure')['selected_family'], 'tie')

    def test_fix_break_abstention_denominator(self):
        result = s.aggregate([row(.1, .3, False), row(None, .3), row(.2, .3)])
        self.assertEqual(result['ranking_fixes'], 1)
        self.assertEqual(result['ranking_breaks'], 1)
        self.assertEqual(result['combined_fixes'], 1)
        self.assertEqual(result['combined_breaks'], 2)
        self.assertEqual(result['pass_count'], 1)
        self.assertEqual(result['combined_failures'], 2)

    def test_source_integrity(self):
        pcm = np.array([.1, .2], dtype=np.float32)
        prior = dict(source_pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),
                     phase_sha256=['phase'], rounding_relative_error=.01, rounding_max_absolute_error=.001)
        self.assertEqual(s.validate_source(pcm, ['phase'], .01, .001, prior), prior['source_pcm_sha256'])
        with self.assertRaises(ValueError):
            s.validate_source(pcm*2, ['phase'], .01, .001, prior)
        with self.assertRaises(ValueError):
            s.validate_source(pcm, ['changed'], .01, .001, prior)

    def test_invalid_residuals(self):
        for value in (-1, np.inf, np.nan):
            with self.assertRaises(ValueError):
                s.decision(value, .2, 'known')


if __name__ == '__main__':
    unittest.main()
