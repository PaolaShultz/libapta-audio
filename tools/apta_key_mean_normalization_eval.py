#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Apply frozen synthetic gates to the one mean-energy key candidate."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from apta_key_mode_diagnostic_summary import load_report
from apta_key_gain_summary import SHIFTS, assert_scaled, verdict
from apta_key_contrast_summary import require, vector, summarize_rows

BASELINE = 'bcb0ca233387ca77ac8c290fa6f461075684673d693713b5b2319226e663bc66'


def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]


def expected_compression(raw):
    raw = vector(raw, 36)
    peak = max(raw)
    scaled_sum = 0.
    for energy in raw:
        scaled_sum = f32(scaled_sum + f32(f32(energy) / f32(peak)))
    factor = f32(36. / scaled_sum)
    return [math.log(f32(1. + f32(f32(f32(e) / f32(peak)) * factor))) for e in raw]


def validate_rows(rows, baseline, shift):
    require(len(rows) == len(baseline) == 720, 'row coverage')
    for row, base in zip(rows, baseline):
        fields = ('kind','condition','stimulus_tonic','stimulus_mode','window','completed_windows')
        require(all(row[k] == base[k] for k in fields), 'stimulus changed')
        if not row['kind'].startswith('pcm_'):
            require(row == base, 'ideal profile/triad changed')
        elif row['kind'] == 'pcm_cumulative':
            c, b = row['contrast'], base['contrast']
            require(c['variants'] == 1 and c['observations'] == 36 and
                    c['native_cumulative_bit_identical'] is True, 'observer coverage')
            require(len(c['raw_energy_by_variant']) == len(c['compressed_by_variant']) == 1, 'variant coverage')
            raw = vector(c['raw_energy_by_variant'][0],36)
            compressed = vector(c['compressed_by_variant'][0],36)
            assert_scaled(b['raw_energy_by_variant'][0],raw,shift)
            expected = expected_compression(raw)
            require(all(math.isclose(x,y,rel_tol=3e-6,abs_tol=3e-7) for x,y in zip(compressed,expected)), 'normalization formula mismatch')
            for field, values in (('raw_folded', raw), ('compressed_window', compressed)):
                actual=vector(c[field],12)
                folded=[sum(values[p+12*o] for o in range(3)) for p in range(12)]
                require(all(math.isclose(x,y,rel_tol=3e-6,abs_tol=3e-7) for x,y in zip(actual,folded)), 'fold mismatch')
        else:
            require('contrast' not in row, 'unexpected trace')


def gain_identity(rows):
    # Raw energies/folded raw vectors must scale; all normalized evidence and
    # native decisions must remain identical, including quantized confidence.
    return [{**{k:v for k,v in row.items() if k!='contrast'},
             **({'contrast':{k:v for k,v in row['contrast'].items()
                             if k not in ('raw_energy_by_variant','raw_folded')}} if 'contrast' in row else {})}
            for row in rows]


def final_metrics(rows, baseline):
    pairs=[(r,b) for r,b in zip(rows,baseline) if r['kind']=='pcm_cumulative' and r['window']==4]
    require(len(pairs)==72,'final coverage')
    correct=lambda r:verdict(r)==(r['stimulus_tonic'],r['stimulus_mode'])
    fixes=sum(correct(r) and not correct(b) for r,b in pairs)
    breaks=sum(not correct(r) and correct(b) for r,b in pairs)
    newly_unsafe=sum(not correct(r) and r['confidence']>=75 and
                     not (not correct(b) and b['confidence']>=75) for r,b in pairs)
    by_condition=[]
    for condition in range(3):
        groups={}
        for mode in range(2):
            selected=[(r,b) for r,b in pairs if r['condition']==condition and r['stimulus_mode']==mode]
            require(len(selected)==12,'condition/mode coverage')
            groups['major' if mode==0 else 'minor']=dict(candidate=sum(correct(r) for r,_ in selected),baseline=sum(correct(b) for _,b in selected))
        by_condition.append(dict(condition=condition,**groups))
    gates=dict(clean_major=by_condition[0]['major']['candidate']>=9,
               clean_minor=by_condition[0]['minor']['candidate']>=11,
               fixes_exceed_breaks=fixes>breaks,
               minor_preserved_each_condition=all(g['minor']['candidate']>=g['minor']['baseline'] for g in by_condition),
               no_new_high_confidence_mismatches=newly_unsafe==0)
    return dict(final_count=72,fixes=fixes,breaks=breaks,
                changed_verdicts=sum(verdict(r)!=verdict(b) for r,b in pairs),
                high_confidence_finals=sum(r['confidence']>=75 for r,_ in pairs),
                high_confidence_mismatches=sum(not correct(r) and r['confidence']>=75 for r,_ in pairs),
                new_high_confidence_mismatches=newly_unsafe,
                by_condition=by_condition,gates=gates)


def evaluate(directory, baseline_path):
    require(hashlib.sha256(baseline_path.read_bytes()).hexdigest()==BASELINE,'frozen baseline hash mismatch')
    base,_=load_report(baseline_path,False,'apta-key-gain-diagnostic-1')
    all_rows={}; reports={}; summaries={}; metrics={}
    for shift in SHIFTS:
        path=directory/f'candidate-shift{shift}.json'
        rows,digest=load_report(path,False,'apta-key-mean-normalized-gain-1')
        meta=json.loads(path.read_bytes())
        require(type(meta['gain_shift']) is int and meta['gain_shift']==shift and
                meta['gain_reversal_exact_samples']==13824000,'gain/sample metadata')
        require(0<meta['scaled_sample_peak']<=.94 and meta['session_bytes']==11824 and
                meta['observer_scratch_bytes']==476,'peak/layout metadata')
        validate_rows(rows,base,shift)
        all_rows[shift]=rows; reports[str(shift)]=digest
        metrics[str(shift)]=final_metrics(rows,base)
        summaries[str(shift)]=summarize_rows(rows)
    invariant=all(gain_identity(r)==gain_identity(all_rows[0]) for r in all_rows.values())
    gates={'gain_invariant':invariant,**{key:all(m['gates'][key] for m in metrics.values()) for key in metrics['0']['gates']}}
    return dict(format='apta-key-mean-normalization-evaluation-1',evidence_level='synthetic-candidate-screen',
                acceptance_claim=False,candidate_promoted=False,holdout_eligible=False,corpus_access=False,
                synthetic_gates_passed=all(gates.values()),gates=gates,
                baseline_sha256=BASELINE,report_sha256=reports,metrics=metrics,groups=summaries,
                independent_transfer='not-executed',resource_gate='not-assessed-by-this-evaluator')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('reports','baseline','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args(); require(not args.output.exists(),'output exists')
    result=evaluate(args.reports,args.baseline)
    with args.output.open('x',encoding='utf-8',newline='\n') as out: out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(gates=result['gates'],gain_one_metrics=result['metrics']['0']),sort_keys=True))


if __name__=='__main__': main()
