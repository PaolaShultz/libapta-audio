#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""C1: supplied-frequency coherent screen. No frequency discovery or key model."""
import argparse
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import apta_key_phase_robustness as p

RCOND = 1e-12
CELL_INDICES = p.f.c.cell_indices(np.arange(6001))
RETAINED = np.flatnonzero((CELL_INDICES >= 0) & (CELL_INDICES < 36))


def phases(fixture, family, realization, count):
    p.f.c.require(isinstance(fixture, int) and fixture >= 0 and family in ('known', 'pure') and
                  isinstance(realization, int) and 0 <= realization < 32 and isinstance(count, int) and count > 0,
                  'invalid phase coordinates')
    angles, hashes = [], []
    for index in range(count):
        digest = hashlib.sha256(f'apta-c1-20260912|{fixture}|{family}|{realization}|{index}'.encode('ascii')).digest()
        angles.append(2*np.pi*(int.from_bytes(digest[:8], 'big')/2**64))
        hashes.append(digest.hex())
    p.f.c.require(all(np.isfinite(v) and 0 <= v < 2*np.pi for v in angles), 'invalid phase value')
    return np.array(angles), hashes


def real_vector(spectrum):
    spectrum = np.asarray(spectrum)
    p.f.c.require(spectrum.shape == (6001,) and np.isfinite(spectrum).all(), 'invalid complex spectrum')
    selected = spectrum[RETAINED]
    return np.concatenate((selected.real, selected.imag))


def factor_matrix(raw):
    raw = np.asarray(raw, dtype=float)
    p.f.c.require(raw.ndim == 2 and raw.shape[0] > 0 and raw.shape[1] > 0 and
                  np.isfinite(raw).all(), 'invalid matrix')
    norms = np.linalg.norm(raw, axis=0)
    p.f.c.require((norms > 0).all(), 'zero column')
    matrix = raw/norms
    u, singular, vt = np.linalg.svd(matrix, full_matrices=False)
    selected = singular > RCOND*singular[0]
    inverse = (vt[selected].T/singular[selected]) @ u[:, selected].T
    p.f.c.require(np.isfinite(inverse).all(), 'invalid pseudoinverse')
    return dict(matrix=matrix, inverse=inverse, norms=norms, singular=singular,
                rank=int(selected.sum()), cutoff=float(RCOND*singular[0]))


def build_model(components):
    p.f.c.require(len(components) > 0, 'empty frequency hypothesis')
    columns = []
    max_parseval = max_direct = 0.0
    frames = np.arange(48000)
    for component in components:
        frequency = component['frequency_hz']
        p.f.c.require(np.isfinite(frequency) and 0 < frequency < 6000, 'invalid frequency')
        phase = 2*np.pi*frequency*frames/48000
        for wave in (np.sin(phase), np.cos(phase)):
            averaged = p.f.average_four(wave, np.float64)
            _, _, parseval, direct = p.f.checked_power(averaged)
            columns.append(real_vector(np.fft.rfft(averaged)))
            max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
    model = factor_matrix(np.array(columns).T)
    info = dict(shape=list(model['matrix'].shape), rank=model['rank'], rcond=RCOND,
                cutoff=model['cutoff'], singular_values=model['singular'].tolist(),
                condition_number=float(model['singular'][0]/model['singular'][-1]),
                matrix_and_inverse_bytes=model['matrix'].nbytes+model['inverse'].nbytes,
                frequencies_hz=[r['frequency_hz'] for r in components],
                max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct)
    p.f.c.require(info['matrix_and_inverse_bytes'] <= 1048576, 'matrix storage gate failed')
    return model, info


