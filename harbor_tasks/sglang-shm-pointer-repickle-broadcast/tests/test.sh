#!/usr/bin/env bash
set +e

MM_UTILS="/workspace/sglang/python/sglang/srt/managers/mm_utils.py"
SCHEDULER="/workspace/sglang/python/sglang/srt/managers/scheduler.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# ── GATE (0.00) ──────────────────────────────────────────────────────
WEIGHTS[gate_syntax]=0.00

# ── Behavioral fail-to-pass (0.70 total) ─────────────────────────────
WEIGHTS[repickle_stable_shm_name]=0.20
WEIGHTS[repickle_no_new_shm]=0.15
WEIGHTS[materialize_correct_data]=0.15
WEIGHTS[materialize_cleans_shm]=0.10
WEIGHTS[batch_unwrap_behavioral]=0.10

# ── Structural / scheduler (0.15 total) ──────────────────────────────
WEIGHTS[unwrap_after_broadcast]=0.10
WEIGHTS[unwrap_not_in_recv_loop]=0.05

# ── Pass-to-pass (0.15 total) ────────────────────────────────────────
WEIGHTS[p2p_single_pickle_roundtrip]=0.10
WEIGHTS[p2p_wrap_unwrap_identity]=0.05

for key in gate_syntax repickle_stable_shm_name repickle_no_new_shm materialize_correct_data materialize_cleans_shm batch_unwrap_behavioral unwrap_after_broadcast unwrap_not_in_recv_loop p2p_single_pickle_roundtrip p2p_wrap_unwrap_identity; do
    RESULTS[$key]=0
done

# Helper: module-stub boilerplate shared by all behavioral tests
STUB_BOILERPLATE='
import sys, types
sys.path.insert(0, "/workspace/sglang/python")
srt = types.ModuleType("sglang.srt")
srt.server_args = types.ModuleType("sglang.srt.server_args")
class FakeArgs:
    skip_tokenizer_init = True
srt.server_args._global_server_args = FakeArgs()
sys.modules["sglang.srt"] = srt
sys.modules["sglang.srt.server_args"] = srt.server_args
import sglang.srt.managers.mm_utils as mm_utils
mm_utils.get_global_server_args = lambda: FakeArgs()
from sglang.srt.managers.mm_utils import ShmPointerMMData
'

# ══════════════════════════════════════════════════════════════════════
# GATE: syntax check on changed files
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (gate): Both files must parse
python3 -c "
import py_compile, sys
for f in ['$MM_UTILS', '$SCHEDULER']:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'SYNTAX ERROR: {e}')
        sys.exit(1)
print('Syntax OK')
"
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.00" > "$REWARD_FILE"
    exit 0
fi
RESULTS[gate_syntax]=1
echo "PASS: gate_syntax"

# ══════════════════════════════════════════════════════════════════════
# Behavioral F2P: multi-pickle roundtrip preserves same shm_name
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.20): Multiple pickle cycles must reuse the same shm segment
python3 -c "
import pickle, torch
$STUB_BOILERPLATE

t = torch.randn(4, 8)
obj = ShmPointerMMData(t)

# First pickle roundtrip
obj2 = pickle.loads(pickle.dumps(obj))
name1 = getattr(obj2, 'shm_name', None)

# Second pickle roundtrip (simulating broadcast)
obj3 = pickle.loads(pickle.dumps(obj2))
name2 = getattr(obj3, 'shm_name', None)

assert name1 is not None, 'No shm_name after first unpickle'
assert name1 == name2, f'shm_name changed: {name1} -> {name2}'
print('PASS: shm_name stable across pickles:', name1)
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[repickle_stable_shm_name]=1
    echo "PASS: repickle_stable_shm_name"
else
    echo "FAIL: repickle_stable_shm_name"
fi

# ══════════════════════════════════════════════════════════════════════
# Behavioral F2P: re-pickle does NOT create new shared memory segments
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.15): __getstate__ must not allocate new shm on re-pickle
python3 -c "
import pickle, torch
from multiprocessing import shared_memory
$STUB_BOILERPLATE

t = torch.randn(4, 8)
obj = ShmPointerMMData(t)

# First unpickle
obj2 = pickle.loads(pickle.dumps(obj))

# Track shm creations during second pickle
created_shms = []
_orig_init = shared_memory.SharedMemory.__init__
def _tracking_init(self, *args, **kwargs):
    _orig_init(self, *args, **kwargs)
    if kwargs.get('create', False) or (len(args) > 1 and args[1]):
        created_shms.append(self.name)
shared_memory.SharedMemory.__init__ = _tracking_init

