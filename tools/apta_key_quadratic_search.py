#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""S2: verified local quadratic proposals, bounded finite-poll termination."""
import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
import apta_key_search_convergence as s1

r=s1.r
require=r.require


def direction(center, neighbors, step):
    valid=[v for v in neighbors if v['score'] is not None]
    if len(valid)<5: return None,'insufficient'
    offsets=(np.array([v['shifts_hz'] for v in valid])-center['shifts_hz'])/step
    u,v=offsets.T
    design=np.column_stack([u,v,.5*u*u,u*v,.5*v*v])
    coefficients,_,rank,_=np.linalg.lstsq(design,np.array([v['score']-center['score'] for v in valid]),rcond=r.RCOND)
    if rank!=5 or not np.isfinite(coefficients).all(): return None,'rank'
    hessian=np.array([[coefficients[2],coefficients[3]],[coefficients[3],coefficients[4]]])
    eigen=np.linalg.eigvalsh(hessian)
    if eigen[0]<=r.RCOND*max(abs(eigen)): return None,'curvature'
    displacement=-step*np.linalg.solve(hessian,coefficients[:2])
    require(np.isfinite(displacement).all(),'nonfinite proposal')
    norm=max(abs(displacement))
    if norm>.125: displacement*=.125/norm
    return displacement,'ready'


def search(evaluate,budget=2049):
    require(isinstance(budget,int) and 81<=budget<=2049,'invalid budget')
    calls,cycles=[],[]
    def sample(point):
        value=evaluate(np.asarray(point,dtype=float))
        require(value['score'] is None or (np.isfinite(value['score']) and value['score']>=0),'invalid objective')
        row=dict(shifts_hz=list(map(float,point)),**value)
        calls.append(row)
        return row
    def best_of(values):
        valid=[v for v in values if v['score'] is not None]
        return min(valid,key=lambda v:(v['score'],v['shifts_hz'])) if valid else None
    for point in itertools.product(np.linspace(-.5,.5,9),repeat=2): sample(point)
    best=best_of(calls)
    status='no_valid_grid' if best is None else 'budget_exhausted'
    step=.0625
    directions=[v for v in itertools.product((-1,0,1),repeat=2) if v!=(0,0)]
    while best is not None and len(calls)+24<=budget:
        center=best
        neighbors=[sample(np.clip(np.array(center['shifts_hz'])+step*np.array(v),-.5,.5)) for v in directions]
        displacement,model_status=direction(center,neighbors,step)
        trials=[]
        if displacement is not None:
            for j in range(16):
                trial=sample(np.clip(np.array(center['shifts_hz'])+displacement*2**(-j),-.5,.5))
                trials.append(trial)
                if trial['score'] is not None and trial['score']<center['score']: break
        candidate=best_of(neighbors+trials)
        improved=candidate is not None and candidate['score']<center['score']
        cycles.append(dict(center=center,step=step,model_status=model_status,
            displacement=displacement.tolist() if displacement is not None else None,
            trials=len(trials),improved=improved,best_candidate=candidate))
        if improved: best=candidate
        elif step<=s1.MIN_STEP:
            status='poll_resolved'
            break
        else: step*=.5
    require(len(calls)<=budget,'budget violation')
    return dict(status=status,best=best,evaluations=len(calls),cycles=len(cycles),final_step=step),dict(calls=calls,cycles=cycles)


def quad(center,condition):
    theta=np.deg2rad(19.)
    q=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    matrix=np.eye(2) if condition==1 else q@np.diag([1.,condition])@q.T
    return lambda point:dict(score=float((point-center)@matrix@(point-center)))


