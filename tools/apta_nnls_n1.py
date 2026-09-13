# SPDX-License-Identifier: Apache-2.0
"""Explicit, fail-closed binding for the corrected experimental NNLS kernel."""
import ctypes as ct
import os
from functools import lru_cache
import numpy as np
# Load the wheel's BLAS dependencies before loading the experimental kernel.
import scipy.optimize  # noqa: F401


@lru_cache(maxsize=1)
def kernel():
    path = os.environ.get('APTA_NNLS_N1_LIBRARY')
    if not path or not os.path.isabs(path):
        raise RuntimeError('set APTA_NNLS_N1_LIBRARY to the explicit absolute artifact path')
    lib = ct.CDLL(path)
    fn = lib.__nnls
    fn.argtypes = [ct.c_int, ct.c_int] + [ct.c_void_p]*7 + [ct.c_int64,
        ct.POINTER(ct.c_double), ct.POINTER(ct.c_int64)]
    fn.restype = None
    return fn


def nnls(matrix, target, *, maxiter):
    a = np.array(matrix, dtype=np.float64, order='F', copy=True)
    b = np.array(target, dtype=np.float64, copy=True)
    if a.ndim != 2 or b.shape != (a.shape[0],) or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('invalid NNLS inputs')
    m, n = a.shape
    # This adapter is intentionally bounded to the frozen augmented E2 domain.
    if not 0 < n <= 180 or not n <= m <= 480 or maxiter <= 0:
        raise ValueError('outside experimental NNLS bounds')
    x = np.zeros(n); w = np.zeros(n); zz = np.zeros(m); saved = np.zeros(m)
    indices = np.zeros(n, dtype=np.int32)
    residual = ct.c_double(); info = ct.c_int64()
    kernel()(m, n, *[v.ctypes.data for v in (a,b,x,w,zz,indices,saved)],
             maxiter, ct.byref(residual), ct.byref(info))
    if info.value != 1:
        raise RuntimeError('NNLS failed: status '+str(info.value))
    return x, residual.value
