#!/usr/bin/env bash
set +e

MODELING="/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py"
MODULAR="/workspace/transformers/src/transformers/models/camembert/modular_camembert.py"
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
ALL_SYNTAX_OK=true
for f in "$MODELING" "$MODULAR"; do
    python3 -c "
import ast, sys
try:
    with open('$f') as fh:
        ast.parse(fh.read())
except SyntaxError as e:
    print(f'GATE FAIL: {e}')
    sys.exit(1)
"
    if [ $? -ne 0 ]; then
        ALL_SYNTAX_OK=false
    fi
done
if [ "$ALL_SYNTAX_OK" = false ]; then
    echo "GATE FAIL: syntax errors found -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: all files have valid syntax"

# ---------- PRIMARY 1 (35%): Behavioral - modeling_camembert.py has correct tied key ----------
# The bug is that _tied_weights_keys maps lm_head.decoder.weight to
# "camembert.embeddings.word_embeddings.weight" instead of
# "roberta.embeddings.word_embeddings.weight".
# Extract the dict value via AST and verify it references "roberta", not "camembert".
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find CamembertForCausalLM class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CamembertForCausalLM":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL FAIL: CamembertForCausalLM class not found")
    sys.exit(1)

# Find _tied_weights_keys assignment
tied_keys_node = None
for item in ast.iter_child_nodes(cls_node):
    if isinstance(item, ast.Assign):
        for target in item.targets:
            if isinstance(target, ast.Name) and target.id == "_tied_weights_keys":
                tied_keys_node = item
                break

if tied_keys_node is None:
    print("BEHAVIORAL FAIL: _tied_weights_keys not found in CamembertForCausalLM")
    sys.exit(1)

# Evaluate the dict to check values
tied_src = ast.get_source_segment(source, tied_keys_node.value)
if tied_src is None:
    print("BEHAVIORAL FAIL: could not extract _tied_weights_keys source")
    sys.exit(1)

# Safely eval the dict literal
try:
    tied_dict = eval(tied_src)
except Exception as e:
    print(f"BEHAVIORAL FAIL: could not eval _tied_weights_keys: {e}")
    sys.exit(1)

# Check that lm_head.decoder.weight maps to roberta.*, not camembert.*
lm_head_target = tied_dict.get("lm_head.decoder.weight", "")
if "camembert" in lm_head_target:
    print(f"BEHAVIORAL FAIL: lm_head.decoder.weight still maps to '{lm_head_target}' (contains 'camembert')")
    sys.exit(1)

if "roberta.embeddings.word_embeddings.weight" not in lm_head_target:
    print(f"BEHAVIORAL FAIL: lm_head.decoder.weight maps to '{lm_head_target}', expected 'roberta.embeddings.word_embeddings.weight'")
    sys.exit(1)

print(f"BEHAVIORAL PASS: lm_head.decoder.weight correctly maps to '{lm_head_target}'")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - modular_camembert.py also has correct tied key ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/models/camembert/modular_camembert.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find CamembertForCausalLM class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CamembertForCausalLM":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL2 FAIL: CamembertForCausalLM class not found in modular file")
    sys.exit(1)

# Find _tied_weights_keys assignment
tied_keys_node = None
for item in ast.iter_child_nodes(cls_node):
    if isinstance(item, ast.Assign):
        for target in item.targets:
            if isinstance(target, ast.Name) and target.id == "_tied_weights_keys":
                tied_keys_node = item
                break

if tied_keys_node is None:
    print("BEHAVIORAL2 FAIL: _tied_weights_keys not defined in modular CamembertForCausalLM")
    sys.exit(1)

tied_src = ast.get_source_segment(source, tied_keys_node.value)
if tied_src is None:
    print("BEHAVIORAL2 FAIL: could not extract _tied_weights_keys source")
    sys.exit(1)

try:
    tied_dict = eval(tied_src)
except Exception as e:
    print(f"BEHAVIORAL2 FAIL: could not eval _tied_weights_keys: {e}")
    sys.exit(1)

lm_head_target = tied_dict.get("lm_head.decoder.weight", "")
if "camembert" in lm_head_target:
    print(f"BEHAVIORAL2 FAIL: modular lm_head.decoder.weight still maps to '{lm_head_target}'")
    sys.exit(1)

if "roberta.embeddings.word_embeddings.weight" not in lm_head_target:
    print(f"BEHAVIORAL2 FAIL: modular lm_head.decoder.weight maps to '{lm_head_target}'")
    sys.exit(1)

# Also check lm_head.decoder.bias -> lm_head.bias
bias_target = tied_dict.get("lm_head.decoder.bias", "")
if bias_target != "lm_head.bias":
    print(f"BEHAVIORAL2 WARN: lm_head.decoder.bias maps to '{bias_target}', expected 'lm_head.bias'")

print(f"BEHAVIORAL2 PASS: modular _tied_weights_keys correctly defined")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral2]=1
    echo "TEST behavioral2: PASS"
else
    echo "TEST behavioral2: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - no "camembert." in tied weights keys ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py"

with open(TARGET) as f:
    source = f.read()

# Check that there is no "camembert.embeddings.word_embeddings.weight" in _tied_weights_keys context
# We look for lines containing both _tied_weights_keys-related dict entries and "camembert.embeddings"
in_tied_block = False
bad_lines = []
for line in source.splitlines():
    stripped = line.strip()
    if "_tied_weights_keys" in stripped:
        in_tied_block = True
    if in_tied_block:
        if "camembert.embeddings" in stripped:
            bad_lines.append(stripped)
        if stripped.startswith("}"):
            in_tied_block = False

if bad_lines:
    print(f"STRUCTURAL FAIL: found 'camembert.embeddings' in _tied_weights_keys context: {bad_lines}")
    sys.exit(1)

print("STRUCTURAL PASS: no incorrect 'camembert.embeddings' reference in tied weights")
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

all_ok = True
for target in [
    "/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py",
    "/workspace/transformers/src/transformers/models/camembert/modular_camembert.py",
]:
    with open(target) as f:
        source = f.read()
    checks = [
        ("class CamembertForCausalLM" in source, "CamembertForCausalLM class present"),
        ("_tied_weights_keys" in source, "_tied_weights_keys present"),
        ("def __init__" in source or "def forward" in source, "methods present"),
        (len(source.splitlines()) > 50, "file has substantial content"),
    ]
    failures = [desc for ok, desc in checks if not ok]
    if failures:
        fname = target.split("/")[-1]
        print(f"ANTI-STUB FAIL ({fname}): {', '.join(failures)}")
        all_ok = False

if not all_ok:
    sys.exit(1)

print("ANTI-STUB PASS: files retain full implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi


# ---------- CONFIG-DERIVED (5%): ruff format check on changed files ----------
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit d81ad48109331f910fd81f699869855cbd50f681
echo "=== Config: ruff format check ==="
RUFF_OK=true
for f in /workspace/transformers/src/transformers/models/camembert/modeling_camembert.py /workspace/transformers/src/transformers/models/camembert/modular_camembert.py; do
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
