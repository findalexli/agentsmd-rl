#!/usr/bin/env bash
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Source annotations for traceability:
# [pr_diff] (0.35): del long_lived_tensors, hf_named_tensors in update_weights loop
# [pr_diff] (0.25): torch.cuda.ipc_collect() called inside weight chunk loop
# [pr_diff] (0.15): torch.cuda.ipc_collect() called after dist.barrier()
# [repo_tests] (0.10): Upstream test suite regression check (CPU-safe subset)
# [static] (0.10): Anti-stub: substantial implementation retained
# [agent_config] (0.05): No wildcard imports - .claude/skills/add-tests-and-ci/SKILL.md:45-48 @ 08b201bd
# [agent_config] (0.05): No bare print() - .claude/skills/add-tests-and-ci/SKILL.md:50-52 @ 08b201bd

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_del_both_tensors]=0.35
WEIGHTS[behavioral_ipc_collect_loop]=0.25
WEIGHTS[behavioral_ipc_collect_after_barrier]=0.15
WEIGHTS[regression_upstream_tests]=0.10
WEIGHTS[antistub]=0.10
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral_del_both_tensors behavioral_ipc_collect_loop behavioral_ipc_collect_after_barrier regression_upstream_tests antistub config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# Gate variable - structural checks only count if behavioral passes
BEHAVIORAL_PASS=0
TOTAL_BEHAVIORAL=0

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- PRIMARY 1 (35%): Behavioral - both tensors deleted in loop ----------
# [pr_diff]: Lines 164-165 @ 19ab6ce - del long_lived_tensors, hf_named_tensors added
python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the update_weights method
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weights":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: update_weights function not found")
    sys.exit(1)

# Look for del statement that deletes BOTH long_lived_tensors AND hf_named_tensors
found_del_long_lived = False
found_del_hf = False
found_in_loop = False

# Walk the AST to find for loops within update_weights
for node in ast.walk(func_node):
    if isinstance(node, ast.For):
        # This is the loop body - check for del statements inside it
        for child in ast.walk(node):
            if isinstance(child, ast.Delete):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "long_lived_tensors":
                            found_del_long_lived = True
                        elif target.id == "hf_named_tensors":
                            found_del_hf = True
                    elif isinstance(target, ast.Tuple):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                if elt.id == "long_lived_tensors":
                                    found_del_long_lived = True
                                elif elt.id == "hf_named_tensors":
                                    found_del_hf = True
        # Also check for loop body's immediate children (more precise)
        # Check that the del happens AFTER ray.get
        has_ray_get_before = False
        for stmt in node.body:
            if isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    if isinstance(stmt.value.func, ast.Attribute):
                        if stmt.value.func.attr == "get":
                            has_ray_get_before = True
            if isinstance(stmt, ast.Delete) and has_ray_get_before:
                found_in_loop = True

# Check if both are deleted somewhere in the function
if found_del_long_lived and found_del_hf and found_in_loop:
    print("BEHAVIORAL PASS: Both long_lived_tensors and hf_named_tensors deleted in loop after ray.get")
    sys.exit(0)
else:
    if not found_del_long_lived:
        print("BEHAVIORAL FAIL: long_lived_tensors not deleted in loop")
    elif not found_del_hf:
        print("BEHAVIORAL FAIL: hf_named_tensors not deleted in loop")
    else:
        print("BEHAVIORAL FAIL: deletions not in correct location (must be after ray.get in loop)")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_del_both_tensors]=1
    echo "TEST behavioral_del_both_tensors: PASS"
else
    echo "TEST behavioral_del_both_tensors: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - torch.cuda.ipc_collect() called inside loop ----------
# [pr_diff]: Line 166 @ 19ab6ce - torch.cuda.ipc_collect() added inside loop
python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find update_weights and check for ipc_collect in the for loop
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weights":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: update_weights function not found")
    sys.exit(1)

# Look for for loop with IPC collect
found_collect_in_loop = False
found_after_del = False

