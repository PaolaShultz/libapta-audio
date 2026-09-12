#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""R3 paired band-SNR robustness of unchanged R2 search/R1 fit."""
import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import apta_key_independent_shift as s

r = s.r
require = r.require
SUPPORTS = ([277.31, 659.47], [523.17, 523.77])
CONDITIONS = ('clean', '40db', '20db')


def vector(samples):
    return r.o.c.real_vector(np.fft.rfft(np.asarray(samples, dtype=float)))


def amplitudes(ratio):
    require(np.isfinite(ratio) and ratio > 0, 'invalid amplitude ratio')
    return np.array([.4*ratio/(1+ratio), .4/(1+ratio)])


def noise(support, phase):
    key = f'apta-r3-noise-20260912|{support}|{phase}'.encode('ascii')
    data = hashlib.shake_256(key).digest(48000*4)
    values = (np.frombuffer(data, dtype='<u4').astype(float)+.5)/2**32-.5
    values -= np.mean(values)
    return values, hashlib.sha256(data).hexdigest()


def scale_noise(clean_vector, noise_vector, snr):
    require(np.isfinite(snr) and np.linalg.norm(clean_vector) > 0 and np.linalg.norm(noise_vector) > 0, 'invalid SNR input')
    return float(np.linalg.norm(clean_vector)/np.linalg.norm(noise_vector)*10**(-snr/20))


def observation(support, phase, ratio, condition):
    require(condition in CONDITIONS, 'invalid condition')
    hashes = [hashlib.sha256(f'apta-r3-phase-20260912|{support}|{phase}|{j}'.encode('ascii')).hexdigest() for j in range(2)]
    angles = [2*np.pi*(int(h[:16], 16)/2**64) for h in hashes]
    source_amplitudes = amplitudes(ratio)
    clean = np.zeros(48000)
    for f, a, angle in zip(SUPPORTS[support], source_amplitudes, angles):
        clean += r.o.c.p.component_wave(dict(frequency_hz=f, amplitude=a), angle)
    clean_double = r.o.c.p.f.average_four(clean, np.float64)
    clean_vector = vector(clean_double)
    raw_noise, noise_hash = noise(support, phase)
    noise_vector = vector(r.o.c.p.f.average_four(raw_noise, np.float64))
    scale, snr, ratio_error, achieved = 0., None, 0., None
    if condition != 'clean':
        snr = 40. if condition == '40db' else 20.
        scale = scale_noise(clean_vector, noise_vector, snr)
        scaled_vector = vector(r.o.c.p.f.average_four(scale*raw_noise, np.float64))
        actual_ratio = float(np.dot(scaled_vector, scaled_vector)/np.dot(clean_vector, clean_vector))
        target_ratio = 10**(-snr/10)
        ratio_error = abs(actual_ratio/target_ratio-1)
        require(ratio_error <= 1e-12, 'noise energy scaling gate')
        achieved = float(-10*np.log10(actual_ratio))
    mixed = clean+scale*raw_noise
    pcm = r.o.c.p.f.average_four(mixed, np.float32)
    double = r.o.c.p.f.average_four(mixed, np.float64)
    rounding = pcm.astype(float)-double
    relative = float(np.linalg.norm(rounding)/np.linalg.norm(double))
    absolute = float(max(abs(rounding)))
    require(relative <= 1e-6 and absolute <= 1e-6, 'rounding gate')
    observed = vector(pcm)
    require(np.isfinite(observed).all() and np.dot(observed, observed) > 0, 'invalid observation')
    perturbation = observed-clean_vector
    ceiling = 1e-10 if condition == 'clean' else float(1.10*np.dot(perturbation, perturbation)/np.dot(observed, observed)+1e-10)
    return observed, dict(support=support, phase_index=phase, amplitude_ratio=ratio, condition=condition,
        true_frequencies_hz=SUPPORTS[support], true_amplitudes=source_amplitudes.tolist(),
        phase_sha256=hashes, clean_source_sha256=hashlib.sha256(clean.tobytes()).hexdigest(),
        noise_uint32_sha256=noise_hash, noise_scale=scale, achieved_band_snr_db=achieved,
        noise_energy_ratio_relative_error=ratio_error,
        observed_pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(),
        rounding_relative_error=relative, rounding_absolute_error=absolute, oracle_residual_ceiling=ceiling)


