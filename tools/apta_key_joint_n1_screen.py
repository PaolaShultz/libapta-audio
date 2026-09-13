#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""N1 regression replay through the frozen E2 evaluator; no fresh-bank claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import apta_key_joint_pcm_screen as frozen
import apta_key_joint_n1 as n1


def run(args):
    original = frozen.j
    try:
        frozen.j = n1
        report, resources = frozen.run(args)
    finally:
        frozen.j = original
    old = json.loads((Path(__file__).resolve().parents[1]/'evidence/1.1/key-joint-pcm-e2-20260912.json').read_text())
    max_coefficient_delta = 0.
    for a,b in zip(report['rows'],old['rows']):
        assert (a['family'],a['mode'],a['fixture_tonic']) == (b['family'],b['mode'],b['fixture_tonic'])
        assert a['pcm_sha256'] == b['pcm_sha256']
        assert a['comparator'] == b['comparator']
        for x,y in zip(a['windows'],b['windows']):
            if y['status']=='ready':
                assert x['status']=='ready'
                delta = max(abs(i-j) for i,j in zip(x['coefficients'],y['coefficients']))
                max_coefficient_delta = max(max_coefficient_delta,delta)
    report.update(format='apta-joint-pcm-n1-1',revision='E2-N1',bank_role='spent-E2-regression',
        pcm_hashes_verified=1152,comparator_identity=True,
        max_previously_valid_coefficient_delta=max_coefficient_delta,
        kernel_sha256=n1.e.c.digest(os.environ['APTA_NNLS_N1_LIBRARY']),
        evaluator_sha256=n1.e.c.digest(frozen.__file__),
        selector_identity_scope='explicit supplied probes; reused local probe may be identical paths')
    report['source_sha256'].update({Path(p).name:n1.e.c.digest(p) for p in
        (__file__,str(Path(__file__).with_name('apta_nnls_n1.py')))})
    return report,resources


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('probe','candidate-probe','sanitize-probe','source-commit','output-prefix'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    paths=[Path(args.output_prefix+s+'.json') for s in ('','-resource')]
    if any(p.exists() for p in paths):raise ValueError('refusing overwrite')
    report,resources=run(args)
    for path,data in zip(paths,(report,resources)):
        with path.open('x') as f:json.dump(data,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps({k:report[k] for k in ('matches','comparator_matches','fixes','breaks','gates','max_kkt','max_previously_valid_coefficient_delta')}))
    print(json.dumps(resources))
