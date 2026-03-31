#!/usr/bin/env bash
set +e

REWARD=0
add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

mkdir -p /logs/verifier

# ============================================================
# GATE: Syntax check on all modified files
# ============================================================
echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): All modified files must be valid Python
GATE_PASS=true
for f in areal/infra/platforms/platform.py areal/infra/platforms/cuda.py \
         areal/engine/fsdp_engine.py areal/engine/megatron_engine.py \
         areal/experimental/engine/archon_engine.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())"; then
        echo "FAIL: syntax error in $f"
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: all files have valid syntax"

# ============================================================
# Stub heavy __init__.py files so we can import platform modules
# without pulling in flask, aiohttp, transformers, etc.
# ============================================================
for init_f in areal/__init__.py areal/infra/__init__.py areal/utils/__init__.py areal/infra/platforms/__init__.py; do
    if [ -f "$init_f" ]; then
        cp "$init_f" "${init_f}.testbak"
        echo "" > "$init_f"
    fi
done
# Ensure cleanup restores init files on exit
trap 'for init_f in areal/__init__.py areal/infra/__init__.py areal/utils/__init__.py areal/infra/platforms/__init__.py; do [ -f "${init_f}.testbak" ] && mv "${init_f}.testbak" "$init_f"; done' EXIT

# ============================================================
# F2P Behavioral: Platform.set_numa_affinity is a callable no-op (0.05)
# ============================================================
echo ""
echo "=== F2P: Platform.set_numa_affinity callable no-op ==="
# [pr_diff] (0.05): Platform base class must expose set_numa_affinity as a no-op
if python3 -c "
import sys; sys.path.insert(0, '.')
from areal.infra.platforms.platform import Platform
result = Platform.set_numa_affinity(0)
assert result is None, f'Expected None, got {result}'
# Also test with different ranks
Platform.set_numa_affinity(1)
Platform.set_numa_affinity(7)
print('OK')
"; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# F2P Behavioral: CudaPlatform.set_numa_affinity handles missing pynvml (0.05)
# ============================================================
echo ""
echo "=== F2P: CudaPlatform handles missing pynvml ==="
# [pr_diff] (0.05): Must not crash when pynvml is not installed
if python3 -c "
import sys
sys.path.insert(0, '.')
# Make absolutely sure pynvml is NOT available
for mod in list(sys.modules):
    if 'pynvml' in mod:
        del sys.modules[mod]
# Block any future import of pynvml
import importlib
orig_import = __builtins__.__import__
def blocking_import(name, *args, **kwargs):
    if name == 'pynvml':
        raise ImportError('pynvml not installed (test mock)')
    return orig_import(name, *args, **kwargs)
__builtins__.__import__ = blocking_import

from areal.infra.platforms.cuda import CudaPlatform
try:
    CudaPlatform.set_numa_affinity(0)
    print('OK: no crash')
except AttributeError:
    print('FAIL: method does not exist')
    sys.exit(1)
except ImportError:
    print('FAIL: ImportError leaked out')
    sys.exit(1)
except Exception as e:
    print(f'FAIL: unhandled exception: {e}')
    sys.exit(1)
finally:
    __builtins__.__import__ = orig_import
"; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# F2P Behavioral: CudaPlatform uses NVML via pynvml (0.40)
# ============================================================
echo ""
echo "=== F2P: CudaPlatform uses NVML with mock pynvml ==="
# [pr_diff] (0.40): Must actually call pynvml NVML functions to set affinity
if python3 -c "
import sys, types
sys.path.insert(0, '.')

# Create a mock pynvml module that tracks calls
mock = types.ModuleType('pynvml')
calls = []

mock.nvmlInit = lambda: calls.append('nvmlInit')

def mock_getHandle(idx):
    calls.append(('getHandle', idx))
    return f'handle_{idx}'
mock.nvmlDeviceGetHandleByIndex = mock_getHandle

mock.nvmlDeviceSetCpuAffinity = lambda h: calls.append(('setCpuAffinity', h))

def mock_getCpuAffinity(h, n=1024, scope=0):
    calls.append(('getCpuAffinity', h))
    return [0xFFFF]
mock.nvmlDeviceGetCpuAffinityWithinScope = mock_getCpuAffinity

mock.nvmlShutdown = lambda: calls.append('nvmlShutdown')
mock.NVML_AFFINITY_SCOPE_NODE = 0
mock.NVML_AFFINITY_SCOPE_SOCKET = 1

class MockNVMLError(Exception): pass
mock.NVMLError = MockNVMLError

sys.modules['pynvml'] = mock

from areal.infra.platforms.cuda import CudaPlatform
CudaPlatform.set_numa_affinity(0)

# Verify NVML was initialized
assert 'nvmlInit' in calls, f'nvmlInit not called. Calls: {calls}'

