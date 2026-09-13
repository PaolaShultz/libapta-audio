#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reconstruct/hash/check frozen N1 numerical cases and prove the kernel delta."""
import argparse
import ctypes as ct
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import numpy as np
import scipy
from scipy.optimize import lsq_linear
import apta_key_joint_pcm_screen as screen
import apta_key_joint_n1 as n1

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/'evidence/1.1/repro/key-joint-n1-20260913'


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def upstream_kernel(output):
    vendor=ROOT/'tools/experimental/nnls_n1'
    for name in ('nnls.h','blaslapack_declarations.h','upstream_nnls.c'):
        shutil.copyfile(vendor/name,output/name)
    blas=next((Path(scipy.__file__).resolve().parent.parent/'scipy.libs').glob('libscipy_openblas*.so'))
    lib=output/'upstream.so'
    command=['cc','-std=c99','-shared','-fPIC','-O2',str(output/'upstream_nnls.c'),str(blas),'-lm','-o',str(lib)]
    subprocess.run(command,check=True)
    fn=ct.CDLL(str(lib)).__nnls
    fn.argtypes=[ct.c_int,ct.c_int]+[ct.c_void_p]*6+[ct.c_int64,ct.POINTER(ct.c_double),ct.POINTER(ct.c_int64)]
    fn.restype=None
    def solve(A,b):
        a=np.array(A,order='F',copy=True);y=b.copy();m,n=a.shape
        x=np.zeros(n);w=np.zeros(n);zz=np.zeros(m);indices=np.zeros(n,dtype=np.int32)
        r=ct.c_double();info=ct.c_int64()
        fn(m,n,*[v.ctypes.data for v in (a,y,x,w,zz,indices)],30*n,ct.byref(r),ct.byref(info))
        assert info.value==1
        return x,r.value
    return solve,dict(command=command,source_sha256=digest(vendor/'upstream_nnls.c'),artifact_sha256=digest(lib),blas_sha256=digest(blas))


def metrics(A,b,x):
    g=A.T@(A@x-b);wide=A.astype(np.longdouble).T@(A.astype(np.longdouble)@x-b)
    projected=np.where(x>1e-10,abs(g),np.maximum(-g,0));worst=int(np.argmax(projected))
    return dict(objective=float(np.sum((A@x-b)**2)),residual_norm=float(np.linalg.norm(A@x-b)),
        kkt=n1.optimality(A,b,x),gradient=g.tolist(),max_extended_gradient_delta=float(np.max(abs(g-wide))),
        finite=bool(np.isfinite(x).all()),minimum_coefficient=float(np.min(x)),worst_index=worst,
        worst_coefficient=float(x[worst]),worst_gradient=float(g[worst]))


