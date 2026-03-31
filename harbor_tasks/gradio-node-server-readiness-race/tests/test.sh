#!/usr/bin/env bash
set +e

SCORE=0
LOG="/logs/verifier"
mkdir -p "$LOG"

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; }

###############################################################################
# GATE: Syntax check — abort if node_server.py has syntax errors
###############################################################################
# [pr_diff] (0.00): Python file must be syntactically valid
if python3 -c "import py_compile; py_compile.compile('/workspace/gradio/gradio/node_server.py', doraise=True)" 2>/dev/null; then
    pass "node_server.py syntax OK"
else
    fail "node_server.py has syntax errors"
    echo "0.0" > "$LOG/reward.txt"
    exit 0
fi

# [pr_diff] (0.00): TypeScript file must exist and be non-empty
if [ -s /workspace/gradio/js/tootils/src/app-launcher.ts ]; then
    pass "app-launcher.ts exists and is non-empty"
else
    fail "app-launcher.ts is missing or empty"
    echo "0.0" > "$LOG/reward.txt"
    exit 0
fi

###############################################################################
# BEHAVIORAL F2P: HTTP 500 server → must return False (CORE BUG TEST)
# Buggy code: TCP socket connects fine → True. Fixed: HTTP 500 → False.
###############################################################################
# [pr_diff] (0.30): Server returning 500 must NOT be detected as ready
python3 -c "
import threading, time, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class Error500Handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(500)
        self.end_headers()
    def do_GET(self):
        self.send_response(500)
        self.end_headers()
    def log_message(self, *a): pass

srv = HTTPServer(('127.0.0.1', 18902), Error500Handler)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
time.sleep(0.1)

sys.path.insert(0, '/workspace/gradio')
for mod in list(sys.modules):
    if 'gradio' in mod:
        del sys.modules[mod]
from gradio.node_server import verify_server_startup
result = verify_server_startup('127.0.0.1', 18902, timeout=2.0)
srv.shutdown()
assert result is False, f'Expected False for HTTP 500 server, got {result}'
" 2>/dev/null && {
    pass "verify_server_startup returns False for HTTP 500 (core F2P)"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
} || {
    fail "verify_server_startup returns True for HTTP 500 (TCP-only check bug)"
}

###############################################################################
# BEHAVIORAL F2P: TCP-only server (accepts TCP, never sends HTTP response)
# Buggy code: TCP connects → True. Fixed code: HTTP times out → False.
# This models the actual race condition: OS socket is listening but the
# application layer isn't serving HTTP yet.
###############################################################################
# [pr_diff] (0.15): TCP-listening but HTTP-unresponsive server → not ready
python3 -c "
import socket, threading, time, sys

# Raw TCP server: accepts connections but never sends any HTTP response
srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv_sock.bind(('127.0.0.1', 18910))
srv_sock.listen(5)

def accept_loop():
    conns = []
    while True:
        try:
            conn, _ = srv_sock.accept()
            conns.append(conn)
            # Hold connection open, never send HTTP response
        except:
            for c in conns:
                try: c.close()
                except: pass
            break

t = threading.Thread(target=accept_loop, daemon=True)
t.start()
time.sleep(0.1)

sys.path.insert(0, '/workspace/gradio')
for mod in list(sys.modules):
    if 'gradio' in mod:
        del sys.modules[mod]
from gradio.node_server import verify_server_startup
result = verify_server_startup('127.0.0.1', 18910, timeout=3.0)
srv_sock.close()
assert result is False, f'Expected False for TCP-only (no HTTP) server, got {result}'
" 2>/dev/null && {
    pass "verify_server_startup returns False for TCP-only server (F2P)"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
} || {
    fail "verify_server_startup returns True for TCP-only server (race condition bug)"
}

###############################################################################
# BEHAVIORAL: HTTP 200 server → True
# Handlers support both GET and HEAD so any valid HTTP method works.
###############################################################################
# [pr_diff] (0.15): Server returning 200 is detected as ready
python3 -c "
import threading, time, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class OKHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, *a): pass

srv = HTTPServer(('127.0.0.1', 18901), OKHandler)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
time.sleep(0.1)

sys.path.insert(0, '/workspace/gradio')
for mod in list(sys.modules):
    if 'gradio' in mod:
        del sys.modules[mod]
