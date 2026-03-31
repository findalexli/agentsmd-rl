#!/usr/bin/env bash
set +e

TOTAL=0.0
FILE="areal/utils/dataloader.py"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "PASS: syntax OK"
else
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# --- Helper: exec the dataloader module with mocked imports ---
EXEC_SETUP='
import sys, ast, types
from torch.utils.data import DistributedSampler
from torchdata.stateful_dataloader import StatefulDataLoader

source = open("'"$FILE"'").read()

class _DatasetConfig:
    batch_size = 4
    shuffle = False
    drop_last = True
    num_workers = 0

class ValidDatasetConfig(_DatasetConfig):
    drop_last = False

exec_globals = {
    "__builtins__": __builtins__,
    "DistributedSampler": DistributedSampler,
    "StatefulDataLoader": StatefulDataLoader,
    "Dataset": object,
    "_DatasetConfig": _DatasetConfig,
    "ValidDatasetConfig": ValidDatasetConfig,
    "Callable": type(lambda: None),
}

modified_source = source
for imp in [
    "from areal.api.cli_args import ValidDatasetConfig, _DatasetConfig",
    "from areal.api.cli_args import _DatasetConfig",
    "from torch.utils.data import DistributedSampler",
    "from torchdata.stateful_dataloader import StatefulDataLoader",
    "from datasets import Dataset",
]:
    modified_source = modified_source.replace(imp, "")

exec(compile(modified_source, "<dataloader>", "exec"), exec_globals)
'

echo ""
echo "=== Behavioral: EvalDistributedSampler does not pad dataset ==="
# [pr_diff] (0.30): Custom sampler must not pad — every sample evaluated exactly once
if python3 -c "
$EXEC_SETUP
EvalDistributedSampler = exec_globals['EvalDistributedSampler']

# Test: dataset_size=10, num_replicas=3 — should cover all 10 indices exactly once
dataset = list(range(10))
all_indices = []
for rank in range(3):
    sampler = EvalDistributedSampler(dataset, num_replicas=3, rank=rank, shuffle=False, drop_last=False)
    indices = list(sampler)
    all_indices.extend(indices)

if sorted(all_indices) != list(range(10)):
    print(f'FAIL: expected indices 0-9, got {sorted(all_indices)}')
    sys.exit(1)

# Test: dataset_size=7, num_replicas=4 — should cover all 7 indices exactly once
dataset = list(range(7))
all_indices = []
for rank in range(4):
    sampler = EvalDistributedSampler(dataset, num_replicas=4, rank=rank, shuffle=False, drop_last=False)
    indices = list(sampler)
    all_indices.extend(indices)

if sorted(all_indices) != list(range(7)):
    print(f'FAIL: expected indices 0-6, got {sorted(all_indices)}')
    sys.exit(1)

# Verify standard DistributedSampler DOES pad (test baseline sanity)
from torch.utils.data import DistributedSampler as StdSampler
dataset = list(range(10))
std_all = []
for rank in range(3):
    s = StdSampler(dataset, num_replicas=3, rank=rank, shuffle=False, drop_last=False)
    std_all.extend(list(s))
if len(std_all) == 10:
    print('FAIL: standard sampler should pad, test baseline broken')
    sys.exit(1)

print('EvalDistributedSampler produces exact indices without padding')
"; then
    echo "PASS: no padding in EvalDistributedSampler"
    add_score 0.30
else
    echo "FAIL: EvalDistributedSampler pads or is missing"
fi

echo ""
echo "=== Behavioral: create_dataloader dispatches EvalDistributedSampler for validation ==="
# [pr_diff] (0.20): create_dataloader must use EvalDistributedSampler when given ValidDatasetConfig
if python3 -c "
$EXEC_SETUP
create_dataloader = exec_globals['create_dataloader']

# Test with ValidDatasetConfig — should use EvalDistributedSampler
dataset = list(range(12))
valid_config = ValidDatasetConfig()
valid_config.batch_size = 4
loader = create_dataloader(dataset, rank=0, world_size=2, dataset_config=valid_config)
sampler = loader.sampler
sampler_name = type(sampler).__name__

if sampler_name != 'EvalDistributedSampler':
    print(f'FAIL: expected EvalDistributedSampler, got {sampler_name}')
    sys.exit(1)

if sampler.drop_last:
    print('FAIL: sampler drop_last should be False for validation')
    sys.exit(1)

print('create_dataloader uses EvalDistributedSampler for validation configs')
"; then
    echo "PASS: correct sampler dispatch for validation"
    add_score 0.20
else
    echo "FAIL: create_dataloader does not dispatch EvalDistributedSampler for validation"
fi

echo ""
echo "=== Behavioral: Edge case — dataset smaller than num_replicas ==="
# [pr_diff] (0.10): Sampler handles dataset_size < num_replicas without padding or crash
if python3 -c "
$EXEC_SETUP
EvalDistributedSampler = exec_globals['EvalDistributedSampler']

