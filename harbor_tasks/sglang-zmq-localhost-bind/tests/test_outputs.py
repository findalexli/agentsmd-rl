"""
Task: sglang-zmq-localhost-bind
Repo: sgl-project/sglang @ d633ab7349a8cdfe939d25745c3f647c508b8be5
PR:   #21435

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
from pathlib import Path

REPO = "/workspace/sglang"

sys.path.insert(0, f"{REPO}/python")

NETWORK_PY = f"{REPO}/python/sglang/srt/utils/network.py"
SCHEDULER_CLIENT = f"{REPO}/python/sglang/multimodal_gen/runtime/scheduler_client.py"
ENCODE_RECEIVER = f"{REPO}/python/sglang/srt/disaggregation/encode_receiver.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All three modified files must parse without errors."""
    for fpath in [NETWORK_PY, SCHEDULER_CLIENT, ENCODE_RECEIVER]:
        src = Path(fpath).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_default_bind_is_localhost():
    """get_zmq_socket_on_host() without host arg must bind to localhost, not wildcard."""
    import zmq

    from sglang.srt.utils.network import get_zmq_socket_on_host

    for socket_type in [zmq.PULL, zmq.REP, zmq.PUB]:
        port, sock = get_zmq_socket_on_host(zmq.Context(), socket_type)
        try:
            endpoint = sock.getsockopt_string(zmq.LAST_ENDPOINT)
            assert "0.0.0.0" not in endpoint, f"Bound to wildcard: {endpoint}"
            assert "tcp://*" not in endpoint, f"Bound to wildcard: {endpoint}"
            assert port > 0, f"Invalid port: {port}"
        finally:
            sock.close()


# [pr_diff] fail_to_pass
def test_default_bind_returns_loopback_address():
    """Default bind endpoint must contain a loopback address (127.0.0.1 or ::1)."""
    import zmq

    from sglang.srt.utils.network import get_zmq_socket_on_host

    port, sock = get_zmq_socket_on_host(zmq.Context(), zmq.PULL)
    try:
        endpoint = sock.getsockopt_string(zmq.LAST_ENDPOINT)
        is_loopback = "127.0.0.1" in endpoint or "::1" in endpoint
        assert is_loopback, f"Expected loopback address, got: {endpoint}"
    finally:
        sock.close()


# [pr_diff] fail_to_pass
def test_broker_no_wildcard_bind():
    """run_zeromq_broker in scheduler_client.py must not bind to tcp://*."""
    # WHY STRUCTURAL: run_zeromq_broker is async and requires ServerArgs with heavy imports
    src = Path(SCHEDULER_CLIENT).read_text()
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if "tcp://*" in stripped and not stripped.startswith("#"):
            raise AssertionError(f"Wildcard bind at line {i}: {stripped}")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_explicit_host_binds_correctly():
    """Passing an explicit host must still work (regression check)."""
    import zmq

    from sglang.srt.utils.network import get_zmq_socket_on_host

    port, sock = get_zmq_socket_on_host(zmq.Context(), zmq.PULL, host="127.0.0.1")
    try:
        endpoint = sock.getsockopt_string(zmq.LAST_ENDPOINT)
        assert "127.0.0.1" in endpoint, f"Expected 127.0.0.1 in endpoint, got: {endpoint}"
        assert port > 0
    finally:
        sock.close()


# [pr_diff] pass_to_pass
def test_explicit_wildcard_still_allowed():
    """Callers that need cross-machine reachability can still pass explicit 0.0.0.0."""
    import zmq

    from sglang.srt.utils.network import get_zmq_socket_on_host

    port, sock = get_zmq_socket_on_host(zmq.Context(), zmq.PULL, host="0.0.0.0")
    try:
        assert port > 0, "Expected valid port for explicit wildcard bind"
    finally:
        sock.close()


# [pr_diff] fail_to_pass
def test_receiver_calls_safe():
    """Encode receiver call sites must be safe (default is localhost OR calls pass host)."""
    # WHY STRUCTURAL: encode_receiver.py imports torch — can't import on CPU-only image
    net_src = Path(NETWORK_PY).read_text()
    net_tree = ast.parse(net_src)

    # Check if get_zmq_socket_on_host defaults to localhost
    for node in ast.walk(net_tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_zmq_socket_on_host":
            func_lines = net_src.splitlines()[node.lineno - 1 : node.end_lineno]
            func_text = "\n".join(func_lines)
            if "127.0.0.1" in func_text or "localhost" in func_text:
                return  # Default is safe — all callers are protected
            break

    # Default is NOT safe — verify receiver calls pass host explicitly
    recv_src = Path(ENCODE_RECEIVER).read_text()
    recv_tree = ast.parse(recv_src)

    calls_found = 0
    calls_with_host = 0
    for node in ast.walk(recv_tree):
        if isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name == "get_zmq_socket_on_host":
                calls_found += 1
                has_host_kw = any(kw.arg == "host" for kw in node.keywords)
                has_3_plus_args = len(node.args) >= 3
                if has_host_kw or has_3_plus_args:
                    calls_with_host += 1

    assert calls_found > 0, "No get_zmq_socket_on_host calls found in encode_receiver.py"
    assert calls_with_host == calls_found, (
        f"Only {calls_with_host}/{calls_found} calls pass host, and default is not safe"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified files must not be hollowed out."""
    min_lines = {
        NETWORK_PY: 150,
        SCHEDULER_CLIENT: 30,
        ENCODE_RECEIVER: 500,
    }
    for fpath, threshold in min_lines.items():
        lines = len(Path(fpath).read_text().splitlines())
        assert lines >= threshold, f"{fpath} only has {lines} lines (expected >= {threshold})"
