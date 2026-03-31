#!/usr/bin/env bash
set -euo pipefail

POST_GRAD="/workspace/torch/_inductor/fx_passes/post_grad.py"
REWARD=0

add_score() {
    REWARD=$(python3 -c "print($REWARD + $1)")
}

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0.00): File must be valid Python
if python3 -c "import ast; ast.parse(open('$POST_GRAD').read())"; then
    echo "GATE PASS: syntax ok"
else
    echo "GATE FAIL: syntax error in post_grad.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

###############################################################################
# BEHAVIORAL FAIL-TO-PASS (0.65 total)
# These tests FAIL on buggy code, PASS on fixed code.
###############################################################################

# [pr_diff] (0.35): unfuse_bias_add_to_pointwise must guard against half-precision dtypes.
# The function should return early (no-op) when input dtype is bfloat16 or float16.
#
# WHY AST: unfuse_bias_add_to_pointwise is a pattern-matcher callback decorated with
# @register_lowering_pattern. It requires the full Inductor graph infrastructure
# (FX graph, pattern matcher, Match objects) to invoke. Cannot be called standalone.
cat > /tmp/test_half_guard.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

# Find the unfuse_bias_add_to_pointwise function
found_guard = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        # Walk the function body looking for a dtype check involving half-precision types
        src = ast.dump(node)
        # Must reference both bfloat16 and float16 (or equivalent half-precision check)
        has_bf16 = "bfloat16" in src or "bf16" in src.lower()
        has_fp16 = "float16" in src or "fp16" in src.lower() or "half" in src.lower()
        if has_bf16 and has_fp16:
            found_guard = True
        break

if found_guard:
    print("PASS: half-precision dtype guard found in unfuse_bias_add_to_pointwise")
else:
    print("FAIL: no half-precision dtype guard in unfuse_bias_add_to_pointwise")
    sys.exit(1)
PYEOF

if python3 /tmp/test_half_guard.py "$POST_GRAD"; then
    add_score 0.35
else
    echo "FAIL: half-precision guard not present"
fi

# [pr_diff] (0.30): The guard must cause the function to return early (no-op) for half dtypes.
# If the dtype is half-precision, the function should return before reaching the replacement logic.
#
# WHY AST: Same reason — pattern matcher callback, requires full Inductor stack.
cat > /tmp/test_early_return.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        # Find an if-statement that checks dtype and has a bare return (or return None)
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.If):
                cond_src = ast.dump(stmt.test)
                # Check condition references dtype and half-precision types
                refs_dtype = "dtype" in cond_src
                refs_half = ("bfloat16" in cond_src or "float16" in cond_src
                             or "bf16" in cond_src.lower() or "fp16" in cond_src.lower()
                             or "half" in cond_src.lower())
                if refs_dtype and refs_half:
                    # Check body has a return statement (bare return = no-op)
                    for body_stmt in stmt.body:
                        if isinstance(body_stmt, ast.Return):
                            # Return with no value or None = no-op (correct)
                            if body_stmt.value is None or (isinstance(body_stmt.value, ast.Constant) and body_stmt.value.value is None):
                                found = True
                                break
                    if found:
                        break

if found:
    print("PASS: early return for half-precision dtypes")
else:
    print("FAIL: no early return for half-precision dtypes")
    sys.exit(1)
PYEOF

if python3 /tmp/test_early_return.py "$POST_GRAD"; then
    add_score 0.30
else
    echo "FAIL: early return logic not found"
fi

###############################################################################
# PASS-TO-PASS REGRESSION (0.15)
# Existing behavior must not break.
###############################################################################

# [pr_diff] (0.10): unfuse_bias_add_to_pointwise function still exists and defines repl()
cat > /tmp/test_function_exists.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

found_fn = False
found_repl = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        found_fn = True
        # Check it still defines repl() inner function
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == "repl":
                found_repl = True
                break
        break

if found_fn and found_repl:
    print("PASS: unfuse_bias_add_to_pointwise with repl() preserved")
else:
    if not found_fn:
        print("FAIL: unfuse_bias_add_to_pointwise function missing")
    else:
        print("FAIL: repl() inner function missing")
    sys.exit(1)
PYEOF

if python3 /tmp/test_function_exists.py "$POST_GRAD"; then
    add_score 0.10
else
    echo "FAIL: function structure broken"
fi

# [pr_diff] (0.05): should_prefer_unfused_addmm helper still exists
cat > /tmp/test_helper_exists.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "should_prefer_unfused_addmm":
        print("PASS: should_prefer_unfused_addmm preserved")
        sys.exit(0)

print("FAIL: should_prefer_unfused_addmm missing")
sys.exit(1)
PYEOF

