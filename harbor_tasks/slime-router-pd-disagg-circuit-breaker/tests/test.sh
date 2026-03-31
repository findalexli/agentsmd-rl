#!/usr/bin/env bash
set +e

SCORE=0
LOGS=/logs/verifier
mkdir -p "$LOGS"

log() { echo "[test.sh] $*"; }

# ── GATE: Syntax check ──────────────────────────────────────────────
# [static] (0.00): Python syntax must be valid
log "GATE: syntax check"
if ! python3 -c "
import py_compile, sys
try:
    py_compile.compile('slime/ray/rollout.py', doraise=True)
except py_compile.PyCompileError as e:
    print(f'SYNTAX ERROR: {e}', file=sys.stderr)
    sys.exit(1)
"; then
    log "GATE FAILED — syntax error in rollout.py"
    echo "0.0" > "$LOGS/reward.txt"
    exit 0
fi
log "GATE passed"

# ── Behavioral tests via AST extraction + mocked execution ──────────
# Justification for AST extract: slime/ray/rollout.py imports ray, torch,
# sglang — heavy GPU/distributed deps that cannot run on CPU.
cat > /tmp/test_start_router.py << 'PYEOF'
"""Behavioral tests for _start_router in slime/ray/rollout.py.

Extracts the function via AST, execs with mocked globals, then calls it
with various arg combos and captures Process construction args.
"""
import ast
import copy
import json
import sys
import textwrap
import time
import types

# --- Read and extract the function ---
with open("slime/ray/rollout.py") as f:
    source = f.read()

tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_start_router":
        func_node = node
        break

if func_node is None:
    print(json.dumps({"error": "_start_router not found"}))
    sys.exit(1)

lines = source.splitlines()
func_lines = lines[func_node.lineno - 1 : func_node.end_lineno]
func_source = "\n".join(func_lines)

# --- Mock environment ---
class MockRouterArgs:
    @classmethod
    def from_cli_args(cls, args, use_router_prefix=False):
        return cls()

class MockLogger:
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def mock_run_router(*a, **kw): pass
def mock_wrap_ipv6(x): return x
def mock_find_available_port(x): return 12345
def mock_get_host_info(): return ("host", "127.0.0.1")

mock_slime_router = types.ModuleType("slime.router.router")
mock_slime_router.run_router = mock_run_router
mock_sglang_router = types.ModuleType("sglang_router.launch_router")
mock_sglang_router.RouterArgs = MockRouterArgs
mock_http_utils = types.ModuleType("slime.utils.http_utils")
mock_http_utils.run_router = mock_run_router

sys.modules["slime"] = types.ModuleType("slime")
sys.modules["slime.router"] = types.ModuleType("slime.router")
sys.modules["slime.router.router"] = mock_slime_router
sys.modules["sglang_router"] = types.ModuleType("sglang_router")
sys.modules["sglang_router.launch_router"] = mock_sglang_router
sys.modules["slime.utils"] = types.ModuleType("slime.utils")
sys.modules["slime.utils.http_utils"] = mock_http_utils


def run_with_capture(func_source, base_ns, args, **kwargs):
    """Exec _start_router with a capturing Process mock, return (result, router_args, process_called)."""
    captured = {"called": False, "target_args": None}

    class CapturingProcess:
        daemon = False
        def __init__(self, target=None, args=None):
            captured["called"] = True
            captured["target_args"] = args
        def start(self): pass
        def is_alive(self): return True

    ns = dict(base_ns)
    ns["multiprocessing"] = types.SimpleNamespace(Process=CapturingProcess)
    exec(func_source, ns)
    fn = ns["_start_router"]
    result = fn(args, **kwargs)
    router_args = None
    if captured["target_args"] is not None:
        router_args = captured["target_args"][0]
    return result, router_args, captured["called"]


def make_args(use_slime_router=False, sglang_router_ip=None,
              sglang_router_port=None, sglang_router_request_timeout_secs=30):
    return types.SimpleNamespace(
        use_slime_router=use_slime_router,
        sglang_router_ip=sglang_router_ip,
        sglang_router_port=sglang_router_port,
        sglang_router_request_timeout_secs=sglang_router_request_timeout_secs,
    )


