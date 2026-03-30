#!/usr/bin/env bash
set +e

TARGET="/workspace/AReaL/areal/experimental/models/archon/moe/router.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.30
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.20
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural antistub config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

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

# ---------- PRIMARY 1 (35%): Behavioral - gate is called as module, not bypassed ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find TokenChoiceTopKRouter.forward
forward_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenChoiceTopKRouter":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "forward":
                forward_node = item
                break
        break

if forward_node is None:
    print("BEHAVIORAL FAIL: TokenChoiceTopKRouter.forward not found")
    sys.exit(1)

forward_source = ast.get_source_segment(source, forward_node)
if forward_source is None:
    lines = source.splitlines()
    forward_source = "\n".join(lines[forward_node.lineno - 1 : forward_node.end_lineno])

# The bug: forward() calls router_gating_linear(x, self.gate.weight, ...) directly
# The fix: forward() should call self.gate(x) instead
import re

# Check that the bypassed call is NOT present
buggy = re.search(r'router_gating_linear\s*\(\s*x\s*,\s*self\.gate\.weight', forward_source)
if buggy:
    print("BEHAVIORAL FAIL: forward() still bypasses self.gate by calling router_gating_linear(x, self.gate.weight, ...)")
    sys.exit(1)

# Check that self.gate(x) IS present
fixed = re.search(r'self\.gate\s*\(\s*x\s*\)', forward_source)
if not fixed:
    print("BEHAVIORAL FAIL: forward() does not call self.gate(x)")
    sys.exit(1)

print("BEHAVIORAL PASS: forward() calls self.gate(x) as a module (DTensor hooks fire)")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - RouterGateLinear class exists and is nn.Linear subclass ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find a class that subclasses nn.Linear and wraps router_gating_linear
gate_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        # Check if it inherits from nn.Linear or something.Linear
        for base in node.bases:
            base_str = ast.get_source_segment(source, base)
            if base_str and "Linear" in base_str:
                # Check if this class has a forward method calling router_gating_linear
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "forward":
                        fwd_src = ast.get_source_segment(source, item)
                        if fwd_src and "router_gating_linear" in fwd_src:
                            gate_class = node
                            break
                break

if gate_class is None:
    print("BEHAVIORAL2 FAIL: no nn.Linear subclass wrapping router_gating_linear found")
    sys.exit(1)

# Check that __init__ accepts router_dtype
init_node = None
for item in gate_class.body:
    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
        init_node = item
        break

if init_node is None:
    print("BEHAVIORAL2 FAIL: gate class has no __init__")
    sys.exit(1)

init_src = ast.get_source_segment(source, init_node)
if init_src and "router_dtype" not in init_src:
    print("BEHAVIORAL2 FAIL: gate class __init__ does not accept router_dtype")
    sys.exit(1)

# Check bias=False in super().__init__
if init_src and "bias=False" not in init_src and "bias = False" not in init_src:
    print("BEHAVIORAL2 FAIL: gate class does not set bias=False for state dict compat")
    sys.exit(1)

# Verify TokenChoiceTopKRouter uses this class
router_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenChoiceTopKRouter":
        router_class = node
        break

if router_class is None:
    print("BEHAVIORAL2 FAIL: TokenChoiceTopKRouter not found")
    sys.exit(1)

router_init = None
for item in router_class.body:
    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
        router_init = item
        break

router_init_src = ast.get_source_segment(source, router_init)
if router_init_src and gate_class.name not in router_init_src:
    print(f"BEHAVIORAL2 FAIL: TokenChoiceTopKRouter.__init__ does not use {gate_class.name}")
    sys.exit(1)

print(f"BEHAVIORAL2 PASS: {gate_class.name} wraps router_gating_linear as nn.Linear subclass")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral2]=1
    echo "TEST behavioral2: PASS"
else
    echo "TEST behavioral2: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural check ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check that nn.Linear is NOT directly assigned to self.gate in TokenChoiceTopKRouter
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenChoiceTopKRouter":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_src = ast.get_source_segment(source, item)
                if init_src and "nn.Linear(" in init_src and "self.gate = nn.Linear(" in init_src:
                    print("STRUCTURAL FAIL: TokenChoiceTopKRouter still assigns self.gate = nn.Linear() directly")
                    sys.exit(1)

print("STRUCTURAL PASS: TokenChoiceTopKRouter does not use plain nn.Linear for gate")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class TokenChoiceTopKRouter" in source, "TokenChoiceTopKRouter class present"),
    ("router_gating_linear" in source, "router_gating_linear function present"),
    ("def forward" in source, "forward methods present"),
    ("nn.Module" in source or "nn.Linear" in source, "nn module usage present"),
    (len(source.splitlines()) > 50, "file has substantial content"),
    ("self.gate" in source, "self.gate attribute present"),
]

failures = [desc for ok, desc in checks if not ok]
if failures:
    print(f"ANTI-STUB FAIL: missing: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file retains full implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: AGENTS.md line 13 @ commit 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: AGENTS.md line 80 @ commit 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral  (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  behavioral2 (${WEIGHTS[behavioral2]}): ${RESULTS[behavioral2]}"
echo "  structural  (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub    (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_no_wildcard (${WEIGHTS[config_no_wildcard]}): ${RESULTS[config_no_wildcard]}"
echo "  config_no_bare_print (${WEIGHTS[config_no_bare_print]}): ${RESULTS[config_no_bare_print]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
