"""
Task: gradio-flaky-playwright-server-ready
Repo: gradio @ a35f5896e43d2585d9206e8256b4d7e321fcd0fe
PR:   13049

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import inspect
import socket
import subprocess
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, "/workspace/gradio")

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_verify_rejects_tcp_only_server():
    """verify_server_startup must reject a server that accepts TCP but doesn't speak HTTP."""
    from gradio.node_server import verify_server_startup

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    port = srv.getsockname()[1]
    srv.listen(5)

    stop = threading.Event()

    def accept_loop():
        srv.settimeout(0.5)
        while not stop.is_set():
            try:
                conn, _ = srv.accept()
                conn.close()
            except socket.timeout:
                pass

    t = threading.Thread(target=accept_loop, daemon=True)
    t.start()

    try:
        result = verify_server_startup("127.0.0.1", port, timeout=3.0)
        assert result is False, (
            "verify_server_startup should return False for a TCP-only server "
            "that does not respond to HTTP requests"
        )
    finally:
        stop.set()
        t.join(timeout=5)
        srv.close()


# [pr_diff] fail_to_pass
def test_verify_rejects_500_error():
    """verify_server_startup must reject a server returning HTTP 500."""
    from gradio.node_server import verify_server_startup

    class Error500Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(500)
            self.end_headers()

        def do_GET(self):
            self.send_response(500)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Error500Handler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    try:
        result = verify_server_startup("127.0.0.1", port, timeout=3.0)
        assert result is False, (
            "verify_server_startup should return False when server returns 500"
        )
    finally:
        server.shutdown()


# [pr_diff] fail_to_pass
def test_verify_default_timeout_increased():
    """Default timeout for verify_server_startup should be increased from the original 5s."""
    from gradio.node_server import verify_server_startup

    sig = inspect.signature(verify_server_startup)
    default_timeout = sig.parameters["timeout"].default
    assert default_timeout >= 10.0, (
        f"Expected default timeout >= 10.0 (was 5.0 before fix), got {default_timeout}"
    )


# [pr_diff] fail_to_pass
def test_ts_http_readiness_polling():
    """TypeScript app-launcher must use HTTP polling for server readiness."""
    ts_path = Path(REPO) / "js" / "tootils" / "src" / "app-launcher.ts"
    content = ts_path.read_text()

    assert "waitForServerReady" in content, (
        "app-launcher.ts should contain a waitForServerReady function "
        "that polls with HTTP requests before resolving"
    )
    assert "import http" in content, (
        "app-launcher.ts should import the http module for HTTP polling"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + behavioral
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_verify_accepts_healthy_server():
    """verify_server_startup must accept a server returning HTTP 200."""
    from gradio.node_server import verify_server_startup

    class OKHandler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(200)
            self.end_headers()

        def do_GET(self):
            self.send_response(200)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), OKHandler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    try:
        result = verify_server_startup("127.0.0.1", port, timeout=5.0)
        assert result is True, (
            "verify_server_startup should return True for a healthy HTTP server"
        )
    finally:
        server.shutdown()


# [pr_diff] pass_to_pass
def test_verify_returns_false_no_server():
    """verify_server_startup must return False when no server is running."""
    from gradio.node_server import verify_server_startup

    # Find a port that's not in use
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    result = verify_server_startup("127.0.0.1", port, timeout=1.0)
    assert result is False, (
        "verify_server_startup should return False when no server is running"
    )


# [static] pass_to_pass
def test_syntax_check():
    """Modified Python file must parse without errors."""
    r = subprocess.run(
        ["python3", "-c", "import py_compile; py_compile.compile('/workspace/gradio/gradio/node_server.py', doraise=True)"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in node_server.py:\n{r.stderr.decode()}"
