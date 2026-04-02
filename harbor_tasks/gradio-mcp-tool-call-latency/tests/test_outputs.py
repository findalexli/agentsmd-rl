"""
Task: gradio-mcp-tool-call-latency
Repo: gradio-app/gradio @ b1f62c0ebc09be80aee830e26689ab70b939cf44
PR:   12961

Bug: MCP call_tool routes ALL events through HTTP loopback (~4s overhead).
Fix: For non-queued events, call blocks.process_api() directly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/mcp.py"


def _get_call_tool_node():
    """Parse mcp.py and return the call_tool AST node."""
    # AST-only because: call_tool is a closure inside create_mcp_server,
    # decorated with @server.call_tool(). Cannot be called without a full
    # Gradio Blocks + MCP server setup.
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "call_tool":
                return node
    return None


def _collect_names(node):
    """Collect all Name and Attribute references in an AST subtree."""
    names = set()
    attrs = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
        if isinstance(child, ast.Attribute):
            attrs.add(child.attr)
    return names, attrs


def _find_if_branch(node, test_pattern):
    """
    Find an If node in the call_tool body whose test matches a pattern.
    Returns (if_body, else_body) or (None, None).
    """
    for child in ast.walk(node):
        if isinstance(child, ast.If):
            test_src = ast.dump(child.test)
            if test_pattern in test_src:
                return child.body, child.orelse
    return None, None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """mcp.py must be syntactically valid Python."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# [static] pass_to_pass
def test_module_imports():
    """gradio.mcp module must import without errors."""
    sys.path.insert(0, REPO)
    from gradio import mcp  # noqa: F401


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_nonqueued_calls_process_api():
    """Non-queued (queue=False) call_tool must use blocks.process_api() directly.

    AST-only because: call_tool is a @server.call_tool() closure inside
    create_mcp_server — cannot be invoked without full Gradio+MCP server.
    """
    call_tool = _get_call_tool_node()
    assert call_tool is not None, "call_tool function not found in mcp.py"

    # Find `if not block_fn.queue:` branch
    nonqueued_body, queued_body = _find_if_branch(call_tool, "block_fn")
    assert nonqueued_body is not None, (
        "No `if ... block_fn.queue ...` branch found in call_tool — "
        "must branch on block_fn.queue to separate queued/non-queued paths"
    )

    # Verify process_api is called in the non-queued branch
    nonqueued_names, nonqueued_attrs = set(), set()
    for stmt in nonqueued_body:
        _, a = _collect_names(stmt)
        nonqueued_attrs.update(a)
    assert "process_api" in nonqueued_attrs, (
        "process_api not called in the non-queued branch — "
        "non-queued events must bypass HTTP loopback and call process_api directly"
    )


# [pr_diff] fail_to_pass
def test_nonqueued_extracts_data():
    """Non-queued path must extract output from process_api result['data'].

    AST-only because: call_tool is a closure (see test_nonqueued_calls_process_api).
    """
    call_tool = _get_call_tool_node()
    assert call_tool is not None, "call_tool function not found"

    nonqueued_body, _ = _find_if_branch(call_tool, "block_fn")
    assert nonqueued_body is not None, "No block_fn.queue branch found"

    # Check for subscript access with "data" key in the non-queued branch
    found_data_access = False
    for stmt in nonqueued_body:
        for child in ast.walk(stmt):
            if isinstance(child, ast.Subscript):
                # Look for something["data"] or something['data']
                if isinstance(child.slice, ast.Constant) and child.slice.value == "data":
                    found_data_access = True
    assert found_data_access, (
        "No ['data'] subscript access in non-queued branch — "
        "must extract output_data from process_api result['data']"
    )


# [pr_diff] fail_to_pass
def test_session_state_imported():
    """SessionState from gradio.state_holder must be available in gradio.mcp."""
    sys.path.insert(0, REPO)
    from gradio import mcp as mcp_mod
    from gradio.state_holder import SessionState

    assert hasattr(mcp_mod, "SessionState"), (
        "SessionState not in gradio.mcp namespace"
    )
    assert mcp_mod.SessionState is SessionState, (
        "SessionState in mcp is not the one from gradio.state_holder"
    )


