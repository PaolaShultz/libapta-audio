#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Frozen ideal-model witnesses and label-selected support diagnostics only."""
import argparse
import json
import platform
import time
import tracemalloc
from pathlib import Path

import numpy as np
import apta_key_coverage_diagnostic as c
import apta_key_partial_attribution as h


def known_columns(meta):
    t, m, condition, window = meta
    root = 48 + t + [0, 5, 7, 0][window - 1]
    third = 4 if window == 3 or m == 0 else 3
    family = 0 if condition < 4 else 1 if condition == 4 else 2
    return [(note - 48) * 3 + family for note in (root, root + third, root + 7)]


def fundamentals(coefficients, model):
    coefficients = np.asarray(coefficients, dtype=float)
    c.require(coefficients.shape == (108,) and np.isfinite(coefficients).all() and
              (coefficients >= 0).all(), "invalid physical coefficients")
    return coefficients.reshape(36, 3).sum(axis=1) * model[2]


def pure_witness(energy, model):
    energy = np.asarray(energy, dtype=float)
    c.require(energy.shape == (36,) and np.isfinite(energy).all() and (energy >= 0).all(), "bad witness energy")
    physical = model[0] * model[1]
    coefficients = np.zeros(108)
    coefficients[::3] = energy / np.diag(physical[:, ::3])
    return coefficients


def solve_support(energy, columns):
    """Label-selected feasible reference, never a global/H1 estimator."""
    energy, columns = np.asarray(energy, dtype=float), np.asarray(columns, dtype=float)
    c.require(energy.shape == (36,) and columns.shape == (36, 3) and
              np.isfinite(energy).all() and np.isfinite(columns).all() and
              (energy >= 0).all() and (columns >= 0).all(), "invalid support problem")
    weights = np.zeros(3)
    best = float(np.dot(energy, energy))
    for mask in range(1, 8):
        active = [i for i in range(3) if mask & (1 << i)]
        fitted = np.linalg.lstsq(columns[:, active], energy, rcond=None)[0]
        if np.any(fitted < -1e-12):
            continue
        candidate = np.zeros(3)
        candidate[active] = np.maximum(0, fitted)
        residual = energy - columns @ candidate
        objective = float(np.dot(residual, residual))
        if objective < best:
            weights, best = candidate, objective
    c.require(np.isfinite(weights).all() and (weights >= 0).all(), "invalid support solution")
    residual = energy - columns @ weights
    c.require(abs(float(np.dot(residual, residual)) - best) <= 1e-12 * max(1.0, float(np.dot(energy, energy))),
              "support objective mismatch")
    return weights, best


def strict_improvement(before, after, input_power):
    return (before - after) / max(1.0, input_power) > 1e-12


def witness_pair(meta, model):
    c.require(meta[2] in (0, 4, 5), "witness requires nominal non-noise condition")
    physical = model[0] * model[1]
    oracle, _, _ = c.oracle(*meta)
    known = np.zeros(108)
    known[known_columns(meta)] = 810000.0
    pure = pure_witness(oracle, model)
    expected_scale = max(1.0, np.linalg.norm(oracle))
    errors = [float(np.linalg.norm(physical @ weights - oracle) / expected_scale) for weights in (known, pure)]
    errors.append(float(np.linalg.norm(physical @ known - physical @ pure) / expected_scale))
    c.require(max(errors) <= 1e-12, "witness equality failed")
    active_counts = [int(np.count_nonzero(weights)) for weights in (known, pure)]
    known_fund, pure_fund = fundamentals(known, model), fundamentals(pure, model)
    return known_fund, pure_fund, dict(id=list(meta), known_columns=known_columns(meta),
        known_coefficients=known.tolist(), pure_coefficients=pure.tolist(), spectrum=oracle.tolist(),
        known_fundamentals=known_fund.tolist(), pure_fundamentals=pure_fund.tolist(),
        equality_relative_errors=errors, active_counts=active_counts,
        both_within_six_columns=all(n <= 6 for n in active_counts),
        invisible_known_columns=[i for i in known_columns(meta) if model[1][i] == 0])


