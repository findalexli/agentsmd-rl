#!/usr/bin/env bash
set +e

REPO="/workspace/prime-rl"
SCORE=0
LOGS="/logs/verifier"
mkdir -p "$LOGS"

echo "=== prime-rl: vLLM sampling args token IDs fix ==="

########################################
# GATE: Syntax check
########################################
echo ""
echo "--- GATE: Syntax check ---"
python3 -c "
import py_compile, sys
files = [
    '$REPO/src/prime_rl/orchestrator/utils.py',
    '$REPO/src/prime_rl/orchestrator/orchestrator.py',
    '$REPO/src/prime_rl/orchestrator/scheduler.py',
]
ok = True
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'FAIL: {e}', file=sys.stderr)
        ok = False
if not ok:
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "$LOGS/reward.txt"
    exit 0
fi
echo "GATE PASSED"

########################################
# Shared helper: extract get_sampling_args and discover vLLM param
########################################
# Write a helper module that all tests source
cat > /tmp/test_helper.py << 'PYEOF'
import ast, sys, re, inspect, textwrap
from dataclasses import dataclass

REPO = sys.argv[1] if len(sys.argv) > 1 else "/workspace/prime-rl"
TARGET = f"{REPO}/src/prime_rl/orchestrator/utils.py"

@dataclass
class FakeExtraBody:
    def __iter__(self):
        return iter({}.items())
    def items(self):
        return {}.items()

@dataclass
class FakeSamplingConfig:
    temperature: float = 1.0
    temp_scheduler: object = None
    min_tokens: int = 0
    repetition_penalty: float = 1.0
    extra_body: object = None
    max_tokens: int = 100

    def __post_init__(self):
        if self.extra_body is None:
            self.extra_body = FakeExtraBody()

    def __iter__(self):
        return iter({
            'temperature': self.temperature,
            'temp_scheduler': self.temp_scheduler,
            'min_tokens': self.min_tokens,
            'repetition_penalty': self.repetition_penalty,
            'extra_body': self.extra_body,
            'max_tokens': self.max_tokens,
        }.items())

