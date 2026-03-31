#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" tag="$3" desc="$4"
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
        DETAILS="${DETAILS}PASS ($weight) [$tag]: $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) [$tag]: $desc\n"
    fi
}

FILE="/repo/torch/_inductor/codegen/mps.py"

# ============================================================
# GATE: Syntax check — abort on failure
# ============================================================
# [static] (0.00): Python source must parse without syntax errors
if python3 -c "
import ast
with open('$FILE') as f:
    ast.parse(f.read())
print('syntax ok')
" 2>/dev/null | grep -q "syntax ok"; then
    echo "GATE PASS: syntax check"
else
    echo "GATE FAIL: syntax error in $FILE"
    echo "0.0" > /logs/verifier/reward.txt
    printf '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}\n' > /logs/verifier/reward.json
    exit 0
fi

# ============================================================
# Helper: extract functions via AST (robust to multi-line bodies)
# ============================================================
# Writes extracted function sources to temp files for reuse
python3 << 'PYEOF'
import ast, textwrap, sys

FILE = "/repo/torch/_inductor/codegen/mps.py"
with open(FILE) as f:
    src = f.read()
lines = src.splitlines(keepends=True)
tree = ast.parse(src)

# Extract value_to_metal (top-level function)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "value_to_metal":
        vtm_src = textwrap.dedent("".join(lines[node.lineno-1:node.end_lineno]))
        with open("/tmp/_vtm.py", "w") as f:
            f.write(vtm_src)
        break

# Extract where() and masked() from MetalOverrides
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "where":
                raw = "".join(lines[item.lineno-1:item.end_lineno])
                dedented = textwrap.dedent(raw)
                # Strip decorator lines (@staticmethod etc.)
                func_lines = [l for l in dedented.splitlines(keepends=True)
                              if not l.strip().startswith("@")]
                with open("/tmp/_where.py", "w") as f:
                    f.write("".join(func_lines))
            if isinstance(item, ast.FunctionDef) and item.name == "masked":
                raw = "".join(lines[item.lineno-1:item.end_lineno])
                with open("/tmp/_masked_raw.py", "w") as f:
                    f.write(raw)
        break
PYEOF

# ============================================================
# BEHAVIORAL: where() casts false-branch to match true-branch type
# ============================================================
# [pr_diff] (0.35): where() must cast false-branch value to match true-branch type
WHERE_RESULT=$(python3 << 'PYEOF'
import math, sys

# Build execution environment with minimal mocks
class MockTorch:
    inf = math.inf

class CSEVariable(str):
    pass

# Type alias used in annotations
OpVarT = object

ns = {
    "math": math, "torch": MockTorch(), "CSEVariable": CSEVariable,
    "OpVarT": OpVarT, "__builtins__": __builtins__,
}

# Load value_to_metal
with open("/tmp/_vtm.py") as f:
    exec(compile(f.read(), "<vtm>", "exec"), ns)

# Load where function (extracted via AST — handles multi-line bodies)
with open("/tmp/_where.py") as f:
    where_src = f.read()

# Provide value_to_metal in the where function's scope
exec(compile(where_src, "<where>", "exec"), ns)
where_fn = ns.get("where")
if where_fn is None:
    print("EXTRACT_FAIL")
    sys.exit(0)

# Call: where("cond", "var_bf16", 0.0)
# Buggy output: "cond ? var_bf16 : 0.0" — no cast, Metal rejects implicit float→bfloat16
# Correct output must wrap the false-branch with a cast referencing var_bf16's type
try:
    result = where_fn("cond", "var_bf16", 0.0)
    print(result)
except Exception as e:
    print(f"ERROR:{e}")
PYEOF
)

if echo "$WHERE_RESULT" | grep -q "EXTRACT_FAIL\|ERROR:"; then
    add_result 0.35 0 "pr_diff" "where() cast: could not extract/call method"
elif echo "$WHERE_RESULT" | grep -q 'decltype.*var_bf16'; then
    # Output contains a type cast referencing the true-branch operand's type
    add_result 0.35 1 "pr_diff" "where() casts false-branch to match true-branch type"
else
    add_result 0.35 0 "pr_diff" "where() does not cast false-branch value (got: $WHERE_RESULT)"
fi

