#!/usr/bin/env bash
# Verifier for pytorch-graphpickler-ignorerawnode-tests
# Task: Add unit tests for ignore_raw_node option in GraphPickler.Options
# Strategy: run agent's tests, then mutate library to verify tests detect breakage
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/pytorch/test/fx/test_graph_pickler.py"
PICKLER="/workspace/pytorch/torch/fx/_graph_pickler.py"

echo "=== pytorch-graphpickler-ignorerawnode-tests verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/pytorch/test/fx/test_graph_pickler.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weight budget:
# T1 (behavioral):  0.35 — agent's tests pass on correct code
# T2 (behavioral):  0.20 — mutation: ignore_raw_node disabled → agent detects
# T3 (behavioral):  0.20 — mutation: raw Node assertion removed → agent detects
# T4 (P2P):         0.15 — existing test behavior preserved
# T5 (anti-stub):   0.10 — >=2 test methods with real assertions
# Total:            1.00

SCORE="0.0"

# -- Discover agent's test classes for ignore_raw_node --
export AGENT_CLASSES=$(python3 << 'PYEOF'
import ast, sys
with open("/workspace/pytorch/test/fx/test_graph_pickler.py") as f:
    source = f.read()
tree = ast.parse(source)
found = []
for node in ast.walk(tree):
    if not isinstance(node, ast.ClassDef):
        continue
    dump = ast.dump(node)
    refs_feature = ("ignore_raw_node" in dump
                    or ("raw" in dump and "Node" in dump and "pickle" in dump.lower())
                    or ("raw" in dump and "Node" in dump and "meta" in dump)
                    or ("raw" in dump and "Node" in dump and "GraphPickler" in dump))
    has_tests = any(isinstance(m, ast.FunctionDef) and m.name.startswith("test_")
                    for m in node.body)
    if refs_feature and has_tests:
        found.append(node.name)
if found:
    print(" ".join(found))
else:
    sys.exit(1)
PYEOF
)

if [ $? -ne 0 ] || [ -z "$AGENT_CLASSES" ]; then
    echo "No test classes found for ignore_raw_node — score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "Discovered agent test classes: $AGENT_CLASSES"

# -- Reusable test runner script --
cat > /tmp/run_agent_tests.py << 'RUNNER'
import sys, os, unittest, importlib.util

sys.path.insert(0, "/workspace/pytorch")
os.chdir("/workspace/pytorch")

spec = importlib.util.spec_from_file_location(
    "test_graph_pickler",
    "/workspace/pytorch/test/fx/test_graph_pickler.py"
)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(f"IMPORT_FAIL: {e}")
    sys.exit(2)

suite = unittest.TestSuite()
for cls_name in os.environ.get("AGENT_CLASSES", "").split():
    cls = getattr(mod, cls_name, None)
    if cls is None:
        print(f"CLASS_MISSING: {cls_name}")
        sys.exit(2)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(cls))

if suite.countTestCases() == 0:
    print("NO_TESTS")
    sys.exit(2)

runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
result = runner.run(suite)

if result.wasSuccessful():
    print(f"ALL_PASS:{result.testsRun}")
    sys.exit(0)
else:
    print(f"SOME_FAIL:{len(result.failures)+len(result.errors)}/{result.testsRun}")
    sys.exit(1)
RUNNER

# -- TEST 1 (BEHAVIORAL): Agent's tests pass on correct code --
# [pr_diff] (0.35): Agent-written tests run successfully against correct library code
echo ""
echo "TEST 1: agent's tests pass on correct code (weight=0.35)"
T1=$(python3 /tmp/run_agent_tests.py 2>/dev/null)
T1_RC=$?
echo "  $T1"
if [ $T1_RC -eq 0 ]; then
    SCORE=$(python3 -c "print(f'{$SCORE + 0.35:.4f}')")
    echo "  +0.35"
fi

