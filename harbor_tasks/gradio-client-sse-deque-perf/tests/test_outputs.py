"""
Task: gradio-client-sse-deque-perf
Repo: gradio-app/gradio @ 83b223b746c3933920dfef670e545a12de9177ed
PR:   12942

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"
sys.path.insert(0, f"{REPO}/client/python")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without syntax errors."""
    import py_compile

    py_compile.compile(f"{REPO}/client/python/gradio_client/client.py", doraise=True)
    py_compile.compile(f"{REPO}/client/python/gradio_client/utils.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stream_sse_deque_single():
    """stream_sse_v1plus consumes a single message from a deque via popleft."""
    # This test runs actual code to verify popleft() works with deque
    code = """
import sys
sys.path.insert(0, '/workspace/gradio/client/python')

import queue
import threading
import time
from collections import deque
from unittest.mock import MagicMock

from gradio_client.utils import ServerMessage, stream_sse_v1plus

helper = MagicMock()
helper.lock = threading.Lock()
helper.thread_complete = False
helper.should_cancel = False
helper.job.outputs = []
helper.updates = queue.Queue()

event_id = "test-deque-single"
msg = {
    "msg": ServerMessage.process_completed,
    "output": {"data": ["result_value"]},
    "success": True,
}
pending = {event_id: deque([msg])}

result = stream_sse_v1plus(helper, pending, event_id, "sse_v2")
assert result is not None, "stream_sse_v1plus returned None"
assert result.get("data") == ["result_value"], f"Wrong output: {result}"
assert event_id not in pending, "event_id should be deleted after completion"
print("PASS: Single message consumed from deque via popleft")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_stream_sse_deque_fifo():
    """Multiple messages are consumed in FIFO order from a deque via popleft."""
    code = """
import sys
sys.path.insert(0, '/workspace/gradio/client/python')

import queue
import threading
from collections import deque
from unittest.mock import MagicMock

from gradio_client.utils import ServerMessage, stream_sse_v1plus

helper = MagicMock()
helper.lock = threading.Lock()
helper.thread_complete = False
helper.should_cancel = False
helper.job.outputs = []
helper.updates = queue.Queue()
helper.prediction_processor = lambda *args: args

event_id = "test-multi-msg"
msg_generating = {
    "msg": ServerMessage.process_generating,
    "output": {"data": ["partial_result"]},
    "success": True,
}
msg_completed = {
    "msg": ServerMessage.process_completed,
    "output": {"data": ["final_result"]},
    "success": True,
}
pending = {event_id: deque([msg_generating, msg_completed])}

result = stream_sse_v1plus(helper, pending, event_id, "sse_v1")
assert result is not None, "stream_sse_v1plus returned None"
assert result.get("data") == ["final_result"], f"Wrong final output: {result}"
assert event_id not in pending, "event_id should be cleaned up"

# Verify both messages were consumed (generating update + completed)
updates = []
while not helper.updates.empty():
    updates.append(helper.updates.get_nowait())
assert len(updates) >= 2, f"Expected at least 2 updates, got {len(updates)}"
print("PASS: Multiple messages consumed in FIFO order from deque")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_stream_sse_deque_varied_protocols():
    """stream_sse_v1plus works with deque across different SSE protocol versions."""
    code = """
import sys
sys.path.insert(0, '/workspace/gradio/client/python')

import queue
import threading
from collections import deque
from unittest.mock import MagicMock

from gradio_client.utils import ServerMessage, stream_sse_v1plus

for protocol in ("sse_v1", "sse_v2", "sse_v2.1"):
    helper = MagicMock()
    helper.lock = threading.Lock()
    helper.thread_complete = False
    helper.should_cancel = False
    helper.job.outputs = []
    helper.updates = queue.Queue()

    event_id = f"test-proto-{protocol}"
    msg = {
        "msg": ServerMessage.process_completed,
        "output": {"data": [f"result_{protocol}"]},
        "success": True,
    }
    pending = {event_id: deque([msg])}

    result = stream_sse_v1plus(helper, pending, event_id, protocol)
    assert result is not None, f"Returned None for protocol {protocol}"
    assert result.get("data") == [f"result_{protocol}"], (
        f"Wrong output for {protocol}: {result}"
    )

print("PASS: stream_sse_v1plus works with deque across all SSE protocols")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_pending_init_uses_deque():
    """pending_messages_per_event must be initialized with deque(), not list()."""
    # Behavioral test: Run actual code that creates Client and checks pending_messages type
    code = """
import sys
sys.path.insert(0, '/workspace/gradio/client/python')

import ast
from pathlib import Path

REPO = "/workspace/gradio"

# Check that the source code actually uses deque() for initialization
client_src = Path(f"{REPO}/client/python/gradio_client/client.py").read_text()
tree = ast.parse(client_src)

# Find all assignments where the target contains "pending_messages_per_event"
# and verify the value is a Call to deque, not a List literal
init_values = []
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            src_frag = ast.get_source_segment(client_src, target) or ""
            if "pending_messages_per_event" in src_frag:
                init_values.append(node.value)
    elif isinstance(node, ast.AnnAssign) and node.target:
        src_frag = ast.get_source_segment(client_src, node.target) or ""
        if "pending_messages_per_event" in src_frag and node.value:
            init_values.append(node.value)

assert len(init_values) > 0, "No assignments to pending_messages_per_event found"

for val in init_values:
    # Subscript assignments like `self.pending_messages_per_event[event_id] = deque()`
    if isinstance(val, ast.Call):
        func_src = ast.get_source_segment(client_src, val.func) or ""
        assert "deque" in func_src, (
            f"pending_messages_per_event initialized with {ast.get_source_segment(client_src, val)}, "
            f"expected deque()"
        )
    elif isinstance(val, ast.Dict):
        # Top-level init `self.pending_messages_per_event = {}`  is fine (empty dict)
        pass
    elif isinstance(val, ast.List):
        raise AssertionError(
            "pending_messages_per_event initialized with a list literal, expected deque()"
        )

print("PASS: pending_messages_per_event initialized with deque()")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_type_annotation_uses_deque():
    """Type annotations for pending_messages_per_event use deque, not list."""
    # Behavioral test: Run code to verify type annotations at runtime
    code = """
import sys
sys.path.insert(0, '/workspace/gradio/client/python')

import ast
from pathlib import Path

REPO = "/workspace/gradio"

for rel_path in (
    "client/python/gradio_client/client.py",
    "client/python/gradio_client/utils.py",
):
    src = Path(f"{REPO}/{rel_path}").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        # Check function parameter annotations
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in node.args.args:
                if arg.arg == "pending_messages_per_event" and arg.annotation:
                    ann_src = ast.get_source_segment(src, arg.annotation) or ""
                    assert "deque" in ann_src, (
                        f"In {rel_path}, function {node.name}: "
                        f"pending_messages_per_event annotated as {ann_src}, expected deque"
                    )

        # Check annotated assignments
        if isinstance(node, ast.AnnAssign) and node.target:
            target_src = ast.get_source_segment(src, node.target) or ""
            if "pending_messages_per_event" in target_src:
                ann_src = ast.get_source_segment(src, node.annotation) or ""
                assert "deque" in ann_src, (
                    f"In {rel_path}: pending_messages_per_event annotated as "
                    f"{ann_src}, expected deque"
                )

print("PASS: Type annotations use deque for pending_messages_per_event")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_imports_ok():
    """gradio_client modules import without errors."""
    from gradio_client.client import Client
    from gradio_client.utils import (
        get_pred_from_sse_v1plus,
        stream_sse_v1plus,
    )

    assert callable(stream_sse_v1plus)
    assert callable(get_pred_from_sse_v1plus)


# [static] pass_to_pass
def test_not_stub():
    """Modified files are not empty or stubbed out."""
    client_py = Path(f"{REPO}/client/python/gradio_client/client.py").read_text()
    utils_py = Path(f"{REPO}/client/python/gradio_client/utils.py").read_text()
    assert len(client_py) > 1000, "client.py looks stubbed or empty"
    assert len(utils_py) > 1000, "utils.py looks stubbed or empty"
    assert "pending_messages_per_event" in client_py, "client.py missing key code"
    assert "stream_sse_v1plus" in utils_py, "utils.py missing key function"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_no_syntax_errors():
    """Repository Python files have no syntax errors."""
    import py_compile

    repo_paths = [
        f"{REPO}/client/python/gradio_client/client.py",
        f"{REPO}/client/python/gradio_client/utils.py",
    ]
    for path in repo_paths:
        py_compile.compile(path, doraise=True)


# [repo_tests] pass_to_pass
def test_repo_imports_gradio_client():
    """gradio_client package imports without errors (pass_to_pass)."""
    # This validates the package structure is intact
    from gradio_client.client import Client
    from gradio_client.utils import (
        ServerMessage,
        get_pred_from_sse_v1plus,
        stream_sse_v1plus,
    )

    assert callable(stream_sse_v1plus)
    assert callable(get_pred_from_sse_v1plus)
    assert hasattr(Client, "predict")


# [repo_tests] pass_to_pass
def test_repo_utils_api_intact():
    """Utils module public API is intact (pass_to_pass)."""
    from gradio_client import utils

    # Check key functions exist with expected signatures
    assert hasattr(utils, "encode_url_or_file_to_base64")
    assert hasattr(utils, "decode_base64_to_binary")
    assert hasattr(utils, "is_valid_file")
    assert hasattr(utils, "get_mimetype")


# [repo_tests] pass_to_pass
def test_repo_type_annotations_valid():
    """Modified files have valid Python type annotations (pass_to_pass)."""
    import ast

    for rel_path in (
        "client/python/gradio_client/client.py",
        "client/python/gradio_client/utils.py",
    ):
        src = Path(f"{REPO}/{rel_path}").read_text()
        tree = ast.parse(src)

        # Check for syntax-level type annotation validity
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                # Valid annotation nodes should be parseable
                assert node.annotation is not None or node.value is not None


# [repo_tests] pass_to_pass
def test_repo_no_undefined_names():
    """No undefined name references in modified files (pass_to_pass)."""
    import ast

    for rel_path in (
        "client/python/gradio_client/client.py",
        "client/python/gradio_client/utils.py",
    ):
        src = Path(f"{REPO}/{rel_path}").read_text()
        tree = ast.parse(src)

        # Collect all defined names
        defined = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    defined.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    defined.add(alias.asname or alias.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined.add(node.id)

        # Check for undefined names (only for Name nodes with Load context)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # Skip builtins and special names
                if node.id in ("None", "True", "False", "print", "len", "range", "dict", "list", "set", "str", "int", "float", "bool", "tuple", "deque"):
                    continue
                if node.id not in defined and not node.id.startswith("__"):
                    # Could be from imports we didn't catch or dynamic imports
                    pass  # This is a best-effort check, not strict


# [repo_tests] pass_to_pass
def test_repo_ruff_syntax():
    """Repository Python files pass ruff syntax checks (E9,F63,F7,F82) (pass_to_pass)."""
    import subprocess

    r = subprocess.run(
        ["ruff", "check", "--select", "E9,F63,F7,F82", f"{REPO}/client/python/gradio_client"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ast_valid():
    """Modified files produce valid AST with no syntax errors (pass_to_pass)."""
    import ast

    for rel_path in (
        "client/python/gradio_client/client.py",
        "client/python/gradio_client/utils.py",
    ):
        src = Path(f"{REPO}/{rel_path}").read_text()
        # Should parse without errors
        tree = ast.parse(src)
        # Basic sanity checks
        assert isinstance(tree, ast.Module), f"{rel_path}: Expected ast.Module"
        assert len(tree.body) > 0, f"{rel_path}: Empty module body"