for node in ast.walk(func_node):
    if isinstance(node, ast.For):
        # Check if this loop contains torch.cuda.ipc_collect() call
        has_del = False
        has_collect = False
        del_line = 0
        collect_line = 0

        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.Delete):
                has_del = True
                del_line = stmt.lineno
            if isinstance(stmt, ast.Expr):
                expr = stmt.value
                if isinstance(expr, ast.Call):
                    # Check for torch.cuda.ipc_collect()
                    if isinstance(expr.func, ast.Attribute):
                        if expr.func.attr == "ipc_collect":
                            # Check parent is torch.cuda
                            if isinstance(expr.func.value, ast.Attribute):
                                if isinstance(expr.func.value.value, ast.Name):
                                    if expr.func.value.value.id == "torch" and expr.func.value.attr == "cuda":
                                        has_collect = True
                                        collect_line = stmt.lineno

        if has_del and has_collect and collect_line > del_line:
            found_collect_in_loop = True
            found_after_del = True

if found_collect_in_loop and found_after_del:
    print("BEHAVIORAL PASS: torch.cuda.ipc_collect() called in loop after del statements")
    sys.exit(0)
else:
    if not found_collect_in_loop:
        print("BEHAVIORAL FAIL: torch.cuda.ipc_collect() not found in loop")
    elif not found_after_del:
        print("BEHAVIORAL FAIL: torch.cuda.ipc_collect() not after del statements")
    else:
        print("BEHAVIORAL FAIL: IPC collect not properly placed")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_ipc_collect_loop]=1
    echo "TEST behavioral_ipc_collect_loop: PASS"
else
    echo "TEST behavioral_ipc_collect_loop: FAIL"
fi

# ---------- PRIMARY 3 (15%): Behavioral - ipc_collect after barrier ----------
# [pr_diff]: Lines 169-171 @ 19ab6ce - torch.cuda.ipc_collect() added after dist.barrier()
python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find update_weights
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weights":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: update_weights function not found")
    sys.exit(1)

# Find dist.barrier call and check for ipc_collect after it
barrier_line = 0
collect_after_barrier = False

for stmt in func_node.body:
    if isinstance(stmt, ast.Expr):
        expr = stmt.value
        if isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Attribute):
                if expr.func.attr == "barrier":
                    if isinstance(expr.func.value, ast.Name):
                        if expr.func.value.id == "dist":
                            barrier_line = stmt.lineno

    # Check for ipc_collect after we found the barrier
    if barrier_line > 0 and isinstance(stmt, ast.Expr):
        expr = stmt.value
        if isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Attribute):
                if expr.func.attr == "ipc_collect":
                    if isinstance(expr.func.value, ast.Attribute):
                        if isinstance(expr.func.value.value, ast.Name):
                            if expr.func.value.value.id == "torch" and expr.func.value.attr == "cuda":
                                if stmt.lineno > barrier_line:
                                    collect_after_barrier = True

if collect_after_barrier:
    print("BEHAVIORAL PASS: torch.cuda.ipc_collect() called after dist.barrier()")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: torch.cuda.ipc_collect() not found after dist.barrier()")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_ipc_collect_after_barrier]=1
    echo "TEST behavioral_ipc_collect_after_barrier: PASS"
else
    echo "TEST behavioral_ipc_collect_after_barrier: FAIL"
fi

# Calculate if behavioral passes for gating
calculate_behavioral() {
    python3 -c "
weights = {'behavioral_del_both_tensors': ${WEIGHTS[behavioral_del_both_tensors]}, 'behavioral_ipc_collect_loop': ${WEIGHTS[behavioral_ipc_collect_loop]}, 'behavioral_ipc_collect_after_barrier': ${WEIGHTS[behavioral_ipc_collect_after_barrier]}}
results = {'behavioral_del_both_tensors': ${RESULTS[behavioral_del_both_tensors]}, 'behavioral_ipc_collect_loop': ${RESULTS[behavioral_ipc_collect_loop]}, 'behavioral_ipc_collect_after_barrier': ${RESULTS[behavioral_ipc_collect_after_barrier]}}
score = sum(weights[k] * results[k] for k in weights if k.startswith('behavioral'))
print(f'{score:.2f}')
"
}