# [pr_diff] fail_to_pass
def test_nonqueued_uses_session_state():
    """Non-queued path must create a SessionState for the process_api call.

    AST-only because: call_tool is a closure (see test_nonqueued_calls_process_api).
    """
    call_tool = _get_call_tool_node()
    assert call_tool is not None, "call_tool function not found"

    nonqueued_body, _ = _find_if_branch(call_tool, "block_fn")
    assert nonqueued_body is not None, "No block_fn.queue branch found"

    nonqueued_names = set()
    for stmt in nonqueued_body:
        n, _ = _collect_names(stmt)
        nonqueued_names.update(n)
    assert "SessionState" in nonqueued_names, (
        "SessionState not used in non-queued branch — "
        "must create SessionState(self.blocks) for process_api call"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — queued path restructuring
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_queued_preserves_http_loopback():
    """Queued (queue=True) call_tool must still use client.submit (HTTP loopback).

    AST-only because: call_tool is a closure (see test_nonqueued_calls_process_api).
    """
    call_tool = _get_call_tool_node()
    assert call_tool is not None, "call_tool function not found"

    _, queued_body = _find_if_branch(call_tool, "block_fn")
    assert queued_body is not None and len(queued_body) > 0, (
        "No else branch for queued events — queued events must preserve "
        "the HTTP loopback path via client.submit"
    )

    queued_attrs = set()
    for stmt in queued_body:
        _, a = _collect_names(stmt)
        queued_attrs.update(a)
    assert "submit" in queued_attrs, (
        "client.submit not called in queued branch — "
        "queued events must use the HTTP loopback path"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_queued_no_process_api():
    """Queued path must NOT call process_api (uses HTTP loopback instead).

    AST-only because: call_tool is a closure (see test_nonqueued_calls_process_api).
    """
    call_tool = _get_call_tool_node()
    assert call_tool is not None, "call_tool function not found"

    _, queued_body = _find_if_branch(call_tool, "block_fn")
    assert queued_body is not None and len(queued_body) > 0

    queued_attrs = set()
    for stmt in queued_body:
        _, a = _collect_names(stmt)
        queued_attrs.update(a)
    assert "process_api" not in queued_attrs, (
        "process_api called in queued branch — queued events should use "
        "client.submit, not process_api"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_call_tool_not_stub():
    """call_tool must contain real logic (>= 6 meaningful statements).

    AST-only because: call_tool is a closure (see test_nonqueued_calls_process_api).
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "call_tool":
            meaningful = sum(
                1
                for child in ast.walk(node)
                if isinstance(
                    child,
                    (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return,
                     ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Await),
                )
            )
            assert meaningful >= 6, (
                f"call_tool has only {meaningful} meaningful statements — likely a stub"
            )
            return

    assert False, "call_tool function not found in mcp.py"


# [static] pass_to_pass
def test_nonqueued_no_submit():
    """Non-queued path must NOT call client.submit (avoids HTTP loopback).

    AST-only because: call_tool is a closure (see test_nonqueued_calls_process_api).
    """
    call_tool = _get_call_tool_node()
    assert call_tool is not None, "call_tool function not found"

    nonqueued_body, _ = _find_if_branch(call_tool, "block_fn")
    assert nonqueued_body is not None, "No block_fn.queue branch found"

    nonqueued_attrs = set()
    for stmt in nonqueued_body:
        _, a = _collect_names(stmt)
        nonqueued_attrs.update(a)
    assert "submit" not in nonqueued_attrs, (
        "client.submit called in non-queued branch — non-queued events "
        "must bypass HTTP loopback entirely"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md:43
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:43 @ b1f62c0ebc09be80aee830e26689ab70b939cf44
def test_ruff_lint():
    """mcp.py must pass ruff linting (Python formatting standard for this repo)."""
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
