#!/usr/bin/env bash
# Verifier for sglang-detokenizer-unbound-fix
# Task: fix UnboundLocalError in run_detokenizer_process() when
#        DetokenizerManager constructor fails
# File: python/sglang/srt/managers/detokenizer_manager.py

set +e

PASS=0
TOTAL=4
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

# ── TEST 1: manager initialized to None before try block ─────────────────
echo ""
echo "TEST 1/4: manager initialized to None before try block"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find run_detokenizer_process function
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        # Look for `manager = None` assignment before the try block
        found_none_init = False
        first_try_lineno = None

        for stmt in node.body:
            if isinstance(stmt, ast.Try):
                first_try_lineno = stmt.lineno
                break

        if first_try_lineno is None:
            print("FAIL: no try block found in run_detokenizer_process")
            sys.exit(1)

        for stmt in node.body:
            if stmt.lineno >= first_try_lineno:
                break
            # Check for `manager = None`
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "manager":
                        if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                            found_none_init = True

        if found_none_init:
            print("PASS: manager = None found before try block")
            sys.exit(0)
        else:
            print("FAIL: manager is not initialized to None before the try block")
            sys.exit(1)

print("FAIL: run_detokenizer_process function not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

# ── TEST 2: except block guards manager with None check ──────────────────
echo ""
echo "TEST 2/4: except block checks manager is not None before calling methods"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "run_detokenizer_process":
        # Find the try/except block
        for stmt in node.body:
            if not isinstance(stmt, ast.Try):
                continue
            # Check exception handlers
            for handler in stmt.handlers:
                handler_src = ast.get_source_segment(source, handler)
                if handler_src is None:
                    # Fallback: check lines
                    lines = source.splitlines()
                    handler_src = "\n".join(lines[handler.lineno - 1:handler.end_lineno])

                # Check for a guard: `if manager is not None` or `if manager`
                has_guard = False
                for sub in ast.walk(handler):
                    if isinstance(sub, ast.If):
                        test = sub.test
                        # `if manager is not None`
                        if isinstance(test, ast.Compare):
                            if (isinstance(test.left, ast.Name) and test.left.id == "manager"
                                and any(isinstance(op, ast.IsNot) for op in test.ops)):
                                has_guard = True
                            elif (isinstance(test.left, ast.Name) and test.left.id == "manager"
                                  and any(isinstance(op, ast.Is) for op in test.ops)):
                                # `if manager is None` with else block also valid
                                # but less likely; skip for now
                                pass
                        # `if manager:` (truthy check)
                        elif isinstance(test, ast.Name) and test.id == "manager":
                            has_guard = True

                if has_guard:
                    print("PASS: except block guards manager with None check")
                    sys.exit(0)

                # Also accept: hasattr(manager, ...) or try/except around the call
                for sub in ast.walk(handler):
                    if isinstance(sub, ast.Call):
                        if isinstance(sub.func, ast.Name) and sub.func.id == "hasattr":
                            if sub.args and isinstance(sub.args[0], ast.Name) and sub.args[0].id == "manager":
                                has_guard = True
                    if isinstance(sub, ast.Try):
                        # Nested try around manager call is also acceptable
                        for nested_handler in sub.handlers:
                            for nh_node in ast.walk(nested_handler):
                                if isinstance(nh_node, ast.Name) and nh_node.id == "UnboundLocalError":
                                    has_guard = True
                                if isinstance(nh_node, ast.Name) and nh_node.id == "NameError":
                                    has_guard = True

                if has_guard:
                    print("PASS: except block guards manager access")
                    sys.exit(0)

                print("FAIL: no None guard found for manager in except block")
                sys.exit(1)

        print("FAIL: no try/except found in run_detokenizer_process")
        sys.exit(1)

print("FAIL: run_detokenizer_process function not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

# ── TEST 3: anti-stub check — file still contains original logic ─────────
echo ""
echo "TEST 3/4: anti-stub — file retains original logic (psutil, signal, logger)"
python3 << 'PYEOF'
import sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

required = ["psutil", "signal", "logger", "DetokenizerManager", "maybe_clear_socket_mapping",
            "run_detokenizer_process", "parent_process", "SIGQUIT"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

# Check file is not trivially short (original is ~450 lines)
line_count = len(source.splitlines())
if line_count < 200:
    print(f"FAIL: file has only {line_count} lines — looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

# ── TEST 4: behavioral — simulate constructor failure path ────────────────
echo ""
echo "TEST 4/4: behavioral — constructor failure does not raise UnboundLocalError"
python3 << 'PYEOF'
import ast, sys, textwrap

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

# Build a test that simulates the constructor failing.
# We mock out all dependencies and make the constructor raise.
test_code = '''
import types, signal

# Mock psutil
psutil_mock = types.ModuleType("psutil")
class MockProcess:
    def __init__(self):
        pass
    def parent(self):
        return self
    def send_signal(self, sig):
        pass
psutil_mock.Process = MockProcess

# Mock logger
class MockLogger:
    def error(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
mock_logger = MockLogger()

# Mock configure_logger
def mock_configure_logger(*a, **kw):
    pass

# Mock get_exception_traceback
def mock_get_traceback():
    return "mock traceback"

# A constructor class that always fails
class FailingManager:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("simulated constructor failure")
    def maybe_clear_socket_mapping(self):
        pass

# Mock server_args and port_args
class MockArgs:
    tokenizer_worker_num = 1

raised_unbound = False
try:
    # We need to exec the function with mocks
    exec_globals = {
        "psutil": psutil_mock,
        "logger": mock_logger,
        "configure_logger": mock_configure_logger,
        "get_exception_traceback": mock_get_traceback,
        "signal": signal,
    }
''' + f'''
    func_source = """{func_src}"""
''' + '''
    exec(func_source, exec_globals)

    # Call it with FailingManager as the class
    try:
        exec_globals["run_detokenizer_process"](MockArgs(), MockArgs(), FailingManager)
    except SystemExit:
        pass  # some versions may sys.exit
    except RuntimeError:
        pass  # constructor failure propagated -- that's fine as long as no UnboundLocalError
except UnboundLocalError as e:
    raised_unbound = True
except NameError as e:
    if "manager" in str(e):
        raised_unbound = True
except Exception as e:
    # Other exceptions are OK -- we only care about UnboundLocalError
    pass

if raised_unbound:
    print("FAIL: UnboundLocalError raised when constructor fails")
    import sys; sys.exit(1)
else:
    print("PASS: no UnboundLocalError when constructor fails")
    import sys; sys.exit(0)
'''

try:
    exec(test_code)
except SystemExit as e:
    sys.exit(e.code)
except Exception as e:
    print(f"FAIL: test harness error: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
echo "Results: $PASS / $TOTAL tests passed"
echo "================================"

REWARD=$(python3 -c "print('{:.4f}'.format(min($PASS/float($TOTAL), 1.0)))")
echo "Reward: $REWARD"
echo "$REWARD" > "$REWARD_FILE"
