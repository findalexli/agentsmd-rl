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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_routes_syntax():
    """gradio/routes.py must parse without syntax errors."""
    # Parsing the file is sufficient — ast.parse raises SyntaxError on bad code
    _parse_routes()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_heartbeat_task_reference_stored():
    """asyncio.create_task(heartbeat()) result must be stored in a variable.

    The bug: create_task was called as a bare expression (fire-and-forget),
    making cancellation impossible. The fix assigns it to a variable.
    """
    tree = _parse_routes()
    sse = _find_sse_stream(tree)

    # Look for any assignment of create_task result within sse_stream
    for node in ast.walk(sse):
        if isinstance(node, ast.Assign):
            value = node.value
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                if value.func.attr == "create_task":
                    # Verify the variable name is meaningful (not _)
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id != "_":
                            return  # PASS: create_task result stored
    raise AssertionError(
        "heartbeat task is not stored in a named variable — "
        "asyncio.create_task() is called as a bare expression (fire-and-forget)"
    )


# [pr_diff] fail_to_pass
def test_heartbeat_cancelled_all_exit_paths():
    """heartbeat task must be cancelled in all 3 exit paths.

    sse_stream has three ways to exit:
      1. Client disconnect (is_disconnected) -> return
      2. Normal completion (all events processed) -> return
      3. Exception (BaseException) -> raise
    Each must cancel the heartbeat task to prevent leaked background tasks.
    Accepts either explicit cancel in each path OR a finally block.
    """
    tree = _parse_routes()
    sse = _find_sse_stream(tree)

    # Count .cancel() calls on a Name node (e.g., heartbeat_task.cancel())
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

    assert cancel_count >= 3 or has_finally_cancel, (
        f"Found {cancel_count} cancel() call(s) and no finally-block cancel. "
        f"Need cancel in all 3 exit paths (disconnect, completion, exception) "
        f"or a single cancel in a finally block."
    )


# [pr_diff] fail_to_pass
def test_heartbeat_task_created_before_try():
    """create_task must be placed before the try block.

    If create_task is inside the try block, the variable won't be defined
    in the except handler if an error occurs before task creation.
    The fix moves create_task above the try statement.
    """
    tree = _parse_routes()
    sse = _find_sse_stream(tree)

    create_task_line = None
    try_line = None

    # Scan direct children of sse_stream body (not nested)
    for stmt in sse.body:
        if isinstance(stmt, ast.Assign):
            value = stmt.value
            if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                if value.func.attr == "create_task":
                    create_task_line = stmt.lineno
        if isinstance(stmt, ast.Try):
            try_line = stmt.lineno

    assert create_task_line is not None, (
        "No create_task assignment found at top level of sse_stream body"
    )
    assert try_line is not None, "No try block found in sse_stream"
    assert create_task_line < try_line, (
        f"create_task (line {create_task_line}) must appear before "
        f"try block (line {try_line})"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression checks
# ---------------------------------------------------------------------------

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


# [static] pass_to_pass
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


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

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
