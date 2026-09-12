#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""C3: unchanged C2 observations/conditions, unchanged O1 model and abstention."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import apta_key_frequency_uncertainty as u
import apta_key_observability as o

c = u.c
require = o.require
INPUTS = ('samples', 'witnesses', 'f1_evidence', 'f2_evidence', 'c1_evidence')


def decision(correct, wrong, family, exact=False):
    require(family in ('known', 'pure'), 'invalid family')
    for value in (correct, wrong):
        require(value is None or (np.isfinite(value) and value >= 0), 'invalid residual')
    available = correct is not None and wrong is not None
    margin = wrong-correct if available else None
    ranking = wrong > correct+1e-6 if available else None
    reconstruction = correct <= (1e-10 if exact else 0.10) if correct is not None else None
    other = 'pure' if family == 'known' else 'known'
    selected = (family if correct < wrong else other if wrong < correct else 'tie') if available else None
    return dict(correct_residual=correct, wrong_residual=wrong, residual_margin=margin,
                discrimination_pass=ranking, reconstruction_pass=reconstruction,
                screen_pass=available and ranking and reconstruction, selected_family=selected,
                abstained=not available, correct_abstained=correct is None, alternative_abstained=wrong is None)


def aggregate(rows):
    require(len(rows) > 0, 'empty group')
    measured = [r for r in rows if not r['abstained']]
    correct = [r['correct_residual'] for r in rows if r['correct_residual'] is not None]
    return dict(count=len(rows), pass_count=sum(r['screen_pass'] for r in rows),
        combined_failures=sum(not r['screen_pass'] for r in rows),
        abstentions=sum(r['abstained'] for r in rows),
        correct_abstentions=sum(r['correct_abstained'] for r in rows),
        alternative_abstentions=sum(r['alternative_abstained'] for r in rows),
        both_abstentions=sum(r['correct_abstained'] and r['alternative_abstained'] for r in rows),
        measured_rankings=len(measured), ranking_failures=sum(r['discrimination_pass'] is False for r in rows),
        rank_reversals=sum(r['wrong_residual'] < r['correct_residual'] for r in measured),
        margin_ties=sum(abs(r['residual_margin']) <= 1e-6 for r in measured),
        reconstruction_failures=sum(r['reconstruction_pass'] is False for r in rows),
        reconstruction_unavailable=sum(r['reconstruction_pass'] is None for r in rows),
        ranking_fixes=sum(r['discrimination_pass'] is True and not r['c2_discrimination_pass'] for r in rows),
        ranking_breaks=sum(r['discrimination_pass'] is not True and r['c2_discrimination_pass'] for r in rows),
        combined_fixes=sum(r['screen_pass'] and not r['c2_screen_pass'] for r in rows),
        combined_breaks=sum(not r['screen_pass'] and r['c2_screen_pass'] for r in rows),
        changed_family_verdicts=sum(r['selected_family'] != r['c2_selected_family'] for r in rows),
        max_correct_residual=max(correct, default=None),
        min_margin=min((r['residual_margin'] for r in measured), default=None))


def validate_source(pcm, hashes, relative, absolute, prior):
    digest = hashlib.sha256(pcm.tobytes()).hexdigest()
    require(digest == prior['source_pcm_sha256'] and hashes == prior['phase_sha256'] and
            relative == prior['rounding_relative_error'] and absolute == prior['rounding_max_absolute_error'],
            'C2 source/phase/rounding drift')
    return digest