try:
    data2 = pickle.dumps(obj2)
finally:
    shared_memory.SharedMemory.__init__ = _orig_init

assert len(created_shms) == 0, f'{len(created_shms)} new shm segment(s) created: {created_shms}'
print('PASS: no new shm created during re-pickle')
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[repickle_no_new_shm]=1
    echo "PASS: repickle_no_new_shm"
else
    echo "FAIL: repickle_no_new_shm"
fi

# ══════════════════════════════════════════════════════════════════════
# Behavioral F2P: tensor data survives multi-pickle + materialization
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.15): After multi-pickle, tensor data must be recoverable
python3 -c "
import pickle, torch
$STUB_BOILERPLATE

t = torch.randn(4, 8)
obj = ShmPointerMMData(t)

# Double pickle roundtrip (simulating ZMQ + broadcast)
obj2 = pickle.loads(pickle.dumps(obj))
obj3 = pickle.loads(pickle.dumps(obj2))

# Get tensor data — try any method the fix might use
result = None
for method_name in ('materialize', 'to_tensor', 'get_tensor', 'resolve'):
    if hasattr(obj3, method_name) and callable(getattr(obj3, method_name)):
        result = getattr(obj3, method_name)()
        break
if result is None and hasattr(obj3, 'tensor'):
    result = obj3.tensor.clone() if hasattr(obj3.tensor, 'clone') else obj3.tensor

assert result is not None, 'Cannot retrieve tensor from double-pickled object'
assert torch.allclose(result, t, atol=1e-6), f'Data mismatch after double pickle'
print('PASS: tensor data correct after double-pickle + retrieval')
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[materialize_correct_data]=1
    echo "PASS: materialize_correct_data"
else
    echo "FAIL: materialize_correct_data"
fi

# ══════════════════════════════════════════════════════════════════════
# Behavioral F2P: materialization releases shm handle
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.10): After getting tensor, shm handle should be released
python3 -c "
import pickle, torch
from multiprocessing import shared_memory
$STUB_BOILERPLATE

t = torch.randn(4, 8)
obj = ShmPointerMMData(t)
obj2 = pickle.loads(pickle.dumps(obj))
shm_name = obj2.shm_name

# Get tensor via whatever method is available
result = None
for method_name in ('materialize', 'to_tensor', 'get_tensor', 'resolve'):
    if hasattr(obj2, method_name) and callable(getattr(obj2, method_name)):
        result = getattr(obj2, method_name)()
        break
if result is None and hasattr(obj2, 'tensor'):
    result = obj2.tensor.clone() if hasattr(obj2.tensor, 'clone') else obj2.tensor
    # Manually close if the fix uses a different cleanup mechanism
    for attr in ('_shm_handle', 'shm', '_shm'):
        handle = getattr(obj2, attr, None)
        if handle is not None:
            try: handle.close()
            except: pass
            try: handle.unlink()
            except: pass

# Verify the shm segment was unlinked (no longer accessible)
import time
time.sleep(0.05)  # Small delay for OS cleanup
try:
    check = shared_memory.SharedMemory(name=shm_name, create=False)
    check.close()
    # Still exists — cleanup didn't unlink it
    print('FAIL: shm segment still accessible after materialization')
    import sys; sys.exit(1)
except FileNotFoundError:
    print('PASS: shm segment cleaned up after materialization')
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[materialize_cleans_shm]=1
    echo "PASS: materialize_cleans_shm"
else
    echo "FAIL: materialize_cleans_shm"
fi

# ══════════════════════════════════════════════════════════════════════
# Behavioral F2P: unwrap_shm_features handles batch requests
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.10): unwrap_shm_features must recurse into batch sub-requests
python3 -c "
import pickle, torch
$STUB_BOILERPLATE

# Override _get_is_default_transport to return False so unwrap actually runs
mm_utils._get_is_default_transport = lambda: False
# Override skip_tokenizer_init to False
class TestArgs:
    skip_tokenizer_init = False
mm_utils.get_global_server_args = lambda: TestArgs()

from sglang.srt.managers.mm_utils import unwrap_shm_features

# Create mock objects that mimic the real request structure
class MockMMItem:
    def __init__(self, tensor):
        self.feature = ShmPointerMMData(tensor)

class MockMMInputs:
    def __init__(self, items):
        self._items = items
    def get(self, key, default=None):
        if key == 'mm_items':
            return self._items
        return default

class MockRequest:
    def __init__(self, tensor):
        self.mm_inputs = MockMMInputs([MockMMItem(tensor)])

class MockBatchRequest:
    def __init__(self, requests):
        self.batch = requests

