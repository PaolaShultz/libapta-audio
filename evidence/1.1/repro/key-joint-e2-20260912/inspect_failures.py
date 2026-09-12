import sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/home/daniel/apta-joint-e2-20260912/source/tools')
import apta_key_joint_pcm_screen as screen
j=screen.j
out=Path('/mnt/d/AI/LIBAPTA/libapta-audio-dsp-20260904/build/key-joint-e2-20260912')
report=json.loads((out/'result.json').read_text());findings=[]
for row in report['rows']:
    for index,w in enumerate(row['windows']):
        if w['status']!='solver_failed':continue
        pcm=screen.window(row['fixture_tonic'],row['mode'],row['family'],index)
        f,a=j.e.peaks(pcm);a/=np.linalg.norm(a)
        kept,matrix,norms=j.model(f,a)
        target=np.zeros(matrix.shape[0]);target[:len(a)]=a
        n=matrix.shape[1];aug=np.vstack((matrix,np.sqrt(j.RIDGE)*np.eye(n)))
        rhs=np.concatenate((target,np.zeros(n)))
        coeff,res=j.nnls(aug,rhs,maxiter=30*n)
        objective=float(np.sum((aug@coeff-rhs)**2));kkt=j.optimality(aug,rhs,coeff)
        findings.append(dict(family=row['family'],tonic=row['tonic'],mode=row['mode'],window=index,
            minimum_coefficient=float(np.min(coeff)),negative_count=int(sum(coeff<0)),
            objective=objective,zero_objective=float(rhs@rhs),kkt=kkt,
            finite=bool(np.isfinite(coeff).all()),fixed_solver_arguments=True,no_clipping_or_retry=True))
with (out/'failure-inspection.json').open('x') as stream:json.dump(findings,stream,indent=2,sort_keys=True)
print(json.dumps(findings,indent=2))
