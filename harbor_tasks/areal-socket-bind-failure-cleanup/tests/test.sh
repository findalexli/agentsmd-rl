#!/usr/bin/env bash
# Verifier for areal-socket-bind-failure-cleanup
# Task: close sockets on bind failure, fix __exit__ traceback in trainers
# Files: network.py, rl_trainer.py, sft_trainer.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

echo "=== areal socket bind failure cleanup verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
GATE_PASS=true
for f in areal/utils/network.py areal/trainer/rl_trainer.py areal/trainer/sft_trainer.py; do
    python3 -c "
import ast, sys
try:
    with open('/workspace/AReaL/$f') as fh:
        ast.parse(fh.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'  FAIL: $f SyntaxError: {e}')
    sys.exit(1)
"
    if [ $? -ne 0 ]; then
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "GATE FAIL: syntax error -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAVIORAL_SOCKET_LEAK=0.25
W_BEHAVIORAL_EXIT_TRACEBACK=0.25
W_BEHAVIORAL_SFT_EXIT=0.10
W_STRUCTURAL_FINALLY=0.15
W_ANTISTUB=0.15
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): behavioral -- socket is closed even on bind failure --
echo ""
echo "TEST 1: behavioral -- socket closed on bind failure (weight=$W_BEHAVIORAL_SOCKET_LEAK)"
T1=$(python3 << 'PYEOF'
import ast, sys, textwrap, socket, types, unittest.mock

with open("/workspace/AReaL/areal/utils/network.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find is_port_free function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "is_port_free":
        func_node = node
        break

if func_node is None:
    print("FAIL: is_port_free not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

# Track socket close calls using mock
close_calls = []
original_socket = socket.socket

class TrackingSocket:
    def __init__(self, *args, **kwargs):
        self._real = original_socket(*args, **kwargs)
        self._closed = False
    def bind(self, addr):
        return self._real.bind(addr)
    def close(self):
        self._closed = True
        close_calls.append(True)
        return self._real.close()
    def __getattr__(self, name):
        return getattr(self._real, name)

# Execute the function with a port that will fail TCP bind
exec_ns = {
    "__builtins__": __builtins__,
    "socket": types.SimpleNamespace(
        socket=TrackingSocket,
        AF_INET=socket.AF_INET,
        SOCK_STREAM=socket.SOCK_STREAM,
        SOCK_DGRAM=socket.SOCK_DGRAM,
    ),
}

exec(func_src, exec_ns)

# Use port 1 which should fail (requires root)
close_calls.clear()
result = exec_ns["is_port_free"](1)

if len(close_calls) >= 1:
    print(f"PASS: socket.close() called {len(close_calls)} time(s) even on bind failure")
    sys.exit(0)
else:
    print("FAIL: socket.close() was NOT called on bind failure")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_SOCKET_LEAK)")
fi

# -- TEST 2 (PRIMARY): behavioral -- rl_trainer __exit__ preserves traceback --
echo ""
echo "TEST 2: behavioral -- rl_trainer __exit__ does not use 'raise exc_value' (weight=$W_BEHAVIORAL_EXIT_TRACEBACK)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/trainer/rl_trainer.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find __exit__ method in a class
exit_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__exit__":
                exit_func = item
                break

if exit_func is None:
    print("FAIL: __exit__ method not found in rl_trainer.py")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[exit_func.lineno - 1:exit_func.end_lineno])

# Check it does NOT have 'raise exc_value'
if "raise exc_value" in func_src:
    print("FAIL: __exit__ still uses 'raise exc_value' (destroys traceback)")
    sys.exit(1)

# It should return False or not have a raise at all
if "return False" in func_src:
    print("PASS: __exit__ returns False (preserves traceback)")
    sys.exit(0)
elif "raise" not in func_src:
    print("PASS: __exit__ does not re-raise (preserves traceback)")
    sys.exit(0)
else:
    print("PASS: __exit__ does not use 'raise exc_value'")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_EXIT_TRACEBACK)")
fi

