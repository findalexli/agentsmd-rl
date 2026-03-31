#!/usr/bin/env bash
set +e

TOTAL=0
BEHAVIORAL_PASSED=0
FILE="areal/api/cli_args.py"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

mkdir -p /logs/verifier

echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: syntax OK"

echo ""
echo "=== Behavioral: OmegaConf.structured(SchedulingSpec()) works ==="
# [pr_diff] (0.30): Core bug — omegaconf must accept SchedulingSpec without ValidationError
if python3 -c "
import sys, ast

source = open('$FILE').read()
exec_globals = {'__builtins__': __builtins__}
exec('''
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar
import sys
''', exec_globals)

tree = ast.parse(source)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SchedulingSpec':
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        class_src = '\n'.join(source.splitlines()[start:end])
        exec(class_src, exec_globals)
        break

SchedulingSpec = exec_globals.get('SchedulingSpec')
if SchedulingSpec is None:
    print('SchedulingSpec class not found')
    sys.exit(1)

from omegaconf import OmegaConf
try:
    cfg = OmegaConf.structured(SchedulingSpec())
    print(f'OmegaConf.structured succeeded: ray_placement_strategy={cfg.ray_placement_strategy}')
except Exception as e:
    print(f'OmegaConf.structured FAILED: {e}')
    sys.exit(1)
"; then
    echo "PASS: OmegaConf.structured(SchedulingSpec()) works"
    add_score 0.30
    BEHAVIORAL_PASSED=1
else
    echo "FAIL: OmegaConf.structured(SchedulingSpec()) raises error"
fi

echo ""
echo "=== Behavioral: Invalid strategy value is rejected ==="
# [pr_diff] (0.25): Invalid ray_placement_strategy must raise an error (runtime validation)
if python3 -c "
import ast, sys

source = open('$FILE').read()
exec_globals = {'__builtins__': __builtins__}
exec('from dataclasses import dataclass, field; from typing import TYPE_CHECKING, Any, ClassVar', exec_globals)

tree = ast.parse(source)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SchedulingSpec':
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        class_src = '\n'.join(source.splitlines()[start:end])
        exec(class_src, exec_globals)
        break

S = exec_globals.get('SchedulingSpec')
if S is None:
    sys.exit(1)

# Must reject multiple invalid strategies (not just one hardcoded value)
invalid_values = ['invalid_value', 'SHARED', 'spread', '', 'none']
rejected = 0
for val in invalid_values:
    try:
        S(ray_placement_strategy=val)
        print(f'No error raised for invalid strategy: {val!r}')
    except Exception as e:
        rejected += 1

if rejected == len(invalid_values):
    print(f'All {rejected} invalid strategies correctly rejected')
    sys.exit(0)
else:
    print(f'Only {rejected}/{len(invalid_values)} invalid strategies rejected')
    sys.exit(1)
"; then
    echo "PASS: invalid strategies rejected"
    add_score 0.25
else
    echo "FAIL: invalid strategies not rejected"
fi

echo ""
echo "=== Behavioral: SchedulingSpec default instantiation works ==="
# [pr_diff] (0.10): SchedulingSpec() default must work with correct value
if python3 -c "
import ast, sys

source = open('$FILE').read()
exec_globals = {'__builtins__': __builtins__}
exec('from dataclasses import dataclass, field; from typing import TYPE_CHECKING, Any, ClassVar', exec_globals)

tree = ast.parse(source)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SchedulingSpec':
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        class_src = '\n'.join(source.splitlines()[start:end])
        exec(class_src, exec_globals)
        break

S = exec_globals.get('SchedulingSpec')
if S is None:
    sys.exit(1)

s = S()
assert s.ray_placement_strategy == 'shared', f'Expected shared, got {s.ray_placement_strategy}'
print('Default instantiation OK, ray_placement_strategy=shared')
"; then
    echo "PASS: default instantiation works"
    add_score 0.10
else
    echo "FAIL: default instantiation broken"
fi

echo ""
echo "=== Behavioral: All valid strategies accepted ==="
# [pr_diff] (0.10): All three valid strategies (shared, separate, deferred) must be accepted
if python3 -c "
import ast, sys

source = open('$FILE').read()
exec_globals = {'__builtins__': __builtins__}
exec('from dataclasses import dataclass, field; from typing import TYPE_CHECKING, Any, ClassVar', exec_globals)

tree = ast.parse(source)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SchedulingSpec':
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        class_src = '\n'.join(source.splitlines()[start:end])
        exec(class_src, exec_globals)
        break

