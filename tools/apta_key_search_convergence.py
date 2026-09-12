#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""S1 finite poll resolution is distinct from exhausted budget and accuracy."""
import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
import apta_key_independent_shift as s

r = s.r
require = r.require
BUDGET = 2049
MIN_STEP = 2**-24


def eligible(status, accurate):
    return status == 'poll_resolved' and bool(accurate)


def search(evaluate, budget=BUDGET):
    require(isinstance(budget,int) and budget >= 81 and budget <= BUDGET, 'invalid budget')
    calls, polls = [], []

    def sample(point):
        fit = evaluate(np.array(point,dtype=float))
        require(fit['score'] is None or (np.isfinite(fit['score']) and fit['score'] >= 0), 'invalid objective')
        row = dict(shifts_hz=list(map(float,point)), **fit)
        calls.append(row)
        return row

    def best_of(values):
        valid = [v for v in values if v['score'] is not None]
        return min(valid,key=lambda v:(v['score'],v['shifts_hz'])) if valid else None

    for point in itertools.product(np.linspace(-.5,.5,9),repeat=2): sample(point)
    best = best_of(calls)
    step = .0625
    status = 'no_valid_grid' if best is None else 'budget_exhausted'
    directions = [v for v in itertools.product((-1,0,1),repeat=2) if v != (0,0)]
    while best is not None and len(calls)+8 <= budget:
        center = best
        neighbors = [sample(np.clip(np.array(center['shifts_hz'])+step*np.array(v),-.5,.5)) for v in directions]
        neighbor = best_of(neighbors)
        improved = neighbor is not None and neighbor['score'] < center['score']
        polls.append(dict(center=center['shifts_hz'],center_score=center['score'],step=step,
                          best_neighbor=neighbor,improved=improved))
        if improved:
            best = neighbor
        elif step <= MIN_STEP:
            status = 'poll_resolved'
            break
        else:
            step *= .5
    require(len(calls) <= budget and (len(calls)-81)%8 == 0, 'poll budget contract')
    return dict(status=status,best=best,evaluations=len(calls),polls=len(polls),final_step=step), dict(calls=calls,polls=polls)


def quadratic(center, condition):
    theta = np.deg2rad(27.)
    rotation = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
    matrix = np.eye(2) if condition == 1 else rotation @ np.diag([1.,condition]) @ rotation.T
    def objective(point):
        difference = point-np.array(center)
        return dict(score=float(difference @ matrix @ difference))
    return objective


