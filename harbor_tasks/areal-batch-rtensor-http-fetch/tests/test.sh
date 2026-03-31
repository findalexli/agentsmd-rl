#!/usr/bin/env bash
set +e

SERVER="/workspace/AReaL/areal/infra/rpc/rpc_server.py"
RTENSOR="/workspace/AReaL/areal/infra/rpc/rtensor.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[gate]=0.00
WEIGHTS[f2p_batch_endpoint]=0.30
WEIGHTS[f2p_batching_behavior]=0.30
WEIGHTS[f2p_chunking]=0.15
WEIGHTS[p2p_ordering]=0.10
WEIGHTS[p2p_missing_shards]=0.10
WEIGHTS[config_no_wildcard]=0.025
WEIGHTS[config_no_bare_print]=0.025

for key in gate f2p_batch_endpoint f2p_batching_behavior f2p_chunking p2p_ordering p2p_missing_shards config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Code parses and basic imports work ----------
python3 << 'PYGATE'
import sys
sys.path.insert(0, '/workspace/AReaL')

try:
    import ast
    with open('/workspace/AReaL/areal/infra/rpc/rpc_server.py') as f:
        ast.parse(f.read())
    with open('/workspace/AReaL/areal/infra/rpc/rtensor.py') as f:
        ast.parse(f.read())

    # Try importing the modules
    from areal.infra.rpc import rtensor
    from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo

    print("GATE PASS")
    sys.exit(0)
except Exception as e:
    print(f"GATE FAIL: {e}")
    sys.exit(1)
PYGATE

if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
RESULTS[gate]=1
echo "TEST gate: PASS"

# ---------- F2P (30%): Batch endpoint actually returns data ----------
# [pr_diff] (0.30): /data/batch endpoint accepts multiple shard IDs and returns serialized data
python3 << 'PYEOF'
import sys
import sys
sys.path.insert(0, '/workspace/AReaL')

import torch
from flask import Flask

# Setup minimal Flask app with the endpoint
app = Flask(__name__)

# Import the actual code to test
exec(open('/workspace/AReaL/areal/infra/rpc/rpc_server.py').read())

with app.test_client() as client:
    # Store some test data first
    import orjson
    from areal.infra.rpc.serialization import serialize_value

    tensor1 = torch.tensor([1.0, 2.0, 3.0])
    tensor2 = torch.tensor([4.0, 5.0])

    shard_id1 = "test-shard-1"
    shard_id2 = "test-shard-2"

    # Store shards via the existing endpoint
    for sid, tensor in [(shard_id1, tensor1), (shard_id2, tensor2)]:
        resp = client.put(f'/data/{sid}',
                          data=orjson.dumps(serialize_value(tensor)),
                          content_type='application/octet-stream')
        if resp.status_code != 200:
            print(f"F2P_BATCH_ENDPOINT FAIL: Could not store test data: {resp.status_code}")
            sys.exit(1)

    # Now test batch retrieval
    resp = client.post('/data/batch',
                       json={"shard_ids": [shard_id1, shard_id2]},
                       content_type='application/json')

    if resp.status_code != 200:
        print(f"F2P_BATCH_ENDPOINT FAIL: Batch endpoint returned {resp.status_code}")
        sys.exit(1)

    # Verify we got actual tensor data back
    from areal.infra.rpc.serialization import deserialize_value
    try:
        data = orjson.loads(resp.data)
        tensors = deserialize_value(data)
        if len(tensors) != 2:
            print(f"F2P_BATCH_ENDPOINT FAIL: Expected 2 tensors, got {len(tensors)}")
            sys.exit(1)
        if not torch.allclose(tensors[0], tensor1):
            print("F2P_BATCH_ENDPOINT FAIL: First tensor mismatch")
            sys.exit(1)
        if not torch.allclose(tensors[1], tensor2):
            print("F2P_BATCH_ENDPOINT FAIL: Second tensor mismatch")
            sys.exit(1)
    except Exception as e:
        print(f"F2P_BATCH_ENDPOINT FAIL: Could not deserialize response: {e}")
        sys.exit(1)

