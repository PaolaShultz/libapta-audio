#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Frozen E1 end-to-end synthetic screen; fixture truth never enters detector."""
import argparse
import hashlib
import json
import resource
import time
from pathlib import Path
import numpy as np
import apta_key_pcm_candidate as e

CONDITIONS=('pure','full','missing','detuned')
BASELINE='3245ecfdb87a4fe07b4ecc7c68e601088aa4d8a5'


def window(tonic,mode,condition,index):
    offset=(0,7,5,0,5,7,7,0)[index]
    root=48+tonic+offset
    third=4 if mode==0 or offset==7 else 3
    notes=[root,root+third,root+7]+([root-12] if index%2 else [])
    partials=(1,) if condition=='pure' else (2,3,4) if condition=='missing' else (1,2,3,4)
    detune=(.23 if index%2==0 else -.19) if condition=='detuned' else 0.
    t=np.arange(e.RATE)/e.RATE;pcm=np.zeros(e.RATE)
    for j,note in enumerate(notes):
        for h in partials:
            seed=f'apta-e1-20260912|{tonic}|{mode}|{condition}|{index}|{j}|{h}'
            phase=int.from_bytes(hashlib.sha256(seed.encode('ascii')).digest()[:8],'big')/2**64*2*np.pi
            frequency=440*2**((note-69+detune)/12)*h
            pcm+=(.12/(len(notes)*h))*np.sin(2*np.pi*frequency*t+phase)
    return pcm.astype(np.float32)


def gates(rows,cpu):
    groups=[]
    for condition in CONDITIONS:
        for mode in (0,1,'all'):
            selected=[r for r in rows if r['condition']==condition and (mode=='all' or r['mode']==mode)]
            groups.append(dict(condition=condition,mode=mode,count=len(selected),
                               matches=sum(r['match'] for r in selected)))
    return dict(accuracy=all(g['matches'] >= (18 if g['mode']=='all' else 9) for g in groups),
                no_breaks=not any(r['break'] for r in rows),
                no_new_high_confidence_errors=not any(r['new_high_confidence_error'] for r in rows),
                confidence_safety=sum(r['high_confidence_error'] for r in rows)<=.05*len(rows),
                cpu=cpu<=60,numeric_memory=e.NUMERIC_BOUND<=8*1024**2),groups


def run(args):
    rows=[];requests=[];cpu=0.
    for condition in CONDITIONS:
        for mode in range(2):
            for tonic in range(12):
                total=np.zeros(12);direct=np.zeros(12);diagnostics=[];hashes=[]
                for index in range(8):
                    pcm=window(tonic,mode,condition,index)
                    hashes.append(hashlib.sha256(pcm.tobytes()).hexdigest())
                    started=time.process_time();a,b,d=e.extract(pcm);cpu+=time.process_time()-started
                    total+=a;direct+=b;diagnostics.append(d)
                requests.extend([(total,8),(direct,8)])
                rows.append(dict(condition=condition,mode=mode,tonic=tonic,pcm_sha256=hashes,
                                 chroma=total.tolist(),direct_chroma=direct.tolist(),windows=diagnostics))
    started=time.process_time()
    child_before=resource.getrusage(resource.RUSAGE_CHILDREN)
    answers=e.c.query_probe(args.probe,requests)
    child_after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu+=time.process_time()-started+child_after.ru_utime+child_after.ru_stime-child_before.ru_utime-child_before.ru_stime
    for probe in (args.candidate_probe,args.sanitize_probe):
        e.c.require(answers==e.c.query_probe(probe,requests),'native selector identity')
    for row,result,base in zip(rows,answers[::2],answers[1::2]):
        expected=(row['tonic'],row['mode'])
        match=e.c.matches(result,expected);base_match=e.c.matches(base,expected)
        high=not match and result.get('confidence',0)>=75
        base_high=not base_match and base.get('confidence',0)>=75
        row.update(result=result,comparator=base,match=match,comparator_match=base_match,
                   fix=match and not base_match,**{'break':not match and base_match},
                   high_confidence_error=high,new_high_confidence_error=high and not base_high)
    decisions,groups=gates(rows,cpu)
    summary=dict(format='apta-pcm-key-e1-1',source_commit=args.source_commit,baseline_commit=BASELINE,
                 source_sha256={Path(p).name:e.c.digest(p) for p in (__file__,e.__file__,e.c.__file__)},
                 probe_sha256={k:e.c.digest(getattr(args,k)) for k in ('probe','candidate_probe','sanitize_probe')},
                 numpy=np.__version__,rows=rows,groups=groups,
                 gates={k:v for k,v in decisions.items() if k!='cpu'},
                 decision='synthetic-pipeline-passed-only' if all(decisions.values()) else 'pipeline-rejected',
                 fixes=sum(r['fix'] for r in rows),breaks=sum(r['break'] for r in rows),
                 high_confidence_errors=sum(r['high_confidence_error'] for r in rows),
                 new_high_confidence_errors=sum(r['new_high_confidence_error'] for r in rows),
                 numeric_bound_bytes=e.NUMERIC_BOUND,selector_identity=True,production_delta=0,
                 acceptance_claim=False,corpus_access=False,confidence_calibrated=False)
    resources=dict(pipeline_cpu_seconds=cpu,cpu_limit_seconds=60,cpu_gate=decisions['cpu'],
                   process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return summary,resources


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('probe','candidate-probe','sanitize-probe','source-commit','output-prefix'):
        p.add_argument('--'+name,required=True)
    args=p.parse_args()
    e.c.require(len(args.source_commit)==40 and all(c in '0123456789abcdef' for c in args.source_commit),'invalid SHA')
    paths=[Path(args.output_prefix+s+'.json') for s in ('','-resource')]
    e.c.require(all(not p.exists() for p in paths),'refusing overwrite')
    summary,resources=run(args)
    for path,data in zip(paths,(summary,resources)):
        with path.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(data,stream,sort_keys=True,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','source_sha256','probe_sha256')}))
    print(json.dumps(resources))


if __name__=='__main__':main()
