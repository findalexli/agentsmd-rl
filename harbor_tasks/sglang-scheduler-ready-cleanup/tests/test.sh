#!/usr/bin/env bash
set -euo pipefail

ENGINE_FILE="/workspace/python/sglang/srt/entrypoints/engine.py"
REWARD=0

add_score() {
    REWARD=$(python3 -c "print($REWARD + $1)")
}

# Helper: extract _wait_for_scheduler_ready (and any helpers it calls) from
# engine.py without importing the module (which pulls in torch, numpy, etc.)
cat > /tmp/extract_func.py << 'PYEOF'
import ast, textwrap

def extract_functions(filepath):
    """Extract _wait_for_scheduler_ready and nearby helper functions from engine.py.

    Returns the source code as a string that can be exec'd.
    """
    with open(filepath) as f:
        source = f.read()

    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    # Find _wait_for_scheduler_ready and any module-level functions it might call
    # (e.g. _scheduler_died_error). Extract all functions near it.
    target_names = set()
    func_ranges = {}

    # First pass: find all top-level function defs
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_ranges[node.name] = (node.lineno - 1, node.end_lineno)

    # Find our target
    if "_wait_for_scheduler_ready" not in func_ranges:
        raise RuntimeError("_wait_for_scheduler_ready not found")

    target_names.add("_wait_for_scheduler_ready")

    # Find what it calls — look for Name nodes that match other top-level functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and child.id in func_ranges:
                    target_names.add(child.id)

    # Also grab any function whose name starts with _ and is right before our target
    # (common pattern for helper functions)
    wait_start = func_ranges["_wait_for_scheduler_ready"][0]
    for name, (start, end) in func_ranges.items():
        if end >= wait_start - 3 and start < wait_start:
            target_names.add(name)

    # Extract source for all target functions
    chunks = []
    for name in sorted(target_names, key=lambda n: func_ranges[n][0]):
        start, end = func_ranges[name]
        chunks.append("".join(lines[start:end]))

    # Add required imports; __future__ annotations makes type hints lazy (avoids NameError)
    header = "from __future__ import annotations\nfrom typing import List, Dict\nimport multiprocessing\n\n"
    return header + "\n\n".join(chunks)

if __name__ == "__main__":
    code = extract_functions("/workspace/python/sglang/srt/entrypoints/engine.py")
    with open("/tmp/engine_funcs.py", "w") as f:
        f.write(code)
    print("Extracted functions to /tmp/engine_funcs.py")
PYEOF

# Run extraction once; all tests import from /tmp/engine_funcs.py
if ! python3 /tmp/extract_func.py 2>&1; then
    echo "CRITICAL: Cannot extract test functions from engine.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0.00): File must be valid Python
if python3 -c "import ast; ast.parse(open('$ENGINE_FILE').read())"; then
    echo "GATE PASS: syntax ok"
else
    echo "GATE FAIL: syntax error in engine.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

###############################################################################
# BEHAVIORAL FAIL-TO-PASS (0.65 total)
# These tests FAIL on buggy code, PASS on fixed code.
###############################################################################

# [pr_diff] (0.35): Non-ready rank 0 detected immediately, not after all ranks
# On BUGGY code: rank 0 sends non-ready, rank 1 never sends → hangs polling rank 1
# On FIXED code: rank 0 non-ready detected right after recv → raises immediately
cat > /tmp/test_immediate_status_2rank.py << 'PYEOF'
import multiprocessing
import signal
import sys
sys.path.insert(0, "/tmp")
from engine_funcs import _wait_for_scheduler_ready

class FakeProc:
    def __init__(self, alive=True, exitcode=0):
        self._alive = alive
        self.exitcode = exitcode
    def is_alive(self):
        return self._alive
    def join(self, timeout=None):
        pass

def timeout_handler(signum, frame):
    print("FAIL: timed out — status check deferred, hung on rank 1")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(15)

# Rank 0: sends non-ready status immediately
r0, w0 = multiprocessing.Pipe(duplex=False)
w0.send({"status": "error", "message": "init failed"})

# Rank 1: never sends anything (slow but alive)
r1, w1 = multiprocessing.Pipe(duplex=False)

try:
    _wait_for_scheduler_ready([r0, r1], [FakeProc(), FakeProc()])
    print("FAIL: no exception raised")
    sys.exit(1)
except RuntimeError as e:
    if "Initialization failed" in str(e):
        print("PASS: rank 0 non-ready detected before polling rank 1")
        sys.exit(0)
    else:
        print(f"FAIL: wrong error: {e}")
        sys.exit(1)
PYEOF

