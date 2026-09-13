# SPDX-License-Identifier: Apache-2.0
"""Frozen fresh A1 generator; evaluator only."""
import hashlib
import numpy as np
import apta_key_joint_pcm as j

def window(tonic,mode,family,index):
    offset=(0,7,5,0,7,0,5,0)[index];root=48+tonic+offset
    third=4 if mode==0 or offset==7 else 3
    notes=[root,root+third,root+7]+([root-12] if index in (1,6) else [])
    partials=(1,) if family=='pure' else (2,3,4) if family=='missing' else (1,2,3,4)
    weights=np.array([1,.5,.25,.75][:len(notes)] if family=='unequal' else [1.]*len(notes))
    weights/=weights.sum()
    detune=(.23 if index%2==0 else -.19) if family=='detuned' else 0.
    exponent=1.7 if family=='steep' else 1.
    t=np.arange(j.e.RATE)/j.e.RATE;pcm=np.zeros(j.e.RATE)
    for n,note in enumerate(notes):
        for h in partials:
            seed=f'apta-a1-fresh-20260913|{tonic}|{mode}|{family}|{index}|{n}|{h}'
            phase=int.from_bytes(hashlib.sha256(seed.encode('ascii')).digest()[:8],'big')/2**64*2*np.pi
            frequency=440*2**((note-69+detune)/12)*h
            pcm+=(.12*weights[n]/h**exponent)*np.sin(2*np.pi*frequency*t+phase)
    return pcm.astype(np.float32)

