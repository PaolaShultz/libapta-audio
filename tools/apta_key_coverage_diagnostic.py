#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic coverage diagnostic. Requires NumPy and the native C probe.

No corpus input, tuning, labels, production frontend or acceptance decision.
See docs/status/APTA-1.1-KEY-COVERAGE-PROTOCOL.md.
"""
import argparse
import ctypes
import hashlib
import json
import platform
import struct
import subprocess
from pathlib import Path

import numpy as np

N = 12000
EDGES = 440.0 * 2.0 ** ((np.arange(37) + 47.5 - 69.0) / 12.0)
DTYPE = np.dtype([("metadata", "<u4", (4,)), ("coefficients", "<f4", (36,)),
                  ("samples", "<f4", (N,))])
CONDITIONS = ["clean", "plus-third", "noise", "minus-third", "harmonics", "missing-fundamental"]
TRANSFORMS = ["absolute-log", "mean-log"]
SOURCES = ["narrow", "dense", "component-oracle"]
F = np.float32


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metadata():
    return [(t, m, c, w) for m in range(2) for t in range(12)
            for c in range(6) for w in range(1, 5)]


def parse_export(data):
    require(len(data) == 8 + 576 * DTYPE.itemsize and data[:8] == b"APTCOV01",
            "bad export magic or length")
    records = np.frombuffer(data, dtype=DTYPE, offset=8)
    require(np.array_equal(records["metadata"], metadata()), "reordered export")
    require(np.isfinite(records["samples"]).all(), "nonfinite PCM")
    coeff = records["coefficients"]
    require(np.isfinite(coeff).all() and (np.abs(coeff) <= 2).all(), "invalid coefficients")
    require(np.array_equal(coeff, np.broadcast_to(coeff[0], coeff.shape)), "coefficient drift")
    return records


def cell_indices(frequencies):
    return np.searchsorted(EDGES, frequencies, side="right") - 1


def integrate(frequencies, powers):
    cells = cell_indices(frequencies)
    inside = (cells >= 0) & (cells < 36)
    return np.bincount(cells[inside], weights=np.asarray(powers)[inside], minlength=36)


def spectrum(samples):
    x = np.asarray(samples, dtype=np.float64)
    require(x.shape == (N,) and np.isfinite(x).all(), "bad FFT input")
    fft = np.fft.rfft(x)
    power = np.abs(fft) ** 2
    spectral = (power[0] + power[-1] + 2 * power[1:-1].sum()) / N
    temporal = np.dot(x, x)
    error = abs(spectral - temporal) / max(temporal, np.finfo(float).tiny)
    require(error <= 1e-12, "Parseval tolerance failed")
    direct_errors = []
    indices = np.arange(N, dtype=np.float64)
    for k in (131, 220, 440):
        phase = 2 * np.pi * k * indices / N
        direct = np.dot(x, np.cos(phase)) - 1j * np.dot(x, np.sin(phase))
        relative = abs(direct - fft[k]) / max(1.0, abs(direct))
        require(relative <= 1e-9, "direct Fourier tolerance failed")
        direct_errors.append(float(relative))
    return integrate(np.arange(N // 2 + 1), power), float(error), max(direct_errors)


def chord(tonic, mode, window):
    return (tonic + [0, 5, 7, 0][window - 1]) % 12, 0 if window == 3 else mode


def oracle(tonic, mode, condition, window):
    root = 48 + tonic + [0, 5, 7, 0][window - 1]
    third = 4 if window == 3 or mode == 0 else 3
    detune = 1 / 3 if condition == 1 else -1 / 3 if condition == 3 else 0
    harmonics = [2, 3, 4] if condition == 5 else [1, 2, 3, 4] if condition == 4 else [1]
    frequencies, powers = [], []
    for note in [root, root + third, root + 7]:
        for h in harmonics:
            freq = 440 * 2 ** ((note - 69 + detune) / 12) * h
            response = abs(np.exp(2j * np.pi * freq * np.arange(4) / 48000).mean())
            frequencies.append(freq)
            powers.append((N * (0.15 / h) * response / 2) ** 2)
    energy = integrate(np.array(frequencies), np.array(powers))
    fundamental = np.zeros(12, dtype=F)
    for note in [root, root + third, root + 7]:
        fundamental[note % 12] += F(1)
    return energy, float(energy.sum() / sum(powers)), fundamental


def logf_function():
    lib = ctypes.CDLL("libm.so.6")
    function = lib.logf
    function.argtypes = [ctypes.c_float]
    function.restype = ctypes.c_float
    return function


def compress(energies, transform, logf):
    e = np.asarray(energies, dtype=F).copy()
    e[~np.isfinite(e) | (e < 0)] = F(0)
    if transform == "mean-log":
        peak = max(e)
        if peak == 0:
            return e
        scaled_sum = F(0)
        for value in e:
            scaled_sum = F(scaled_sum + F(value / peak))
        factor = F(F(36) / scaled_sum)
        e = np.array([F(F(value / peak) * factor) for value in e], dtype=F)
    else:
        require(transform == "absolute-log", "unknown compression")
    return np.array([logf(F(F(1) + value)) for value in e], dtype=F)


def fold_add(cumulative, compressed):
    result = cumulative.copy()
    for bin_index, value in enumerate(compressed):
        result[bin_index % 12] = F(result[bin_index % 12] + value)
    return result


def distance(energy, reference):
    total = float(np.sum(energy, dtype=np.float64))
    ref_total = float(reference.sum())
    require(total > 0 and ref_total > 0, "empty diagnostic energy")
    return float(np.abs(energy / total - reference / ref_total).sum()), total / ref_total


def native_rows(path, old_path):
    report = json.loads(Path(path).read_text())
    require(report["format"] == "apta-key-coverage-diagnostic-1" and
            report["row_count"] == 1296 and report["checks_passed"] is True and
            report["acceptance_claim"] is False and report["semitone_band"] is False,
            "invalid native report")
    rows = report["rows"]
    require(len(rows) == 1296, "incomplete native rows")
    old = json.loads(Path(old_path).read_text())
    filtered = [r for r in rows if r["condition"] < 3]
    require(len(filtered) == 720 and filtered == old["rows"], "legacy 720-row identity failed")
    cumulative = [r for r in rows if r["kind"] == "pcm_cumulative"]
    require([(r["stimulus_tonic"], r["stimulus_mode"], r["condition"], r["window"])
             for r in cumulative] == metadata(), "native rows reordered")
    return cumulative


def query_probe(path, requests):
    payload = b"".join(np.asarray(chroma, dtype="<f4").tobytes() + struct.pack("<I", windows)
                       for chroma, windows in requests)
    result = subprocess.run([str(path), "--binary"], input=payload, capture_output=True, check=True)
    answers = [json.loads(line) for line in result.stdout.splitlines()]
    require(len(answers) == len(requests), "incomplete probe responses")
    return answers


def matches(result, expected):
    return result.get("available", False) and (result["tonic"], result["mode"]) == tuple(expected)


def score_group(rows, baseline):
    require(len(rows) == len(baseline) and len(rows) > 0, "invalid scoring group")
    counts = dict(count=len(rows), matches=0, tonic_only_errors=0, mode_only_errors=0,
                  tonic_and_mode_errors=0, unavailable=0, high_confidence_errors=0,
                  changed=0, fixes=0, breaks=0, new_high_confidence_errors=0)
    for row, base in zip(rows, baseline):
        require(row["id"] == base["id"] and row["expected"] == base["expected"], "scoring alignment")
        r, b, expected = row["result"], base["result"], row["expected"]
        correct, was_correct = matches(r, expected), matches(b, expected)
        counts["matches"] += int(correct)
        if not r.get("available"):
            counts["unavailable"] += 1
        elif not correct:
            wrong_tonic, wrong_mode = r["tonic"] != expected[0], r["mode"] != expected[1]
            counts["tonic_and_mode_errors" if wrong_tonic and wrong_mode else
                   "tonic_only_errors" if wrong_tonic else "mode_only_errors"] += 1
        high = r.get("confidence", 0) >= 75 and not correct
        prior_high = b.get("confidence", 0) >= 75 and not was_correct
        counts["high_confidence_errors"] += int(high)
        counts["new_high_confidence_errors"] += int(high and not prior_high)
        counts["changed"] += int((r.get("tonic"), r.get("mode")) != (b.get("tonic"), b.get("mode")))
        counts["fixes"] += int(correct and not was_correct)
        counts["breaks"] += int(not correct and was_correct)
    return counts


def evaluate(args):
    paths = {name: getattr(args, name) for name in
             ("default_samples", "i1_samples", "default_report", "i1_report",
              "default_legacy", "i1_legacy", "probe", "i1_probe")}
    require(digest(paths["default_samples"]) == digest(paths["i1_samples"]), "PCM/coefficient build mismatch")
    records = parse_export(Path(paths["default_samples"]).read_bytes())
    native = {"absolute-log": native_rows(paths["default_report"], paths["default_legacy"]),
              "mean-log": native_rows(paths["i1_report"], paths["i1_legacy"])}
    logf = logf_function()
    requests, details, identity, energy_metrics = [], [], [], []
    max_parseval = max_direct = 0.0
    cumulative = {}

    def add(source, transform, scope, meta, chroma, windows, expected):
        t, m, c, w = meta
        details.append(dict(source=source, transform=transform, scope=scope,
                            id=[t, m, c, w], expected=list(expected), chroma=chroma.tolist()))
        requests.append((chroma, windows))
        return len(requests) - 1

    for i, record in enumerate(records):
        meta = tuple(int(v) for v in record["metadata"])
        t, m, c, w = meta
        if w == 1:
            cumulative = {(source, tr): np.zeros(12, dtype=F) for source in SOURCES for tr in TRANSFORMS}
            cumulative[("fundamental-oracle", "none")] = np.zeros(12, dtype=F)
        dense, parseval, direct = spectrum(record["samples"])
        max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
        ideal, in_range, fundamental = oracle(t, m, c, w)
        raw = np.asarray(native["absolute-log"][i]["contrast"]["raw_energy_by_variant"], dtype=F)
        require(raw.shape == (1, 36) and np.isfinite(raw).all() and (raw >= 0).all(), "invalid native energies")
        other = np.asarray(native["mean-log"][i]["contrast"]["raw_energy_by_variant"], dtype=F)
        require(raw.tobytes() == other.tobytes(), "native raw energy mismatch")
        representations = dict(narrow=raw[0], dense=dense, **{"component-oracle": ideal})
        metrics = dict(id=list(meta), in_range_fraction=in_range)
        for source, energy in representations.items():
            l1, capture = distance(np.asarray(energy, dtype=np.float64), ideal)
            metrics[source] = dict(normalized_l1=l1, capture_ratio=capture)
            for transform in TRANSFORMS:
                compressed = compress(energy, transform, logf)
                local = fold_add(np.zeros(12, dtype=F), compressed)
                total = fold_add(cumulative[(source, transform)], compressed)
                cumulative[(source, transform)] = total
                add(source, transform, "local", meta, local, 1, chord(t, m, w))
                index = add(source, transform, "cumulative", meta, total, w, (t, m))
                if source == "narrow":
                    row = native[transform][i]
                    require(total.tobytes() == np.asarray(row["chroma"], dtype=F).tobytes(),
                            "native cumulative float identity failed")
                    require(compressed.tobytes() == np.asarray(row["contrast"]["compressed_by_variant"][0], dtype=F).tobytes(),
                            "native compression float identity failed")
                    identity.append((index, row))
        energy_metrics.append(metrics)
        key = ("fundamental-oracle", "none")
        cumulative[key] = np.asarray(cumulative[key] + fundamental, dtype=F)
        add(*key, "local", meta, fundamental, 1, chord(t, m, w))
        add(*key, "cumulative", meta, cumulative[key], w, (t, m))

    answers = query_probe(args.probe, requests)
    require(answers == query_probe(args.i1_probe, requests), "C selector build mismatch")
    for index, row in identity:
        result = answers[index]
        require(result == dict(available=True, tonic=row["selected_tonic"], mode=row["selected_mode"],
                               confidence=row["confidence"], candidates=row["native_candidates"]),
                "native selector identity failed")
    for row, answer in zip(details, answers):
        row["result"] = answer

    groups = []
    for condition in range(6):
        for mode in (0, 1, "all"):
            for scope in ("local", "first", "final"):
                def subset(source, transform):
                    return [r for r in details if r["source"] == source and r["transform"] == transform
                            and r["id"][2] == condition and (mode == "all" or r["id"][1] == mode)
                            and ((scope == "local" and r["scope"] == "local") or
                                 (scope != "local" and r["scope"] == "cumulative"
                                  and r["id"][3] == (1 if scope == "first" else 4)))]
                for transform in TRANSFORMS:
                    baseline = subset("narrow", transform)
                    for source in SOURCES + ["fundamental-oracle"]:
                        tr = "none" if source == "fundamental-oracle" else transform
                        groups.append(dict(condition=CONDITIONS[condition], mode=mode, scope=scope,
                                           source=source, transform=transform,
                                           **score_group(subset(source, tr), baseline)))
    coverage = []
    for c, condition in enumerate(CONDITIONS):
        for mode in (0, 1, "all"):
            selected = [r for r in energy_metrics if r["id"][2] == c and (mode == "all" or r["id"][1] == mode)]
            coverage.append(dict(condition=condition, mode=mode, windows=len(selected),
                                 median_in_range_fraction=float(np.median([r["in_range_fraction"] for r in selected])),
                                 **{s: {k: float(np.median([r[s][k] for r in selected]))
                                        for k in ("normalized_l1", "capture_ratio")} for s in SOURCES}))
    detuned = [r for r in coverage if r["mode"] == "all" and r["condition"] in ("plus-third", "minus-third")]
    summary = dict(format="apta-key-coverage-result-1", acceptance_claim=False, candidate_retained=False,
                   corpus_access=False, input_sha256={k: digest(v) for k, v in paths.items()},
                   tool_sha256=digest(__file__), source_commit=args.source_commit,
                   environment=dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform()),
                   windows=576, progressions=144, native_rows_per_build=1296, native_legacy_rows_identical_per_build=720,
                   native_cumulative_bit_identity_per_build=576, native_selector_results=len(answers),
                   native_selector_build_identity=True, production_cpu_ram_state_delta=0,
                   max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct,
                   coverage_contribution_supported=all(r["dense"]["normalized_l1"] < r["narrow"]["normalized_l1"] for r in detuned),
                   coverage=coverage, scores=groups)
    return summary, dict(format="apta-key-coverage-detail-1", energy=energy_metrics, rows=details)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("default-samples", "i1-samples", "default-report", "i1-report", "default-legacy", "i1-legacy",
                 "probe", "i1-probe", "source-commit", "summary", "detail"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    require(not Path(args.summary).exists() and not Path(args.detail).exists(), "refusing output overwrite")
    summary, detail = evaluate(args)
    for path, value in ((args.summary, summary), (args.detail, detail)):
        with open(path, "x", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
            output.write("\n")
    print(json.dumps({k: summary[k] for k in ("windows", "native_selector_results", "coverage_contribution_supported")}))


if __name__ == "__main__":
    main()
