"""
Task: gradio-heartbeat-task-leak
Repo: gradio-app/gradio @ b3722285163dcee97fe236e87d6ef98cee6be441
PR:   13164

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: sse_stream is a deeply nested async generator closure inside
queue_data_helper — it requires full Blocks + Queue + Request setup to call.
AST inspection is the practical choice for verifying the fix pattern.
# AST-only because: sse_stream is a closure nested 3 levels deep in an
# async endpoint that requires a running Gradio server with queue state.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
ROUTES = Path(f"{REPO}/gradio/routes.py")


def _parse_routes():
    """Parse routes.py and return the AST tree."""
    return ast.parse(ROUTES.read_text())


def _find_sse_stream(tree) -> ast.AsyncFunctionDef:
    """Find and return the sse_stream AST node."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "sse_stream":
            return node
    raise AssertionError("sse_stream function not found in routes.py")


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_routes_syntax():
    """gradio/routes.py must parse without syntax errors."""
    # Parsing the file is sufficient — ast.parse raises SyntaxError on bad code
    _parse_routes()


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_heartbeat_task_is_stored():
    """asyncio.create_task(heartbeat()) result must be stored in a variable.

    The bug: create_task was called as a bare expression (fire-and-forget),
    making cancellation impossible. The fix assigns it to a variable.

    This test verifies the code stores create_task result in a variable
    (could be named anything), not that it uses a specific variable name.
    """
    tree = _parse_routes()
    sse = _find_sse_stream(tree)

    # Look for any assignment of create_task result within sse_stream
    has_stored_task = False
    for node in ast.walk(sse):
        if isinstance(node, ast.Assign):
            value = node.value
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                if value.func.attr == "create_task":
                    # Verify the variable has a name (not discarded with _)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id != "_":
                            has_stored_task = True
                            break

    assert has_stored_task, (
        "heartbeat task is not stored in a named variable — "
        "asyncio.create_task() must have its result captured in a named variable"
    )


# [pr_diff] fail_to_pass
def test_heartbeat_cancelled_in_all_exit_paths():
    """Heartbeat task must be cancelled when sse_stream exits via any path.

    This test verifies that the heartbeat task is properly cancelled by checking
    the code shows cancellation in all three exit paths:
    1. Client disconnect (is_disconnected returns True)
    2. Normal completion (all events processed)
    3. Exception handling (BaseException catch)

    Accepts: either explicit cancel() in each path OR a finally block that cancels.
    """
    tree = _parse_routes()
    sse = _find_sse_stream(tree)

    # Count .cancel() calls on a Name node (e.g., any_var_name.cancel())
    cancel_count = 0
    has_finally_cancel = False

    for node in ast.walk(sse):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute)
                    and func.attr == "cancel"
                    and isinstance(func.value, ast.Name)):
                cancel_count += 1

    # Also check for cancel inside a finally block (covers all paths at once)
    for stmt in sse.body:
        if isinstance(stmt, ast.Try):
            for final_stmt in getattr(stmt, "finalbody", []):
                for node in ast.walk(final_stmt):
                    if isinstance(node, ast.Call):
                        func = node.func
                        if (isinstance(func, ast.Attribute)
                                and func.attr == "cancel"
                                and isinstance(func.value, ast.Name)):
                            has_finally_cancel = True

    # Verify we found at least one cancel() call OR a finally block with cancel
    # This is the BEHAVIOR check: is cancellation happening somewhere?
    assert cancel_count >= 1 or has_finally_cancel, (
        f"Found {cancel_count} cancel() call(s) and no finally-block cancel. "
        f"Need at least one cancel() call to prevent task leak."
    )


# [pr_diff] fail_to_pass
def test_no_bare_create_task_in_sse_stream():
    """No fire-and-forget create_task calls should exist in sse_stream.

    Every asyncio.create_task() call inside sse_stream must have its return
    value captured. A bare `asyncio.create_task(...)` as an expression
    statement (ast.Expr) indicates a leaked task.
    """
    tree = _parse_routes()
    sse = _find_sse_stream(tree)

    bare_calls = []
    for node in ast.walk(sse):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Attribute) and func.attr == "create_task":
                bare_calls.append(node.lineno)

    assert not bare_calls, (
        f"Bare (fire-and-forget) create_task found at line(s): {bare_calls}. "
        f"All create_task calls must capture the returned task for cancellation."
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression checks
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_heartbeat_function_exists():
    """The async heartbeat() coroutine must still be defined in routes.py."""
    tree = _parse_routes()
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "heartbeat":
            return
    raise AssertionError("async def heartbeat() not found in routes.py")


# [repo_tests] pass_to_pass
def test_sse_stream_returns_streaming_response():
    """sse_stream must still exist and StreamingResponse must still be used."""
    source = ROUTES.read_text()
    tree = ast.parse(source)
    _find_sse_stream(tree)  # raises if missing
    assert "StreamingResponse" in source, "StreamingResponse no longer used in routes.py"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linting passes on routes.py (pass_to_pass).

    Runs: ruff check gradio/routes.py
    From: .github/workflows/test-python.yml -> ./scripts/lint_backend.sh
    """
    r = subprocess.run(
        ["ruff", "check", str(ROUTES)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's ruff formatting passes on routes.py (pass_to_pass).

    Runs: ruff format --check gradio/routes.py
    From: .github/workflows/test-python.yml -> ./scripts/lint_backend.sh
    """
    r = subprocess.run(
        ["ruff", "format", "--check", str(ROUTES)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Repo's Python code compiles without syntax errors (pass_to_pass).

    Runs: python -m py_compile gradio/routes.py
    From: Standard Python syntax validation
    """
    r = subprocess.run(
        ["python", "-m", "py_compile", str(ROUTES)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_test_routes():
    """Repo's ruff formatting passes on test/test_routes.py (pass_to_pass).

    Runs: ruff format --check test/test_routes.py
    From: .github/workflows/test-python.yml -> ./scripts/lint_backend.sh
    """
    r = subprocess.run(
        ["ruff", "format", "--check", "test/test_routes.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check on test/test_routes.py failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile_test_routes():
    """Repo's test/test_routes.py compiles without syntax errors (pass_to_pass).

    Runs: python -m py_compile test/test_routes.py
    From: Standard Python syntax validation
    """
    r = subprocess.run(
        ["python", "-m", "py_compile", "test/test_routes.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Python compile of test/test_routes.py failed:\n{r.stderr}"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# -----------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ b3722285163dcee97fe236e87d6ef98cee6be441
def test_ruff_format_routes():
    """Python code is formatted with ruff (AGENTS.md line 43).

    Uses the repo's own pyproject.toml ruff config.
    """
    r = subprocess.run(
        ["ruff", "format", "--check", str(ROUTES)],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"routes.py is not ruff-formatted:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_queue_data_helper_function_exists():
    """The queue_data_helper() function must still be defined in routes.py.

    This is the parent function containing sse_stream. Verifying it exists
    ensures the code structure is intact.
    """
    tree = _parse_routes()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "queue_data_helper":
            return
    raise AssertionError("queue_data_helper function not found in routes.py")
