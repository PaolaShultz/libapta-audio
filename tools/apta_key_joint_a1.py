# SPDX-License-Identifier: Apache-2.0
"""Frozen E2-A1: N1 attribution with linear amplitude-mass chroma."""
import numpy as np
import apta_key_joint_n1 as n1

e=n1.e
NUMERIC_BOUND=n1.NUMERIC_BOUND+12*8


def amplitude_chroma(frequencies, amplitudes):
    result=np.zeros(12)
    for frequency,amplitude in zip(frequencies,amplitudes):
        midi=int(np.floor(69+12*np.log2(frequency/440)+.5))
        result[midi%12]+=amplitude
    if result.sum()>0:result/=result.sum()
    return result


def attribute(frequencies,amplitudes):
    chroma,diagnostic=n1.attribute(frequencies,amplitudes)
    if diagnostic['status']=='ready':
        chroma=amplitude_chroma(diagnostic['frequencies_hz'],diagnostic['physical_amplitudes'])
    return chroma,diagnostic


def extract(pcm):
    f,a=e.peaks(pcm)
    chroma,diagnostic=attribute(f,a)
    return chroma,e.chroma(f,a),dict(peak_count=len(f),**diagnostic)
