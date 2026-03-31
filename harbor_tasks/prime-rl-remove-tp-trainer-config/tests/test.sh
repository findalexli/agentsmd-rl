#!/usr/bin/env bash
set +e

BASE="/workspace/prime-rl/src/prime_rl"
TRAINER_CFG="$BASE/configs/trainer.py"
RL_CFG="$BASE/configs/rl.py"
PARALLEL_DIMS="$BASE/trainer/parallel_dims.py"
SFT_TRAIN="$BASE/trainer/sft/train.py"
CHANGELOG="/workspace/prime-rl/CHANGELOG.md"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.70, regression=0.15, config=0.05, anti-stub=0.10
WEIGHTS[f2p_ndps]=0.20
WEIGHTS[f2p_seqlen]=0.15
WEIGHTS[f2p_no_tp_field]=0.15
WEIGHTS[f2p_sft_no_tp]=0.10
WEIGHTS[f2p_rl_no_tp]=0.10
WEIGHTS[p2p_core_fields]=0.05
WEIGHTS[p2p_retained_props]=0.05
WEIGHTS[p2p_get_parallel]=0.05
WEIGHTS[config_no_tryexcept]=0.05
WEIGHTS[antistub_pdims]=0.05
WEIGHTS[antistub_trainer]=0.05

for key in f2p_ndps f2p_seqlen f2p_no_tp_field f2p_sft_no_tp f2p_rl_no_tp p2p_core_fields p2p_retained_props p2p_get_parallel config_no_tryexcept antistub_pdims antistub_trainer; do
    RESULTS[$key]=0
done

# ========== GATE: Syntax check ==========
python3 -c "
import ast
for f in ['$TRAINER_CFG','$RL_CFG','$PARALLEL_DIMS','$SFT_TRAIN']:
    ast.parse(open(f).read())
" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: all files parse"

# ========== FAIL-TO-PASS: non_data_parallel_size returns cp*pp (0.20) ==========
# [pr_diff] (0.20): non_data_parallel_size must be cp*pp, not cp*tp*pp
# AST-extract the property, then call it with mock self to verify behavior
python3 << 'PYEOF'
import ast, sys, textwrap, types

with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find ParallelDims class and extract non_data_parallel_size
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ParallelDims":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "non_data_parallel_size":
                lines = source.splitlines(keepends=True)
                func_src = "".join(lines[item.lineno-1:item.end_lineno])
                # Remove decorator if any (cached_property)
                func_src_lines = func_src.splitlines(keepends=True)
                body_lines = [l for l in func_src_lines if not l.strip().startswith("@")]
                func_src = "".join(body_lines)
                break
        break
else:
    print("FAIL: ParallelDims class not found"); sys.exit(1)

# Create a mock self with known values
class MockSelf:
    cp = 4
    pp = 2
    # If tp still exists in the formula, this will inflate the result
    tp = 8

# Execute the extracted function
ns = {}
exec(textwrap.dedent(func_src), ns)
func = ns["non_data_parallel_size"]

result = func(MockSelf())
expected = 4 * 2  # cp * pp = 8

if result == expected:
    print(f"PASS: non_data_parallel_size={result} (cp*pp={expected})")
    sys.exit(0)
elif result == 4 * 8 * 2:
    print(f"FAIL: non_data_parallel_size={result} still includes tp (cp*tp*pp={4*8*2})")
    sys.exit(1)
