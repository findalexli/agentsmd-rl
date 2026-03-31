#!/bin/bash
set +e

mkdir -p /logs/verifier

TARGET="python/sglang/test/runners.py"

# ── GATE: Python syntax validity ──────────────────────────────────────
# [agent_config] (gate): "All submitted code must be syntactically valid"
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
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# Initialize scores
T1=1  # BEHAVIORAL: forward() raises RuntimeError with exit code message on dead subprocess
T2=1  # BEHAVIORAL: forward() returns result when subprocess alive and output ready
T3=1  # STRUCTURAL: forward() implements polling loop with timeout (not infinite block)
T4=1  # STRUCTURAL: HFRunner has required methods
T5=1  # ANTI-STUB: file is substantial
T6=1  # CONFIG-DERIVED: new test files have main guard

# ── TEST 1 (0.35): BEHAVIORAL — forward() raises proper error on dead subprocess ───
# [pr_diff] (0.35): Hang detection with RuntimeError containing exit code
python3 << 'PYEOF'
import ast, sys, os, signal, textwrap, re, subprocess

def alarm_handler(signum, frame):
    print("FAIL: forward() hung (SIGALRM after 30s - bug NOT fixed)")
    sys.exit(1)

signal.signal(signal.SIGALRM, alarm_handler)
signal.alarm(30)

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
    print("FAIL: forward() method not found")
    sys.exit(1)

# Extract the BODY of forward method
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

# Build test script
test_code = '''\
import multiprocessing as mp
import queue as queue_mod
import sys
import re

class FakeProcess:
    def __init__(self):
        self._alive = False
        self._exitcode = 42
    def is_alive(self):
        return self._alive
    @property
    def exitcode(self):
        return self._exitcode
    @property
    def pid(self):
        return -1
    def terminate(self): pass
    def kill(self): pass
    def join(self, timeout=None): pass

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
    result = forward(obj, prompts=["test"])
    print("FAIL: forward() returned without raising (returned:", result, ")")
    sys.exit(1)
except RuntimeError as e:
    msg = str(e)
    # Verify message contains exit code information
    if "exit code" in msg.lower() or "exitcode" in msg.lower():
        # Extract the exit code from message and verify it matches
        match = re.search(r"(exit code|exitcode)[=\\s]*(\\\\d|-\\\\d)", msg, re.I)
        if match:
            exit_code_in_msg = int(match.group(2))
            if exit_code_in_msg == 42:
                print(f"PASS: forward() raised RuntimeError with correct exit code: {msg}")
                sys.exit(0)
            else:
                print(f"PARTIAL: RuntimeError raised but exit code wrong (got {exit_code_in_msg}, expected 42): {msg}")
                sys.exit(0)  # Still counts as fix, just verify it has exit code
        else:
            print(f"PASS: forward() raised RuntimeError with exit code mention: {msg}")
            sys.exit(0)
    else:
        print(f"FAIL: RuntimeError raised but missing exit code info: {msg}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: forward() raised {type(e).__name__} instead of RuntimeError: {e}")
    sys.exit(1)
'''.replace("FORWARD_BODY", body_reindented)

test_file = "/tmp/_test_forward_hang.py"
with open(test_file, "w") as f:
    f.write(test_code)

proc = subprocess.run([sys.executable, test_file], timeout=25, capture_output=True, text=True)
print(proc.stdout.strip())
if proc.stderr.strip():
    print("stderr:", proc.stderr.strip()[-500:])

signal.alarm(0)
sys.exit(0 if proc.returncode == 0 else 1)
PYEOF
T1=$?

# ── TEST 2 (0.25): BEHAVIORAL — forward() returns result when subprocess healthy ────
# [pr_diff] (0.25): Pass-to-pass: normal operation unchanged
python3 << 'PYEOF'
import ast, sys, os, signal, subprocess

def alarm_handler(signum, frame):
    print("FAIL: pass-to-pass test hung")
    sys.exit(1)

signal.signal(signal.SIGALRM, alarm_handler)
signal.alarm(20)

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

hfrunner_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        hfrunner_node = node
        break

if hfrunner_node is None:
    print("FAIL: HFRunner class not found")
    sys.exit(1)

forward_node = None
for item in hfrunner_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "forward":
        forward_node = item
        break

if forward_node is None:
    print("FAIL: forward() not found")
    sys.exit(1)

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

class FakeAliveProcess:
    def is_alive(self):
        return True
    @property
    def exitcode(self):
        return None
    @property
    def pid(self):
        return 12345
    def terminate(self): pass
    def kill(self): pass
    def join(self, timeout=None): pass

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
expected = {"output": "hello world", "logprobs": [1.0, 2.0]}
obj.out_queue.put(expected)

result = forward(obj, prompts=["test"])

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

proc = subprocess.run([sys.executable, test_file], timeout=15, capture_output=True, text=True)
print(proc.stdout.strip())
if proc.stderr.strip():
    print("stderr:", proc.stderr.strip()[-300:])

signal.alarm(0)
sys.exit(0 if proc.returncode == 0 else 1)
PYEOF
T2=$?

# ── TEST 3 (0.15): STRUCTURAL — forward() implements polling pattern ─────────────────
# [pr_diff] (0.15): Verify while loop with queue.Empty handling and is_alive check
python3 << 'PYEOF'
import ast, sys

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find HFRunner.forward
forward_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                forward_node = item
                break
        break

