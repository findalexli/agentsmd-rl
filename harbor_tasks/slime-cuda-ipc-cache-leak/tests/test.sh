#!/usr/bin/env bash
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_del_hf_tensors]=0.25
WEIGHTS[behavioral_ipc_collect_loop]=0.25
WEIGHTS[behavioral_ipc_collect_barrier]=0.15
WEIGHTS[structural_no_todo]=0.10
WEIGHTS[antistub]=0.15
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral_del_hf_tensors behavioral_ipc_collect_loop behavioral_ipc_collect_barrier structural_no_todo antistub config_no_wildcard config_no_bare_print; do
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

# ---------- PRIMARY 1 (30%): Behavioral - hf_named_tensors deleted in loop ----------
python3 << 'PYEOF'
import sys, ast

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the update_weights method
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weights":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: update_weights function not found")
    sys.exit(1)

# Check that del statement includes hf_named_tensors
func_source = ast.get_source_segment(source, func_node)
if func_source is None:
    lines = source.splitlines()
    func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Look for del statement that includes hf_named_tensors
found_del_hf = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Delete):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "hf_named_tensors":
                found_del_hf = True
            elif isinstance(target, ast.Tuple):
                for elt in target.elts:
                    if isinstance(elt, ast.Name) and elt.id == "hf_named_tensors":
                        found_del_hf = True

if found_del_hf:
    print("BEHAVIORAL PASS: hf_named_tensors is deleted in update_weights")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: hf_named_tensors not found in any del statement")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_del_hf_tensors]=1
    echo "TEST behavioral_del_hf_tensors: PASS"
else
    echo "TEST behavioral_del_hf_tensors: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - torch.cuda.ipc_collect() called in loop ----------
python3 << 'PYEOF'
import sys, re

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    content = f.read()

# Find the for loop body and check for ipc_collect
# The loop is: for hf_named_tensors in self._hf_weight_iterator...
loop_match = re.search(
    r'for\s+hf_named_tensors\s+in.*?(?=\n\s{8}dist\.barrier|\n\s{8}#.*barrier|\nclass\s)',
    content, re.DOTALL
)

if loop_match:
    loop_body = loop_match.group(0)
    if "ipc_collect" in loop_body:
        print("BEHAVIORAL PASS: torch.cuda.ipc_collect() called inside the weight chunk loop")
        sys.exit(0)
    else:
        print("BEHAVIORAL FAIL: ipc_collect not found in the weight chunk loop")
        sys.exit(1)
else:
    # Fallback: just check that ipc_collect appears in the file at least once
    count = content.count("ipc_collect")
    if count >= 1:
        print(f"BEHAVIORAL PASS: ipc_collect found {count} time(s) in file")
        sys.exit(0)
    else:
        print("BEHAVIORAL FAIL: ipc_collect not found anywhere in file")
        sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_ipc_collect_loop]=1
    echo "TEST behavioral_ipc_collect_loop: PASS"
else
    echo "TEST behavioral_ipc_collect_loop: FAIL"
fi

# ---------- PRIMARY 3 (15%): Behavioral - ipc_collect after barrier ----------
python3 << 'PYEOF'
import sys, re

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    content = f.read()

# Check that ipc_collect appears after the dist.barrier() call
# The barrier is: dist.barrier(group=get_gloo_group())
barrier_pos = content.find("dist.barrier(group=get_gloo_group())")
if barrier_pos == -1:
    barrier_pos = content.find("dist.barrier(")

if barrier_pos == -1:
    print("BEHAVIORAL FAIL: dist.barrier() not found")
    sys.exit(1)

after_barrier = content[barrier_pos:]
# Check for ipc_collect after barrier but before the next function def or class
next_section = re.search(r'\n\s{4}def\s|\nclass\s', after_barrier)
if next_section:
    section = after_barrier[:next_section.start()]
else:
    section = after_barrier

if "ipc_collect" in section:
    print("BEHAVIORAL PASS: torch.cuda.ipc_collect() called after dist.barrier()")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: ipc_collect not found after dist.barrier()")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_ipc_collect_barrier]=1
    echo "TEST behavioral_ipc_collect_barrier: PASS"
else
    echo "TEST behavioral_ipc_collect_barrier: FAIL"
fi

# ---------- SUPPLEMENTARY (10%): Structural - TODO comment removed ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    content = f.read()

# The original had "# TODO improve" near _send_to_colocated_engine
if "# TODO improve" in content:
    print("STRUCTURAL FAIL: '# TODO improve' comment still present")
    sys.exit(1)
else:
    print("STRUCTURAL PASS: '# TODO improve' comment removed")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_no_todo]=1
    echo "TEST structural_no_todo: PASS"
else
    echo "TEST structural_no_todo: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("def update_weights" in source, "update_weights method present"),
    ("ray.get" in source, "ray.get call present"),
    ("dist.barrier" in source, "dist.barrier call present"),
    ("long_lived_tensors" in source, "long_lived_tensors reference present"),
    (len(source.splitlines()) > 50, "file has substantial content"),
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
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 08b201bd576e02fba08dae22e5c9324643e88884
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 08b201bd576e02fba08dae22e5c9324643e88884
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_del_hf_tensors': ${WEIGHTS[behavioral_del_hf_tensors]}, 'behavioral_ipc_collect_loop': ${WEIGHTS[behavioral_ipc_collect_loop]}, 'behavioral_ipc_collect_barrier': ${WEIGHTS[behavioral_ipc_collect_barrier]}, 'structural_no_todo': ${WEIGHTS[structural_no_todo]}, 'antistub': ${WEIGHTS[antistub]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
results = {'behavioral_del_hf_tensors': ${RESULTS[behavioral_del_hf_tensors]}, 'behavioral_ipc_collect_loop': ${RESULTS[behavioral_ipc_collect_loop]}, 'behavioral_ipc_collect_barrier': ${RESULTS[behavioral_ipc_collect_barrier]}, 'structural_no_todo': ${RESULTS[structural_no_todo]}, 'antistub': ${RESULTS[antistub]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_del_hf_tensors    (${WEIGHTS[behavioral_del_hf_tensors]}): ${RESULTS[behavioral_del_hf_tensors]}"
echo "  behavioral_ipc_collect_loop  (${WEIGHTS[behavioral_ipc_collect_loop]}): ${RESULTS[behavioral_ipc_collect_loop]}"
echo "  behavioral_ipc_collect_barrier (${WEIGHTS[behavioral_ipc_collect_barrier]}): ${RESULTS[behavioral_ipc_collect_barrier]}"
echo "  structural_no_todo           (${WEIGHTS[structural_no_todo]}): ${RESULTS[structural_no_todo]}"
echo "  antistub                     (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_no_wildcard           (${WEIGHTS[config_no_wildcard]}): ${RESULTS[config_no_wildcard]}"
echo "  config_no_bare_print         (${WEIGHTS[config_no_bare_print]}): ${RESULTS[config_no_bare_print]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
