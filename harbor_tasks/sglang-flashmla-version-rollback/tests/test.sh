#!/usr/bin/env bash
set +e

TOTAL=0.0
CMAKE_FILE="/workspace/sglang/sgl-kernel/cmake/flashmla.cmake"
PY_FILE="/workspace/sglang/sgl-kernel/python/sgl_kernel/flash_mla.py"
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

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Both files must exist and Python must parse
if ! python3 -c "
import ast, sys
with open('$PY_FILE') as f:
    try:
        ast.parse(f.read())
    except SyntaxError as e:
        print(f'SyntaxError in flash_mla.py: {e}')
        sys.exit(1)
print('Python file OK')
"; then
    echo "GATE FAILED: syntax error in $PY_FILE"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
if [ ! -f "$CMAKE_FILE" ]; then
    echo "GATE FAILED: $CMAKE_FILE not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

echo ""
echo "=== Behavioral: GIT_TAG points to the older stable FlashMLA commit ==="
# [pr_diff] (0.25): cmake must reference the older stable FlashMLA version
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()
# The rolled-back GIT_TAG
if 'be055fb7df0090fde45f08e9cb5b8b4c0272da73' not in content:
    print('FAIL: GIT_TAG does not reference the stable commit')
    sys.exit(1)
# The broken newer tag must NOT be present
if '9804b12079e4c873514d3457aa588d3ccf40da28' in content:
    print('FAIL: Newer broken GIT_TAG still present')
    sys.exit(1)
print('PASS: GIT_TAG references older stable commit')
" 2>&1; then
    add_score 0.25 "behavioral"
    echo "SCORE: +0.25"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: Source files match the older FlashMLA layout ==="
# [pr_diff] (0.15): cmake must reference flat source files, not nested instantiation dirs
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()

# The older version uses these flat source paths
required_sources = [
    'csrc/smxx/get_mla_metadata.cu',
    'csrc/smxx/mla_combine.cu',
    'csrc/sm90/decode/dense/splitkv_mla.cu',
    'csrc/sm90/decode/sparse_fp8/splitkv_mla.cu',
]

# The newer version uses nested dirs (should NOT be present)
forbidden_sources = [
    'csrc/smxx/decode/get_decoding_sched_meta/get_decoding_sched_meta.cu',
    'csrc/smxx/decode/combine/combine.cu',
    'csrc/sm90/decode/dense/instantiations/',
    'csrc/sm90/decode/sparse_fp8/instantiations/',
]

ok = True
for src in required_sources:
    if src not in content:
        print(f'FAIL: Missing required source: {src}')
        ok = False

for src in forbidden_sources:
    if src in content:
        print(f'FAIL: Forbidden newer-version source found: {src}')
        ok = False

if ok:
    print('PASS')
else:
    sys.exit(1)
" 2>&1; then
    add_score 0.15 "behavioral"
    echo "SCORE: +0.15"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: SM103a patch targets flashmla_utils.h ==="
# [pr_diff] (0.10): Older FlashMLA uses csrc/flashmla_utils.h, not csrc/utils.h
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()
if 'flashmla_utils.h' in content and 'csrc/utils.h' not in content:
    print('PASS: Correctly references flashmla_utils.h')
else:
    print('FAIL: Should reference flashmla_utils.h, not utils.h')
    sys.exit(1)
" 2>&1; then
    add_score 0.10 "behavioral"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: Import error guards removed from Python functions ==="
# [pr_diff] (0.10): _flashmla_import_error guard must be removed from all 3 functions
if python3 -c "
import ast, sys

with open('$PY_FILE') as f:
    source = f.read()
    tree = ast.parse(source)

target_funcs = ['get_mla_metadata', 'flash_mla_with_kvcache', 'flash_mla_sparse_fwd']
found_guard = []

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in target_funcs:
        func_lines = source.split('\n')[node.lineno - 1 : node.end_lineno]
        func_src = '\n'.join(func_lines)
        if '_flashmla_import_error' in func_src:
            found_guard.append(node.name)

if found_guard:
    print(f'FAIL: Import error guards still present in: {found_guard}')
    sys.exit(1)
print('PASS: No import error guards in any of the 3 functions')
" 2>&1; then
    add_score 0.10 "behavioral"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: C++20 flags removed from compile options ==="
# [pr_diff] (0.05): Older FlashMLA does not require C++20 compilation
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()
if '-std=c++20' in content:
    print('FAIL: C++20 compile flags still present')
    sys.exit(1)
print('PASS: No C++20 flags')
" 2>&1; then
    add_score 0.05 "behavioral"
    echo "SCORE: +0.05"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: kerutils include path removed ==="
# [pr_diff] (0.05): Older FlashMLA does not have csrc/kerutils/include
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()
if 'kerutils' in content:
    print('FAIL: kerutils include path still present')
    sys.exit(1)
print('PASS: No kerutils include path')
" 2>&1; then
    add_score 0.05 "behavioral"
    echo "SCORE: +0.05"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Regression: Cutlass SM103a patch section preserved ==="
# [pr_diff] (0.10): The cutlass patching logic must survive the rollback
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()

