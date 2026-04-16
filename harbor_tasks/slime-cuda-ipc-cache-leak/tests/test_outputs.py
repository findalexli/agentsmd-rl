"""
Task: slime-cuda-ipc-cache-leak
Repo: THUDM/slime @ 08b201bd576e02fba08dae22e5c9324643e88884
PR:   1731

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/slime"
TARGET = f"{REPO}/slime/backends/megatron_utils/update_weight/update_weight_from_tensor.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_target():
    """Parse the target file and return the AST tree."""
    src = Path(TARGET).read_text()
    return ast.parse(src), src


def _find_function(tree, name):
    """Find a function/method by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _del_or_none_assignments_in_loop(func_ast):
    """Find all variable names that are deleted or assigned None inside the
    outermost for-loop body of update_weights (the weight-chunk loop)."""
    # Locate the outermost for-loop inside the function
    loop_node = None
    for node in func_ast.body:
        if isinstance(node, ast.For):
            loop_node = node
            break

    if loop_node is None:
        return set()

    released = set()
    for child in ast.walk(loop_node):
        # del statement
        if isinstance(child, ast.Delete):
            for t in child.targets:
                if isinstance(t, ast.Name):
                    released.add(t.id)
                elif isinstance(t, ast.Tuple):
                    for elt in t.elts:
                        if isinstance(elt, ast.Name):
                            released.add(elt.id)
        # assignment to None:  x = None  or  x, y = None, None
        elif isinstance(child, ast.Assign):
            if isinstance(child.value, ast.Constant) and child.value.value is None:
                for t in child.targets:
                    if isinstance(t, ast.Name):
                        released.add(t.id)
                    elif isinstance(t, ast.Tuple):
                        for elt in t.elts:
                            if isinstance(elt, ast.Name):
                                released.add(elt.id)
    return released


# Script that mock-executes update_weights and prints an ordered event log as JSON.
# Passed to subprocess as `python3 -c <script> <target_path> <num_chunks>`.
_MOCK_SCRIPT = textwrap.dedent("""\
import sys, ast, textwrap, json
from unittest.mock import MagicMock

target_path = sys.argv[1]
num_chunks = int(sys.argv[2])

src = open(target_path).read()
tree = ast.parse(src)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "update_weights":
        func_node = node
        break
assert func_node is not None, "update_weights not found"

# Extract function source (skip @torch.no_grad() decorator)
lines = src.splitlines()
func_lines = lines[func_node.lineno - 1 : func_node.end_lineno]
func_src = textwrap.dedent('\\n'.join(func_lines))

# Build mock namespace matching the function's global references
torch_mock = MagicMock()
ray_mock = MagicMock()
dist_mock = MagicMock()
gloo_group = MagicMock()
pp_weights = MagicMock()

events = []
torch_mock.cuda.ipc_collect.side_effect = lambda: events.append("ipc_collect")
dist_mock.barrier.side_effect = lambda **kw: events.append("barrier")
dist_mock.get_rank.return_value = 1   # non-zero rank -> skip rank-0 blocks
ray_mock.get.side_effect = lambda refs: events.append("ray_get")

ns = {
    'torch': torch_mock,
    'ray': ray_mock,
    'dist': dist_mock,
    'get_gloo_group': gloo_group,
    'post_process_weights': pp_weights,
}

exec(func_src, ns)

# Build mock self with controllable weight chunks
mock_self = MagicMock()
mock_self.weight_version = 0
mock_self.quantization_config = None
mock_self.rollout_engines = []
mock_self.use_distribute = False
chunks = [{"w": MagicMock()} for _ in range(num_chunks)]
mock_self._hf_weight_iterator.get_hf_weight_chunks.return_value = chunks
mock_self._send_hf_params.return_value = ([], MagicMock())

ns['update_weights'](mock_self)
print(json.dumps(events))
""")


