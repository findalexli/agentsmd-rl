#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
DETAILS=""
REPO="/workspace/pytorch"

add_result() {
    local weight=$1 pass=$2 desc=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $desc\n"
    fi
}

# Helper: extract and exec the triton config class, return attribute value
exec_triton_class() {
    python3 -c "
import ast, os, sys
from typing import Optional, Any, Union, Literal

source = open('$REPO/torch/_inductor/config.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'triton':
        lines = source.splitlines()
        class_src = '\n'.join(lines[node.lineno - 1:node.end_lineno])
        ns = {
            'os': os,
            '__builtins__': __builtins__,
            'is_fbcode': lambda: False,
            'Optional': Optional,
            'Any': Any,
            'Union': Union,
            'Literal': Literal,
            'TYPE_CHECKING': False,
        }
        try:
            exec(class_src, ns)
            val = getattr(ns['triton'], '$1', 'MISSING')
            print(val)
        except Exception as e:
            print(f'EXEC_ERROR:{e}')
        sys.exit(0)
print('NOT_FOUND')
" 2>&1
}

# ============================================================
# GATE: Syntax check — abort on failure
# ============================================================
echo "=== GATE: Syntax check ==="
GATE_PASS=1

for f in \
    "$REPO/torch/_inductor/config.py" \
    "$REPO/torch/_inductor/codegen/triton.py" \
    "$REPO/torch/_inductor/runtime/triton_heuristics.py"; do
    if [ -f "$f" ]; then
        if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
            echo "GATE FAIL: $f has syntax errors"
            GATE_PASS=0
        fi
    fi
done

if [ "$GATE_PASS" = "0" ]; then
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "gate": "fail"}' > /logs/verifier/reward.json
    echo "Gate failed."
    exit 0
fi
echo "Gate passed."

# ============================================================
# Fail-to-pass: Config defaults to False (0.15)
# [pr_diff] (0.15): New config attribute defaults to disabling multi-stages
# On base commit: attribute doesn't exist -> MISSING -> FAIL
# ============================================================
echo ""
echo "=== F2P: Config default value ==="
CONFIG_DEFAULT=$(exec_triton_class mix_order_reduction_allow_multi_stages)

if [ "$CONFIG_DEFAULT" = "False" ]; then
    add_result 0.15 1 "Config mix_order_reduction_allow_multi_stages defaults to False"
else
    add_result 0.15 0 "Config should default to False (got: $CONFIG_DEFAULT)"
fi

# ============================================================
# Fail-to-pass: Config responds to env var (0.15)
# [pr_diff] (0.15): Setting env var enables multi-stages
# On base commit: attribute doesn't exist -> MISSING -> FAIL
# ============================================================
echo ""
echo "=== F2P: Env var enables multi-stages ==="
ENV_CHECK=$(TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES=1 \
    exec_triton_class mix_order_reduction_allow_multi_stages)

if [ "$ENV_CHECK" = "True" ]; then
    add_result 0.15 1 "Config is True when env var set to 1"
else
    add_result 0.15 0 "Config should be True when env var=1 (got: $ENV_CHECK)"
fi