# Build a batch with 2 sub-requests, each wrapping a tensor in ShmPointerMMData
t1 = torch.randn(2, 4)
t2 = torch.randn(3, 5)
req1 = MockRequest(t1)
req2 = MockRequest(t2)
batch_req = MockBatchRequest([req1, req2])

# Pickle roundtrip to simulate the real path
batch_req2 = pickle.loads(pickle.dumps(batch_req))

# Call unwrap — this should recurse into batch and materialize tensors
unwrap_shm_features(batch_req2)

# Verify: features should now be plain tensors, not ShmPointerMMData
for i, sub_req in enumerate(batch_req2.batch):
    items = sub_req.mm_inputs.get('mm_items', [])
    for j, item in enumerate(items):
        feat = item.feature
        assert isinstance(feat, torch.Tensor), \
            f'batch[{i}].mm_items[{j}].feature is {type(feat).__name__}, expected Tensor'

print('PASS: unwrap_shm_features correctly unwraps batch sub-requests')
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[batch_unwrap_behavioral]=1
    echo "PASS: batch_unwrap_behavioral"
else
    echo "FAIL: batch_unwrap_behavioral"
fi

# ══════════════════════════════════════════════════════════════════════
# Structural: unwrap called after broadcast, near end of recv_requests
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.10): unwrap_shm_features must be called after broadcasts
# WHY AST: scheduler.py requires full server/distributed runtime to import
python3 -c "
import ast, sys

with open('$SCHEDULER') as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'recv_requests':
        # Walk the function body to find call positions by line number
        unwrap_lines = []
        return_lines = []
        for child in ast.walk(node):
            # Find calls to unwrap_shm_features
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name) and func.id == 'unwrap_shm_features':
                    unwrap_lines.append(child.lineno)
                elif isinstance(func, ast.Attribute) and func.attr == 'unwrap_shm_features':
                    unwrap_lines.append(child.lineno)
            # Find return statements
            if isinstance(child, ast.Return):
                return_lines.append(child.lineno)

        assert len(unwrap_lines) > 0, 'No unwrap_shm_features call in recv_requests'
        assert len(return_lines) > 0, 'No return in recv_requests'

        last_unwrap = max(unwrap_lines)
        last_return = max(return_lines)
        # unwrap should be near the end, within 15 lines of a return
        assert last_return >= last_unwrap, \
            f'unwrap at line {last_unwrap} is after last return at {last_return}'
        assert last_return - last_unwrap <= 15, \
            f'unwrap at {last_unwrap} too far from return at {last_return}'
        print(f'PASS: unwrap at line {last_unwrap}, return at {last_return}')
        sys.exit(0)

print('FAIL: recv_requests not found')
sys.exit(1)
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[unwrap_after_broadcast]=1
    echo "PASS: unwrap_after_broadcast"
else
    echo "FAIL: unwrap_after_broadcast"
fi

# ══════════════════════════════════════════════════════════════════════
# Structural: unwrap NOT called inline in the zmq recv loop
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.05): unwrap must not happen inside try/except zmq.ZMQError block
# WHY AST: scheduler.py requires full server runtime to import
python3 -c "
import ast, sys

with open('$SCHEDULER') as f:
    source = f.read()

tree = ast.parse(source)

def find_unwrap_in_try_blocks(node):
    \"\"\"Check if unwrap_shm_features is called inside a try/except that catches ZMQError.\"\"\"
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Try):
            # Check if any handler catches ZMQError
            catches_zmq = False
            for handler in child.handlers:
                if handler.type and hasattr(handler.type, 'attr') and 'ZMQError' in getattr(handler.type, 'attr', ''):
                    catches_zmq = True
                if handler.type and hasattr(handler.type, 'id') and 'ZMQError' in getattr(handler.type, 'id', ''):
                    catches_zmq = True
            if catches_zmq:
                # Check if unwrap_shm_features is called in the try body
                for try_child in ast.walk(child):
                    if isinstance(try_child, ast.Call):
                        func = try_child.func
                        if isinstance(func, ast.Name) and func.id == 'unwrap_shm_features':
                            return True
                        if isinstance(func, ast.Attribute) and func.attr == 'unwrap_shm_features':
                            return True
        result = find_unwrap_in_try_blocks(child)
        if result:
            return True
    return False

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'recv_requests':
        if find_unwrap_in_try_blocks(node):
            print('FAIL: unwrap_shm_features called inside ZMQ recv try-block')
            sys.exit(1)
        print('PASS: unwrap not in ZMQ recv loop')
        sys.exit(0)

print('FAIL: recv_requests not found')
sys.exit(1)
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[unwrap_not_in_recv_loop]=1
    echo "PASS: unwrap_not_in_recv_loop"
