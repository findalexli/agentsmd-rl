"""
Task: areal-batch-rtensor-http-fetch
Repo: inclusionAI/AReaL @ 3142b88a5e93e991df727c81892d6cb8bd65d06e
PR:   1077

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"
SERVER = f"{REPO}/areal/infra/rpc/rpc_server.py"
RTENSOR = f"{REPO}/areal/infra/rpc/rtensor.py"

# Mock preamble that creates lightweight package stubs to avoid the heavy
# areal/__init__.py → areal/infra/__init__.py import cascades (which pull in
# ray, transformers, hydra, CUDA engines, etc.).  Only the modules actually
# needed for the code under test are imported for real.
_MOCK_PREAMBLE = """\
import sys, types
from unittest.mock import MagicMock

# --- 1. Mock heavy external deps not installed in the container ---
for _m in [
    'ray', 'ray.internal', 'ray.util', 'ray.actor',
    'uvloop',
    'hydra', 'hydra.core', 'hydra.core.global_hydra',
    'omegaconf',
    'transformers', 'transformers.utils', 'transformers.utils.import_utils',
    'transformers.integrations', 'transformers.integrations.hub_kernels',
    'sglang', 'vllm',
]:
    sys.modules.setdefault(_m, MagicMock())

sys.modules['transformers.utils.import_utils'].is_torch_npu_available = lambda: False
sys.modules['transformers.integrations.hub_kernels'].is_kernel = lambda x: False
sys.modules['omegaconf'].MISSING = object()
sys.modules['omegaconf'].DictConfig = MagicMock
sys.modules['omegaconf'].OmegaConf = MagicMock()

# Provide real sentinel types so isinstance() works in serialization.py
class _FakeTokenizer: pass
class _FakeTokenizerFast: pass
class _FakeProcessorMixin: pass
_tf = sys.modules['transformers']
_tf.PreTrainedTokenizer = _FakeTokenizer
_tf.PreTrainedTokenizerFast = _FakeTokenizerFast
_tf.ProcessorMixin = _FakeProcessorMixin
_tf.AutoTokenizer = MagicMock()
_tf.AutoProcessor = MagicMock()

# --- 2. Create real package stubs to bypass heavy __init__.py cascades ---
# areal/__init__.py imports from areal.infra which cascades into controllers,
# launchers, schedulers, etc.  We short-circuit by inserting empty packages
# with correct __path__ so submodule lookups still find the .py files.
for _pkg in ['areal', 'areal.infra', 'areal.utils', 'areal.infra.utils',
             'areal.infra.rpc']:
    _mod = types.ModuleType(_pkg)
    _mod.__path__ = ['/workspace/AReaL/' + _pkg.replace('.', '/')]
    _mod.__package__ = _pkg
    sys.modules[_pkg] = _mod

# --- 3. Mock internal modules with heavy transitive deps ---
# These are imported by rpc_server.py but irrelevant to the endpoint under test.
for _m in [
    'areal.api', 'areal.api.cli_args', 'areal.api.engine_api',
    'areal.infra.platforms', 'areal.infra.platforms.cpu',
    'areal.infra.platforms.cuda', 'areal.infra.platforms.npu',
    'areal.infra.platforms.platform', 'areal.infra.platforms.unknown',
    'areal.utils.data', 'areal.utils.dynamic_import',
    'areal.utils.name_resolve', 'areal.utils.names',
    'areal.utils.perf_tracer', 'areal.utils.seeding',
    'areal.utils.network', 'areal.utils.pkg_version',
    'areal.utils.constants',
    'areal.infra.utils.proc',
    'areal.engine', 'areal.engine.fsdp_utils',
    'areal.engine.fsdp_utils.attn_impl',
    'areal.version', 'areal.trainer',
]:
    sys.modules.setdefault(_m, MagicMock())
"""


def _run_python(script: str, timeout: int = 30) -> None:
    """Run a Python script (with mock preamble) in a subprocess; assert exit code 0."""
    full_script = _MOCK_PREAMBLE + "\n" + script
    r = subprocess.run(
        ["python3", "-c", full_script],
        capture_output=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, (
        f"Script failed (rc={r.returncode}):\n"
        f"STDOUT: {r.stdout.decode()}\nSTDERR: {r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [SERVER, RTENSOR]:
        src = Path(path).read_text()
        ast.parse(src)

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    # Install ruff if needed
    subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, timeout=120)
    r = subprocess.run(
        ["ruff", "check", SERVER, RTENSOR],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    # Install ruff if needed
    subprocess.run(["pip", "install", "ruff==0.14.9", "-q"], capture_output=True, timeout=120)
    r = subprocess.run(
        ["ruff", "format", "--check", SERVER, RTENSOR],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"



# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — server: /data/batch endpoint
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_batch_endpoint_returns_data():
    """POST /data/batch returns stored tensor data for valid shard IDs."""
    _run_python(f"""