# ============================================================
# Fail-to-pass: Heuristics limits stages when config=False (0.30)
# [pr_diff] (0.30): persistent_reduction sets MAX_NUM_STAGES=1 when disabled
# On base commit: no config check exists -> always multi-stage -> FAIL
#
# Strategy: Extract the AST node (If/IfExp/Assign) from persistent_reduction
# that connects mix_order_reduction_allow_multi_stages to MAX_NUM_STAGES,
# then exec it with mock variables to verify MAX_NUM_STAGES==1.
# ============================================================
echo ""
echo "=== F2P: Heuristics limits stages when disabled ==="
HEUR_CHECK=$(python3 << 'PYEOF'
import ast, sys, textwrap

source = open("/workspace/pytorch/torch/_inductor/runtime/triton_heuristics.py").read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "persistent_reduction":
        func_node = node
        break

if func_node is None:
    print("FUNC_NOT_FOUND")
    sys.exit(0)

# Strategy 1: Find an If/IfExp AST node containing both the config key and MAX_NUM_STAGES
for child in ast.walk(func_node):
    if isinstance(child, ast.If):
        segment = ast.get_source_segment(source, child)
        if segment and "mix_order_reduction_allow_multi_stages" in segment and "MAX_NUM_STAGES" in segment:
            block = textwrap.dedent(segment)
            ns = {
                "inductor_meta": {"mix_order_reduction_allow_multi_stages": False},
                "rnumel_hint": 10000,
                "num_iters": 8,
                "__builtins__": __builtins__,
            }
            try:
                exec(block, ns)
                ms = ns.get("MAX_NUM_STAGES")
                if ms == 1:
                    print("OK")
                else:
                    print(f"WRONG:{ms}")
            except Exception as e:
                print(f"EXEC_FAIL:{e}")
            sys.exit(0)

# Strategy 2: Find an Assign node with both references (ternary style)
for child in ast.walk(func_node):
    if isinstance(child, ast.Assign):
        segment = ast.get_source_segment(source, child)
        if segment and "MAX_NUM_STAGES" in segment and "mix_order_reduction_allow_multi_stages" in segment:
            block = textwrap.dedent(segment)
            ns = {
                "inductor_meta": {"mix_order_reduction_allow_multi_stages": False},
                "rnumel_hint": 10000,
                "__builtins__": __builtins__,
            }
            try:
                exec(block, ns)
                ms = ns.get("MAX_NUM_STAGES")
                if ms == 1:
                    print("OK")
                else:
                    print(f"WRONG:{ms}")
            except Exception as e:
                print(f"EXEC_FAIL:{e}")
            sys.exit(0)

# Strategy 3: Line-range extraction — find lines mentioning either keyword,
# take the range between first config-key mention and last MAX_NUM_STAGES mention
func_lines = source.splitlines()[func_node.lineno - 1:func_node.end_lineno]
config_line = None
max_stage_last = None
for i, line in enumerate(func_lines):
    if "mix_order_reduction_allow_multi_stages" in line and config_line is None:
        config_line = i
    if "MAX_NUM_STAGES" in line:
        max_stage_last = i

if config_line is not None and max_stage_last is not None and max_stage_last >= config_line:
    block_lines = func_lines[config_line:max_stage_last + 1]
    block = textwrap.dedent("\n".join(block_lines))
    ns = {
        "inductor_meta": {"mix_order_reduction_allow_multi_stages": False},
        "rnumel_hint": 10000,
        "num_iters": 8,
        "__builtins__": __builtins__,
    }
    try:
        exec(block, ns)
        ms = ns.get("MAX_NUM_STAGES")
        if ms == 1:
            print("OK")
        else:
            print(f"WRONG:{ms}")
    except Exception as e:
        print(f"RANGE_EXEC_FAIL:{e}")
    sys.exit(0)

# No config check found in persistent_reduction — base commit state
print("NO_CONFIG_CHECK")
PYEOF
)

if [ "$HEUR_CHECK" = "OK" ]; then
    add_result 0.30 1 "persistent_reduction sets MAX_NUM_STAGES=1 when multi-stages disabled"
else
    add_result 0.30 0 "Heuristics should limit to 1 stage when disabled (got: $HEUR_CHECK)"
fi

# ============================================================
# Fail-to-pass: Heuristics allows multi-stages when config=True (0.10)
# [pr_diff] (0.10): persistent_reduction allows >1 stages when enabled
# On base commit: no config check -> FAIL (NO_CONFIG_CHECK)
# ============================================================
echo ""
echo "=== F2P: Heuristics allows multi-stages when enabled ==="
HEUR_MULTI=$(python3 << 'PYEOF'
import ast, sys, textwrap

source = open("/workspace/pytorch/torch/_inductor/runtime/triton_heuristics.py").read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "persistent_reduction":
        func_node = node
        break

if func_node is None:
    print("FUNC_NOT_FOUND")
    sys.exit(0)

# Same extraction strategies as above, but test with allow_multi_stages=True
mock = {
    "inductor_meta": {"mix_order_reduction_allow_multi_stages": True},
    "rnumel_hint": 4096,
    "num_iters": 16,
    "__builtins__": __builtins__,
}

# Strategy 1: If node
for child in ast.walk(func_node):
    if isinstance(child, ast.If):
        segment = ast.get_source_segment(source, child)
        if segment and "mix_order_reduction_allow_multi_stages" in segment and "MAX_NUM_STAGES" in segment:
            block = textwrap.dedent(segment)
            ns = dict(mock)
            try:
                exec(block, ns)
                ms = ns.get("MAX_NUM_STAGES")
                print("OK" if ms is not None and ms > 1 else f"WRONG:{ms}")
            except Exception as e:
                print(f"EXEC_FAIL:{e}")
            sys.exit(0)

# Strategy 2: Assign node
for child in ast.walk(func_node):
    if isinstance(child, ast.Assign):
        segment = ast.get_source_segment(source, child)
        if segment and "MAX_NUM_STAGES" in segment and "mix_order_reduction_allow_multi_stages" in segment:
            block = textwrap.dedent(segment)
            ns = dict(mock)
            try:
                exec(block, ns)
                ms = ns.get("MAX_NUM_STAGES")
                print("OK" if ms is not None and ms > 1 else f"WRONG:{ms}")
            except Exception as e:
                print(f"EXEC_FAIL:{e}")
            sys.exit(0)

# Strategy 3: Line-range
func_lines = source.splitlines()[func_node.lineno - 1:func_node.end_lineno]
config_line = None
max_stage_last = None
for i, line in enumerate(func_lines):
    if "mix_order_reduction_allow_multi_stages" in line and config_line is None:
        config_line = i
    if "MAX_NUM_STAGES" in line:
        max_stage_last = i

if config_line is not None and max_stage_last is not None and max_stage_last >= config_line:
    block = textwrap.dedent("\n".join(func_lines[config_line:max_stage_last + 1]))
    ns = dict(mock)
    try:
        exec(block, ns)
        ms = ns.get("MAX_NUM_STAGES")
        print("OK" if ms is not None and ms > 1 else f"WRONG:{ms}")
    except Exception as e:
        print(f"RANGE_EXEC_FAIL:{e}")
    sys.exit(0)

print("NO_CONFIG_CHECK")
PYEOF
)