if python3 /tmp/test_immediate_status_2rank.py 2>&1; then
    add_score 0.35
    echo "PASS (0.35): immediate status check (2 ranks)"
else
    echo "FAIL (0.35): immediate status check (2 ranks)"
fi

# [pr_diff] (0.30): Mid-rank non-ready detected before reaching later ranks
# On BUGGY code: rank 0 ready, rank 1 non-ready, rank 2 never sends → hangs on rank 2
# On FIXED code: rank 1 non-ready detected right after recv → raises immediately
cat > /tmp/test_immediate_status_3rank.py << 'PYEOF'
import multiprocessing
import signal
import sys
sys.path.insert(0, "/tmp")
from engine_funcs import _wait_for_scheduler_ready

class FakeProc:
    def __init__(self, alive=True, exitcode=0):
        self._alive = alive
        self.exitcode = exitcode
    def is_alive(self):
        return self._alive
    def join(self, timeout=None):
        pass

def timeout_handler(signum, frame):
    print("FAIL: timed out — status check deferred, hung on rank 2")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(15)

# Rank 0: ready
r0, w0 = multiprocessing.Pipe(duplex=False)
w0.send({"status": "ready", "rank": 0})

# Rank 1: non-ready
r1, w1 = multiprocessing.Pipe(duplex=False)
w1.send({"status": "error", "message": "rank 1 init failed"})

# Rank 2: never sends (slow but alive)
r2, w2 = multiprocessing.Pipe(duplex=False)

try:
    _wait_for_scheduler_ready(
        [r0, r1, r2],
        [FakeProc(), FakeProc(), FakeProc()]
    )
    print("FAIL: no exception raised")
    sys.exit(1)
except RuntimeError as e:
    if "Initialization failed" in str(e):
        print("PASS: rank 1 non-ready detected before polling rank 2")
        sys.exit(0)
    else:
        print(f"FAIL: wrong error: {e}")
        sys.exit(1)
PYEOF

if python3 /tmp/test_immediate_status_3rank.py 2>&1; then
    add_score 0.30
    echo "PASS (0.30): immediate status check (3 ranks)"
else
    echo "FAIL (0.30): immediate status check (3 ranks)"
fi

###############################################################################
# PASS-TO-PASS (0.15 total)
# These tests pass on both old and new code — regression checks.
###############################################################################

# [pr_diff] (0.05): EOFError raises descriptive error with rank and exit code
cat > /tmp/test_eoferror.py << 'PYEOF'
import multiprocessing
import sys
sys.path.insert(0, "/tmp")
from engine_funcs import _wait_for_scheduler_ready

class FakeProc:
    def __init__(self, alive=False, exitcode=-9):
        self._alive = alive
        self.exitcode = exitcode
    def is_alive(self):
        return self._alive
    def join(self, timeout=None):
        pass

r0, w0 = multiprocessing.Pipe(duplex=False)
w0.close()

try:
    _wait_for_scheduler_ready([r0], [FakeProc()])
    print("FAIL: did not raise")
    sys.exit(1)
except RuntimeError as e:
    msg = str(e)
    if "Rank 0" in msg and "exit code" in msg:
        print("PASS: EOFError produces descriptive error")
        sys.exit(0)
    else:
        print(f"FAIL: error not descriptive: {msg}")
        sys.exit(1)
PYEOF

if python3 /tmp/test_eoferror.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): EOFError error message"
else
    echo "FAIL (0.05): EOFError error message"
fi

# [pr_diff] (0.05): Dead process detected during poll timeout
cat > /tmp/test_dead_proc.py << 'PYEOF'
import sys
sys.path.insert(0, "/tmp")
from engine_funcs import _wait_for_scheduler_ready

class FakeProc:
    def __init__(self, alive=False, exitcode=-9):
        self._alive = alive
        self.exitcode = exitcode
    def is_alive(self):
        return self._alive
    def join(self, timeout=None):
        pass

class SlowPipeReader:
    def poll(self, timeout=None):
        return False

try:
    _wait_for_scheduler_ready([SlowPipeReader()], [FakeProc()])
    print("FAIL: did not raise")
    sys.exit(1)
except RuntimeError as e:
    msg = str(e)
    if "Rank 0" in msg and "died during initialization" in msg:
        print("PASS: dead process detected")
        sys.exit(0)
    else:
        print(f"FAIL: wrong error: {msg}")
        sys.exit(1)
PYEOF

if python3 /tmp/test_dead_proc.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): dead process detection"
else
    echo "FAIL (0.05): dead process detection"
fi