def _mock_execute_update_weights(num_chunks: int = 2) -> list[str]:
    """Mock-execute update_weights via subprocess and return ordered event log.

    Events are strings like "barrier", "ray_get", "ipc_collect".
    """
    r = subprocess.run(
        ["python3", "-c", _MOCK_SCRIPT, TARGET, str(num_chunks)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Mock execution failed: {r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    tree, _ = _parse_target()
    assert tree is not None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess mock-execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ipc_collect_in_loop():
    """torch.cuda.ipc_collect() must be called inside the weight chunk for-loop
    to release IPC cache entries after each chunk."""
    events = _mock_execute_update_weights(num_chunks=2)
    barrier_indices = [i for i, e in enumerate(events) if e == "barrier"]
    assert len(barrier_indices) >= 2, (
        f"Expected >= 2 barrier calls, got {len(barrier_indices)}; events: {events}"
    )
    # The weight-update loop runs between the first and second barrier calls
    loop_events = events[barrier_indices[0] + 1 : barrier_indices[1]]
    ipc_in_loop = loop_events.count("ipc_collect")
    assert ipc_in_loop >= 2, (
        f"Expected >= 2 ipc_collect calls in loop (one per chunk), got {ipc_in_loop}. "
        f"Loop events: {loop_events}"
    )


# [pr_diff] fail_to_pass
def test_ipc_collect_after_barrier():
    """torch.cuda.ipc_collect() must be called after the post-loop dist.barrier()
    to clean up the last chunk's IPC entries for non-source ranks."""
    events = _mock_execute_update_weights(num_chunks=2)
    barrier_indices = [i for i, e in enumerate(events) if e == "barrier"]
    assert len(barrier_indices) >= 2, (
        f"Expected >= 2 barrier calls, got {len(barrier_indices)}; events: {events}"
    )
    # Post-loop section: between the second barrier and the third (or end)
    post_start = barrier_indices[1] + 1
    post_end = barrier_indices[2] if len(barrier_indices) > 2 else len(events)
    post_events = events[post_start:post_end]
    ipc_after = post_events.count("ipc_collect")
    assert ipc_after >= 1, (
        f"Expected >= 1 ipc_collect after post-loop barrier, got {ipc_after}. "
        f"Post-loop events: {post_events}, all events: {events}"
    )


# [pr_diff] fail_to_pass
def test_tensors_released_in_loop():
    """GPU tensors created per chunk (the send result and iteration variable) must
    be released inside the weight-chunk loop so the CUDA caching allocator can
    reclaim memory blocks.

    This test checks that the loop body contains at least two distinct release
    operations (del or assignment to None) for variables that originate from the
    weight-chunk send.  A correct fix may use any variable naming; the test
    checks the structural pattern (at least two releases inside the loop body).
    """
    tree, _ = _parse_target()
    func = _find_function(tree, "update_weights")
    assert func is not None, "update_weights function not found"

    released = _del_or_none_assignments_in_loop(func)
    assert len(released) >= 2, (
        f"Expected at least 2 release operations (del or =None) inside the weight-chunk loop, "
        f"but found only {len(released)}: {sorted(released)}. "
        f"GPU tensors from each chunk (send result + iteration var) must be explicitly released."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """update_weights must have a substantial body (not a stub)."""
    tree, _ = _parse_target()
    func = _find_function(tree, "update_weights")
    assert func is not None, "update_weights function not found"

    body_count = sum(
        1 for s in func.body
        if not (
            isinstance(s, ast.Pass)
            or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
        )
    )
    assert body_count > 5, f"update_weights has only {body_count} statements (need >5)"


# [static] pass_to_pass
def test_send_hf_params_exists():
    """_send_hf_params method must still exist (not deleted or renamed)."""
    tree, _ = _parse_target()
    func = _find_function(tree, "_send_hf_params")
    assert func is not None, "_send_hf_params method not found"


# [repo_tests] pass_to_pass
def test_send_to_colocated_engine_structure():
    """_send_to_colocated_engine must retain its tuple return signature."""
    tree, _ = _parse_target()
    func = _find_function(tree, "_send_to_colocated_engine")
    assert func is not None, "_send_to_colocated_engine not found"

    has_tuple_return = any(
        isinstance(child, ast.Return) and isinstance(child.value, ast.Tuple)
        for child in ast.walk(func)
    )
    assert has_tuple_return, "_send_to_colocated_engine missing tuple return"


# [static] pass_to_pass
def test_ray_and_dist_integration():
    """Core distributed integration (ray.get, dist.barrier) must be intact."""
    _, src = _parse_target()
    assert "ray.get" in src, "ray.get call missing from source"
    assert "dist.barrier" in src, "dist.barrier call missing from source"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks (enriched)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linting passes on target directory (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "slime/backends/megatron_utils/update_weight/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Repo's black formatting passes on target directory (pass_to_pass)."""
    r = subprocess.run(
        ["black", "--check", "slime/backends/megatron_utils/update_weight/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_imports():
    """Repo's isort import ordering passes on target directory (pass_to_pass)."""
    r = subprocess.run(
        ["isort", "--check", "slime/backends/megatron_utils/update_weight/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_autoflake_unused_imports():
    """Repo's autoflake check for unused imports passes on target directory (pass_to_pass)."""
    r = subprocess.run(
        ["autoflake", "--check", "--remove-all-unused-imports", "-r", "slime/backends/megatron_utils/update_weight/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"autoflake unused imports check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - CI enrichment
def test_repo_python_syntax():
    """Target file has valid Python syntax (pass_to_pass). CI enrichment."""
    r = subprocess.run(
        ["python", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - CI enrichment
def test_repo_pyproject_toml_valid():
    """pyproject.toml is valid TOML and parseable (pass_to_pass). CI enrichment."""
    r = subprocess.run(
        ["python", "-c", f"import tomllib; tomllib.load(open('{REPO}/pyproject.toml', 'rb'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr[-500:]}"
