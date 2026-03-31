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
W_BEHAVIORAL_SIGQUIT=0.25
W_BEHAVIORAL_EXCEPT_COMPLETES=0.15
W_PASSTOPASS=0.10
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

# ── TEST 2 (PRIMARY): behavioral — SIGQUIT must be sent to parent on constructor failure ──
# [pr_diff] (0.25): Critical fix - parent_process.send_signal(signal.SIGQUIT) must execute
echo ""
echo "TEST 2: behavioral — SIGQUIT sent to parent when constructor fails (weight=$W_BEHAVIORAL_SIGQUIT)"
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

# Track whether the parent signal was sent with SIGQUIT
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

# Mock logger
class MockLogger:
    def error(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

setproctitle_mock = types.SimpleNamespace(setproctitle=lambda t: None)

class MockArgs:
    tokenizer_worker_num = 1

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

try:
    exec_globals["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except SystemExit:
    pass
except Exception:
    pass

# CRITICAL: SIGQUIT must have been sent - this is the core bug fix
if signal.SIGQUIT in parent_signal_sent:
    print("PASS: SIGQUIT sent to parent on constructor failure")
    sys.exit(0)
else:
    print(f"FAIL: SIGQUIT not sent to parent. Signals sent: {parent_signal_sent}")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_SIGQUIT)")
fi

# ── TEST 3 (SECONDARY): behavioral — except block error logging ──
echo ""
echo "TEST 3: behavioral — error is logged when constructor fails (weight=$W_BEHAVIORAL_EXCEPT_COMPLETES)"
T3=$(python3 << 'PYEOF'
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

class FailingManager:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("simulated constructor failure")
    def maybe_clear_socket_mapping(self):
        pass

# Mock logger that records error calls
error_messages = []
class RecordingLogger:
    def error(self, *a, **kw): error_messages.append(a)
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

psutil_mock = types.ModuleType("psutil")
class MockProcess:
    def __init__(self): pass
    def parent(self): return self
    def send_signal(self, sig): pass
psutil_mock.Process = MockProcess

setproctitle_mock = types.SimpleNamespace(setproctitle=lambda t: None)

class MockArgs:
    tokenizer_worker_num = 1

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
    exec_globals["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
except SystemExit:
    pass
except Exception:
    pass

if error_messages:
    print("PASS: error logged when constructor fails")
    sys.exit(0)
else:
    print("FAIL: no error logged")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_EXCEPT_COMPLETES)")
fi

# ── TEST 4 (PASS-TO-PASS): function structure maintained ──
echo ""
echo "TEST 4: pass-to-pass — function signature and structure intact (weight=$W_PASSTOPASS)"
T4=$(python3 << 'PYEOF'
import ast, sys

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

# Check it has the expected parameters (at least server_args, port_args)
arg_names = [a.arg for a in func_node.args.args]
if len(arg_names) < 2:
    print(f"FAIL: expected at least 2 params, got {arg_names}")
    sys.exit(1)

# Check function body is non-trivial (not just pass/return)
# Allow both try/except and try/except/finally patterns
if len(func_node.body) < 2:
    print("FAIL: function body too short — may be stubbed")
    sys.exit(1)

# Check there's error handling of some form
has_error_handling = False
for stmt in func_node.body:
    if isinstance(stmt, ast.Try):
        has_error_handling = True
        break

if not has_error_handling:
    print("FAIL: function lost its error handling structure")
    sys.exit(1)

print("PASS: function signature and structure intact")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_PASSTOPASS)")
fi

# ── TEST 5: anti-stub check — file retains original logic ──
# [pr_diff] (0.05): File should contain proper socket cleanup logic
echo ""
echo "TEST 5: anti-stub — file retains original logic (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

# Check that run_detokenizer_process exists and has real implementation
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        func_node = node
        break

if func_node is None:
    print("FAIL: run_detokenizer_process not found")
    sys.exit(1)

# Count non-pass/non-docstring statements in function body
meaningful_stmts = 0
for stmt in func_node.body:
    if isinstance(stmt, ast.Pass):
        continue
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
        # Docstring
        continue
    meaningful_stmts += 1
    # Recursively count in try blocks
    if isinstance(stmt, ast.Try):
        for try_stmt in stmt.body:
            if not isinstance(try_stmt, ast.Pass):
                meaningful_stmts += 1

if meaningful_stmts < 3:
    print(f"FAIL: function has only {meaningful_stmts} meaningful statements — looks like a stub")
    sys.exit(1)

# Check for essential function references using AST (not string matching)
# to avoid false positives from comments
try_block_found = False
except_block_found = False
cleanup_found = False

for stmt in func_node.body:
    if isinstance(stmt, ast.Try):
        try_block_found = True
        # Check except handlers exist
        if stmt.handlers:
            except_block_found = True
        # Check for cleanup logic (maybe_clear_socket_mapping or similar)
        for handler in stmt.handlers:
            for handler_stmt in handler.body:
                handler_src = ast.unparse(handler_stmt) if hasattr(ast, 'unparse') else ""
                if "maybe_clear" in handler_src or ("manager" in handler_src and "None" in handler_src):
                    cleanup_found = True
        # Also check finally block if present
        if stmt.finalbody:
            for fin_stmt in stmt.finalbody:
                fin_src = ast.unparse(fin_stmt) if hasattr(ast, 'unparse') else ""
                if "maybe_clear" in fin_src or ("manager" in fin_src and "None" in fin_src):
                    cleanup_found = True

if not try_block_found:
    print("FAIL: no try block found")
    sys.exit(1)

if not except_block_found:
    print("FAIL: no except handler found")
    sys.exit(1)

# Ensure file isn't drastically shortened
line_count = len(source.splitlines())
if line_count < 150:
    print(f"FAIL: file has only {line_count} lines — looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines with proper error handling structure")
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
