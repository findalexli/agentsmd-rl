"""
Task: gradio-client-sse-deque-perf
Repo: gradio-app/gradio @ 83b223b746c3933920dfef670e545a12de9177ed
PR:   12942

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

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


# [pr_diff] fail_to_pass
def test_stream_sse_deque_fifo():
    """Multiple messages are consumed in FIFO order from a deque via popleft."""
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


# [pr_diff] fail_to_pass
def test_stream_sse_deque_varied_protocols():
    """stream_sse_v1plus works with deque across different SSE protocol versions."""
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


# [pr_diff] fail_to_pass
def test_pending_init_uses_deque():
    """pending_messages_per_event must be initialized with deque(), not list()."""
    import ast

    # AST-only because: Client.__init__ requires a running Gradio server to construct
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


# [pr_diff] fail_to_pass
def test_type_annotation_uses_deque():
    """Type annotations for pending_messages_per_event use deque, not list."""
    import ast

    # AST-only because: need to inspect type annotations, not runtime behavior
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