import torch, orjson
from areal.infra.rpc.rpc_server import app
from areal.infra.rpc.serialization import serialize_value, deserialize_value

with app.test_client() as client:
    tensors = {{
        "shard-a": torch.tensor([1.0, 2.0, 3.0]),
        "shard-b": torch.tensor([4.0, 5.0]),
        "shard-c": torch.tensor([7.0, 8.0, 9.0, 10.0]),
    }}
    for sid, t in tensors.items():
        resp = client.put(f'/data/{{sid}}',
                          data=orjson.dumps(serialize_value(t)),
                          content_type='application/octet-stream')
        assert resp.status_code == 200, f"PUT /data/{{sid}} failed: {{resp.status_code}}"

    resp = client.post('/data/batch',
                       json={{"shard_ids": ["shard-a", "shard-b", "shard-c"]}},
                       content_type='application/json')
    assert resp.status_code == 200, f"Batch returned {{resp.status_code}}"

    result = deserialize_value(orjson.loads(resp.data))
    assert len(result) == 3, f"Expected 3 tensors, got {{len(result)}}"
    assert torch.allclose(result[0], tensors["shard-a"]), "shard-a mismatch"
    assert torch.allclose(result[1], tensors["shard-b"]), "shard-b mismatch"
    assert torch.allclose(result[2], tensors["shard-c"]), "shard-c mismatch"
""")


# [pr_diff] fail_to_pass
def test_batch_endpoint_preserves_order():
    """Batch fetch returns shards in the exact order requested."""
    _run_python(f"""
import torch, orjson
from areal.infra.rpc.rpc_server import app
from areal.infra.rpc.serialization import serialize_value, deserialize_value

with app.test_client() as client:
    # Store 5 shards with distinct values
    ids = [f"order-{{i}}" for i in range(5)]
    for i, sid in enumerate(ids):
        t = torch.tensor([float(i) * 10 + j for j in range(3)])
        resp = client.put(f'/data/{{sid}}',
                          data=orjson.dumps(serialize_value(t)),
                          content_type='application/octet-stream')
        assert resp.status_code == 200

    # Request in reverse order
    reversed_ids = list(reversed(ids))
    resp = client.post('/data/batch',
                       json={{"shard_ids": reversed_ids}},
                       content_type='application/json')
    assert resp.status_code == 200, f"Batch returned {{resp.status_code}}"

    result = deserialize_value(orjson.loads(resp.data))
    assert len(result) == 5, f"Expected 5 tensors, got {{len(result)}}"

    # Verify reverse order: result[0] should be order-4's tensor, etc.
    for j, tensor in enumerate(result):
        original_idx = 4 - j
        expected = torch.tensor([float(original_idx) * 10 + k for k in range(3)])
        assert torch.allclose(tensor, expected), (
            f"Position {{j}}: expected tensor for order-{{original_idx}}, got {{tensor}}"
        )
""")


# [pr_diff] fail_to_pass
def test_batch_endpoint_missing_shards():
    """Batch endpoint returns 400 with missing_shard_ids for absent shards."""
    _run_python(f"""
import torch, orjson
from areal.infra.rpc.rpc_server import app
from areal.infra.rpc.serialization import serialize_value

with app.test_client() as client:
    # Store one shard
    t = torch.tensor([1.0, 2.0])
    resp = client.put('/data/present-shard',
                      data=orjson.dumps(serialize_value(t)),
                      content_type='application/octet-stream')
    assert resp.status_code == 200

    # Request batch with one present and two missing
    resp = client.post('/data/batch',
                       json={{"shard_ids": ["present-shard", "missing-1", "missing-2"]}},
                       content_type='application/json')
    assert resp.status_code == 400, f"Expected 400, got {{resp.status_code}}"

    data = resp.get_json()
    assert "missing_shard_ids" in data, "Response missing 'missing_shard_ids' field"
    missing = set(data["missing_shard_ids"])
    assert "missing-1" in missing, "missing-1 not reported"
    assert "missing-2" in missing, "missing-2 not reported"
    assert "present-shard" not in missing, "present-shard incorrectly reported as missing"