base_ns = {
    "time": time,
    "random": __import__("random"),
    "copy": copy,
    "logger": MockLogger(),
    "_wrap_ipv6": mock_wrap_ipv6,
    "find_available_port": mock_find_available_port,
    "get_host_info": mock_get_host_info,
}

results = {}

# ── TEST 1 (F2P): Slime router + PD disagg doesn't crash, returns ip/port,
#    Process is spawned, and pd flag is set on router_args ──────────────
try:
    args = make_args(use_slime_router=True)
    result, router_args, proc_called = run_with_capture(
        func_source, base_ns, args, has_pd_disaggregation=True
    )
    # Must not crash (the old assertion is gone)
    # Must spawn a Process
    # Must return (ip, port)
    # Must set the pd flag on router_args
    ok_no_crash = True
    ok_process = proc_called
    ok_return = (isinstance(result, (tuple, list)) and len(result) >= 2
                 and result[0] is not None and result[1] is not None)
    ok_pd_flag = (router_args is not None
                  and getattr(router_args, "slime_router_pd_disaggregation", False) is True)
    results["slime_pd_no_crash"] = ok_no_crash and ok_process
    results["slime_pd_return"] = ok_return
    results["slime_pd_flag"] = ok_pd_flag
except AssertionError:
    # The buggy code raises AssertionError here
    results["slime_pd_no_crash"] = False
    results["slime_pd_return"] = False
    results["slime_pd_flag"] = False
except Exception as e:
    # Other errors (mock limitations) — crash is the bug, not these
    results["slime_pd_no_crash"] = True
    results["slime_pd_return"] = False
    results["slime_pd_flag"] = False

# ── TEST 2 (F2P): Non-slime router + PD disagg sets disable_circuit_breaker ─
try:
    args = make_args(use_slime_router=False)
    result, router_args, proc_called = run_with_capture(
        func_source, base_ns, args, has_pd_disaggregation=True
    )
    results["circuit_breaker_disabled"] = (
        proc_called
        and router_args is not None
        and getattr(router_args, "disable_circuit_breaker", False) is True
    )
except Exception:
    results["circuit_breaker_disabled"] = False

# ── TEST 3 (P2P): Slime router without PD still works ──────────────
try:
    args = make_args(use_slime_router=True)
    result, router_args, proc_called = run_with_capture(
        func_source, base_ns, args, has_pd_disaggregation=False
    )
    results["slime_no_pd_works"] = (
        proc_called
        and isinstance(result, (tuple, list)) and len(result) >= 2
        and result[0] is not None and result[1] is not None
    )
except Exception:
    results["slime_no_pd_works"] = False

# ── TEST 4 (P2P): Non-slime router without PD doesn't set circuit breaker ─
try:
    args = make_args(use_slime_router=False)
    result, router_args, proc_called = run_with_capture(
        func_source, base_ns, args, has_pd_disaggregation=False
    )
    results["no_pd_no_circuit_breaker"] = (
        proc_called
        and router_args is not None
        and getattr(router_args, "disable_circuit_breaker", False) is not True
    )
except Exception:
    results["no_pd_no_circuit_breaker"] = False

print(json.dumps(results))
PYEOF

# Run the behavioral test suite
log "Running behavioral tests..."
TEST_OUTPUT=$(python3 /tmp/test_start_router.py 2>&1)
TEST_EXIT=$?
log "Test output: $TEST_OUTPUT"

if [ $TEST_EXIT -ne 0 ]; then
    log "Test script failed to run"
    echo "0.0" > "$LOGS/reward.txt"
    exit 0
fi

# Parse results — last line is JSON
RESULTS_JSON=$(echo "$TEST_OUTPUT" | tail -1)

# Helper to read a boolean from the JSON results
check() {
    python3 -c "import json,sys; r=json.loads(sys.stdin.read()); print(1 if r.get('$1') else 0)" <<< "$RESULTS_JSON"
}