def fit(observation, model, verify=False):
    observation = np.asarray(observation, dtype=float)
    matrix = model['matrix']
    p.f.c.require(observation.shape == (matrix.shape[0],) and np.isfinite(observation).all(), 'invalid observation')
    total = float(np.dot(observation, observation))
    p.f.c.require(total > 0 and np.isfinite(total), 'zero/nonfinite observation energy')
    coefficients = model['inverse'] @ observation
    predicted = matrix @ coefficients
    residual = observation-predicted
    score = float(np.dot(residual, residual)/total)
    p.f.c.require(np.isfinite(coefficients).all() and np.isfinite(score) and score >= 0, 'invalid fit')
    discrepancy = None
    if verify:
        independent = np.linalg.lstsq(matrix, observation, rcond=RCOND)[0]
        discrepancy = float(np.linalg.norm(predicted-matrix @ independent)/max(1.0, np.linalg.norm(observation)))
        p.f.c.require(discrepancy <= 1e-10, 'independent least-squares disagreement')
    return dict(normalized_squared_residual=score, unit_column_coefficients=coefficients.tolist(),
                physical_sine_cosine_coefficients=(coefficients/model['norms']).tolist(),
                independent_prediction_discrepancy=discrepancy)


def passes(correct, wrong):
    return correct <= 1e-10 and wrong > correct+1e-6


