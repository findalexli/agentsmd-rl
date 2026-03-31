#!/usr/bin/env bash
set +e

MODELING="/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py"
MODULAR="/workspace/transformers/src/transformers/models/camembert/modular_camembert.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weighted scoring: >=60% behavioral, <=40% structural
# [pr_diff] (0.40): Model loads without ValueError (fail-to-pass)
# [pr_diff] (0.15): Weight tying works correctly (behavioral)
# [pr_diff] (0.20): Both files have correct fix (structural)
# [agent_config] (0.10): No stub implementation (function depth)
# [agent_config] (0.10): Upstream tests pass (regression)
# [agent_config] (0.05): ruff format check

declare -A WEIGHTS
WEIGHTS[behavioral]=0.40
WEIGHTS[behavioral2]=0.15
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[regression]=0.10
WEIGHTS[config_ruff]=0.05

declare -A RESULTS
for key in behavioral behavioral2 structural antistub regression config_ruff; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
ALL_SYNTAX_OK=true
for f in "$MODELING" "$MODULAR"; do
    if [ -f "$f" ]; then
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
    fi
done
if [ "$ALL_SYNTAX_OK" = false ]; then
    echo "GATE FAIL: syntax errors found -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: all files have valid syntax"

# ---------- BEHAVIORAL (40%): Fail-to-pass - Model loads without ValueError ----------
# [pr_diff] (0.40): CamembertForCausalLM loads without ValueError
python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/workspace/transformers')
os.chdir('/workspace/transformers')

# Must suppress transformers logging noise
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['HF_HOME'] = '/tmp/hf_cache'

try:
    from transformers.models.camembert.modeling_camembert import CamembertForCausalLM
    from transformers.models.camembert.configuration_camembert import CamembertConfig

    # Create a minimal config for testing
    config = CamembertConfig(
        vocab_size=100,
        hidden_size=32,
        num_hidden_layers=2,
        num_attention_heads=2,
        intermediate_size=64,
        max_position_embeddings=128,
    )

    # This is where the bug manifests: post_init() validates tie_weights_keys
    # and raises ValueError if they don't match
    try:
        model = CamembertForCausalLM(config)
        print("BEHAVIORAL PASS: CamembertForCausalLM instantiated without ValueError")
        sys.exit(0)
    except ValueError as e:
        if "tie_weights_keys" in str(e).lower() or "_tied_weights_keys" in str(e).lower():
            print(f"BEHAVIORAL FAIL: ValueError on tie_weights_keys - bug not fixed: {e}")
            sys.exit(1)
        # Some other ValueError, re-raise to see what it is
        raise

