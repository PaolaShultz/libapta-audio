"""Historical deterministic deletion reduction; write only to a supplied new path."""
import argparse
from pathlib import Path
import numpy as np
from scipy.optimize import nnls
p=Path(__file__).parent
d=np.load(p/'missing-8-1-6.npz');A=d['augmented'].copy();b=d['rhs'].copy()
def fails(A,b):
 try:x,r=nnls(A,b,maxiter=30*A.shape[1])
 except RuntimeError:return False
 g=A.T@(A@x-b)
 return np.max(np.where(x>1e-10,abs(g),np.maximum(-g,0)))>1e-8
changed=True
while changed:
 changed=False
 for axis in (1,0):
  for i in range(A.shape[axis]-1,-1,-1):
   if A.shape[axis]<=2:continue
   C=np.delete(A,i,axis);y=np.delete(b,i) if axis==0 else b
   if fails(C,y):A,b=C,y;changed=True
print(A.shape)
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args()
with args.output.open('xb') as stream:np.savez(stream,augmented=A,rhs=b)
print(repr(A));print(repr(b));print(nnls(A,b,maxiter=30*A.shape[1]))