def metrics(best, seeds, row, baseline):
    if best is None:
        return dict(abstained=True, frequency_error_hz=None, amplitude_absolute_error=None,
                    amplitude_relative_error=None, frequency_pass=False, amplitude_pass=False,
                    residual_pass=False, no_regression=False, screen_pass=False)
    order = np.argsort(seeds+best['shifts_hz'])
    frequency_error = float(max(abs((seeds+best['shifts_hz'])[order]-row['true_frequencies_hz'])))
    errors = abs(np.array(best['amplitudes'])[order]-row['true_amplitudes'])
    absolute = float(max(errors))
    relative = float(max(errors/row['true_amplitudes']))
    condition = row['condition']
    frequency_limit = {'clean':1e-4, '40db':.02, '20db':.10}[condition]
    amplitude_pass = absolute <= 1e-4 if condition == 'clean' else relative <= (.10 if condition == '40db' else .50)
    frequency_pass = frequency_error <= frequency_limit
    residual_pass = best['score'] <= row['oracle_residual_ceiling']
    no_regression = baseline['score'] is None or best['score'] <= baseline['score']+1e-12
    return dict(abstained=False, frequency_error_hz=frequency_error, amplitude_absolute_error=absolute,
        amplitude_relative_error=relative, frequency_pass=frequency_pass, amplitude_pass=bool(amplitude_pass),
        residual_pass=residual_pass, no_regression=no_regression,
        screen_pass=bool(frequency_pass and amplitude_pass and residual_pass and no_regression))


def aggregate(rows):
    require(len(rows) > 0, 'empty group')
    return dict(count=len(rows), passes=sum(v['screen_pass'] for v in rows),
        abstentions=sum(v['abstained'] for v in rows), frequency_failures=sum(not v['frequency_pass'] for v in rows),
        amplitude_failures=sum(not v['amplitude_pass'] for v in rows), residual_failures=sum(not v['residual_pass'] for v in rows),
        residual_pass_inaccurate=sum(v['residual_pass'] and not (v['frequency_pass'] and v['amplitude_pass']) for v in rows),
        no_regression_failures=sum(not v['no_regression'] for v in rows),
        max_frequency_error_hz=max((v['frequency_error_hz'] for v in rows if not v['abstained']), default=None),
        max_relative_amplitude_error=max((v['amplitude_relative_error'] for v in rows if not v['abstained']), default=None),
        max_residual=max((v['best']['score'] for v in rows if v['best']), default=None))