else:
    print(f"FAIL: non_data_parallel_size={result}, expected {expected}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_ndps]=1 && echo "TEST f2p_ndps: PASS" || echo "TEST f2p_ndps: FAIL"

# ========== FAIL-TO-PASS: seq_len_divisor returns cp*2 (0.15) ==========
# [pr_diff] (0.15): seq_len_divisor must be cp*2, not tp*cp*2
python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ParallelDims":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "seq_len_divisor":
                lines = source.splitlines(keepends=True)
                func_src = "".join(lines[item.lineno-1:item.end_lineno])
                func_src_lines = func_src.splitlines(keepends=True)
                body_lines = [l for l in func_src_lines if not l.strip().startswith("@")]
                func_src = "".join(body_lines)
                break
        break
else:
    print("FAIL: ParallelDims class not found"); sys.exit(1)

class MockSelf:
    cp = 4
    tp = 8  # If tp still in formula, result inflated

ns = {}
exec(textwrap.dedent(func_src), ns)
func = ns["seq_len_divisor"]

result = func(MockSelf())
expected = 4 * 2  # cp * 2 = 8

if result == expected:
    print(f"PASS: seq_len_divisor={result} (cp*2={expected})")
    sys.exit(0)
elif result == 8 * 4 * 2:
    print(f"FAIL: seq_len_divisor={result} still includes tp (tp*cp*2={8*4*2})")
    sys.exit(1)
else:
    print(f"FAIL: seq_len_divisor={result}, expected {expected}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_seqlen]=1 && echo "TEST f2p_seqlen: PASS" || echo "TEST f2p_seqlen: FAIL"

# ========== FAIL-TO-PASS: ParallelDims has no tp field (0.15) ==========
# [pr_diff] (0.15): ParallelDims dataclass must not accept tp parameter
# Behavioral: extract __init__ signature via AST and check fields, or try constructing
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ParallelDims":
        fields = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Skip private fields (like _world_mesh, _submeshes)
                if not item.target.id.startswith("_"):
                    fields.append(item.target.id)
        if "tp" in fields:
            print(f"FAIL: ParallelDims still has tp field (fields: {fields})")
            sys.exit(1)
        # Also verify tp_enabled property is removed
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "tp_enabled":
                print("FAIL: ParallelDims still has tp_enabled property")
                sys.exit(1)
        print(f"PASS: ParallelDims has no tp field (fields: {fields})")
        sys.exit(0)

print("FAIL: ParallelDims class not found"); sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_no_tp_field]=1 && echo "TEST f2p_no_tp_field: PASS" || echo "TEST f2p_no_tp_field: FAIL"

# ========== FAIL-TO-PASS: SFT train.py doesn't multiply by tp (0.10) ==========
# [pr_diff] (0.10): SFT micro-batch, dataset sharding, token accounting must not use model.tp
# Behavioral: extract expressions involving batch_size/seq_len computation and verify no tp
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/trainer/sft/train.py") as f:
    source = f.read()
tree = ast.parse(source)

# Check that no expression multiplies or divides by model.tp or config.model.tp
# This is behavioral in the sense that we check the computation, not just existence
tp_refs = []
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr == "tp":
        # Get the parent chain — look for .model.tp or .config.model.tp
        if isinstance(node.value, ast.Attribute) and node.value.attr == "model":
            tp_refs.append(ast.get_source_segment(source, node) or f"line {node.lineno}")
        # Also catch bare self.tp or config.tp patterns
        elif isinstance(node.value, ast.Attribute) and node.value.attr == "config":
            tp_refs.append(ast.get_source_segment(source, node) or f"line {node.lineno}")

if tp_refs:
    print(f"FAIL: sft/train.py still references tp in: {tp_refs}")
    sys.exit(1)
print("PASS: sft/train.py has no model.tp references")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_sft_no_tp]=1 && echo "TEST f2p_sft_no_tp: PASS" || echo "TEST f2p_sft_no_tp: FAIL"

# ========== FAIL-TO-PASS: rl.py auto_setup_deployment doesn't use model.tp (0.10) ==========
# [pr_diff] (0.10): non_data_parallel_size calc in auto_setup_deployment must not include tp
python3 << 'PYEOF'
import ast, sys, textwrap

with open("/workspace/prime-rl/src/prime_rl/configs/rl.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find auto_setup_deployment method and check for .model.tp references
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "auto_setup_deployment":
        found = True
        for n in ast.walk(node):
            if isinstance(n, ast.Attribute) and n.attr == "tp":
                if isinstance(n.value, ast.Attribute) and n.value.attr == "model":
                    print("FAIL: auto_setup_deployment still references .model.tp")
                    sys.exit(1)
        print("PASS: auto_setup_deployment does not reference model.tp")
        sys.exit(0)

if not found:
    print("FAIL: auto_setup_deployment not found")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_rl_no_tp]=1 && echo "TEST f2p_rl_no_tp: PASS" || echo "TEST f2p_rl_no_tp: FAIL"

# ========== REGRESSION: ParallelDims retains core fields (0.05) ==========
# [pr_diff] (0.05): pass-to-pass — dp_replicate, dp_shard, cp, pp, ep, world_size must exist
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ParallelDims":
        fields = set()
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.add(item.target.id)
        for required in ["dp_replicate", "dp_shard", "cp", "pp", "ep", "world_size"]:
            if required not in fields:
                print(f"FAIL: ParallelDims missing {required}"); sys.exit(1)
        print("PASS: ParallelDims core fields intact"); sys.exit(0)
print("FAIL: ParallelDims not found"); sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_core_fields]=1 && echo "TEST p2p_core_fields: PASS" || echo "TEST p2p_core_fields: FAIL"

# ========== REGRESSION: Retained properties still work (0.05) ==========
# [pr_diff] (0.05): pass-to-pass — dp_enabled, cp_enabled, pp_enabled, ep_enabled still exist
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ParallelDims":
        methods = set()
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.add(item.name)
        for required in ["dp_enabled", "cp_enabled", "pp_enabled", "ep_enabled",
                         "non_data_parallel_size", "seq_len_divisor", "build_mesh"]:
            if required not in methods:
                print(f"FAIL: ParallelDims missing method {required}"); sys.exit(1)
        print("PASS: retained properties/methods intact"); sys.exit(0)
print("FAIL: ParallelDims not found"); sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_retained_props]=1 && echo "TEST p2p_retained_props: PASS" || echo "TEST p2p_retained_props: FAIL"