S = exec_globals.get('SchedulingSpec')
if S is None:
    sys.exit(1)

for strategy in ['shared', 'separate', 'deferred']:
    try:
        s = S(ray_placement_strategy=strategy)
        assert s.ray_placement_strategy == strategy
    except Exception as e:
        print(f'Strategy {strategy!r} rejected: {e}')
        sys.exit(1)
print('All valid strategies accepted')
"; then
    echo "PASS: all valid strategies accepted"
    add_score 0.10
else
    echo "FAIL: valid strategy rejected"
fi

echo ""
echo "=== Behavioral: OmegaConf roundtrip preserves strategy ==="
# [pr_diff] (0.05): OmegaConf structured → to_yaml → from_yaml roundtrip works
if python3 -c "
import ast, sys

source = open('$FILE').read()
exec_globals = {'__builtins__': __builtins__}
exec('from dataclasses import dataclass, field; from typing import TYPE_CHECKING, Any, ClassVar', exec_globals)

tree = ast.parse(source)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SchedulingSpec':
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        class_src = '\n'.join(source.splitlines()[start:end])
        exec(class_src, exec_globals)
        break

S = exec_globals.get('SchedulingSpec')
if S is None:
    sys.exit(1)

from omegaconf import OmegaConf

for strategy in ['shared', 'separate', 'deferred']:
    cfg = OmegaConf.structured(S(ray_placement_strategy=strategy))
    yaml_str = OmegaConf.to_yaml(cfg)
    reloaded = OmegaConf.create(yaml_str)
    val = reloaded.ray_placement_strategy
    assert val == strategy, f'Roundtrip failed: {strategy} -> {val}'
print('OmegaConf roundtrip OK for all strategies')
"; then
    echo "PASS: OmegaConf roundtrip works"
    add_score 0.05
else
    echo "FAIL: OmegaConf roundtrip broken"
fi

echo ""
echo "=== Pass-to-pass: Other dataclass fields intact ==="
# [pr_diff] (0.10): SchedulingSpec must still have core fields
if python3 -c "
import ast, sys

source = open('$FILE').read()
tree = ast.parse(source)

required_fields = {'cpu', 'gpu', 'mem', 'task_type', 'exclude', 'nodelist', 'ray_placement_strategy'}

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SchedulingSpec':
        found = set()
        for item in ast.walk(node):
            if isinstance(item, ast.AnnAssign) and hasattr(item.target, 'id'):
                found.add(item.target.id)
        missing = required_fields - found
        if missing:
            print(f'Missing fields: {missing}')
            sys.exit(1)
        print(f'All required fields present: {required_fields}')
        sys.exit(0)
print('SchedulingSpec not found')
sys.exit(1)
"; then
    echo "PASS: core fields intact"
    add_score 0.10
else
    echo "FAIL: core fields missing"
fi

# === Gated structural/config checks (only if behavioral passed) ===
if [ "$BEHAVIORAL_PASSED" -eq 1 ]; then

    echo ""
    echo "=== Config-derived: No wildcard imports ==="
    # [agent_config] (0.05): "No wildcard imports" — AGENTS.md:25 @ 6860e70
    if ! grep -q 'from .* import \*' "$FILE"; then
        echo "PASS: no wildcard imports"
        add_score 0.05
    else
        echo "FAIL: wildcard import found"
    fi

    echo ""
    echo "=== Config-derived: Unused Literal import removed ==="
    # [agent_config] (0.05): Clean imports — if Literal is no longer used, it should be removed
    if python3 -c "
import ast, sys

source = open('$FILE').read()
tree = ast.parse(source)

literal_imported = False
literal_used = False

for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module == 'typing':
        for alias in node.names:
            if alias.name == 'Literal':
                literal_imported = True
    if isinstance(node, ast.Subscript):
        if isinstance(node.value, ast.Name) and node.value.id == 'Literal':
            literal_used = True

if literal_imported and not literal_used:
    print('Literal is imported but unused')
    sys.exit(1)
print('Imports are clean')
"; then
        echo "PASS: no unused Literal import"
        add_score 0.05
    else
        echo "FAIL: unused Literal import remains"
    fi

else
    echo ""
    echo "=== SKIPPED: Config/structural checks gated behind behavioral pass ==="
fi

echo ""
echo "=== Total score: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
reward = $TOTAL
data = {
    'reward': reward,
    'behavioral': min(reward, 0.80),
    'regression': min(max(0, reward - 0.80), 0.10),
    'config': min(max(0, reward - 0.90), 0.10),
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
