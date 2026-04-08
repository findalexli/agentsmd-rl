"""
Task: vllm-rocm-aiter-state-leak
Repo: vllm-project/vllm @ 0aac2048bf3a7e60eaddf1ebcb4165ed777eb8ff
PR:   20255

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests use subprocess to execute behavioral simulations of the state-leak
pattern AND structural AST verification of the actual fix. The target modules
require torch + ROCm GPU, so we cannot import them directly; instead we
simulate the class-level caching pattern and verify the fix addresses it.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vllm"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet via subprocess in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """All three modified files must parse without errors."""
    r = _run_py("""
import ast, sys
files = [
    "tests/kernels/moe/test_shared_fused_moe_routed_transform.py",
    "tests/kernels/moe/test_routing_simulator.py",
    "vllm/distributed/parallel_state.py",
]
for f in files:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f"FAIL: {f}: {e}", file=sys.stderr)
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_rocm_env_setup_not_gated_on_use_rocm_aiter():
    """AITER env-var setup runs for all ROCm cases, not just use_rocm_aiter=True.

    Behavioral: simulate a test param loop where use_rocm_aiter=False needs
    env vars set too. Structural: verify the AST condition no longer includes
    use_rocm_aiter as a gate.
    """
    r = _run_py("""
import ast, os, sys

# --- Behavioral simulation ---
# Simulate the bug: env setup is only run when use_rocm_aiter is True.
# This means a False case inherits stale env vars from a prior True case.
os.environ["VLLM_ROCM_USE_AITER"] = "1"
os.environ["VLLM_ROCM_USE_AITER_MOE"] = "1"

# Bug behavior: when use_rocm_aiter=False, env vars are NOT reset,
# so stale "1" values survive from the prior test.
use_rocm_aiter = False
# Simulate the buggy code: only set env vars when use_rocm_aiter is True
if False:  # represents: if current_platform.is_rocm() and use_rocm_aiter:
    os.environ["VLLM_ROCM_USE_AITER"] = "0"
    os.environ["VLLM_ROCM_USE_AITER_MOE"] = "0"

# Stale values survive — this IS the bug
assert os.environ.get("VLLM_ROCM_USE_AITER") == "1", "stale state should persist (bug demo)"

# Now simulate the fix: env vars are always set regardless of use_rocm_aiter
# (the gate on use_rocm_aiter is removed, only is_rocm() remains)
if True:  # represents: if current_platform.is_rocm():
    os.environ["VLLM_ROCM_USE_AITER"] = "1" if use_rocm_aiter else "0"
    os.environ["VLLM_ROCM_USE_AITER_MOE"] = "1" if use_rocm_aiter else "0"

# Fix works: env vars now correctly reflect use_rocm_aiter=False
assert os.environ["VLLM_ROCM_USE_AITER"] == "0", "fix should reset to 0"
assert os.environ["VLLM_ROCM_USE_AITER_MOE"] == "0", "fix should reset to 0"

# --- Structural verification ---
tree = ast.parse(open("tests/kernels/moe/test_shared_fused_moe_routed_transform.py").read())
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "test_routed_input_transform_inside_vs_outside":
        func = node
        break
assert func is not None, "test function not found"

for child in ast.walk(func):
    if not isinstance(child, ast.If):
        continue
    has_setenv = any(
        isinstance(sub, ast.Call)
        and isinstance(sub.func, ast.Attribute)
        and sub.func.attr == "setenv"
        for sub in ast.walk(child)
    )
    if has_setenv:
        cond_names = {n.id for n in ast.walk(child.test) if isinstance(n, ast.Name)}
        assert "use_rocm_aiter" not in cond_names, "env-var setup still gated on use_rocm_aiter"
        break

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_cleanup_calls_refresh_env_variables():
    """cleanup_dist_env_and_memory calls refresh_env_variables() to reset AITER state.

    Behavioral: simulate the class-level caching pattern where env vars are
    read at construction time and cached. Verify that refresh_env_variables()
    resets the cached state to match current os.environ.
    Structural: verify the AST contains the call.
    """
    r = _run_py("""
import ast, os, sys

# --- Behavioral simulation of the state-leak pattern ---
class SimulatedAiterOps:
    # Simulates rocm_aiter_ops: caches env vars as class-level state.
    def __init__(self):
        self._refresh()

    def _refresh(self):
        self.use_aiter = os.environ.get("VLLM_ROCM_USE_AITER", "0") == "1"
        self.use_aiter_moe = os.environ.get("VLLM_ROCM_USE_AITER_MOE", "0") == "1"

    def refresh_env_variables(self):
        self._refresh()

# Test 1: enable AITER
os.environ["VLLM_ROCM_USE_AITER"] = "1"
ops = SimulatedAiterOps()
assert ops.use_aiter is True, "should be True after enabling"

# Test 2: disable AITER — WITHOUT refresh (the bug)
os.environ["VLLM_ROCM_USE_AITER"] = "0"
assert ops.use_aiter is True, "BUG: stale cached True survives across tests"

# Cleanup with refresh (the fix)
ops.refresh_env_variables()
assert ops.use_aiter is False, "FIX: refresh resets cached state to match env"

# --- Structural verification ---
tree = ast.parse(open("vllm/distributed/parallel_state.py").read())
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "cleanup_dist_env_and_memory":
        func = node
        break
assert func is not None, "cleanup_dist_env_and_memory not found"

call_attrs = set()
for child in ast.walk(func):
    if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
        call_attrs.add(child.func.attr)
assert "refresh_env_variables" in call_attrs, "refresh_env_variables() not called"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_routing_simulator_no_direct_dict_mutation():
    """test_routing_strategy_integration does not directly mutate environment_variables dict.

    Behavioral: demonstrate that direct dict mutation survives teardown while
    monkeypatch.setitem is auto-restored. Structural: verify no Subscript
    assignment to environment_variables in the AST.
    """
    r = _run_py("""
import ast, sys

# --- Behavioral simulation ---
# Direct dict mutation (the bug pattern):
shared_dict = {"VLLM_MOE_ROUTING_SIMULATION_STRATEGY": "default"}
shared_dict["VLLM_MOE_ROUTING_SIMULATION_STRATEGY"] = "hashcvt"
# No automatic restore — value stays "hashcvt" after test teardown
assert shared_dict["VLLM_MOE_ROUTING_SIMULATION_STRATEGY"] == "hashcvt"
# This would pollute the next test

# monkeypatch.setitem pattern (the fix):
# In real pytest, monkeypatch.setitem restores the original at teardown.
# Simulate by saving/restoring:
original = shared_dict.copy()
shared_dict["VLLM_MOE_ROUTING_SIMULATION_STRATEGY"] = "hashcvt"
# teardown restores:
shared_dict.update(original)
assert shared_dict["VLLM_MOE_ROUTING_SIMULATION_STRATEGY"] == "default"

# --- Structural verification ---
tree = ast.parse(open("tests/kernels/moe/test_routing_simulator.py").read())
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "test_routing_strategy_integration":
        func = node
        break
assert func is not None, "test_routing_strategy_integration not found"

for child in ast.walk(func):
    if isinstance(child, ast.Assign):
        for target in child.targets:
            if (isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Attribute)
                and target.value.attr == "environment_variables"):
                raise AssertionError("Direct dict mutation of environment_variables still present")

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


def test_cleanup_retains_existing_calls():
    """cleanup_dist_env_and_memory still calls disable_envs_cache() and gc.unfreeze()."""
    r = _run_py("""
import ast, sys

tree = ast.parse(open("vllm/distributed/parallel_state.py").read())
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "cleanup_dist_env_and_memory":
        func = node
        break
assert func is not None, "function not found"

call_attrs = set()
for child in ast.walk(func):
    if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
        call_attrs.add(child.func.attr)

assert "disable_envs_cache" in call_attrs, "Missing call to disable_envs_cache()"
assert "unfreeze" in call_attrs, "Missing call to gc.unfreeze()"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_aiter_env_var_names_present():
    """Test file still references both VLLM_ROCM_USE_AITER and VLLM_ROCM_USE_AITER_MOE."""
    r = _run_py("""
import ast, sys

tree = ast.parse(open("tests/kernels/moe/test_shared_fused_moe_routed_transform.py").read())

found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if node.value in ("VLLM_ROCM_USE_AITER", "VLLM_ROCM_USE_AITER_MOE"):
            found.add(node.value)

assert "VLLM_ROCM_USE_AITER" in found, "Missing VLLM_ROCM_USE_AITER string"
assert "VLLM_ROCM_USE_AITER_MOE" in found, "Missing VLLM_ROCM_USE_AITER_MOE string"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Anti-stub (static) — verify meaningful implementation
# ---------------------------------------------------------------------------


def test_cleanup_not_stub():
    """cleanup_dist_env_and_memory has meaningful code, not emptied out."""
    r = _run_py("""
import ast, sys

tree = ast.parse(open("vllm/distributed/parallel_state.py").read())
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "cleanup_dist_env_and_memory":
        func = node
        break
assert func is not None, "function not found"

stmt_types = (ast.Assign, ast.Call, ast.If, ast.Import, ast.ImportFrom, ast.Return, ast.Expr)
stmts = sum(1 for child in ast.walk(func) if isinstance(child, stmt_types))
# Base version has ~10 statements; fix adds ~3-5 more
assert stmts >= 8, f"cleanup body too small ({stmts} statements), likely a stub"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