""")


# [pr_diff] fail_to_pass
def test_batch_endpoint_empty_request():
    """Batch endpoint handles empty shard_ids list gracefully."""
    _run_python(f"""
import orjson
from areal.infra.rpc.rpc_server import app
from areal.infra.rpc.serialization import deserialize_value

with app.test_client() as client:
    resp = client.post('/data/batch',
                       json={{"shard_ids": []}},
                       content_type='application/json')
    assert resp.status_code == 200, f"Expected 200 for empty request, got {{resp.status_code}}"

    result = deserialize_value(orjson.loads(resp.data))
    assert isinstance(result, list), f"Expected list, got {{type(result)}}"
    assert len(result) == 0, f"Expected empty list, got {{len(result)}} items"
""")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_single_shard_retrieval():
    """Existing single-shard GET /data/<shard_id> still works."""
    _run_python(f"""
import torch, orjson
from areal.infra.rpc.rpc_server import app
from areal.infra.rpc.serialization import serialize_value, deserialize_value

with app.test_client() as client:
    t = torch.tensor([3.14, 2.72, 1.41])
    resp = client.put('/data/single-test',
                      data=orjson.dumps(serialize_value(t)),
                      content_type='application/octet-stream')
    assert resp.status_code == 200, f"PUT failed: {{resp.status_code}}"

    resp = client.get('/data/single-test')
    assert resp.status_code == 200, f"GET failed: {{resp.status_code}}"

    result = deserialize_value(orjson.loads(resp.data))
    assert torch.allclose(result, t), f"Tensor mismatch: {{result}} vs {{t}}"
""")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — client: HttpRTensorBackend batching
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_backend_max_shards_configurable():
    """HttpRTensorBackend accepts and validates max_shards_per_request."""
    _run_python(f"""
from areal.infra.rpc.rtensor import HttpRTensorBackend

# Default construction
backend = HttpRTensorBackend()
assert hasattr(backend, "max_shards_per_request"), "Missing max_shards_per_request attribute"
assert backend.max_shards_per_request > 0, "Default must be positive"

# Custom values
for val in [1, 8, 16, 64, 128]:
    b = HttpRTensorBackend(max_shards_per_request=val)
    assert b.max_shards_per_request == val, f"Expected {{val}}, got {{b.max_shards_per_request}}"

# Invalid: zero and negative must raise
try:
    HttpRTensorBackend(max_shards_per_request=0)
    raise AssertionError("max_shards_per_request=0 should raise")
except (ValueError, TypeError):
    pass

try:
    HttpRTensorBackend(max_shards_per_request=-3)
    raise AssertionError("max_shards_per_request=-3 should raise")
except (ValueError, TypeError):
    pass
""")


# [pr_diff] fail_to_pass
def test_backend_groups_by_node():
    """fetch() groups shards by node_addr into batch requests."""
    _run_python(f"""
import torch
from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo

backend = HttpRTensorBackend(max_shards_per_request=100)

shards = [
    TensorShardInfo(shard_id="a1", node_addr="node-a"),
    TensorShardInfo(shard_id="b1", node_addr="node-b"),
    TensorShardInfo(shard_id="a2", node_addr="node-a"),
    TensorShardInfo(shard_id="b2", node_addr="node-b"),
    TensorShardInfo(shard_id="a3", node_addr="node-a"),
]

group_calls = []

async def mock_fetch_shard_group(session, node_addr, grouped, **kwargs):
    ids = [s.shard_id for _, s in grouped]
    group_calls.append((node_addr, ids))
    return [torch.tensor([idx]) for idx, _ in grouped]

class FakeSession:
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False

backend._create_session = lambda: FakeSession()
backend._fetch_shard_group = mock_fetch_shard_group

results = backend.fetch(shards)

assert len(group_calls) == 2, f"Expected 2 groups, got {{len(group_calls)}}"
nodes = {{n for n, _ in group_calls}}
assert nodes == {{"node-a", "node-b"}}, f"Expected nodes a,b, got {{nodes}}"

for node, ids in group_calls:
    if node == "node-a":
        assert ids == ["a1", "a2", "a3"], f"node-a shards: {{ids}}"
    else:
        assert ids == ["b1", "b2"], f"node-b shards: {{ids}}"
""")


# [pr_diff] fail_to_pass
def test_backend_chunks_large_requests():
    """Same-node shards exceeding max_shards_per_request are chunked."""
    _run_python(f"""
import torch
from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo

