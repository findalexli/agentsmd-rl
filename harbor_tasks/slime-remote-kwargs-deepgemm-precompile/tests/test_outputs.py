"""
Task: slime-remote-kwargs-deepgemm-precompile
Repo: THUDM/slime @ 243d0883b90e407ee56a6a51d2d8d80fe5cae47e
PR:   1765

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
DIST_FILE = f"{REPO}/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py"
ROLLOUT_FILE = f"{REPO}/slime/ray/rollout.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    for fpath in [DIST_FILE, ROLLOUT_FILE]:
        src = Path(fpath).read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_keyword_args_in_remote_call():
    """init_weights_update_group.remote() calls in connect_rollout_engines_from_distributed
    must use keyword arguments for all core params, not positional."""
    script = '''
import ast, sys

DIST_FILE = "/workspace/slime/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py"
src = open(DIST_FILE).read()
tree = ast.parse(src)

target = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == "connect_rollout_engines_from_distributed":
            target = node
            break

if target is None:
    print("FAIL: connect_rollout_engines_from_distributed not found")
    sys.exit(1)

required_kwargs = {"master_address", "master_port", "rank_offset", "world_size", "group_name"}
calls_found = 0
calls_ok = 0

for node in ast.walk(target):
    if not isinstance(node, ast.Call):
        continue
    func = node.func
    if not (isinstance(func, ast.Attribute) and func.attr == "remote"):
        continue
    inner = func.value
    if not (isinstance(inner, ast.Attribute) and inner.attr == "init_weights_update_group"):
        continue

    calls_found += 1
    kw_names = {kw.arg for kw in node.keywords if kw.arg is not None}
    if required_kwargs.issubset(kw_names) and len(node.args) == 0:
        calls_ok += 1

if calls_found == 0:
    print("FAIL: No init_weights_update_group.remote() calls found")
    sys.exit(1)

if calls_found != calls_ok:
    print(f"FAIL: {calls_found - calls_ok}/{calls_found} calls still use positional args")
    sys.exit(1)

print("PASS")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_precompile_default_true():
    """SGLANG_JIT_DEEPGEMM_PRECOMPILE must default to 'true' in start_engines."""
    script = '''
import ast, sys

ROLLOUT = "/workspace/slime/slime/ray/rollout.py"
src = open(ROLLOUT).read()
tree = ast.parse(src)

start_engines = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == "start_engines":
            start_engines = node
            break

if start_engines is None:
    print("FAIL: start_engines not found")
    sys.exit(1)

for node in ast.walk(start_engines):
    if not isinstance(node, ast.Dict):
        continue
    for key, val in zip(node.keys, node.values):
        if key is None:
            continue
        if isinstance(key, ast.Constant) and key.value == "SGLANG_JIT_DEEPGEMM_PRECOMPILE":
            if isinstance(val, ast.Constant) and str(val.value).lower() == "true":
                print("PASS")
                sys.exit(0)
            else:
                actual = val.value if isinstance(val, ast.Constant) else "unknown"
                print(f"FAIL: SGLANG_JIT_DEEPGEMM_PRECOMPILE defaults to '{actual}', expected 'true'")
                sys.exit(1)

print("FAIL: SGLANG_JIT_DEEPGEMM_PRECOMPILE not found in start_engines")
sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_fast_warmup_present():
    """SGLANG_JIT_DEEPGEMM_FAST_WARMUP must be present with default 'true'
    in start_engines."""
    script = '''
import ast, sys

ROLLOUT = "/workspace/slime/slime/ray/rollout.py"
src = open(ROLLOUT).read()
tree = ast.parse(src)

start_engines = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == "start_engines":
            start_engines = node
            break

if start_engines is None:
    print("FAIL: start_engines not found")
    sys.exit(1)

for node in ast.walk(start_engines):
    if not isinstance(node, ast.Dict):
        continue
    for key, val in zip(node.keys, node.values):
        if key is None:
            continue
        if isinstance(key, ast.Constant) and key.value == "SGLANG_JIT_DEEPGEMM_FAST_WARMUP":
            if isinstance(val, ast.Constant) and str(val.value).lower() == "true":
                print("PASS")
                sys.exit(0)
            else:
                actual = val.value if isinstance(val, ast.Constant) else "unknown"
                print(f"FAIL: SGLANG_JIT_DEEPGEMM_FAST_WARMUP defaults to '{actual}', expected 'true'")
                sys.exit(1)

print("FAIL: SGLANG_JIT_DEEPGEMM_FAST_WARMUP not found in start_engines")
sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_env_vars_preserved():
    """Existing env vars in start_engines must still be present."""
    src = Path(ROLLOUT_FILE).read_text()
    tree = ast.parse(src)

    start_engines = _find_method(tree, "start_engines")
    assert start_engines is not None, "start_engines method not found"

    required = {
        "SGL_DISABLE_TP_MEMORY_INBALANCE_CHECK",
        "SGLANG_DISABLE_TP_MEMORY_INBALANCE_CHECK",
        "SGLANG_MEMORY_SAVER_CUDA_GRAPH",
        "SGLANG_BATCH_INVARIANT_OPS_ENABLE_MM_FALLBACK_VARIANT",
    }
    found = set()
    for node in ast.walk(start_engines):
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if key is not None and isinstance(key, ast.Constant) and isinstance(key.value, str):
                    found.add(key.value)

    missing = required - found
    assert not missing, f"Missing env vars: {missing}"


# [pr_diff] pass_to_pass
def test_connect_function_preserved():
    """connect_rollout_engines_from_distributed must exist with non-trivial body."""
    src = Path(DIST_FILE).read_text()
    tree = ast.parse(src)

    func = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "connect_rollout_engines_from_distributed":
                func = node
                break

    assert func is not None, "connect_rollout_engines_from_distributed not found"
    stmts = [n for n in ast.walk(func) if isinstance(n, ast.stmt)]
    assert len(stmts) > 5, f"Function body too small ({len(stmts)} stmts) — likely a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be truncated or replaced with stubs."""
    import os

    dist_size = os.path.getsize(DIST_FILE)
    rollout_size = os.path.getsize(ROLLOUT_FILE)
    assert dist_size > 7000, f"dist file too small ({dist_size} bytes) — likely truncated"
    assert rollout_size > 16000, f"rollout file too small ({rollout_size} bytes) — likely truncated"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_method(tree: ast.AST, name: str):
    """Find a function/method by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node
    return None