def evaluate(args):
    started = time.process_time()
    evidence = json.loads(Path(args.h1_evidence).read_text())
    for name, key in (("h1_detail", "result-detail.json"), ("h1_summary", "result.json")):
        c.require(c.digest(getattr(args, name)) == evidence["artifact_sha256"][key], "H1 artifact mismatch")
    for name, key in (("samples", "samples"), ("coverage_detail", "coverage_detail")):
        c.require(c.digest(getattr(args, name)) == evidence["input_sha256"][key], "coverage input mismatch")
    c.require(c.digest(h.__file__) == evidence["tool_sha256"] and
              c.digest(c.__file__) == evidence["coverage_tool_sha256"], "imported source drift")
    for name, key in (("probe", "probe"), ("i1_probe", "i1_probe")):
        c.require(c.digest(getattr(args, name)) == evidence["input_sha256"][key], "native probe drift")
    for relative, expected in evidence["validation"]["native_binary_and_production_object_hashes"].items():
        c.require(c.digest(Path(args.native_root) / relative) == expected, "native object drift: " + relative)
    h1 = json.loads(Path(args.h1_detail).read_text())
    prior = json.loads(Path(args.coverage_detail).read_text())
    records = c.parse_export(Path(args.samples).read_bytes())
    c.require([fit["id"] for fit in h1["fits"]] == [list(v) for v in c.metadata()], "H1 fit order")
    local_h1 = [r for r in h1["rows"] if r["scope"] == "local"]
    c.require([r["id"] for r in local_h1] == [list(v) for v in c.metadata()], "H1 local order")
    pure_baseline = {tuple(r["id"]): r for r in prior["rows"] if r["source"] == "component-oracle"
                     and r["transform"] == "mean-log" and r["scope"] == "local"}
    model = h.dictionary()
    physical = model[0] * model[1]
    dictionary = h.dictionary_info(model)
    dictionary["duplicate_pitch_class_counts"] = dict(
        same=sum((a // 3) % 12 == (b // 3) % 12 for a, b in dictionary["duplicate_column_pairs"]),
        different=sum((a // 3) % 12 != (b // 3) % 12 for a, b in dictionary["duplicate_column_pairs"]))
    dictionary["columns"] = [dict(index=i, midi=48 + i // 3, family=i % 3,
                                     norm=float(model[1][i]), zero=bool(model[1][i] == 0)) for i in range(108)]
    fits, witnesses, requests = [], [], []
    max_parseval = max_direct = max_h1_residual_discrepancy = 0.0
    logf = c.logf_function()
    traced_peak = 0
    for record, prior_fit, original in zip(records, h1["fits"], local_h1):
        meta = tuple(int(v) for v in record["metadata"])
        dense, parseval, direct = c.spectrum(record["samples"])
        max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
        weights = np.zeros(108)
        selected = prior_fit["selected"]
        c.require(len(selected) <= 6 and len(set(selected)) == len(selected) and
                  all(0 <= i < 108 for i in selected) and len(selected) == len(prior_fit["weights"]), "bad H1 coefficients")
        weights[selected] = prior_fit["weights"]
        c.require(np.isfinite(weights).all() and (weights >= 0).all(), "invalid H1 weight")
        residual = dense - model[0] @ weights
        input_power = float(np.dot(dense, dense))
        before = float(np.dot(residual, residual))
        relative = np.linalg.norm(residual) / max(1.0, np.linalg.norm(dense))
        discrepancy = abs(float(relative) - prior_fit["residual_relative_norm"])
        c.require(discrepancy <= 1e-12, "recorded H1 residual drift")
        max_h1_residual_discrepancy = max(max_h1_residual_discrepancy, discrepancy)
        columns = known_columns(meta)
        support_weights, after = solve_support(dense, model[0][:, columns])
        if not fits:
            tracemalloc.start()
            repeated, repeated_objective = solve_support(dense, model[0][:, columns])
            _, traced_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            c.require(np.array_equal(repeated, support_weights) and repeated_objective == after, "support allocation replay drift")
        fits.append(dict(id=list(meta), known_columns=columns, support_unit_weights=support_weights.tolist(),
                         h1_relative_squared_residual=before / max(1.0, input_power),
                         support_relative_squared_residual=after / max(1.0, input_power),
                         strict_improvement=strict_improvement(before, after, input_power),
                         h1_local_correct=c.matches(original["result"], original["expected"]),
                         h1_original_result=original["result"], expected=original["expected"]))
        if meta[2] in (0, 4, 5):
            known, pure, witness = witness_pair(meta, model)
            for source in (known, pure):
                chroma = c.fold_add(np.zeros(12, dtype=c.F), c.compress(source, "mean-log", logf))
                requests.append((chroma, 1))
            witnesses.append(witness)
    c.require(len(fits) == 576 and len(witnesses) == 288 and len(requests) == 576, "incomplete matrix")
    answers = c.query_probe(args.probe, requests)
    c.require(answers == c.query_probe(args.i1_probe, requests), "selector build difference")
    rows_known, rows_pure = [], []
    for i, witness in enumerate(witnesses):
        meta = witness["id"]
        expected = list(c.chord(meta[0], meta[1], meta[3]))
        known_result, pure_result = answers[2*i:2*i+2]
        c.require(pure_result == pure_baseline[tuple(meta)]["result"], "pure witness prior selector difference")
        witness.update(known_result=known_result, pure_result=pure_result, expected=expected)
        rows_known.append(dict(id=meta, expected=expected, result=known_result))
        rows_pure.append(dict(id=meta, expected=expected, result=pure_result))
    witness_groups, fit_groups = [], []
    for condition in range(6):
        for mode in (0, 1, "all"):
            def belongs(row):
                return row["id"][2] == condition and (mode == "all" or row["id"][1] == mode)
            group = [r for r in fits if belongs(r)]
            errors = [r for r in group if not r["h1_local_correct"]]
            fit_groups.append(dict(condition=c.CONDITIONS[condition], mode=mode, count=len(group),
                strict_improvements=sum(r["strict_improvement"] for r in group), h1_local_errors=len(errors),
                strict_improvements_among_h1_errors=sum(r["strict_improvement"] for r in errors),
                median_h1_relative_squared_residual=float(np.median([r["h1_relative_squared_residual"] for r in group])),
                median_support_relative_squared_residual=float(np.median([r["support_relative_squared_residual"] for r in group]))))
            if condition in (0, 4, 5):
                known = [r for r in rows_known if belongs(r)]
                pure = [r for r in rows_pure if belongs(r)]
                selected_witnesses = [r for r in witnesses if belongs(r)]
                scored = c.score_group(pure, known)
                witness_groups.append(dict(condition=c.CONDITIONS[condition], mode=mode,
                    known_matches=sum(c.matches(r["result"], r["expected"]) for r in known),
                    pure_vs_known=scored,
                    both_within_six=sum(r["both_within_six_columns"] for r in selected_witnesses),
                    changed_within_six=sum(r["both_within_six_columns"] and
                        (r["known_result"]["tonic"], r["known_result"]["mode"]) !=
                        (r["pure_result"]["tonic"], r["pure_result"]["mode"]) for r in selected_witnesses),
                    with_invisible_known_note=sum(bool(r["invisible_known_columns"]) for r in selected_witnesses)))
    c.require(sum(not r["h1_local_correct"] for r in fits) == 14, "H1 error count drift")
    elapsed = time.process_time() - started
    c.require(elapsed <= 120, "host analysis CPU limit exceeded")
    result = dict(format="apta-key-identifiability-result-1", source_commit=args.source_commit,
        baseline_commit="220f203759d54ea9c98a2fe843b0646eda757998", acceptance_claim=False,
        candidate_retained=False, corpus_access=False, production_cpu_ram_state_delta=0,
        environment=dict(numpy=np.__version__, python=platform.python_version(), platform=platform.platform()),
        input_sha256={name: c.digest(getattr(args, name)) for name in
                      ("samples", "coverage_detail", "h1_detail", "h1_summary", "h1_evidence", "probe", "i1_probe")},
        tool_sha256=c.digest(__file__), h1_tool_sha256=c.digest(h.__file__), coverage_tool_sha256=c.digest(c.__file__),
        all_prior_native_hashes_verified=True, native_selector_build_identity=True, pure_selector_prior_identity=True,
        windows=576, witness_pairs=288, native_selector_requests=576,
        max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct,
        max_h1_residual_discrepancy=max_h1_residual_discrepancy,
        max_witness_equality_error=max(max(r["equality_relative_errors"]) for r in witnesses),
        dictionary=dictionary, witness_groups=witness_groups, fit_groups=fit_groups)
    return result, dict(witnesses=witnesses, support_comparisons=fits), dict(
        process_cpu_seconds=elapsed, limit_seconds=120, cpu_gate_pass=True,
        first_support_call_incremental_traced_peak_bytes=traced_peak,
        traced_peak_excludes_model_and_full_report=True, production_cpu_ram_state_delta=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("samples", "coverage-detail", "h1-detail", "h1-summary", "h1-evidence", "probe", "i1-probe",
                 "native-root", "source-commit", "output-prefix"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    paths = [Path(args.output_prefix + suffix + ".json") for suffix in ("", "-detail", "-resource")]
    c.require(all(not p.exists() for p in paths), "refusing overwrite")
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
    print(json.dumps(dict(witness_pairs=values[0]["witness_pairs"], resource=values[2])))


if __name__ == "__main__":
    main()
