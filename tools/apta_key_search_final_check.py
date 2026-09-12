#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""S3 last search checkpoint; unchanged S2, new paired noise evidence."""
import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
import apta_key_quadratic_search as q
import apta_key_noise_robustness as n

r=q.r
require=r.require
SUPPORTS=([349.23,830.41],[622.17,622.87])


def observation(support,phase,ratio,condition):
    require(condition in n.CONDITIONS,'invalid condition')
    hashes=[hashlib.sha256(f'apta-s3-phase-20260912|{support}|{phase}|{j}'.encode('ascii')).hexdigest() for j in range(2)]
    angles=[2*np.pi*(int(h[:16],16)/2**64) for h in hashes]
    amplitudes=n.amplitudes(ratio)
    clean=sum((r.o.c.p.component_wave(dict(frequency_hz=f,amplitude=a),angle)
               for f,a,angle in zip(SUPPORTS[support],amplitudes,angles)),np.zeros(48000))
    clean_vector=n.vector(r.o.c.p.f.average_four(clean,np.float64))
    data=hashlib.shake_256(f'apta-s3-noise-20260912|{support}|{phase}'.encode('ascii')).digest(48000*4)
    raw=(np.frombuffer(data,dtype='<u4').astype(float)+.5)/2**32-.5
    raw-=raw.mean()
    raw_vector=n.vector(r.o.c.p.f.average_four(raw,np.float64))
    scale=0.; achieved=None; scaling_error=0.
    if condition!='clean':
        snr=40. if condition=='40db' else 20.
        scale=n.scale_noise(clean_vector,raw_vector,snr)
        noise_vector=n.vector(r.o.c.p.f.average_four(scale*raw,np.float64))
        actual=float(np.dot(noise_vector,noise_vector)/np.dot(clean_vector,clean_vector))
        scaling_error=abs(actual/10**(-snr/10)-1)
        require(scaling_error<=1e-12,'noise energy gate')
        achieved=float(-10*np.log10(actual))
    mixed=clean+scale*raw
    pcm=r.o.c.p.f.average_four(mixed,np.float32)
    double=r.o.c.p.f.average_four(mixed,np.float64)
    relative=float(np.linalg.norm(pcm.astype(float)-double)/np.linalg.norm(double))
    absolute=float(max(abs(pcm.astype(float)-double)))
    require(relative<=1e-6 and absolute<=1e-6,'rounding gate')
    observed=n.vector(pcm)
    delta=observed-clean_vector
    ceiling=1e-10 if condition=='clean' else float(1.1*np.dot(delta,delta)/np.dot(observed,observed)+1e-10)
    return observed,dict(support=support,phase_index=phase,amplitude_ratio=ratio,condition=condition,
        true_frequencies_hz=SUPPORTS[support],true_amplitudes=amplitudes.tolist(),phase_sha256=hashes,
        clean_source_sha256=hashlib.sha256(clean.tobytes()).hexdigest(),noise_uint32_sha256=hashlib.sha256(data).hexdigest(),
        observed_pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),noise_scale=scale,achieved_band_snr_db=achieved,
        noise_energy_ratio_relative_error=scaling_error,rounding_relative_error=relative,rounding_absolute_error=absolute,
        oracle_residual_ceiling=ceiling)


def assess(result,seeds,provenance,baseline):
    accuracy=n.metrics(result['best'],seeds,provenance,baseline)
    return dict(**{k:v for k,v in accuracy.items() if k!='screen_pass'},accuracy_pass=accuracy['screen_pass'],
                termination_pass=result['status']=='poll_resolved',
                screen_pass=q.s1.eligible(result['status'],accuracy['screen_pass']))


