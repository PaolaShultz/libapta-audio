#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""F2 finite phase bank: diagnostic hypotheses only, never a key detector."""
import argparse
import hashlib
import json
import platform
import time
import tracemalloc
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import apta_key_within_cell as f


def phases(fixture, family, realization, count):
    f.c.require(isinstance(fixture, int) and fixture >= 0 and family in ("known", "pure") and
                isinstance(realization, int) and 0 <= realization < 32 and isinstance(count, int) and count > 0,
                "invalid phase coordinates")
    angles, hashes = [], []
    for j in range(count):
        message = f"apta-f2-20260911|{fixture}|{family}|{realization}|{j}".encode("ascii")
        digest = hashlib.sha256(message).digest()
        angles.append(2 * np.pi * (int.from_bytes(digest[:8], "big") / 2**64))
        hashes.append(digest.hex())
    f.c.require(all(np.isfinite(v) and 0 <= v < 2*np.pi for v in angles), "invalid phase value")
    return np.array(angles), hashes


def component_wave(component, phase):
    frequency, amplitude = component["frequency_hz"], component["amplitude"]
    f.c.require(np.isfinite(frequency) and 0 < frequency < 6000 and np.isfinite(amplitude) and amplitude > 0
                and np.isfinite(phase), "invalid component")
    return amplitude * np.sin(2*np.pi*frequency*np.arange(48000)/48000 + phase)


def observation(components, angles):
    f.c.require(len(components) > 0 and len(components) == len(angles), "component/phase length mismatch")
    samples = np.zeros(48000)
    for component, phase in zip(components, angles):
        samples += component_wave(component, phase)
    rounded = f.average_four(samples, np.float32)
    double = f.average_four(samples, np.float64)
    error = rounded.astype(float) - double
    relative = float(np.linalg.norm(error) / max(np.linalg.norm(double), np.finfo(float).tiny))
    absolute = float(np.max(np.abs(error)))
    f.c.require(relative <= 1e-6 and absolute <= 1e-6, "source rounding limit failed")
    return rounded, relative, absolute


def marginal_reference(components):
    f.c.require(len(components) > 0, "empty reference")
    power = np.zeros(6001)
    max_parseval = max_direct = 0.0
    for component in components:
        # Explicit cosine avoids treating sin(x+pi/2) rounding as an identity.
        frequency, amplitude = component["frequency_hz"], component["amplitude"]
        phase = 2*np.pi*frequency*np.arange(48000)/48000
        for wave in (amplitude*np.sin(phase), amplitude*np.cos(phase)):
            p, _, parseval, direct = f.checked_power(f.average_four(wave, np.float64))
            power += 0.5*p
            max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
    f.c.require(np.isfinite(power).all() and (power >= 0).all(), "invalid reference power")
    return power, max_parseval, max_direct


def passes(correct, wrong):
    return wrong > correct + 1e-6


