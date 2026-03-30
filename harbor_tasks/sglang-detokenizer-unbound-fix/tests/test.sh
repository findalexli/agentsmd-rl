#!/usr/bin/env bash
# Verifier for sglang-detokenizer-unbound-fix
# Task: fix UnboundLocalError in run_detokenizer_process() when
#        DetokenizerManager constructor fails
# File: python/sglang/srt/managers/detokenizer_manager.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py"

echo "=== sglang detokenizer unbound fix verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAVIORAL_UNBOUND=0.35
W_BEHAVIORAL_EXCEPT_COMPLETES=0.30
W_PASSTOPASS=0.10
W_STRUCTURAL=0.10
W_ANTISTUB=0.05
W_CONFIG=0.10

SCORE="0.0"

# ── TEST 1 (PRIMARY): behavioral — constructor failure must NOT raise UnboundLocalError ──
echo ""
echo "TEST 1: behavioral — constructor failure does not raise UnboundLocalError (weight=$W_BEHAVIORAL_UNBOUND)"
T1=$(python3 << 'PYEOF'
import ast, sys, textwrap, types, signal

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

# Extract run_detokenizer_process function source
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        func_node = node
        break

if func_node is None:
    print("FAIL: run_detokenizer_process not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

# A constructor that always fails
class FailingManager:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("simulated constructor failure")
    def maybe_clear_socket_mapping(self):
        pass

# Mock psutil — Process().parent() returns object with send_signal
psutil_mock = types.ModuleType("psutil")
class MockProcess:
    def __init__(self): pass
    def parent(self): return self
    def send_signal(self, sig): pass
psutil_mock.Process = MockProcess

# Mock logger
class MockLogger:
    def error(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

# Mock setproctitle module
setproctitle_mock = types.SimpleNamespace(setproctitle=lambda t: None)

class MockArgs:
    tokenizer_worker_num = 1

# Build exec namespace with all names the function definition and body may reference:
# - DetokenizerManager: used as default param value in the signature
# - ServerArgs, PortArgs: used as type annotations in the signature
# - kill_itself_when_parent_died, setproctitle, configure_logger: called in body
# - psutil, signal, logger, get_exception_traceback: used in body
exec_globals = {
    "DetokenizerManager": FailingManager,
    "ServerArgs": MockArgs,
    "PortArgs": MockArgs,
    "kill_itself_when_parent_died": lambda: None,
    "setproctitle": setproctitle_mock,
    "psutil": psutil_mock,
    "logger": MockLogger(),
    "configure_logger": lambda *a, **kw: None,
    "get_exception_traceback": lambda: "mock traceback",
    "signal": signal,
    "__builtins__": __builtins__,
}

exec(func_src, exec_globals)

raised_unbound = False
try:
    # Pass FailingManager explicitly as the detokenizer_manager_class argument
    exec_globals["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except UnboundLocalError as e:
    raised_unbound = True
except NameError as e:
    if "manager" in str(e):
        raised_unbound = True
except SystemExit:
    pass  # acceptable
except Exception:
    pass  # other errors are fine — only UnboundLocalError matters

if raised_unbound:
    print("FAIL: UnboundLocalError raised when constructor fails")
    sys.exit(1)
else:
    print("PASS: no UnboundLocalError when constructor fails")
    sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_UNBOUND)")
fi

# ── TEST 2 (PRIMARY): behavioral — except block runs to completion on constructor failure ──
echo ""
echo "TEST 2: behavioral — except block completes without crash on constructor failure (weight=$W_BEHAVIORAL_EXCEPT_COMPLETES)"
T2=$(python3 << 'PYEOF'
import ast, sys, textwrap, types, signal

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        func_node = node
        break

if func_node is None:
    print("FAIL: run_detokenizer_process not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

# A constructor that always fails
class FailingManager:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("simulated constructor failure")
    def maybe_clear_socket_mapping(self):
        pass

# Mock logger that records calls
error_messages = []
class RecordingLogger:
    def error(self, *a, **kw): error_messages.append(a)
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

# Track whether the except block sent the parent signal
parent_signal_sent = []

# Mock psutil with tracking
psutil_mock = types.ModuleType("psutil")
class MockProcessTracked:
    def __init__(self): pass
    def parent(self):
        p = types.SimpleNamespace()
        p.send_signal = lambda sig: parent_signal_sent.append(sig)
        return p
    def send_signal(self, sig):
        parent_signal_sent.append(sig)
psutil_mock.Process = MockProcessTracked

# Mock setproctitle module
setproctitle_mock = types.SimpleNamespace(setproctitle=lambda t: None)

class MockArgs:
    tokenizer_worker_num = 1

# Build exec namespace with all names the function definition and body may reference
exec_globals = {
    "DetokenizerManager": FailingManager,
    "ServerArgs": MockArgs,
    "PortArgs": MockArgs,
    "kill_itself_when_parent_died": lambda: None,
    "setproctitle": setproctitle_mock,
    "psutil": psutil_mock,
    "logger": RecordingLogger(),
    "configure_logger": lambda *a, **kw: None,
    "get_exception_traceback": lambda: "mock traceback",
    "signal": signal,
    "__builtins__": __builtins__,
}

exec(func_src, exec_globals)

try:
    # Pass FailingManager explicitly as the detokenizer_manager_class argument
    exec_globals["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except SystemExit:
    pass
except UnboundLocalError:
    print("FAIL: except block crashed with UnboundLocalError — did not complete")
    sys.exit(1)
except NameError as e:
    if "manager" in str(e):
        print("FAIL: except block crashed with NameError on 'manager' — did not complete")
        sys.exit(1)
except Exception:
    pass  # other exceptions may propagate, that's ok

# The except block should have logged the error and/or sent the parent signal.
# At least one of these should have happened if the except block ran to completion.
if error_messages or parent_signal_sent:
    print("PASS: except block ran to completion (logged error or sent parent signal)")
    sys.exit(0)
else:
    # Even if neither was recorded, if we got here without UnboundLocalError that's
    # still a partial success — but the except block may not have run fully.
    # Accept it: the key fix is no crash.
    print("PASS: no crash in except block (cleanup may differ from original)")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_EXCEPT_COMPLETES)")
fi

# ── TEST 3 (SECONDARY): pass-to-pass — function is still callable structure ──
echo ""
echo "TEST 3: pass-to-pass — function signature and structure intact (weight=$W_PASSTOPASS)"
T3=$(python3 << 'PYEOF'
import ast, sys, inspect

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        func_node = node
        break

if func_node is None:
    print("FAIL: run_detokenizer_process function not found")
    sys.exit(1)

# Check it has the expected parameters (server_args, port_args, and the manager class)
arg_names = [a.arg for a in func_node.args.args]
if len(arg_names) < 2:
    print(f"FAIL: expected at least 2 params, got {arg_names}")
    sys.exit(1)

# Check there is a try/except block in the function
has_try = False
for stmt in func_node.body:
    if isinstance(stmt, ast.Try):
        has_try = True
        break

if not has_try:
    print("FAIL: function lost its try/except structure")
    sys.exit(1)

# Check function body is non-trivial (not just pass/return)
if len(func_node.body) < 3:
    print("FAIL: function body too short — may be stubbed")
    sys.exit(1)

print("PASS: function signature and structure intact")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_PASSTOPASS)")
fi

# ── TEST 4 (SUPPLEMENTARY): light structural — function exists with try/except ──
echo ""
echo "TEST 4: structural — run_detokenizer_process has try/except with handler (weight=$W_STRUCTURAL)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        for stmt in node.body:
            if isinstance(stmt, ast.Try) and len(stmt.handlers) > 0:
                # Check the except handler references "manager" somewhere
                # (it should use manager in some way — clearing sockets, etc.)
                handler_src_lines = source.splitlines()[stmt.handlers[0].lineno - 1:stmt.handlers[0].end_lineno]
                handler_text = "\n".join(handler_src_lines)
                if "manager" in handler_text or "maybe_clear" in handler_text:
                    print("PASS: try/except with handler referencing manager found")
                    sys.exit(0)
                else:
                    print("FAIL: except handler does not reference manager at all")
                    sys.exit(1)
        print("FAIL: no try/except with handlers found")
        sys.exit(1)

print("FAIL: run_detokenizer_process not found")
sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL)")
fi

# ── TEST 5: anti-stub check — file retains original logic ──
echo ""
echo "TEST 5: anti-stub — file retains original logic (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

required = ["psutil", "signal", "logger", "DetokenizerManager", "maybe_clear_socket_mapping",
            "run_detokenizer_process", "parent_process", "SIGQUIT"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 200:
    print(f"FAIL: file has only {line_count} lines — looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# ── TEST 6: Config-derived — new test files have main guard (weight=$W_CONFIG) ──
# Config-derived test (0.10): "Has `if __name__ == '__main__': unittest.main()`"
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ 17f43d15187be710828a1ff6a4843fdddb0b1eb7
echo ""
echo "TEST 6: config-derived — new test files have main guard (weight=$W_CONFIG)"
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
T6="PASS"
if [ -z "$NEW_TEST_FILES" ]; then
    echo "PASS (no new test files added)"
else
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "FAIL: $tf missing main guard"
            T6="FAIL"
        fi
    done
    echo "$T6"
fi
if [ "$T6" = "PASS" ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