# These are from the base commit's cutlass patch section which must be preserved
required = [
    'CUTLASS_ARCH_MMA_SM103_SUPPORTED',
    'CUTLASS_ARCH_MMA_SM103_ENABLED',
    'CUTLASS_ARCH_MMA_SM100A_ENABLED',
    'cutlass/arch/config.h',
    'SM103_FOUND',
    'compute_103a',
]

ok = True
for r in required:
    if r not in content:
        print(f'FAIL: Missing preserved cutlass element: {r}')
        ok = False

if ok:
    print('PASS: Cutlass SM103a patch section preserved')
else:
    sys.exit(1)
" 2>&1; then
    add_score 0.10 "regression"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Regression: Core cmake structure preserved ==="
# [pr_diff] (0.05): FetchContent, CUDA flags, extension sources, link libs
if python3 -c "
import sys
with open('$CMAKE_FILE') as f:
    content = f.read()

checks = [
    'FetchContent_Declare',
    'FetchContent_Populate(repo-flashmla)',
    'FLASHMLA_CUDA_FLAGS',
    '--expt-relaxed-constexpr',
    '--expt-extended-lambda',
    'flashmla_ops',
    'csrc/flashmla_extension.cc',
    'csrc/extension/sm90/dense_fp8/',
    'target_link_libraries(flashmla_ops',
    'install(TARGETS flashmla_ops',
    'SKBUILD_SABI_VERSION',
    'compute_90a',
    'compute_100a',
]

ok = True
for check in checks:
    if check not in content:
        print(f'FAIL: Missing expected cmake element: {check}')
        ok = False

if ok:
    print('PASS')
else:
    sys.exit(1)
" 2>&1; then
    add_score 0.05 "regression"
    echo "SCORE: +0.05"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Regression: Python functions have correct signatures and call torch.ops ==="
# [pr_diff] (0.10): Functions must retain their parameter signatures and dispatch to torch.ops
if python3 -c "
import ast, sys

with open('$PY_FILE') as f:
    source = f.read()
    tree = ast.parse(source)

# Expected function names -> minimum required parameter names (subset)
expected_sigs = {
    'get_mla_metadata': {'cache_seqlens', 'num_heads_k'},
    'flash_mla_with_kvcache': {'q', 'k_cache', 'block_table', 'head_dim_v', 'tile_scheduler_metadata'},
    'flash_mla_sparse_fwd': {'q', 'kv', 'indices', 'sm_scale'},
}

# Each function must call torch.ops.sgl_kernel.*
expected_ops = {
    'get_mla_metadata': 'get_mla_decoding_metadata',
    'flash_mla_with_kvcache': 'fwd_kvcache_mla',
    'flash_mla_sparse_fwd': 'sparse_prefill_fwd',
}

ok = True
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in expected_sigs:
        # Check parameter names
        param_names = {arg.arg for arg in node.args.args}
        missing = expected_sigs[node.name] - param_names
        if missing:
            print(f'FAIL: {node.name} missing parameters: {missing}')
            ok = False

        # Check function body calls torch.ops
        func_lines = source.split('\n')[node.lineno - 1 : node.end_lineno]
        func_src = '\n'.join(func_lines)
        op_name = expected_ops[node.name]
        if op_name not in func_src:
            print(f'FAIL: {node.name} does not dispatch to torch.ops.*{op_name}*')
            ok = False

if ok:
    print('PASS: All functions have correct signatures and dispatch to torch.ops')
else:
    sys.exit(1)
" 2>&1; then
    add_score 0.10 "regression"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Anti-gaming: File structure integrity ==="
# [static] (0.05): Files must not be stubbed — check line counts and structural depth
if python3 -c "
import os, sys

cmake_size = os.path.getsize('$CMAKE_FILE')
py_size = os.path.getsize('$PY_FILE')

with open('$CMAKE_FILE') as f:
    cmake_lines = len(f.readlines())
with open('$PY_FILE') as f:
    py_lines = len(f.readlines())

# The base cmake file is ~160 lines, fixed version ~120 lines. Stub would be ~30.
if cmake_size < 2000:
    print(f'FAIL: cmake file too small ({cmake_size} bytes)')
    sys.exit(1)
if cmake_lines < 80:
    print(f'FAIL: cmake file too few lines ({cmake_lines})')
    sys.exit(1)
if py_size < 2000:
    print(f'FAIL: Python file too small ({py_size} bytes)')
    sys.exit(1)
if py_lines < 80:
    print(f'FAIL: Python file too few lines ({py_lines})')
    sys.exit(1)

print(f'PASS: cmake={cmake_size}b/{cmake_lines}L, python={py_size}b/{py_lines}L')
" 2>&1; then
    add_score 0.05 "structural"
    echo "SCORE: +0.05"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== TOTAL: $TOTAL ==="

# Write final reward
echo "$TOTAL" > /logs/verifier/reward.txt
REWARD_JSON=$(python3 -c "
import json
d = json.loads('$REWARD_JSON')
d['reward'] = $TOTAL
print(json.dumps(d))
")
echo "$REWARD_JSON" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