# -- TEST 2 (BEHAVIORAL MUTATION): ignore_raw_node feature disabled --
# [pr_diff] (0.20): Agent's tests detect when ignore_raw_node=True stops working
echo ""
echo "TEST 2: mutation — ignore_raw_node forced to False (weight=0.20)"
if [ $T1_RC -eq 0 ]; then
    cp "$PICKLER" "${PICKLER}.bak"

    python3 << 'PYEOF'
import re, sys

with open("/workspace/pytorch/torch/fx/_graph_pickler.py") as f:
    source = f.read()

lines = source.split('\n')
mutated = 0
for i, line in enumerate(lines):
    if 'ignore_raw_node' not in line:
        continue
    stripped = line.strip()
    # Skip definitions: field declarations like "ignore_raw_node: bool = False"
    if re.match(r'^ignore_raw_node\s*[:=]', stripped):
        continue
    # Skip __init__ assignments: "self.ignore_raw_node = ..."
    if re.match(r'^self\.ignore_raw_node\s*=', stripped):
        continue
    # Skip comments
    if stripped.startswith('#'):
        continue
    # Replace attribute reads with False so the feature never activates
    new_line = re.sub(r'(?:\w+\.)*ignore_raw_node(?!\s*[=:])', 'False', line)
    if new_line != line:
        lines[i] = new_line
        mutated += 1

if mutated == 0:
    print("WARNING: no mutations applied")
    sys.exit(1)
with open("/workspace/pytorch/torch/fx/_graph_pickler.py", 'w') as f:
    f.write('\n'.join(lines))
print(f"Mutated {mutated} line(s)")
PYEOF
    MUT_OK=$?

    if [ $MUT_OK -eq 0 ]; then
        T2=$(python3 /tmp/run_agent_tests.py 2>/dev/null)
        T2_RC=$?
        echo "  $T2"
        if [ $T2_RC -eq 1 ]; then
            SCORE=$(python3 -c "print(f'{$SCORE + 0.20:.4f}')")
            echo "  +0.20 (tests correctly detected broken ignore_raw_node)"
        elif [ $T2_RC -eq 0 ]; then
            echo "  Tests still pass — don't verify ignore_raw_node feature"
        else
            echo "  Import error after mutation — skipping"
        fi
    else
        echo "  Could not apply mutation — skipping"
    fi

    cp "${PICKLER}.bak" "$PICKLER"
else
    echo "  Skipped (T1 failed)"
fi

# -- TEST 3 (BEHAVIORAL MUTATION): raw Node assertion removed --
# [pr_diff] (0.20): Agent's tests detect when default-raises behavior is broken
echo ""
echo "TEST 3: mutation — raw Node assertion neutralized (weight=0.20)"
if [ $T1_RC -eq 0 ]; then
    cp "$PICKLER" "${PICKLER}.bak"

    python3 << 'PYEOF'
import re, sys

with open("/workspace/pytorch/torch/fx/_graph_pickler.py") as f:
    source = f.read()

lines = source.split('\n')
mutated = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    # Match assert/raise statements that mention raw Node
    if (re.search(r'\b(assert|raise)\b', stripped)
            and re.search(r'[Rr]aw', stripped)
            and re.search(r'[Nn]ode', stripped)):
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'pass  # MUTATED: assertion removed'
        mutated += 1

# Fallback: search for the error message string
if mutated == 0:
    for i, line in enumerate(lines):
        if 'Unexpected' in line and 'raw' in line.lower() and 'Node' in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + 'pass  # MUTATED'
            mutated += 1
            # Neutralize the enclosing assert/raise on previous line
            if i > 0 and re.search(r'\b(assert|raise)\b', lines[i-1]):
                indent2 = len(lines[i-1]) - len(lines[i-1].lstrip())
                lines[i-1] = ' ' * indent2 + 'if False:  # MUTATED'
                mutated += 1

if mutated == 0:
    print("WARNING: no mutations applied")
    sys.exit(1)
with open("/workspace/pytorch/torch/fx/_graph_pickler.py", 'w') as f:
    f.write('\n'.join(lines))