def evaluate(args):
    prior=json.loads(Path(args.s1_evidence).read_text())
    require(r.o.c.p.f.c.digest(s1.__file__)==prior['tool_sha256'],'S1 source drift')
    for name,digest in prior['source_sha256'].items():
        require(r.o.c.p.f.c.digest(Path(__file__).parent/name)==digest,'dependency drift')
    require(r.o.c.p.f.c.digest(args.o1_evidence)==prior['input_sha256']['o1_evidence'],'O1 evidence drift')
    o1=json.loads(Path(args.o1_evidence).read_text())
    require(r.o.evaluate(o1['source_commit'])['rows']==o1['rows'],'O1 control drift')
    for row in prior['quadratics']:
        result,_=s1.search(s1.quadratic(row['center'],row['condition']))
        require(result==row['result'],'S1 quadratic replay drift')
    rows,traces,fits=[],[],[]
    for center in ([.137,-.263],[-.317,.229]):
        for condition in (1,64,1024,16384):
            objective=quad(np.array(center),condition)
            old,_=s1.search(objective)
            result,trace=search(objective)
            error=float(max(abs(np.array(result['best']['shifts_hz'])-center)))
            old_error=float(max(abs(np.array(old['best']['shifts_hz'])-center)))
            accurate=error<=1e-4 and result['best']['score']<=1e-8
            old_pass=s1.eligible(old['status'],old_error<=1e-4 and old['best']['score']<=1e-8)
            rows.append(dict(kind='quadratic',center=center,condition=condition,result=result,error=error,
                accurate=accurate,screen_pass=s1.eligible(result['status'],accurate),old_result=old,old_pass=old_pass))
            traces.append(dict(row=len(rows)-1,**trace))
    for support,frequencies in enumerate(([329.37,783.49],[587.13,587.83])):
        for ratio in (4.,.25):
            expected=np.array([.4*ratio/(1+ratio),.4/(1+ratio)])
            for phase in range(2):
                hashes=[hashlib.sha256(f'apta-s2-20260912|{support}|{phase}|{j}'.encode('ascii')).hexdigest() for j in range(2)]
                angles=[2*np.pi*(int(h[:16],16)/2**64) for h in hashes]
                pcm,relative,absolute=r.o.c.p.observation([dict(frequency_hz=f,amplitude=a) for f,a in zip(frequencies,expected)],angles)
                observed=r.o.c.real_vector(np.fft.rfft(pcm.astype(float)))
                seeds=np.array(frequencies)+[-.27,.31]
                objective=lambda shift:r.fit(observed,seeds+shift)
                old,old_trace=s1.search(objective)
                result,trace=search(objective)
                oracle=r.fit(observed,frequencies)
                fits.extend(old_trace['calls']+trace['calls']+[oracle])
                oracle_pass=oracle['score'] is not None and oracle['score']<=1e-10 and max(abs(np.array(oracle['amplitudes'])-expected))<=1e-4
                def assess(value):
                    if value['best'] is None:return False,None,None
                    best=value['best']
                    order=np.argsort(seeds+best['shifts_hz'])
                    error=float(max(abs((seeds+best['shifts_hz'])[order]-frequencies)))
                    amplitude_error=float(max(abs(np.array(best['amplitudes'])[order]-expected)))
                    return error<=1e-4 and amplitude_error<=1e-4 and best['score']<=1e-10,error,amplitude_error
                accurate,error,amplitude_error=assess(result)
                old_accurate,_,_=assess(old)
                no_regression=result['best'] is not None and (old['best'] is None or result['best']['score']<=old['best']['score']+1e-12)
                rows.append(dict(kind='tone',support=support,ratio=ratio,phase=phase,frequencies_hz=frequencies,
                    pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),phase_sha256=hashes,
                    rounding_relative_error=relative,rounding_absolute_error=absolute,result=result,
                    accurate=accurate,error=error,amplitude_error=amplitude_error,old_result=old,
                    old_pass=s1.eligible(old['status'],old_accurate),oracle=oracle,oracle_pass=bool(oracle_pass),
                    no_regression=bool(no_regression),screen_pass=s1.eligible(result['status'],accurate and oracle_pass and no_regression)))
                traces.append(dict(row=len(rows)-1,**trace))
    require(len(rows)==16,'bank size drift')
    valid=[v for v in fits if v['score'] is not None]
    summary=dict(format='apta-quadratic-search-s2-1',source_commit=args.source_commit,
        baseline_commit='f7d0e7018de6fbab4bad85f9a03b01b0a922355f',tool_sha256=r.o.c.p.f.c.digest(__file__),
        source_sha256=dict(prior['source_sha256'],**{Path(s1.__file__).name:prior['tool_sha256']}),
        input_sha256={name:r.o.c.p.f.c.digest(getattr(args,name)) for name in ('s1_evidence','o1_evidence')},
        original_s1_quadratics_identical=8,original_o1_rows_identical=24,numpy=np.__version__,
        decision='finite-quadratic-search-passed-only' if all(v['screen_pass'] for v in rows) else 'finite-quadratic-search-rejected',
        passes=sum(v['screen_pass'] for v in rows),count=16,termination_counts=dict(Counter(v['result']['status'] for v in rows)),
        fixes=sum(v['screen_pass'] and not v['old_pass'] for v in rows),breaks=sum(not v['screen_pass'] and v['old_pass'] for v in rows),
        model_status_counts=dict(Counter(c['model_status'] for t in traces for c in t['cycles'])),
        max_analytic_column_error=max(v['max_column_error'] for v in fits),
        max_prediction_error=max(v['prediction_error'] for v in valid),max_storage_bytes=max(v['storage_bytes'] for v in fits),
        instrument_gates_pass=True,acceptance_claim=False,corpus_access=False,candidate_retained=False,
        production_cpu_ram_state_delta=0,rows=rows)
    return summary,dict(traces=traces)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('s1-evidence','o1-evidence','source-commit','output-prefix'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    require(len(args.source_commit)==40 and all(v in '0123456789abcdef' for v in args.source_commit),'invalid revision')
    paths=[Path(args.output_prefix+s+'.json') for s in ('','-detail','-resource')]
    require(all(not p.exists() for p in paths),'refusing overwrite')
    started=time.process_time()
    summary,detail=evaluate(args)
    elapsed=time.process_time()-started
    require(elapsed<=300,'CPU gate')
    for path,value in zip(paths,(summary,detail,dict(cpu_seconds=elapsed,limit_seconds=300))):
        with path.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
            stream.write('\n')
    print(json.dumps({k:summary[k] for k in ('decision','passes','termination_counts','fixes','breaks')}))


if __name__=='__main__':main()
