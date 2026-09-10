#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate the fixed binary-gain probe and summarize synthetic decisions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from apta_key_mode_diagnostic_summary import load_report
from apta_key_contrast_summary import inspect_trace, scores, summarize_rows, require

SHIFTS = (-4, -2, 0, 1)
BASELINES = {False: '384bfcda5634861d122b3ff0f9c1f0262560364239d72de953ba653e7651f6d6',
             True: '72c305af710f37b78cabb79377403453c286336b320815cbc7840b352c2381ce'}


def float_bits(value):
    return struct.pack('<f', value)


def assert_scaled(before, after, shift):
    require(len(before) == len(after), 'scaling vector shape')
    require(all(math.isfinite(a) and math.isfinite(b) and a >= 0 and b >= 0 and
                float_bits(math.ldexp(a, 2 * shift)) == float_bits(b)
                for a, b in zip(before, after)), 'raw energy gain-squared mismatch')


def verdict(row):
    return row['selected_tonic'], row['selected_mode']


def raw_verdict(vector):
    values = scores(vector)
    return max(range(24), key=lambda i: values[i])


def validate_rows(rows, baseline, band, shift):
    require(type(shift) is int and shift in SHIFTS, 'unregistered gain')
    require(len(rows) == len(baseline) == 720, 'row coverage')
    pcm = 0
    for row, base in zip(rows, baseline):
        identity = ('kind', 'condition', 'stimulus_tonic', 'stimulus_mode', 'window', 'completed_windows')
        require(all(row[k] == base[k] for k in identity), 'stimulus order or identity changed')
        if not row['kind'].startswith('pcm_'):
            require(row == base, 'ideal vector changed')
        elif row['kind'] == 'pcm_cumulative':
            inspect_trace(row, 3 if band else 1)
            b, r = base['contrast'], row['contrast']
            for first, second in zip(b['raw_energy_by_variant'], r['raw_energy_by_variant']):
                assert_scaled(first, second, shift)
            assert_scaled(b['raw_folded'], r['raw_folded'], shift)
            require(raw_verdict(b['raw_folded']) == raw_verdict(r['raw_folded']), 'raw argmax changed')
            pcm += 1
        else:
            require('contrast' not in row, 'unexpected window trace')
        if shift == 0:
            require(row == base, 'gain-one baseline changed')
    require(pcm == 288, 'observed window count')


def read_gain(path, baseline_rows, baseline_meta, band, shift):
    rows, digest = load_report(path, band, 'apta-key-gain-diagnostic-1')
    meta = json.loads(path.read_bytes())
    require(type(meta.get('gain_shift')) is int and meta['gain_shift'] == shift, 'gain metadata mismatch')
    require(meta.get('gain_reversal_exact_samples') == 13824000, 'sample coverage mismatch')
    peak = meta.get('scaled_sample_peak')
    require(type(peak) in (int, float) and math.isfinite(peak) and 0 < peak <= .94, 'sample peak/clipping')
    require(all(meta[k] == baseline_meta[k] for k in ('observer_scratch_bytes', 'session_bytes')), 'resource metadata changed')
    validate_rows(rows, baseline_rows, band, shift)
    return rows, digest, peak


def comparisons(rows, base):
    pairs = [(a, b) for a, b in zip(rows, base) if a['kind'].startswith('pcm_')]
    final = [(a, b) for a, b in pairs if a['kind'] == 'pcm_cumulative' and a['window'] == 4]
    return dict(pcm_rows=len(pairs), changed_pcm_verdicts=sum(verdict(a) != verdict(b) for a, b in pairs),
        final_rows=len(final), changed_final_verdicts=sum(verdict(a) != verdict(b) for a, b in final),
        final_mode_only_changes=sum(a['selected_tonic'] == b['selected_tonic'] and a['selected_mode'] != b['selected_mode'] for a, b in final),
        final_tonic_changes=sum(a['selected_tonic'] != b['selected_tonic'] for a, b in final),
        final_high_confidence_outputs=sum(a['confidence'] >= 75 for a, _ in final),
        final_high_confidence_stimulus_mismatches=sum(a['confidence'] >= 75 and verdict(a) != (a['stimulus_tonic'], a['stimulus_mode']) for a, _ in final))


def summarize(reports, baseline_paths):
    result = dict(format='apta-key-gain-summary-1', evidence_level='synthetic-diagnostic',
                  acceptance_claim=False, candidate_promoted=False, corpus_access=False,
                  shifts=list(SHIFTS), builds={}, confidence_safety='not-assessed-for-real-music')
    for band, name in ((False, 'default'), (True, 'band')):
        path = baseline_paths[name]
        require(hashlib.sha256(path.read_bytes()).hexdigest() == BASELINES[band], 'frozen contrast hash mismatch')
        baseline_rows, _ = load_report(path, band, 'apta-key-contrast-diagnostic-1')
        meta = json.loads(path.read_bytes())
        build = dict(baseline_sha256=BASELINES[band], gains=[])
        for shift in SHIFTS:
            rows, digest, peak = read_gain(reports / f'{name}-shift{shift}.json', baseline_rows, meta, band, shift)
            build['gains'].append(dict(gain_shift=shift, gain=math.ldexp(1., shift), report_sha256=digest,
                scaled_sample_peak=peak, exact_reversible_samples=13824000,
                exact_scaled_energy_windows=288, raw_argmax_unchanged_windows=288,
                comparisons=comparisons(rows, baseline_rows), groups=summarize_rows(rows)))
        result['builds'][name] = build
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('reports', 'baseline-default', 'baseline-band', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'output exists')
    report = summarize(args.reports, {'default':args.baseline_default, 'band':args.baseline_band})
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