def evaluate(args):
    old = json.loads(Path(args.r2_evidence).read_text())
    require(r.o.c.p.f.c.digest(s.__file__) == old['tool_sha256'], 'R2 tool drift')
    for name in ('r1_evidence','o1_evidence'):
        require(r.o.c.p.f.c.digest(getattr(args,name)) == old['input_sha256'][name], 'input drift')
    control, _ = s.evaluate(SimpleNamespace(r1_evidence=args.r1_evidence, o1_evidence=args.o1_evidence, source_commit=old['source_commit']))
    require(control['rows'] == old['rows'] and control['stresses'] == old['stresses'], 'R2 replay drift')
    rows, traces, fits = [], [], []
    for support in range(2):
        for ratio in (1.,4.,.25):
            for phase in range(2):
                clean_result = None
                for condition in CONDITIONS:
                    observed, provenance = observation(support, phase, ratio, condition)
                    seeds = np.array(SUPPORTS[support])+[-.31,.27]
                    baseline = r.fit(observed, seeds)
                    oracle = r.fit(observed, SUPPORTS[support])
                    best, calls = s.search(lambda shifts:r.fit(observed, seeds+shifts))
                    fits.extend([baseline,oracle]+calls)
                    result = metrics(best, seeds, provenance, baseline)
                    if condition == 'clean':
                        clean_result = result['screen_pass']
                    rows.append(dict(**provenance, baseline=baseline, oracle=oracle, best=best, **result,
                        clean_pair_pass=clean_result, paired_break=bool(clean_result and not result['screen_pass']),
                        paired_fix=bool(not clean_result and result['screen_pass']), evaluations=len(calls),
                        candidate_status_counts=dict(Counter(v['status'] for v in calls))))
                    traces.append(dict(row=len(rows)-1, calls=calls))
    require(len(rows) == 36, 'row count drift')
    valid = [v for v in fits if v['score'] is not None]
    totals = [dict(condition=condition, **aggregate([v for v in rows if v['condition'] == condition])) for condition in CONDITIONS]
    groups = [dict(support=support, amplitude_ratio=ratio, condition=condition,
                   **aggregate([v for v in rows if (v['support'],v['amplitude_ratio'],v['condition']) == (support,ratio,condition)]))
              for support in range(2) for ratio in (1.,4.,.25) for condition in CONDITIONS]
    summary = dict(format='apta-key-noise-robustness-r3-1', source_commit=args.source_commit,
        baseline_commit='948da5344c642e2a99d11acf72fbea90cf7e3cf9', tool_sha256=r.o.c.p.f.c.digest(__file__),
        r2_tool_sha256=r.o.c.p.f.c.digest(s.__file__), r1_tool_sha256=r.o.c.p.f.c.digest(r.__file__),
        source_sha256=old['source_sha256'], input_sha256={name:r.o.c.p.f.c.digest(getattr(args,name))
            for name in ('r2_evidence','r1_evidence','o1_evidence')}, numpy=np.__version__,
        original_r2_rows_identical=32, original_r2_stresses_identical=6,
        original_r1_rows_identical=48, original_o1_rows_identical=24,
        decision='finite-noise-screen-passed-only' if all(v['screen_pass'] for v in rows) else 'finite-noise-screen-rejected',
        totals=totals, groups=groups, overall=aggregate(rows),
        noisy_paired_breaks=sum(v['paired_break'] for v in rows if v['condition'] != 'clean'),
        noisy_paired_fixes=sum(v['paired_fix'] for v in rows if v['condition'] != 'clean'),
        max_analytic_column_error=max(v['max_column_error'] for v in fits),
        max_prediction_error=max(v['prediction_error'] for v in valid), max_storage_bytes=max(v['storage_bytes'] for v in fits),
        candidate_status_counts=dict(Counter(v['status'] for t in traces for v in t['calls'])),
        instrument_gates_pass=True, acceptance_claim=False, corpus_access=False, candidate_retained=False,
        production_cpu_ram_state_delta=0, rows=rows)
    return summary, dict(traces=traces)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('r2-evidence','r1-evidence','o1-evidence','source-commit','output-prefix'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    require(len(args.source_commit) == 40 and all(v in '0123456789abcdef' for v in args.source_commit), 'invalid revision')
    paths = [Path(args.output_prefix+suffix+'.json') for suffix in ('','-detail','-resource')]
    require(all(not path.exists() for path in paths), 'refusing overwrite')
    started = time.process_time()
    summary, detail = evaluate(args)
    elapsed = time.process_time()-started
    require(elapsed <= 300, 'CPU gate')
    for path, value in zip(paths,(summary,detail,dict(cpu_seconds=elapsed,limit_seconds=300))):
        with path.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
            stream.write('\n')
    print(json.dumps(dict(decision=summary['decision'],totals=summary['totals'],cpu_seconds=elapsed)))


if __name__ == '__main__':
    main()