# [pr_diff] (0.05): Happy path — all ranks report ready
cat > /tmp/test_happy_path.py << 'PYEOF'
import multiprocessing
import sys
sys.path.insert(0, "/tmp")
from engine_funcs import _wait_for_scheduler_ready

class FakeProc:
    def __init__(self):
        self.exitcode = None
    def is_alive(self):
        return True
    def join(self, timeout=None):
        pass

r0, w0 = multiprocessing.Pipe(duplex=False)
r1, w1 = multiprocessing.Pipe(duplex=False)
w0.send({"status": "ready", "rank": 0})
w1.send({"status": "ready", "rank": 1})

result = _wait_for_scheduler_ready([r0, r1], [FakeProc(), FakeProc()])
assert len(result) == 2, f"Expected 2, got {len(result)}"
assert result[0]["rank"] == 0
assert result[1]["rank"] == 1
print("PASS: happy path works")
PYEOF

if python3 /tmp/test_happy_path.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): happy path"
else
    echo "FAIL (0.05): happy path"
fi

###############################################################################
# STRUCTURAL (0.15 total)
###############################################################################

# [pr_diff] (0.10): Error message not duplicated in _wait_for_scheduler_ready
# WHY AST: checks code organization (DRY), not runtime behavior
cat > /tmp/test_dedup.py << 'PYEOF'
import ast
import sys

with open("/workspace/python/sglang/srt/entrypoints/engine.py") as f:
    source = f.read()

for node in ast.walk(ast.parse(source)):
    if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
        func_src = ast.get_source_segment(source, node)
        count = func_src.count("scheduler died during initialization")
        if count <= 1:
            print(f"PASS: error message appears {count} time(s) — deduplicated")
            sys.exit(0)
        else:
            print(f"FAIL: error message appears {count} times — duplicated")
            sys.exit(1)

print("FAIL: function not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_dedup.py 2>&1; then
    add_score 0.10
    echo "PASS (0.10): error message deduplicated"
else
    echo "FAIL (0.10): error message deduplicated"
fi

# [pr_diff] (0.05): Poll-timeout dead-process check not nested inside else clause
# On BUGGY code: the dead-process for-loop is inside "else:" (only runs when poll returns False via else)
# On FIXED code: the dead-process for-loop runs at the while-loop level after poll timeout
cat > /tmp/test_no_else_nesting.py << 'PYEOF'
import ast
import sys

with open("/workspace/python/sglang/srt/entrypoints/engine.py") as f:
    source = f.read()

tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
        # Walk the function body looking for while loops
        for child in ast.walk(node):
            if isinstance(child, ast.While):
                # Check if the while loop has an orelse block containing
                # the dead-process check (the buggy pattern)
                if child.orelse:
                    # If there's an else clause on the while loop, that's fine
                    # (while/else is different). Check for For+else on the If.
                    pass
                # Check for if/else pattern: if poll(): ... else: <dead-check>
                for stmt in child.body:
                    if isinstance(stmt, ast.If):
                        if stmt.orelse:
                            # Check if else body contains is_alive check
                            else_src = ast.get_source_segment(source, stmt)
                            if else_src and "is_alive" in else_src and "else:" in else_src:
                                print("FAIL: dead-process check is nested inside else clause")
                                sys.exit(1)

        print("PASS: dead-process check not nested in else")
        sys.exit(0)

print("FAIL: function not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_no_else_nesting.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): no else nesting for dead-process check"
else
    echo "FAIL (0.05): no else nesting for dead-process check"
fi

# [pr_diff] (0.05): Anti-stub — function has meaningful implementation
cat > /tmp/test_antistub.py << 'PYEOF'
import ast
import sys

with open("/workspace/python/sglang/srt/entrypoints/engine.py") as f:
    source = f.read()

for node in ast.walk(ast.parse(source)):
    if isinstance(node, ast.FunctionDef) and node.name == "_wait_for_scheduler_ready":
        body_lines = node.end_lineno - node.lineno
        if body_lines >= 10:
            print(f"PASS: {body_lines} lines — not stubbed")
            sys.exit(0)
        else:
            print(f"FAIL: only {body_lines} lines — likely stubbed")
            sys.exit(1)

print("FAIL: function not found")
sys.exit(1)
PYEOF

if python3 /tmp/test_antistub.py 2>&1; then
    add_score 0.05
    echo "PASS (0.05): anti-stub"
else
    echo "FAIL (0.05): anti-stub"
fi

###############################################################################
# Write reward
###############################################################################

echo ""
echo "=== SCORE: $REWARD / 1.0 ==="
echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
json.dump({
    'reward': $REWARD,
    'behavioral': 0.65,
    'regression': 0.15,
    'structural': 0.20,
    'config': 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
