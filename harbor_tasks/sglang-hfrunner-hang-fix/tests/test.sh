#!/bin/bash
set +e

PASS=0
TOTAL=5
TARGET="python/sglang/test/runners.py"

mkdir -p /logs/verifier

# GATE: Python syntax validity
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

# TEST 1: No bare self.out_queue.get() without timeout in forward()
python3 << 'PYEOF'
import ast, sys

with open("python/sglang/test/runners.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the HFRunner class and its forward method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                # Look for bare .get() calls on out_queue with no timeout
                for call_node in ast.walk(item):
                    if isinstance(call_node, ast.Call):
                        func = call_node.func
                        if isinstance(func, ast.Attribute) and func.attr == "get":
                            if isinstance(func.value, ast.Attribute) and func.value.attr == "out_queue":
                                # Check if timeout keyword is present
                                has_timeout = any(kw.arg == "timeout" for kw in call_node.keywords)
                                has_positional_timeout = len(call_node.args) >= 2
                                if not has_timeout and not has_positional_timeout:
                                    print("FAIL: bare out_queue.get() without timeout found")
                                    sys.exit(1)
                print("PASS: no bare out_queue.get() without timeout")
                sys.exit(0)

print("FAIL: could not find HFRunner.forward method")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# TEST 2: Code checks model_proc.is_alive()
python3 << 'PYEOF'
import sys

with open("python/sglang/test/runners.py") as f:
    source = f.read()

# Find the forward method region and check for is_alive
in_forward = False
found = False
for line in source.splitlines():
    stripped = line.strip()
    if "def forward" in line:
        in_forward = True
    elif in_forward and (stripped.startswith("def ") or (stripped and not stripped.startswith("#") and not stripped.startswith("@") and line and not line[0].isspace() and stripped)):
        # Reached next top-level or class-level def
        if not line.startswith(" " * 4) and not line.startswith("\t"):
            break
    if in_forward and "is_alive" in line:
        found = True
        break

if found:
    print("PASS: is_alive check found in forward method context")
    sys.exit(0)
else:
    print("FAIL: no is_alive check found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# TEST 3: RuntimeError raised when subprocess dies
python3 << 'PYEOF'
import ast, sys

with open("python/sglang/test/runners.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                for child in ast.walk(item):
                    if isinstance(child, ast.Raise) and child.exc is not None:
                        # Check if it raises RuntimeError or any exception with a message
                        exc = child.exc
                        if isinstance(exc, ast.Call):
                            if isinstance(exc.func, ast.Name) and exc.func.id in ("RuntimeError", "ChildProcessError", "SubprocessError", "Exception", "OSError"):
                                print(f"PASS: raises {exc.func.id}")
                                sys.exit(0)
                        elif isinstance(exc, ast.Name):
                            print(f"PASS: raises {exc.id}")
                            sys.exit(0)
                print("FAIL: no RuntimeError or similar exception raised in forward()")
                sys.exit(1)

print("FAIL: could not find HFRunner.forward")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# TEST 4: queue.get uses timeout parameter
python3 << 'PYEOF'
import ast, sys

with open("python/sglang/test/runners.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                for call_node in ast.walk(item):
                    if isinstance(call_node, ast.Call):
                        func = call_node.func
                        if isinstance(func, ast.Attribute) and func.attr == "get":
                            has_timeout = any(kw.arg == "timeout" for kw in call_node.keywords)
                            has_positional_timeout = len(call_node.args) >= 2
                            if has_timeout or has_positional_timeout:
                                print("PASS: queue.get() uses timeout")
                                sys.exit(0)
                print("FAIL: no queue.get() with timeout found in forward()")
                sys.exit(1)

print("FAIL: could not find HFRunner.forward")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# TEST 5: Anti-stub - file still has full HFRunner class with __init__, forward, terminate
python3 << 'PYEOF'
import ast, sys

with open("python/sglang/test/runners.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HFRunner":
        methods = {item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
        required = {"__init__", "forward"}
        # terminate or __del__ or cleanup
        has_cleanup = bool(methods & {"terminate", "__del__", "cleanup", "__exit__"})
        has_required = required.issubset(methods)
        # Check file is substantial (not a stub)
        if has_required and len(source.splitlines()) > 100:
            print(f"PASS: HFRunner has methods {methods & (required | {'terminate','__del__','cleanup'})} and file has {len(source.splitlines())} lines")
            sys.exit(0)
        else:
            print(f"FAIL: missing methods or file too short. methods={methods}, lines={len(source.splitlines())}")
            sys.exit(1)

print("FAIL: HFRunner class not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
fi

# Compute reward
REWARD=$(python3 -c "print(min($PASS / $TOTAL, 1.0))")
echo "Score: $PASS / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt
