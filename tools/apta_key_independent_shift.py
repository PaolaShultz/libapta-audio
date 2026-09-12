#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""R2 bounded independent two-tone search, unchanged R1 fit contract."""
import argparse
import hashlib
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np
import apta_key_local_shift as r

require = r.require
SUPPORTS = ([311.23, 733.61], [512.19, 512.79])
ERRORS = ([-.31, .27], [.29, -.33])


def search(evaluate):
    calls = []

    def sample(shifts):
        result = evaluate(np.array(shifts, dtype=float))
        require(result['score'] is None or (np.isfinite(result['score']) and result['score'] >= 0), 'invalid objective')
        row = dict(shifts_hz=list(map(float, shifts)), **result)
        calls.append(row)
        return row

    def best_of(candidates):
        valid = [v for v in candidates if v['score'] is not None]
        return min(valid, key=lambda v: (v['score'], v['shifts_hz'])) if valid else None

    for shifts in itertools.product(np.linspace(-.5, .5, 9), repeat=2):
        sample(shifts)
    best = best_of(calls)
    if best is None:
        return None, calls
    directions = [v for v in itertools.product((-1, 0, 1), repeat=2) if v != (0, 0)]
    step = .0625
    for _ in range(24):
        center = np.array(best['shifts_hz'])
        neighbors = [sample(np.clip(center+step*np.array(v), -.5, .5)) for v in directions]
        best = best_of([best]+neighbors)
        step *= .5
    require(len(calls) == 273, 'search budget drift')
    return best, calls


def source(support, phase_index, total):
    hashes = [hashlib.sha256(f'apta-r2-20260912|{support}|{phase_index}|{j}'.encode('ascii')).hexdigest()
              for j in range(2)]
    angles = np.array([2*np.pi*(int(v[:16], 16)/2**64) for v in hashes])
    components = [dict(frequency_hz=f, amplitude=total/2) for f in SUPPORTS[support]]
    pcm, relative, absolute = r.o.c.p.observation(components, angles)
    require(relative <= 1e-6, 'rounding gate')
    return r.o.c.real_vector(np.fft.rfft(pcm.astype(float))), dict(
        source_pcm_sha256=hashlib.sha256(pcm.tobytes()).hexdigest(), phase_sha256=hashes,
        rounding_relative_error=relative, rounding_absolute_error=absolute)


def recovery_metrics(best, seeds, truth, expected_amplitude, baseline):
    if best is None:
        return dict(screen_pass=False, abstained=True, frequency_error_hz=None,
                    amplitude_error=None, reconstruction_pass=False, no_regression=False)
    frequency_error = float(max(abs(np.sort(seeds+best['shifts_hz'])-np.sort(truth))))
    amplitude_error = max(abs(v-expected_amplitude) for v in best['amplitudes'])
    reconstruction = best['score'] <= 1e-10
    no_regression = baseline['score'] is None or best['score'] <= baseline['score']+1e-12
    return dict(screen_pass=bool(frequency_error <= 1e-4 and amplitude_error <= 1e-4 and reconstruction and no_regression),
        abstained=False, frequency_error_hz=frequency_error, amplitude_error=amplitude_error,
        reconstruction_pass=reconstruction, no_regression=no_regression)


def amplitude_stress_pass(oracle, best):
    return oracle['status'] == 'amplitude' and (best is None or best['score'] > 1e-10)


def evaluate(args):
    old = json.loads(Path(args.r1_evidence).read_text())
    require(r.o.c.p.f.c.digest(r.__file__) == old['tool_sha256'], 'R1 source drift')
    require(r.o.c.p.f.c.digest(args.o1_evidence) == old['o1_evidence_sha256'], 'O1 evidence drift')
    control, _ = r.evaluate(args.o1_evidence, old['source_commit'])
    require(control['rows'] == old['rows'], 'R1 control drift')
    rows, traces, stresses = [], [], []
    all_fits = []
    for support in range(2):
        for total in (.2, .8):
            for phase in range(4):
                observation, provenance = source(support, phase, total)
                oracle = r.fit(observation, SUPPORTS[support])
                all_fits.append(oracle)
                oracle_pass = oracle['score'] is not None and oracle['score'] <= 1e-10 and max(
                    abs(a-total/2) for a in oracle['amplitudes']) <= 1e-4
                for errors in ERRORS:
                    seeds = np.array(SUPPORTS[support])+errors
                    baseline = r.fit(observation, seeds)
                    best, calls = search(lambda shifts: r.fit(observation, seeds+shifts))
                    all_fits.extend([baseline]+calls)
                    metrics = recovery_metrics(best, seeds, SUPPORTS[support], total/2, baseline)
                    metrics['screen_pass'] = metrics['screen_pass'] and oracle_pass
                    rows.append(dict(support=support, total_source_amplitude=total, phase_index=phase,
                        true_frequencies_hz=SUPPORTS[support], seed_errors_hz=errors, **provenance,
                        baseline=baseline, oracle=oracle, oracle_pass=oracle_pass, best=best, **metrics,
                        evaluations=len(calls), candidate_status_counts=dict(Counter(c['status'] for c in calls))))
                    traces.append(dict(kind='recovery', row=len(rows)-1, calls=calls))
    for phase in range(4):
        observation, provenance = source(0, phase, 1.4)
        oracle = r.fit(observation, SUPPORTS[0])
        seeds = np.array(SUPPORTS[0])+ERRORS[0]
        best, calls = search(lambda shifts: r.fit(observation, seeds+shifts))
        all_fits.extend([oracle]+calls)
        stresses.append(dict(kind='amplitude', phase_index=phase, **provenance, oracle=oracle, best=best,
            screen_pass=amplitude_stress_pass(oracle, best), evaluations=len(calls),
            candidate_status_counts=dict(Counter(c['status'] for c in calls))))
        traces.append(dict(kind='amplitude', row=len(stresses)-1, calls=calls))
    observation = .2*r.o.independent_pair(512.)[:, 0]
    for kind, frequencies in [('rank', [512., 512.+2**-32]), ('weak', [1200.+2**-40])]:
        result = r.fit(observation, frequencies)
        all_fits.append(result)
        stresses.append(dict(kind=kind, frequencies_hz=frequencies, fit=result, screen_pass=result['status'] == kind))
    require(len(rows) == 32 and len(stresses) == 6, 'incomplete matrix')
    valid = [v for v in all_fits if v['score'] is not None]
    passed = all(v['screen_pass'] for v in rows+stresses)
    summary = dict(format='apta-key-independent-shift-r2-1', source_commit=args.source_commit,
        baseline_commit='c8c44fa2f33a4aa1a61496a1fa807a98d75d70e1',
        tool_sha256=r.o.c.p.f.c.digest(__file__), r1_tool_sha256=r.o.c.p.f.c.digest(r.__file__),
        source_sha256=old['source_sha256'], input_sha256={name:r.o.c.p.f.c.digest(getattr(args,name))
            for name in ('r1_evidence', 'o1_evidence')}, numpy=np.__version__,
        original_r1_rows_identical=48, original_o1_rows_identical=control['original_o1_rows_identical'],
        decision='bounded-independent-screen-passed-only' if passed else 'bounded-independent-screen-rejected',
        recovery_pass_count=sum(v['screen_pass'] for v in rows), recovery_count=32,
        stress_pass_count=sum(v['screen_pass'] for v in stresses), stress_count=6,
        recovery_abstentions=sum(v['abstained'] for v in rows),
        max_frequency_error_hz=max((v['frequency_error_hz'] for v in rows if not v['abstained']), default=None),
        max_refined_residual=max((v['best']['score'] for v in rows if v['best']), default=None),
        max_amplitude_error=max((v['amplitude_error'] for v in rows if not v['abstained']), default=None),
        reconstruction_fixes=sum(v['reconstruction_pass'] and (v['baseline']['score'] is None or v['baseline']['score'] > 1e-10) for v in rows),
        reconstruction_breaks=sum(not v['reconstruction_pass'] and v['baseline']['score'] is not None and v['baseline']['score'] <= 1e-10 for v in rows),
        max_analytic_column_error=max(v['max_column_error'] for v in all_fits),
        max_prediction_error=max(v['prediction_error'] for v in valid),
        max_storage_bytes=max(v['storage_bytes'] for v in all_fits),
        candidate_status_counts=dict(Counter(v['status'] for t in traces for v in t['calls'])),
        instrument_gates_pass=True, acceptance_claim=False, corpus_access=False,
        candidate_retained=False, production_cpu_ram_state_delta=0, rows=rows, stresses=stresses)
    return summary, dict(traces=traces)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('r1-evidence', 'o1-evidence', 'source-commit', 'output-prefix'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    require(len(args.source_commit) == 40 and all(v in '0123456789abcdef' for v in args.source_commit), 'invalid revision')
    paths = [Path(args.output_prefix+s+'.json') for s in ('', '-detail', '-resource')]
    require(all(not p.exists() for p in paths), 'refusing overwrite')
    started = time.process_time()
    summary, detail = evaluate(args)
    elapsed = time.process_time()-started
    require(elapsed <= 300, 'CPU gate')
    for path, value in zip(paths, (summary, detail, dict(cpu_seconds=elapsed, limit_seconds=300))):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','stresses','source_sha256','input_sha256')}))


if __name__ == '__main__':
    main()