else
    echo "FAIL: unwrap_not_in_recv_loop"
fi

# ══════════════════════════════════════════════════════════════════════
# Pass-to-pass: single pickle roundtrip still works
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.10): Basic pickle/unpickle must still produce correct tensor
python3 -c "
import pickle, torch
$STUB_BOILERPLATE

# Test with multiple dtypes and shapes
test_cases = [
    torch.randn(4, 8),                       # float32, 2D
    torch.randint(0, 100, (10,)),             # int64, 1D
    torch.randn(2, 3, 4, dtype=torch.float64), # float64, 3D
]

for i, t in enumerate(test_cases):
    obj = ShmPointerMMData(t)
    obj2 = pickle.loads(pickle.dumps(obj))

    # Get tensor via any available method
    result = None
    for method_name in ('materialize', 'to_tensor', 'get_tensor', 'resolve'):
        if hasattr(obj2, method_name) and callable(getattr(obj2, method_name)):
            result = getattr(obj2, method_name)()
            break
    if result is None and hasattr(obj2, 'tensor'):
        result = obj2.tensor

    assert result is not None, f'Case {i}: cannot get tensor from unpickled object'
    assert result.shape == t.shape, f'Case {i}: shape {result.shape} != {t.shape}'
    assert result.dtype == t.dtype, f'Case {i}: dtype {result.dtype} != {t.dtype}'
    assert torch.allclose(result, t, atol=1e-6), f'Case {i}: data mismatch'

print('PASS: single roundtrip preserves data across dtypes/shapes')
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[p2p_single_pickle_roundtrip]=1
    echo "PASS: p2p_single_pickle_roundtrip"
else
    echo "FAIL: p2p_single_pickle_roundtrip"
fi

# ══════════════════════════════════════════════════════════════════════
# Pass-to-pass: wrap + unwrap is identity on single requests
# ══════════════════════════════════════════════════════════════════════
# [pr_diff] (0.05): wrap_shm_features then unwrap_shm_features = original tensor
python3 -c "
import pickle, torch
$STUB_BOILERPLATE

# Override transport check so wrap/unwrap actually run
mm_utils._get_is_default_transport = lambda: False
class TestArgs:
    skip_tokenizer_init = False
mm_utils.get_global_server_args = lambda: TestArgs()

from sglang.srt.managers.mm_utils import wrap_shm_features, unwrap_shm_features

class MockMMItem:
    def __init__(self, tensor):
        self.feature = tensor

class MockMMInputs:
    def __init__(self, items):
        self._items = items
    def get(self, key, default=None):
        if key == 'mm_items':
            return self._items
        return default

class MockRequest:
    def __init__(self, tensor):
        self.mm_inputs = MockMMInputs([MockMMItem(tensor)])

t = torch.randn(3, 6)
req = MockRequest(t)

# Wrap (tensor -> ShmPointerMMData)
wrap_shm_features(req)
item = req.mm_inputs.get('mm_items')[0]
assert isinstance(item.feature, ShmPointerMMData), \
    f'After wrap, feature should be ShmPointerMMData, got {type(item.feature).__name__}'

# Simulate pickle transport
req2 = pickle.loads(pickle.dumps(req))

# Unwrap (ShmPointerMMData -> tensor)
unwrap_shm_features(req2)
result = req2.mm_inputs.get('mm_items')[0].feature
assert isinstance(result, torch.Tensor), \
    f'After unwrap, feature should be Tensor, got {type(result).__name__}'
assert torch.allclose(result, t, atol=1e-6), 'Data mismatch after wrap+unwrap'

print('PASS: wrap+pickle+unwrap roundtrip is identity')
" 2>&1
if [ $? -eq 0 ]; then
    RESULTS[p2p_wrap_unwrap_identity]=1
    echo "PASS: p2p_wrap_unwrap_identity"
else
    echo "FAIL: p2p_wrap_unwrap_identity"
fi

# ══════════════════════════════════════════════════════════════════════
# Compute final score
# ══════════════════════════════════════════════════════════════════════
echo ""
echo "=== Results ==="
TOTAL=0
for key in "${!WEIGHTS[@]}"; do
    w=${WEIGHTS[$key]}
    r=${RESULTS[$key]}
    contribution=$(python3 -c "print(f'{$w * $r:.4f}')")
    TOTAL=$(python3 -c "print(f'{$TOTAL + $w * $r:.4f}')")
    echo "  $key: result=$r weight=$w contribution=$contribution"
done

echo ""
echo "Total score: $TOTAL"
echo "$TOTAL" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