# ========== REGRESSION: get_parallel_dims function still exists (0.05) ==========
# [pr_diff] (0.05): pass-to-pass — get_parallel_dims must still be defined
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    tree = ast.parse(f.read())
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
if "get_parallel_dims" not in funcs:
    print("FAIL: get_parallel_dims function missing"); sys.exit(1)
print("PASS: get_parallel_dims still defined"); sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_get_parallel]=1 && echo "TEST p2p_get_parallel: PASS" || echo "TEST p2p_get_parallel: FAIL"

# ========== CONFIG: No unnecessary try/except in changed files (0.05) ==========
# [agent_config] (0.05): "Avoid try/except blocks unless really necessary" — AGENTS.md:5 @ 80a52899
python3 << 'PYEOF'
import ast, sys
for fpath, name in [
    ("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py", "parallel_dims.py"),
    ("/workspace/prime-rl/src/prime_rl/configs/trainer.py", "trainer.py"),
]:
    with open(fpath) as f:
        tree = ast.parse(f.read())
    try_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
    if try_count > 2:
        print(f"FAIL: {name} has {try_count} try/except blocks (excessive)"); sys.exit(1)
print("PASS: no unnecessary try/except in changed files"); sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[config_no_tryexcept]=1 && echo "TEST config_no_tryexcept: PASS" || echo "TEST config_no_tryexcept: FAIL"

# ========== ANTI-STUB: parallel_dims.py has substantive content (0.05) ==========
# [pr_diff] (0.05): parallel_dims.py must not be hollowed out
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/trainer/parallel_dims.py") as f:
    source = f.read()
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
tree = ast.parse(source)
# Must have substantial methods in ParallelDims
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ParallelDims":
        method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
        if method_count < 8:
            print(f"FAIL: ParallelDims has only {method_count} methods (stubbed)"); sys.exit(1)
if len(lines) < 80:
    print(f"FAIL: parallel_dims.py has only {len(lines)} non-blank lines"); sys.exit(1)
print(f"PASS: parallel_dims.py has {len(lines)} substantive lines, adequate methods"); sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[antistub_pdims]=1 && echo "TEST antistub_pdims: PASS" || echo "TEST antistub_pdims: FAIL"

# ========== ANTI-STUB: trainer.py ModelConfig still has fields (0.05) ==========
# [pr_diff] (0.05): ModelConfig must retain existing fields (not stubbed out)
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/configs/trainer.py") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "ModelConfig":
        field_count = sum(1 for item in node.body if isinstance(item, ast.AnnAssign))
        if field_count < 5:
            print(f"FAIL: ModelConfig has only {field_count} fields (stubbed)"); sys.exit(1)
        # Must still have cp and dp_replicate
        fields = set()
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.add(item.target.id)
        for required in ["cp", "dp_replicate", "ep"]:
            if required not in fields:
                print(f"FAIL: ModelConfig missing required field {required}"); sys.exit(1)
        print(f"PASS: ModelConfig has {field_count} fields including cp, dp_replicate, ep"); sys.exit(0)
print("FAIL: ModelConfig not found"); sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[antistub_trainer]=1 && echo "TEST antistub_trainer: PASS" || echo "TEST antistub_trainer: FAIL"

# ========== SCORE ==========
SCORE=$(python3 -c "
w={
    'f2p_ndps':${WEIGHTS[f2p_ndps]},
    'f2p_seqlen':${WEIGHTS[f2p_seqlen]},
    'f2p_no_tp_field':${WEIGHTS[f2p_no_tp_field]},
    'f2p_sft_no_tp':${WEIGHTS[f2p_sft_no_tp]},
    'f2p_rl_no_tp':${WEIGHTS[f2p_rl_no_tp]},
    'p2p_core_fields':${WEIGHTS[p2p_core_fields]},
    'p2p_retained_props':${WEIGHTS[p2p_retained_props]},
    'p2p_get_parallel':${WEIGHTS[p2p_get_parallel]},
    'config_no_tryexcept':${WEIGHTS[config_no_tryexcept]},
    'antistub_pdims':${WEIGHTS[antistub_pdims]},
    'antistub_trainer':${WEIGHTS[antistub_trainer]},
}
r={
    'f2p_ndps':${RESULTS[f2p_ndps]},
    'f2p_seqlen':${RESULTS[f2p_seqlen]},
    'f2p_no_tp_field':${RESULTS[f2p_no_tp_field]},
    'f2p_sft_no_tp':${RESULTS[f2p_sft_no_tp]},
    'f2p_rl_no_tp':${RESULTS[f2p_rl_no_tp]},
    'p2p_core_fields':${RESULTS[p2p_core_fields]},
    'p2p_retained_props':${RESULTS[p2p_retained_props]},
    'p2p_get_parallel':${RESULTS[p2p_get_parallel]},
    'config_no_tryexcept':${RESULTS[config_no_tryexcept]},
    'antistub_pdims':${RESULTS[antistub_pdims]},
    'antistub_trainer':${RESULTS[antistub_trainer]},
}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
