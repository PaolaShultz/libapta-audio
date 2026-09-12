#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""R1 local common shift with supplied spacing and synthetic amplitude budget."""
import argparse
import hashlib
import json
import math
import time
from collections import Counter
from pathlib import Path

import numpy as np
import apta_key_observability as o

require = o.require
RCOND = np.sqrt(np.finfo(float).eps)
SUPPORTS = ([233.17], [233.17, 587.41], [440.13, 440.63])


def phases(support, realization, count):
    hashes = [hashlib.sha256(f'apta-r1-20260912|{support}|{realization}|{j}'.encode('ascii')).hexdigest()
              for j in range(count)]
    return np.array([2*np.pi*(int(h[:16], 16)/2**64) for h in hashes]), hashes


def amplitude_valid(coefficients):
    values = np.asarray(coefficients, dtype=float)
    require(values.ndim == 1 and values.size > 0 and values.size % 2 == 0 and np.isfinite(values).all(),
            'invalid physical coefficients')
    return bool(np.hypot(values[::2], values[1::2]).sum() <= 1.)


def factor(raw):
    raw = np.asarray(raw, dtype=float)
    require(raw.ndim == 2 and raw.shape[1] > 0 and np.isfinite(raw).all(), 'invalid raw matrix')
    if np.any(np.linalg.norm(raw, axis=0) <= o.FLOOR):
        return None, 'weak'
    left, singular, right = np.linalg.svd(raw, full_matrices=False)
    selected = singular > RCOND*singular[0]
    if int(selected.sum()) != raw.shape[1]:
        return None, 'rank'
    inverse = (right.T/singular) @ left.T
    require(raw.nbytes+inverse.nbytes <= 1048576, 'matrix storage gate')
    return dict(raw=raw, inverse=inverse, condition=float(singular[0]/singular[-1])), 'ready'


def fit(observation, frequencies):
    observation = np.asarray(observation, dtype=float)
    require(observation.shape == (1778,) and np.isfinite(observation).all() and
            np.dot(observation, observation) > 0, 'invalid/zero observation')
    require(1 <= len(frequencies) <= 2, 'unsupported tone count')
    pairs, errors = [], []
    for frequency in frequencies:
        raw = o.raw_pair(frequency)
        error = float(max(np.linalg.norm(raw-o.independent_pair(frequency), axis=0)/o.SCALE))
        require(error <= 1e-10, 'analytic column validation gate')
        pairs.append(raw)
        errors.append(error)
    model, status = factor(np.concatenate(pairs, axis=1))
    result = dict(status=status, score=None, max_column_error=max(errors), condition=None,
                  coefficients=None, amplitudes=None, prediction_error=None, storage_bytes=0)
    if model is None:
        return result
    raw, inverse = model['raw'], model['inverse']
    coefficients = inverse @ observation
    require(np.isfinite(coefficients).all(), 'nonfinite solution')
    result.update(condition=model['condition'], coefficients=coefficients.tolist(),
                  amplitudes=np.hypot(coefficients[::2], coefficients[1::2]).tolist(),
                  storage_bytes=raw.nbytes+inverse.nbytes)
    if not amplitude_valid(coefficients):
        result['status'] = 'amplitude'
        return result
    prediction = raw @ coefficients
    independent = raw @ np.linalg.lstsq(raw, observation, rcond=RCOND)[0]
    error = float(np.linalg.norm(prediction-independent)/max(1., np.linalg.norm(observation)))
    require(error <= 1e-10, 'independent prediction gate')
    residual = observation-prediction
    score = float(np.dot(residual, residual)/np.dot(observation, observation))
    require(np.isfinite(score), 'nonfinite score')
    result.update(score=score, prediction_error=error)
    return result


def search(evaluate):
    """Bounded generic 33-point + 24-update golden search, invalid scores excluded."""
    calls = []

    def sample(shift):
        result = evaluate(float(shift))
        require(result['score'] is None or (np.isfinite(result['score']) and result['score'] >= 0), 'invalid objective')
        calls.append(dict(shift_hz=float(shift), **result))
        return result['score'] if result['score'] is not None else math.inf

    grid = np.linspace(-.5, .5, 33)
    scores = [sample(shift) for shift in grid]
    if all(math.isinf(v) for v in scores):
        return None, calls
    index = min(range(33), key=lambda i: (scores[i], grid[i]))
    low, high = grid[max(0, index-1)], grid[min(32, index+1)]
    ratio = (math.sqrt(5)-1)/2
    left, right = high-ratio*(high-low), low+ratio*(high-low)
    fl, fr = sample(left), sample(right)
    for _ in range(24):
        if fl <= fr:
            high, right, fr = right, left, fl
            left = high-ratio*(high-low)
            fl = sample(left)
        else:
            low, left, fl = left, right, fr
            right = low+ratio*(high-low)
            fr = sample(right)
    require(len(calls) == 59, 'search budget drift')
    valid = [r for r in calls if r['score'] is not None]
    return min(valid, key=lambda r: (r['score'], r['shift_hz'])), calls


