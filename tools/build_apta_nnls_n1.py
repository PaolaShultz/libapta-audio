#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build the explicit Linux/SciPy-1.18.1-wheel experimental N1 kernel."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import scipy


def build(output):
    if scipy.__version__ != '1.18.1' or sys.platform != 'linux':
        raise RuntimeError('N1 build requires Linux and SciPy 1.18.1 wheel')
    source = Path(__file__).resolve().parent / 'experimental/nnls_n1'
    libraries = list((Path(scipy.__file__).resolve().parent.parent / 'scipy.libs').glob('libscipy_openblas*.so'))
    if len(libraries) != 1:
        raise RuntimeError('expected one bundled LP64 SciPy OpenBLAS library')
    output.mkdir(parents=True, exist_ok=False)
    for name in ('upstream_nnls.c', 'nnls.h', 'blaslapack_declarations.h'):
        shutil.copyfile(source / name, output / name)
    shutil.copyfile(output / 'upstream_nnls.c', output / 'nnls_n1.c')
    subprocess.run(['patch', str(output / 'nnls_n1.c'), str(source / 'restore-rejected-column.patch')], check=True)
    header = output / 'nnls.h'
    header.write_text(header.read_text().replace('CBLAS_INT* restrict indices, const int64_t maxiter',
        'CBLAS_INT* restrict indices, double* restrict saved, const int64_t maxiter'))
    artifact = output / 'libapta_nnls_n1.so'
    command = ['cc', '-std=c99', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra', '-Werror',
        str(output / 'nnls_n1.c'), str(libraries[0]), '-lm', '-o', str(artifact)]
    subprocess.run(command, check=True)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = dict(revision='E2-N1', scipy=scipy.__version__, command=command,
        source_sha256={p.name:digest(p) for p in sorted(source.iterdir()) if p.is_file()},
        blas_sha256=digest(libraries[0]), artifact_sha256=digest(artifact))
    (output / 'build.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    print(artifact.resolve())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    build(parser.parse_args().output.resolve())