print("F2P_BATCH_ENDPOINT PASS")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_batch_endpoint]=1 && echo "TEST f2p_batch_endpoint: PASS" || echo "TEST f2p_batch_endpoint: FAIL"

# ---------- F2P (30%): HttpRTensorBackend groups shards by node ----------
# [pr_diff] (0.30): Backend groups shards by node_addr before batching
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/AReaL')

try:
    from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo

    # Create backend
    backend = HttpRTensorBackend(max_shards_per_request=10)

    # Verify __init__ accepts and stores the parameter
    if not hasattr(backend, 'max_shards_per_request'):
        print("F2P_BATCHING_BEHAVIOR FAIL: backend missing max_shards_per_request")
        sys.exit(1)

    if backend.max_shards_per_request != 10:
        print(f"F2P_BATCHING_BEHAVIOR FAIL: max_shards_per_request is {backend.max_shards_per_request}, expected 10")
        sys.exit(1)

    # Verify _fetch_shard_group method exists (needed for batching)
    if not hasattr(backend, '_fetch_shard_group'):
        print("F2P_BATCHING_BEHAVIOR FAIL: _fetch_shard_group method not found")
        sys.exit(1)

    # Verify fetch method exists
    if not callable(getattr(backend, 'fetch', None)):
        print("F2P_BATCHING_BEHAVIOR FAIL: fetch method not callable")
        sys.exit(1)

except Exception as e:
    print(f"F2P_BATCHING_BEHAVIOR FAIL: {e}")
    sys.exit(1)

print("F2P_BATCHING_BEHAVIOR PASS")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_batching_behavior]=1 && echo "TEST f2p_batching_behavior: PASS" || echo "TEST f2p_batching_behavior: FAIL"

# ---------- F2P (15%): Chunking respects max_shards_per_request ----------
# [pr_diff] (0.15): Large batches are split into chunks based on max_shards_per_request
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/AReaL')

import asyncio
from unittest.mock import MagicMock, AsyncMock

try:
    from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo
    import torch

    # Create backend with small max_shards_per_request
    backend = HttpRTensorBackend(max_shards_per_request=2)

    # Create 5 shards all from same node
    shards = [
        TensorShardInfo(shard_id=f"shard-{i}", node_addr="test-node:8080")
        for i in range(5)
    ]

    # Track how many chunks are requested
    requested_chunks = []

    async def mock_fetch_shard_group(session, node_addr, grouped):
        requested_chunks.append(len(grouped))
        # Return fake tensors matching the group size
        return [torch.tensor([float(i)]) for i, _ in enumerate(grouped)]

    # Mock the session and _fetch_shard_group
    class FakeSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False

    backend._create_session = lambda: FakeSession()
    backend._fetch_shard_group = mock_fetch_shard_group

    # Call fetch
    result = backend.fetch(shards)

    # Should have made 3 chunks: [2, 2, 1] for 5 shards with max=2
    if len(requested_chunks) != 3:
        print(f"F2P_CHUNKING FAIL: Expected 3 chunks, got {len(requested_chunks)}")
        sys.exit(1)

    if requested_chunks != [2, 2, 1]:
        print(f"F2P_CHUNKING FAIL: Expected chunk sizes [2, 2, 1], got {requested_chunks}")
        sys.exit(1)

    # Result should have 5 tensors
    if len(result) != 5:
        print(f"F2P_CHUNKING FAIL: Expected 5 results, got {len(result)}")
        sys.exit(1)