TOTAL_BEHAVIORAL=$(calculate_behavioral)
echo "TOTAL_BEHAVIORAL: $TOTAL_BEHAVIORAL"

# Check if at least 2 of 3 behavioral tests pass (threshold >= 50% of behavioral weight)
BEHAVIORAL_PASS_COUNT=$((RESULTS[behavioral_del_both_tensors] + RESULTS[behavioral_ipc_collect_loop] + RESULTS[behavioral_ipc_collect_after_barrier]))
if [ $BEHAVIORAL_PASS_COUNT -ge 2 ]; then
    BEHAVIORAL_PASS=1
    echo "BEHAVIORAL GATE: PASS (${BEHAVIORAL_PASS_COUNT}/3 tests passed)"
else
    BEHAVIORAL_PASS=0
    echo "BEHAVIORAL GATE: FAIL (${BEHAVIORAL_PASS_COUNT}/3 tests passed)"
fi

# ---------- REGRESSION (10%): Upstream tests (skip if behavioral fails) ----------
# [repo_tests]: Check that upstream function still has correct structure
if [ $BEHAVIORAL_PASS -eq 1 ]; then
    echo "=== Regression: upstream function structure ==="
    python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

try:
    with open(TARGET) as f:
        source = f.read()
    tree = ast.parse(source)

    # Check that _send_to_colocated_engine still exists and has proper structure
    found_send_fn = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_send_to_colocated_engine":
            found_send_fn = True
            # Check it returns a tuple
            has_return = False
            for child in ast.walk(node):
                if isinstance(child, ast.Return):
                    if isinstance(child.value, ast.Tuple):
                        has_return = True
            if has_return:
                print("REGRESSION PASS: _send_to_colocated_engine exists with proper return structure")
                sys.exit(0)
            else:
                print("REGRESSION FAIL: _send_to_colocated_engine missing proper return")
                sys.exit(1)

    if not found_send_fn:
        print("REGRESSION FAIL: _send_to_colocated_engine function not found")
        sys.exit(1)
except Exception as e:
    print(f"REGRESSION SKIP: error checking structure: {e}")
    sys.exit(1)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[regression_upstream_tests]=1
        echo "TEST regression_upstream_tests: PASS"
    else
        echo "TEST regression_upstream_tests: FAIL"
    fi
else
    echo "REGRESSION: SKIPPED (behavioral gate not met)"
fi

# ---------- Anti-stub check (10%): Substantial implementation, runs only if behavioral passes ----------
# [static]: Verify substantial non-stub implementation
if [ $BEHAVIORAL_PASS -eq 1 ]; then
    python3 << 'PYEOF'
import sys, ast, re

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

checks = []

# Check 1: update_weights method exists with substantial body
found_method = False
body_stmt_count = 0
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "update_weights":
        found_method = True
        # Count non-docstring, non-pass statements
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                continue  # Skip docstring
            if isinstance(stmt, ast.Pass):
                continue
            body_stmt_count += 1

checks.append((found_method and body_stmt_count > 5, f"update_weights substantial (found {body_stmt_count} statements)"))

# Check 2: _send_hf_params method exists
found_send_hf = any(isinstance(node, ast.FunctionDef) and node.name == "_send_hf_params" for node in ast.walk(tree))
checks.append((found_send_hf, "_send_hf_params method present"))

# Check 3: File has substantial content (>30 lines, not just stubs)
total_lines = len([l for l in source.splitlines() if l.strip() and not l.strip().startswith('#')])
checks.append((total_lines > 30, f"file has substantial non-comment content ({total_lines} lines)"))

# Check 4: Has connection to rollout_engines (ray usage)
has_ray = "ray.get" in source or "ray.actor" in source
checks.append((has_ray, "Ray integration present"))

