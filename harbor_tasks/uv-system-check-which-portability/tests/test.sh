#!/usr/bin/env bash
set +e

SCORE=0
TARGET="/repos/uv/scripts/check_system_python.py"

pass_check() { SCORE=$(python3 -c "print(round($SCORE + $1, 2))"); echo "PASS ($1): $2"; }
fail_check() { echo "FAIL ($1): $2"; }

mkdir -p /results

# ── GATE: Syntax check ─────────────────────────────────────────────────
# [pr_diff] (0.00): Script must be valid Python
python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: Syntax error in $TARGET"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: Syntax valid"

# ── F2P Behavioral 1 (0.35): Path check runs when os.name == "nt" ─────
# [pr_diff] (0.35): PATH verification must not be skipped on Windows
# The buggy code wraps the check in `if os.name != "nt":`, skipping it.
# Any correct fix should run the path check on ALL platforms.
# We load the module, mock all side-effects, set os.name="nt",
# call install_package, and verify the path-checking code executed.
python3 << 'PYEOF'
import sys, os, importlib.util, unittest.mock as mock, logging

TARGET = "/repos/uv/scripts/check_system_python.py"

# Load module without running __main__
spec = importlib.util.spec_from_file_location('check_system_python', TARGET)
mod = importlib.util.module_from_spec(spec)
mod.__name__ = 'check_system_python'
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(f"Module load failed: {e}")
    sys.exit(2)

if not hasattr(mod, 'install_package'):
    print("install_package function not found")
    sys.exit(1)

# --- Instrumentation ---
path_check_ran = False

class FakeResult:
    returncode = 0
    stdout = b''
    stderr = b''

def mock_run(cmd, **kwargs):
    global path_check_ran
    if isinstance(cmd, list) and len(cmd) >= 2:
        if cmd[0] in ('which', 'where') and 'pylint' in cmd:
            path_check_ran = True
    return FakeResult()

def mock_which(name):
    global path_check_ran
    if name == 'pylint':
        path_check_ran = True
    return f'/usr/bin/{name}'

# Capture log messages as secondary signal
log_msgs = []
class LogCapture(logging.Handler):
    def emit(self, record):
        log_msgs.append(record.getMessage())

capture = LogCapture()
logging.getLogger().addHandler(capture)
logging.getLogger().setLevel(logging.DEBUG)

# Mock tempfile.TemporaryDirectory context manager
mock_td_inst = mock.MagicMock()
mock_td_inst.__enter__ = mock.Mock(return_value='/tmp/fakedir')
mock_td_inst.__exit__ = mock.Mock(return_value=False)
mock_td_cls = mock.Mock(return_value=mock_td_inst)

with mock.patch.object(mod.subprocess, 'run', mock_run), \
     mock.patch.object(mod.shutil, 'which', mock_which), \
     mock.patch('os.name', 'nt'), \
     mock.patch.object(mod.tempfile, 'TemporaryDirectory', mock_td_cls):
    try:
        mod.install_package(uv='/usr/bin/uv', package='pylint')
    except Exception:
        pass  # May fail for unrelated reasons — we only care about instrumentation

logging.getLogger().removeHandler(capture)

# Check: did the path check actually run?
path_logged = any('path' in m.lower() for m in log_msgs if 'pylint' in m.lower())

if path_check_ran or path_logged:
    print("OK: Path check executed with os.name='nt'")
    sys.exit(0)
else:
    print("FAIL: Path check was skipped when os.name='nt'")
    sys.exit(1)
PYEOF
rc=$?
if [ $rc -eq 0 ]; then
    pass_check 0.35 "Path check runs on Windows (os.name=nt)"
elif [ $rc -eq 2 ]; then
    echo "SKIP (0.35): Could not load module — falling back"
    fail_check 0.35 "Path check runs on Windows (module load failed)"
else
    fail_check 0.35 "Path check skipped on Windows"
fi

# ── F2P Behavioral 2 (0.25): Uses cross-platform path lookup ──────────
# [pr_diff] (0.25): Must not shell out to Unix `which` binary
# Buggy code calls subprocess.run(["which", "pylint"]).
# Fixed code should use shutil.which or another cross-platform mechanism.
# We mock both, run with os.name="posix" (so both buggy/fixed reach the code),
# and verify subprocess which is NOT called.
python3 << 'PYEOF'
import sys, os, importlib.util, unittest.mock as mock, logging

TARGET = "/repos/uv/scripts/check_system_python.py"

spec = importlib.util.spec_from_file_location('check_system_python2', TARGET)
mod = importlib.util.module_from_spec(spec)
mod.__name__ = 'check_system_python2'
try:
    spec.loader.exec_module(mod)
except Exception:
    sys.exit(2)

if not hasattr(mod, 'install_package'):
    sys.exit(1)

calls = {'shutil_which': False, 'subprocess_which': False}

class FakeResult:
    returncode = 0
    stdout = b''
    stderr = b''

def mock_run(cmd, **kwargs):
    if isinstance(cmd, list) and len(cmd) >= 2:
        if cmd[0] in ('which', 'where') and 'pylint' in cmd:
            calls['subprocess_which'] = True
    return FakeResult()

def mock_which(name):
    if name == 'pylint':
        calls['shutil_which'] = True
    return f'/usr/bin/{name}'

logging.disable(logging.CRITICAL)

mock_td_inst = mock.MagicMock()
mock_td_inst.__enter__ = mock.Mock(return_value='/tmp/fakedir')
mock_td_inst.__exit__ = mock.Mock(return_value=False)
mock_td_cls = mock.Mock(return_value=mock_td_inst)

