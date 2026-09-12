#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explicit offline E1 candidate; PCM only, no labels or oracle inputs."""
import argparse
import json
import wave
import numpy as np
import apta_key_coverage_diagnostic as c

RATE = 48000
FFT = 65536
# Conservative live-array reservation: input/conversion/window products, FFT
# scratch/results, and five worst-case 240-by-60 attribution arrays.
NUMERIC_BOUND = RATE*8*4 + FFT*8*3 + (FFT//2+1)*16*2 + 240*60*8*5


def peaks(pcm):
    x = np.asarray(pcm, dtype=np.float64)
    c.require(x.shape == (RATE,) and np.isfinite(x).all() and
              np.max(np.abs(x)) <= 1, 'invalid PCM window')
    magnitude = np.abs(np.fft.rfft(x*np.hanning(RATE), n=FFT))
    bins = np.arange(1, len(magnitude)-1)
    inside = (bins*RATE/FFT >= 65) & (bins*RATE/FFT <= 4200)
    band_max = float(np.max(magnitude[bins[inside]]))
    if band_max == 0:
        return np.array([]), np.array([])
    selected = bins[inside & (magnitude[bins] > magnitude[bins-1]) &
                    (magnitude[bins] >= magnitude[bins+1]) &
                    (magnitude[bins] >= .01*band_max)]
    selected = sorted(selected, key=lambda k: (-magnitude[k], k))[:60]
    frequencies, amplitudes = [], []
    for k in selected:
        a,b,d = np.log(np.maximum(magnitude[k-1:k+2], np.finfo(float).tiny))
        denominator = a-2*b+d
        offset = 0. if denominator == 0 else float(np.clip(.5*(a-d)/denominator, -.5, .5))
        frequencies.append((k+offset)*RATE/FFT)
        amplitudes.append(float(magnitude[k]))
    order = np.argsort(frequencies, kind='stable')
    return np.array(frequencies)[order], np.array(amplitudes)[order]


def templates(frequencies):
    if len(frequencies) == 0:
        return np.array([]), np.zeros((0,0))
    candidates = np.unique((frequencies[:,None]/np.arange(1,5)).ravel())
    candidates = candidates[(candidates >= 65) & (candidates <= 1047)]
    kept, rows = [], []
    for fundamental in candidates:
        row = np.zeros(len(frequencies))
        matched = []
        for h in range(1,5):
            distances = np.abs(1200*np.log2(frequencies/(h*fundamental)))
            k = int(np.argmin(distances))
            if distances[k] <= 20 and row[k] == 0:
                row[k] = 1/h
                matched.append(h)
        if 1 in matched or len(matched) >= 2:
            kept.append(fundamental); rows.append(row)
    return np.array(kept), np.array(rows).reshape(-1,len(frequencies))


def attribute(frequencies, amplitudes):
    frequencies = np.asarray(frequencies, dtype=float)
    residual = np.asarray(amplitudes, dtype=float).copy()
    c.require(frequencies.ndim == 1 and frequencies.shape == residual.shape and
              len(frequencies) <= 60 and np.isfinite(frequencies).all() and
              np.isfinite(residual).all() and (frequencies > 0).all() and
              (residual >= 0).all(), 'invalid peaks')
    fundamentals, matrix = templates(frequencies)
    original = float(residual@residual)
    norms = np.sum(matrix*matrix,axis=1)
    chosen, energies = [], [original]
    for _ in range(12):
        if not len(matrix) or energies[-1] <= .01*original:
            break
        projection = matrix@residual
        caps = np.full(matrix.shape, np.inf)
        np.divide(residual[None,:],matrix,out=caps,where=matrix>0)
        amplitude = np.minimum(projection/norms, np.min(caps,axis=1))
        reduction = 2*amplitude*projection-amplitude**2*norms
        index = int(np.argmax(reduction))
        if reduction[index] <= 0:
            break
        residual -= amplitude[index]*matrix[index]
        c.require(np.min(residual) >= -1e-12*max(1,np.sqrt(original)), 'negative residual')
        residual = np.maximum(residual,0)
        energy = float(residual@residual)
        c.require(energy <= energies[-1]+1e-12*max(1,original), 'objective increase')
        energies.append(energy)
        chosen.append((float(fundamentals[index]),float(amplitude[index])))
    return chosen, dict(selected_count=len(chosen),residual_energies=energies,
                       residual_fraction=energies[-1]/original if original else 0.)


def chroma(frequencies, amplitudes):
    result = np.zeros(12,dtype=np.float64)
    for frequency, amplitude in zip(frequencies,amplitudes):
        midi = int(np.floor(69+12*np.log2(frequency/440)+.5))
        result[midi%12] += amplitude**2
    if result.sum() > 0:
        result /= result.sum()
    return result


def extract(pcm):
    frequencies, amplitudes = peaks(pcm)
    selected, diagnostics = attribute(frequencies, amplitudes)
    candidate = chroma([p[0] for p in selected],[p[1] for p in selected])
    return candidate, chroma(frequencies,amplitudes), dict(peak_count=len(frequencies),**diagnostics)


def wav_windows(stream):
    c.require(stream.getframerate() == RATE and stream.getnchannels() in (1,2)
              and stream.getsampwidth() == 2 and stream.getcomptype() == 'NONE', 'requires PCM16 48 kHz mono/stereo')
    for _ in range(stream.getnframes()//RATE):
        raw = stream.readframes(RATE)
        c.require(len(raw) == RATE*stream.getnchannels()*2, 'truncated WAV')
        yield np.frombuffer(raw,dtype='<i2').astype(float).reshape(-1,stream.getnchannels()).mean(axis=1)/32768


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experimental-e1', action='store_true', required=True)
    p.add_argument('--wav',required=True);p.add_argument('--probe',required=True)
    args=p.parse_args()
    # CLI keeps only accumulated state; no duration-proportional diagnostics.
    total=np.zeros(12);direct=np.zeros(12);count=0;max_peaks=0;max_components=0
    with wave.open(args.wav,'rb') as stream:
        trailing=stream.getnframes()%RATE
        for pcm in wav_windows(stream):
            a,b,d=extract(pcm);total+=a;direct+=b;count+=1
            max_peaks=max(max_peaks,d['peak_count']);max_components=max(max_components,d['selected_count'])
    result=c.query_probe(args.probe,[(total,max(1,count))])[0]
    print(json.dumps(dict(experimental='E1',result=result,windows=count,trailing_samples=trailing,
                         max_peaks=max_peaks,max_components=max_components,numeric_bound_bytes=NUMERIC_BOUND,
                         confidence_calibrated=False,acceptance_claim=False),allow_nan=False))


if __name__ == '__main__':main()