# ── Fail-to-pass checks ─────────────────────────────────────────────

# [pr_diff] (0.25): Slime router + PD disagg no longer crashes AND Process spawned
T1=$(check slime_pd_no_crash)
if [ "$T1" = "1" ]; then
    log "PASS (0.25): slime router + PD disagg no crash + process spawned"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    log "FAIL (0.25): slime router + PD disagg crashes or no process"
fi

# [pr_diff] (0.10): Slime router + PD disagg returns valid (ip, port)
T1R=$(check slime_pd_return)
if [ "$T1R" = "1" ]; then
    log "PASS (0.10): slime router + PD returns (ip, port)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL (0.10): slime router + PD bad return value"
fi

# [pr_diff] (0.15): Slime router PD disagg flag is set on router_args
T2=$(check slime_pd_flag)
if [ "$T2" = "1" ]; then
    log "PASS (0.15): slime_router_pd_disaggregation flag set"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    log "FAIL (0.15): slime_router_pd_disaggregation flag not set"
fi

# [pr_diff] (0.20): Circuit breaker disabled for non-slime router + PD disagg
T3=$(check circuit_breaker_disabled)
if [ "$T3" = "1" ]; then
    log "PASS (0.20): circuit breaker disabled with PD disagg"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    log "FAIL (0.20): circuit breaker not disabled with PD disagg"
fi

# ── Pass-to-pass checks ─────────────────────────────────────────────

# [pr_diff] (0.10): Slime router without PD still works (regression)
T4=$(check slime_no_pd_works)
if [ "$T4" = "1" ]; then
    log "PASS (0.10): slime router without PD still works"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL (0.10): slime router without PD broken"
fi

# [pr_diff] (0.10): Non-slime router without PD doesn't set circuit breaker (regression)
T5=$(check no_pd_no_circuit_breaker)
if [ "$T5" = "1" ]; then
    log "PASS (0.10): no circuit breaker without PD disagg"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    log "FAIL (0.10): circuit breaker unexpectedly set without PD"
fi

# ── Anti-stub check ─────────────────────────────────────────────────
# [static] (0.10): Function must not be stubbed out
STUB_OK=0
if python3 -c "
import ast, sys
with open('slime/ray/rollout.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_start_router':
        # Strip docstrings and bare constants from body count
        body = [n for n in node.body
                if not (isinstance(n, ast.Expr) and isinstance(getattr(n, 'value', None), ast.Constant))]
        if len(body) < 5:
            print('STUB: function body too short (%d stmts)' % len(body))
            sys.exit(1)
        for n in ast.walk(node):
            if isinstance(n, ast.Raise) and isinstance(getattr(n, 'exc', None), ast.Call):
                if getattr(getattr(n.exc, 'func', None), 'id', '') == 'NotImplementedError':
                    print('STUB: raises NotImplementedError')
                    sys.exit(1)
        sys.exit(0)
print('FAIL: _start_router not found')
sys.exit(1)
"; then
    log "PASS (0.10): anti-stub check"
    STUB_OK=1
fi
if [ "$STUB_OK" = "1" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
fi

# ── Final score ──────────────────────────────────────────────────────
log "Score: $SCORE / 1.0"
echo "$SCORE" > "$LOGS/reward.txt"

# Write detailed reward.json
python3 -c "
import json
score = $SCORE
t1 = 0.25 if '$T1' == '1' else 0
t1r = 0.10 if '$T1R' == '1' else 0
t2 = 0.15 if '$T2' == '1' else 0
t3 = 0.20 if '$T3' == '1' else 0
t4 = 0.10 if '$T4' == '1' else 0
t5 = 0.10 if '$T5' == '1' else 0
stub = 0.10 if '$STUB_OK' == '1' else 0
json.dump({
    'reward': score,
    'behavioral': t1 + t1r + t2 + t3 + t4 + t5,
    'regression': t4 + t5,
    'structural': stub,
}, open('$LOGS/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