def run(output):
    assert np.__version__=='2.5.2' and scipy.__version__=='1.18.1'
    assert os.environ.get('OPENBLAS_NUM_THREADS')=='1'
    output.mkdir(parents=True,exist_ok=False)
    original,build=upstream_kernel(output)
    old=json.loads((ROOT/'evidence/1.1/key-joint-pcm-e2-20260912.json').read_text())
    for name,expected in old['source_sha256'].items():assert digest(ROOT/'tools'/name)==expected
    rows=[]
    for row in old['rows']:
        for i,w in enumerate(row['windows']):
            if w['status']!='solver_failed':continue
            pcm=screen.window(row['fixture_tonic'],row['mode'],row['family'],i)
            pcm_sha=hashlib.sha256(pcm.tobytes()).hexdigest();assert pcm_sha==row['pcm_sha256'][i]
            name=f"{row['family']}-{row['fixture_tonic']}-{row['mode']}-{i}"
            d=np.load(CASES/(name+'.npz'))
            f,a=n1.e.peaks(pcm);raw_norm=float(np.linalg.norm(a));a/=raw_norm
            kept,A,norms=n1.model(f,a);b=np.r_[a,np.zeros(len(A)-len(a))];n=A.shape[1]
            B=np.vstack((A,np.sqrt(n1.RIDGE)*np.eye(n)));y=np.r_[b,np.zeros(n)]
            for key,value in dict(pcm=pcm,frequencies=f,amplitudes=a,kept=kept,matrix=A,norms=norms,target=b,augmented=B,rhs=y).items():
                np.testing.assert_array_equal(d[key],value)
            check=case(B,y,original)
            np.testing.assert_array_equal(check.pop('_old_x'),d['coefficients'])
            gradient=A.T@(A@np.array(check['original_coefficients'])-b)+n1.RIDGE*np.array(check['original_coefficients'])
            gram=(A.T@A+n1.RIDGE*np.eye(n))@np.array(check['original_coefficients'])-A.T@b
            check.update(identity=dict(family=row['family'],fixture_tonic=row['fixture_tonic'],expected_tonic=row['tonic'],mode=row['mode'],window=i),
                pcm_sha256=pcm_sha,array_archive_sha256=digest(CASES/(name+'.npz')),raw_amplitude_l2=raw_norm,
                target_l2=float(np.linalg.norm(b)),column_norm_error=float(np.max(abs(np.linalg.norm(A,axis=0)-1))),
                matrix_shape=list(A.shape),augmented_shape=list(B.shape),max_gram_gradient_delta=float(np.max(abs(gradient-gram))))
            rows.append(check)
    d=np.load(CASES/'reduced.npz');reduced=case(d['augmented'],d['rhs'],original);reduced.pop('_old_x')
    reduced.update(shape=list(d['augmented'].shape),array_archive_sha256=digest(CASES/'reduced.npz'),
                   reduction='deterministic reverse column/row deletion preserving KKT failure; not globally minimal')
    report=dict(format='apta-n1-numerical-cause-1',python=platform.python_version(),platform=platform.platform(),
        numpy=np.__version__,scipy=scipy.__version__,OPENBLAS_NUM_THREADS=os.environ['OPENBLAS_NUM_THREADS'],
        numpy_config=np.show_config(mode='dicts'),scipy_config=scipy.show_config(mode='dicts'),
        original_build=build,corrected_kernel_sha256=digest(os.environ['APTA_NNLS_N1_LIBRARY']),
        rows=rows,reduced=reduced,objective='||Ax-b||^2 + 0.001||x||^2, x>=0',acceptance_claim=False)
    (output/'report.json').write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print(json.dumps([dict(identity=r['identity'],old_kkt=r['original']['kkt'],n1_kkt=r['corrected']['kkt']) for r in rows]))


def case(A,b,original):
    before=A.copy();target=b.copy();x,r=screen.j.nnls(A,b,maxiter=30*A.shape[1]);cx,cr=original(A,b)
    np.testing.assert_array_equal(x,cx);assert r==cr
    corrected,norm=n1.nnls(A,b,maxiter=30*A.shape[1])
    ref=lsq_linear(A,b,bounds=(0,np.inf),method='bvls',tol=1e-12,max_iter=30*A.shape[1])
    old=metrics(A,b,x);new=metrics(A,b,corrected);reference=metrics(A,b,ref.x)
    assert old['kkt']>1e-8 and new['kkt']<=1e-8 and reference['kkt']<=1e-8
    assert new['objective']<=old['objective'] and abs(new['residual_norm']-norm)<1e-13
    np.testing.assert_allclose(corrected,ref.x,atol=2e-10,rtol=2e-10)
    np.testing.assert_array_equal(A,before);np.testing.assert_array_equal(b,target)
    return dict(original=old,corrected=new,reference_bvls=reference,original_reported_rnorm=r,
        corrected_reported_rnorm=norm,original_coefficients=x.tolist(),corrected_coefficients=corrected.tolist(),
        reference_coefficients=ref.x.tolist(),upstream_compiled_matches_wheel=True,inputs_unchanged=True,_old_x=x)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path)
    run(p.parse_args().output_dir.resolve())