def evaluate(args):
    started = time.process_time()
    prior = json.loads(Path(args.f1_evidence).read_text())
    f.c.require(f.c.digest(f.__file__) == prior["tool_sha256"], "F1 source drift")
    f.c.require(f.c.digest(args.samples) == prior["input_sha256"]["samples"] and
                f.c.digest(args.witnesses) == prior["input_sha256"]["witnesses"], "F1 input drift")
    control, _, _ = f.evaluate(SimpleNamespace(samples=args.samples, witnesses=args.witnesses, source_commit=prior["source_commit"]))
    f.c.require(control["rows"] == prior["rows"], "eight original F1 rows changed")
    public = json.loads(Path(args.witnesses).read_text())
    examples, seen = [], set()
    for example in public["exact_six_column_counterexamples"]:
        key = json.dumps(example["nonzero_spectrum"], sort_keys=True)
        if key not in seen:
            examples.append(example)
            seen.add(key)
    f.c.require(len(examples) == 4, "fixture count mismatch")
    rows, groups, detail, reference_records = [], [], [], []
    max_parseval = control["max_parseval_relative_error"]
    max_direct = control["max_direct_scaled_error"]
    peak = 0
    for fixture, example in enumerate(examples):
        ideal = np.zeros(36)
        for item in example["nonzero_spectrum"]:
            ideal[item["midi"]-48] = item["energy"]
        components, references = {}, {}
        for family in ("known", "pure"):
            _, components[family] = f.reference(example, family)
            power, parseval, direct = marginal_reference(components[family])
            references[family] = power
            max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
            reference_records.append(dict(fixture=fixture, family=family, components=components[family], power=power.tolist()))
            if fixture == 0 and family == "known":
                tracemalloc.start()
                repeated, p, d = marginal_reference(components[family])
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                f.c.require(np.array_equal(power, repeated) and p == parseval and d == direct, "reference replay mismatch")
        for family in ("known", "pure"):
            other = "pure" if family == "known" else "known"
            selected = []
            for realization in range(32):
                angles, hashes = phases(fixture, family, realization, len(components[family]))
                pcm, relative, absolute = observation(components[family], angles)
                power, _, parseval, direct = f.checked_power(pcm)
                max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
                correct, dc = f.fine_distance(power, references[family], ideal)
                wrong, dw = f.fine_distance(power, references[other], ideal)
                row = dict(fixture=fixture, representative_id=example["id"], generating_family=family,
                           realization=realization, phases_radians=angles.tolist(), phase_sha256=hashes,
                           distance_correct=correct, distance_wrong=wrong, signed_margin=wrong-correct,
                           screen_pass=passes(correct, wrong), rounding_relative_error=relative,
                           rounding_max_absolute_error=absolute)
                selected.append(row)
                rows.append(row)
                detail.append(dict(**row, correct_cells=dc, wrong_cells=dw))
            groups.append(dict(fixture=fixture, representative_id=example["id"], generating_family=family,
                               count=len(selected), pass_count=sum(r["screen_pass"] for r in selected),
                               fail_count=sum(not r["screen_pass"] for r in selected),
                               wrong_closer=sum(r["signed_margin"] < 0 for r in selected),
                               min_margin=min(r["signed_margin"] for r in selected),
                               median_margin=float(np.median([r["signed_margin"] for r in selected])),
                               max_correct_distance=max(r["distance_correct"] for r in selected),
                               min_wrong_distance=min(r["distance_wrong"] for r in selected)))
    f.c.require(len(rows) == 256 and len(groups) == 8 and len(reference_records) == 8, "incomplete phase bank")
    passed = all(r["screen_pass"] for r in rows)
    elapsed = time.process_time() - started
    f.c.require(elapsed <= 60, "host analysis CPU limit exceeded")
    summary = dict(format="apta-key-phase-f2-result-1", source_commit=args.source_commit,
                   baseline_commit="ce4a491f414e0d284eca0f43e9ae8b2621e8d0f6", acceptance_claim=False,
                   candidate_retained=False, phase_invariant_proof=False, corpus_access=False,
                   production_cpu_ram_state_delta=0, h1_remains_rejected=True,
                   decision="finite-phase-screen-passed-only" if passed else "phase-marginal-construction-rejected",
                   all_observations_pass=passed, pass_count=sum(r["screen_pass"] for r in rows),
                   fail_count=sum(not r["screen_pass"] for r in rows), observations=256,
                   unique_fixtures=4, phase_realizations_per_family=32, original_f1_rows_identical=8,
                   input_sha256={name: f.c.digest(getattr(args, name)) for name in ("samples", "witnesses", "f1_evidence")},
                   tool_sha256=f.c.digest(__file__), f1_tool_sha256=f.c.digest(f.__file__),
                   coverage_tool_sha256=f.c.digest(f.c.__file__), h1_tool_sha256=f.c.digest(f.h.__file__),
                   environment=dict(numpy=np.__version__, python=platform.python_version(), platform=platform.platform()),
                   max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct, groups=groups, rows=rows)
    resource = dict(process_cpu_seconds=elapsed, cpu_limit_seconds=60, cpu_gate_pass=True,
                    first_reference_incremental_traced_peak_bytes=peak,
                    traced_peak_excludes_components_and_full_report=True, production_cpu_ram_state_delta=0)
    return summary, dict(references=reference_records, rows=detail), resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("samples", "witnesses", "f1-evidence", "source-commit", "output-prefix"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    paths = [Path(args.output_prefix + suffix + ".json") for suffix in ("", "-detail", "-resource")]
    f.c.require(all(not p.exists() for p in paths), "refusing overwrite")
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
    print(json.dumps(dict(decision=values[0]["decision"], pass_count=values[0]["pass_count"], resource=values[2])))


if __name__ == "__main__":
    main()
