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

# Weights: 80% behavioral, 20% structural
W_BEHAVIORAL_SOCKET_TCP=0.25    # [pr_diff] (0.25): TCP socket closed on bind failure
W_BEHAVIORAL_SOCKET_UDP=0.20    # [pr_diff] (0.20): UDP socket closed on bind failure
W_BEHAVIORAL_TRACEBACK_RL=0.20  # [pr_diff] (0.20): RL __exit__ preserves traceback
W_BEHAVIORAL_TRACEBACK_SFT=0.15 # [pr_diff] (0.15): SFT __exit__ preserves traceback
W_ANTISTUB=0.10                 # [static] (0.10): Anti-stub depth check
W_CONFIG_NO_WILDCARD=0.05       # [agent_config] (0.05): No wildcard imports
W_CONFIG_NO_BARE_PRINT=0.05     # [agent_config] (0.05): No bare print() in production code

SCORE="0.0"
BEHAVIORAL_PASS=false

# -- TEST 1 (F2P): behavioral -- TCP socket closed on bind failure --
echo ""
echo "TEST 1: behavioral -- TCP socket closed on bind failure (weight=$W_BEHAVIORAL_SOCKET_TCP)"
T1=$(python3 << 'PYEOF'
import ast, sys, textwrap, socket, types

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

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

tcp_close_called = False
udp_close_called = False
original_socket = socket.socket

class TrackingSocket:
    def __init__(self, *args, **kwargs):
        self._family = args[0] if args else kwargs.get('family', socket.AF_INET)
        self._type = args[1] if len(args) > 1 else kwargs.get('type', socket.SOCK_STREAM)
        self._real = original_socket(*args, **kwargs)
        self._closed = False
    def bind(self, addr):
        return self._real.bind(addr)
    def close(self):
        self._closed = True
        nonlocal tcp_close_called, udp_close_called
        if self._type == socket.SOCK_STREAM:
            tcp_close_called = True
        elif self._type == socket.SOCK_DGRAM:
            udp_close_called = True
        return self._real.close()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    def __getattr__(self, name):
        return getattr(self._real, name)

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

tcp_close_called = False
udp_close_called = False
result = exec_ns["is_port_free"](1)  # Port 1 requires root, bind will fail

if tcp_close_called:
    print("PASS: TCP socket.close() called on bind failure")
    sys.exit(0)
else:
    print("FAIL: TCP socket.close() was NOT called on bind failure")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_SOCKET_TCP)")
    BEHAVIORAL_PASS=true
fi

# -- TEST 2 (F2P): behavioral -- UDP socket closed on bind failure --
echo ""
echo "TEST 2: behavioral -- UDP socket closed on bind failure (weight=$W_BEHAVIORAL_SOCKET_UDP)"
T2=$(python3 << 'PYEOF'
import ast, sys, textwrap, socket, types

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

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1:func_node.end_lineno]))

tcp_close_called = False
udp_close_called = False
original_socket = socket.socket

class TrackingSocket:
    def __init__(self, *args, **kwargs):
        self._family = args[0] if args else kwargs.get('family', socket.AF_INET)
        self._type = args[1] if len(args) > 1 else kwargs.get('type', socket.SOCK_STREAM)
        self._real = original_socket(*args, **kwargs)
        self._closed = False
    def bind(self, addr):
        return self._real.bind(addr)
    def close(self):
        self._closed = True
        nonlocal tcp_close_called, udp_close_called
        if self._type == socket.SOCK_STREAM:
            tcp_close_called = True
        elif self._type == socket.SOCK_DGRAM:
            udp_close_called = True
        return self._real.close()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    def __getattr__(self, name):
        return getattr(self._real, name)

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

tcp_close_called = False
udp_close_called = False
result = exec_ns["is_port_free"](1)

if udp_close_called:
    print("PASS: UDP socket.close() called on bind failure")
    sys.exit(0)
else:
    print("FAIL: UDP socket.close() was NOT called on bind failure")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_SOCKET_UDP)")
    BEHAVIORAL_PASS=true
fi

# -- TEST 3 (F2P): behavioral -- RL __exit__ preserves exception traceback --
# Tests BEHAVIOR: calls __exit__ with real exception info and verifies traceback is preserved.
# Accepts: return False/None, raise with .with_traceback(tb), bare raise in except, etc.
echo ""
echo "TEST 3: behavioral -- RL __exit__ preserves exception traceback (weight=$W_BEHAVIORAL_TRACEBACK_RL)"
T3=$(python3 << 'PYEOF'
import ast, sys, textwrap, traceback as tb_module

with open("/workspace/AReaL/areal/trainer/rl_trainer.py") as f:
    source = f.read()

tree = ast.parse(source)

exit_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__exit__":
                exit_func = item
                break
        if exit_func:
            break

if exit_func is None:
    print("FAIL: __exit__ method not found in rl_trainer.py")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[exit_func.lineno - 1:exit_func.end_lineno]))