def evaluate(args):
    started = time.process_time()
    prior = json.loads(Path(args.f2_evidence).read_text())
    p.f.c.require(p.f.c.digest(p.__file__) == prior['tool_sha256'], 'F2 source drift')
    for name in ('samples', 'witnesses', 'f1_evidence'):
        p.f.c.require(p.f.c.digest(getattr(args, name)) == prior['input_sha256'][name], 'old input drift: '+name)
    control, _, _ = p.evaluate(SimpleNamespace(samples=args.samples, witnesses=args.witnesses,
        f1_evidence=args.f1_evidence, source_commit=prior['source_commit']))
    p.f.c.require(control['rows'] == prior['rows'] and control['original_f1_rows_identical'] == 8, 'F2/F1 control drift')
    examples, seen = [], set()
    for example in json.loads(Path(args.witnesses).read_text())['exact_six_column_counterexamples']:
        key = json.dumps(example['nonzero_spectrum'], sort_keys=True)
        if key not in seen:
            seen.add(key)
            examples.append(example)
    p.f.c.require(len(examples) == 4, 'fixture count mismatch')
    rows, details, groups, models_info = [], [], [], []
    max_parseval = control['max_parseval_relative_error']
    max_direct = control['max_direct_scaled_error']
    peak = 0
    for fixture, example in enumerate(examples):
        components, models, marginals = {}, {}, {}
        ideal = np.zeros(36)
        for item in example['nonzero_spectrum']:
            ideal[item['midi']-48] = item['energy']
        for family in ('known', 'pure'):
            _, components[family] = p.f.reference(example, family)
            models[family], info = build_model(components[family])
            models_info.append(dict(fixture=fixture, family=family, **info))
            marginal, parseval, direct = p.marginal_reference(components[family])
            marginals[family] = marginal
            max_parseval = max(max_parseval, parseval, info['max_parseval_relative_error'])
            max_direct = max(max_direct, direct, info['max_direct_scaled_error'])
            if fixture == 0 and family == 'known':
                tracemalloc.start()
                repeated, repeated_info = build_model(components[family])
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                p.f.c.require(info == repeated_info and np.array_equal(models[family]['inverse'], repeated['inverse']),
                              'matrix replay drift')
        for family in ('known', 'pure'):
            other = 'pure' if family == 'known' else 'known'
            selected = []
            for realization in range(32):
                angles, hashes = phases(fixture, family, realization, len(components[family]))
                # The frozen generator sees phases; the fit receives only FFT and model.
                pcm, relative, absolute = p.observation(components[family], angles)
                power, _, parseval, direct = p.f.checked_power(pcm)
                vector = real_vector(np.fft.rfft(pcm.astype(float)))
                correct = fit(vector, models[family], verify=realization == 0)
                wrong = fit(vector, models[other], verify=realization == 0)
                dcorrect = correct['normalized_squared_residual']
                dwrong = wrong['normalized_squared_residual']
                f2correct, _ = p.f.fine_distance(power, marginals[family], ideal)
                f2wrong, _ = p.f.fine_distance(power, marginals[other], ideal)
                max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
                row = dict(fixture=fixture, representative_id=example['id'], generating_family=family,
                    realization=realization, phases_radians=angles.tolist(), phase_sha256=hashes,
                    correct_residual=dcorrect, wrong_residual=dwrong, residual_margin=dwrong-dcorrect,
                    screen_pass=passes(dcorrect, dwrong), correct_reconstruction_pass=dcorrect <= 1e-10,
                    discrimination_pass=dwrong > dcorrect+1e-6,
                    frozen_f2_correct_distance=f2correct, frozen_f2_wrong_distance=f2wrong,
                    frozen_f2_pass=p.passes(f2correct, f2wrong),
                    rounding_relative_error=relative, rounding_max_absolute_error=absolute)
                selected.append(row)
                rows.append(row)
                details.append(dict(**row, correct_fit=correct, wrong_fit=wrong))
            groups.append(dict(fixture=fixture, generating_family=family, count=32,
                pass_count=sum(r['screen_pass'] for r in selected),
                frozen_f2_pass_count=sum(r['frozen_f2_pass'] for r in selected),
                max_correct_residual=max(r['correct_residual'] for r in selected),
                min_wrong_residual=min(r['wrong_residual'] for r in selected),
                min_margin=min(r['residual_margin'] for r in selected),
                median_margin=float(np.median([r['residual_margin'] for r in selected]))))
    p.f.c.require(len(rows) == 256 and len(models_info) == 8 and len(groups) == 8, 'incomplete new matrix')
    passed = all(r['screen_pass'] for r in rows)
    elapsed = time.process_time()-started
    p.f.c.require(elapsed <= 60, 'host CPU limit exceeded')
    summary = dict(format='apta-key-coherent-c1-result-1', source_commit=args.source_commit,
        baseline_commit='1622027e64251e5b15e6630b9d64bf2157d59ac9', acceptance_claim=False, candidate_retained=False,
        supplied_frequencies=True, frequency_discovery=False, phase_invariant_proof=False,
        corpus_access=False, production_cpu_ram_state_delta=0,
        decision='new-phase-supplied-frequency-screen-passed-only' if passed else 'coherent-construction-rejected',
        all_observations_pass=passed, pass_count=sum(r['screen_pass'] for r in rows), observations=256,
        frozen_f2_new_bank_pass_count=sum(r['frozen_f2_pass'] for r in rows),
        previous_f2_rows_identical=256, previous_f1_rows_identical=8,
        input_sha256={name: p.f.c.digest(getattr(args, name)) for name in ('samples', 'witnesses', 'f1_evidence', 'f2_evidence')},
        tool_sha256=p.f.c.digest(__file__), f2_tool_sha256=p.f.c.digest(p.__file__),
        f1_tool_sha256=p.f.c.digest(p.f.__file__), coverage_tool_sha256=p.f.c.digest(p.f.c.__file__),
        h1_tool_sha256=p.f.c.digest(p.f.h.__file__),
        environment=dict(numpy=np.__version__, python=platform.python_version(), platform=platform.platform()),
        retained_bin_count=len(RETAINED), first_retained_bin_hz=int(RETAINED[0]), last_retained_bin_hz=int(RETAINED[-1]),
        max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct,
        max_independent_prediction_discrepancy=max(fit_result['independent_prediction_discrepancy']
             for row in details for fit_result in (row['correct_fit'], row['wrong_fit'])
             if fit_result['independent_prediction_discrepancy'] is not None),
        models=models_info, groups=groups, rows=rows)
    resource = dict(process_cpu_seconds=elapsed, cpu_limit_seconds=60, cpu_gate_pass=True,
        largest_matrix_and_inverse_bytes=max(r['matrix_and_inverse_bytes'] for r in models_info),
        numeric_storage_limit_bytes=1048576, numeric_storage_gate_pass=True,
        first_matrix_incremental_traced_peak_bytes=peak, traced_peak_excludes_other_models_and_reports=True,
        production_cpu_ram_state_delta=0)
    return summary, dict(rows=details), resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('samples', 'witnesses', 'f1-evidence', 'f2-evidence', 'source-commit', 'output-prefix'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    paths = [Path(args.output_prefix+suffix+'.json') for suffix in ('', '-detail', '-resource')]
    p.f.c.require(all(not path.exists() for path in paths), 'refusing overwrite')
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    print(json.dumps(dict(decision=values[0]['decision'], pass_count=values[0]['pass_count'],
                         frozen_f2_new_bank_pass_count=values[0]['frozen_f2_new_bank_pass_count'], resource=values[2])))


if __name__ == '__main__':
    main()
