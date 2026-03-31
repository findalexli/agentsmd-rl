#!/usr/bin/env bash
set +e

TOTAL=0
POSSIBLE=100
FILE="areal/engine/vllm_ext/areal_vllm_server.py"

add() { TOTAL=$((TOTAL + $1)); }

echo "=== Gate: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "PASS: syntax OK"

########################################################################
# Helper: Extract an async function from the file and execute it with
# mocks to verify call ordering and error resilience.
# This is a genuine behavioral test — we CALL the code, not just inspect AST.
########################################################################
cat > /tmp/behavioral_test.py << 'PYEOF'
"""
Extract an async function, exec it with mocks, verify behavior.

Usage:
  python3 /tmp/behavioral_test.py <func_name> <file> normal
  python3 /tmp/behavioral_test.py <func_name> <file> error_resilience
"""
import ast, sys, asyncio, textwrap
from unittest.mock import AsyncMock, MagicMock

func_name = sys.argv[1]
filepath = sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "normal"

source = open(filepath).read()
tree = ast.parse(source)

# Find the target function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
        func_node = node
        break

if func_node is None:
    print(f"FAIL: async function '{func_name}' not found", file=sys.stderr)
    sys.exit(1)

# Anti-stub: function body must have >= 4 top-level statements
if len(func_node.body) < 4:
    print(f"FAIL: {func_name} body too short ({len(func_node.body)} stmts, need >=4)", file=sys.stderr)
    sys.exit(1)

# Extract function source lines
lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Build a namespace with stubs for type annotations and common names
ns = {
    "__builtins__": __builtins__,
    "logger": MagicMock(),
    "JSONResponse": lambda content=None, **kw: {"content": content},
    "json": MagicMock(),
    "asyncio": asyncio,
}
# Add type annotation stubs so exec of function def doesn't blow up
for tname in [
    "UpdateWeightsRequest", "UpdateWeightsRequestLora",
    "UpdateGroupRequest", "UpdateWeightsFromXcclRequest",
    "UpdateWeightsFromXcclRequestLora", "Request", "Response",
    "Optional", "List", "Dict", "Any",
]:
    ns[tname] = MagicMock()

try:
    exec(compile(func_src, filepath, "exec"), ns)
except Exception as e:
    print(f"FAIL: could not compile/exec function: {e}", file=sys.stderr)
    sys.exit(1)

func = ns.get(func_name)
if not callable(func):
    print(f"FAIL: {func_name} not callable after exec", file=sys.stderr)
    sys.exit(1)

# Build mock self with engine_client
mock_self = MagicMock()
mock_client = AsyncMock()
mock_self.engine_client = mock_client

# Build mock request with common attributes
mock_request = MagicMock()
mock_request.name_or_path = "test/model"
mock_request.load_format = "auto"
mock_request.revision = "main"
mock_request.model_dump.return_value = {"name_or_path": "test/model"}

# Track call order via side_effects
call_log = []

async def _pause(*a, **kw):
    call_log.append("pause")
async def _resume(*a, **kw):
    call_log.append("resume")
async def _rpc(*a, **kw):
    call_log.append("rpc")
    return MagicMock()
async def _rpc_raise(*a, **kw):
    call_log.append("rpc")
    raise RuntimeError("simulated RPC failure")

errors = []

if mode == "normal":
    mock_client.pause_generation.side_effect = _pause
    mock_client.resume_generation.side_effect = _resume
    mock_client.collective_rpc.side_effect = _rpc

    try:
        asyncio.run(func(mock_self, mock_request))
    except Exception:
        pass  # other failures are OK; we only care about call sequence

    if "pause" not in call_log:
        errors.append("pause_generation() never called")
    if "rpc" not in call_log:
        errors.append("collective_rpc() never called")
    if "resume" not in call_log:
        errors.append("resume_generation() never called")

    # Check ordering: pause before rpc
    if "pause" in call_log and "rpc" in call_log:
        if call_log.index("pause") > call_log.index("rpc"):
            errors.append(f"pause_generation called AFTER collective_rpc: {call_log}")

elif mode == "error_resilience":
    mock_client.pause_generation.side_effect = _pause
    mock_client.resume_generation.side_effect = _resume
    mock_client.collective_rpc.side_effect = _rpc_raise

    try:
        asyncio.run(func(mock_self, mock_request))
    except Exception:
        pass  # expected — rpc raises

    if "resume" not in call_log:
        errors.append("resume_generation NOT called after collective_rpc failure (finally block missing or broken)")

