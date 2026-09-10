#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Frozen development-only MTG transfer wrapper; private artifacts stay local."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import wave

import apta_1_1_giantsteps_key_validation as base

SEED = 'apta-1.1-mtg-mean-key-v1'
OLD_SEAL = '1fadadc5e5df343558eeb476aa2346fc688bea6ebbc98a09a996a649be3b0146'
FORMAT = 'apta-1.1-mtg-mean-key-development-1'
EPOCH = '1788998400'
OLD_SELECT = base.select_candidates
ERROR = base.ValidationError
SHA = base.sha256_file
ROOT = Path(__file__).resolve().parents[1]
I1_EVIDENCE = ROOT / 'evidence/1.1/key-mean-cost-i1-20260910.json'


def require(condition, message):
    if not condition:
        raise ERROR(message)


def read(path):
    return json.loads(path.read_bytes())


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def fresh(path):
    require(not path.exists(), 'output already exists')


def choose(inventory, original_md5):
    old = OLD_SELECT(inventory)
    require(base.selection_sha256(old) == OLD_SEAL, 'prior selection seal changed')
    excluded = [r for part in old.values() for r in part]
    ids = {r.source_id for r in excluded}
    hashes = {r.transport_md5 for r in excluded} | set(original_md5)
    remaining = [r for r in inventory if r.source_id not in ids]
    require(len(remaining) == 1015, 'remaining inventory changed')
    selected = []
    for name in base.KEY_NAMES:
        group = sorted((r for r in remaining if r.key_name == name and r.transport_md5 not in hashes),
                       key=lambda r: (hashlib.sha256(f'{SEED}:track:{r.source_id}'.encode()).hexdigest(), r.source_id))
        require(len(group) >= 4, 'class quota unavailable after exclusions')
        selected.extend(group[:4])
    selected.sort(key=lambda r: (r.key_tonic, r.key_mode, r.source_id))
    require(len({r.source_id for r in selected}) == len({r.transport_md5 for r in selected}) == 96,
            'duplicate selected transport or ID')
    return selected


def preflight(mtg, original):
    for root in (mtg, original):
        status = subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=no'], text=True)
        require(not status, 'dataset tracked content is dirty')
    inventory = base.inventory(mtg, original)
    selected = choose(inventory, [base._read_transport_md5(p) for p in (original/'md5').glob('*.md5')])
    seal = base.selection_sha256(dict(development=selected, holdout=[]))
    summary = dict(format=FORMAT, operation='preflight', acceptance_claim=False, holdout_eligible=False,
                   selection_seed=SEED, selection_sha256=seal, prior_selection_sha256=OLD_SEAL,
                   inventory_count=1159, remaining_after_id_exclusions=1015, track_count=96,
                   mode_counts={m: sum(r.key_mode == m for r in selected) for m in ('major','minor')},
                   per_class_count=4, reserved_holdout_count=48, spent_mtg_count=96,
                   source_id_overlap=0, excluded_transport_overlap=0,
                   mtg_revision=base.MTG_REVISION, original_revision=base.ORIGINAL_REVISION)
    return selected, summary


@contextmanager
def transport(selected=None):
    def selector(_rows):
        require(selected is not None, 'selection required')
        return dict(development=selected, holdout=[])
    changes = dict(FORMAT=FORMAT, REPORT_FORMAT=FORMAT+'-report', select_candidates=selector,
                   SELECTION_SEED=SEED)
    saved = {k:getattr(base,k) for k in changes}
    try:
        for k,v in changes.items(): setattr(base,k,v)
        yield
    finally:
        for k,v in saved.items(): setattr(base,k,v)


def fingerprint(path):
    with wave.open(str(path), 'rb') as stream:
        geometry = [stream.getframerate(),stream.getnchannels(),stream.getsampwidth(),stream.getnframes()]
        digest = hashlib.sha256(json.dumps(geometry,separators=(',',':')).encode())
        while block := stream.readframes(65536): digest.update(block)
    return dict(wav_sha256=SHA(path),pcm_sha256=digest.hexdigest(),geometry=geometry)


def make_exclusions(catalog, output):
    fresh(output)
    groups = read(catalog)
    expected = dict(mtg=96,original=96,fmak1=96,fmak2=96,fmak3=72,asap=40,final_dj=60)
    require(set(groups)==set(expected),'exclusion groups changed')
    records=[]
    for group,count in expected.items():
        require(len(groups[group])==count, 'exclusion group count changed')
        for path in groups[group]: records.append(dict(group=group,**fingerprint(Path(path))))
    value=dict(format=FORMAT+'-exclusions',catalog_sha256=SHA(catalog),counts=expected,records=records)
    write_new(output,value)
    return dict(counts=expected,record_count=len(records),exclusions_sha256=SHA(output))


