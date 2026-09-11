#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""F1: fixed-reference frequency detail diagnostic; no estimator or music."""
import argparse
import json
import math
import platform
import time
import tracemalloc
from pathlib import Path

import numpy as np
import apta_key_coverage_diagnostic as c
import apta_key_partial_attribution as h


def average_four(samples, dtype):
    samples = np.asarray(samples, dtype=dtype)
    c.require(samples.shape == (48000,) and np.isfinite(samples).all(), "invalid 48-kHz reference")
    grouped = samples.reshape(12000, 4)
    result = np.zeros(12000, dtype=dtype)
    for i in range(4):
        result = np.asarray(result + grouped[:, i], dtype=dtype)
    return np.asarray(result / dtype(4), dtype=dtype)


def reference(example, kind):
    c.require(kind in ("known", "pure"), "unknown reference")
    source = example[kind + "_nonzero_coefficients"]
    frames = np.arange(48000, dtype=np.float64) + (example["id"][3] - 1) * 48000
    samples = np.zeros(48000)
    components = []
    for column in source:
        midi = column["midi"]
        frequency = 440.0 * math.pow(2.0, (midi - 69.0) / 12.0)
        c.require(column["family"] == (2 if kind == "known" else 0), "unexpected witness family")
        if kind == "known":
            c.require(column["coefficient"] == 810000, "unexpected known amplitude")
        for harmonic in ((2, 3, 4) if kind == "known" else (1,)):
            amplitude = 0.15 / harmonic if kind == "known" else 2 * math.sqrt(column["coefficient"]) / c.N
            # Match the original C order of floating operations in phase.
            phase = 6.2831853071795864769 * frequency * harmonic * frames / 48000
            samples += amplitude * np.sin(phase)
            actual_frequency = frequency * harmonic
            cell = int(c.cell_indices(actual_frequency))
            inside = 0 <= cell < 36
            center = 440 * 2 ** ((48 + cell - 69) / 12) if inside else None
            components.append(dict(source_midi=midi, harmonic=harmonic, amplitude=amplitude,
                                   frequency_hz=actual_frequency, retained=inside,
                                   cell_midi=48 + cell if inside else None,
                                   cell_center_hz=center, offset_hz=actual_frequency - center if inside else None))
    return samples, components


def checked_power(samples):
    cells, parseval, direct = c.spectrum(samples)
    power = np.abs(np.fft.rfft(np.asarray(samples, dtype=np.float64))) ** 2
    c.require(power.shape == (6001,) and np.isfinite(power).all() and (power >= 0).all(), "invalid FFT power")
    return power, cells, parseval, direct


def fine_distance(actual, target, ideal):
    actual, target, ideal = [np.asarray(v, dtype=float) for v in (actual, target, ideal)]
    c.require(actual.shape == (6001,) and target.shape == (6001,) and ideal.shape == (36,), "bad score shape")
    c.require(all(np.isfinite(v).all() and (v >= 0).all() for v in (actual, target, ideal)) and ideal.sum() > 0,
              "invalid score power")
    cell_index = c.cell_indices(np.arange(6001))
    result = 0.0
    details = []
    for cell in np.flatnonzero(ideal > 0):
        indices = np.flatnonzero(cell_index == cell)
        a, b = actual[indices], target[indices]
        c.require(a.sum() > 0 and b.sum() > 0, "empty scored cell")
        pa, pb = a / a.sum(), b / b.sum()
        distance = float(np.abs(pa - pb).sum())
        weight = float(ideal[cell] / ideal.sum())
        result += weight * distance
        details.append(dict(midi=48 + int(cell), bins_hz=indices.tolist(), ideal_weight=weight,
                            distance=distance, actual_distribution=pa.tolist(), target_distribution=pb.tolist(),
                            actual_peak_bin_hz=int(indices[np.argmax(a)]), target_peak_bin_hz=int(indices[np.argmax(b)])))
    c.require(0 <= result <= 2 + 1e-15, "fine score outside L1 bounds")
    return float(result), details


def supports(dtrue, dalt):
    return dalt > 100 * dtrue + 1e-9


