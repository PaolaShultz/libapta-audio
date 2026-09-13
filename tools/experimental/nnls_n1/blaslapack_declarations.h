#include <stdint.h>
#define CBLAS_INT int
#define BLAS_FUNC(name) scipy_##name##_
extern double scipy_ddot_(int*,double*,int*,double*,int*);
extern double scipy_dnrm2_(int*,double*,int*);
extern void scipy_dlarfgp_(int*,double*,double*,int*,double*);
extern void scipy_dlarf_(char*,int*,int*,double*,int*,double*,double*,int*,double*);
extern void scipy_dlartgp_(double*,double*,double*,double*,double*);