# Build a minimal test class with the extracted __exit__
test_class_src = '''
class TestTrainer:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True
    def __enter__(self):
        return self
''' + textwrap.indent(func_src, '')

class MockLogger:
    def error(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass

exec_ns = {"__builtins__": __builtins__, "logger": MockLogger()}
try:
    exec(test_class_src, exec_ns)
except Exception as e:
    print(f"FAIL: Could not exec __exit__: {e}")
    sys.exit(1)

TestTrainer = exec_ns["TestTrainer"]

# Create an exception with a KNOWN traceback origin
def trigger_original_error():
    raise ValueError("original error from trigger_original_error")

try:
    trigger_original_error()
except ValueError:
    exc_type, exc_value, exc_tb = sys.exc_info()
    # Verify our traceback has the expected origin
    original_frames = tb_module.extract_tb(exc_tb)
    assert any(f.name == "trigger_original_error" for f in original_frames)

    trainer = TestTrainer()
    try:
        result = trainer.__exit__(exc_type, exc_value, exc_tb)
        # __exit__ returned normally — correct if result is falsy
        if result:
            print("FAIL: __exit__ suppresses exception (returns truthy)")
            sys.exit(1)
        else:
            print("PASS: __exit__ returns falsy, exception propagates with original traceback")
            sys.exit(0)
    except BaseException as reraise_exc:
        # __exit__ re-raised the exception. Check if traceback is preserved.
        new_tb = sys.exc_info()[2]
        new_frames = tb_module.extract_tb(new_tb)
        # If traceback is preserved, "trigger_original_error" should appear in frames
        has_original_frame = any(f.name == "trigger_original_error" for f in new_frames)
        if has_original_frame:
            print("PASS: __exit__ re-raises with preserved traceback")
            sys.exit(0)
        else:
            print("FAIL: __exit__ re-raises but destroys original traceback (likely 'raise exc_value')")
            sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_TRACEBACK_RL)")
    BEHAVIORAL_PASS=true
fi

# -- TEST 4 (F2P): behavioral -- SFT __exit__ preserves exception traceback --
echo ""
echo "TEST 4: behavioral -- SFT __exit__ preserves exception traceback (weight=$W_BEHAVIORAL_TRACEBACK_SFT)"
T4=$(python3 << 'PYEOF'
import ast, sys, textwrap, traceback as tb_module

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
        if exit_func:
            break

if exit_func is None:
    print("FAIL: __exit__ method not found in sft_trainer.py")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[exit_func.lineno - 1:exit_func.end_lineno]))

test_class_src = '''
class TestTrainer:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True
    def __enter__(self):
        return self
''' + textwrap.indent(func_src, '')

class MockLogger:
    def error(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass

exec_ns = {"__builtins__": __builtins__, "logger": MockLogger()}
try:
    exec(test_class_src, exec_ns)
except Exception as e:
    print(f"FAIL: Could not exec __exit__: {e}")
    sys.exit(1)

TestTrainer = exec_ns["TestTrainer"]

def trigger_original_error():
    raise ValueError("original error from trigger_original_error")

try:
    trigger_original_error()
except ValueError:
    exc_type, exc_value, exc_tb = sys.exc_info()
    original_frames = tb_module.extract_tb(exc_tb)
    assert any(f.name == "trigger_original_error" for f in original_frames)

    trainer = TestTrainer()
    try:
        result = trainer.__exit__(exc_type, exc_value, exc_tb)
        if result:
            print("FAIL: __exit__ suppresses exception (returns truthy)")
            sys.exit(1)
        else:
            print("PASS: __exit__ returns falsy, exception propagates with original traceback")
            sys.exit(0)
    except BaseException as reraise_exc:
        new_tb = sys.exc_info()[2]
        new_frames = tb_module.extract_tb(new_tb)
        has_original_frame = any(f.name == "trigger_original_error" for f in new_frames)
        if has_original_frame:
            print("PASS: __exit__ re-raises with preserved traceback")
            sys.exit(0)
        else:
            print("FAIL: __exit__ re-raises but destroys original traceback (likely 'raise exc_value')")
            sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_TRACEBACK_SFT)")
    BEHAVIORAL_PASS=true