if forward_node is None:
    print("FAIL: forward() not found")
    sys.exit(1)

# Check for required polling loop pattern:
# 1. While loop (infinite or conditional)
# 2. Try block inside while
# 3. queue.Empty exception handling
# 4. is_alive() check on model_proc

has_while = False
has_try = False
has_queue_empty = False
has_is_alive = False

for node in ast.walk(forward_node):
    # While loop
    if isinstance(node, ast.While):
        has_while = True
    # Try block
    if isinstance(node, ast.Try):
        has_try = True
        # Check for queue.Empty handler (or Exception handler)
        for handler in node.handlers:
            # Check if it's queue.Empty or just Empty (aliased)
            if isinstance(handler.type, ast.Attribute):
                if handler.type.attr == "Empty":
                    has_queue_empty = True
            elif isinstance(handler.type, ast.Name):
                if handler.type.id == "Empty":
                    has_queue_empty = True
    # is_alive() call
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "is_alive":
                has_is_alive = True

# Also check for timeout parameter in queue.get() calls
has_timeout = False
for node in ast.walk(forward_node):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "get":
                # Check for timeout keyword argument
                for kw in node.keywords:
                    if kw.arg == "timeout":
                        has_timeout = True

score = 0
if has_while: score += 1
if has_try: score += 1
if has_queue_empty: score += 1
if has_is_alive: score += 1
if has_timeout: score += 1

# Need at least 4 of 5 indicators
if score >= 4:
    print(f"PASS: forward() has polling pattern (score: {score}/5)")
    print(f"  - While loop: {has_while}")
    print(f"  - Try block: {has_try}")
    print(f"  - queue.Empty handler: {has_queue_empty}")
    print(f"  - is_alive check: {has_is_alive}")
    print(f"  - timeout param: {has_timeout}")
    sys.exit(0)
else:
    print(f"FAIL: Missing polling pattern (score: {score}/5)")
    print(f"  - While loop: {has_while}")
    print(f"  - Try block: {has_try}")
    print(f"  - queue.Empty handler: {has_queue_empty}")
    print(f"  - is_alive check: {has_is_alive}")
    print(f"  - timeout param: {has_timeout}")
    sys.exit(1)
PYEOF
T3=$?

# ── TEST 4 (0.10): STRUCTURAL — HFRunner has required methods ────────────────────────
# [pr_diff] (0.10): Class structure preserved
python3 << 'PYEOF'
import ast, sys

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        methods = {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
        required = {"__init__", "forward", "terminate"}
        if required.issubset(methods):
            print(f"PASS: HFRunner has required methods")
            sys.exit(0)
        else:
            missing = required - methods
            print(f"FAIL: HFRunner missing methods: {missing}")
            sys.exit(1)

print("FAIL: HFRunner class not found")
sys.exit(1)
PYEOF
T4=$?

# ── TEST 5 (0.05): ANTI-STUB — file is substantial ───────────────────────────────────
# [agent_config] (0.05): "Protect against file gutting stubs"
python3 << 'PYEOF'
import ast, sys

TARGET = "python/sglang/test/runners.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

line_count = len(source.splitlines())
class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
func_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))

if line_count < 50:
    print(f"FAIL: file only has {line_count} lines")
    sys.exit(1)

if class_count < 1 or func_count < 3:
    print(f"FAIL: file gutted ({class_count} classes, {func_count} functions)")
    sys.exit(1)

print(f"PASS: file substantial ({line_count} lines, {class_count} classes, {func_count} funcs)")
sys.exit(0)
PYEOF
T5=$?

# ── TEST 6 (0.10): CONFIG-DERIVED — new test files have main guard ───────────────────
# Source: .claude/skills/*/SKILL.md guidelines for sglang test patterns
python3 << 'PYEOF'
import subprocess, sys, os, re

os.chdir("/workspace/sglang")

# Get new test files added by agent
try:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD"],
        capture_output=True, text=True, timeout=10
    )
    new_files = result.stdout.strip().split("\\n") if result.stdout.strip() else []
except Exception as e:
    print(f"T6 PASS (git diff failed: {e})")
    sys.exit(0)

test_files = [f for f in new_files if f.endswith(".py") and ("/test" in f or f.startswith("test/"))]

if not test_files:
    print("T6 PASS (no new test files)")
    sys.exit(0)

all_ok = True
for tf in test_files:
    if not os.path.exists(tf):
        continue
    with open(tf) as f:
        content = f.read()
    # Check for main guard pattern
    if re.search(r'if\\s+__name__\\s*==\\s*["\']__main__["\']', content):
        continue
    print(f"T6 FAIL: {tf} missing main guard")
    all_ok = False

if all_ok:
    print("T6 PASS: all new test files have main guard")
    sys.exit(0)
else:
    sys.exit(1)
PYEOF
T6=$?

# ── Compute weighted reward ───────────────────────────────────────────
# Weights:
# T1: behavioral hang+error test    0.35
# T2: behavioral pass-to-pass       0.25
# T3: structural polling pattern    0.15
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
if $T6 == 0: w += 0.10
print(f'{w:.2f}')
")

echo "Score: $REWARD (T1=$T1 T2=$T2 T3=$T3 T4=$T4 T5=$T5 T6=$T6)"
echo "$REWARD" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
