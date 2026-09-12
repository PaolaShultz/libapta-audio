#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""C2 finite frequency-error sensitivity; no frequency search or new fitter."""
import argparse
import hashlib
import json
import math
import platform
import time
import tracemalloc
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import apta_key_coherent as c

CONDITIONS = ('exact', 'minus-quarter-hz', 'plus-quarter-hz', 'independent-quarter-hz', 'nearest-hz')


def perturb(components, condition, fixture, family):
    c.p.f.c.require(condition in CONDITIONS and isinstance(fixture, int) and fixture >= 0 and
                     family in ('known', 'pure') and len(components) > 0, 'invalid frequency construction')
    result, provenance = [], []
    for index, component in enumerate(components):
        frequency = component['frequency_hz']
        c.p.f.c.require(np.isfinite(frequency) and 0 < frequency < 6000, 'invalid input frequency')
        phase_hash = None
        if condition == 'exact':
            changed = frequency
        elif condition == 'minus-quarter-hz':
            changed = frequency-0.25
        elif condition == 'plus-quarter-hz':
            changed = frequency+0.25
        elif condition == 'nearest-hz':
            changed = float(math.floor(frequency+0.5))
        else:
            digest = hashlib.sha256(f'apta-c2-20260912|{fixture}|{family}|{index}'.encode('ascii')).digest()
            phase_hash = digest.hex()
            changed = frequency+(0.25 if digest[0] & 1 else -0.25)
        c.p.f.c.require(0 < changed < 6000 and np.isfinite(changed), 'perturbed frequency outside supported range')
        result.append(dict(component, frequency_hz=changed))
        provenance.append(dict(component=index, original_frequency_hz=frequency, supplied_frequency_hz=changed,
                               offset_hz=changed-frequency, sign_sha256=phase_hash))
    return result, provenance


def gates(correct, wrong, exact=False):
    ceiling = 1e-10 if exact else 0.10
    ranking = wrong > correct+1e-6
    reconstruction = correct <= ceiling
    return dict(discrimination_pass=ranking, reconstruction_pass=reconstruction,
                screen_pass=ranking and reconstruction)


def group_rows(rows, condition, fixture, family):
    selected = [r for r in rows if (r['condition'], r['fixture'], r['generating_family']) == (condition, fixture, family)]
    c.p.f.c.require(len(selected) == 32, 'incomplete score group')
    return dict(condition=condition, fixture=fixture, generating_family=family, count=32,
        pass_count=sum(r['screen_pass'] for r in selected),
        ranking_failures=sum(not r['discrimination_pass'] for r in selected),
        rank_reversals=sum(r['wrong_residual'] < r['correct_residual'] for r in selected),
        margin_ties=sum(abs(r['wrong_residual']-r['correct_residual']) <= 1e-6 for r in selected),
        reconstruction_failures=sum(not r['reconstruction_pass'] for r in selected),
        changed_family_verdicts=sum(r['changed_family_verdict'] for r in selected),
        max_correct_residual=max(r['correct_residual'] for r in selected),
        median_correct_residual=float(np.median([r['correct_residual'] for r in selected])),
        min_margin=min(r['residual_margin'] for r in selected))