fi

# -- TEST 5: anti-stub check (GATED on behavioral) --
echo ""
echo "TEST 5: anti-stub -- files have implementation depth (weight=$W_ANTISTUB)"
if [ "$BEHAVIORAL_PASS" = false ]; then
    echo "SKIP: gated behind behavioral pass"
    T5="SKIP"
else
    T5=$(python3 << 'PYEOF'
import ast, sys

files_to_check = [
    ("/workspace/AReaL/areal/utils/network.py", "is_port_free"),
    ("/workspace/AReaL/areal/trainer/rl_trainer.py", "__exit__"),
    ("/workspace/AReaL/areal/trainer/sft_trainer.py", "__exit__"),
]

for path, func_name in files_to_check:
    try:
        with open(path) as f:
            source = f.read()
    except FileNotFoundError:
        print(f"FAIL: {path} not found")
        sys.exit(1)

    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"FAIL: {path} has syntax errors")
        sys.exit(1)

    found = False
    for node in ast.walk(tree):
        target = None
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            target = node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == func_name:
                    target = item
                    break

        if target:
            found = True
            # Count non-docstring statements
            stmt_count = 0
            for stmt in target.body:
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                    continue
                stmt_count += 1
            if stmt_count < 3:
                print(f"FAIL: {path}:{func_name} has only {stmt_count} statements (likely stub)")
                sys.exit(1)
            break

    if not found:
        print(f"FAIL: {func_name} not found in {path}")
        sys.exit(1)

print("PASS: all target functions have sufficient implementation depth")
sys.exit(0)
PYEOF
    )
    echo "$T5"
    if echo "$T5" | grep -q "^PASS"; then
        SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
    fi
fi

# -- TEST 6: Config-derived -- no wildcard imports (GATED on behavioral) --
echo ""
echo "TEST 6: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
if [ "$BEHAVIORAL_PASS" = false ]; then
    echo "SKIP: gated behind behavioral pass"
else
    # [agent_config] (0.05): No wildcard imports
    grep -rn "from .* import \*" /workspace/AReaL/areal/utils/network.py /workspace/AReaL/areal/trainer/rl_trainer.py /workspace/AReaL/areal/trainer/sft_trainer.py 2>/dev/null
    if [ $? -ne 0 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
        echo "PASS"
    else
        echo "FAIL: wildcard import found"
    fi
fi

# -- TEST 7: Config-derived -- no bare print() (GATED on behavioral) --
echo ""
echo "TEST 7: config-derived -- no bare print() in production code (weight=$W_CONFIG_NO_BARE_PRINT)"
if [ "$BEHAVIORAL_PASS" = false ]; then
    echo "SKIP: gated behind behavioral pass"
else
    # [agent_config] (0.05): No bare print() — check via AST to avoid matching comments/strings
    python3 << 'PYEOF'
import ast, sys

files = [
    "/workspace/AReaL/areal/utils/network.py",
    "/workspace/AReaL/areal/trainer/rl_trainer.py",
    "/workspace/AReaL/areal/trainer/sft_trainer.py",
]

for path in files:
    with open(path) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "print":
                print(f"FAIL: bare print() call at {path}:{node.lineno}")
                sys.exit(1)

print("PASS: no bare print() calls")
sys.exit(0)
PYEOF
    if [ $? -eq 0 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_BARE_PRINT)")
    fi
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# Write detailed breakdown
cat > /logs/verifier/reward.json << EOJSON
{
  "reward": $REWARD,
  "behavioral_socket_tcp": $(python3 -c "s=$SCORE; w=$W_BEHAVIORAL_SOCKET_TCP; print(w if s >= w else 0)"),
  "behavioral_socket_udp": $(python3 -c "s=$SCORE; w=$W_BEHAVIORAL_SOCKET_UDP; print(w if s >= w else 0)"),
  "behavioral_traceback_rl": $(python3 -c "s=$SCORE; w=$W_BEHAVIORAL_TRACEBACK_RL; print(w if s >= w else 0)"),
  "behavioral_traceback_sft": $(python3 -c "s=$SCORE; w=$W_BEHAVIORAL_TRACEBACK_SFT; print(w if s >= w else 0)"),
  "antistub": $(python3 -c "s=$SCORE; w=$W_ANTISTUB; print(w if s >= w else 0)"),
  "config": $(python3 -c "s=$SCORE; w=$W_CONFIG_NO_WILDCARD+$W_CONFIG_NO_BARE_PRINT; print(w if s >= w else 0)")
}
EOJSON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