if [ "$HEUR_MULTI" = "OK" ]; then
    add_result 0.10 1 "persistent_reduction allows >1 stages when multi-stages enabled"
else
    add_result 0.10 0 "Heuristics should allow >1 stages when enabled (got: $HEUR_MULTI)"
fi

# ============================================================
# Behavioral: Codegen propagates config key via AST (0.15)
# [pr_diff] (0.15): inductor_meta_common includes the config key as a dict key
# Uses AST Constant node check — comments/strings in other contexts won't match
# ============================================================
echo ""
echo "=== Behavioral: Codegen propagation ==="
CODEGEN_CHECK=$(python3 << 'PYEOF'
import ast, sys

source = open("/workspace/pytorch/torch/_inductor/codegen/triton.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "inductor_meta_common":
        # Check that "mix_order_reduction_allow_multi_stages" appears as a
        # string constant key in a dict literal or subscript assignment
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                if child.value == "mix_order_reduction_allow_multi_stages":
                    print("OK")
                    sys.exit(0)
        print("MISSING")
        sys.exit(0)

print("FUNC_NOT_FOUND")
PYEOF
)

if [ "$CODEGEN_CHECK" = "OK" ]; then
    add_result 0.15 1 "inductor_meta_common includes mix_order_reduction_allow_multi_stages key"
else
    add_result 0.15 0 "inductor_meta_common should include the config key (got: $CODEGEN_CHECK)"
fi

# ============================================================
# Pass-to-pass: Existing config attributes still present (0.10)
# [repo_tests] (0.10): Other mix_order_reduction configs unchanged
# ============================================================
echo ""
echo "=== P2P: Existing configs intact ==="
P2P_PASS=1
for attr in mix_order_reduction mix_order_reduction_autotune_split_size mix_order_reduction_non_strict_mode; do
    VAL=$(exec_triton_class "$attr")
    if [ "$VAL" = "MISSING" ] || [ "$VAL" = "NOT_FOUND" ]; then
        P2P_PASS=0
        echo "  Missing existing config: $attr (got: $VAL)"
    fi
done

add_result 0.10 "$P2P_PASS" "Existing mix_order_reduction config attributes still present"

# ============================================================
# Anti-stub: Config actually toggles with env var (0.05)
# [static] (0.05): Not a bare `= False` — env var changes the value
# ============================================================
echo ""
echo "=== Anti-stub: Config toggles ==="
TOGGLE_CHECK=$(python3 << 'PYEOF'
import ast, os, sys
from typing import Optional, Any, Union, Literal

source = open("/workspace/pytorch/torch/_inductor/config.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "triton":
        lines = source.splitlines()
        class_src = "\n".join(lines[node.lineno - 1:node.end_lineno])
        base_ns = {
            "os": os,
            "__builtins__": __builtins__,
            "is_fbcode": lambda: False,
            "Optional": Optional,
            "Any": Any,
            "Union": Union,
            "Literal": Literal,
            "TYPE_CHECKING": False,
        }

        # Test WITHOUT env var
        env_backup = os.environ.pop(
            "TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES", None
        )
        ns1 = dict(base_ns)
        exec(class_src, ns1)
        val_off = getattr(ns1["triton"], "mix_order_reduction_allow_multi_stages", "MISSING")

        # Test WITH env var = 1
        os.environ["TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES"] = "1"
        ns2 = dict(base_ns)
        exec(class_src, ns2)
        val_on = getattr(ns2["triton"], "mix_order_reduction_allow_multi_stages", "MISSING")

        # Restore
        if env_backup is not None:
            os.environ["TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES"] = env_backup
        else:
            os.environ.pop("TORCHINDUCTOR_MIX_ORDER_REDUCTION_ALLOW_MULTI_STAGES", None)

        if val_off == False and val_on == True:
            print("OK")
        else:
            print(f"TOGGLE_FAIL:off={val_off},on={val_on}")
        sys.exit(0)
print("NOT_FOUND")
PYEOF
)

if [ "$TOGGLE_CHECK" = "OK" ]; then
    add_result 0.05 1 "Config toggles correctly with env var"
else
    add_result 0.05 0 "Config should toggle with env var (got: $TOGGLE_CHECK)"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "=== Results ==="
echo -e "$DETAILS"
echo "Total: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
print(json.dumps({
    'reward': round(score, 2),
    'behavioral': round(min(score, 0.85), 2),
    'regression': round(min(max(score - 0.85, 0), 0.10), 2),
    'config': 0.0,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
