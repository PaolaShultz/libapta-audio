# SPDX-License-Identifier: Apache-2.0
import io
import unittest
import wave
import numpy as np
import apta_key_pcm_candidate as e


class PcmCandidateTests(unittest.TestCase):
    def test_silence_and_invalid(self):
        a,b,d=e.extract(np.zeros(e.RATE))
        self.assertFalse(a.any());self.assertFalse(b.any());self.assertEqual(d['selected_count'],0)
        for x in (np.zeros(12),np.full(e.RATE,np.nan),np.full(e.RATE,1.01)):
            with self.assertRaises(ValueError):e.extract(x)

    def test_unknown_peaks_and_gain(self):
        t=np.arange(e.RATE)/e.RATE
        x=.2*np.sin(2*np.pi*397.3*t)+.07*np.sin(2*np.pi*817.2*t)
        f,a=e.peaks(x)
        self.assertTrue(any(abs(v-397.3)<.2 for v in f))
        self.assertTrue(any(abs(v-817.2)<.2 for v in f))
        one=e.extract(x);two=e.extract(x*.25)
        np.testing.assert_allclose(one[0],two[0],atol=1e-12)
        self.assertLessEqual(one[2]['peak_count'],60)
        self.assertLessEqual(one[2]['selected_count'],12)
        self.assertLess(e.NUMERIC_BOUND,8*1024**2)

    def test_attribution_and_objective(self):
        chosen,d=e.attribute([200.,400.,600.,800.],[1.,.5,1/3,.25])
        self.assertEqual(chosen[0],(200.,1.))
        self.assertEqual(d['selected_count'],1)
        self.assertTrue(all(b<=a for a,b in zip(d['residual_energies'],d['residual_energies'][1:])))
        with self.assertRaises(ValueError):e.attribute([200],[-1])

    def test_stream_rate_and_trailing(self):
        def make(rate):
            data=io.BytesIO()
            with wave.open(data,'wb') as w:
                w.setparams((2,2,rate,0,'NONE','not compressed'))
                w.writeframes(np.tile(np.array([100,-100],dtype='<i2'),e.RATE+17).tobytes())
            data.seek(0);return data
        with wave.open(make(e.RATE),'rb') as w:
            rows=list(e.wav_windows(w))
            self.assertEqual(len(rows),1);self.assertFalse(rows[0].any())
            self.assertEqual(w.getnframes()%e.RATE,17)
        with wave.open(make(44100),'rb') as w:
            with self.assertRaises(ValueError):list(e.wav_windows(w))


if __name__=='__main__':unittest.main()
