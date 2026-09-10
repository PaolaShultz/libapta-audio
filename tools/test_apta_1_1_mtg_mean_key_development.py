# SPDX-License-Identifier: Apache-2.0
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

import apta_1_1_mtg_mean_key_development as probe


def fixture():
    labels=[dict(track=f'track-{i:024x}',key_tonic=t,key_mode=m)
            for i,(t,m) in enumerate((t,m) for t in range(12) for m in ('major','minor') for _ in range(4))]
    results=[dict(track=r['track'],key_tonic=r['key_tonic'],key_mode=r['key_mode'],key_confidence=50) for r in labels]
    return labels,results


def reports(mutator):
    labels,results=fixture();changed=copy.deepcopy(results);mutator(changed)
    return probe.base.score_rows(labels,results),probe.base.score_rows(labels,changed)


class TransferTests(unittest.TestCase):
    def test_disjoint_deterministic_selection_and_transport_exclusion(self):
        rows=[]
        for index,name in enumerate(probe.base.KEY_NAMES):
            for n in range(49 if index<7 else 48):
                token=f'{index}-{n}'
                rows.append(probe.base.Candidate(token,name,index//2,'major' if index%2==0 else 'minor',hashlib.md5(token.encode()).hexdigest()))
        old=probe.OLD_SELECT(rows);seal=probe.base.selection_sha256(old)
        with patch.object(probe,'OLD_SEAL',seal):
            chosen=probe.choose(rows,[])
            self.assertEqual(chosen,probe.choose(list(reversed(rows)),[]))
            excluded={r.source_id for part in old.values() for r in part}
            self.assertFalse(excluded & {r.source_id for r in chosen})
            self.assertEqual(len(chosen),96)
            replacement=probe.choose(rows,[chosen[0].transport_md5])
            self.assertNotIn(chosen[0],replacement)
        with self.assertRaises(probe.ERROR):probe.choose(rows,[])

    def test_mode_regression_veto_despite_net_improvement(self):
        labels,r=fixture();base=copy.deepcopy(r);cand=copy.deepcopy(r)
        for x in base:
            if x['key_mode']=='major':x['key_mode']='minor'
        cand[4]['key_tonic']=7
        result=probe.compare(probe.base.score_rows(labels,base),probe.base.score_rows(labels,cand))
        self.assertTrue(result['gates']['fixes_exceed_breaks'])
        self.assertFalse(result['gates']['modes_preserved'])

    def test_confidence_75_is_inclusive(self):
        b,c=reports(lambda rows:rows[0].update(key_mode='minor',key_confidence=75))
        result=probe.compare(b,c)
        self.assertEqual(result['new_high_confidence_errors'],1)
        self.assertFalse(result['development_gates_passed'])

    def test_absolute_gate_and_missing_denominator(self):
        b,c=reports(lambda rows:[r.update(key_tonic=(r['key_tonic']+1)%12) for r in rows[:29]])
        result=probe.compare(b,c)
        self.assertFalse(result['gates']['total_at_least_70_percent'])
        c['tracks'].pop()
        with self.assertRaises(probe.ERROR):probe.compare(b,c)

    def test_label_drift_rejected(self):
        b,c=reports(lambda rows:None)
        c['tracks'][0]['expected_tonic']=7
        with self.assertRaises(probe.ERROR):probe.compare(b,c)

    def test_success_does_not_grant_holdout(self):
        labels,r=fixture();wrong=copy.deepcopy(r);wrong[0]['key_mode']='minor'
        result=probe.compare(probe.base.score_rows(labels,wrong),probe.base.score_rows(labels,r))
        self.assertTrue(result['development_gates_passed'])
        self.assertFalse(result['holdout_eligible'])
        self.assertFalse(result['acceptance_claim'])

    def test_pcm_fingerprint_ignores_container_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            a=Path(temp)/'a.wav';b=Path(temp)/'b.wav'
            with wave.open(str(a),'wb') as w:
                w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(b'\x01\x00'*100)
            data=a.read_bytes();b.write_bytes(data+b'JUNK\x04\x00\x00\x00abcd')
            self.assertNotEqual(probe.fingerprint(a)['wav_sha256'],probe.fingerprint(b)['wav_sha256'])
            self.assertEqual(probe.fingerprint(a)['pcm_sha256'],probe.fingerprint(b)['pcm_sha256'])

    def test_output_no_overwrite_and_transport_restored(self):
        original=probe.base.FORMAT
        with self.assertRaises(RuntimeError):
            with probe.transport([]):
                self.assertEqual(probe.base.FORMAT,probe.FORMAT)
                raise RuntimeError('test')
        self.assertEqual(probe.base.FORMAT,original)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'out.json';probe.write_new(p,{})
            with self.assertRaises(FileExistsError):probe.write_new(p,{'changed':True})
            self.assertEqual(probe.read(p),{})


if __name__=='__main__':unittest.main()