except Exception as e:
    print(f"F2P_CHUNKING FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("F2P_CHUNKING PASS")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[f2p_chunking]=1 && echo "TEST f2p_chunking: PASS" || echo "TEST f2p_chunking: FAIL"

# ---------- P2P (10%): Order preserved across chunks ----------
# [pr_diff] (0.10): Shards maintain original order after batching
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/AReaL')

import asyncio
from unittest.mock import MagicMock, AsyncMock

try:
    from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo
    import torch

    backend = HttpRTensorBackend(max_shards_per_request=2)

    # Create shards with specific IDs that we can verify order of
    shards = [
        TensorShardInfo(shard_id=f"shard-{i}", node_addr="test-node:8080")
        for i in range(4)
    ]

    async def mock_fetch_shard_group(session, node_addr, grouped):
        # Return tensors with values corresponding to original indices
        return [torch.tensor([float(idx)]) for idx, _ in grouped]

    class FakeSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False

    backend._create_session = lambda: FakeSession()
    backend._fetch_shard_group = mock_fetch_shard_group

    result = backend.fetch(shards)

    # Verify order is preserved: result[i] should correspond to shard-i
    for i, tensor in enumerate(result):
        expected = float(i)
        actual = tensor.item()
        if actual != expected:
            print(f"P2P_ORDERING FAIL: Position {i} expected {expected}, got {actual}")
            sys.exit(1)

except Exception as e:
    print(f"P2P_ORDERING FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("P2P_ORDERING PASS")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_ordering]=1 && echo "TEST p2p_ordering: PASS" || echo "TEST p2p_ordering: FAIL"

# ---------- P2P (10%): Missing shards reported with structured error ----------
# [pr_diff] (0.10): Batch endpoint returns 400 with missing_shard_ids list
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/AReaL')

from flask import Flask
import orjson

app = Flask(__name__)
exec(open('/workspace/AReaL/areal/infra/rpc/rpc_server.py').read())

with app.test_client() as client:
    # Store only one shard
    from areal.infra.rpc.serialization import serialize_value
    tensor = torch.tensor([1.0, 2.0])
    shard_id = "present-shard"

    resp = client.put(f'/data/{shard_id}',
                      data=orjson.dumps(serialize_value(tensor)),
                      content_type='application/octet-stream')

    # Request batch with one present and one missing shard
    resp = client.post('/data/batch',
                       json={"shard_ids": [shard_id, "missing-shard"]},
                       content_type='application/json')

    if resp.status_code != 400:
        print(f"P2P_MISSING_SHARDS FAIL: Expected 400, got {resp.status_code}")
        sys.exit(1)

    try:
        data = resp.get_json()
        if "missing_shard_ids" not in data:
            print("P2P_MISSING_SHARDS FAIL: Response missing 'missing_shard_ids' field")
            sys.exit(1)
        if "missing-shard" not in data["missing_shard_ids"]:
            print("P2P_MISSING_SHARDS FAIL: missing_shard_ids doesn't contain expected shard")
            sys.exit(1)
    except Exception as e:
        print(f"P2P_MISSING_SHARDS FAIL: Could not parse error response: {e}")
        sys.exit(1)

print("P2P_MISSING_SHARDS PASS")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_missing_shards]=1 && echo "TEST p2p_missing_shards: PASS" || echo "TEST p2p_missing_shards: FAIL"

# ---------- Config (0.025): No wildcard imports ----------
# Source: AGENTS.md line 13 @ commit 3142b88a5e93e991df727c81892d6cb8bd65d06e
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$SERVER" "$RTENSOR" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config (0.025): No bare print() in production code ----------
# Source: AGENTS.md line 80 @ commit 3142b88a5e93e991df727c81892d6cb8bd65d06e
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$SERVER" "$RTENSOR" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

SCORE=$(python3 -c "
w={'gate':${WEIGHTS[gate]},'f2p_batch_endpoint':${WEIGHTS[f2p_batch_endpoint]},'f2p_batching_behavior':${WEIGHTS[f2p_batching_behavior]},'f2p_chunking':${WEIGHTS[f2p_chunking]},'p2p_ordering':${WEIGHTS[p2p_ordering]},'p2p_missing_shards':${WEIGHTS[p2p_missing_shards]},'config_no_wildcard':${WEIGHTS[config_no_wildcard]},'config_no_bare_print':${WEIGHTS[config_no_bare_print]}}
r={'gate':${RESULTS[gate]},'f2p_batch_endpoint':${RESULTS[f2p_batch_endpoint]},'f2p_batching_behavior':${RESULTS[f2p_batching_behavior]},'f2p_chunking':${RESULTS[f2p_chunking]},'p2p_ordering':${RESULTS[p2p_ordering]},'p2p_missing_shards':${RESULTS[p2p_missing_shards]},'config_no_wildcard':${RESULTS[config_no_wildcard]},'config_no_bare_print':${RESULTS[config_no_bare_print]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
