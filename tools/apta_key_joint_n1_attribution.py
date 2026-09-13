#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Evaluation-only N1 mechanism traces. Supplied notes never enter the detector."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import apta_key_joint_n1 as j
import apta_key_joint_pcm_screen as bank


def trace(report, probe):
    rows=[];requests=[]
    old=json.loads((Path(__file__).resolve().parents[1]/'evidence/1.1/key-joint-pcm-e2-20260912.json').read_text())
    failed={(r['family'],r['mode'],r['fixture_tonic']) for r in old['rows']
            if any(w['status']=='solver_failed' for w in r['windows'])}
    selected=[r for r in report['rows'] if r['family']=='unequal' or r['break'] or
              (r['family'],r['mode'],r['fixture_tonic']) in failed]
    for r in selected:
        totals={k:np.zeros(12) for k in ('detector','known_support','ideal_squared','ideal_equal')}
        windows=[]
        for i in range(8):
            pcm=bank.window(r['fixture_tonic'],r['mode'],r['family'],i)
            assert hashlib.sha256(pcm.tobytes()).hexdigest() == r['pcm_sha256'][i]
            offset=(0,5,0,7,5,0,7,0)[i];root=47+r['fixture_tonic']+offset
            third=4 if r['mode']==0 or offset==7 else 3
            notes=np.array([root,root+third,root+7]+([root-12] if i in (2,5) else []))
            detune=(.17 if i%2==0 else -.27) if r['family']=='detuned' else 0.
            truth=440*2**((notes-69+detune)/12)
            weights=np.array([1,.5,.25,.75][:len(notes)] if r['family']=='unequal' else [1.]*len(notes));weights/=weights.sum()
            f,a=j.e.peaks(pcm);a=a/np.linalg.norm(a);kept,A,norms=j.model(f,a)
            b=np.r_[a,np.zeros(len(A)-len(a))];x,obj,kkt=j.solve(A,b)
            distance=abs(1200*np.log2(kept[:,None]/truth[None,:]))
            support=np.any(distance<=20,axis=1);cols=np.repeat(support,3)
            sx,so,sk=j.solve(A[:,cols],b)
            physical=(x/norms).reshape(-1,3).sum(axis=1)
            known=(sx/norms[cols]).reshape(-1,3).sum(axis=1)
            chromas=dict(detector=j.e.chroma(kept,physical),known_support=j.e.chroma(kept[support],known),
                ideal_squared=j.e.chroma(truth,weights),ideal_equal=j.e.chroma(truth,np.ones(len(truth))))
            for k,c in chromas.items():totals[k]+=c
            peak_coverage=[]
            for note,hz in zip(notes,truth):
                peak_coverage.append(dict(midi=int(note),frequency_hz=float(hz),candidate_cents=float(np.min(abs(1200*np.log2(kept/hz)))),
                    partials=[dict(h=h,peak_index=j.match(f,h*hz)) for h in range(1,5)]))
            windows.append(dict(index=i,peaks_hz=f.tolist(),normalized_peak_amplitudes=a.tolist(),true_notes=peak_coverage,
                objective=obj,kkt=kkt,known_support_objective=so,known_support_kkt=sk,
                chroma={k:v.tolist() for k,v in chromas.items()},
                assignments=[dict(frequency_hz=float(hz),midi=int(np.floor(69+12*np.log2(hz/440)+.5)),
                    true_support=bool(support[k]),physical_amplitude=float(physical[k]),
                    normalized_coefficients=x[3*k:3*k+3].tolist()) for k,hz in enumerate(kept)]))
        row=dict(family=r['family'],mode=r['mode'],fixture_tonic=r['fixture_tonic'],tonic=r['tonic'],
            result=r['result'],comparator=r['comparator'],windows=windows,chroma={k:v.tolist() for k,v in totals.items()})
        requests.extend((c,8) for c in totals.values());rows.append(row)
    answers=j.e.c.query_probe(probe,requests)
    for i,row in enumerate(rows):
        row['diagnostic_selections']=dict(zip(('detector','known_support','ideal_squared','ideal_equal'),answers[4*i:4*i+4]))
        assert row['diagnostic_selections']['detector']==row['result']
    return dict(format='apta-n1-attribution-trace-1',evaluation_only=True,acceptance_claim=False,rows=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',required=True);p.add_argument('--probe',required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    if Path(a.output).exists():raise ValueError('refusing overwrite')
    result=trace(json.loads(Path(a.report).read_text()),a.probe)
    with Path(a.output).open('x') as f:json.dump(result,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    for r in result['rows']:
        print(r['family'],r['fixture_tonic'],r['mode'],{k:(v.get('tonic'),v.get('mode')) for k,v in r['diagnostic_selections'].items()},
            'uncovered',[(w['index'],n['midi'],n['candidate_cents']) for w in r['windows'] for n in w['true_notes'] if n['candidate_cents']>20])
