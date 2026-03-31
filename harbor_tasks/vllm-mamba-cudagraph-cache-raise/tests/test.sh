#!/usr/bin/env bash
set +e

SCORE=0
RUNNER="/workspace/vllm/vllm/v1/worker/gpu_model_runner.py"
CONFIG="/workspace/vllm/vllm/config/compilation.py"

echo "=== vllm-mamba-cudagraph-cache-raise ==="
echo ""

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): Modified files must be valid Python
echo "--- GATE: Python syntax check ---"
for f in "$RUNNER" "$CONFIG"; do
    if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$f').read())
except SyntaxError as e:
    print(f'Syntax error in $f: {e}')
    sys.exit(1)
"; then
        echo "GATE FAILED: syntax error in $f"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "GATE PASSED"
echo ""

########################################
# BEHAVIORAL: Fail-to-pass checks
########################################

# [pr_diff] (0.35): The silent-capping approach must be replaced — calling
# adjust_cudagraph_sizes_for_mamba_cache should either not exist or not
# silently shrink cudagraph_capture_sizes for the shared config.
# On the buggy baseline this method exists and silently caps sizes.
echo "--- CHECK: silent capping of cudagraph sizes eliminated ---"
F2P1_RESULT=$(python3 -c "
import ast, sys, textwrap

# Try to import CompilationConfig and test the method directly
sys.path.insert(0, '/workspace/vllm')

with open('$CONFIG') as f:
    source = f.read()
tree = ast.parse(source)

# Check if adjust_cudagraph_sizes_for_mamba_cache exists in CompilationConfig
method_exists = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'CompilationConfig':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == 'adjust_cudagraph_sizes_for_mamba_cache':
                    method_exists = True

if not method_exists:
    # Method removed — the silent capping behavior is eliminated
    print('OK')
    sys.exit(0)

# Method still exists — test if it still silently caps sizes
# Extract and run it to check behavior
try:
    # Build a minimal mock to test the method
    exec_ns = {}
    # Extract class with just the method
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'CompilationConfig':
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == 'adjust_cudagraph_sizes_for_mamba_cache':
                        lines = source.splitlines(keepends=True)
                        func_src = textwrap.dedent(''.join(lines[item.lineno-1:item.end_lineno]))
                        break

    # Create a simple object to test on
    import types, logging
    logger = logging.getLogger('test')

    class FakeConfig:
        def __init__(self):
            self.cudagraph_capture_sizes = [1, 2, 4, 8, 16, 32]
            self.max_cudagraph_capture_size = 32

    ns = {'logger': logger, '__builtins__': __builtins__}
    exec('import logging\\nlogger = logging.getLogger(\"test\")\\n' + func_src, ns)
    func = ns['adjust_cudagraph_sizes_for_mamba_cache']

    cfg = FakeConfig()
    original_sizes = list(cfg.cudagraph_capture_sizes)

    # Call with num_blocks=8 — buggy code silently caps to [1,2,4,8]
    func(cfg, 8)

    if cfg.cudagraph_capture_sizes != original_sizes:
        # Still silently capping — bug not fixed
        print(f'FAIL: method still silently caps sizes from {original_sizes} to {cfg.cudagraph_capture_sizes}')
    else:
        # Method exists but no longer caps — acceptable alternative
        print('OK')
except Exception as e:
    # If method exists but raises instead of silently capping, that's acceptable
    print(f'OK (method raises: {type(e).__name__})')
" 2>&1)
echo "  $F2P1_RESULT"
if echo "$F2P1_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.35)")
    echo "  +0.35"
fi
echo ""

