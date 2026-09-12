#!/usr/bin/env bash
set -euo pipefail
out=/mnt/d/AI/LIBAPTA/libapta-audio-dsp-20260904/build/key-joint-e2-20260912
root=/home/daniel/apta-joint-e2-20260912
export OPENBLAS_NUM_THREADS=1
export ASAN_OPTIONS=detect_leaks=1:halt_on_error=1
export UBSAN_OPTIONS=halt_on_error=1
mkdir -p "$root/source"
tar -xf "$out/source.tar" -C "$root/source"
cd "$root/source/tools"
python3 -m unittest test_apta_key_joint_pcm test_apta_key_pcm_candidate > "$out/tests.log" 2>&1
for variant in default candidate sanitize; do
 APTA_COVERAGE_PROBE=/home/daniel/apta-coverage-20260910/$variant/tests/apta_key_chroma_probe python3 -m unittest test_apta_key_coverage_diagnostic > "$out/coverage-$variant.log" 2>&1
done
for suffix in result repeat; do
 python3 apta_key_joint_pcm_screen.py --probe /home/daniel/apta-coverage-20260910/default/tests/apta_key_chroma_probe --candidate-probe /home/daniel/apta-coverage-20260910/candidate/tests/apta_key_chroma_probe --sanitize-probe /home/daniel/apta-coverage-20260910/sanitize/tests/apta_key_chroma_probe --source-commit 3ca838a87d0c044e987d06125bc1a5e1efd27aa6 --output-prefix "$out/$suffix" > "$out/$suffix.log" 2> "$out/$suffix.stderr"
done
cmp "$out/result.json" "$out/repeat.json"
cat "$out/result.log" "$out/repeat.log"
