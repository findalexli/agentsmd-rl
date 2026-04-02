"""
Task: gradio-heartbeat-task-leak
Repo: gradio-app/gradio @ b3722285163dcee97fe236e87d6ef98cee6be441
PR:   13164

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: sse_stream is a deeply nested async generator closure inside
queue_data_helper, requiring a full Blocks + Queue + Request setup to call
directly. AST inspection is the practical choice for verifying the fix
pattern (stored task reference + cancel in every exit path).
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
ROUTES = Path(f"{REPO}/gradio/routes.py")


def _parse_sse_stream() -> ast.AsyncFunctionDef:
    """Find and return the sse_stream AST node."""
    tree = ast.parse(ROUTES.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "sse_stream":
            return node
    raise AssertionError("sse_stream function not found in routes.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_routes_syntax():
    """gradio/routes.py must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{ROUTES}').read())"],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error in routes.py:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_heartbeat_task_reference_stored():
    """asyncio.create_task(heartbeat()) result must be stored in a variable.

    The bug: create_task was called as a bare expression (fire-and-forget),
    making cancellation impossible. The fix assigns it to a variable.
    """
    sse = _parse_sse_stream()
    for child in ast.walk(sse):
        if isinstance(child, (ast.Assign, ast.AnnAssign)):
            value = child.value if isinstance(child, ast.Assign) else child.value
            if isinstance(value, ast.Call):
                func = value.func
                # asyncio.create_task(...)
                if isinstance(func, ast.Attribute) and func.attr == "create_task":
                    return  # Found an assignment of create_task → PASS
    raise AssertionError(
        "heartbeat task is not stored in a variable — "
        "asyncio.create_task() is called as a bare expression"
    )


# [pr_diff] fail_to_pass
def test_heartbeat_cancelled_all_exit_paths():
    """heartbeat task must be cancelled in all 3 exit paths.

    sse_stream has three ways to exit:
      1. Client disconnect → return
      2. Normal completion (all events processed) → return
      3. Exception → raise
    Each must cancel the heartbeat task to prevent leaked background tasks.
    Accepts either explicit cancel in each path OR a finally block with cancel.
    """
    sse = _parse_sse_stream()

    # Count cancel() calls on a Name (e.g., heartbeat_task.cancel())
    cancel_count = 0
    has_finally_cancel = False
    for child in ast.walk(sse):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Attribute) and func.attr == "cancel":
                if isinstance(func.value, ast.Name):
                    cancel_count += 1

    # Check for cancel inside a finally block (covers all paths with one call)
    for stmt in sse.body:
        if isinstance(stmt, ast.Try) or (
            hasattr(ast, "TryStar") and isinstance(stmt, ast.TryStar)
        ):
            for final_stmt in getattr(stmt, "finalbody", []):
                for node in ast.walk(final_stmt):
                    if isinstance(node, ast.Call):
                        func = node.func
                        if isinstance(func, ast.Attribute) and func.attr == "cancel":
                            if isinstance(func.value, ast.Name):
                                has_finally_cancel = True

    assert cancel_count >= 3 or has_finally_cancel, (
        f"Only {cancel_count} cancel() call(s) found and no finally-block cancel. "
        f"Need cancel in all 3 exit paths or a single cancel in finally."
    )


# [pr_diff] fail_to_pass
def test_heartbeat_task_created_before_try():
    """heartbeat task must be created before the try block.

    If create_task is inside the try block, the variable won't be defined
    in the except handler if task creation fails. The fix moves it before try.
    """
    sse = _parse_sse_stream()
    # Walk direct children of sse_stream body (not nested)
    create_task_line = None
    try_line = None
    for stmt in sse.body:
        # Look for create_task assignment at top level of sse_stream
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            value = stmt.value if isinstance(stmt, ast.Assign) else stmt.value
            if isinstance(value, ast.Call):
                func = value.func
                if isinstance(func, ast.Attribute) and func.attr == "create_task":
                    create_task_line = stmt.lineno
        if isinstance(stmt, ast.Try) or (
            hasattr(ast, "TryStar") and isinstance(stmt, ast.TryStar)
        ):
            try_line = stmt.lineno

    assert create_task_line is not None, (
        "No create_task assignment found in sse_stream body (top level)"
    )
    assert try_line is not None, "No try block found in sse_stream"
    assert create_task_line < try_line, (
        f"create_task (line {create_task_line}) must come before "
        f"try block (line {try_line})"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_heartbeat_function_exists():
    """The async heartbeat() function must still be defined in routes.py."""
    tree = ast.parse(ROUTES.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "heartbeat":
            return
    raise AssertionError("heartbeat async function not found in routes.py")


# [repo_tests] pass_to_pass
def test_sse_stream_returns_streaming_response():
    """sse_stream must still exist and StreamingResponse must still be used."""
    source = ROUTES.read_text()
    tree = ast.parse(source)

    found_sse = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "sse_stream":
            found_sse = True
            break
    assert found_sse, "sse_stream function not found"
    assert "StreamingResponse" in source, "StreamingResponse no longer used"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ b3722285163dcee97fe236e87d6ef98cee6be441
def test_ruff_format_routes():
    """Python code is formatted with ruff (AGENTS.md line 43)."""
    r = subprocess.run(
        ["ruff", "check", "--select=E,W", str(ROUTES)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff lint errors in routes.py:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