def validated_prepared(prepared, seal, exclusions):
    with transport(): manifest,labels=base.load_prepared(prepared)
    require(manifest['split']=='development' and manifest['selection_seed']==SEED,'development-only split required')
    require(manifest['selection_sha256']==read(seal)['selection_sha256'],'selection seal mismatch')
    require(SHA(prepared/'private-sources.json')==manifest['private_sources_sha256'],'private mapping changed')
    sources=read(prepared/'private-sources.json')
    require(len(sources)==96 and len({s['track'] for s in sources})==96,'mapping coverage')
    source_by_id={s['track']:s for s in sources}
    exclusion=read(exclusions)
    require(exclusion['format']==FORMAT+'-exclusions' and len(exclusion['records'])==556,'exclusion inventory changed')
    hashes={r['wav_sha256'] for r in exclusion['records']}; pcm={r['pcm_sha256'] for r in exclusion['records']}
    observed=[]
    for label in labels:
        track=label['track']; require(track in source_by_id,'mapping IDs mismatch')
        record=fingerprint(prepared/'audio'/f'{track}.wav')
        require(record['wav_sha256']==source_by_id[track]['canonical_sha256'],'canonical SHA mismatch')
        require(track=='track-'+record['wav_sha256'][:24],'opaque identity mismatch')
        require(record['geometry'][:3]==[48000,2,2] and record['geometry'][3]>0,'canonical geometry')
        require(record['wav_sha256'] not in hashes and record['pcm_sha256'] not in pcm,'spent audio overlap')
        observed.append(record)
    require(len({r['pcm_sha256'] for r in observed})==96,'duplicate selected PCM')
    require(all(sum(l['key_tonic']==t and l['key_mode']==m for l in labels)==4 for t in range(12) for m in ('major','minor')),'label class counts')
    audit=dict(format=FORMAT+'-audio-audit',count=96,excluded_records=556,wav_overlap=0,pcm_overlap=0,
               exclusions_sha256=SHA(exclusions),manifest_sha256=SHA(prepared/'manifest.json'),selection_seal_sha256=SHA(seal))
    return manifest, labels, audit


def prepare(args):
    selected,summary=preflight(args.mtg,args.original)
    require(summary==read(args.seal),'preflight seal changed')
    # Canonical preparation supports resuming transport failures, never a finalized set.
    with transport(selected):
        base.prepare(args.mtg,args.original,args.output,'development',args.ffmpeg,args.curl,'2026-09-10T00:00:00Z',False,None)
    _,_,audit=validated_prepared(args.output,args.seal,args.exclusions)
    write_new(args.output/'audio-audit.json',audit)
    return audit


def run(args):
    fresh(args.output)
    _,_,audit=validated_prepared(args.prepared,args.seal,args.exclusions)
    require(audit==read(args.prepared/'audio-audit.json'),'prepared audit changed')
    expected=read(I1_EVIDENCE)['binary_sha256'][args.flavor]['tools/apta-analyze']
    require(SHA(args.analyzer)==expected,'analyzer differs from frozen I1 detector')
    require(os.environ.get('SOURCE_DATE_EPOCH')==EPOCH,'epoch differs from protocol')
    with transport(): result=base.run_analysis(args.prepared,args.analyzer,args.output,args.revision)
    return dict(track_count=result['track_count'],complete=result['complete'],run_sha256=SHA(args.output/'run.json'))


def evaluate(args):
    fresh(args.output)
    _,labels,audit=validated_prepared(args.prepared,args.seal,args.exclusions)
    require(audit==read(args.prepared/'audio-audit.json'),'audio audit mismatch')
    run_record=read(args.run/'run.json')
    require(run_record['complete'] is True and run_record['track_count']==96,'incomplete run')
    require(run_record['source_date_epoch']==int(EPOCH) and run_record['source_revision']==args.revision,'run provenance')
    require(run_record['analyzer_sha256']==read(I1_EVIDENCE)['binary_sha256'][args.flavor]['tools/apta-analyze'],'run analyzer')
    require(run_record['manifest_sha256']==SHA(args.prepared/'manifest.json') and run_record['mapping_sha256']==SHA(args.run/'mapping.csv'),'run manifest/mapping changed')
    import apta_1_1_export_acceptance_results as exporter
    mappings=exporter.read_mapping(args.run/'mapping.csv')
    hashes={r['track']:r['apta_sha256'] for r in run_record['outputs']}
    require(len(hashes)==len(run_record['outputs'])==96 and set(hashes)=={l['track'] for l in labels},'output coverage')
    require(len(mappings)==96 and all(SHA(p)==hashes[t] for t,p in mappings),'output hash mismatch')
    with transport(): result=base.evaluate(args.prepared,args.inspector,args.run/'mapping.csv',args.output)
    return result['overall']


