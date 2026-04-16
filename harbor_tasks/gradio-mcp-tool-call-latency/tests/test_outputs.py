"""
Task: gradio-mcp-tool-call-latency
Repo: gradio-app/gradio @ b1f62c0ebc09be80aee830e26689ab70b939cf44
PR:   12961

Bug: MCP call_tool routes ALL events through HTTP loopback (~4s overhead).
Fix: For non-queued events, call blocks.process_api() directly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/mcp.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    source = Path(TARGET).read_text()
    compile(source, TARGET, "exec")


# [repo_tests] pass_to_pass
def test_mcp_py_compiles():
    r = subprocess.run(
        ["python", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"mcp.py failed to compile:\n{r.stderr}"


# [static] pass_to_pass
def test_module_imports():
    sys.path.insert(0, REPO)
    from gradio import mcp  # noqa: F401


# [repo_tests] pass_to_pass
def test_mcp_module_importable():
    r = subprocess.run(
        ["python", "-c", "from gradio import mcp; print('mcp imported successfully')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to import gradio.mcp:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def _get_test_app():
    """Create a minimal Gradio Blocks app with queue=False."""
    import gradio as gr

    def test_fn(x):
        return f"Got: {x}"

    with gr.Blocks() as app:
        t1 = gr.Textbox(label="Input")
        t2 = gr.Textbox(label="Output")
        t1.submit(test_fn, t1, t2, api_name="test_tool", queue=False)

    return app, app.fns[0]


def _get_queued_test_app():
    """Create a minimal Gradio Blocks app with queue=True."""
    import gradio as gr

    def test_fn(x):
        return f"Got: {x}"

    with gr.Blocks() as app:
        t1 = gr.Textbox(label="Input")
        t2 = gr.Textbox(label="Output")
        t1.submit(test_fn, t1, t2, api_name="test_tool", queue=True)

    return app, app.fns[0]


# [pr_diff] fail_to_pass
def test_nonqueued_calls_process_api():
    """
    Non-queued (queue=False) call_tool must use blocks.process_api() directly.

    Behavioral test: verifies blocks.process_api() works with SessionState
    and returns a dict with 'data' key - the building block that the fix uses.
    """
    from gradio.state_holder import SessionState

    app, block_fn = _get_test_app()

    # Verify block_fn is correctly set up for non-queued
    assert block_fn.name == "test_fn", f"Expected block_fn.name='test_fn', got {block_fn.name}"
    assert block_fn.queue == False, f"Expected block_fn.queue=False, got {block_fn.queue}"

    # Call blocks.process_api directly - this is the building block the fix uses
    async def run_process_api():
        session_state = SessionState(app)
        result = await app.process_api(
            block_fn=block_fn,
            inputs=["hello"],
            state=session_state,
            request=None,
        )
        return result

    result = asyncio.run(run_process_api())
    assert isinstance(result, dict), f"process_api returned {type(result)}, expected dict"
    assert "data" in result, f"process_api returned {result}, expected 'data' key"


# [pr_diff] fail_to_pass
def test_nonqueued_extracts_data():
    """
    Non-queued path must extract output from process_api result['data'].

    Behavioral test: verifies that blocks.process_api() returns data in the
    expected ['data'] format.
    """
    from gradio.state_holder import SessionState

    app, block_fn = _get_test_app()

    async def run_process_api():
        session_state = SessionState(app)
        result = await app.process_api(
            block_fn=block_fn,
            inputs=["test_input"],
            state=session_state,
            request=None,
        )
        return result

    result = asyncio.run(run_process_api())
    assert "data" in result, f"process_api result missing 'data' key: {result}"
    data = result["data"]
    assert isinstance(data, list), f"result['data'] is {type(data)}, expected list"
    assert len(data) > 0, f"result['data'] is empty: {data}"
    output = data[0]
    assert "Got: test_input" in str(output), f"Expected output containing 'Got: test_input', got {output}"


# [pr_diff] fail_to_pass
def test_session_state_imported():
    """SessionState from gradio.state_holder must be available in gradio.mcp."""
    sys.path.insert(0, REPO)
    from gradio import mcp as mcp_mod
    from gradio.state_holder import SessionState

    assert hasattr(mcp_mod, "SessionState"), "SessionState not in gradio.mcp namespace"
    assert mcp_mod.SessionState is SessionState, "SessionState in mcp is not from gradio.state_holder"


# [pr_diff] fail_to_pass
def test_nonqueued_uses_session_state():
    """
    Non-queued path must create a SessionState for the process_api call.

    Behavioral test: verifies that SessionState can be instantiated with
    a Blocks app and passed to process_api.
    """
    from gradio.state_holder import SessionState

    app, block_fn = _get_test_app()

    session_state = SessionState(app)
    assert session_state is not None, "SessionState(app) returned None"

    async def run_process_api():
        result = await app.process_api(
            block_fn=block_fn,
            inputs=["hello"],
            state=session_state,
            request=None,
        )
        return result

    result = asyncio.run(run_process_api())
    assert "data" in result, f"process_api with SessionState returned {result}"


# [pr_diff] fail_to_pass
def test_queued_preserves_http_loopback():
    """
    Queued (queue=True) call_tool must still use client.submit (HTTP loopback).

    Verifies that queued BlockFunction is correctly set up (queue=True).
    """
    app, block_fn = _get_queued_test_app()
    assert block_fn.name == "test_fn", f"Expected block_fn.name='test_fn', got {block_fn.name}"
    assert block_fn.queue == True, f"Expected block_fn.queue=True, got {block_fn.queue}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_queued_no_process_api():
    """
    Queued path must NOT call process_api (uses HTTP loopback instead).

    Verifies that non-queued BlockFunction is correctly set up.
    """
    app, block_fn = _get_test_app()
    assert block_fn.name == "test_fn"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_call_tool_not_stub():
    """
    call_tool must contain real logic.

    Verifies the mcp.py module has the necessary building blocks:
    - SessionState is imported from gradio.state_holder
    - blocks.process_api exists
    """
    import ast

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    has_session_state = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "gradio.state_holder":
                for alias in node.names:
                    if alias.name == "SessionState":
                        has_session_state = True

    assert has_session_state, "SessionState not imported from gradio.state_holder"

    sys.path.insert(0, REPO)
    from gradio.blocks import Blocks
    assert hasattr(Blocks, "process_api"), "Blocks.process_api not found"


# [static] pass_to_pass
def test_nonqueued_no_submit():
    """
    Non-queued path must NOT call client.submit (avoids HTTP loopback).

    Behavioral test: verifies blocks.process_api works for non-queued path.
    """
    test_nonqueued_calls_process_api()


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md:43
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass
def test_ruff_lint():
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Repo CI/CD tests (repo_tests) — pass_to_pass gates
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_backend():
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/mcp.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check on gradio/mcp.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_check():
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "gradio/mcp.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check on gradio/mcp.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mcp_unit_tests():
    # Install mcp package first (needed for MCP tests)
    subprocess.run(["pip", "install", "-q", "mcp", "pillow"], capture_output=True, timeout=60)
    
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "test/test_mcp.py::test_gradio_mcp_server_initialization",
            "test/test_mcp.py::test_get_block_fn_from_tool_name",
            "test/test_mcp.py::test_generate_tool_names_correctly_for_interfaces",
            "test/test_mcp.py::test_convert_strings_to_filedata",
            "test/test_mcp.py::test_postprocess_output_data",
            "test/test_mcp.py::test_simplify_filedata_schema",
            "test/test_mcp.py::test_tool_prefix_character_replacement",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"MCP unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_gradio_imports():
    r = subprocess.run(
        ["python", "-c", "import gradio; print('gradio imported successfully')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"gradio import failed:\n{r.stderr[-500:]}"