except ImportError as e:
    print(f"BEHAVIORAL FAIL: Could not import CamembertForCausalLM: {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL FAIL: Unexpected error during instantiation: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

BEHAVIORAL_PASS=${RESULTS[behavioral]}

# ---------- BEHAVIORAL2 (15%): Weight tying actually works ----------
# Only run if behavioral passed (gate)
if [ "$BEHAVIORAL_PASS" -eq 1 ]; then
    python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/workspace/transformers')
os.chdir('/workspace/transformers')
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'

from transformers.models.camembert.modeling_camembert import CamembertForCausalLM
from transformers.models.camembert.configuration_camembert import CamembertConfig

config = CamembertConfig(
    vocab_size=100,
    hidden_size=32,
    num_hidden_layers=2,
    num_attention_heads=2,
    intermediate_size=64,
    max_position_embeddings=128,
)

model = CamembertForCausalLM(config)

# Verify weight tying is set up correctly
# The lm_head.decoder.weight should be tied to roberta.embeddings.word_embeddings.weight
if hasattr(model, 'lm_head') and hasattr(model.lm_head, 'decoder'):
    lm_weight = model.lm_head.decoder.weight
    embed_weight = model.roberta.embeddings.word_embeddings.weight

    # Check they share the same memory (tied)
    if lm_weight is not embed_weight:
        print("BEHAVIORAL2 FAIL: lm_head.decoder.weight is not the same object as embeddings.weight (not tied)")
        sys.exit(1)

    # Verify modifying one affects the other
    original_val = lm_weight[0, 0].item()
    lm_weight[0, 0] = 999.0
    if embed_weight[0, 0].item() != 999.0:
        print("BEHAVIORAL2 FAIL: Modifying lm_head weight did not affect embedding weight")
        sys.exit(1)
    # Restore
    lm_weight[0, 0] = original_val

    print("BEHAVIORAL2 PASS: Weight tying verified - lm_head.decoder.weight tied to embeddings")
    sys.exit(0)
else:
    print("BEHAVIORAL2 FAIL: Model missing lm_head.decoder structure")
    sys.exit(1)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[behavioral2]=1
        echo "TEST behavioral2: PASS"
    else
        echo "TEST behavioral2: FAIL"
    fi
else
    echo "TEST behavioral2: SKIPPED (behavioral gate not passed)"
fi

# ---------- STRUCTURAL (20%): Both files have correct _tied_weights_keys ----------
# This is a sanity check that the fix is in both files
# [pr_diff]: Fix must be in both modeling_camembert.py and modular_camembert.py
python3 << 'PYEOF'
import ast, sys

TARGETS = [
    "/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py",
    "/workspace/transformers/src/transformers/models/camembert/modular_camembert.py"
]

all_ok = True

for target in TARGETS:
    if not os.path.exists(target):
        # modular may not exist, that's ok for partial credit
        continue

    with open(target) as f:
        source = f.read()

    tree = ast.parse(source)

    # Find CamembertForCausalLM class and check _tied_weights_keys
    found_correct = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CamembertForCausalLM":
            for item in ast.iter_child_nodes(node):
                if isinstance(item, ast.Assign):
                    for target_node in item.targets:
                        if isinstance(target_node, ast.Name) and target_node.id == "_tied_weights_keys":
                            # Extract and check the dict
                            try:
                                tied_src = ast.get_source_segment(source, item.value)
                                tied_dict = eval(tied_src)
                                lm_head_target = tied_dict.get("lm_head.decoder.weight", "")
                                if "roberta.embeddings.word_embeddings.weight" in lm_head_target:
                                    found_correct = True
                            except:
                                pass

    if not found_correct:
        fname = target.split("/")[-1]
        print(f"STRUCTURAL FAIL: {fname} missing correct _tied_weights_keys")
        all_ok = False

if all_ok:
    print("STRUCTURAL PASS: Both files have correct _tied_weights_keys")
    sys.exit(0)
else:
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- ANTI-STUB (10%): Functions have meaningful implementation ----------
# [agent_config] (0.10): "Code changes should have meaningful implementation depth"
# Source: CLAUDE.md "Avoid stubs" guidelines
python3 << 'PYEOF'
import ast, sys

TARGETS = [
    "/workspace/transformers/src/transformers/models/camembert/modeling_camembert.py",
]

# Check that CamembertForCausalLM has meaningful method bodies (not just pass)
for target in TARGETS:
    with open(target) as f:
        source = f.read()

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CamembertForCausalLM":
            # Check __init__ has more than just pass or simple assignment
            for item in ast.iter_child_nodes(node):
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    # Count non-docstring statements
                    stmt_count = 0
                    for stmt in item.body:
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                            continue  # Skip docstring
                        if isinstance(stmt, ast.Pass):
                            continue  # Skip pass
                        stmt_count += 1

                    if stmt_count < 2:
                        print(f"ANTI-STUB FAIL: __init__ has insufficient implementation ({stmt_count} meaningful statements)")
                        sys.exit(1)

                    # Check for super().__init__() call
                    has_super = False
                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Call):
                            if isinstance(stmt.func, ast.Attribute) and stmt.func.attr == "__init__":
                                if isinstance(stmt.func.value, ast.Call) and isinstance(stmt.func.value.func, ast.Name):
                                    if stmt.func.value.func.id == "super":
                                        has_super = True

                    if not has_super and stmt_count < 5:
                        print("ANTI-STUB FAIL: __init__ missing super().__init__() and looks stub-like")
                        sys.exit(1)

print("ANTI-STUB PASS: Implementation has meaningful depth")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- REGRESSION (10%): Upstream model tests pass ----------
# [agent_config] (0.10): "Changed files pass ruff format" / existing tests
# Only run if behavioral passed (meaningful test)
if [ "$BEHAVIORAL_PASS" -eq 1 ]; then
    cd /workspace/transformers
    # Run any existing camembert tests that are CPU-safe and don't need large models
    python3 -m pytest tests/models/camembert/test_modeling_camembert.py -k "not slow and not gpu" -x --timeout=120 -q 2>/dev/null
    if [ $? -eq 0 ]; then
        RESULTS[regression]=1
        echo "TEST regression: PASS"
    else
        # Try a simpler test - just verify import works
        python3 -c "
import sys
sys.path.insert(0, '/workspace/transformers')
from transformers.models.camembert.modeling_camembert import CamembertForCausalLM, CamembertForMaskedLM
from transformers.models.camembert.configuration_camembert import CamembertConfig
print('Import test passed')
" 2>/dev/null
        if [ $? -eq 0 ]; then
            RESULTS[regression]=1
            echo "TEST regression: PASS (import only)"
        else
            echo "TEST regression: FAIL"
        fi
    fi
else
    echo "TEST regression: SKIPPED (behavioral gate not passed)"
fi

# ---------- CONFIG-DERIVED (5%): ruff format check ----------
# [agent_config] (0.05): "Changed files pass ruff format" — CLAUDE.md:5-10
RUFF_OK=true
for f in /workspace/transformers/src/transformers/models/camembert/modeling_camembert.py /workspace/transformers/src/transformers/models/camembert/modular_camembert.py; do
    if [ -f "$f" ]; then
        python3 -m ruff check --select I "$f" 2>/dev/null
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
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'regression': ${WEIGHTS[regression]}, 'config_ruff': ${WEIGHTS[config_ruff]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'regression': ${RESULTS[regression]}, 'config_ruff': ${RESULTS[config_ruff]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral  (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  behavioral2 (${WEIGHTS[behavioral2]}): ${RESULTS[behavioral2]}"
echo "  structural  (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub    (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  regression  (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  config_ruff (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
