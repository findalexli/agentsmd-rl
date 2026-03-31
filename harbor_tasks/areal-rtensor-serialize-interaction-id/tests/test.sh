#!/usr/bin/env bash
set +e

cd /repos/AReaL
mkdir -p /output

REWARD=0
add_reward() {
    REWARD=$(python3 -c "print(round($REWARD + $1, 4))")
}

# === GATE: Syntax check ===
# [pr_diff] (0): Syntax gate — abort on failure
echo "=== GATE: Syntax check ==="
if ! python3 -c "
import ast, sys
files = [
    'areal/experimental/openai/types.py',
    'areal/experimental/openai/proxy/server.py',
    'areal/experimental/inference_service/data_proxy/app.py',
]
for f in files:
    try:
        with open(f) as fh:
            ast.parse(fh.read())
    except SyntaxError as e:
        print(f'Syntax error in {f}: {e}', file=sys.stderr)
        sys.exit(1)
print('All files parse OK')
"; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# === Fail-to-pass: interaction_id setter and getter on bare instance ===
# [pr_diff] (0.15): Bare InteractionWithTokenLogpReward supports setting interaction_id
echo "=== Test 1: interaction_id setter+getter on bare instance ==="
if python3 -c "
from areal.experimental.openai.types import InteractionWithTokenLogpReward
i = InteractionWithTokenLogpReward()
i.interaction_id = 'test-id-123'
got = i.interaction_id
assert got == 'test-id-123', f'Expected test-id-123, got {got}'
print('PASS')
" 2>&1; then
    add_reward 0.15
    echo "  +0.15"
else
    echo "  FAIL"
fi

# === Fail-to-pass: interaction_id is None initially, set via setter, read back ===
# [pr_diff] (0.15): interaction_id returns None before set, returns value after set
echo "=== Test 2: interaction_id None->set->read lifecycle ==="
if python3 -c "
from areal.experimental.openai.types import InteractionWithTokenLogpReward
i = InteractionWithTokenLogpReward()
# Initially should be None (no completion, no response, no stored ID)
assert i.interaction_id is None, f'Expected None initially, got {i.interaction_id}'
# Set via public setter
i.interaction_id = 'lifecycle-id-789'
got = i.interaction_id
assert got == 'lifecycle-id-789', f'Expected lifecycle-id-789, got {got}'
# Set again — should overwrite
i.interaction_id = 'updated-id-999'
got2 = i.interaction_id
assert got2 == 'updated-id-999', f'Expected updated-id-999, got {got2}'
print('PASS')
" 2>&1; then
    add_reward 0.15
    echo "  +0.15"
else
    echo "  FAIL"
fi

# === Fail-to-pass: setter raises ValueError for completion interactions ===
# [pr_diff] (0.10): Cannot overwrite interaction_id on completion/response objects
echo "=== Test 3: setter raises ValueError on completion instance ==="
if python3 -c "
from areal.experimental.openai.types import InteractionWithTokenLogpReward
from unittest.mock import MagicMock
i = InteractionWithTokenLogpReward()
i.completion = MagicMock()
i.completion.id = 'comp-123'
try:
    i.interaction_id = 'should-fail'
    import sys
    print('FAIL: Expected error but setter succeeded', file=sys.stderr)
    sys.exit(1)
except Exception:
    pass  # Any exception type is acceptable (ValueError, RuntimeError, etc.)
print('PASS')
" 2>&1; then
    add_reward 0.10
    echo "  +0.10"
else
    echo "  FAIL"
fi

# === Fail-to-pass: serialize/deserialize roundtrip preserves interaction_id ===
# [pr_diff] (0.30): interaction_id survives serialize → deserialize cycle (core bug)
echo "=== Test 4: roundtrip preserves interaction_id ==="
if python3 -c "
from areal.experimental.openai.proxy.server import (
    deserialize_interactions,
    serialize_interactions,
)
from areal.experimental.openai.types import InteractionWithTokenLogpReward
import torch

i = InteractionWithTokenLogpReward()
i._cache = {
    'input_ids': torch.tensor([[1, 2, 3]]),
    'logprobs': torch.tensor([[0.1, 0.2, 0.3]]),
}
i.reward = 1.0
i.interaction_id = 'preserve-me-456'

serialized = serialize_interactions({'k1': i})
deserialized = deserialize_interactions(serialized)