def evaluate(args):
    start = time.process_time()
    old = json.loads(Path(args.c2_evidence).read_text())
    o1 = json.loads(Path(args.o1_evidence).read_text())
    require(c.p.f.c.digest(u.__file__) == old['tool_sha256'], 'C2 source drift')
    for name in INPUTS:
        require(c.p.f.c.digest(getattr(args, name)) == old['input_sha256'][name], 'input drift: '+name)
    for name, digest in o1['source_sha256'].items():
        require(c.p.f.c.digest(Path(o.__file__).parent/name) == digest, 'O1 dependency drift: '+name)
    o1_control = o.evaluate(o1['source_commit'])
    require(o1_control['rows'] == o1['rows'], 'O1 numerical bank drift')
    control, _, _ = u.evaluate(SimpleNamespace(**{name: getattr(args, name) for name in INPUTS},
                                               source_commit=old['source_commit']))
    require(control['rows'] == old['rows'], 'C2 control drift')
    old_rows = {(r['condition'], r['fixture'], r['generating_family'], r['realization']): r for r in old['rows']}
    require(len(old_rows) == 1280, 'C2 row coverage')
    examples, seen = [], set()
    for example in json.loads(Path(args.witnesses).read_text())['exact_six_column_counterexamples']:
        key = json.dumps(example['nonzero_spectrum'], sort_keys=True)
        if key not in seen:
            examples.append(example)
            seen.add(key)
    require(len(examples) == 4, 'fixture count')
    components, models, model_info = {}, {}, []
    max_column_error = 0.
    # Validate every supplied model before producing any C3 family scores.
    for fixture, example in enumerate(examples):
        for family in ('known', 'pure'):
            _, source = c.p.f.reference(example, family)
            components[fixture, family] = source
            for condition in u.CONDITIONS:
                hypothesis, provenance = u.perturb(source, condition, fixture, family)
                frequencies = [v['frequency_hz'] for v in hypothesis]
                model, info = o.build_model(frequencies)
                errors = []
                for index, frequency in enumerate(frequencies):
                    raw = o.raw_pair(frequency)
                    pair_errors = np.linalg.norm(raw-o.independent_pair(frequency), axis=0)/o.SCALE
                    require(max(pair_errors) <= 1e-10, 'raw analytic column gate')
                    if index in info['structural_zero_components']:
                        require(np.count_nonzero(raw) == 0, 'omitted nonzero column')
                    errors.append(pair_errors.tolist())
                    max_column_error = max(max_column_error, float(max(pair_errors)))
                condition_number = float(model['singular'][0]/model['singular'][-1]) if model is not None else None
                info.update(condition=condition, fixture=fixture, family=family, frequency_provenance=provenance,
                            analytic_fft_scaled_errors=errors, condition_number=condition_number)
                models[condition, fixture, family] = (model, info)
                model_info.append(info)
    rows, details, independent_errors, amplitudes = [], [], [], []
    nulls = 0
    max_exact_delta = 0.
    for condition in u.CONDITIONS:
        for fixture in range(4):
            for family in ('known', 'pure'):
                other = 'pure' if family == 'known' else 'known'
                model, info = models[condition, fixture, family]
                alternative, alternative_info = models[condition, fixture, other]
                source = components[fixture, family]
                for realization in range(32):
                    prior = old_rows[condition, fixture, family, realization]
                    angles, hashes = c.phases(fixture, family, realization, len(source))
                    pcm, relative, absolute = c.p.observation(source, angles)
                    digest = validate_source(pcm, hashes, relative, absolute, prior)
                    vector = c.real_vector(np.fft.rfft(pcm.astype(float)))
                    correct = o.fit(vector, model) if model is not None else None
                    wrong = o.fit(vector, alternative) if alternative is not None else None
                    dcorrect = correct['normalized_squared_residual'] if correct else None
                    dwrong = wrong['normalized_squared_residual'] if wrong else None
                    result = decision(dcorrect, dwrong, family, condition == 'exact')
                    if condition == 'exact':
                        require(result['screen_pass'], 'exact control scientific veto')
                        delta = max(abs(dcorrect-prior['correct_residual']), abs(dwrong-prior['wrong_residual']))
                        require(delta <= 1e-10, 'exact residual numerical drift')
                        max_exact_delta = max(max_exact_delta, delta)
                    for fit in (correct, wrong):
                        if fit is not None:
                            independent_errors.append(fit['independent_prediction_discrepancy'])
                            values = fit['physical_sine_cosine_coefficients']
                            nulls += sum(v is None for v in values)
                            amplitudes.extend(abs(v) for v in values if v is not None)
                    row = dict(condition=condition, fixture=fixture, generating_family=family, realization=realization,
                        source_pcm_sha256=digest, phase_sha256=hashes,
                        rounding_relative_error=relative, rounding_max_absolute_error=absolute,
                        correct_model_status=info['status'], alternative_model_status=alternative_info['status'],
                        c2_discrimination_pass=prior['discrimination_pass'], c2_screen_pass=prior['screen_pass'],
                        c2_selected_family=prior['selected_family'],
                        correct_residual_delta_from_c2=dcorrect-prior['correct_residual'] if dcorrect is not None else None,
                        wrong_residual_delta_from_c2=dwrong-prior['wrong_residual'] if dwrong is not None else None,
                        **result)
                    rows.append(row)
                    details.append(dict(condition=condition, fixture=fixture, generating_family=family,
                                        realization=realization, correct_fit=correct, wrong_fit=wrong))
    require(len(rows) == 1280 and len(model_info) == 40, 'incomplete C3 screen')
    groups = [dict(condition=condition, fixture=fixture, generating_family=family,
                   **aggregate([r for r in rows if (r['condition'], r['fixture'], r['generating_family']) ==
                               (condition, fixture, family)]))
              for condition in u.CONDITIONS for fixture in range(4) for family in ('known', 'pure')]
    totals = [dict(condition=condition, **aggregate([r for r in rows if r['condition'] == condition]))
              for condition in u.CONDITIONS]
    perturbed = aggregate([r for r in rows if r['condition'] != 'exact'])
    summary = dict(format='apta-key-observable-frequency-c3-result-1', source_commit=args.source_commit,
        baseline_commit='360c0c460d03438dd237cb9d5101109ecc5a0d2b',
        tool_sha256=c.p.f.c.digest(__file__), input_sha256={name:c.p.f.c.digest(getattr(args, name))
            for name in INPUTS+('c2_evidence', 'o1_evidence')},
        o1_tool_sha256=c.p.f.c.digest(o.__file__), c2_tool_sha256=c.p.f.c.digest(u.__file__),
        original_o1_rows_identical=24, original_c2_rows_identical=1280,
        original_c1_rows_identical=control['original_c1_rows_identical'],
        original_f2_rows_identical=control['original_f2_rows_identical'],
        original_f1_rows_identical=control['original_f1_rows_identical'],
        all_source_rows_identical=1280, max_exact_residual_delta=max_exact_delta,
        max_analytic_fft_scaled_error=max_column_error,
        max_independent_prediction_discrepancy=max(independent_errors, default=None),
        max_absolute_physical_coefficient=max(amplitudes, default=None), null_physical_coefficients=nulls,
        decision='finite-screen-passed-only' if perturbed['pass_count'] == 1024 else 'frequency-error-screen-rejected',
        instrument_gates_pass=True, acceptance_claim=False, candidate_retained=False, corpus_access=False,
        frequency_estimator=False, production_cpu_ram_state_delta=0,
        environment=control['environment'], condition_totals=totals, perturbed_totals=perturbed,
        groups=groups, models=model_info, rows=rows)
    elapsed = time.process_time()-start
    require(elapsed <= 120, 'host CPU gate')
    resource = dict(process_cpu_seconds=elapsed, cpu_limit_seconds=120,
                    largest_matrix_and_inverse_bytes=max(r['matrix_and_inverse_bytes'] for r in model_info),
                    matrix_limit_bytes=1048576, production_cpu_ram_state_delta=0)
    return summary, dict(rows=details), resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in INPUTS+('c2_evidence', 'o1_evidence', 'source_commit', 'output_prefix'):
        parser.add_argument('--'+name.replace('_', '-'), required=True)
    args = parser.parse_args()
    require(len(args.source_commit) == 40 and all(v in '0123456789abcdef' for v in args.source_commit), 'invalid revision')
    paths = [Path(args.output_prefix+suffix+'.json') for suffix in ('', '-detail', '-resource')]
    require(all(not p.exists() for p in paths), 'refusing overwrite')
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write('\n')
    print(json.dumps(dict(decision=values[0]['decision'], totals=values[0]['condition_totals'], resource=values[2])))


if __name__ == '__main__':
    main()