def compare(baseline,candidate):
    require(len(baseline['tracks'])==len(candidate['tracks'])==96,'report coverage')
    b={r['track']:r for r in baseline['tracks']}; c={r['track']:r for r in candidate['tracks']}
    require(set(b)==set(c) and len(b)==96,'report IDs differ')
    require(all(sum(r['expected_tonic']==t and r['expected_mode']==m for r in c.values())==4
                for t in range(12) for m in ('major','minor')),'class coverage')
    for t in b:
        require((b[t]['expected_tonic'],b[t]['expected_mode'])==(c[t]['expected_tonic'],c[t]['expected_mode']),'labels differ')
    modes={m:dict(count=sum(r['expected_mode']==m for r in c.values()),
                  baseline=sum(r['expected_mode']==m and r['key_correct'] for r in b.values()),
                  candidate=sum(r['expected_mode']==m and r['key_correct'] for r in c.values())) for m in ('major','minor')}
    require(all(m['count']==48 for m in modes.values()),'mode coverage')
    fixes=sum(not b[t]['key_correct'] and c[t]['key_correct'] for t in b)
    breaks=sum(b[t]['key_correct'] and not c[t]['key_correct'] for t in b)
    unsafe=lambda r:not r['key_correct'] and r['key_confidence']>=75
    new_unsafe=sum(unsafe(c[t]) and not unsafe(b[t]) for t in b)
    high=sum(unsafe(r) for r in c.values())
    correct=sum(r['key_correct'] for r in c.values())
    gates=dict(total_at_least_70_percent=correct>=68,each_mode_at_least_60_percent=all(m['candidate']>=29 for m in modes.values()),
               accuracy_improved=fixes>breaks,fixes_exceed_breaks=fixes>breaks,
               modes_preserved=all(m['candidate']>=m['baseline'] for m in modes.values()),
               no_new_high_confidence_errors=new_unsafe==0,high_confidence_errors_at_most_5_percent=high<=4)
    return dict(format=FORMAT+'-comparison',acceptance_claim=False,holdout_eligible=False,development_gates_passed=all(gates.values()),
                track_count=96,baseline_correct=sum(r['key_correct'] for r in b.values()),candidate_correct=correct,by_mode=modes,
                fixes=fixes,breaks=breaks,changed_verdicts=sum((b[t]['key_tonic'],b[t]['key_mode'])!=(c[t]['key_tonic'],c[t]['key_mode']) for t in b),
                baseline_high_confidence_errors=sum(unsafe(r) for r in b.values()),candidate_high_confidence_errors=high,new_high_confidence_errors=new_unsafe,
                gates=gates,error_families=dict(baseline=baseline['error_families'],candidate=candidate['error_families']))


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='command',required=True)
    for command in ('preflight','prepare','exclusions','run','evaluate','compare'):
        p=sub.add_parser(command); p.add_argument('--output',type=Path,required=True)
        if command in ('preflight','prepare'):
            for k in ('mtg','original'):p.add_argument('--'+k,type=Path,required=True)
        if command in ('prepare','run','evaluate'):
            for k in ('seal','exclusions'):p.add_argument('--'+k,type=Path,required=True)
        if command in ('run','evaluate'):
            p.add_argument('--prepared',type=Path,required=True);p.add_argument('--revision',required=True)
            p.add_argument('--flavor',choices=('default','candidate'),required=True)
        if command=='prepare':p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--curl',default='curl')
        if command=='exclusions':p.add_argument('--catalog',type=Path,required=True)
        if command=='run':p.add_argument('--analyzer',type=Path,required=True)
        if command=='evaluate':p.add_argument('--inspector',type=Path,required=True);p.add_argument('--run',type=Path,required=True)
        if command=='compare':p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='preflight':
        _,result=preflight(args.mtg,args.original);write_new(args.output,result)
    elif args.command=='exclusions':result=make_exclusions(args.catalog,args.output)
    elif args.command=='prepare':result=prepare(args)
    elif args.command=='run':result=run(args)
    elif args.command=='evaluate':result=evaluate(args)
    else:
        with transport():b=base._load_report(args.baseline);c=base._load_report(args.candidate)
        result=compare(b,c);result['report_sha256']=dict(baseline=SHA(args.baseline),candidate=SHA(args.candidate))
        write_new(args.output,result)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__': main()