def evaluate(args):
    prior=json.loads(Path(args.s2_evidence).read_text())
    r3=json.loads(Path(args.r3_evidence).read_text())
    require(r.o.c.p.f.c.digest(q.__file__)==prior['tool_sha256'],'S2 tool drift')
    require(r.o.c.p.f.c.digest(n.__file__)==r3['tool_sha256'],'R3 helper drift')
    for name,digest in prior['source_sha256'].items():
        require(r.o.c.p.f.c.digest(Path(__file__).parent/name)==digest,'dependency drift')
    require(r.o.c.p.f.c.digest(args.o1_evidence)==prior['input_sha256']['o1_evidence'],'O1 evidence drift')
    o1=json.loads(Path(args.o1_evidence).read_text())
    require(r.o.evaluate(o1['source_commit'])['rows']==o1['rows'],'O1 replay drift')
    old_quadratics=[v for v in prior['rows'] if v['kind']=='quadratic']
    require(len(old_quadratics)==8,'quadratic count')
    for row in old_quadratics:
        result,_=q.search(q.quad(np.array(row['center']),row['condition']))
        require(result==row['result'],'S2 quadratic replay drift')
    rows,traces,fits=[],[],[]
    for support in range(2):
        for ratio in (1.,4.,.25):
            for phase in range(2):
                for condition in n.CONDITIONS:
                    observed,provenance=observation(support,phase,ratio,condition)
                    seeds=np.array(SUPPORTS[support])+[-.31,.27]
                    objective=lambda shift:r.fit(observed,seeds+shift)
                    baseline=r.fit(observed,seeds)
                    oracle=r.fit(observed,SUPPORTS[support])
                    old,old_calls=n.s.search(objective)
                    old_metrics=n.metrics(old,seeds,provenance,baseline)
                    result,trace=q.search(objective)
                    fits.extend([baseline,oracle]+old_calls+trace['calls'])
                    metrics=assess(result,seeds,provenance,baseline)
                    rows.append(dict(**provenance,baseline=baseline,oracle=oracle,old_result=old,old_metrics=old_metrics,
                        result=result,best=result['best'],**metrics,
                        same_gate_fix=metrics['screen_pass'] and not old_metrics['screen_pass'],
                        same_gate_break=not metrics['screen_pass'] and old_metrics['screen_pass'],
                        evaluations=result['evaluations']))
                    traces.append(dict(row=len(rows)-1,**trace))
    require(len(rows)==36,'row count')
    totals=[dict(condition=condition,**n.aggregate([v for v in rows if v['condition']==condition]),
                termination_failures=sum(not v['termination_pass'] for v in rows if v['condition']==condition),
                accuracy_passes=sum(v['accuracy_pass'] for v in rows if v['condition']==condition)) for condition in n.CONDITIONS]
    valid=[v for v in fits if v['score'] is not None]
    summary=dict(format='apta-search-final-check-s3-1',source_commit=args.source_commit,
        baseline_commit='13b779ab1f492f4b7e765983cf1399ee8ad07ae8',tool_sha256=r.o.c.p.f.c.digest(__file__),
        source_sha256=dict(prior['source_sha256'],**{Path(q.__file__).name:prior['tool_sha256'],Path(n.__file__).name:r3['tool_sha256']}),
        input_sha256={name:r.o.c.p.f.c.digest(getattr(args,name)) for name in ('s2_evidence','r3_evidence','o1_evidence')},numpy=np.__version__,
        original_s2_quadratics_identical=8,original_o1_rows_identical=24,
        decision='final-search-checkpoint-passed-only' if all(v['screen_pass'] for v in rows) else 'final-search-checkpoint-rejected',
        passes=sum(v['screen_pass'] for v in rows),count=36,totals=totals,
        termination_counts=dict(Counter(v['result']['status'] for v in rows)),fixes=sum(v['same_gate_fix'] for v in rows),
        breaks=sum(v['same_gate_break'] for v in rows),max_evaluations=max(v['evaluations'] for v in rows),
        max_analytic_column_error=max(v['max_column_error'] for v in fits),max_prediction_error=max(v['prediction_error'] for v in valid),
        max_storage_bytes=max(v['storage_bytes'] for v in fits),instrument_gates_pass=True,acceptance_claim=False,
        corpus_access=False,candidate_retained=False,production_cpu_ram_state_delta=0,rows=rows)
    return summary,dict(traces=traces)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('s2-evidence','r3-evidence','o1-evidence','source-commit','output-prefix'):parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    require(len(args.source_commit)==40 and all(v in '0123456789abcdef' for v in args.source_commit),'invalid revision')
    paths=[Path(args.output_prefix+s+'.json') for s in ('','-detail','-resource')]
    require(all(not p.exists() for p in paths),'refusing overwrite')
    started=time.process_time();summary,detail=evaluate(args);elapsed=time.process_time()-started
    require(elapsed<=300,'CPU gate')
    for path,value in zip(paths,(summary,detail,dict(cpu_seconds=elapsed,limit_seconds=300))):
        with path.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')
    print(json.dumps({k:summary[k] for k in ('decision','passes','totals','termination_counts','fixes','breaks','max_evaluations')}))


if __name__=='__main__':main()
