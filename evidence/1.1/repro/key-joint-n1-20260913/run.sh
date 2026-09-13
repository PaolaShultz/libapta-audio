#!/usr/bin/env bash
# Reproduce in a new output directory. No old evidence is overwritten.
set -euo pipefail
if test "$#" -ne 2; then
 echo 'usage: run.sh ABSOLUTE_NEW_OUTPUT_DIR ABSOLUTE_NATIVE_CHROMA_PROBE' >&2
 exit 2
fi
out=$1
probe=$2
case "$out" in /*) ;; *) exit 2;; esac
case "$probe" in /*) ;; *) exit 2;; esac
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$root"
mkdir "$out"
uv venv --python 3.13 "$out/venv"
uv pip install --python "$out/venv/bin/python" numpy==2.5.2 scipy==1.18.1
py="$out/venv/bin/python"
export OPENBLAS_NUM_THREADS=1
"$py" tools/build_apta_nnls_n1.py --output "$out/kernel" > "$out/build.log"
export APTA_NNLS_N1_LIBRARY="$out/kernel/libapta_nnls_n1.so"
export APTA_COVERAGE_PROBE="$probe"
export PYTHONPATH="$root/tools"
sha=$(git rev-parse HEAD)
"$py" -m unittest test_apta_key_joint_a1 test_apta_key_joint_n1 test_apta_key_joint_pcm test_apta_key_pcm_candidate test_apta_key_coverage_diagnostic > "$out/tests.log" 2>&1
"$py" tools/apta_key_joint_n1_numerics.py --output-dir "$out/numerical-proof" > "$out/numerical.log"
for suffix in result repeat; do
 "$py" tools/apta_key_joint_n1_screen.py --probe "$probe" --candidate-probe "$probe" --sanitize-probe "$probe" --source-commit "$sha" --output-prefix "$out/n1-$suffix" > "$out/n1-$suffix.log" 2> "$out/n1-$suffix.stderr"
 "$py" tools/apta_key_joint_a1_screen.py --instrument N1 --bank fresh --manifest evidence/1.1/repro/key-joint-n1-20260913/a1-fresh-manifest.json --probe "$probe" --source-commit "$sha" --output-prefix "$out/n1-fresh-$suffix" > "$out/n1-fresh-$suffix.log" 2> "$out/n1-fresh-$suffix.stderr"
 for bank in regression fresh; do
  if test "$bank" = regression; then
   manifest=evidence/1.1/key-joint-pcm-e2-20260912.json
   reference="$out/n1-result.json"
  else
   manifest=evidence/1.1/repro/key-joint-n1-20260913/a1-fresh-manifest.json
   reference="$out/n1-fresh-result.json"
  fi
  "$py" tools/apta_key_joint_a1_screen.py --instrument A1 --bank "$bank" --manifest "$manifest" --probe "$probe" --source-commit "$sha" --n1-report "$reference" --output-prefix "$out/a1-$bank-$suffix" > "$out/a1-$bank-$suffix.log" 2> "$out/a1-$bank-$suffix.stderr"
 done
done
for name in n1 n1-fresh a1-regression a1-fresh; do
 cmp "$out/$name-result.json" "$out/$name-repeat.json"
done
"$py" tools/apta_key_joint_n1_attribution.py --report "$out/n1-result.json" --probe "$probe" --output "$out/attribution.json" > "$out/attribution.log"
