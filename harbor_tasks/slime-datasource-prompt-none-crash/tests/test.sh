#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/slime
LOG_DIR=/logs/verifier
mkdir -p "$LOG_DIR"
SCORE=0

# === GATE (0): Syntax check — abort on failure ===
echo "=== GATE: Syntax check ==="
if ! python3 -c "
import py_compile
py_compile.compile('$REPO/slime/rollout/data_source.py', doraise=True)
py_compile.compile('$REPO/slime/ray/rollout.py', doraise=True)
print('PASS: syntax OK')
"; then
    echo "FAIL: syntax error — aborting"
    echo "0.00" > "$LOG_DIR/reward.txt"
    exit 0
fi

# After gate, allow individual tests to fail without killing script
set +e

# Helper: exec data_source.py classes in a mock environment.
# Mocks torch and slime internal imports so we can call the actual Python methods.
MOCK_SETUP=$(cat <<'PYSETUP'
import abc, copy, logging, os, sys, tempfile
from pathlib import Path
from unittest.mock import MagicMock
from types import SimpleNamespace

# --- Mock heavy deps ---
class _FailOnNoneDataset:
    """Simulates real Dataset: crashes if path is None."""
    def __init__(self, path, **kwargs):
        if path is None:
            raise ValueError("prompt_data is None — Dataset cannot load from None")
        self.samples = [MagicMock() for _ in range(3)]
    def __len__(self):
        return len(self.samples)
    def shuffle(self, epoch):
        pass

_torch_mock = SimpleNamespace(
    load=lambda path, **kw: {},
    save=lambda obj, path: None,
)

Dataset = _FailOnNoneDataset
load_function = MagicMock()
load_processor = MagicMock(return_value=None)
load_tokenizer = MagicMock(return_value=MagicMock())
Sample = MagicMock()
torch = _torch_mock
logger = logging.getLogger('test')

# --- Read and exec just the class definitions ---
with open('/workspace/slime/slime/rollout/data_source.py') as _f:
    _source = _f.read()
_idx = _source.find('class DataSource')
_body = _source[_idx:]
exec(_body)
# Now RolloutDataSource is available in this namespace
PYSETUP
)

# [pr_diff] (0.30): __len__ returns 0 when dataset is None, correct count otherwise
echo ""
echo "=== Test 1: __len__ returns 0 when dataset=None, correct count otherwise ==="
T1=$(python3 -c "
$MOCK_SETUP

# Part A: dataset is None → must return 0
ds = object.__new__(RolloutDataSource)
ds.dataset = None
try:
    result = len(ds)
    if result != 0:
        print(f'FAIL: expected 0 for None dataset, got {result}')
        raise SystemExit(0)
except (TypeError, AttributeError) as e:
    print(f'FAIL: crashed on None dataset: {e}')
    raise SystemExit(0)

# Part B: dataset exists → must return actual length (anti-stub)
ds2 = object.__new__(RolloutDataSource)
ds2.dataset = _FailOnNoneDataset('/fake/path.jsonl')
try:
    result2 = len(ds2)
    if result2 == 3:
        print('PASS')
    else:
        print(f'FAIL: expected 3 for real dataset, got {result2}')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1 | tail -1)
echo "$T1"
if [ "$T1" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.30)"); fi

# [pr_diff] (0.25): Constructor handles prompt_data=None without crashing
echo ""
echo "=== Test 2: Constructor skips Dataset when prompt_data=None ==="
T2=$(python3 -c "
$MOCK_SETUP

args = SimpleNamespace(
    rollout_global_dataset=True,
    prompt_data=None,
    hf_checkpoint='test',
    dump_details=None,
    rollout_max_prompt_len=100,
    input_key='prompt',
    multimodal_keys=None,
    label_key='answer',
    metadata_key=None,
    tool_key=None,
    apply_chat_template=False,
    apply_chat_template_kwargs=None,
    rollout_seed=42,
    rollout_shuffle=False,
)
try:
    ds = RolloutDataSource(args)
    if ds.dataset is None:
        print('PASS')
    else:
        print('FAIL: dataset should be None when prompt_data is None')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1 | tail -1)