def evaluate(args):
    prior = json.loads(Path(args.r1_evidence).read_text())
    r2 = json.loads(Path(args.r2_evidence).read_text())
    require(r.o.c.p.f.c.digest(r.__file__) == prior['tool_sha256'], 'R1 source drift')
    require(r.o.c.p.f.c.digest(s.__file__) == r2['tool_sha256'], 'R2 source drift')
    require(r.o.c.p.f.c.digest(args.r1_evidence) == r2['input_sha256']['r1_evidence'], 'R1 evidence drift')
    require(r.o.c.p.f.c.digest(args.o1_evidence) == prior['o1_evidence_sha256'], 'O1 evidence drift')
    control,_ = r.evaluate(args.o1_evidence,prior['source_commit'])
    require(control['rows'] == prior['rows'], 'R1 control drift')
    quadratics, tones, traces, fits = [], [], [], []
    for center in ([.173,-.287],[-.219,.341]):
        for condition in (1,16,256,4096):
            objective = quadratic(center,condition)
            old,_ = s.search(objective)
            result,trace = search(objective)
            error = float(max(abs(np.array(result['best']['shifts_hz'])-center)))
            old_error = float(max(abs(np.array(old['shifts_hz'])-center)))
            accurate = error <= 1e-4 and result['best']['score'] <= 1e-8
            quadratics.append(dict(center=center,condition=condition,result=result,error=error,accurate=accurate,
                old_result=old,old_error=old_error,old_accurate=old_error <= 1e-4 and old['score'] <= 1e-8,
                screen_pass=eligible(result['status'],accurate)))
            traces.append(dict(kind='quadratic',row=len(quadratics)-1,**trace))
    for support,frequencies in enumerate(([293.27,698.43],[466.21,466.91])):
        for ratio in (4.,.25):
            expected = np.array([.4*ratio/(1+ratio),.4/(1+ratio)])
            for phase in range(2):
                hashes = [hashlib.sha256(f'apta-s1-20260912|{support}|{phase}|{j}'.encode('ascii')).hexdigest() for j in range(2)]
                angles = [2*np.pi*(int(h[:16],16)/2**64) for h in hashes]
                components = [dict(frequency_hz=f,amplitude=a) for f,a in zip(frequencies,expected)]
                pcm,relative,absolute = r.o.c.p.observation(components,angles)
                observed = r.o.c.real_vector(np.fft.rfft(pcm.astype(float)))
                seeds = np.array(frequencies)+[-.29,.33]
                objective = lambda shift:r.fit(observed,seeds+shift)
                old,old_calls = s.search(objective)
                result,trace = search(objective)
                oracle = r.fit(observed,frequencies)
                fits.extend(old_calls+trace['calls']+[oracle])
                oracle_pass = oracle['score'] is not None and oracle['score'] <= 1e-10 and max(abs(np.array(oracle['amplitudes'])-expected)) <= 1e-4
                best = result['best']
                error = amplitude_error = None
                accurate = no_regression = False
                if best:
                    order = np.argsort(seeds+best['shifts_hz'])
                    error = float(max(abs((seeds+best['shifts_hz'])[order]-frequencies)))
                    amplitude_error = float(max(abs(np.array(best['amplitudes'])[order]-expected)))
                    accurate = error <= 1e-4 and amplitude_error <= 1e-4 and best['score'] <= 1e-10
                    no_regression = old is None or best['score'] <= old['score']+1e-12
                old_accurate = False
                if old:
                    order = np.argsort(seeds+old['shifts_hz'])
                    old_accurate = bool(max(abs((seeds+old['shifts_hz'])[order]-frequencies)) <= 1e-4 and
                        max(abs(np.array(old['amplitudes'])[order]-expected)) <= 1e-4 and old['score'] <= 1e-10)
                tones.append(dict(support=support,ratio=ratio,phase=phase,frequencies_hz=frequencies,
                    phase_sha256=hashes,pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),
                    rounding_relative_error=relative,rounding_absolute_error=absolute,result=result,
                    error_hz=error,amplitude_error=amplitude_error,accurate=bool(accurate),old_accurate=old_accurate,
                    old_result=old,oracle=oracle,oracle_pass=bool(oracle_pass),no_regression=bool(no_regression),
                    screen_pass=eligible(result['status'],accurate and oracle_pass and no_regression)))
                traces.append(dict(kind='tone',row=len(tones)-1,**trace))
    all_rows = quadratics+tones
    valid = [v for v in fits if v['score'] is not None]
    summary = dict(format='apta-search-convergence-s1-1',source_commit=args.source_commit,
        baseline_commit='03b5c9f158cf7be94141c4dca4e0e3e3c4ab233d',tool_sha256=r.o.c.p.f.c.digest(__file__),
        source_sha256=dict(prior['source_sha256'],**{Path(r.__file__).name:prior['tool_sha256'],Path(s.__file__).name:r2['tool_sha256']}),
        input_sha256={name:r.o.c.p.f.c.digest(getattr(args,name)) for name in ('r1_evidence','r2_evidence','o1_evidence')},
        numpy=np.__version__,original_r1_rows_identical=48,original_o1_rows_identical=24,
        decision='finite-termination-screen-passed-only' if all(v['screen_pass'] for v in all_rows) else 'finite-termination-screen-rejected',
        quadratic_passes=sum(v['screen_pass'] for v in quadratics),tone_passes=sum(v['screen_pass'] for v in tones),
        termination_counts=dict(Counter(v['result']['status'] for v in all_rows)),
        accurate_but_budget_exhausted=sum(v['accurate'] and v['result']['status']=='budget_exhausted' for v in all_rows),
        resolved_but_inaccurate=sum(not v['accurate'] and v['result']['status']=='poll_resolved' for v in all_rows),
        accuracy_fixes=sum(v['accurate'] and not v['old_accurate'] for v in all_rows),
        accuracy_breaks=sum(not v['accurate'] and v['old_accurate'] for v in all_rows),
        max_analytic_column_error=max(v['max_column_error'] for v in fits),
        max_prediction_error=max(v['prediction_error'] for v in valid),max_storage_bytes=max(v['storage_bytes'] for v in fits),
        instrument_gates_pass=True,acceptance_claim=False,corpus_access=False,candidate_retained=False,
        production_cpu_ram_state_delta=0,quadratics=quadratics,tones=tones)
    return summary,dict(traces=traces)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('r1-evidence','r2-evidence','o1-evidence','source-commit','output-prefix'): parser.add_argument('--'+name,required=True)
    args = parser.parse_args()
    require(len(args.source_commit)==40 and all(v in '0123456789abcdef' for v in args.source_commit),'invalid revision')
    paths = [Path(args.output_prefix+suffix+'.json') for suffix in ('','-detail','-resource')]
    require(all(not v.exists() for v in paths),'refusing overwrite')
    started = time.process_time()
    summary,detail = evaluate(args)
    elapsed = time.process_time()-started
    require(elapsed <= 300,'CPU gate')
    for path,value in zip(paths,(summary,detail,dict(cpu_seconds=elapsed,limit_seconds=300))):
        with path.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
            stream.write('\n')
    print(json.dumps({k:summary[k] for k in ('decision','quadratic_passes','tone_passes','termination_counts','resolved_but_inaccurate','accuracy_fixes','accuracy_breaks')}))


if __name__=='__main__': main()