print(f"Mutated {mutated} line(s)")
PYEOF
    MUT_OK=$?

    if [ $MUT_OK -eq 0 ]; then
        T3=$(python3 /tmp/run_agent_tests.py 2>/dev/null)
        T3_RC=$?
        echo "  $T3"
        if [ $T3_RC -eq 1 ]; then
            SCORE=$(python3 -c "print(f'{$SCORE + 0.20:.4f}')")
            echo "  +0.20 (tests correctly detected removed assertion)"
        elif [ $T3_RC -eq 0 ]; then
            echo "  Tests still pass — don't verify default-raises behavior"
        else
            echo "  Import error after mutation — skipping"
        fi
    else
        echo "  Could not apply mutation — skipping"
    fi

    cp "${PICKLER}.bak" "$PICKLER"
else
    echo "  Skipped (T1 failed)"
fi

# -- TEST 4 (PASS-TO-PASS): Existing test behavior preserved --
# [repo_tests] (0.15): Agent's changes must not break existing serialization behavior
echo ""
echo "TEST 4: pass-to-pass — existing test behavior (weight=0.15)"
T4=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, "/workspace/pytorch")
try:
    import torch
    from torch.fx import symbolic_trace

    class M(torch.nn.Module):
        def forward(self, x):
            y = torch.neg(x)
            return y + 1

    gm = symbolic_trace(M())
    node = next(n for n in gm.graph.nodes if n.op == "call_function")
    node.type = torch.Tensor
    state = node.__getstate__()
    assert state["type"] is torch.Tensor, f"Expected torch.Tensor, got {state['type']}"

    print("PASS: existing serialization behavior intact")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
PYEOF
)
echo "  $T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print(f'{$SCORE + 0.15:.4f}')")
    echo "  +0.15"
fi

# -- TEST 5 (ANTI-STUB): Test methods have real assertions --
# [static] (0.10): Tests must have real assertions and non-trivial bodies
echo ""
echo "TEST 5: anti-stub — test methods have real assertions (weight=0.10)"
T5=$(python3 << 'PYEOF'
import ast, sys, os

with open("/workspace/pytorch/test/fx/test_graph_pickler.py") as f:
    source = f.read()
tree = ast.parse(source)

classes = os.environ.get("AGENT_CLASSES", "").split()
test_methods = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name in classes:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                test_methods.append(item)

if len(test_methods) < 2:
    print(f"FAIL: found {len(test_methods)} test method(s), need >= 2")
    sys.exit(1)

for method in test_methods:
    has_assert = False
    has_pickler_call = False
    stmt_count = 0
    for child in ast.walk(method):
        if isinstance(child, ast.Call):
            func_name = ""
            if isinstance(child.func, ast.Attribute):
                func_name = child.func.attr
            elif isinstance(child.func, ast.Name):
                func_name = child.func.id
            if "assert" in func_name.lower() or func_name.startswith("assert"):
                has_assert = True
            if func_name in ("dumps", "loads", "assertRaises"):
                has_pickler_call = True
        if isinstance(child, ast.Assert):
            has_assert = True
        if isinstance(child, (ast.Assign, ast.Expr, ast.Assert, ast.With, ast.If, ast.Return)):
            stmt_count += 1

    if not has_assert:
        print(f"FAIL: {method.name} lacks assertions (stub)")
        sys.exit(1)
    if stmt_count < 3:
        print(f"FAIL: {method.name} has only {stmt_count} statements (trivial)")
        sys.exit(1)

# Check that at least one method references dumps/loads/assertRaises (actually exercises pickling)
any_pickler = False
for method in test_methods:
    dump = ast.dump(method)
    if "dumps" in dump or "loads" in dump or "pickle" in dump.lower():
        any_pickler = True
        break
if not any_pickler:
    print("FAIL: no test method actually calls dumps/loads (not testing pickling)")
    sys.exit(1)

print(f"PASS: {len(test_methods)} test methods with real assertions and pickler calls")
sys.exit(0)
PYEOF
)
echo "  $T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print(f'{$SCORE + 0.10:.4f}')")
    echo "  +0.10"
fi

# -- Final score --
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