if errors:
    for e in errors:
        print(f"FAIL ({func_name}, {mode}): {e}", file=sys.stderr)
    sys.exit(1)

print(f"OK ({func_name}, {mode}): call_log={call_log}")
sys.exit(0)
PYEOF

########################################################################
# BEHAVIORAL: Weight update endpoints — call ordering
# [pr_diff] (0.10 each): pause → rpc → resume sequence verified by execution
########################################################################

for fn in areal_update_weight areal_update_weight_lora areal_update_weight_xccl areal_update_weight_lora_xccl; do
    echo ""
    echo "=== Behavioral: ${fn} call ordering (pause → rpc → resume) ==="
    # [pr_diff] (0.10): weight update must call pause, then rpc, then resume
    if python3 /tmp/behavioral_test.py "$fn" "$FILE" normal; then
        echo "PASS"
        add 10
    else
        echo "FAIL"
    fi
done

########################################################################
# BEHAVIORAL: Weight update endpoints — error resilience
# [pr_diff] (0.05 each): resume_generation called even when collective_rpc raises
########################################################################

for fn in areal_update_weight areal_update_weight_lora areal_update_weight_xccl areal_update_weight_lora_xccl; do
    echo ""
    echo "=== Behavioral: ${fn} error resilience (resume after rpc failure) ==="
    # [pr_diff] (0.05): resume_generation must be called even on RPC failure
    if python3 /tmp/behavioral_test.py "$fn" "$FILE" error_resilience; then
        echo "PASS"
        add 5
    else
        echo "FAIL"
    fi
done

########################################################################
# BEHAVIORAL: Pause endpoint — calls native pause_generation
########################################################################

echo ""
echo "=== Behavioral: areal_pause_generation uses native API ==="
# [pr_diff] (0.05): areal_pause_generation must call pause_generation, not abort
cat > /tmp/test_pause.py << 'PYEOF'
import ast, sys, asyncio
from unittest.mock import AsyncMock, MagicMock

filepath = sys.argv[1]
source = open(filepath).read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "areal_pause_generation":
        func_node = node
        break

if func_node is None:
    print("FAIL: areal_pause_generation not found", file=sys.stderr)
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

ns = {"__builtins__": __builtins__, "logger": MagicMock(), "JSONResponse": lambda **kw: kw,
      "Request": MagicMock(), "asyncio": __import__("asyncio")}
for t in ["Optional", "Any"]:
    ns[t] = MagicMock()

exec(compile(func_src, filepath, "exec"), ns)
func = ns["areal_pause_generation"]

mock_self = MagicMock()
mock_client = AsyncMock()
mock_self.engine_client = mock_client

calls = []
async def _p(*a, **kw): calls.append("pause")
async def _a(*a, **kw): calls.append("abort")
mock_client.pause_generation.side_effect = _p
mock_client.abort_all_reqs.side_effect = _a
mock_client.call_utility_async.side_effect = _a

try:
    asyncio.run(func(mock_self, MagicMock()))
except Exception:
    pass

if "pause" not in calls:
    print("FAIL: pause_generation() never called", file=sys.stderr)
    sys.exit(1)
if "abort" in calls:
    print("FAIL: still calls abort_all_reqs/call_utility_async", file=sys.stderr)
    sys.exit(1)
print(f"OK: areal_pause_generation calls={calls}")
sys.exit(0)
PYEOF

if python3 /tmp/test_pause.py "$FILE"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

########################################################################
# BEHAVIORAL: Continue endpoint — calls resume_generation
########################################################################

echo ""
echo "=== Behavioral: areal_continue_generation calls resume_generation ==="
# [pr_diff] (0.05): must call resume_generation on the engine client
cat > /tmp/test_continue.py << 'PYEOF'
import ast, sys, asyncio
from unittest.mock import AsyncMock, MagicMock

filepath = sys.argv[1]
source = open(filepath).read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "areal_continue_generation":
        func_node = node
        break

if func_node is None:
    print("FAIL: areal_continue_generation not found", file=sys.stderr)
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

ns = {"__builtins__": __builtins__, "logger": MagicMock(), "JSONResponse": lambda **kw: kw,
      "Request": MagicMock(), "asyncio": __import__("asyncio")}
for t in ["Optional", "Any"]:
    ns[t] = MagicMock()

