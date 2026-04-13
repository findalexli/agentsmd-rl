"""
Task: gradio-node-server-readiness-race
Repo: gradio-app/gradio @ a35f5896e43d2585d9206e8256b4d7e321fcd0fe

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO = "/workspace/gradio"
NODE_SERVER_PATH = f"{REPO}/gradio/node_server.py"


def _load_node_server():
    """Load node_server.py directly, bypassing gradio.__init__ (heavy deps)."""
    spec = importlib.util.spec_from_file_location("node_server", NODE_SERVER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_handler(status_code):
    """Create an HTTP handler that returns the given status code."""
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            self.send_response(status_code)
            self.end_headers()

        def do_GET(self):
            self.send_response(status_code)
            self.end_headers()

        def log_message(self, *a):
            pass

    return Handler


def _start_http_server(port, status_code):
    srv = HTTPServer(("127.0.0.1", port), _make_handler(status_code))
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    time.sleep(0.1)
    return srv


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """node_server.py must be syntactically valid Python."""
    import py_compile
    py_compile.compile(NODE_SERVER_PATH, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_http_500_server_not_ready():
    """Server returning HTTP 500 must NOT be considered ready.

    The base code only checks TCP connectivity, so any listening socket
    (including one returning 500) is wrongly reported as ready.
    """
    mod = _load_node_server()
    srv = _start_http_server(18902, 500)
    try:
        result = mod.verify_server_startup("127.0.0.1", 18902, timeout=2.0)
        assert result is False, f"Expected False for HTTP 500 server, got {result}"
    finally:
        srv.shutdown()


# [pr_diff] fail_to_pass
def test_tcp_only_server_not_ready():
    """TCP-listening but HTTP-unresponsive server must NOT be considered ready.

    A socket that accepts connections but never sends an HTTP response
    should not pass the readiness check.
    """
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv_sock.bind(("127.0.0.1", 18910))
    srv_sock.listen(5)

    conns = []

    def accept_loop():
        while True:
            try:
                conn, _ = srv_sock.accept()
                conns.append(conn)
            except Exception:
                break

    t = threading.Thread(target=accept_loop, daemon=True)
    t.start()
    time.sleep(0.1)

    mod = _load_node_server()
    try:
        result = mod.verify_server_startup("127.0.0.1", 18910, timeout=3.0)
        assert result is False, f"Expected False for TCP-only server, got {result}"
    finally:
        for c in conns:
            try:
                c.close()
            except Exception:
                pass
        srv_sock.close()


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_http_200_server_ready():
    """Server returning HTTP 200 must be detected as ready."""
    mod = _load_node_server()
    srv = _start_http_server(18901, 200)
    try:
        result = mod.verify_server_startup("127.0.0.1", 18901, timeout=5.0)
        assert result is True, f"Expected True for HTTP 200 server, got {result}"
    finally:
        srv.shutdown()


# [pr_diff] pass_to_pass
def test_http_404_server_ready():
    """Server returning HTTP 404 (< 500) is still considered ready.

    The app is running and responding — a 404 is not a server error.
    """
    mod = _load_node_server()
    srv = _start_http_server(18903, 404)
    try:
        result = mod.verify_server_startup("127.0.0.1", 18903, timeout=5.0)
        assert result is True, f"Expected True for HTTP 404 server, got {result}"
    finally:
        srv.shutdown()


# [pr_diff] pass_to_pass
def test_http_302_server_ready():
    """Server returning HTTP 302 redirect (< 500) is still ready."""
    mod = _load_node_server()
    srv = _start_http_server(18905, 302)
    try:
        result = mod.verify_server_startup("127.0.0.1", 18905, timeout=5.0)
        assert result is True, f"Expected True for HTTP 302 server, got {result}"
    finally:
        srv.shutdown()


# [pr_diff] pass_to_pass
def test_no_server_returns_false():
    """No server listening on port must return False."""
    mod = _load_node_server()
    result = mod.verify_server_startup("127.0.0.1", 18999, timeout=1.0)
    assert result is False, f"Expected False for no server, got {result}"


# [pr_diff] pass_to_pass
def test_attempt_connection_not_broken():
    """attempt_connection must still work after changes (regression guard)."""
    mod = _load_node_server()
    srv = _start_http_server(18904, 200)
    try:
        result = mod.attempt_connection("127.0.0.1", 18904)
        assert result is True, f"Expected True, got {result}"
    finally:
        srv.shutdown()


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ a35f5896e43d2585d9206e8256b4d7e321fcd0fe
def test_ruff_node_server():
    """node_server.py must pass ruff linting (AGENTS.md requires ruff formatting)."""
    r = subprocess.run(
        ["ruff", "check", "gradio/node_server.py"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Structural (pr_diff) — TypeScript check (no Node.js in container)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ts_launcher_uses_http_readiness():
    """app-launcher.ts must use HTTP (not just TCP) for readiness polling.

    # AST-only because: no Node.js runtime in container to execute TypeScript
    """
    ts_path = Path(f"{REPO}/js/tootils/src/app-launcher.ts")
    assert ts_path.exists(), "app-launcher.ts is missing"
    content = ts_path.read_text()
    assert any(
        pat in content for pat in ["http.request", "http.get", "fetch("]
    ), "app-launcher.ts does not use HTTP for readiness polling"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (p2p_enrichment)
#
# CI Commands Discovered and Added:
# - "ruff check gradio/node_server.py" - Added as test_repo_ruff_node_server
# - "ruff format --check gradio/node_server.py" - Added as test_repo_ruff_format_node_server
# - "python -m py_compile gradio/node_server.py" - Added as test_repo_node_server_syntax
#
# CI Commands Discovered but NOT Added (require Dockerfile changes):
# - "ruff check gradio" - fails on base commit (3 pre-existing errors)
# - "ruff format --check gradio" - fails on base commit (formatting issues)
# - "ty check" - ty not installed in container
# - "pnpm lint/format/ts:check/test" - pnpm/node not installed in container
# - "pytest" - gradio dependencies not installed, needs full venv setup
# - "python -m pytest test/test_http_server.py" - requires gradio install
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass - node_server.py must be syntactically valid (CI: py_compile)
def test_repo_node_server_syntax():
    """gradio/node_server.py must have valid Python syntax (pass_to_pass).

    Uses Python s py_compile module (same as CI s syntax validation).
    """
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/gradio/node_server.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - node_server.py must pass ruff linting (CI: ruff check)
def test_repo_ruff_node_server():
    """gradio/node_server.py must pass ruff linting (pass_to_pass).

    This is the repo s primary Python linter as defined in scripts/lint_backend.sh.
    The full repo has pre-existing lint issues, but node_server.py is clean.
    """
    r = subprocess.run(
        ["ruff", "check", "gradio/node_server.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - node_server.py must pass ruff format check (CI: ruff format)
def test_repo_ruff_format_node_server():
    """gradio/node_server.py must pass ruff format check (pass_to_pass).

    This is the repo s formatting check as defined in scripts/lint_backend.sh.
    """
    r = subprocess.run(
        ["ruff", "format", "--check", "gradio/node_server.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - app-launcher.ts must be valid TypeScript (CI: syntax check)
def test_repo_ts_syntax():
    """js/tootils/src/app-launcher.ts must have valid TypeScript syntax (pass_to_pass).

    TypeScript files must be syntactically valid (basic structure check).
    This covers the second modified file from the PR.
    """
    ts_path = Path(f"{REPO}/js/tootils/src/app-launcher.ts")
    assert ts_path.exists(), "app-launcher.ts does not exist"
    content = ts_path.read_text()
    # Basic TypeScript syntax validation: must have balanced braces and valid imports
    open_braces = content.count("{")
    close_braces = content.count("}")
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert open_braces == close_braces, "Unbalanced braces in TypeScript file"
    assert open_parens == close_parens, "Unbalanced parentheses in TypeScript file"


# [static] pass_to_pass - node_server.py must exist
def test_repo_node_server_exists():
    """gradio/node_server.py must exist (pass_to_pass)."""
    assert Path(NODE_SERVER_PATH).exists(), f"{NODE_SERVER_PATH} does not exist"