# -- TEST 3 (PRIMARY): behavioral -- sft_trainer __exit__ preserves traceback --
echo ""
echo "TEST 3: behavioral -- sft_trainer __exit__ does not use 'raise exc_value' (weight=$W_BEHAVIORAL_SFT_EXIT)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/trainer/sft_trainer.py") as f:
    source = f.read()

tree = ast.parse(source)

exit_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__exit__":
                exit_func = item
                break

if exit_func is None:
    print("FAIL: __exit__ method not found in sft_trainer.py")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[exit_func.lineno - 1:exit_func.end_lineno])

if "raise exc_value" in func_src:
    print("FAIL: __exit__ still uses 'raise exc_value' (destroys traceback)")
    sys.exit(1)

if "return False" in func_src:
    print("PASS: __exit__ returns False (preserves traceback)")
    sys.exit(0)
elif "raise" not in func_src:
    print("PASS: __exit__ does not re-raise (preserves traceback)")
    sys.exit(0)
else:
    print("PASS: __exit__ does not use 'raise exc_value'")
    sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_SFT_EXIT)")
fi

# -- TEST 4 (SUPPLEMENTARY): structural -- is_port_free uses finally blocks --
echo ""
echo "TEST 4: structural -- is_port_free uses finally for socket cleanup (weight=$W_STRUCTURAL_FINALLY)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/utils/network.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "is_port_free":
        func_node = node
        break

if func_node is None:
    print("FAIL: is_port_free not found")
    sys.exit(1)

# Count try statements with finalbody
finally_count = 0
for stmt in ast.walk(func_node):
    if isinstance(stmt, ast.Try) and stmt.finalbody:
        finally_count += 1

if finally_count >= 2:
    print(f"PASS: is_port_free has {finally_count} try/finally blocks (TCP + UDP)")
    sys.exit(0)
elif finally_count == 1:
    # Could be using context manager or a single combined finally
    print("PASS: is_port_free has at least 1 try/finally block")
    sys.exit(0)
else:
    # Check for 'with' statement (context manager) as alternative
    lines = source.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])
    if "finally:" in func_src or "with " in func_src:
        print("PASS: cleanup mechanism found in is_port_free")
        sys.exit(0)
    print("FAIL: no finally blocks or context managers in is_port_free")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_FINALLY)")
fi

# -- TEST 5: anti-stub check --
echo ""
echo "TEST 5: anti-stub -- files retain original logic (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import sys

files = {
    "/workspace/AReaL/areal/utils/network.py": ["is_port_free", "socket", "AF_INET", "SOCK_STREAM", "SOCK_DGRAM", "bind"],
    "/workspace/AReaL/areal/trainer/rl_trainer.py": ["__exit__", "__enter__", "close", "logger"],
    "/workspace/AReaL/areal/trainer/sft_trainer.py": ["__exit__", "__enter__", "close", "logger"],
}

for path, required in files.items():
    with open(path) as f:
        source = f.read()
    missing = [r for r in required if r not in source]
    if missing:
        print(f"FAIL: {path} is missing: {missing}")
        sys.exit(1)
    if len(source.splitlines()) < 50:
        print(f"FAIL: {path} too short -- likely stubbed")
        sys.exit(1)

print("PASS: all files retain original logic")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: AGENTS.md line 13 @ commit 7cad4dac2d1f230891f201dbbfa91403e621cec1
echo ""
echo "TEST 6: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" /workspace/AReaL/areal/utils/network.py /workspace/AReaL/areal/trainer/rl_trainer.py /workspace/AReaL/areal/trainer/sft_trainer.py 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: AGENTS.md line 80 @ commit 7cad4dac2d1f230891f201dbbfa91403e621cec1
echo ""
echo "TEST 7: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" /workspace/AReaL/areal/utils/network.py /workspace/AReaL/areal/trainer/rl_trainer.py /workspace/AReaL/areal/trainer/sft_trainer.py 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_BARE_PRINT)")
    echo "PASS"
else
    echo "FAIL: bare print() found"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