from gradio.node_server import verify_server_startup
result = verify_server_startup('127.0.0.1', 18901, timeout=5.0)
srv.shutdown()
assert result is True, f'Expected True for HTTP 200 server, got {result}'
" 2>/dev/null && {
    pass "verify_server_startup returns True for HTTP 200"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
} || {
    fail "verify_server_startup does not return True for HTTP 200"
}

###############################################################################
# BEHAVIORAL: HTTP 404 server → True (status < 500 means app is running)
###############################################################################
# [pr_diff] (0.10): Server returning 404 is still considered ready
python3 -c "
import threading, time, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class NotFoundHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(404)
        self.end_headers()
    def do_GET(self):
        self.send_response(404)
        self.end_headers()
    def log_message(self, *a): pass

srv = HTTPServer(('127.0.0.1', 18903), NotFoundHandler)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
time.sleep(0.1)

sys.path.insert(0, '/workspace/gradio')
for mod in list(sys.modules):
    if 'gradio' in mod:
        del sys.modules[mod]
from gradio.node_server import verify_server_startup
result = verify_server_startup('127.0.0.1', 18903, timeout=5.0)
srv.shutdown()
assert result is True, f'Expected True for HTTP 404 server, got {result}'
" 2>/dev/null && {
    pass "verify_server_startup returns True for HTTP 404 (< 500)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
} || {
    fail "verify_server_startup does not accept HTTP 404"
}

###############################################################################
# BEHAVIORAL P2P: No server → False
###############################################################################
# [pr_diff] (0.05): No server on port returns False
python3 -c "
import sys
sys.path.insert(0, '/workspace/gradio')
for mod in list(sys.modules):
    if 'gradio' in mod:
        del sys.modules[mod]
from gradio.node_server import verify_server_startup
result = verify_server_startup('127.0.0.1', 18999, timeout=1.0)
assert result is False, f'Expected False for no server, got {result}'
" 2>/dev/null && {
    pass "verify_server_startup returns False when nothing is listening"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
} || {
    fail "verify_server_startup does not return False for no server"
}

###############################################################################
# BEHAVIORAL P2P: attempt_connection still works (regression)
###############################################################################
# [pr_diff] (0.05): attempt_connection not broken by changes
python3 -c "
import threading, time, sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class OKHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, *a): pass

srv = HTTPServer(('127.0.0.1', 18904), OKHandler)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
time.sleep(0.1)

sys.path.insert(0, '/workspace/gradio')
for mod in list(sys.modules):
    if 'gradio' in mod:
        del sys.modules[mod]
from gradio.node_server import attempt_connection
result = attempt_connection('127.0.0.1', 18904)
srv.shutdown()
assert result is True, f'Expected True, got {result}'
" 2>/dev/null && {
    pass "attempt_connection still works (regression)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
} || {
    fail "attempt_connection broken"
}

###############################################################################
# STRUCTURAL: TypeScript app-launcher.ts has HTTP readiness check
# Cannot run TS in this container (python:3.12-slim, no Node), so structural
# check is justified. Pattern accepts http.request, http.get, or fetch().
###############################################################################
# [pr_diff] (0.10): TypeScript launcher uses HTTP for readiness polling
if grep -qE '(http\.(request|get)|fetch\s*\()' /workspace/gradio/js/tootils/src/app-launcher.ts 2>/dev/null; then
    pass "app-launcher.ts uses HTTP for readiness polling"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    fail "app-launcher.ts does not use HTTP for readiness polling"
fi

###############################################################################
# CONFIG: ruff lint on changed Python file
###############################################################################
# [agent_config] (0.05): "Python code is formatted with ruff" — AGENTS.md:43
if command -v ruff &>/dev/null; then
    if ruff check /workspace/gradio/gradio/node_server.py --select E,W --quiet 2>/dev/null; then
        pass "ruff check passes on node_server.py"
        SCORE=$(python3 -c "print($SCORE + 0.05)")
    else
        fail "ruff check fails on node_server.py"
    fi
else
    # ruff not installed — give benefit of the doubt
    pass "ruff not available, skipping (neutral)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi

###############################################################################
# FINAL SCORE
###############################################################################

FINAL=$(python3 -c "print(f'{min(1.0, max(0.0, $SCORE)):.4f}')")

echo ""
echo "=== SCORE ==="
echo "  Reward: $FINAL"
echo "$FINAL" > "$LOG/reward.txt"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