def evaluate(o1_path, source_commit):
    old = json.loads(Path(o1_path).read_text())
    for name, digest in old['source_sha256'].items():
        require(o.c.p.f.c.digest(Path(o.__file__).parent/name) == digest, 'dependency drift: '+name)
    require(o.evaluate(old['source_commit'])['rows'] == old['rows'], 'O1 control drift')
    rows, traces = [], []
    for support, frequencies in enumerate(SUPPORTS):
        for amplitude in (.05, .20):
            for realization in range(4):
                angles, hashes = phases(support, realization, len(frequencies))
                components = [dict(frequency_hz=f, amplitude=amplitude/len(frequencies)) for f in frequencies]
                pcm, relative, absolute = o.c.p.observation(components, angles)
                require(relative <= 1e-6, 'source rounding gate')
                observation = o.c.real_vector(np.fft.rfft(pcm.astype(float)))
                oracle = fit(observation, frequencies)
                for seed_error in (-.37, .37):
                    seeds = np.array(frequencies)+seed_error
                    baseline = fit(observation, seeds)
                    best, calls = search(lambda shift: fit(observation, seeds+shift))
                    expected = amplitude/len(frequencies)
                    oracle_pass = oracle['score'] is not None and oracle['score'] <= 1e-10 and max(
                        abs(v-expected) for v in oracle['amplitudes']) <= 1e-5
                    shift_error = abs(best['shift_hz']+seed_error) if best else None
                    amplitude_error = max(abs(v-expected) for v in best['amplitudes']) if best else None
                    no_regression = best is not None and (baseline['score'] is None or best['score'] <= baseline['score']+1e-12)
                    passed = bool(best is not None and shift_error <= 1e-5 and best['score'] <= 1e-10 and
                                  amplitude_error <= 1e-5 and no_regression and oracle_pass)
                    rows.append(dict(support=support, true_frequencies_hz=frequencies, total_source_amplitude=amplitude,
                        phase_index=realization, phase_sha256=hashes, source_pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),
                        source_rounding_relative_error=relative, source_rounding_absolute_error=absolute,
                        seed_error_hz=seed_error, baseline=baseline, oracle=oracle, oracle_pass=oracle_pass,
                        best=best, shift_error_hz=shift_error, amplitude_error=amplitude_error,
                        no_regression=no_regression, screen_pass=passed, evaluations=len(calls),
                        candidate_status_counts=dict(Counter(r['status'] for r in calls))))
                    traces.append(dict(row=len(rows)-1, calls=calls))
    require(len(rows) == 48, 'bank size drift')
    all_fits = [f for row in rows for f in (row['baseline'], row['oracle'])]+[f for t in traces for f in t['calls']]
    valid = [f for f in all_fits if f['score'] is not None]
    summary = dict(format='apta-key-local-shift-r1-1', source_commit=source_commit,
        baseline_commit='0f82a398fab4e05f153edc4e2e6b68ef14512ad1',
        tool_sha256=o.c.p.f.c.digest(__file__), o1_evidence_sha256=o.c.p.f.c.digest(o1_path),
        source_sha256=old['source_sha256'], numpy=np.__version__, original_o1_rows_identical=24,
        instrument_gates_pass=True, decision='bounded-common-shift-screen-passed-only' if all(r['screen_pass'] for r in rows)
        else 'bounded-common-shift-screen-rejected', pass_count=sum(r['screen_pass'] for r in rows), count=48,
        abstentions=sum(r['best'] is None for r in rows), oracle_pass_count=sum(r['oracle_pass'] for r in rows),
        max_shift_error_hz=max((r['shift_error_hz'] for r in rows if r['best']), default=None),
        max_amplitude_error=max((r['amplitude_error'] for r in rows if r['best']), default=None),
        max_refined_residual=max((r['best']['score'] for r in rows if r['best']), default=None),
        reconstruction_fixes=sum(r['best'] is not None and r['best']['score'] <= 1e-10 and
            (r['baseline']['score'] is None or r['baseline']['score'] > 1e-10) for r in rows),
        reconstruction_breaks=sum(r['baseline']['score'] is not None and r['baseline']['score'] <= 1e-10 and
            (r['best'] is None or r['best']['score'] > 1e-10) for r in rows),
        max_analytic_column_error=max(f['max_column_error'] for f in all_fits),
        max_prediction_error=max(f['prediction_error'] for f in valid),
        max_storage_bytes=max(f['storage_bytes'] for f in all_fits),
        candidate_status_counts=dict(Counter(f['status'] for t in traces for f in t['calls'])),
        acceptance_claim=False, corpus_access=False, candidate_retained=False, production_cpu_ram_state_delta=0,
        rows=rows)
    return summary, dict(traces=traces)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('o1-evidence', 'source-commit', 'output-prefix'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    require(len(args.source_commit) == 40 and all(v in '0123456789abcdef' for v in args.source_commit), 'invalid revision')
    paths = [Path(args.output_prefix+s+'.json') for s in ('', '-detail', '-resource')]
    require(all(not p.exists() for p in paths), 'refusing overwrite')
    started = time.process_time()
    summary, detail = evaluate(args.o1_evidence, args.source_commit)
    elapsed = time.process_time()-started
    require(elapsed <= 120, 'CPU gate')
    for path, value in zip(paths, (summary, detail, dict(cpu_seconds=elapsed, limit_seconds=120))):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows', 'source_sha256')}))


if __name__ == '__main__':
    main()
