#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
TARGET="/workspace/sglang/python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"
REWARD_JSON="{}"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
    REWARD_JSON=$(python3 -c "
import json
d = json.loads('$REWARD_JSON')
d['$2'] = d.get('$2', 0) + $1
print(json.dumps(d))
")
}

echo "=== GATE: File exists and is non-empty ==="
# [pr_diff] (gate): Target file must exist
if [ ! -s "$TARGET" ]; then
    echo "GATE FAILED: $TARGET missing or empty"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

# ---- Helper: strip C/C++ comments from the file for robust analysis ----
STRIPPED=$(python3 -c "
import re, sys
with open('$TARGET') as f:
    src = f.read()
# Remove block comments
src = re.sub(r'/\*.*?\*/', '', src, flags=re.DOTALL)
# Remove line comments
src = re.sub(r'//[^\n]*', '', src)
print(src)
")

# ---- Anti-stub gate: file must have real content ----
echo ""
echo "=== GATE: Anti-stub (file has real CUDA content) ==="
# [pr_diff] (gate): File must be substantial, not a stub
NLINES=$(echo "$STRIPPED" | grep -cE '\S' || true)
if [ "$NLINES" -lt 80 ]; then
    echo "GATE FAILED: Only $NLINES non-empty lines (expected >=80 for a real kernel)"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: $NLINES non-empty lines"

echo ""
echo "=== Behavioral (F2P): Kernel uses 2D grid dispatch via blockIdx.y (0.30) ==="
# [pr_diff] (0.30): Kernel must use blockIdx.y inside the kernel function body
# to dispatch between Q and K processing. The base code has NO blockIdx.y usage.
# WHY structural: CUDA C++ (.cuh) — cannot compile/run without nvcc + GPU.
# Check: blockIdx.y appears in non-comment code AND is used in a conditional or assignment
BIDY_COUNT=$(echo "$STRIPPED" | grep -cP 'blockIdx\s*\.\s*y' || true)
BIDY_IN_COND=$(echo "$STRIPPED" | grep -cP '(if|switch|=)\s*.*blockIdx\s*\.\s*y' || true)
if [ "$BIDY_COUNT" -ge 1 ] && [ "$BIDY_IN_COND" -ge 1 ]; then
    echo "PASS: blockIdx.y used in conditional/assignment ($BIDY_COUNT occurrences)"
    add_score 0.30 "behavioral"
else
    echo "FAIL: blockIdx.y not found in meaningful context (count=$BIDY_COUNT, in_cond=$BIDY_IN_COND)"
fi

echo ""
echo "=== Behavioral (F2P): Shared memory halved from 64 ==="
# [pr_diff] (0.15): Shared memory must be reduced. The base code uses shared_memory[64].
# Accept any shared buffer size <= 32 (not exactly 32 — allow alternatives).
# WHY structural: CUDA C++ code.
SMEM_OK=$(echo "$STRIPPED" | python3 -c "
import re, sys
src = sys.stdin.read()
# Find __shared__ float arrays or float shared_memory[N] declarations
# Accept various naming conventions
matches = re.findall(r'(?:__shared__\s+float\s+\w+\s*\[\s*(\d+)\s*\]|float\s+shared_memory\s*\[\s*(\d+)\s*\])', src)
if not matches:
    sys.exit(1)
for m in matches:
    size = int(m[0] or m[1])
    if size <= 32:
        print(f'Found shared buffer of size {size}')
        sys.exit(0)
sys.exit(1)
" 2>&1) && SMEM_PASS=1 || SMEM_PASS=0
if [ "$SMEM_PASS" -eq 1 ]; then
    echo "PASS: $SMEM_OK"
    add_score 0.15 "behavioral"
else
    echo "FAIL: No shared memory buffer <= 32 found (base uses 64)"
fi

echo ""
echo "=== Behavioral (F2P): Dual register vectors eliminated ==="
# [pr_diff] (0.15): The kernel should NOT simultaneously hold separate Q and K data vectors.
# Base code has v_q, v_k, v_q_weight, v_k_weight, v_q_out, v_k_out — six vec_t variables.
# After fix, only generic names should remain (e.g. v_data, v_weight, v_out or similar).
# Check: count distinct vec_t variable declarations in kernel body. Should be <=3 (was 6).
# WHY structural: CUDA C++ code.
VEC_DECLS=$(echo "$STRIPPED" | python3 -c "
import re, sys
src = sys.stdin.read()
# Find vec_t variable declarations (not pointer casts)
decls = re.findall(r'\bvec_t\s+(\w+)\s*;', src)
print(len(decls))
print(' '.join(decls))
")
VEC_COUNT=$(echo "$VEC_DECLS" | head -1)
VEC_NAMES=$(echo "$VEC_DECLS" | tail -1)
if [ "$VEC_COUNT" -le 3 ]; then
    echo "PASS: $VEC_COUNT vec_t declarations (was 6 in base): $VEC_NAMES"
    add_score 0.15 "behavioral"
else
    echo "FAIL: $VEC_COUNT vec_t declarations — still holding dual Q/K vectors: $VEC_NAMES"
fi

echo ""
echo "=== Behavioral (F2P): 2D grid launch ==="
# [pr_diff] (0.15): LaunchKernel must use a 2D grid with second dim = 2.
# Accept: dim3(N, 2), dim3 grid(N, 2), dim3{N, 2}, or any dim3 construction with 2.
# WHY structural: CUDA C++ code.
DIM3_OK=$(echo "$STRIPPED" | python3 -c "
import re, sys
src = sys.stdin.read()
# Look for dim3 construction near LaunchKernel or with a literal 2 as second arg
# Pattern: dim3 followed by ( or { with two args where second is 2
if re.search(r'dim3\s*[\({]\s*[^,]+,\s*2\s*[\)}]', src):
    print('dim3 with y=2 found')
    sys.exit(0)
# Also accept: LaunchKernel with dim3 in arguments
if re.search(r'LaunchKernel\s*\(.*dim3', src):
    print('LaunchKernel with dim3 found')
    sys.exit(0)
sys.exit(1)
" 2>&1) && DIM3_PASS=1 || DIM3_PASS=0
if [ "$DIM3_PASS" -eq 1 ]; then
    echo "PASS: $DIM3_OK"
    add_score 0.15 "behavioral"
else
    echo "FAIL: No 2D grid launch (dim3 with y=2) found"
fi

echo ""
echo "=== Pass-to-pass: rms helper function still exists ==="
# [pr_diff] (0.10): The rms() helper must still exist (not removed)
# Accept any rms function that takes packed_t args and returns packed_t
RMS_OK=$(echo "$STRIPPED" | grep -cP '\brms\s*\(' || true)
RMS_BODY=$(echo "$STRIPPED" | python3 -c "
import re, sys
src = sys.stdin.read()
# Find rms function with a body (not just declaration)
if re.search(r'\brms\s*\([^)]*\)\s*\{[^}]+\}', src, re.DOTALL):
    sys.exit(0)
sys.exit(1)
" 2>&1) && RMS_HAS_BODY=1 || RMS_HAS_BODY=0
if [ "$RMS_OK" -ge 1 ] && [ "$RMS_HAS_BODY" -eq 1 ]; then
    echo "PASS: rms helper function present with body"
    add_score 0.10 "regression"
else
    echo "FAIL: rms helper function missing or empty"
fi

echo ""
echo "=== Pass-to-pass: QKNormAcrossHeadsKernel struct still exists ==="
# [pr_diff] (0.05): Launcher struct must still exist with a run method
STRUCT_OK=$(echo "$STRIPPED" | grep -cP 'struct\s+QKNormAcrossHeadsKernel' || true)
RUN_OK=$(echo "$STRIPPED" | python3 -c "
import re, sys
src = sys.stdin.read()
# Match 'void' followed by 'run(' possibly across lines (static void\n  run(...))
if re.search(r'\bvoid\s+run\s*\(', src):
    sys.exit(0)
sys.exit(1)
" 2>&1) && RUN_FOUND=1 || RUN_FOUND=0
RUN_OK=$RUN_FOUND
if [ "$STRUCT_OK" -ge 1 ] && [ "$RUN_OK" -ge 1 ]; then
    echo "PASS: QKNormAcrossHeadsKernel struct with run() present"
    add_score 0.05 "regression"
else
    echo "FAIL: QKNormAcrossHeadsKernel struct or run() missing"
fi

echo ""
echo "=== Structural: rms parameters are const-qualified ==="
# [pr_diff] (0.10): rms() parameters should be const (read-only).
# Accept: const ref, const value, const pointer — any const qualification.
# WHY structural: CUDA C++ code.
CONST_OK=$(echo "$STRIPPED" | python3 -c "
import re, sys
src = sys.stdin.read()
# Find the rms function signature and check for const on parameters
match = re.search(r'\brms\s*\(([^)]+)\)', src)
if not match:
    sys.exit(1)
params = match.group(1)
# Count non-return-type params (skip first if it's template stuff)
# The key params after any template: val/weight should be const
param_list = [p.strip() for p in params.split(',')]
const_params = sum(1 for p in param_list if 'const' in p)
# At least the data params should be const (val and weight)
if const_params >= 2:
    print(f'const on {const_params} params')
    sys.exit(0)
sys.exit(1)
" 2>&1) && CONST_PASS=1 || CONST_PASS=0
if [ "$CONST_PASS" -eq 1 ]; then
    echo "PASS: $CONST_OK"
    add_score 0.10 "structural"
else
    echo "FAIL: rms parameters not const-qualified"
fi

echo ""
echo "=== TOTAL: $TOTAL ==="
REWARD_JSON=$(python3 -c "
import json
d = json.loads('$REWARD_JSON')
d['reward'] = $TOTAL
print(json.dumps(d))
")
echo "$TOTAL" > /logs/verifier/reward.txt
echo "$REWARD_JSON" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