# ============================================================
# BEHAVIORAL: where() preserves value_to_metal AND casts for special values
# ============================================================
# [pr_diff] (0.15): where() wraps special float values (inf) with type cast
WHERE_INF_RESULT=$(python3 << 'PYEOF'
import math, sys

class MockTorch:
    inf = math.inf

class CSEVariable(str):
    pass

OpVarT = object
ns = {
    "math": math, "torch": MockTorch(), "CSEVariable": CSEVariable,
    "OpVarT": OpVarT, "__builtins__": __builtins__,
}

with open("/tmp/_vtm.py") as f:
    exec(compile(f.read(), "<vtm>", "exec"), ns)
with open("/tmp/_where.py") as f:
    exec(compile(f.read(), "<where>", "exec"), ns)

where_fn = ns.get("where")
if where_fn is None:
    print("EXTRACT_FAIL")
    sys.exit(0)

# Call: where("mask", "x", math.inf)
# value_to_metal(inf) → "HUGE_VALF", then must be cast to match x's type
try:
    result = where_fn("mask", "x", math.inf)
    print(result)
except Exception as e:
    print(f"ERROR:{e}")
PYEOF
)

if echo "$WHERE_INF_RESULT" | grep -q "EXTRACT_FAIL\|ERROR:"; then
    add_result 0.15 0 "pr_diff" "where() inf: could not extract/call method"
elif echo "$WHERE_INF_RESULT" | grep -q 'HUGE_VALF' && echo "$WHERE_INF_RESULT" | grep -qE 'decltype\(.{0,5}x.{0,5}\)'; then
    add_result 0.15 1 "pr_diff" "where() wraps special float values (inf) with cast"
else
    add_result 0.15 0 "pr_diff" "where() does not properly handle special values (got: $WHERE_INF_RESULT)"
fi

# ============================================================
# BEHAVIORAL: masked() adds type casts to both branches
# NOTE: masked() depends on V.kernel framework objects — cannot be called directly.
# AST check justified: needs Inductor codegen infrastructure unavailable on CPU.
# ============================================================
# [pr_diff] (0.15): masked() must cast both body result and else-branch value
MASKED_RESULT=$(python3 << 'PYEOF'
import re

with open("/tmp/_masked_raw.py") as f:
    body_text = f.read()

# Count occurrences of the static_cast<decltype pattern in the method body.
# A correct fix adds this cast in BOTH the if-body assignment and else-branch assignment.
# We count pattern occurrences rather than checking exact template variable names,
# so alternative fixes using different variable names still pass.
cast_count = len(re.findall(r'static_cast<decltype', body_text))

# Verify method is non-trivial (anti-stub for this specific check)
meaningful = [l for l in body_text.splitlines()
              if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('@')]

if cast_count >= 2 and len(meaningful) > 5:
    print("BOTH_CAST")
elif cast_count == 1 and len(meaningful) > 5:
    print("PARTIAL_CAST")
elif len(meaningful) <= 5:
    print("STUB")
else:
    print("NO_CAST")
PYEOF
)

if [ "$MASKED_RESULT" = "BOTH_CAST" ]; then
    add_result 0.15 1 "pr_diff" "masked() casts both body result and else-branch"
else
    add_result 0.15 0 "pr_diff" "masked() missing casts (got: $MASKED_RESULT)"
fi

# ============================================================
# PASS-TO-PASS: value_to_metal still converts special values correctly
# ============================================================
# [repo_tests] (0.15): value_to_metal preserves special value handling
P2P_RESULT=$(python3 << 'PYEOF'
import math, sys

class MockTorch:
    inf = math.inf

class CSEVariable(str):
    pass

ns = {"math": math, "torch": MockTorch(), "CSEVariable": CSEVariable, "__builtins__": __builtins__}

with open("/tmp/_vtm.py") as f:
    exec(compile(f.read(), "<vtm>", "exec"), ns)
vtm = ns["value_to_metal"]

checks = [
    (vtm(0.0), "0.0"),
    (vtm(1.5), "1.5"),
    (vtm(math.inf), "HUGE_VALF"),
    (vtm(-math.inf), "-HUGE_VALF"),
    (vtm(math.nan), "NAN"),
    (vtm(True), "true"),
    (vtm(False), "false"),
    (vtm(42), "42"),
]
all_ok = all(got == expected for got, expected in checks)
if all_ok:
    print("PASS")
else:
    for got, expected in checks:
        if got != expected:
            print(f"FAIL: got {got!r}, expected {expected!r}")
    print("FAIL")
PYEOF
)

