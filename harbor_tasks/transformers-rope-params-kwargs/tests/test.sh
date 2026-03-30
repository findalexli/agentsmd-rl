#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/configuration_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weighted scoring
declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.33
WEIGHTS[behavioral2]=0.24
WEIGHTS[structural]=0.19
WEIGHTS[antistub]=0.19
WEIGHTS[config_ruff]=0.05

for key in behavioral behavioral2 structural antistub config_ruff; do
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

# ---------- PRIMARY 1 (35%): Behavioral fail-to-pass ----------
# When a config does NOT have rope_parameters attribute but kwargs contain
# rope_scaling and rope_theta, convert_rope_params_to_dict should still be called.
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/configuration_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the __post_init__ method in PreTrainedConfig
post_init_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedConfig":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                post_init_node = item
                break
        break

if post_init_node is None:
    print("BEHAVIORAL FAIL: __post_init__ not found in PreTrainedConfig")
    sys.exit(1)

# The fix must handle the case where hasattr(self, "rope_parameters") is False
# but kwargs has rope_scaling and rope_theta. Check that there's an elif/else
# branch after the hasattr check that handles kwargs with rope_scaling/rope_theta.
has_elif_rope_scaling = False
has_convert_call_in_elif = False

for node in ast.walk(post_init_node):
    if isinstance(node, ast.If):
        test_src = ast.get_source_segment(source, node.test) or ""
        if "rope_parameters" in test_src and "hasattr" in test_src:
            # Check for elif (orelse with If)
            for orelse_node in node.orelse:
                if isinstance(orelse_node, ast.If):
                    orelse_test = ast.get_source_segment(source, orelse_node.test) or ""
                    if "rope_scaling" in orelse_test or "rope_theta" in orelse_test:
                        has_elif_rope_scaling = True
                        for sub in ast.walk(orelse_node):
                            if isinstance(sub, ast.Call):
                                call_src = ast.get_source_segment(source, sub) or ""
                                if "convert_rope_params_to_dict" in call_src:
                                    has_convert_call_in_elif = True

if not has_elif_rope_scaling:
    print("BEHAVIORAL FAIL: no elif branch checking rope_scaling/rope_theta in kwargs")
    sys.exit(1)

if not has_convert_call_in_elif:
    print("BEHAVIORAL FAIL: elif branch does not call convert_rope_params_to_dict")
    sys.exit(1)

print("BEHAVIORAL PASS: elif branch handles rope_scaling/rope_theta in kwargs with conversion")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Warning emitted for legacy format ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/configuration_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

post_init_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedConfig":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__post_init__":
                post_init_node = item
                break
        break

if post_init_node is None:
    print("BEHAVIORAL2 FAIL: __post_init__ not found")
    sys.exit(1)

found_warning = False
for node in ast.walk(post_init_node):
    if isinstance(node, ast.If):
        test_src = ast.get_source_segment(source, node.test) or ""
        if "rope_parameters" in test_src and "hasattr" in test_src:
            for orelse_node in node.orelse:
                if isinstance(orelse_node, ast.If):
                    orelse_test = ast.get_source_segment(source, orelse_node.test) or ""
                    if "rope_scaling" in orelse_test or "rope_theta" in orelse_test:
                        for sub in ast.walk(orelse_node):
                            if isinstance(sub, ast.Expr) and isinstance(sub.value, ast.Call):
                                call_src = ast.get_source_segment(source, sub.value) or ""
                                if "warning" in call_src.lower() and "logger" in call_src:
                                    found_warning = True
                            elif isinstance(sub, ast.Call):
                                call_src = ast.get_source_segment(source, sub) or ""
                                if "warning" in call_src.lower() and "logger" in call_src:
                                    found_warning = True

if not found_warning:
    print("BEHAVIORAL2 FAIL: elif branch does not emit a warning for legacy RoPE format")
    sys.exit(1)

print("BEHAVIORAL2 PASS: warning emitted for legacy RoPE kwargs")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral2]=1
    echo "TEST behavioral2: PASS"
else
    echo "TEST behavioral2: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural check ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/transformers/src/transformers/configuration_utils.py"

with open(TARGET) as f:
    source = f.read()

if 'kwargs.get("rope_scaling")' not in source and "kwargs.get('rope_scaling')" not in source:
    print("STRUCTURAL FAIL: no kwargs.get for rope_scaling found")
    sys.exit(1)

if 'kwargs.get("rope_theta")' not in source and "kwargs.get('rope_theta')" not in source:
    print("STRUCTURAL FAIL: no kwargs.get for rope_theta found")
    sys.exit(1)

print("STRUCTURAL PASS: kwargs.get checks for rope_scaling and rope_theta present")
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

TARGET = "/workspace/transformers/src/transformers/configuration_utils.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class PreTrainedConfig" in source, "PreTrainedConfig class present"),
    ("def __post_init__" in source, "__post_init__ method present"),
    ("convert_rope_params_to_dict" in source, "convert_rope_params_to_dict referenced"),
    ("rope_parameters" in source, "rope_parameters referenced"),
    (len(source.splitlines()) > 500, "file has substantial content"),
    ("GenerationConfig" in source, "GenerationConfig still referenced"),
    ("def from_pretrained" in source, "from_pretrained method present"),
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
# Source: CLAUDE.md lines 5-10 @ commit d65c2b138a3d27a3321f7bbced0efc9bfb5a9688
echo "=== Config: ruff format check ==="
RUFF_OK=true
for f in /workspace/transformers/src/transformers/configuration_utils.py; do
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
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff': ${WEIGHTS[config_ruff]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff': ${RESULTS[config_ruff]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral  (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  behavioral2 (${WEIGHTS[behavioral2]}): ${RESULTS[behavioral2]}"
echo "  structural  (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub    (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff    (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