if python3 /tmp/test_helper_exists.py "$POST_GRAD"; then
    add_score 0.05
else
    echo "FAIL: helper function missing"
fi

###############################################################################
# STRUCTURAL / ANTI-STUB (0.10)
###############################################################################

# [pr_diff] (0.05): unfuse_bias_add_to_pointwise must have non-trivial body (not stubbed)
cat > /tmp/test_not_stubbed.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        # Must have at least 5 statements (guard + repl def + match.replace_by_example)
        if len(node.body) >= 3:
            print(f"PASS: function has {len(node.body)} top-level statements")
            sys.exit(0)
        else:
            print(f"FAIL: function appears stubbed ({len(node.body)} statements)")
            sys.exit(1)

print("FAIL: function not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_not_stubbed.py "$POST_GRAD"; then
    add_score 0.05
else
    echo "FAIL: function stubbed"
fi

# [pr_diff] (0.05): The repl inner function still handles alpha/beta scaling
cat > /tmp/test_repl_scaling.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == "repl":
                src = ast.dump(item)
                has_alpha = "alpha" in src
                has_beta = "beta" in src
                if has_alpha and has_beta:
                    print("PASS: repl handles alpha/beta scaling")
                    sys.exit(0)
                else:
                    print("FAIL: repl missing alpha/beta handling")
                    sys.exit(1)

print("FAIL: repl not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_repl_scaling.py "$POST_GRAD"; then
    add_score 0.05
else
    echo "FAIL: repl scaling broken"
fi

###############################################################################
# CONFIG-DERIVED (0.10)
###############################################################################

# [agent_config] (0.05): "Minimize comments; be concise" — CLAUDE.md:48
# Check that the function doesn't have excessive comments relative to code.
cat > /tmp/test_concise.py << 'PYEOF'
import ast
import sys
import re

with open(sys.argv[1]) as f:
    lines = f.readlines()
    f.seek(0)
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        start = node.lineno - 1
        end = node.end_lineno
        method_lines = lines[start:end]
        comments = sum(1 for l in method_lines if re.match(r'^\s*#', l))
        code = sum(1 for l in method_lines if l.strip() and not re.match(r'^\s*#', l))
        if code > 0 and comments <= code:
            print(f"PASS: concise comments ({comments} comments, {code} code lines)")
            sys.exit(0)
        else:
            print(f"FAIL: too many comments ({comments} comments, {code} code lines)")
            sys.exit(1)

print("FAIL: function not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_concise.py "$POST_GRAD"; then
    add_score 0.05
else
    echo "FAIL: comments not concise"
fi

# [agent_config] (0.05): "Match existing code style and architectural patterns" — CLAUDE.md:57
# The existing pattern in post_grad.py uses early-return guards (return with no value)
# in pattern matcher callbacks. The new guard should follow this convention.
cat > /tmp/test_style.py << 'PYEOF'
import ast
import sys

with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())

# Check that the dtype guard uses a bare return (matching existing style)
# rather than raising an exception or returning a special value
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "unfuse_bias_add_to_pointwise":
        for stmt in node.body:
            if isinstance(stmt, ast.If):
                cond_src = ast.dump(stmt.test)
                if "dtype" in cond_src:
                    for body_stmt in stmt.body:
                        if isinstance(body_stmt, ast.Return):
                            if body_stmt.value is None or (isinstance(body_stmt.value, ast.Constant) and body_stmt.value.value is None):
                                print("PASS: guard uses bare return (matches existing style)")
                                sys.exit(0)
                            else:
                                print("FAIL: guard returns a value instead of bare return")
                                sys.exit(1)
                        if isinstance(body_stmt, ast.Raise):
                            print("FAIL: guard raises instead of returning (doesn't match style)")
                            sys.exit(1)

print("FAIL: dtype guard not found for style check")
sys.exit(1)
PYEOF

if python3 /tmp/test_style.py "$POST_GRAD"; then
    add_score 0.05
else
    echo "FAIL: style doesn't match existing patterns"
fi

###############################################################################
# FINAL SCORE
###############################################################################
echo ""
echo "=== FINAL SCORE: $REWARD ==="
echo "$REWARD" > /logs/verifier/reward.txt

# Write detailed breakdown
python3 -c "
import json
reward = float('$REWARD')
behavioral = min(0.65, reward)
regression = min(0.15, max(0.0, reward - 0.65))
structural = min(0.10, max(0.0, reward - 0.80))
config = min(0.10, max(0.0, reward - 0.90))
json.dump({
    'reward': reward,
    'behavioral': behavioral,
    'regression': regression,
    'structural': structural,
    'config': config,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