# dataset_size=2, num_replicas=4 — should cover exactly [0,1], some ranks get 0 samples
dataset = list(range(2))
all_indices = []
for rank in range(4):
    sampler = EvalDistributedSampler(dataset, num_replicas=4, rank=rank, shuffle=False, drop_last=False)
    indices = list(sampler)
    all_indices.extend(indices)

if sorted(all_indices) != list(range(2)):
    print(f'FAIL: expected indices [0, 1], got {sorted(all_indices)}')
    sys.exit(1)

# Exact division: dataset_size=6, num_replicas=3 — 2 each, total 6
dataset = list(range(6))
all_indices = []
for rank in range(3):
    sampler = EvalDistributedSampler(dataset, num_replicas=3, rank=rank, shuffle=False, drop_last=False)
    indices = list(sampler)
    all_indices.extend(indices)

if sorted(all_indices) != list(range(6)):
    print(f'FAIL: expected indices 0-5, got {sorted(all_indices)}')
    sys.exit(1)

print('Edge cases handled correctly')
"; then
    echo "PASS: edge cases work"
    add_score 0.10
else
    echo "FAIL: edge case handling broken"
fi

echo ""
echo "=== Pass-to-pass: Training config still uses DistributedSampler ==="
# [pr_diff] (0.10): create_dataloader must still use standard DistributedSampler for non-validation configs
if python3 -c "
$EXEC_SETUP
create_dataloader = exec_globals['create_dataloader']

# Test with base _DatasetConfig (training) — should use standard DistributedSampler
dataset = list(range(12))
train_config = _DatasetConfig()
train_config.batch_size = 4
loader = create_dataloader(dataset, rank=0, world_size=2, dataset_config=train_config)
sampler = loader.sampler
sampler_name = type(sampler).__name__

if sampler_name != 'DistributedSampler':
    print(f'FAIL: expected DistributedSampler for training, got {sampler_name}')
    sys.exit(1)

if not sampler.drop_last:
    print('FAIL: sampler drop_last should be True for training')
    sys.exit(1)

print('Training config still uses standard DistributedSampler with drop_last=True')
"; then
    echo "PASS: training config unchanged"
    add_score 0.10
else
    echo "FAIL: training config behavior changed"
fi

echo ""
echo "=== Behavioral: No duplicate indices across ranks ==="
# [pr_diff] (0.05): Each sample evaluated exactly once — no duplicates
if python3 -c "
$EXEC_SETUP
EvalDistributedSampler = exec_globals['EvalDistributedSampler']

# Test with several sizes: no duplicates allowed
for ds_size, nrep in [(10, 3), (7, 4), (13, 5), (100, 7)]:
    dataset = list(range(ds_size))
    all_indices = []
    for rank in range(nrep):
        sampler = EvalDistributedSampler(dataset, num_replicas=nrep, rank=rank, shuffle=False, drop_last=False)
        all_indices.extend(list(sampler))
    if len(all_indices) != len(set(all_indices)):
        dups = [x for x in all_indices if all_indices.count(x) > 1]
        print(f'FAIL: duplicate indices found for ds_size={ds_size}, nrep={nrep}: {set(dups)}')
        sys.exit(1)
    if len(all_indices) != ds_size:
        print(f'FAIL: wrong count for ds_size={ds_size}: got {len(all_indices)}')
        sys.exit(1)

print('No duplicate indices across all test cases')
"; then
    echo "PASS: no duplicates"
    add_score 0.05
else
    echo "FAIL: duplicate indices found"
fi

echo ""
echo "=== Structural: No wildcard imports ==="
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30 @ fdca82d
if ! grep -q 'from .* import \*' "$FILE"; then
    echo "PASS: no wildcard imports"
    add_score 0.05
else
    echo "FAIL: wildcard import found"
fi

echo ""
echo "=== Structural: Anti-stub check ==="
# [pr_diff] (0.05): EvalDistributedSampler must not be stubbed — needs __init__ and __iter__
if python3 -c "
import ast, sys

source = open('$FILE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'EvalDistributedSampler':
        methods = {n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)}

        # Must have __init__
        if '__init__' not in methods:
            print('EvalDistributedSampler has no __init__')
            sys.exit(1)

        # Check __init__ is not trivial
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                real_body = [s for s in item.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
                    and not isinstance(s, ast.Pass)]
                if len(real_body) < 2:
                    print(f'__init__ too short ({len(real_body)} real stmts)')
                    sys.exit(1)

        print('EvalDistributedSampler not stubbed')
        sys.exit(0)

print('EvalDistributedSampler not found')
sys.exit(1)
"; then
    echo "PASS: methods not stubbed"
    add_score 0.05
else
    echo "FAIL: methods appear to be stubbed"
fi

echo ""
echo "=== Total score: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
reward = $TOTAL
behavioral = min(0.65, round(min(reward, 0.65), 4))
regression = min(0.10, round(max(0, min(reward - 0.65, 0.10)), 4))
config = min(0.05, round(max(0, min(reward - 0.75, 0.05)), 4))
structural = round(max(0, reward - behavioral - regression - config), 4)
data = {
    'reward': reward,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'structural': structural,
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
