#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Experimental E2: joint nonnegative attribution, no production dependency."""
import argparse
import json
import wave
import numpy as np
from scipy.optimize import nnls
import apta_key_pcm_candidate as e

RIDGE = 1e-3
TYPES = ((1,), (1,2,3,4), (2,3,4))
# Explicit arrays plus conservative allowance for solver copies/workspace.
NUMERIC_BOUND = e.NUMERIC_BOUND + 12*480*180*8


def match(frequencies, target):
    distances = np.abs(1200*np.log2(frequencies/target))
    index = int(np.argmin(distances))
    return index if distances[index] <= 20 else None


def model(frequencies, amplitudes):
    candidates=np.unique((frequencies[:,None]/np.arange(1,5)).ravel())
    ranked=[]
    for f in candidates[(candidates>=65)&(candidates<=1047)]:
        score=0.
        for h in range(1,5):
            index=match(frequencies,h*f)
            if index is not None:score+=amplitudes[index]/h
        ranked.append((float(f),float(score)))
    kept=[]
    for f,score in sorted(ranked,key=lambda v:(-v[1],v[0])):
        if all(abs(1200*np.log2(f/other))>=20 for other in kept):kept.append(f)
        if len(kept)==60:break
    kept.sort()
    absent={};locations=[]
    for f in kept:
        row=[]
        for h in range(1,5):
            index=match(frequencies,f*h)
            if index is None:
                key=int(np.floor(60*np.log2(f*h/65)+.5))
                if key not in absent:absent[key]=len(frequencies)+len(absent)
                index=absent[key]
            row.append(index)
        locations.append(row)
    matrix=np.zeros((len(frequencies)+len(absent),len(kept)*3))
    for j,row in enumerate(locations):
        for kind,partials in enumerate(TYPES):
            for h in partials:matrix[row[h-1],3*j+kind]+=1/h
    norms=np.linalg.norm(matrix,axis=0)
    if len(norms):matrix/=norms
    return np.array(kept),matrix,norms


def optimality(matrix,target,coefficients):
    gradient=matrix.T@(matrix@coefficients-target)
    active=coefficients>1e-10
    projected=np.where(active,np.abs(gradient),np.maximum(-gradient,0))
    return float(np.max(projected,initial=0)/max(1,float(np.max(np.abs(matrix.T@target),initial=0))))


def solve(matrix,target):
    n=matrix.shape[1]
    augmented=np.vstack((matrix,np.sqrt(RIDGE)*np.eye(n)))
    rhs=np.concatenate((target,np.zeros(n)))
    coefficients,_=nnls(augmented,rhs,maxiter=30*n)
    objective=float(np.sum((augmented@coefficients-rhs)**2))
    kkt=optimality(augmented,rhs,coefficients)
    e.c.require(np.isfinite(coefficients).all() and (coefficients>=0).all() and
                objective <= float(rhs@rhs)+1e-10 and kkt<=1e-8,'NNLS numerical gate')
    return coefficients,objective,kkt


def attribute(frequencies, amplitudes):
    f=np.asarray(frequencies,dtype=float);a=np.asarray(amplitudes,dtype=float)
    e.c.require(f.ndim==1 and f.shape==a.shape and len(f)<=60 and np.isfinite(f).all()
                and np.isfinite(a).all() and (f>0).all() and (a>=0).all(),'invalid peaks')
    order=np.argsort(f,kind='stable');f=f[order];a=a[order]
    if not len(f) or not np.any(a):
        return np.zeros(12),dict(status='silence',candidates=0,kkt=0.,objective=0.)
    a=a/np.linalg.norm(a)
    kept,matrix,norms=model(f,a)
    if not len(kept):
        return np.zeros(12),dict(status='no_candidates',candidates=0,kkt=0.,objective=1.)
    target=np.zeros(matrix.shape[0]);target[:len(a)]=a
    try:
        coeff,objective,kkt=solve(matrix,target)
    except (RuntimeError,ValueError) as error:
        return np.zeros(12),dict(status='solver_failed',candidates=len(kept),reason=type(error).__name__)
    physical=(coeff/norms).reshape(-1,3).sum(axis=1)
    return e.chroma(kept,physical),dict(status='ready',candidates=len(kept),kkt=kkt,objective=objective,
        residual=float(np.sum((matrix@coeff-target)**2)),frequencies_hz=kept.tolist(),
        physical_amplitudes=physical.tolist(),coefficients=coeff.tolist(),matrix_shape=list(matrix.shape))


def extract(pcm):
    f,a=e.peaks(pcm)
    chroma,diagnostic=attribute(f,a)
    return chroma,e.chroma(f,a),dict(peak_count=len(f),**diagnostic)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experimental-e2',action='store_true',required=True)
    p.add_argument('--wav',required=True);p.add_argument('--probe',required=True)
    args=p.parse_args();total=np.zeros(12);count=0;failed=False
    with wave.open(args.wav,'rb') as stream:
        trailing=stream.getnframes()%e.RATE
        for pcm in e.wav_windows(stream):
            a,_,d=extract(pcm);total+=a;count+=1
            failed=failed or d['status']=='solver_failed'
    result=(dict(available=False,reason='solver_failed') if failed else
            e.c.query_probe(args.probe,[(total,max(1,count))])[0])
    print(json.dumps(dict(experimental='E2',result=result,windows=count,trailing_samples=trailing,
                         numeric_bound_bytes=NUMERIC_BOUND,confidence_calibrated=False,acceptance_claim=False),allow_nan=False))


if __name__=='__main__':main()
