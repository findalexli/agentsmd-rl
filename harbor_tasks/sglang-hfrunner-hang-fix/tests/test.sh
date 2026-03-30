#!/bin/bash
set +e

PASS=0
TOTAL=5
TARGET="python/sglang/test/runners.py"

mkdir -p /logs/verifier

# ── GATE: Python syntax validity ──────────────────────────────────────
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE: syntax check failed, aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ── TEST 1 (0.35): BEHAVIORAL — forward() does NOT hang when subprocess is dead ──
# This is the critical fail-to-pass test. We extract the forward() method BODY
# via AST, wrap it in a standalone function with a mock self, and verify it
# raises (or returns quickly) rather than blocking forever when the subprocess
# is dead and the output queue is empty.
python3 << 'PYEOF'
import ast, sys, os, signal, textwrap

# Deadman's switch: if this script runs longer than 25s, the test hangs → FAIL
def alarm_handler(signum, frame):
    print("FAIL: forward() hung (SIGALRM after 25s — the bug is NOT fixed)")
    sys.exit(1)

signal.signal(signal.SIGALRM, alarm_handler)
signal.alarm(25)

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find HFRunner class
hfrunner_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        hfrunner_node = node
        break

if hfrunner_node is None:
    print("FAIL: HFRunner class not found")
    sys.exit(1)

# Find forward method
forward_node = None
for item in hfrunner_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "forward":
        forward_node = item
        break

if forward_node is None:
    print("FAIL: forward() method not found in HFRunner")
    sys.exit(1)

# Extract the BODY of the forward method (not the def line / signature)
# This avoids needing DEFAULT_PROMPTS, type annotations, torch, etc.
lines = source.splitlines()
body_start = forward_node.body[0].lineno
body_end = forward_node.end_lineno
body_lines = lines[body_start - 1 : body_end]
body_source = "\n".join(body_lines)

# Determine the indentation of the body so we can dedent it
first_body_line = body_lines[0]
body_indent = len(first_body_line) - len(first_body_line.lstrip())

# Build test script that wraps the body in a function and calls it
test_code = '''\
import multiprocessing as mp
import queue as queue_mod
import sys
import time

class FakeProcess:
    """Simulates a subprocess that has already died."""
    def is_alive(self):
        return False
    @property
    def exitcode(self):
        return 1
    @property
    def pid(self):
        return -1
    def terminate(self):
        pass
    def kill(self):
        pass
    def join(self, timeout=None):
        pass

class FakeSelf:
    def __init__(self):
        self.in_queue = mp.Queue()
        self.out_queue = mp.Queue()
        self.model_proc = FakeProcess()
        self.model_type = "generation"
        self.output_str_only = False

def forward(self, prompts=None, image_data=None, max_new_tokens=8,
            lora_paths=None, token_ids_logprob=None):
FORWARD_BODY

obj = FakeSelf()
try:
    result = forward(obj, prompts=["test prompt"], image_data=None,
                     max_new_tokens=8, lora_paths=None, token_ids_logprob=None)
    # If forward() returned quickly without hanging, that is acceptable
    print("PASS: forward() returned without hanging (returned value)")
    sys.exit(0)
except SystemExit:
    raise
except Exception as e:
    # Fixed code raises an exception — this is the expected behavior
    print(f"PASS: forward() raised {type(e).__name__}: {e}")
    sys.exit(0)
'''

# Re-indent the body to 4 spaces (one level inside the wrapper function)
reindented = []
for line in body_lines:
    if line.strip() == "":
        reindented.append("")
    else:
        reindented.append("    " + line[body_indent:])
body_reindented = "\n".join(reindented)

test_code = test_code.replace("FORWARD_BODY", body_reindented)

test_file = "/tmp/_test_forward_hang.py"
with open(test_file, "w") as f:
    f.write(test_code)

import subprocess
proc = subprocess.run(
    [sys.executable, test_file],
    timeout=20,
    capture_output=True,
    text=True,
)
print(proc.stdout.strip())
if proc.stderr.strip():
    print("stderr:", proc.stderr.strip()[-500:])

signal.alarm(0)

if proc.returncode == 0:
    sys.exit(0)
else:
    print(f"FAIL: test subprocess exited with code {proc.returncode}")
    sys.exit(1)
