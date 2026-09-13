#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fixed A1/N1 evaluations on spent E2 or separately hash-frozen fresh fixtures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import time
import numpy as np
import scipy
import apta_key_joint_pcm_screen as old
import apta_key_joint_a1_fixtures as fresh
import apta_key_joint_n1 as n1
import apta_key_joint_a1 as a1

ROOT=Path(__file__).resolve().parents[1]


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pcm_hash(pcm):return hashlib.sha256(pcm.tobytes()).hexdigest()


def freeze():
    old_report=json.loads((ROOT/'evidence/1.1/key-joint-pcm-e2-20260912.json').read_text())
    old_hashes={h for r in old_report['rows'] for h in r['pcm_sha256']}
    rows=[]
    for family in old.FAMILIES:
        for mode in range(2):
            for tonic in range(12):
                hashes=[pcm_hash(fresh.window(tonic,mode,family,i)) for i in range(8)]
                assert not set(hashes)&old_hashes
                rows.append(dict(family=family,mode=mode,fixture_tonic=tonic,tonic=tonic,pcm_sha256=hashes))
    return dict(format='apta-a1-fresh-manifest-1',generator_sha256=digest(fresh.__file__),
        numpy=np.__version__,phase_domain='apta-a1-fresh-20260913',disjoint_from_e2=True,rows=rows)


def run(args):
    if os.environ.get('OPENBLAS_NUM_THREADS')!='1':raise ValueError('requires OPENBLAS_NUM_THREADS=1')
    module=n1 if args.instrument=='N1' else a1
    manifest=json.loads(Path(args.manifest).read_text())
    generator=old.window if args.bank=='regression' else fresh.window
    if args.bank=='fresh':assert manifest['generator_sha256']==digest(fresh.__file__)
    rows=[];requests=[];cpu=0.
    for identity in manifest['rows']:
        family=identity['family'];mode=identity['mode'];tonic=identity['fixture_tonic']
        total=np.zeros(12);direct=np.zeros(12);windows=[];hashes=[];failed=False
        for i in range(8):
            pcm=generator(tonic,mode,family,i);hashes.append(pcm_hash(pcm))
            assert hashes[-1]==identity['pcm_sha256'][i]
            start=time.process_time();c,d,w=module.extract(pcm);cpu+=time.process_time()-start
            total+=c;direct+=d;windows.append(w);failed|=w['status']=='solver_failed'
        if failed:total[:]=0
        requests.extend(((total,8),(direct,8)))
        rows.append(dict(family=family,mode=mode,fixture_tonic=tonic,tonic=identity['tonic'],
            pcm_sha256=hashes,chroma=total.tolist(),direct_chroma=direct.tolist(),windows=windows))
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.process_time()
    answers=n1.e.c.query_probe(args.probe,requests)
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu+=time.process_time()-start+after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime
    for row,result,base in zip(rows,answers[::2],answers[1::2]):
        expected=(row['tonic'],row['mode']);matched=n1.e.c.matches(result,expected);bm=n1.e.c.matches(base,expected)
        high=not matched and result.get('confidence',0)>=75
        row.update(result=result,comparator=base,match=matched,comparator_match=bm,fix=matched and not bm,
            **{'break':not matched and bm},high_confidence_error=high,
            new_high_confidence_error=high and not (not bm and base.get('confidence',0)>=75))
    checks,groups=old.gates(rows)
    checks['numeric_memory']=module.NUMERIC_BOUND<=16*1024**2
    relative=None
    if args.n1_report:
        reference=json.loads(Path(args.n1_report).read_text());fixes=breaks=0
        for row,base in zip(rows,reference['rows']):
            assert row['pcm_sha256']==base['pcm_sha256'] and row['comparator']==base['comparator']
            row['n1_result']=base['result'];row['n1_match']=base['match']
            row['fix_vs_n1']=row['match'] and not base['match']
            row['break_vs_n1']=not row['match'] and base['match']
            fixes+=row['fix_vs_n1'];breaks+=row['break_vs_n1']
        relative=dict(fixes=fixes,breaks=breaks);checks['no_breaks_vs_n1']=breaks==0
    paths=[__file__,fresh.__file__,old.__file__,old.j.__file__,n1.__file__,a1.__file__,n1.e.__file__,n1.e.c.__file__,Path(__file__).with_name('apta_nnls_n1.py')]
    report=dict(format='apta-joint-a1-screen-1',revision='E2-'+args.instrument,bank_role=args.bank,
        source_commit=args.source_commit,source_sha256={Path(p).name:digest(p) for p in paths},
        manifest_sha256=digest(args.manifest),probe_sha256=digest(args.probe),kernel_sha256=digest(os.environ['APTA_NNLS_N1_LIBRARY']),
        numpy=np.__version__,scipy=scipy.__version__,rows=rows,groups=groups,gates=checks,relative_to_n1=relative,
        matches=sum(r['match'] for r in rows),comparator_matches=sum(r['comparator_match'] for r in rows),
        fixes=sum(r['fix'] for r in rows),breaks=sum(r['break'] for r in rows),
        high_confidence_errors=sum(r['high_confidence_error'] for r in rows),
        max_kkt=max(w.get('kkt',0) for r in rows for w in r['windows']),numeric_bound_bytes=module.NUMERIC_BOUND,
        decision='synthetic-only-pass' if all(checks.values()) and cpu<=120 else 'rejected',
        acceptance_claim=False,production_delta=0,confidence_calibrated=False,corpus_access=False)
    return report,dict(pipeline_cpu_seconds=cpu,cpu_gate=cpu<=120,cpu_limit_seconds=120,
        process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def write(path,data):
    with Path(path).open('x') as f:json.dump(data,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze-manifest')
    p.add_argument('--instrument',choices=('N1','A1'));p.add_argument('--bank',choices=('regression','fresh'))
    for name in ('manifest','probe','source-commit','output-prefix','n1-report'):p.add_argument('--'+name)
    args=p.parse_args()
    if args.freeze_manifest:
        if Path(args.freeze_manifest).exists():raise ValueError('refusing overwrite')
        write(args.freeze_manifest,freeze())
    else:
        if not all((args.instrument,args.bank,args.manifest,args.probe,args.source_commit,args.output_prefix)):
            p.error('all evaluation arguments required')
        if len(args.source_commit)!=40 or any(c not in '0123456789abcdef' for c in args.source_commit):p.error('full SHA required')
        if args.instrument=='A1' and not args.n1_report:p.error('A1 requires N1 comparison report')
        paths=[args.output_prefix+s+'.json' for s in ('','-resource')]
        if any(Path(p).exists() for p in paths):raise ValueError('refusing overwrite')
        report,resources=run(args)
        for path,data in zip(paths,(report,resources)):write(path,data)
        print(json.dumps({k:report[k] for k in ('revision','bank_role','matches','comparator_matches','fixes','breaks','relative_to_n1','gates')}))
        print(json.dumps(resources))