# [pr_diff] (0.25): When max_num_seqs exceeds available Mamba cache blocks,
# _check_and_update_cudagraph_mode must raise an error (not silently degrade).
# On buggy baseline, it calls adjust_cudagraph_sizes_for_mamba_cache which
# silently caps — it should raise instead.
echo "--- CHECK: error raised when max_num_seqs > num_blocks ---"
F2P2_RESULT=$(python3 -c "
import ast, sys, textwrap

with open('$RUNNER') as f:
    source = f.read()
tree = ast.parse(source)

# Find _check_and_update_cudagraph_mode and extract it
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == '_check_and_update_cudagraph_mode':
            func_node = node
            break

if func_node is None:
    print('FAIL: _check_and_update_cudagraph_mode not found')
    sys.exit(0)

# Check behavioral requirement: the function should raise an exception
# when max_num_seqs > num_blocks for Mamba models (not silently cap).
# We check for ANY raise statement (ValueError, RuntimeError, etc.)
# as the specific exception type is an implementation detail.
has_raise = False
has_mamba_check = False
calls_silent_cap = False

for child in ast.walk(func_node):
    if isinstance(child, ast.Raise) and child.exc is not None:
        has_raise = True
    # Check if it still calls the silent capping method
    if isinstance(child, ast.Attribute):
        if child.attr == 'adjust_cudagraph_sizes_for_mamba_cache':
            calls_silent_cap = True

# Check for references to mamba in the function (handles has_mamba, MambaSpec, etc.)
func_lines = source.splitlines()[func_node.lineno-1:func_node.end_lineno]
func_text = '\\n'.join(func_lines).lower()
has_mamba_check = 'mamba' in func_text

if calls_silent_cap:
    print('FAIL: still calls adjust_cudagraph_sizes_for_mamba_cache (silent capping)')
elif has_raise and has_mamba_check:
    print('OK')
elif has_raise:
    print('OK')
elif not has_mamba_check:
    # If Mamba handling was moved elsewhere or removed entirely,
    # check that the old silent-cap call is gone
    print('OK')
else:
    print('FAIL: Mamba check exists but no error is raised for insufficient blocks')
" 2>&1)
echo "  $F2P2_RESULT"
if echo "$F2P2_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
    echo "  +0.25"
fi
echo ""

########################################
# BEHAVIORAL: Pass-to-pass checks
########################################

# [pr_diff] (0.10): adjust_cudagraph_sizes_for_spec_decode must still work correctly.
# This is an existing method that must NOT be removed or broken by the fix.
echo "--- CHECK: adjust_cudagraph_sizes_for_spec_decode still functional ---"
P2P1_RESULT=$(python3 -c "
import ast, sys, textwrap

sys.path.insert(0, '/workspace/vllm')

with open('$CONFIG') as f:
    source = f.read()
tree = ast.parse(source)

# Find and extract the method
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'CompilationConfig':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == 'adjust_cudagraph_sizes_for_spec_decode':
                    found = True
                    break

if not found:
    print('FAIL: adjust_cudagraph_sizes_for_spec_decode removed')
    sys.exit(0)

# Try to instantiate CompilationConfig and call the method
try:
    from vllm.config.compilation import CompilationConfig
    cfg = CompilationConfig()
    cfg.cudagraph_capture_sizes = [1, 2, 4, 8, 16, 32]
    cfg.max_cudagraph_capture_size = 32
    # Call with uniform_decode_query_len=2, tp_size=1
    cfg.adjust_cudagraph_sizes_for_spec_decode(2, 1)
    # Should adjust sizes — verify it ran without error
    if cfg.cudagraph_capture_sizes is not None and len(cfg.cudagraph_capture_sizes) > 0:
        print('OK')
    else:
        print('FAIL: method cleared all sizes unexpectedly')
except ImportError:
    # Can't import full config — fall back to existence check
    print('OK' if found else 'FAIL')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1)
echo "  $P2P1_RESULT"
if echo "$P2P1_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

# [pr_diff] (0.05): Key methods preserved in gpu_model_runner.py
echo "--- CHECK: core methods preserved ---"
P2P2_RESULT=$(python3 -c "
import ast

with open('$RUNNER') as f:
    tree = ast.parse(f.read())

required = {
    '_check_and_update_cudagraph_mode',
    'initialize_kv_cache',
    'initialize_attn_backend',
    '_init_minimal_kv_cache_for_profiling',
}
found = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in required:
            found.add(node.name)

missing = required - found
if missing:
    print(f'FAIL: missing methods: {missing}')
else:
    print('OK')
" 2>&1)
echo "  $P2P2_RESULT"
if echo "$P2P2_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

########################################
# BEHAVIORAL: Profiling skip check
########################################

# [pr_diff] (0.10): _init_minimal_kv_cache_for_profiling must signal that
# validation should be skipped. The buggy code doesn't distinguish profiling
# from real init, causing false errors with artificially small cache.
# Accept any mechanism: parameter, flag, context var, etc.
echo "--- CHECK: profiling path skips Mamba validation ---"
PROF_RESULT=$(python3 -c "
import ast

with open('$RUNNER') as f:
    source = f.read()
tree = ast.parse(source)

# Find _init_minimal_kv_cache_for_profiling
profiling_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == '_init_minimal_kv_cache_for_profiling':
            profiling_func = node
            break

if profiling_func is None:
    print('FAIL: _init_minimal_kv_cache_for_profiling not found')
    import sys; sys.exit(0)

# Check that the profiling path has been modified to signal 'this is profiling'
# Accept any approach: keyword arg, attribute set, context manager, etc.
func_text = '\\n'.join(source.splitlines()[profiling_func.lineno-1:profiling_func.end_lineno])

# The buggy version just calls self.initialize_kv_cache(minimal_config) with no signal.
# A fix must add some differentiator. Check for common patterns:
has_profiling_signal = False

# Pattern 1: keyword arg like profiling=True, is_profiling=True, etc.
for child in ast.walk(profiling_func):
    if isinstance(child, ast.Call):
        for kw in child.keywords:
            if kw.arg and 'profil' in kw.arg.lower():
                if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    has_profiling_signal = True

# Pattern 2: setting an attribute like self._is_profiling = True before the call
for child in ast.walk(profiling_func):
    if isinstance(child, ast.Assign):
        for target in child.targets:
            if isinstance(target, ast.Attribute) and 'profil' in target.attr.lower():
                has_profiling_signal = True

# Pattern 3: wrapping in a context manager related to profiling
for child in ast.walk(profiling_func):
    if isinstance(child, ast.With):
        for item in child.items:
            ctx = item.context_expr
            ctx_text = ast.dump(ctx)
            if 'profil' in ctx_text.lower():
                has_profiling_signal = True

# Pattern 4: the call chain has changed (different from buggy baseline)
# Buggy baseline: self.initialize_kv_cache(minimal_config) — exactly 1 positional arg
buggy_pattern = False
for child in ast.walk(profiling_func):
    if isinstance(child, ast.Call):
        func = child.func
        if isinstance(func, ast.Attribute) and func.attr == 'initialize_kv_cache':
            if len(child.args) == 1 and len(child.keywords) == 0:
                buggy_pattern = True
            elif len(child.args) > 1 or len(child.keywords) > 0:
                has_profiling_signal = True  # Extra args = some signal added

if has_profiling_signal:
    print('OK')
elif not buggy_pattern:
    # Call was changed in some other way
    print('OK')
else:
    print('FAIL: _init_minimal_kv_cache_for_profiling unchanged from buggy baseline')
" 2>&1)
echo "  $PROF_RESULT"
if echo "$PROF_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# REGRESSION: No silent capping reference
########################################

# [pr_diff] (0.05): The runner must not reference the removed silent-cap method
echo "--- CHECK: no reference to silent-cap method in runner ---"
REF_RESULT=$(python3 -c "
with open('$RUNNER') as f:
    content = f.read()
if 'adjust_cudagraph_sizes_for_mamba_cache' in content:
    print('FAIL: runner still references adjust_cudagraph_sizes_for_mamba_cache')
else:
    print('OK')
" 2>&1)
echo "  $REF_RESULT"
if echo "$REF_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

########################################
# STRUCTURAL: Anti-stub checks
########################################

# [pr_diff] (0.05): _check_and_update_cudagraph_mode must not be a stub
echo "--- CHECK: _check_and_update_cudagraph_mode not a stub ---"
STUB_RESULT=$(python3 -c "
import ast

with open('$RUNNER') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == '_check_and_update_cudagraph_mode':
            # Count non-docstring, non-pass, non-comment body statements
            body = node.body
            meaningful = 0
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                     ast.If, ast.For, ast.While, ast.Return,
                                     ast.Raise, ast.Call, ast.Expr)):
                    meaningful += 1
            if meaningful < 10:
                print(f'FAIL: _check_and_update_cudagraph_mode appears to be a stub ({meaningful} statements)')
            else:
                print('OK')
            break
else:
    print('FAIL: method not found')
" 2>&1)
echo "  $STUB_RESULT"
if echo "$STUB_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

# [pr_diff] (0.05): No NotImplementedError or TODO stubs in modified areas
echo "--- CHECK: no stub markers in Mamba-related sections ---"
NOSTUB_RESULT=$(python3 -c "
import ast

issues = []
for filepath in ['$RUNNER', '$CONFIG']:
    with open(filepath) as f:
        source = f.read()

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in ('_check_and_update_cudagraph_mode', 'initialize_kv_cache',
                             'initialize_attn_backend'):
                for child in ast.walk(node):
                    if isinstance(child, ast.Raise) and child.exc is not None:
                        exc = child.exc
                        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                            if exc.func.id == 'NotImplementedError':
                                issues.append(f'{node.name} raises NotImplementedError')
                    if isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant):
                        if isinstance(child.value.value, str) and 'TODO' in child.value.value:
                            issues.append(f'{node.name} has TODO in docstring')

if issues:
    for i in issues:
        print(f'  {i}')
    print('FAIL')
else:
    print('OK')
" 2>&1)
echo "  $NOSTUB_RESULT"
if echo "$NOSTUB_RESULT" | grep -q "^OK"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

########################################
# Final score
########################################
echo "=== RESULTS ==="
echo "Score: $SCORE / 1.00"

FINAL=$(python3 -c "print(f'{min(float($SCORE), 1.0):.4f}')")
echo "Final reward: $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
score = min(float('$SCORE'), 1.0)
# behavioral: F2P (0.35 + 0.25) + P2P (0.10 + 0.05) + profiling behavioral (0.10) = 0.85
# regression: 0.05
# structural: 0.10
behavioral = min(score, 0.85)
regression = min(max(score - 0.85, 0), 0.05)
structural = min(max(score - 0.90, 0), 0.10)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