def evaluate(args):
    start = time.process_time()
    public = json.loads(Path(args.witnesses).read_text())
    c.require(c.digest(args.samples) == public["input_sha256"]["samples"], "PCM hash drift")
    c.require(c.digest(h.__file__) == public["h1_tool_sha256"] and
              c.digest(c.__file__) == public["coverage_tool_sha256"], "reference source drift")
    examples = public["exact_six_column_counterexamples"]
    c.require(len(examples) == 8 and len({tuple(r["id"]) for r in examples}) == 8, "invalid witness IDs")
    unique = len({json.dumps(r["nonzero_spectrum"], sort_keys=True) for r in examples})
    c.require(unique == public["exact_six_column_counterexample_unique_spectra"] == 4, "unique witness count drift")
    c.require([r["id"] for r in examples] == sorted([r["id"] for r in examples]), "witness order drift")
    model = h.dictionary()
    physical = model[0] * model[1]
    records = c.parse_export(Path(args.samples).read_bytes())
    observed = {tuple(int(v) for v in record["metadata"]): record["samples"] for record in records}
    rows, details = [], []
    max_parseval = max_direct = 0.0
    peak = 0
    for example in examples:
        meta = example["id"]
        actual = observed[tuple(meta)]
        ideal = np.zeros(36)
        for item in example["nonzero_spectrum"]:
            ideal[item["midi"] - 48] = item["energy"]
        errors = []
        for kind in ("known", "pure"):
            weights = np.zeros(108)
            for item in example[kind + "_nonzero_coefficients"]:
                weights[item["column"]] = item["coefficient"]
            errors.append(float(np.linalg.norm(physical @ weights - ideal) / max(1.0, np.linalg.norm(ideal))))
        c.require(max(errors) <= 1e-12, "ideal witness reconstruction failed")
        known48, known_components = reference(example, "known")
        alternative48, pure_components = reference(example, "pure")
        if not rows:
            tracemalloc.start()
            repeated, _ = reference(example, "known")
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            c.require(np.array_equal(repeated, known48), "reference allocation replay mismatch")
        rounded = average_four(known48, np.float32)
        sample_relative = float(np.linalg.norm(rounded.astype(float) - actual) / max(np.linalg.norm(actual.astype(float)), np.finfo(float).tiny))
        sample_absolute = float(np.max(np.abs(rounded.astype(float) - actual)))
        c.require(sample_relative <= 1e-6 and sample_absolute <= 1e-6, "actual C PCM reconstruction failed")
        known = average_four(known48, np.float64)
        alternative = average_four(alternative48, np.float64)
        powers, cells = [], []
        for samples in (actual, known, alternative):
            power, integrated, parseval, direct = checked_power(samples)
            powers.append(power)
            cells.append(integrated)
            max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
        dtrue, true_detail = fine_distance(powers[0], powers[1], ideal)
        dalt, alt_detail = fine_distance(powers[0], powers[2], ideal)
        coarse_true, ratio_true = c.distance(cells[0], cells[1])
        coarse_alt, ratio_alt = c.distance(cells[0], cells[2])
        row = dict(id=meta, sample_relative_error=sample_relative, sample_max_absolute_error=sample_absolute,
                   ideal_witness_relative_errors=errors, fine_actual_known=dtrue, fine_actual_alternative=dalt,
                   required_margin=100*dtrue + 1e-9, fixed_reference_support=supports(dtrue, dalt),
                   coarse_actual_known=coarse_true, coarse_actual_alternative=coarse_alt,
                   actual_to_known_total_energy_ratio=ratio_true, actual_to_alternative_total_energy_ratio=ratio_alt)
        rows.append(row)
        details.append(dict(**row, known_components=known_components, alternative_components=pure_components,
                            actual_cell_energies=cells[0].tolist(), known_cell_energies=cells[1].tolist(),
                            alternative_cell_energies=cells[2].tolist(), known_comparison=true_detail, alternative_comparison=alt_detail))
    elapsed = time.process_time() - start
    c.require(elapsed <= 30, "host CPU limit exceeded")
    summary = dict(format="apta-key-within-cell-f1-result-1", source_commit=args.source_commit,
                   baseline_commit="31d3d9245a919d0db53a01abe6e9eaec8a068878", acceptance_claim=False,
                   candidate_retained=False, corpus_access=False, h1_remains_rejected=True, production_cpu_ram_state_delta=0,
                   reference_phases="fixed-original-absolute-frame", phase_robustness_claim=False,
                   input_sha256=dict(samples=c.digest(args.samples), witnesses=c.digest(args.witnesses)),
                   tool_sha256=c.digest(__file__), coverage_tool_sha256=c.digest(c.__file__), h1_tool_sha256=c.digest(h.__file__),
                   environment=dict(numpy=np.__version__, python=platform.python_version(), platform=platform.platform()),
                   witness_pairs=8, unique_ideal_spectra=4, fixed_reference_support_count=sum(r["fixed_reference_support"] for r in rows),
                   all_fixed_references_supported=all(r["fixed_reference_support"] for r in rows),
                   max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct, rows=rows)
    resource = dict(process_cpu_seconds=elapsed, cpu_limit_seconds=30, cpu_gate_pass=True,
                    first_known_reference_incremental_traced_peak_bytes=peak,
                    traced_peak_excludes_other_arrays_and_full_report=True, production_cpu_ram_state_delta=0)
    return summary, dict(rows=details), resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("samples", "witnesses", "source-commit", "output-prefix"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    paths = [Path(args.output_prefix + suffix + ".json") for suffix in ("", "-detail", "-resource")]
    c.require(all(not p.exists() for p in paths), "refusing overwrite")
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open("x", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
    print(json.dumps(dict(supported_pairs=values[0]["fixed_reference_support_count"], resource=values[2])))


if __name__ == "__main__":
    main()