echo "$T2"
if [ "$T2" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi

# [pr_diff] (0.20): load() doesn't crash when dataset=None and shuffle=True
echo ""
echo "=== Test 3: load() handles dataset=None with shuffle=True ==="
T3=$(python3 -c "
$MOCK_SETUP

# Create a temp checkpoint file so load() reaches the shuffle line
tmpdir = tempfile.mkdtemp()
os.makedirs(os.path.join(tmpdir, 'rollout'), exist_ok=True)
cp_path = os.path.join(tmpdir, 'rollout', 'global_dataset_state_dict_0.pt')
with open(cp_path, 'w') as f:
    f.write('fake')

ds = object.__new__(RolloutDataSource)
ds.dataset = None
ds.args = SimpleNamespace(
    rollout_global_dataset=True,
    rollout_shuffle=True,
    load=tmpdir,
)
ds.epoch_id = 0
ds.sample_offset = 0
ds.sample_group_index = 0
ds.sample_index = 0
ds.metadata = {}

try:
    ds.load(rollout_id=0)
    print('PASS')
except (AttributeError, TypeError) as e:
    print(f'FAIL: {e}')
except Exception as e:
    print(f'FAIL: unexpected error: {e}')
" 2>&1 | tail -1)
echo "$T3"
if [ "$T3" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

# [pr_diff] (0.10): Router disables health check — exec the function and inspect args
echo ""
echo "=== Test 4: Router sets disable_health_check ==="
T4=$(python3 -c "
import ast, sys

with open('$REPO/slime/ray/rollout.py') as f:
    source = f.read()

tree = ast.parse(source)

# Find the _start_router function
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_start_router':
        # Walk the function body looking for an assignment to disable_health_check = True
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute) and target.attr == 'disable_health_check':
                        if isinstance(child.value, ast.Constant) and child.value.value is True:
                            found = True
            elif isinstance(child, ast.AugAssign):
                pass  # not relevant
        break

if found:
    print('PASS')
else:
    print('FAIL: disable_health_check = True not found in _start_router function')
" 2>&1 | tail -1)
echo "$T4"
if [ "$T4" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

# [pr_diff] (0.10): P2P — get_samples returns empty Sample objects when dataset=None
echo ""
echo "=== Test 5: P2P — get_samples works when dataset is None ==="
T5=$(python3 -c "
$MOCK_SETUP

args = SimpleNamespace(
    rollout_global_dataset=True,
    prompt_data=None,
    hf_checkpoint='test',
    dump_details=None,
    rollout_max_prompt_len=100,
    input_key='prompt',
    multimodal_keys=None,
    label_key='answer',
    metadata_key=None,
    tool_key=None,
    apply_chat_template=False,
    apply_chat_template_kwargs=None,
    rollout_seed=42,
    rollout_shuffle=False,
    n_samples_per_prompt=1,
)
try:
    ds = RolloutDataSource(args)
    samples = ds.get_samples(2)
    if len(samples) == 2 and all(len(g) == 1 for g in samples):
        print('PASS')
    else:
        print(f'FAIL: unexpected samples structure: {len(samples)} groups')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1 | tail -1)
echo "$T5"
if [ "$T5" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

# [pr_diff] (0.05): P2P — Constructor with prompt_data set still creates dataset
echo ""
echo "=== Test 6: P2P — Constructor with prompt_data creates dataset ==="
T6=$(python3 -c "
$MOCK_SETUP

args = SimpleNamespace(
    rollout_global_dataset=True,
    prompt_data='/fake/path.jsonl',
    hf_checkpoint='test',
    dump_details=None,
    rollout_max_prompt_len=100,
    input_key='prompt',
    multimodal_keys=None,
    label_key='answer',
    metadata_key=None,
    tool_key=None,
    apply_chat_template=False,
    apply_chat_template_kwargs=None,
    rollout_seed=42,
    rollout_shuffle=False,
)
try:
    ds = RolloutDataSource(args)
    if ds.dataset is not None and len(ds) == 3:
        print('PASS')
    else:
        print(f'FAIL: expected dataset with 3 items, got dataset={ds.dataset}, len={len(ds) if ds.dataset else "N/A"}')
except Exception as e:
    print(f'FAIL: {e}')
" 2>&1 | tail -1)
echo "$T6"
if [ "$T6" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# --- Final score ---
echo ""
echo "=== Final Score ==="
# Round to 2 decimal places
SCORE=$(python3 -c "print(f'{min(1.0, $SCORE):.2f}')")
echo "Deterministic score: $SCORE"
echo "$SCORE" > "$LOG_DIR/reward.txt"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