# Verify device handle was obtained
handle_calls = [c for c in calls if isinstance(c, tuple) and c[0] == 'getHandle']
assert len(handle_calls) > 0, f'nvmlDeviceGetHandleByIndex not called. Calls: {calls}'

# Verify CPU affinity was set (accept either nvmlDeviceSetCpuAffinity or
# nvmlDeviceGetCpuAffinityWithinScope — both are valid NVML approaches)
affinity_calls = [c for c in calls if isinstance(c, tuple) and c[0] in ('setCpuAffinity', 'getCpuAffinity')]
assert len(affinity_calls) > 0, f'No NVML affinity call made. Calls: {calls}'

print(f'OK: NVML calls verified: {[c[0] if isinstance(c, tuple) else c for c in calls]}')
"; then
    echo "PASS"
    add 0.40
else
    echo "FAIL"
fi

# ============================================================
# F2P Behavioral: CudaPlatform calls nvmlShutdown for cleanup (0.10)
# ============================================================
echo ""
echo "=== F2P: CudaPlatform cleans up NVML (nvmlShutdown) ==="
# [pr_diff] (0.10): Must call nvmlShutdown after NVML operations (finally block)
if python3 -c "
import sys, types
sys.path.insert(0, '.')

mock = types.ModuleType('pynvml')
calls = []

mock.nvmlInit = lambda: calls.append('nvmlInit')
mock.nvmlDeviceGetHandleByIndex = lambda idx: (calls.append('getHandle'), f'h{idx}')[1]
mock.nvmlDeviceSetCpuAffinity = lambda h: calls.append('setCpuAffinity')
mock.nvmlDeviceGetCpuAffinityWithinScope = lambda h, n=1024, s=0: (calls.append('getCpuAffinity'), [0xFFFF])[1]
mock.nvmlShutdown = lambda: calls.append('nvmlShutdown')
mock.NVML_AFFINITY_SCOPE_NODE = 0
mock.NVML_AFFINITY_SCOPE_SOCKET = 1
class MockNVMLError(Exception): pass
mock.NVMLError = MockNVMLError
sys.modules['pynvml'] = mock

from areal.infra.platforms.cuda import CudaPlatform
CudaPlatform.set_numa_affinity(0)

assert 'nvmlShutdown' in calls, f'nvmlShutdown not called — NVML not cleaned up. Calls: {calls}'

# Also verify shutdown happens AFTER init (ordering)
init_idx = calls.index('nvmlInit')
shutdown_idx = calls.index('nvmlShutdown')
assert shutdown_idx > init_idx, 'nvmlShutdown called before nvmlInit'
print('OK: nvmlShutdown called after nvmlInit')
"; then
    echo "PASS"
    add 0.10
else
    echo "FAIL"
fi

# ============================================================
# F2P Behavioral: CudaPlatform handles NVML runtime error (0.05)
# ============================================================
echo ""
echo "=== F2P: CudaPlatform handles NVML runtime error ==="
# [pr_diff] (0.05): Must catch NVML runtime errors without crashing
if python3 -c "
import sys, types
sys.path.insert(0, '.')

mock = types.ModuleType('pynvml')

class MockNVMLError(Exception): pass
mock.NVMLError = MockNVMLError

def failing_init():
    raise MockNVMLError('NVML mock failure: driver not loaded')
mock.nvmlInit = failing_init
mock.nvmlShutdown = lambda: None
mock.nvmlDeviceGetHandleByIndex = lambda idx: None
mock.nvmlDeviceSetCpuAffinity = lambda h: None
mock.nvmlDeviceGetCpuAffinityWithinScope = lambda h, n=1024, s=0: [0xFFFF]
mock.NVML_AFFINITY_SCOPE_NODE = 0
mock.NVML_AFFINITY_SCOPE_SOCKET = 1
sys.modules['pynvml'] = mock

from areal.infra.platforms.cuda import CudaPlatform
try:
    CudaPlatform.set_numa_affinity(0)
    print('OK: NVML error handled gracefully')
except Exception as e:
    print(f'FAIL: unhandled exception: {type(e).__name__}: {e}')
    sys.exit(1)
"; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# F2P Structural: Engine files call set_numa_affinity (AST) (0.15)
# ============================================================
echo ""
echo "=== F2P: Engines call set_numa_affinity (AST check) ==="
# [pr_diff] (0.15): All three engines must have a call expression for set_numa_affinity
# Justification for AST: engines require distributed setup (torch.distributed,
# FSDP, Megatron) that cannot be initialized in CPU-only test environment
if python3 -c "
import ast, sys