# Use os.name="posix" so both buggy and fixed code reach the path check
with mock.patch.object(mod.subprocess, 'run', mock_run), \
     mock.patch.object(mod.shutil, 'which', mock_which), \
     mock.patch.object(mod.tempfile, 'TemporaryDirectory', mock_td_cls):
    try:
        mod.install_package(uv='/usr/bin/uv', package='pylint')
    except Exception:
        pass

logging.disable(logging.NOTSET)

if calls['subprocess_which']:
    print("FAIL: Still uses subprocess which (not cross-platform)")
    sys.exit(1)

if calls['shutil_which']:
    print("OK: Uses shutil.which (cross-platform)")
    sys.exit(0)

# Neither called — the path check didn't run at all (likely a stub or broken)
print("FAIL: No path check mechanism was invoked")
sys.exit(1)
PYEOF
rc=$?
if [ $rc -eq 0 ]; then
    pass_check 0.25 "Uses cross-platform path lookup (not subprocess which)"
elif [ $rc -eq 2 ]; then
    echo "SKIP (0.25): Could not load module"
    fail_check 0.25 "Cross-platform path lookup (module load failed)"
else
    fail_check 0.25 "Still uses Unix-only which command"
fi

# ── P2P: Module loads and function is callable (0.15) ──────────────────
# [pr_diff] (0.15): Script must remain a valid, loadable module with key APIs
python3 << 'PYEOF'
import sys, importlib.util

TARGET = "/repos/uv/scripts/check_system_python.py"
spec = importlib.util.spec_from_file_location('check_system_python3', TARGET)
mod = importlib.util.module_from_spec(spec)
mod.__name__ = 'check_system_python3'
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(f"Module failed to load: {e}")
    sys.exit(1)

# install_package must exist and be callable
if not hasattr(mod, 'install_package') or not callable(mod.install_package):
    print("install_package not found or not callable")
    sys.exit(1)

# Key modules must be imported
for name in ['subprocess', 'shutil', 'os', 'tempfile', 'logging', 'argparse']:
    if not hasattr(mod, name):
        print(f"Module {name} not imported")
        sys.exit(1)

# CLI args must be defined in source
source = open(TARGET).read()
for arg in ['--uv', '--externally-managed']:
    if arg not in source:
        print(f"CLI arg {arg} missing")
        sys.exit(1)

print("OK: Module loads, install_package callable, CLI args present")
PYEOF
if [ $? -eq 0 ]; then pass_check 0.15 "Module loads and function callable"; else fail_check 0.15 "Module broken"; fi

# ── Anti-stub: install_package body depth (0.10) ──────────────────────
# [pr_diff] (0.10): install_package must have real implementation, not a stub
python3 << 'PYEOF'
import ast, sys

TARGET = "/repos/uv/scripts/check_system_python.py"
source = open(TARGET).read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'install_package':
        # Count meaningful statements (exclude docstrings, pass, bare constants)
        meaningful = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.If, ast.With,
                                  ast.For, ast.While, ast.Try, ast.Raise, ast.Return)):
                meaningful += 1
            elif isinstance(child, ast.Expr):
                if not isinstance(child.value, (ast.Constant, ast.Str)):
                    meaningful += 1
        if meaningful < 10:
            print(f"install_package has only {meaningful} statements — likely a stub")
            sys.exit(1)
        print(f"OK: install_package has {meaningful} meaningful statements")
        sys.exit(0)

print("install_package function not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then pass_check 0.10 "install_package not a stub"; else fail_check 0.10 "install_package appears stubbed"; fi

# ── Config: Top-level shutil import (0.05) ─────────────────────────────
# [agent_config] (0.05): "PREFER top-level imports" — CLAUDE.md:14 @ cedae1aa
python3 << 'PYEOF'
import ast, sys

TARGET = "/repos/uv/scripts/check_system_python.py"
source = open(TARGET).read()
tree = ast.parse(source)

for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == 'shutil':
                print("OK: shutil imported at top level")
                sys.exit(0)
    if isinstance(node, ast.ImportFrom) and node.module and 'shutil' in node.module:
        print("OK: shutil imported at top level (from import)")
        sys.exit(0)

print("shutil not imported at top level")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then pass_check 0.05 "Top-level shutil import (CLAUDE.md)"; else fail_check 0.05 "shutil not at top level"; fi

# ── Config: No abbreviated variable names (0.05) ──────────────────────
# [agent_config] (0.05): "AVOID shortening variable names" — CLAUDE.md:15 @ cedae1aa
python3 << 'PYEOF'
import ast, sys

TARGET = "/repos/uv/scripts/check_system_python.py"
source = open(TARGET).read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'install_package':
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and len(target.id) == 1 and target.id != '_':
                        # Check if this assignment involves the which/path-check area
                        if isinstance(child.value, ast.Call):
                            func = child.value.func
                            func_str = ast.dump(func)
                            if 'which' in func_str.lower() or 'shutil' in func_str.lower():
                                print(f"Single-letter var '{target.id}' in path-check code")
                                sys.exit(1)
        break

print("OK: No abbreviated variable names in fix area")
PYEOF
if [ $? -eq 0 ]; then pass_check 0.05 "No abbreviated vars (CLAUDE.md)"; else fail_check 0.05 "Abbreviated variable names found"; fi

# ── Final score ─────────────────────────────────────────────────────────
echo ""
echo "Score: $SCORE / 1.0"
echo "$SCORE" > /logs/verifier/reward.txt
echo "{\"reward\": $SCORE}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
