# Experimental N1 NNLS kernel

`upstream_nnls.c` and `nnls.h` are unmodified SciPy v1.18.1 sources:
https://github.com/scipy/scipy/tree/v1.18.1/scipy/optimize/src
SciPy's BSD license is preserved in LICENSE.txt. The small LP64 BLAS declaration
header is local build glue, not the full upstream header.

`restore-rejected-column.patch` adds caller-owned scratch, saves the prospective
Householder column segment, and restores it on both rejection paths. Accepted
columns, pivots, active-set updates, termination and iteration budget are unchanged.
The matching header signature is changed by the explicit builder. This avoids
allocation inside the kernel. Extra live storage is at most 480 doubles.

`tools/build_apta_nnls_n1.py` builds a separate Linux host library against the
installed SciPy 1.18.1 wheel's LP64 BLAS. It refuses an existing output directory.
It does not patch SciPy, enter CMake, or change any production build. The Python
binding requires APTA_NNLS_N1_LIBRARY to name an explicit absolute artifact path.
No production/embedded/platform portability claim is made.

The returned solution must still pass the frozen external numerical gates.
BVLS is used only by diagnostic tests; it is not a fallback.