engines = [
    'areal/engine/fsdp_engine.py',
    'areal/engine/megatron_engine.py',
    'areal/experimental/engine/archon_engine.py',
]
found = 0
for path in engines:
    source = open(path).read()
    tree = ast.parse(source)
    has_call = False
    for node in ast.walk(tree):
        # Look for actual Call nodes with .set_numa_affinity attribute
        # This rejects comments and string mentions — only real code passes
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == 'set_numa_affinity':
                has_call = True
                break
    if has_call:
        found += 1
        print(f'  OK: {path}')
    else:
        print(f'  MISSING: {path}')

if found == 3:
    sys.exit(0)
elif found >= 1:
    # Partial credit
    print(f'Found {found}/3 engines')
    sys.exit(0)
else:
    sys.exit(1)
"; then
    ENGINE_COUNT=$(python3 -c "
import ast
engines = [
    'areal/engine/fsdp_engine.py',
    'areal/engine/megatron_engine.py',
    'areal/experimental/engine/archon_engine.py',
]
c = 0
for p in engines:
    tree = ast.parse(open(p).read())
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'set_numa_affinity':
            c += 1; break
print(c)
")
    if [ "$ENGINE_COUNT" -eq 3 ]; then
        echo "PASS: all 3 engines"
        add 0.15
    else
        PARTIAL=$(python3 -c "print(round(0.15 * $ENGINE_COUNT / 3, 4))")
        echo "PARTIAL: $ENGINE_COUNT/3 engines"
        add "$PARTIAL"
    fi
else
    echo "FAIL: no engines call set_numa_affinity"
fi

# ============================================================
# P2P: Platform existing methods (0.05)
# ============================================================
echo ""
echo "=== P2P: Platform existing methods ==="
# [pr_diff] (0.05): Existing Platform methods must still be present
if python3 -c "
import sys; sys.path.insert(0, '.')
from areal.infra.platforms.platform import Platform
required = ['set_allocator_settings', 'get_custom_env_vars',
            'clear_cublas_workspaces', 'get_vllm_worker_class']
missing = [m for m in required if not hasattr(Platform, m)]
assert not missing, f'Missing: {missing}'
print('OK')
"; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# P2P: CudaPlatform existing methods (0.05)
# ============================================================
echo ""
echo "=== P2P: CudaPlatform existing methods ==="
# [pr_diff] (0.05): CudaPlatform existing methods must still work
if python3 -c "
import sys; sys.path.insert(0, '.')
from areal.infra.platforms.cuda import CudaPlatform
required = ['clear_memory', 'clear_cublas_workspaces', 'set_allocator_settings', 'get_custom_env_vars']
missing = [m for m in required if not hasattr(CudaPlatform, m)]
assert not missing, f'Missing: {missing}'
print('OK')
"; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# Config: No wildcard imports (0.05)
# ============================================================
echo ""
echo "=== Config: No wildcard imports ==="
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30 @ 682d564
WILDCARD_FOUND=false
for f in areal/infra/platforms/platform.py areal/infra/platforms/cuda.py; do
    if python3 -c "
import ast, sys
source = open('$f').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and any(a.name == '*' for a in node.names):
        sys.exit(1)
"; then
        :
    else
        echo "  FAIL: wildcard import in $f"
        WILDCARD_FOUND=true
    fi
done
if [ "$WILDCARD_FOUND" = false ]; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# Structural: Anti-stub — CudaPlatform.set_numa_affinity has real implementation (0.05)
# ============================================================
echo ""
echo "=== Structural: Anti-stub ==="
# [pr_diff] (0.05): CudaPlatform.set_numa_affinity must have substantial implementation
if python3 -c "
import ast, sys
source = open('areal/infra/platforms/cuda.py').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'CudaPlatform':
        for item in ast.walk(node):
            if isinstance(item, ast.FunctionDef) and item.name == 'set_numa_affinity':
                # Filter out docstrings and pass statements
                body = [s for s in item.body
                        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                        and not isinstance(s, ast.Pass)]
                if len(body) < 2:
                    print(f'FAIL: only {len(body)} meaningful statements (need >= 2)')
                    sys.exit(1)
                print(f'OK: {len(body)} meaningful statements')
                sys.exit(0)
        print('FAIL: set_numa_affinity not found in CudaPlatform')
        sys.exit(1)
print('FAIL: CudaPlatform not found')
sys.exit(1)
"; then
    echo "PASS"
    add 0.05
else
    echo "FAIL"
fi

# ============================================================
# Final score
# ============================================================
echo ""
echo "=== Total score: $REWARD ==="
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
reward = $REWARD
data = {
    'reward': reward,
    'behavioral': round(min(0.70, reward), 4),
    'regression': round(min(0.10, max(0, reward - 0.70)), 4),
    'config': round(min(0.05, max(0, reward - 0.80)), 4),
    'structural': round(min(0.05, max(0, reward - 0.85)), 4),
    'style_rubric': 0.0,
}
json.dump(data, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