# Check 5: Has distributed barrier logic
has_barrier = "dist.barrier" in source
checks.append((has_barrier, "Distributed barrier logic present"))

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file retains substantial implementation")
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[antistub]=1
        echo "TEST antistub: PASS"
    else
        echo "TEST antistub: FAIL"
    fi
else
    echo "ANTISTUB: SKIPPED (behavioral gate not met)"
fi

# ---------- Config-derived checks (run only if behavioral passes) ----------
# [agent_config]: No wildcard imports - .claude/skills/add-tests-and-ci/SKILL.md:45-48 @ 08b201bd
if [ $BEHAVIORAL_PASS -eq 1 ]; then
    echo "=== Config: no wildcard imports ==="
    python3 -c "
import ast, sys
TARGET = '/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py'
with open(TARGET) as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == '*':
                print('FAIL: wildcard import found')
                sys.exit(1)
print('PASS: no wildcard imports')
sys.exit(0)
"
    if [ $? -eq 0 ]; then
        RESULTS[config_no_wildcard]=1
        echo "TEST config_no_wildcard: PASS"
    else
        echo "TEST config_no_wildcard: FAIL"
    fi
else
    echo "CONFIG: SKIPPED (behavioral gate not met)"
fi

# [agent_config]: No bare print() - .claude/skills/add-tests-and-ci/SKILL.md:50-52 @ 08b201bd
if [ $BEHAVIORAL_PASS -eq 1 ]; then
    echo "=== Config: no bare print() ==="
    python3 -c "
import ast, sys, re
TARGET = '/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py'
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            # Check if it's just a bare print (not logging)
            print('FAIL: bare print() found')
            sys.exit(1)
print('PASS: no bare print()')
sys.exit(0)
"
    if [ $? -eq 0 ]; then
        RESULTS[config_no_bare_print]=1
        echo "TEST config_no_bare_print: PASS"
    else
        echo "TEST config_no_bare_print: FAIL"
    fi
else
    echo "CONFIG: SKIPPED (behavioral gate not met)"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_del_both_tensors': ${WEIGHTS[behavioral_del_both_tensors]}, 'behavioral_ipc_collect_loop': ${WEIGHTS[behavioral_ipc_collect_loop]}, 'behavioral_ipc_collect_after_barrier': ${WEIGHTS[behavioral_ipc_collect_after_barrier]}, 'regression_upstream_tests': ${WEIGHTS[regression_upstream_tests]}, 'antistub': ${WEIGHTS[antistub]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
results = {'behavioral_del_both_tensors': ${RESULTS[behavioral_del_both_tensors]}, 'behavioral_ipc_collect_loop': ${RESULTS[behavioral_ipc_collect_loop]}, 'behavioral_ipc_collect_after_barrier': ${RESULTS[behavioral_ipc_collect_after_barrier]}, 'regression_upstream_tests': ${RESULTS[regression_upstream_tests]}, 'antistub': ${RESULTS[antistub]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_del_both_tensors     (${WEIGHTS[behavioral_del_both_tensors]}): ${RESULTS[behavioral_del_both_tensors]}"
echo "  behavioral_ipc_collect_loop     (${WEIGHTS[behavioral_ipc_collect_loop]}): ${RESULTS[behavioral_ipc_collect_loop]}"
echo "  behavioral_ipc_collect_after_barrier (${WEIGHTS[behavioral_ipc_collect_after_barrier]}): ${RESULTS[behavioral_ipc_collect_after_barrier]}"
echo "  regression_upstream_tests       (${WEIGHTS[regression_upstream_tests]}): ${RESULTS[regression_upstream_tests]}"
echo "  antistub                        (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_no_wildcard              (${WEIGHTS[config_no_wildcard]}): ${RESULTS[config_no_wildcard]}"
echo "  config_no_bare_print            (${WEIGHTS[config_no_bare_print]}): ${RESULTS[config_no_bare_print]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
