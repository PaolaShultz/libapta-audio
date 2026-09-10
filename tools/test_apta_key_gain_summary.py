# SPDX-License-Identifier: Apache-2.0
import copy
import math
from pathlib import Path
import tempfile
import unittest

import apta_key_gain_summary as gain


class GainTests(unittest.TestCase):
    def test_all_fixed_binary_scalings(self):
        values = [0., .03125, 1., 1234.5, 1e7]
        for shift in gain.SHIFTS:
            gain.assert_scaled(values, [math.ldexp(v, 2 * shift) for v in values], shift)

    def test_corrupt_or_wrong_power_scaling_rejected(self):
        for values in ([.25], [2.], [float('nan')], [float('inf')], [-1.], []):
            with self.subTest(values=values), self.assertRaises(ValueError):
                gain.assert_scaled([1.], values, 1)

    def test_float_roundtrip_uses_float_identity(self):
        value = 1.23456789
        rounded = float(format(value, '.9g'))
        gain.assert_scaled([value], [rounded], 0)

    def test_unknown_gain_or_incomplete_rows_rejected(self):
        for shift in (2, -1, True, 0.):
            with self.subTest(shift=shift), self.assertRaisesRegex(ValueError, 'unregistered gain'):
                gain.validate_rows([], [], False, shift)
        with self.assertRaisesRegex(ValueError, 'row coverage'):
            gain.validate_rows([], [], False, 0)

    def test_baseline_hash_before_gain_file_access(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path=root/'baseline.json'; path.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'contrast hash mismatch'):
                gain.summarize(root, {'default':path, 'band':path})

    def test_mode_only_and_tonic_changes_are_separate(self):
        base = [dict(kind='pcm_cumulative', window=4, selected_tonic=0, selected_mode=0,
                     confidence=80, stimulus_tonic=0, stimulus_mode=0) for _ in range(3)]
        rows = copy.deepcopy(base)
        rows[0]['selected_mode']=1
        rows[1]['selected_tonic']=7
        result=gain.comparisons(rows,base)
        self.assertEqual(result['pcm_rows'],3)
        self.assertEqual(result['final_rows'],3)
        self.assertEqual(result['changed_final_verdicts'],2)
        self.assertEqual(result['final_mode_only_changes'],1)
        self.assertEqual(result['final_tonic_changes'],1)
        self.assertEqual(result['final_high_confidence_stimulus_mismatches'],2)


if __name__ == '__main__':
    unittest.main()