def evaluate(args):
    start = time.process_time()
    prior = json.loads(Path(args.c1_evidence).read_text())
    c.p.f.c.require(c.p.f.c.digest(c.__file__) == prior['tool_sha256'], 'C1 source drift')
    for name in ('samples', 'witnesses', 'f1_evidence', 'f2_evidence'):
        c.p.f.c.require(c.p.f.c.digest(getattr(args, name)) == prior['input_sha256'][name], 'prior input drift: '+name)
    control, _, _ = c.evaluate(SimpleNamespace(samples=args.samples, witnesses=args.witnesses,
        f1_evidence=args.f1_evidence, f2_evidence=args.f2_evidence, source_commit=prior['source_commit']))
    c.p.f.c.require(control['rows'] == prior['rows'] and control['previous_f2_rows_identical'] == 256 and
                    control['previous_f1_rows_identical'] == 8, 'original C1/F2/F1 rows drift')
    original_rows = {(r['fixture'], r['generating_family'], r['realization']): r for r in prior['rows']}
    examples, seen = [], set()
    for example in json.loads(Path(args.witnesses).read_text())['exact_six_column_counterexamples']:
        key = json.dumps(example['nonzero_spectrum'], sort_keys=True)
        if key not in seen:
            examples.append(example)
            seen.add(key)
    c.p.f.c.require(len(examples) == 4, 'fixture count drift')
    rows, details, models_info, source_hashes = [], [], [], {}
    max_parseval = control['max_parseval_relative_error']
    max_direct = control['max_direct_scaled_error']
    peak = 0
    independent_errors = []
    for condition in CONDITIONS:
        for fixture, example in enumerate(examples):
            components, models = {}, {}
            for family in ('known', 'pure'):
                _, components[family] = c.p.f.reference(example, family)
                hypothesis, provenance = perturb(components[family], condition, fixture, family)
                models[family], info = c.build_model(hypothesis)
                models_info.append(dict(condition=condition, fixture=fixture, family=family, **info,
                                        column_norms=models[family]['norms'].tolist(), frequency_provenance=provenance))
                max_parseval = max(max_parseval, info['max_parseval_relative_error'])
                max_direct = max(max_direct, info['max_direct_scaled_error'])
                if condition == 'minus-quarter-hz' and fixture == 0 and family == 'known':
                    tracemalloc.start()
                    repeated, repeated_info = c.build_model(hypothesis)
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    c.p.f.c.require(info == repeated_info and np.array_equal(models[family]['inverse'], repeated['inverse']),
                                    'perturbed matrix replay mismatch')
            for family in ('known', 'pure'):
                other = 'pure' if family == 'known' else 'known'
                for realization in range(32):
                    angles, hashes = c.phases(fixture, family, realization, len(components[family]))
                    pcm, relative, absolute = c.p.observation(components[family], angles)
                    original = original_rows[(fixture, family, realization)]
                    c.p.f.c.require(hashes == original['phase_sha256'] and angles.tolist() == original['phases_radians']
                                    and relative == original['rounding_relative_error'] and
                                    absolute == original['rounding_max_absolute_error'], 'frozen source/phase drift')
                    source_hash = hashlib.sha256(pcm.tobytes()).hexdigest()
                    source_id = (fixture, family, realization)
                    if condition == 'exact':
                        source_hashes[source_id] = source_hash
                    else:
                        c.p.f.c.require(source_hash == source_hashes[source_id], 'PCM changed with hypothesis')
                    _, _, parseval, direct = c.p.f.checked_power(pcm)
                    max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
                    vector = c.real_vector(np.fft.rfft(pcm.astype(float)))
                    correct = c.fit(vector, models[family], verify=realization == 0)
                    wrong = c.fit(vector, models[other], verify=realization == 0)
                    dcorrect, dwrong = correct['normalized_squared_residual'], wrong['normalized_squared_residual']
                    for fit_result in (correct, wrong):
                        if fit_result['independent_prediction_discrepancy'] is not None:
                            independent_errors.append(fit_result['independent_prediction_discrepancy'])
                    if condition == 'exact':
                        c.p.f.c.require(dcorrect == original['correct_residual'] and dwrong == original['wrong_residual'],
                                        'exact C1 fit residual drift')
                    verdict = family if dcorrect < dwrong else other if dwrong < dcorrect else 'tie'
                    row = dict(condition=condition, fixture=fixture, representative_id=example['id'], generating_family=family,
                        realization=realization, phase_sha256=hashes, source_pcm_sha256=source_hash,
                        correct_residual=dcorrect, wrong_residual=dwrong, residual_margin=dwrong-dcorrect,
                        selected_family=verdict, changed_family_verdict=verdict != family,
                        rounding_relative_error=relative, rounding_max_absolute_error=absolute,
                        **gates(dcorrect, dwrong, exact=condition == 'exact'))
                    rows.append(row)
                    details.append(dict(**row, correct_fit=correct, wrong_fit=wrong))
    c.p.f.c.require(len(rows) == 1280 and len(models_info) == 40 and len(source_hashes) == 256, 'incomplete C2 matrix')
    groups = [group_rows(rows, condition, fixture, family) for condition in CONDITIONS
              for fixture in range(4) for family in ('known', 'pure')]
    perturbed = [r for r in rows if r['condition'] != 'exact']
    passed = all(r['screen_pass'] for r in perturbed)
    totals = []
    for condition in CONDITIONS:
        selected = [r for r in groups if r['condition'] == condition]
        totals.append(dict(condition=condition,
            **{key: sum(r[key] for r in selected) for key in ('count', 'pass_count', 'ranking_failures', 'rank_reversals',
                                                              'margin_ties', 'reconstruction_failures', 'changed_family_verdicts')},
            max_correct_residual=max(r['max_correct_residual'] for r in selected),
            min_margin=min(r['min_margin'] for r in selected)))
    elapsed = time.process_time()-start
    c.p.f.c.require(elapsed <= 120, 'host process CPU limit exceeded')
    summary = dict(format='apta-key-frequency-uncertainty-c2-result-1', source_commit=args.source_commit,
        baseline_commit='8ae4e4ec8a4b9c713ea69653fd2e6e98ab5bb7c6', acceptance_claim=False, corpus_access=False,
        candidate_retained=False, frequency_estimator=False, production_cpu_ram_state_delta=0,
        decision='finite-frequency-error-screen-passed-only' if passed else 'fixed-frequency-error-screen-rejected',
        all_perturbed_observations_pass=passed, perturbed_observations=1024,
        perturbed_pass_count=sum(r['screen_pass'] for r in perturbed), observations=1280,
        original_c1_rows_identical=256, original_f2_rows_identical=256, original_f1_rows_identical=8,
        exact_condition_residuals_identical=256, identical_source_pcm_across_conditions=True,
        input_sha256={name: c.p.f.c.digest(getattr(args, name)) for name in
                      ('samples', 'witnesses', 'f1_evidence', 'f2_evidence', 'c1_evidence')},
        tool_sha256=c.p.f.c.digest(__file__), c1_tool_sha256=c.p.f.c.digest(c.__file__),
        environment=dict(numpy=np.__version__, python=platform.python_version(), platform=platform.platform()),
        max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct,
        max_independent_prediction_discrepancy=max(independent_errors),
        condition_totals=totals, groups=groups, models=models_info, rows=rows)
    resource = dict(process_cpu_seconds=elapsed, cpu_limit_seconds=120, cpu_gate_pass=True,
        largest_matrix_and_inverse_bytes=max(r['matrix_and_inverse_bytes'] for r in models_info),
        numeric_storage_limit_bytes=1048576, numeric_storage_gate_pass=True,
        first_perturbed_matrix_incremental_traced_peak_bytes=peak,
        traced_peak_excludes_other_models_and_reports=True, production_cpu_ram_state_delta=0)
    return summary, dict(rows=details), resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('samples', 'witnesses', 'f1-evidence', 'f2-evidence', 'c1-evidence', 'source-commit', 'output-prefix'):
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args()
    paths = [Path(args.output_prefix+suffix+'.json') for suffix in ('', '-detail', '-resource')]
    c.p.f.c.require(all(not path.exists() for path in paths), 'refusing overwrite')
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    print(json.dumps(dict(decision=values[0]['decision'], totals=values[0]['condition_totals'], resource=values[2])))


if __name__ == '__main__':
    main()