cases = [
    (2, 5, [["s0", "s1"], ["s2", "s3"], ["s4"]]),
    (3, 7, [["s0", "s1", "s2"], ["s3", "s4", "s5"], ["s6"]]),
    (4, 4, [["s0", "s1", "s2", "s3"]]),
    (1, 3, [["s0"], ["s1"], ["s2"]]),
]

for max_per_req, n_shards, expected_chunks in cases:
    backend = HttpRTensorBackend(max_shards_per_request=max_per_req)
    shards = [TensorShardInfo(shard_id=f"s{{i}}", node_addr="node-a") for i in range(n_shards)]

    chunk_calls = []

    async def mock_fetch(session, node_addr, grouped, **kw):
        ids = [s.shard_id for _, s in grouped]
        chunk_calls.append(ids)
        return [torch.tensor([int(s.shard_id[1:])]) for _, s in grouped]

    class FakeSession:
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False

    backend._create_session = lambda: FakeSession()
    backend._fetch_shard_group = mock_fetch

    backend.fetch(shards)
    assert chunk_calls == expected_chunks, (
        f"max={{max_per_req}}, n={{n_shards}}: got {{chunk_calls}}, expected {{expected_chunks}}"
    )
""")


# [pr_diff] fail_to_pass
def test_backend_preserves_original_order():
    """Results maintain original request order across grouped/chunked fetches."""
    _run_python(f"""
import torch
from areal.infra.rpc.rtensor import HttpRTensorBackend, TensorShardInfo

backend = HttpRTensorBackend(max_shards_per_request=2)

# Interleave 3 nodes, 8 shards
shards = [
    TensorShardInfo(shard_id="a0", node_addr="node-a"),
    TensorShardInfo(shard_id="b0", node_addr="node-b"),
    TensorShardInfo(shard_id="c0", node_addr="node-c"),
    TensorShardInfo(shard_id="a1", node_addr="node-a"),
    TensorShardInfo(shard_id="b1", node_addr="node-b"),
    TensorShardInfo(shard_id="a2", node_addr="node-a"),
    TensorShardInfo(shard_id="c1", node_addr="node-c"),
    TensorShardInfo(shard_id="b2", node_addr="node-b"),
]

async def mock_fetch(session, node_addr, grouped, **kw):
    return [torch.tensor([idx]) for idx, _ in grouped]

class FakeSession:
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False

backend._create_session = lambda: FakeSession()
backend._fetch_shard_group = mock_fetch

results = backend.fetch(shards)
assert len(results) == 8, f"Expected 8 results, got {{len(results)}}"
for i, t in enumerate(results):
    assert t.item() == i, f"Position {{i}}: got {{t.item()}}, expected {{i}}"
""")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:10937 @ 3142b88a5e93e991df727c81892d6cb8bd65d06e
def test_no_wildcard_imports():
    """No wildcard imports (from x import *) in modified files."""
    for path in [SERVER, RTENSOR]:
        src = Path(path).read_text()
        matches = re.findall(r"^\s*from\s+\S+\s+import\s+\*", src, re.MULTILINE)
        assert not matches, f"Wildcard import in {path}: {matches}"


# [agent_config] pass_to_pass — AGENTS.md:10997 @ 3142b88a5e93e991df727c81892d6cb8bd65d06e
def test_no_bare_print():
    """No bare print() calls in production code (must use logger)."""
    for path in [SERVER, RTENSOR]:
        src = Path(path).read_text()
        matches = re.findall(r"^\s*print\(", src, re.MULTILINE)
        assert not matches, f"Bare print() in {path}: {matches}"


# [agent_config] pass_to_pass — AGENTS.md:31 @ 3142b88a5e93e991df727c81892d6cb8bd65d06e
def test_no_hardcoded_endpoints():
    """No hardcoded IP addresses or static URL strings in modified files."""
    # Matches "http://..." or "https://..." literals that don't use an f-string variable,
    # i.e., the hostname is a literal (not {something}).
    hardcoded_url_re = re.compile(r'"https?://[^{"\s][^"\s]*"')
    # Matches dotted-quad IP address literals like "192.168.1.1" or "127.0.0.1"
    ip_literal_re = re.compile(r"(?:(?!0\\.0\\.0\\.0\\b)\\d{1,3}(?:\\.\\d{1,3}){3})")
    for path in [SERVER, RTENSOR]:
        src = Path(path).read_text()
        url_matches = hardcoded_url_re.findall(src)
        assert not url_matches, f"Hardcoded URL literal in {path}: {url_matches}"
        ip_matches = ip_literal_re.findall(src)
        assert not ip_matches, f"Hardcoded IP literal in {path}: {ip_matches}"
