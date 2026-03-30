#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_signature]=0.24
WEIGHTS[behavioral_arange]=0.24
WEIGHTS[behavioral_callsite]=0.14
WEIGHTS[structural]=0.19
WEIGHTS[antistub]=0.14
WEIGHTS[config_ruff]=0.05

for key in behavioral_signature behavioral_arange behavioral_callsite structural antistub config_ruff; do
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

# ---------- PRIMARY 1 (25%): Behavioral - relative_positional_encoding accepts device param ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find XLNetModel class -> relative_positional_encoding method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "XLNetModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "relative_positional_encoding":
                # Check if it has a 'device' parameter
                param_names = [arg.arg for arg in item.args.args]
                if "device" in param_names:
                    print("BEHAVIORAL_SIGNATURE PASS: relative_positional_encoding has device parameter")
                    sys.exit(0)
                else:
                    print(f"BEHAVIORAL_SIGNATURE FAIL: params are {param_names}, missing 'device'")
                    sys.exit(1)

print("BEHAVIORAL_SIGNATURE FAIL: could not find XLNetModel.relative_positional_encoding")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_signature]=1
    echo "TEST behavioral_signature: PASS"
else
    echo "TEST behavioral_signature: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - torch.arange calls use device parameter ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find relative_positional_encoding method
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "XLNetModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "relative_positional_encoding":
                func_node = item
                break

if func_node is None:
    print("BEHAVIORAL_ARANGE FAIL: method not found")
    sys.exit(1)

# Find all torch.arange calls in the method and check they have device= keyword
arange_calls = []
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr == "arange" and
            isinstance(func.value, ast.Name) and func.value.id == "torch"):
            arange_calls.append(node)

if not arange_calls:
    print("BEHAVIORAL_ARANGE FAIL: no torch.arange calls found")
    sys.exit(1)

all_have_device = True
for call in arange_calls:
    has_device = any(kw.arg == "device" for kw in call.keywords)
    if not has_device:
        line = call.lineno
        print(f"  FAIL: torch.arange at line {line} missing device= keyword")
        all_have_device = False

if all_have_device:
    print(f"BEHAVIORAL_ARANGE PASS: all {len(arange_calls)} torch.arange calls have device= parameter")
    sys.exit(0)
else:
    print("BEHAVIORAL_ARANGE FAIL: some torch.arange calls missing device=")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_arange]=1
    echo "TEST behavioral_arange: PASS"
else
    echo "TEST behavioral_arange: FAIL"
fi

# ---------- PRIMARY 3 (15%): Behavioral - call site passes device, no .to() ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find XLNetModel.forward method
forward_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "XLNetModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                forward_node = item
                break

if forward_node is None:
    print("BEHAVIORAL_CALLSITE FAIL: XLNetModel.forward not found")
    sys.exit(1)

forward_src = ast.get_source_segment(source, forward_node)
if forward_src is None:
    lines = source.splitlines()
    forward_src = "\n".join(lines[forward_node.lineno - 1 : forward_node.end_lineno])

# Check that the call to relative_positional_encoding passes device=
if "device=" in forward_src and "relative_positional_encoding" in forward_src:
    # Also check that the old .to(output_h.device) pattern after pos_emb is removed
    import re
    # Look for pos_emb = ... .to(output_h.device) or pos_emb.to(
    old_pattern = re.search(r'pos_emb\s*=\s*self\.relative_positional_encoding.*\n\s*pos_emb\s*=\s*pos_emb\.to\(', forward_src)
    if old_pattern:
        print("BEHAVIORAL_CALLSITE FAIL: old .to() pattern still present after relative_positional_encoding call")
        sys.exit(1)
    print("BEHAVIORAL_CALLSITE PASS: call site passes device= and no redundant .to()")
    sys.exit(0)
else:
    print("BEHAVIORAL_CALLSITE FAIL: call site does not pass device= to relative_positional_encoding")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_callsite]=1
    echo "TEST behavioral_callsite: PASS"
else
    echo "TEST behavioral_callsite: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - no .to(device) after relative_positional_encoding ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

# Check that the pattern "pos_emb = pos_emb.to(output_h.device)" is gone
if "pos_emb.to(output_h.device)" in source or "pos_emb = pos_emb.to(" in source:
    print("STRUCTURAL FAIL: redundant .to() still present for pos_emb")
    sys.exit(1)
else:
    print("STRUCTURAL PASS: no redundant .to() for pos_emb")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (15%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class XLNetModel" in source, "XLNetModel class present"),
    ("def relative_positional_encoding" in source, "method present"),
    ("def forward" in source, "forward method present"),
    ("torch.arange" in source, "torch.arange used"),
    (len(source.splitlines()) > 500, "file has substantial content"),
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


# ---------- CONFIG-DERIVED (5%): ruff format check on changed files ----------
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit be6cf0848668852e3267d297211eb7e983e6c786
echo "=== Config: ruff format check ==="
RUFF_OK=true
for f in /workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py; do
    if [ -f "$f" ]; then
        ruff check --select I "$f" 2>/dev/null
        if [ $? -ne 0 ]; then RUFF_OK=false; fi
    fi
done
if [ "$RUFF_OK" = true ]; then
    RESULTS[config_ruff]=1
    echo "TEST config_ruff: PASS"
else
    echo "TEST config_ruff: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_signature': ${WEIGHTS[behavioral_signature]}, 'behavioral_arange': ${WEIGHTS[behavioral_arange]}, 'behavioral_callsite': ${WEIGHTS[behavioral_callsite]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff': ${WEIGHTS[config_ruff]}}
results = {'behavioral_signature': ${RESULTS[behavioral_signature]}, 'behavioral_arange': ${RESULTS[behavioral_arange]}, 'behavioral_callsite': ${RESULTS[behavioral_callsite]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff': ${RESULTS[config_ruff]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_signature (${WEIGHTS[behavioral_signature]}): ${RESULTS[behavioral_signature]}"
echo "  behavioral_arange    (${WEIGHTS[behavioral_arange]}): ${RESULTS[behavioral_arange]}"
echo "  behavioral_callsite  (${WEIGHTS[behavioral_callsite]}): ${RESULTS[behavioral_callsite]}"
echo "  structural           (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub             (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff    (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
