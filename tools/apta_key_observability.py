#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""O1 analytic projected tones; abstention is not a family score."""
import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
import apta_key_coherent as c

N = 12000
SCALE = N/2
FLOOR = SCALE*np.sqrt(np.finfo(float).eps)
require = c.p.f.c.require


def geometric(offsets):
    """Finite DFT sum with exact integral-cycle zeros, no near-grid snapping."""
    offsets = np.asarray(offsets, dtype=float)
    require(np.isfinite(offsets).all(), 'nonfinite geometric argument')
    integral = offsets == np.rint(offsets)
    result = np.zeros(offsets.shape, dtype=complex)
    result[integral & (np.remainder(offsets, N) == 0)] = N
    noninteger = ~integral
    values = offsets[noninteger]
    fractional = values-np.rint(values)
    result[noninteger] = np.expm1(2j*np.pi*fractional)/np.expm1(2j*np.pi*values/N)
    return result


def raw_pair(frequency):
    require(np.isfinite(frequency) and 0 < frequency < 6000, 'invalid frequency')
    response = np.mean(np.exp(2j*np.pi*frequency*np.arange(4)/48000))
    positive = response*geometric(frequency-c.RETAINED)
    negative = response.conjugate()*geometric(-frequency-c.RETAINED)
    sine = (positive-negative)/(2j)
    cosine = (positive+negative)/2
    return np.column_stack([np.concatenate([v.real, v.imag]) for v in (sine, cosine)])


def weak_pair(norms):
    norms = np.asarray(norms, dtype=float)
    require(norms.shape == (2,) and np.isfinite(norms).all() and (norms >= 0).all(), 'invalid pair norms')
    return bool(np.any(norms <= FLOOR))


def build_model(frequencies):
    require(len(frequencies) > 0, 'empty hypothesis')
    pairs, active, omitted, weak, norms = [], [], [], [], []
    for index, frequency in enumerate(frequencies):
        pair = raw_pair(frequency)
        pair_norms = np.linalg.norm(pair, axis=0)
        norms.append(pair_norms.tolist())
        structural = frequency == np.rint(frequency) and not (c.RETAINED[0] <= frequency <= c.RETAINED[-1])
        if structural:
            require(np.count_nonzero(pair) == 0, 'structural zero drift')
            omitted.append(index)
        else:
            if weak_pair(pair_norms):
                weak.append(index)
            active.extend([2*index, 2*index+1])
            pairs.append(pair)
    info = dict(frequencies_hz=list(frequencies), raw_column_norms=norms,
                structural_zero_components=omitted, weak_components=weak,
                normalization_floor=float(FLOOR), active_columns=active,
                status='ready', rank=None, matrix_and_inverse_bytes=0)
    if weak or not pairs:
        info['status'] = 'abstain_weak' if weak else 'abstain_empty'
        return None, info
    model = c.factor_matrix(np.concatenate(pairs, axis=1))
    info['rank'] = model['rank']
    info['matrix_and_inverse_bytes'] = model['matrix'].nbytes+model['inverse'].nbytes
    require(info['matrix_and_inverse_bytes'] <= 1048576, 'matrix storage gate')
    if model['rank'] != len(active):
        info['status'] = 'abstain_rank'
        return None, info
    model['active_columns'] = active
    model['physical_size'] = 2*len(frequencies)
    return model, info


def fit(observation, model):
    require(model is not None, 'abstaining model has no score')
    result = c.fit(observation, model, verify=True)
    physical = [None]*model['physical_size']
    for index, value in zip(model['active_columns'], result['physical_sine_cosine_coefficients']):
        physical[index] = value
    result['physical_sine_cosine_coefficients'] = physical
    return result


def independent_pair(frequency):
    phase = 2*np.pi*frequency*np.arange(48000)/48000
    return np.column_stack([c.real_vector(np.fft.rfft(c.p.f.average_four(wave, np.float64)))
                            for wave in (np.sin(phase), np.cos(phase))])


def bank():
    return [0.5, 127., 128., 440., 1016., 1017., 2048., 5999.]+[
        base+sign*2.**(-exponent) for base in (127., 1017.)
        for exponent in (4, 16, 28, 40) for sign in (-1, 1)]


def evaluate(source_commit):
    rows = []
    for frequency in bank():
        raw = raw_pair(frequency)
        independent = independent_pair(frequency)
        errors = np.linalg.norm(raw-independent, axis=0)/SCALE
        require(float(max(errors)) <= 1e-10, 'analytic/time-domain mismatch')
        model, info = build_model([frequency])
        integral = frequency == np.rint(frequency)
        grid_error = None
        if integral and info['status'] == 'ready':
            index = int(np.flatnonzero(c.RETAINED == frequency)[0])
            response = np.mean(np.exp(2j*np.pi*frequency*np.arange(4)/48000))
            expected = np.zeros_like(raw)
            expected[index] = [(-1j*SCALE*response).real, (SCALE*response).real]
            expected[index+len(c.RETAINED)] = [(-1j*SCALE*response).imag, (SCALE*response).imag]
            grid_error = float(np.linalg.norm(raw-expected)/SCALE)
            require(grid_error <= 1e-10, 'visible grid response mismatch')
        if not integral:
            require(not info['structural_zero_components'], 'near-grid incorrectly omitted')
        result = None
        amplitude_error = None
        if model is not None:
            phase = 2*np.pi*frequency*np.arange(48000)/48000
            pcm = c.p.f.average_four(np.sin(phase)+0.5*np.cos(phase), np.float64)
            result = fit(c.real_vector(np.fft.rfft(pcm)), model)
            require(result['normalized_squared_residual'] <= 1e-10, 'reconstruction gate')
            amplitude_error = float(np.max(np.abs(np.array(result['physical_sine_cosine_coefficients'])-[1., 0.5])))
        rows.append(dict(frequency_hz=frequency, **{k:v for k,v in info.items() if k != 'frequencies_hz'},
                         analytic_fft_scaled_errors=errors.tolist(), grid_scaled_error=grid_error,
                         fit=result, max_absolute_amplitude_error=amplitude_error))
    require(len(rows) == 24, 'bank length drift')
    sources = [Path(__file__), Path(c.__file__), Path(c.p.__file__), Path(c.p.f.__file__), Path(c.p.f.c.__file__)]
    return dict(screen='O1 numerical observability', source_commit=source_commit,
                tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                python=platform.python_version(), numpy=np.__version__, rows=rows,
                gates_pass=True, family_verdicts_evaluated=0,
                max_analytic_fft_scaled_error=max(max(r['analytic_fft_scaled_errors']) for r in rows),
                max_matrix_and_inverse_bytes=max(r['matrix_and_inverse_bytes'] for r in rows),
                statuses={s: sum(r['status'] == s for r in rows) for s in sorted({r['status'] for r in rows})})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-commit', required=True)
    parser.add_argument('--output-prefix', required=True)
    args = parser.parse_args()
    require(len(args.source_commit) == 40 and all(v in '0123456789abcdef' for v in args.source_commit), 'invalid revision')
    start = time.process_time()
    result = evaluate(args.source_commit)
    elapsed = time.process_time()-start
    require(elapsed <= 30, 'CPU gate')
    Path(args.output_prefix+'.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    Path(args.output_prefix+'-resource.json').write_text(json.dumps(dict(cpu_seconds=elapsed), indent=2)+'\n')
    print(json.dumps(dict(statuses=result['statuses'], cpu_seconds=elapsed, gates_pass=True)))


if __name__ == '__main__':
    main()
