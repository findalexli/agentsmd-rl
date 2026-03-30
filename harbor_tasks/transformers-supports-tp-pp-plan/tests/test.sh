#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/modeling_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_tp]=0.23
WEIGHTS[behavioral_pp]=0.24
WEIGHTS[behavioral_pp_setter]=0.10
WEIGHTS[structural]=0.19
WEIGHTS[antistub]=0.19
WEIGHTS[config_ruff]=0.05

for key in behavioral_tp behavioral_pp behavioral_pp_setter structural antistub config_ruff; do
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

# ---------- PRIMARY 1 (25%): Behavioral - supports_tp_plan uses truthiness not 'is not None' ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find supports_tp_plan property
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "supports_tp_plan":
                func_node = item
                break

if func_node is None:
    print("BEHAVIORAL_TP FAIL: supports_tp_plan not found")
    sys.exit(1)

func_src = ast.get_source_segment(source, func_node)
if func_src is None:
    lines = source.splitlines()
    func_src = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# The bug: using 'is not None' instead of truthiness check
# The fix should use 'if self._tp_plan:' not 'if self._tp_plan is not None:'
if "_tp_plan is not None" in func_src:
    print("BEHAVIORAL_TP FAIL: still using 'is not None' check for _tp_plan")
    sys.exit(1)

# Check it uses truthiness
if "self._tp_plan" in func_src or "self.base_model._tp_plan" in func_src:
    print("BEHAVIORAL_TP PASS: supports_tp_plan uses truthiness check")
    sys.exit(0)
else:
    print("BEHAVIORAL_TP FAIL: _tp_plan not referenced in supports_tp_plan")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_tp]=1
    echo "TEST behavioral_tp: PASS"
else
    echo "TEST behavioral_tp: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - supports_pp_plan uses truthiness not 'is not None' ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "supports_pp_plan":
                func_node = item
                break

if func_node is None:
    print("BEHAVIORAL_PP FAIL: supports_pp_plan not found")
    sys.exit(1)

func_src = ast.get_source_segment(source, func_node)
if func_src is None:
    lines = source.splitlines()
    func_src = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

if "_pp_plan is not None" in func_src:
    print("BEHAVIORAL_PP FAIL: still using 'is not None' check for _pp_plan")
    sys.exit(1)

# Also check that config.base_model_pp_plan is checked
if "base_model_pp_plan" in func_src:
    print("BEHAVIORAL_PP PASS: supports_pp_plan uses truthiness and checks config")
    sys.exit(0)
else:
    # Accept without config check if truthiness is fixed
    if "self._pp_plan" in func_src or "self.base_model._pp_plan" in func_src:
        print("BEHAVIORAL_PP PASS: supports_pp_plan uses truthiness check")
        sys.exit(0)

print("BEHAVIORAL_PP FAIL: _pp_plan not properly referenced")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_pp]=1
    echo "TEST behavioral_pp: PASS"
else
    echo "TEST behavioral_pp: FAIL"
fi

# ---------- PRIMARY 3 (10%): Behavioral - pp_plan setter has validation ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find pp_plan setter
setter_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "pp_plan":
                # Check if this is a setter (has @pp_plan.setter decorator)
                for dec in item.decorator_list:
                    dec_src = ast.get_source_segment(source, dec)
                    if dec_src and "setter" in dec_src:
                        setter_node = item
                        break

if setter_node is None:
    print("BEHAVIORAL_PP_SETTER FAIL: pp_plan setter not found")
    sys.exit(1)

setter_src = ast.get_source_segment(source, setter_node)
if setter_src is None:
    lines = source.splitlines()
    setter_src = "\n".join(lines[setter_node.lineno - 1 : setter_node.end_lineno])

# Check for input validation (isinstance check or ValueError)
if "isinstance" in setter_src or "ValueError" in setter_src:
    print("BEHAVIORAL_PP_SETTER PASS: pp_plan setter has input validation")
    sys.exit(0)
else:
    print("BEHAVIORAL_PP_SETTER FAIL: pp_plan setter lacks validation")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_pp_setter]=1
    echo "TEST behavioral_pp_setter: PASS"
else
    echo "TEST behavioral_pp_setter: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - PipelineParallel enum removed ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check that PipelineParallel enum class is removed
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PipelineParallel":
        print("STRUCTURAL FAIL: PipelineParallel enum still present")
        sys.exit(1)

# Check that Enum import is removed (if not used elsewhere)
if "from enum import Enum" in source:
    # Check if Enum is used anywhere else
    enum_uses = source.count("Enum")
    # The import line counts as one use
    if enum_uses <= 1:
        print("STRUCTURAL FAIL: unused Enum import still present")
        sys.exit(1)

print("STRUCTURAL PASS: PipelineParallel removed and Enum import cleaned up")
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

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class PreTrainedModel" in source, "PreTrainedModel class present"),
    ("supports_tp_plan" in source, "supports_tp_plan present"),
    ("supports_pp_plan" in source, "supports_pp_plan present"),
    ("_tp_plan" in source, "_tp_plan referenced"),
    ("_pp_plan" in source, "_pp_plan referenced"),
    (len(source.splitlines()) > 1000, "file has substantial content"),
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
# Source: CLAUDE.md lines 5-10 @ commit 09fea1e6e970a1051b1141ce320a3d696b2c15ed
echo "=== Config: ruff format check ==="
RUFF_OK=true
for f in /workspace/transformers/src/transformers/modeling_utils.py; do
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
weights = {'behavioral_tp': ${WEIGHTS[behavioral_tp]}, 'behavioral_pp': ${WEIGHTS[behavioral_pp]}, 'behavioral_pp_setter': ${WEIGHTS[behavioral_pp_setter]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff': ${WEIGHTS[config_ruff]}}
results = {'behavioral_tp': ${RESULTS[behavioral_tp]}, 'behavioral_pp': ${RESULTS[behavioral_pp]}, 'behavioral_pp_setter': ${RESULTS[behavioral_pp_setter]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff': ${RESULTS[config_ruff]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_tp        (${WEIGHTS[behavioral_tp]}): ${RESULTS[behavioral_tp]}"
echo "  behavioral_pp        (${WEIGHTS[behavioral_pp]}): ${RESULTS[behavioral_pp]}"
echo "  behavioral_pp_setter (${WEIGHTS[behavioral_pp_setter]}): ${RESULTS[behavioral_pp_setter]}"
echo "  structural           (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub             (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff    (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