if echo "$P2P_RESULT" | head -1 | grep -q "PASS"; then
    add_result 0.15 1 "repo_tests" "value_to_metal preserves special value handling"
else
    add_result 0.15 0 "repo_tests" "value_to_metal regression ($P2P_RESULT)"
fi

# ============================================================
# STRUCTURAL: Anti-stub check
# ============================================================
# [static] (0.10): Methods are not stubbed out (pass/NotImplementedError/...)
ANTISTUB_RESULT=$(python3 << 'PYEOF'
import ast

with open("/repo/torch/_inductor/codegen/mps.py") as f:
    src = f.read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name in ("masked", "where"):
                if len(item.body) <= 2:
                    for stmt in item.body:
                        if isinstance(stmt, ast.Pass):
                            print(f"STUB:{item.name}")
                        elif isinstance(stmt, ast.Raise):
                            print(f"STUB:{item.name}")
                        elif isinstance(stmt, ast.Return) and stmt.value is None:
                            print(f"STUB:{item.name}")
print("DONE")
PYEOF
)

if echo "$ANTISTUB_RESULT" | grep -q "STUB"; then
    add_result 0.10 0 "static" "Anti-stub: methods are stubbed out"
else
    add_result 0.10 1 "static" "Anti-stub: masked() and where() have real implementations"
fi

# ============================================================
# CONFIG: Follows existing static_cast<decltype(...)> pattern
# ============================================================
# [agent_config] (0.10): Uses static_cast<decltype(...)> consistent with codebase — CLAUDE.md:57 @ 036b25f5
CONFIG_RESULT=$(python3 << 'PYEOF'
import ast

with open("/repo/torch/_inductor/codegen/mps.py") as f:
    src = f.read()
tree = ast.parse(src)

where_ok = False
masked_ok = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "MetalOverrides":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "where":
                body = "\n".join(src.splitlines()[item.lineno-1:item.end_lineno])
                where_ok = "static_cast<decltype" in body
            if isinstance(item, ast.FunctionDef) and item.name == "masked":
                body = "\n".join(src.splitlines()[item.lineno-1:item.end_lineno])
                masked_ok = "static_cast<decltype" in body

if where_ok and masked_ok:
    print("CONSISTENT")
elif where_ok or masked_ok:
    print("PARTIAL")
else:
    print("NONE")
PYEOF
)

if [ "$CONFIG_RESULT" = "CONSISTENT" ]; then
    add_result 0.10 1 "agent_config" "Uses static_cast<decltype(...)> consistent with existing patterns — CLAUDE.md:57 @ 036b25f5"
else
    add_result 0.10 0 "agent_config" "Does not follow existing decltype cast pattern ($CONFIG_RESULT) — CLAUDE.md:57 @ 036b25f5"
fi

# ============================================================
# Results
# ============================================================
echo ""
echo "=== Test Results ==="
printf "$DETAILS"
echo ""
echo "Score: $SCORE / $TOTAL"

BEHAVIORAL=$(python3 -c "
score = 0
details = '''$(printf "$DETAILS")'''
for line in details.strip().split('\n'):
    if 'pr_diff' in line and line.startswith('PASS'):
        w = float(line.split('(')[1].split(')')[0])
        score += w
print(round(score, 4))
")

REGRESSION=$(python3 -c "
score = 0
details = '''$(printf "$DETAILS")'''
for line in details.strip().split('\n'):
    if 'repo_tests' in line and line.startswith('PASS'):
        w = float(line.split('(')[1].split(')')[0])
        score += w
print(round(score, 4))
")

CONFIG=$(python3 -c "
score = 0
details = '''$(printf "$DETAILS")'''
for line in details.strip().split('\n'):
    if 'agent_config' in line and line.startswith('PASS'):
        w = float(line.split('(')[1].split(')')[0])
        score += w
print(round(score, 4))
")

echo "$SCORE" > /logs/verifier/reward.txt
printf '{"reward": %s, "behavioral": %s, "regression": %s, "config": %s, "style_rubric": 0.0}\n' \
    "$SCORE" "$BEHAVIORAL" "$REGRESSION" "$CONFIG" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
