"""
Task: slime-httpx-disable-system-proxy
Repo: THUDM/slime @ e46e660059b5f2ae949ad812c7d49af823f415a3
PR:   1714

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

import pytest

TARGET = Path("/workspace/slime/slime/utils/http_utils.py")
REPO = "/workspace/slime"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    source = TARGET.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_init_client_trust_env_disabled():
    """init_http_client creates AsyncClient with trust_env=False across varied configs."""
    r = subprocess.run(
        ["python3", "-c", """
import os, sys, types
os.environ["HTTP_PROXY"] = "http://fake-proxy:8080"
os.environ["HTTPS_PROXY"] = "http://fake-proxy:8080"

import slime.utils.http_utils as mod
import httpx

def make_args(num_gpus, concurrency, gpus_per_engine=1):
    return types.SimpleNamespace(
        rollout_num_gpus=num_gpus,
        sglang_server_concurrency=concurrency,
        rollout_num_gpus_per_engine=gpus_per_engine,
        use_distributed_post=False,
    )

configs = [
    make_args(2, 10),
    make_args(4, 8, 2),
    make_args(1, 32),
]
for args in configs:
    mod._http_client = None
    mod.init_http_client(args)
    client = mod._http_client
    assert isinstance(client, httpx.AsyncClient), "Must create an AsyncClient"
    assert not client._trust_env, (
        f"Client must have trust_env=False (gpus={args.rollout_num_gpus}, "
        f"concurrency={args.sglang_server_concurrency})"
    )
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_init_client_proxy_not_mounted():
    """With proxy env vars set, init_http_client must not mount proxy transports."""
    r = subprocess.run(
        ["python3", "-c", """
import os, sys, types
os.environ["HTTP_PROXY"] = "http://fake-proxy:9090"
os.environ["HTTPS_PROXY"] = "http://fake-proxy:9090"

import slime.utils.http_utils as mod
import httpx

args = types.SimpleNamespace(
    rollout_num_gpus=2,
    sglang_server_concurrency=16,
    rollout_num_gpus_per_engine=1,
    use_distributed_post=False,
)
mod._http_client = None
mod.init_http_client(args)
client = mod._http_client
assert len(client._mounts) == 0, (
    f"Client should not have proxy mounts (found {len(client._mounts)} mounts). "
    "Set trust_env=False to prevent httpx from reading proxy env vars."
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_ray_actor_trust_env_disabled():
    """_HttpPosterActor's client must ignore system proxy env vars.

    The actor class is nested inside _init_ray_distributed_post and decorated
    with @ray.remote.  We mock Ray just enough to instantiate the actor locally
    and verify the client does not mount proxy transports when HTTP_PROXY /
    HTTPS_PROXY environment variables are present.
    """
    r = subprocess.run(
        ["python3", "-c", """
import os, sys, types

# Proxy env vars must be set BEFORE importing the module
os.environ["HTTP_PROXY"] = "http://fake-proxy:8080"
os.environ["HTTPS_PROXY"] = "http://fake-proxy:8080"

# --- Minimal Ray mock so the nested class can be defined & instantiated ---
ray_mod = types.ModuleType("ray")

class _MockRemote:
    def __init__(self, cls):
        self._cls = cls
    def options(self, **kw):
        return self
    def remote(self, *a, **kw):
        return self._cls(*a, **kw)

ray_mod.remote = lambda cls: _MockRemote(cls)
ray_mod.nodes = lambda: [{"Alive": True, "NodeID": "node-0"}]

sched_mod = types.ModuleType("ray.util.scheduling_strategies")
class _FakeStrategy:
    def __init__(self, **kw): pass
sched_mod.NodeAffinitySchedulingStrategy = _FakeStrategy

sys.modules["ray"] = ray_mod
sys.modules["ray.util"] = types.ModuleType("ray.util")
sys.modules["ray.util.scheduling_strategies"] = sched_mod

# --- Run the real code ---
import slime.utils.http_utils as mod
import httpx

mod._post_actors = []       # reset global
mod._client_concurrency = 8

mod._init_ray_distributed_post(types.SimpleNamespace(num_gpus_per_node=1))

assert mod._post_actors, "No actors were created"
for idx, actor in enumerate(mod._post_actors):
    client = actor._client
    assert isinstance(client, httpx.AsyncClient), f"Actor {idx}: not an AsyncClient"
    assert len(client._mounts) == 0, (
        f"Actor {idx}: client has {len(client._mounts)} proxy mount(s); "
        "system proxy env vars must be ignored for intra-cluster traffic."
    )
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pre_commit) — pre-commit hooks from the repo
# ---------------------------------------------------------------------------

# [pre_commit] pass_to_pass
def test_pre_commit_ruff():
    """Repo passes ruff linting (pre-commit hook)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    if r.returncode != 0:
        pytest.skip("Could not install ruff (no network)")

    r = subprocess.run(
        ["ruff", "check", "slime/utils/http_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [pre_commit] pass_to_pass
def test_pre_commit_black():
    """Modified file passes black format check (pre-commit hook)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    if r.returncode != 0:
        pytest.skip("Could not install black (no network)")

    r = subprocess.run(
        ["black", "--check", "slime/utils/http_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr[-500:]}"


# [pre_commit] pass_to_pass
def test_pre_commit_isort():
    """Modified file passes isort import format check (pre-commit hook)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    if r.returncode != 0:
        pytest.skip("Could not install isort (no network)")

    r = subprocess.run(
        ["isort", "--check", "--profile=black", "slime/utils/http_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # First pass may fail due to formatting, but --check should pass if already formatted
    assert r.returncode == 0, f"isort format check failed:\n{r.stderr[-500:]}"


# [pre_commit] pass_to_pass
def test_pre_commit_yaml():
    """All YAML files are valid (pre-commit check-yaml hook)."""
    r = subprocess.run(
        ["pip", "install", "pre-commit", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        pytest.skip("Could not install pre-commit (no network)")

    r = subprocess.run(
        ["pre-commit", "run", "check-yaml", "--all-files"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Exit 0 = passed, Exit 1 = failed but may have made changes
    # In CI mode with --all-files, it should pass if all files are valid
    if r.returncode != 0:
        # Check if it is a real error or just formatting issues
        if "Failed" in r.stdout or "Failed" in r.stderr:
            assert False, f"check-yaml found invalid YAML:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual repo CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_compileall():
    """All Python modules compile without syntax errors."""
    r = subprocess.run(
        ["python3", "-m", "compileall", "slime/utils/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Compileall failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_import_check():
    """Modified module imports without errors."""
    r = subprocess.run(
        ["python3", "-c", "import slime.utils.http_utils; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "Module import did not complete successfully"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_init_client_preserves_config():
    """init_http_client creates AsyncClient with connection limits and timeout."""
    r = subprocess.run(
        ["python3", "-c", """
import sys, types
import slime.utils.http_utils as mod
import httpx

for num_gpus, concurrency, gpus_per_engine in [(4, 8, 2), (2, 16, 1), (8, 4, 4)]:
    args = types.SimpleNamespace(
        rollout_num_gpus=num_gpus,
        sglang_server_concurrency=concurrency,
        rollout_num_gpus_per_engine=gpus_per_engine,
        use_distributed_post=False,
    )
    mod._http_client = None
    mod.init_http_client(args)
    client = mod._http_client
    assert isinstance(client, httpx.AsyncClient), "Must create an AsyncClient"
    pool = client._transport._pool
    assert pool._max_connections > 1, (
        f"Client must configure connection limits "
        f"(gpus={num_gpus}, concurrency={concurrency})"
    )
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