PYEOF
T1=$?
if [ $T1 -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# ── TEST 2 (0.25): BEHAVIORAL — forward() still works when subprocess produces output ──
# Pass-to-pass: if the queue has data and process is alive, forward() returns it.
python3 << 'PYEOF'
import ast, sys, os, signal

signal.signal(signal.SIGALRM, lambda s,f: (print("FAIL: pass-to-pass test hung"), sys.exit(1)))
signal.alarm(15)

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find HFRunner class
hfrunner_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        hfrunner_node = node
        break

if hfrunner_node is None:
    print("FAIL: HFRunner class not found")
    sys.exit(1)

# Find forward method
forward_node = None
for item in hfrunner_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "forward":
        forward_node = item
        break

if forward_node is None:
    print("FAIL: forward() not found")
    sys.exit(1)

# Extract the BODY of forward (not the signature)
lines = source.splitlines()
body_start = forward_node.body[0].lineno
body_end = forward_node.end_lineno
body_lines = lines[body_start - 1 : body_end]
first_body_line = body_lines[0]
body_indent = len(first_body_line) - len(first_body_line.lstrip())

reindented = []
for line in body_lines:
    if line.strip() == "":
        reindented.append("")
    else:
        reindented.append("    " + line[body_indent:])
body_reindented = "\n".join(reindented)

test_code = '''\
import multiprocessing as mp
import queue as queue_mod
import sys
import time

class FakeAliveProcess:
    """Simulates a subprocess that is alive and healthy."""
    def is_alive(self):
        return True
    @property
    def exitcode(self):
        return None
    @property
    def pid(self):
        return 12345
    def terminate(self):
        pass
    def kill(self):
        pass
    def join(self, timeout=None):
        pass

class FakeSelf:
    def __init__(self):
        self.in_queue = mp.Queue()
        self.out_queue = mp.Queue()
        self.model_proc = FakeAliveProcess()
        self.model_type = "generation"
        self.output_str_only = False

def forward(self, prompts=None, image_data=None, max_new_tokens=8,
            lora_paths=None, token_ids_logprob=None):
FORWARD_BODY

obj = FakeSelf()

# Pre-load the output queue with a result BEFORE calling forward()
expected = {"output": "hello world", "logprobs": [1.0, 2.0]}
obj.out_queue.put(expected)

result = forward(obj, prompts=["test"], image_data=None,
                 max_new_tokens=8, lora_paths=None, token_ids_logprob=None)

if result == expected:
    print("PASS: forward() returned correct result from queue")
    sys.exit(0)
else:
    print(f"FAIL: forward() returned {result!r}, expected {expected!r}")
    sys.exit(1)
'''.replace("FORWARD_BODY", body_reindented)

test_file = "/tmp/_test_forward_passthrough.py"
with open(test_file, "w") as f:
    f.write(test_code)

import subprocess
proc = subprocess.run(
    [sys.executable, test_file],
    timeout=12,
    capture_output=True,
    text=True,
)
print(proc.stdout.strip())
if proc.stderr.strip():
    print("stderr:", proc.stderr.strip()[-300:])

signal.alarm(0)

if proc.returncode == 0:
    sys.exit(0)
else:
    print(f"FAIL: test subprocess exited with code {proc.returncode}")
    sys.exit(1)
PYEOF
T2=$?
if [ $T2 -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# ── TEST 3 (0.15): SUPPLEMENTARY STRUCTURAL — HFRunner.forward() has been modified ──
# Light check: forward() body is no longer just `self.in_queue.put(...); return self.out_queue.get()`
python3 << 'PYEOF'
import ast, sys

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                # Count the number of AST statements in forward body
                # Original buggy version has exactly 2 statements:
                #   self.in_queue.put(...)
                #   return self.out_queue.get()
                body_stmts = len(item.body)
                # Count total AST nodes in the method body (rough complexity measure)
                total_nodes = sum(1 for _ in ast.walk(item))
                if body_stmts > 2 or total_nodes > 20:
                    print(f"PASS: forward() has been modified ({body_stmts} stmts, {total_nodes} AST nodes)")
                    sys.exit(0)
                else:
                    print(f"FAIL: forward() looks unmodified ({body_stmts} stmts, {total_nodes} AST nodes)")
                    sys.exit(1)
        print("FAIL: forward() not found in HFRunner")
        sys.exit(1)

print("FAIL: HFRunner class not found")
sys.exit(1)
PYEOF
T3=$?
if [ $T3 -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# ── TEST 4 (0.10): SUPPLEMENTARY STRUCTURAL — HFRunner class still has required methods ──
python3 << 'PYEOF'
import ast, sys

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        methods = {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
        required = {"__init__", "forward"}
        if required.issubset(methods):
            print(f"PASS: HFRunner has required methods: {methods & required}")
            sys.exit(0)
        else:
            print(f"FAIL: HFRunner missing methods. Found: {methods}, need: {required}")
            sys.exit(1)

print("FAIL: HFRunner class not found")
sys.exit(1)
PYEOF
T4=$?
if [ $T4 -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# ── TEST 5 (0.15): ANTI-STUB — file is substantial and not gutted ──
python3 << 'PYEOF'
import ast, sys

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

line_count = len(source.splitlines())
class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
func_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))

if line_count < 100:
    print(f"FAIL: file only has {line_count} lines — looks like a stub")
    sys.exit(1)

if class_count < 1 or func_count < 5:
    print(f"FAIL: file looks gutted ({class_count} classes, {func_count} functions)")
    sys.exit(1)

print(f"PASS: file is substantial ({line_count} lines, {class_count} classes, {func_count} functions)")
sys.exit(0)
PYEOF
T5=$?
if [ $T5 -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# ── TEST 6 (0.10): Config-derived — new test files have main guard ──
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ 5ef56682b800c3905973c86beeddf1318cedb2a9
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
T6=1
if [ -z "$NEW_TEST_FILES" ]; then
    echo "T6 PASS (no new test files added)"
    T6=0
else
    ALL_OK=1
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "T6 FAIL: $tf missing main guard"
            ALL_OK=0
        fi
    done
    if [ "$ALL_OK" -eq 1 ]; then
        echo "T6 PASS"
        T6=0
    fi
fi

# ── Compute weighted reward ──────────────────────────────────────────
# T1: behavioral hang test          0.35
# T2: behavioral pass-to-pass       0.25
# T3: structural forward modified   0.15
# T4: structural required methods   0.10
# T5: anti-stub                     0.05
# T6: config-derived main guard     0.10
# Total                             1.00
REWARD=$(python3 -c "
w = 0.0
if $T1 == 0: w += 0.35
if $T2 == 0: w += 0.25
if $T3 == 0: w += 0.15
if $T4 == 0: w += 0.10
if $T5 == 0: w += 0.05
if ${T6:-1} == 0: w += 0.10
print(f'{w:.2f}')
")
echo "Score: $REWARD (T1=$T1 T2=$T2 T3=$T3 T4=$T4 T5=$T5 T6=${T6:-1})"
echo "$REWARD" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