got = deserialized['k1'].interaction_id
assert got == 'preserve-me-456', f'Expected preserve-me-456, got {got}'
print('PASS')
" 2>&1; then
    add_reward 0.30
    echo "  +0.30"
else
    echo "  FAIL"
fi

# === Fail-to-pass: roundtrip with multiple interactions preserves all IDs ===
# [pr_diff] (0.10): Multiple interactions each retain their own interaction_id
echo "=== Test 5: multi-interaction roundtrip ==="
if python3 -c "
from areal.experimental.openai.proxy.server import (
    deserialize_interactions,
    serialize_interactions,
)
from areal.experimental.openai.types import InteractionWithTokenLogpReward
import torch

interactions = {}
for idx in range(3):
    item = InteractionWithTokenLogpReward()
    item._cache = {
        'input_ids': torch.tensor([[idx, idx+1]]),
        'logprobs': torch.tensor([[0.1 * idx, 0.2 * idx]]),
    }
    item.reward = float(idx)
    item.interaction_id = f'batch-id-{idx}'
    interactions[f'key_{idx}'] = item

serialized = serialize_interactions(interactions)
deserialized = deserialize_interactions(serialized)

for idx in range(3):
    key = f'key_{idx}'
    got = deserialized[key].interaction_id
    expected = f'batch-id-{idx}'
    assert got == expected, f'{key}: expected {expected}, got {got}'
    assert deserialized[key].reward == float(idx), f'{key}: reward mismatch'
print('PASS')
" 2>&1; then
    add_reward 0.10
    echo "  +0.10"
else
    echo "  FAIL"
fi

# === Pass-to-pass: serialize_value/deserialize_value tensor roundtrip ===
# [repo_tests] (0.10): Core serialization utilities still work correctly
echo "=== Test 6: serialize_value/deserialize_value P2P ==="
if python3 -c "
from areal.infra.rpc.serialization import serialize_value, deserialize_value
import torch

t = torch.tensor([1.0, 2.0, 3.0])
s = serialize_value(t)
d = deserialize_value(s)
assert torch.allclose(t, d), 'Tensor roundtrip failed'

data = {'a': torch.tensor([1, 2]), 'b': 'hello', 'c': [torch.tensor([3.0])]}
s2 = serialize_value(data)
d2 = deserialize_value(s2)
assert torch.allclose(data['a'], d2['a'])
assert d2['b'] == 'hello'
assert torch.allclose(data['c'][0], d2['c'][0])
print('PASS')
" 2>&1; then
    add_reward 0.10
    echo "  +0.10"
else
    echo "  FAIL"
fi

# === Fail-to-pass: setter rejects overwrite on response instance too ===
# [pr_diff] (0.05): Cannot overwrite interaction_id on response objects (not just completion)
echo "=== Test 7: setter rejects on response instance ==="
if python3 -c "
from areal.experimental.openai.types import InteractionWithTokenLogpReward
from unittest.mock import MagicMock
i = InteractionWithTokenLogpReward()
i.response = MagicMock()
i.response.id = 'resp-456'
try:
    i.interaction_id = 'should-fail'
    import sys
    print('FAIL: Expected error but setter succeeded', file=sys.stderr)
    sys.exit(1)
except Exception:
    pass  # Any exception is acceptable
print('PASS')
" 2>&1; then
    add_reward 0.05
    echo "  +0.05"
else
    echo "  FAIL"
fi

# === Config-derived (gated): No wildcard imports ===
# [agent_config] (0.05): "No wildcard imports (from x import *)" — AGENTS.md:30 @ 3bf10c9
BEHAVIORAL_PASSED=0
if [ "$(python3 -c "print(1 if $REWARD >= 0.25 else 0)")" = "1" ]; then
    BEHAVIORAL_PASSED=1
fi

echo "=== Test 8: No wildcard imports ==="
if [ "$BEHAVIORAL_PASSED" = "1" ]; then
    if ! grep -rn 'from .* import \*' \
        areal/experimental/openai/types.py \
        areal/experimental/openai/proxy/server.py \
        areal/experimental/inference_service/data_proxy/app.py 2>/dev/null; then
        add_reward 0.05
        echo "  +0.05"
    else
        echo "  FAIL: wildcard imports found"
    fi
else
    echo "  SKIP (behavioral gate not met)"
fi

echo ""
echo "Total reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
