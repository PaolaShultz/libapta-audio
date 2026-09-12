#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""E2 fresh complete pipeline screen; metadata restricted to evaluation."""
import argparse
import hashlib
import json
import resource
import time
from pathlib import Path
import numpy as np
import scipy
import apta_key_joint_pcm as j

FAMILIES=('pure','full','missing','detuned','unequal','steep')
BASELINE='66a7c5f134b1bc31f81c0a953ef2ee0dec876b11'


def window(tonic,mode,family,index):
    offset=(0,5,0,7,5,0,7,0)[index];root=47+tonic+offset
    third=4 if mode==0 or offset==7 else 3
    notes=[root,root+third,root+7]+([root-12] if index in (2,5) else [])
    partials=(1,) if family=='pure' else (2,3,4) if family=='missing' else (1,2,3,4)
    weights=np.array([1,.5,.25,.75][:len(notes)] if family=='unequal' else [1.]*len(notes))
    weights/=weights.sum()
    detune=(.17 if index%2==0 else -.27) if family=='detuned' else 0.
    exponent=1.7 if family=='steep' else 1.
    t=np.arange(j.e.RATE)/j.e.RATE;pcm=np.zeros(j.e.RATE)
    for n,note in enumerate(notes):
        for h in partials:
            seed=f'apta-e2-20260912|{tonic}|{mode}|{family}|{index}|{n}|{h}'
            phase=int.from_bytes(hashlib.sha256(seed.encode('ascii')).digest()[:8],'big')/2**64*2*np.pi
            frequency=440*2**((note-69+detune)/12)*h
            pcm+=(.12*weights[n]/h**exponent)*np.sin(2*np.pi*frequency*t+phase)
    return pcm.astype(np.float32)


def gates(rows):
    j.e.c.require(len(rows)==144,'incomplete E2 bank')
    groups=[]
    for family in FAMILIES:
        for mode in (0,1,'all'):
            selected=[r for r in rows if r['family']==family and (mode=='all' or r['mode']==mode)]
            j.e.c.require(len(selected)==(24 if mode=='all' else 12),'group size')
            groups.append(dict(family=family,mode=mode,count=len(selected),matches=sum(r['match'] for r in selected)))
    return dict(accuracy=all(g['matches'] >= (18 if g['mode']=='all' else 9) for g in groups),
        no_breaks=not any(r['break'] for r in rows),
        no_new_high_confidence_errors=not any(r['new_high_confidence_error'] for r in rows),
        confidence_safety=sum(r['high_confidence_error'] for r in rows)<=.05*len(rows),
        availability=sum(not r['result'].get('available',False) for r in rows)<=.05*len(rows),
        numerical=not any(w['status']=='solver_failed' for r in rows for w in r['windows']),
        numeric_memory=j.NUMERIC_BOUND<=16*1024**2),groups


def run(args):
    rows=[];requests=[];cpu=0.
    for family in FAMILIES:
        for mode in range(2):
            for tonic in range(12):
                total=np.zeros(12);direct=np.zeros(12);diagnostics=[];hashes=[];failed=False
                for index in range(8):
                    pcm=window(tonic,mode,family,index);hashes.append(hashlib.sha256(pcm.tobytes()).hexdigest())
                    started=time.process_time();a,b,d=j.extract(pcm);cpu+=time.process_time()-started
                    total+=a;direct+=b;diagnostics.append(d);failed=failed or d['status']=='solver_failed'
                if failed:total[:]=0
                requests.extend([(total,8),(direct,8)])
                rows.append(dict(family=family,mode=mode,tonic=(tonic+11)%12,fixture_tonic=tonic,
                                 pcm_sha256=hashes,chroma=total.tolist(),direct_chroma=direct.tolist(),windows=diagnostics))
    started=time.process_time();before=resource.getrusage(resource.RUSAGE_CHILDREN)
    answers=j.e.c.query_probe(args.probe,requests)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu+=time.process_time()-started+after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    for probe in (args.candidate_probe,args.sanitize_probe):
        j.e.c.require(answers==j.e.c.query_probe(probe,requests),'native selector identity')
    for row,result,base in zip(rows,answers[::2],answers[1::2]):
        expected=(row['tonic'],row['mode'])
        matched=j.e.c.matches(result,expected);base_match=j.e.c.matches(base,expected)
        high=not matched and result.get('confidence',0)>=75
        base_high=not base_match and base.get('confidence',0)>=75
        row.update(result=result,comparator=base,match=matched,comparator_match=base_match,
                   fix=matched and not base_match,**{'break':not matched and base_match},
                   high_confidence_error=high,new_high_confidence_error=high and not base_high)
    checks,groups=gates(rows)
    summary=dict(format='apta-joint-pcm-e2-1',source_commit=args.source_commit,baseline_commit=BASELINE,
        source_sha256={Path(p).name:j.e.c.digest(p) for p in (__file__,j.__file__,j.e.__file__,j.e.c.__file__)},
        probe_sha256={k:j.e.c.digest(getattr(args,k)) for k in ('probe','candidate_probe','sanitize_probe')},
        numpy=np.__version__,scipy=scipy.__version__,rows=rows,groups=groups,gates=checks,
        decision='synthetic-pipeline-passed-only' if all(checks.values()) and cpu<=120 else 'pipeline-rejected',
        matches=sum(r['match'] for r in rows),comparator_matches=sum(r['comparator_match'] for r in rows),
        fixes=sum(r['fix'] for r in rows),breaks=sum(r['break'] for r in rows),
        high_confidence_errors=sum(r['high_confidence_error'] for r in rows),
        new_high_confidence_errors=sum(r['new_high_confidence_error'] for r in rows),
        max_kkt=max(w.get('kkt',0) for r in rows for w in r['windows']),
        numeric_bound_bytes=j.NUMERIC_BOUND,selector_identity=True,production_delta=0,
        acceptance_claim=False,corpus_access=False,confidence_calibrated=False)
    return summary,dict(pipeline_cpu_seconds=cpu,cpu_limit_seconds=120,cpu_gate=cpu<=120,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('probe','candidate-probe','sanitize-probe','source-commit','output-prefix'):
        p.add_argument('--'+name,required=True)
    args=p.parse_args()
    j.e.c.require(len(args.source_commit)==40 and all(c in '0123456789abcdef' for c in args.source_commit),'invalid SHA')
    paths=[Path(args.output_prefix+s+'.json') for s in ('','-resource')]
    j.e.c.require(all(not p.exists() for p in paths),'refusing overwrite')
    summary,resources=run(args)
    for path,data in zip(paths,(summary,resources)):
        with path.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(data,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','source_sha256','probe_sha256')}))
    print(json.dumps(resources))


if __name__=='__main__':main()
