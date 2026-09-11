#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""H1: frozen synthetic-only partial attribution; no production detector."""
import argparse
import json
import platform
import time
import tracemalloc
from pathlib import Path

import numpy as np
import apta_key_coverage_diagnostic as coverage

HARMONICS = ((1,), (1, 2, 3, 4), (2, 3, 4))
BASELINE = "6cd9fa45779058aa8b36057180d2e8b9adfebd4b"


def response(frequency):
    return abs(np.exp(2j * np.pi * frequency * np.arange(4) / 48000).mean())


def dictionary():
    columns, fundamental_response = [], []
    for midi in range(48, 84):
        frequency = 440 * 2 ** ((midi - 69) / 12)
        fundamental_response.append(response(frequency) ** 2)
        for harmonics in HARMONICS:
            frequencies = np.array([frequency * h for h in harmonics])
            weights = np.array([response(frequency * h) ** 2 / h ** 2 for h in harmonics])
            columns.append(coverage.integrate(frequencies, weights))
    matrix = np.array(columns, dtype=np.float64).T.copy()
    norms = np.linalg.norm(matrix, axis=0)
    matrix[:, norms > 0] /= norms[norms > 0]
    return matrix, norms, np.array(fundamental_response)


def attribute(energy, model):
    """Input is only 36 energies and a label-independent, fixed dictionary."""
    energy = np.asarray(energy, dtype=np.float64)
    coverage.require(energy.shape == (36,) and np.isfinite(energy).all() and
                     (energy >= 0).all(), "invalid attribution input")
    matrix, norms, fundamental_response = model
    residual = energy.copy()
    weights = np.zeros(108)
    selected = []
    enabled = norms > 0
    squared_norm = np.einsum("ij,ij->j", matrix, matrix)
    input_power = float(np.dot(energy, energy))
    max_increase = 0.0
    updates = 0
    for _ in range(6):
        projections = matrix.T @ residual
        projections[~enabled] = 0
        projections[selected] = 0
        chosen = int(np.argmax(projections))
        if projections[chosen] <= 0:
            break
        selected.append(chosen)
        for _ in range(32):
            for index in selected:
                column = matrix[:, index]
                old = weights[index]
                updated = max(0.0, old + np.dot(column, residual) / squared_norm[index])
                before = float(np.dot(residual, residual))
                residual -= column * (updated - old)
                weights[index] = updated
                after = float(np.dot(residual, residual))
                increase = (after - before) / max(1.0, input_power)
                max_increase = max(max_increase, increase)
                coverage.require(increase <= 1e-12, "coordinate objective increase")
                updates += 1
    reconstructed = matrix @ weights
    error = float(np.linalg.norm(energy - reconstructed - residual) / max(1.0, np.linalg.norm(energy)))
    coverage.require(error <= 1e-12, "residual reconstruction identity")
    equivalent = np.zeros(36)
    for index in selected:
        equivalent[index // 3] += weights[index] / norms[index]
    equivalent *= fundamental_response
    coverage.require(np.isfinite(equivalent).all() and (equivalent >= 0).all(), "invalid recovered energy")
    gradients = matrix.T @ residual
    # Diagnostic violations across all enabled columns; this is bounded fitting,
    # not a claim of NNLS convergence after six selected columns.
    violations = np.where(weights > 0, np.abs(gradients), np.maximum(0, gradients))
    violations[~enabled] = 0
    return equivalent, dict(selected=selected, weights=[float(weights[j]) for j in selected],
        coordinate_updates=updates, residual_relative_norm=float(np.linalg.norm(residual) / max(1.0, np.linalg.norm(energy))),
        residual_identity_error=error, max_objective_increase_scaled=max_increase,
        max_coordinate_violation_scaled=float(max(violations) / max(1.0, np.linalg.norm(energy))))


def dictionary_info(model):
    matrix, norms, fundamental_response = model
    duplicates = [(a, b) for a in range(108) for b in range(a + 1, 108)
                  if norms[a] > 0 and norms[b] > 0 and np.array_equal(matrix[:, a], matrix[:, b])]
    # Named persistent numeric work arrays at peak: dictionary, norms, response,
    # input, residual, weights, enabled, squared norms, projections, column copy,
    # reconstruction, equivalent, gradients, violations. Python temporaries and
    # containers are separately measured with tracemalloc.
    workspace = matrix.nbytes + norms.nbytes + fundamental_response.nbytes + 8 * (36 * 5 + 108 * 6) + 108
    return dict(shape=list(matrix.shape), dictionary_bytes=matrix.nbytes,
                named_numeric_workspace_bound_bytes=workspace,
                disabled_columns=np.flatnonzero(norms == 0).tolist(), duplicate_column_pairs=duplicates)


def groups(details, prior):
    result = []
    for condition in range(6):
        for mode in (0, 1, "all"):
            for scope in ("local", "first", "final"):
                def subset(rows):
                    return [r for r in rows if r["id"][2] == condition and
                            (mode == "all" or r["id"][1] == mode) and
                            ((scope == "local" and r["scope"] == "local") or
                             (scope != "local" and r["scope"] == "cumulative" and
                              r["id"][3] == (1 if scope == "first" else 4)))]
                for baseline in ("narrow", "dense"):
                    baseline_rows = [r for r in prior if r["source"] == baseline and r["transform"] == "mean-log"]
                    result.append(dict(condition=coverage.CONDITIONS[condition], mode=mode, scope=scope,
                                       baseline=baseline, **coverage.score_group(subset(details), subset(baseline_rows))))
    return result


def scientific_gates(scores):
    def select(scope, baseline, condition=None):
        return [r for r in scores if r["mode"] == "all" and r["scope"] == scope and r["baseline"] == baseline
                and (condition is None or r["condition"] == condition)]
    final = select("final", "dense")
    coverage.require(len(final) == 6 and all(r["count"] == 24 for r in final), "incomplete scoring matrix")
    local = select("local", "dense")
    coverage.require(len(local) == 6 and all(r["count"] == 96 for r in local), "incomplete local matrix")
    missing = "missing-fundamental"
    return dict(first_five_final_24=all(r["matches"] == 24 for r in final if r["condition"] != missing),
                no_final_break_vs_dense=all(r["breaks"] == 0 for r in final),
                missing_final_24=select("final", "dense", missing)[0]["matches"] == 24,
                missing_local_at_least_89=select("local", "dense", missing)[0]["matches"] >= 89,
                no_final_break_vs_narrow=all(r["breaks"] == 0 for r in select("final", "narrow")),
                no_new_high_confidence_errors=all(r["new_high_confidence_errors"] == 0 for r in scores),
                overall_local_no_decrease_vs_dense=sum(r["fixes"] - r["breaks"] for r in local) >= 0)


def evaluate(args):
    validation = json.loads(Path(args.validation).read_text())
    summary = json.loads(Path(args.coverage_summary).read_text())
    pinned = {"samples": "default.bin", "coverage_detail": "detail.json", "coverage_summary": "summary.json"}
    for name, key in pinned.items():
        coverage.require(coverage.digest(getattr(args, name)) == validation["artifact_sha256"][key], "input hash mismatch: " + name)
    coverage.require(coverage.digest(coverage.__file__) == summary["tool_sha256"], "coverage implementation drift")
    for name, key in (("probe", "default/tests/apta_key_chroma_probe"),
                      ("i1_probe", "candidate/tests/apta_key_chroma_probe")):
        coverage.require(coverage.digest(getattr(args, name)) == validation["binary_sha256"][key], "selector hash drift")
    records = coverage.parse_export(Path(args.samples).read_bytes())
    prior = json.loads(Path(args.coverage_detail).read_text())["rows"]
    model = dictionary()
    info = dictionary_info(model)
    requests, details, fits = [], [], []
    cumulative = np.zeros(12, dtype=coverage.F)
    logf = coverage.logf_function()
    attribution_cpu = 0.0
    max_parseval = max_direct = 0.0
    traced_peak = 0
    for record in records:
        t, m, c, w = [int(v) for v in record["metadata"]]
        if w == 1:
            cumulative = np.zeros(12, dtype=coverage.F)
        dense, parseval, direct = coverage.spectrum(record["samples"])
        max_parseval, max_direct = max(max_parseval, parseval), max(max_direct, direct)
        started = time.process_time()
        energy, fit = attribute(dense, model)
        attribution_cpu += time.process_time() - started
        # Measure allocations on the first window in a separate, untimed replay.
        if not details:
            tracemalloc.start()
            replay_energy, replay_fit = attribute(dense, model)
            _, traced_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            coverage.require(np.array_equal(energy, replay_energy) and fit == replay_fit, "allocation replay identity")
        compressed = coverage.compress(energy, "mean-log", logf)
        local = coverage.fold_add(np.zeros(12, dtype=coverage.F), compressed)
        cumulative = coverage.fold_add(cumulative, compressed)
        for scope, chroma, count, expected in (("local", local, 1, coverage.chord(t, m, w)),
                                                ("cumulative", cumulative, w, (t, m))):
            details.append(dict(id=[t, m, c, w], scope=scope, expected=list(expected), chroma=chroma.tolist()))
            requests.append((chroma, count))
        fits.append(dict(id=[t, m, c, w], energy=energy.tolist(), **fit))
    results = coverage.query_probe(args.probe, requests)
    coverage.require(results == coverage.query_probe(args.i1_probe, requests), "selector build mismatch")
    for row, result in zip(details, results):
        row["result"] = result
    scores = groups(details, prior)
    gates = scientific_gates(scores)
    gates.update(dictionary_32_kib=info["dictionary_bytes"] <= 32768,
                 numeric_workspace_64_kib=info["named_numeric_workspace_bound_bytes"] <= 65536,
                 bounded_iterations=all(len(r["selected"]) <= 6 and r["coordinate_updates"] <= 672 for r in fits))
    outcome = dict(format="apta-key-partial-attribution-h1-result-1", source_commit=args.source_commit,
                   baseline_commit=BASELINE, acceptance_claim=False, corpus_access=False, production_cpu_ram_state_delta=0,
                   scientific_and_static_resource_gates=gates,
                   scientific_and_static_resource_pass=all(gates.values()),
                   environment=dict(numpy=np.__version__, python=platform.python_version(), platform=platform.platform()),
                   input_sha256={name: coverage.digest(getattr(args, name)) for name in
                                 ("samples", "coverage_detail", "coverage_summary", "validation", "probe", "i1_probe")},
                   tool_sha256=coverage.digest(__file__), coverage_tool_sha256=coverage.digest(coverage.__file__),
                   windows=576, progressions=144, native_selector_results=len(results), native_selector_build_identity=True,
                   max_parseval_relative_error=max_parseval, max_direct_scaled_error=max_direct,
                   dictionary=info, scores=scores,
                   fit_statistics={key: dict(max=float(max(r[key] for r in fits)), median=float(np.median([r[key] for r in fits])))
                                   for key in ("coordinate_updates", "residual_relative_norm", "residual_identity_error",
                                               "max_objective_increase_scaled", "max_coordinate_violation_scaled")})
    resource = dict(format="apta-key-partial-attribution-h1-resource-1", attribution_process_cpu_seconds=attribution_cpu,
                    attribution_cpu_limit_seconds=60, attribution_cpu_gate=attribution_cpu <= 60,
                    first_window_traced_peak_incremental_bytes=traced_peak,
                    traced_peak_excludes_prebuilt_dictionary=True,
                    retained_for_synthetic_robustness_only=all(gates.values()) and attribution_cpu <= 60,
                    acceptance_claim=False, production_cpu_ram_state_delta=0)
    return outcome, dict(format="apta-key-partial-attribution-h1-detail-1", fits=fits, rows=details), resource


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("samples", "coverage-detail", "coverage-summary", "validation", "probe", "i1-probe", "source-commit", "output-prefix"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    paths = [Path(args.output_prefix + suffix + ".json") for suffix in ("", "-detail", "-resource")]
    coverage.require(all(not p.exists() for p in paths), "refusing output overwrite")
    values = evaluate(args)
    for path, value in zip(paths, values):
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
    print(json.dumps(dict(gates=values[0]["scientific_and_static_resource_gates"], resource=values[2])))


if __name__ == "__main__":
    main()