def extract_function(filepath, func_name):
    """Extract a function from source using AST (robust to decorators, multiline sigs)."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            lines = source.splitlines(keepends=True)
            func_src = "".join(lines[node.lineno - 1:node.end_lineno])
            # Remove SamplingConfig type annotation so our mock works
            func_src = re.sub(r':\s*SamplingConfig', '', func_src)
            ns = {"__builtins__": __builtins__}
            exec(compile(func_src, '<extracted>', 'exec'), ns)
            return ns[func_name], node
    return None, None

def discover_vllm_param(func):
    """Find the boolean parameter that controls vLLM-specific behavior.
    Tries: any param with 'vllm' in its name, then any bool param besides known ones."""
    sig = inspect.signature(func)
    known = {'sampling_config', 'temperature'}
    # First: param name contains 'vllm'
    for name, p in sig.parameters.items():
        if name in known:
            continue
        if 'vllm' in name.lower():
            return name
    # Fallback: any bool-defaulted param that isn't in known
    for name, p in sig.parameters.items():
        if name in known:
            continue
        if isinstance(p.default, bool):
            return name
    # Last fallback: try legacy name
    for name in sig.parameters:
        if name == 'use_token_client':
            return name
    return None

def call_with_vllm(func, cfg, temperature, vllm_param, vllm_value):
    """Call get_sampling_args with the discovered vLLM param."""
    if vllm_param:
        return func(cfg, temperature=temperature, **{vllm_param: vllm_value})
    else:
        # Try positional: func(cfg, temperature, vllm_value)
        return func(cfg, temperature, vllm_value)
PYEOF

########################################
# F2P 1: vLLM=True → return_token_ids in extra_body
########################################
# [pr_diff] (0.35): Core bug — vLLM backend must get return_token_ids=True
echo ""
echo "--- F2P: vLLM backend gets return_token_ids ---"
F2P_1=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from test_helper import *

func, node = extract_function(TARGET, 'get_sampling_args')
if func is None:
    print('0'); sys.exit(0)

vllm_param = discover_vllm_param(func)
cfg = FakeSamplingConfig()

try:
    result = call_with_vllm(func, cfg, 0.7, vllm_param, True)
except Exception:
    print('0'); sys.exit(0)

if not isinstance(result, dict):
    print('0'); sys.exit(0)

eb = result.get('extra_body', {})
if isinstance(eb, dict) and eb.get('return_token_ids') == True:
    print('1')
else:
    print('0')
PYEOF
)
echo "  Result: $F2P_1"
SCORE=$(python3 -c "print($SCORE + 0.35 * ${F2P_1:-0})")

########################################
# F2P 2: vLLM=False → no vLLM-specific keys AND result is non-trivial
########################################
# [pr_diff] (0.20): Non-vLLM backend must NOT get return_token_ids/top_k/min_p
echo ""
echo "--- F2P: non-vLLM backend omits vLLM keys ---"
F2P_2=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from test_helper import *

func, node = extract_function(TARGET, 'get_sampling_args')
if func is None:
    print('0'); sys.exit(0)

vllm_param = discover_vllm_param(func)
cfg = FakeSamplingConfig()

try:
    result = call_with_vllm(func, cfg, 0.7, vllm_param, False)
except Exception:
    print('0'); sys.exit(0)

if not isinstance(result, dict):
    print('0'); sys.exit(0)

# Stub protection: result must have logprobs key (non-trivial output)
if 'logprobs' not in result:
    print('0'); sys.exit(0)

eb = result.get('extra_body', {})
if not isinstance(eb, dict):
    eb = {}
has_vllm_keys = 'return_token_ids' in eb or 'top_k' in eb or 'min_p' in eb
print('0' if has_vllm_keys else '1')
PYEOF
)
echo "  Result: $F2P_2"
SCORE=$(python3 -c "print($SCORE + 0.20 * ${F2P_2:-0})")

########################################
# F2P 3: logprobs always True regardless of backend
########################################
# [pr_diff] (0.10): logprobs must be set for both backends
echo ""
echo "--- F2P: logprobs always True ---"
F2P_3=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from test_helper import *

func, node = extract_function(TARGET, 'get_sampling_args')
if func is None:
    print('0'); sys.exit(0)

vllm_param = discover_vllm_param(func)
cfg = FakeSamplingConfig()

ok = True
for val in [True, False]:
    try:
        result = call_with_vllm(func, cfg, 0.7, vllm_param, val)
        if not isinstance(result, dict) or result.get('logprobs') != True:
            ok = False
            break
    except Exception:
        ok = False
        break

print('1' if ok else '0')
PYEOF
)
echo "  Result: $F2P_3"
SCORE=$(python3 -c "print($SCORE + 0.10 * ${F2P_3:-0})")

########################################
# P2P: min_tokens and repetition_penalty preserved
########################################
# [pr_diff] (0.10): existing params must still appear in extra_body
echo ""
echo "--- P2P: min_tokens and repetition_penalty preserved ---"
P2P_1=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from test_helper import *

func, node = extract_function(TARGET, 'get_sampling_args')
if func is None:
    print('0'); sys.exit(0)

vllm_param = discover_vllm_param(func)
cfg = FakeSamplingConfig(min_tokens=10, repetition_penalty=1.5)

try:
    result = call_with_vllm(func, cfg, 0.7, vllm_param, True)
except Exception:
    print('0'); sys.exit(0)

if not isinstance(result, dict):
    print('0'); sys.exit(0)

eb = result.get('extra_body', {})
if not isinstance(eb, dict):
    print('0'); sys.exit(0)

ok = eb.get('min_tokens') == 10 and eb.get('repetition_penalty') == 1.5
print('1' if ok else '0')
PYEOF
)
echo "  Result: $P2P_1"
SCORE=$(python3 -c "print($SCORE + 0.10 * ${P2P_1:-0})")

########################################
# P2P: max_tokens in result
########################################
# [pr_diff] (0.05): max_tokens must still be passed through
echo ""
echo "--- P2P: max_tokens in result ---"
P2P_2=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from test_helper import *

func, node = extract_function(TARGET, 'get_sampling_args')
if func is None:
    print('0'); sys.exit(0)

vllm_param = discover_vllm_param(func)
cfg = FakeSamplingConfig(max_tokens=200)

try:
    result = call_with_vllm(func, cfg, 0.7, vllm_param, True)
except Exception:
    print('0'); sys.exit(0)

if not isinstance(result, dict):
    print('0'); sys.exit(0)

print('1' if result.get('max_tokens') == 200 else '0')
PYEOF
)
echo "  Result: $P2P_2"
SCORE=$(python3 -c "print($SCORE + 0.05 * ${P2P_2:-0})")

########################################
# Structural: orchestrator.py callers updated
########################################
# [pr_diff] (0.10): orchestrator.py must not use old use_token_client keyword
# WHY AST: orchestrator.py imports heavy deps (vllm, verifiers, etc.) — cannot execute on CPU
echo ""
echo "--- Structural: orchestrator.py caller uses correct flag ---"
S1=$(python3 << 'PYEOF'
import ast

with open("/workspace/prime-rl/src/prime_rl/orchestrator/orchestrator.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        name = ''
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name == 'get_sampling_args':
            for kw in node.keywords:
                if kw.arg == 'use_token_client':
                    print('0')
                    raise SystemExit(0)

# No old keyword found — pass
print('1')
PYEOF
)
echo "  Result: $S1"
SCORE=$(python3 -c "print($SCORE + 0.10 * ${S1:-0})")

########################################
# Config: function signature doesn't use use_token_client
########################################
# [agent_config] (0.05): "Explicit is better than implicit" — AGENTS.md:13 @ b92c2128
echo ""
echo "--- Config: explicit parameter naming ---"
C1=$(python3 << 'PYEOF'
import ast

with open("/workspace/prime-rl/src/prime_rl/orchestrator/utils.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_sampling_args':
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.arg == 'use_token_client':
                print('0')
                raise SystemExit(0)
        print('1')
        raise SystemExit(0)

print('0')
PYEOF
)
echo "  Result: $C1"
SCORE=$(python3 -c "print($SCORE + 0.05 * ${C1:-0})")

########################################
# Anti-stub: get_sampling_args is substantive
########################################
echo ""
echo "--- Anti-stub: get_sampling_args is substantive ---"
AS=$(python3 << 'PYEOF'
import ast

with open("/workspace/prime-rl/src/prime_rl/orchestrator/utils.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'get_sampling_args':
        # Count meaningful statements (exclude docstrings, pass, ellipsis)
        meaningful = 0
        for stmt in ast.walk(node):
            if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                 ast.If, ast.For, ast.Return, ast.Call)):
                meaningful += 1
        print('1' if meaningful >= 5 else '0')
        raise SystemExit(0)

print('0')
PYEOF
)
echo "  Result: $AS"
SCORE=$(python3 -c "print($SCORE + 0.05 * ${AS:-0})")

########################################
# Final score
########################################
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$LOGS/reward.txt"

# Write detailed JSON
python3 -c "
import json
json.dump({
    'reward': float('$SCORE'),
    'behavioral': 0.35 * ${F2P_1:-0} + 0.20 * ${F2P_2:-0} + 0.10 * ${F2P_3:-0},
    'regression': 0.10 * ${P2P_1:-0} + 0.05 * ${P2P_2:-0},
    'structural': 0.10 * ${S1:-0} + 0.05 * ${AS:-0},
    'config': 0.05 * ${C1:-0},
}, open('$LOGS/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