exec(compile(func_src, filepath, "exec"), ns)
func = ns["areal_continue_generation"]

mock_self = MagicMock()
mock_client = AsyncMock()
mock_self.engine_client = mock_client

called = []
async def _r(*a, **kw): called.append("resume")
mock_client.resume_generation.side_effect = _r

try:
    asyncio.run(func(mock_self, MagicMock()))
except Exception:
    pass

if "resume" not in called:
    print("FAIL: resume_generation() never called", file=sys.stderr)
    sys.exit(1)
print(f"OK: areal_continue_generation calls={called}")
sys.exit(0)
PYEOF

if python3 /tmp/test_continue.py "$FILE"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

########################################################################
# STRUCTURAL: No monkey-patching remains (gated behind syntax check)
########################################################################

echo ""
echo "=== Structural: No EngineCore monkey-patching ==="
# [pr_diff] (0.05): setattr(EngineCore, ...) and hook() must be removed
if python3 -c "
import ast, sys

source = open('$FILE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'setattr':
        if node.args and isinstance(node.args[0], ast.Name) and node.args[0].id == 'EngineCore':
            print('setattr(EngineCore, ...) found', file=sys.stderr)
            sys.exit(1)
    if isinstance(node, ast.FunctionDef) and node.name == 'hook':
        print('hook() function still defined', file=sys.stderr)
        sys.exit(1)
sys.exit(0)
"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

echo ""
echo "=== Structural: No abort_all_reqs function definition ==="
# [pr_diff] (0.05): standalone abort_all_reqs function must be removed
if python3 -c "
import ast, sys

tree = ast.parse(open('$FILE').read())
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'abort_all_reqs':
        print('abort_all_reqs still defined', file=sys.stderr)
        sys.exit(1)
sys.exit(0)
"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

########################################################################
# PASS-TO-PASS: Existing endpoints and structures preserved
########################################################################

echo ""
echo "=== Pass-to-pass: All route decorators preserved ==="
# [pr_diff] (0.05): all original route paths must still exist
if python3 -c "
import ast, sys

source = open('$FILE').read()
tree = ast.parse(source)

route_strings = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                for arg in dec.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        route_strings.add(arg.value)

required = {
    '/areal_update_weights', '/areal_update_weights_lora',
    '/areal_update_weights_xccl', '/areal_update_weights_lora_xccl',
    '/areal_init_weights_update_group',
    '/areal_set_update_weight_meta', '/areal_set_update_weight_meta_lora',
    '/areal_pause_generation', '/areal_continue_generation',
    '/v1/completions',
}
missing = required - route_strings
if missing:
    print(f'Missing routes: {missing}', file=sys.stderr)
    sys.exit(1)
sys.exit(0)
"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

echo ""
echo "=== Pass-to-pass: Request model classes preserved ==="
# [pr_diff] (0.05): Pydantic model classes must still be defined
if python3 -c "
import ast, sys

tree = ast.parse(open('$FILE').read())
required = {'UpdateWeightsRequest', 'UpdateWeightsRequestLora', 'UpdateGroupRequest',
            'UpdateWeightsFromXcclRequest', 'UpdateWeightsFromXcclRequestLora'}
found = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name in required}
missing = required - found
if missing:
    print(f'Missing: {missing}', file=sys.stderr)
    sys.exit(1)
sys.exit(0)
"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

########################################################################
# CONFIG-DERIVED: No wildcard imports
########################################################################

echo ""
echo "=== Config-derived: No wildcard imports ==="
# [agent_config] (0.05): "No wildcard imports" — CLAUDE.md:65
if python3 -c "
import ast, sys
tree = ast.parse(open('$FILE').read())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == '*':
                sys.exit(1)
sys.exit(0)
"; then
    echo "PASS"
    add 5
else
    echo "FAIL"
fi

########################################################################
# Final score
########################################################################

echo ""
REWARD=$(python3 -c "print(round($TOTAL / $POSSIBLE, 4))")
echo "=== Final score: $REWARD ($TOTAL / $POSSIBLE) ==="
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
total = $TOTAL
beh = min(total, 70)
reg = min(max(total - 70, 0), 10)
cfg = min(max(total - 80, 0), 5)
json.dump({
    'reward': round(total / $POSSIBLE, 4),
    'behavioral': round(beh / $POSSIBLE, 4),
    'regression': round(reg / $POSSIBLE, 4),
    'config': round(cfg / $POSSIBLE, 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
