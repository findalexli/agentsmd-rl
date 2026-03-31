#!/usr/bin/env bash
set +e

UTILS_PY="/workspace/prime-rl/src/prime_rl/utils/utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.75, regression=0.10, structural=0.15
WEIGHTS[async_exit]=0.30
WEIGHTS[sync_exit]=0.25
WEIGHTS[finally_cleanup]=0.10
WEIGHTS[wandb_cleanup]=0.10
WEIGHTS[p2p_success]=0.10
WEIGHTS[antistub]=0.15

for key in async_exit sync_exit finally_cleanup wandb_cleanup p2p_success antistub; do
    RESULTS[$key]=0
done

# ========== GATE: Syntax check ==========
python3 -c "import ast; ast.parse(open('$UTILS_PY').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: utils.py parses"

# ---- Helper: extract clean_exit function and exec with mocks ----
EXTRACT_AND_EXEC='
import asyncio, sys, types, functools

wandb_mock = types.ModuleType("wandb")
wandb_mock.finish = lambda exit_code=None: None
sys.modules["wandb"] = wandb_mock

dist_mock = types.ModuleType("torch.distributed")
dist_mock.is_initialized = lambda: False
dist_mock.destroy_process_group = lambda: None
sys.modules["torch"] = types.ModuleType("torch")
sys.modules["torch.distributed"] = dist_mock

with open("/workspace/prime-rl/src/prime_rl/utils/utils.py") as f:
    src = f.read()

lines = src.split("\n")
start = None
end = None
for i, line in enumerate(lines):
    if line.startswith("def clean_exit("):
        start = i
    elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
        end = i
        break
if end is None:
    end = len(lines)

func_src = "\n".join(lines[start:end])
ns = {
    "asyncio": asyncio,
    "functools": functools,
    "wandb": wandb_mock,
    "dist": dist_mock,
    "sys": sys,
    "get_logger": lambda: types.SimpleNamespace(
        opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None)
    ),
}
exec(func_src, ns)
clean_exit = ns["clean_exit"]
'

# ========== BEHAVIORAL: Async wrapper terminates with SystemExit on error (0.30) ==========
# [pr_diff] (0.30): Async clean_exit must raise SystemExit (via sys.exit) instead of re-raising the original exception
python3 << PYEOF
$EXTRACT_AND_EXEC

@clean_exit
async def failing_async():
    raise ValueError("dataset is not set")

# Run it — should get SystemExit, not ValueError
try:
    asyncio.run(failing_async())
    print("FAIL: no exception raised at all")
    sys.exit(1)
except SystemExit:
    print("PASS: async wrapper raises SystemExit")
    sys.exit(0)
except ValueError:
    print("FAIL: async wrapper re-raised ValueError instead of calling sys.exit")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected exception type: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[async_exit]=1 && echo "TEST async_exit: PASS" || echo "TEST async_exit: FAIL"

# ========== BEHAVIORAL: Sync wrapper terminates with SystemExit on error (0.25) ==========
# [pr_diff] (0.25): Sync clean_exit must raise SystemExit (via sys.exit) instead of re-raising the original exception
python3 << PYEOF
$EXTRACT_AND_EXEC

@clean_exit
def failing_sync():
    raise RuntimeError("config missing")

try:
    failing_sync()
    print("FAIL: no exception raised at all")
    sys.exit(1)
except SystemExit:
    print("PASS: sync wrapper raises SystemExit")
    sys.exit(0)
except RuntimeError:
    print("FAIL: sync wrapper re-raised RuntimeError instead of calling sys.exit")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected exception type: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[sync_exit]=1 && echo "TEST sync_exit: PASS" || echo "TEST sync_exit: FAIL"

# ========== BEHAVIORAL: Finally block still runs (dist cleanup) (0.10) ==========
# [pr_diff] (0.10): The finally block must still execute, destroying the process group on error
python3 << 'PYEOF'
import asyncio, sys, types, functools

wandb_mock = types.ModuleType("wandb")
wandb_mock.finish = lambda exit_code=None: None
sys.modules["wandb"] = wandb_mock

# Track whether destroy_process_group was called
cleanup_called = []
dist_mock = types.ModuleType("torch.distributed")
dist_mock.is_initialized = lambda: True
dist_mock.destroy_process_group = lambda: cleanup_called.append(True)
sys.modules["torch"] = types.ModuleType("torch")
sys.modules["torch.distributed"] = dist_mock

with open("/workspace/prime-rl/src/prime_rl/utils/utils.py") as f:
    src = f.read()

lines = src.split("\n")
start = None
end = None
for i, line in enumerate(lines):
    if line.startswith("def clean_exit("):
        start = i
    elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
        end = i
        break
if end is None:
    end = len(lines)

func_src = "\n".join(lines[start:end])
ns = {
    "asyncio": asyncio,
    "functools": functools,
    "wandb": wandb_mock,
    "dist": dist_mock,
    "sys": sys,
    "get_logger": lambda: types.SimpleNamespace(
        opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None)
    ),
}
exec(func_src, ns)
clean_exit = ns["clean_exit"]

@clean_exit
async def failing_async():
    raise ValueError("boom")

try:
    asyncio.run(failing_async())
except (SystemExit, Exception):
    pass

if cleanup_called:
    print("PASS: finally block ran destroy_process_group")
    sys.exit(0)
else:
    print("FAIL: destroy_process_group was not called")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[finally_cleanup]=1 && echo "TEST finally_cleanup: PASS" || echo "TEST finally_cleanup: FAIL"

# ========== BEHAVIORAL: wandb.finish(exit_code=1) called on error (0.10) ==========
# [pr_diff] (0.10): wandb.finish must be called with exit_code=1 when an exception occurs
python3 << 'PYEOF'
import asyncio, sys, types, functools

# Track wandb.finish calls
finish_calls = []
wandb_mock = types.ModuleType("wandb")
wandb_mock.finish = lambda exit_code=None: finish_calls.append(exit_code)
sys.modules["wandb"] = wandb_mock

dist_mock = types.ModuleType("torch.distributed")
dist_mock.is_initialized = lambda: False
dist_mock.destroy_process_group = lambda: None
sys.modules["torch"] = types.ModuleType("torch")
sys.modules["torch.distributed"] = dist_mock

with open("/workspace/prime-rl/src/prime_rl/utils/utils.py") as f:
    src = f.read()

lines = src.split("\n")
start = None
end = None
for i, line in enumerate(lines):
    if line.startswith("def clean_exit("):
        start = i
    elif start is not None and i > start and line and not line[0].isspace() and line[0] != "#":
        end = i
        break
if end is None:
    end = len(lines)

func_src = "\n".join(lines[start:end])
ns = {
    "asyncio": asyncio,
    "functools": functools,
    "wandb": wandb_mock,
    "dist": dist_mock,
    "sys": sys,
    "get_logger": lambda: types.SimpleNamespace(
        opt=lambda **kw: types.SimpleNamespace(error=lambda msg: None)
    ),
}
exec(func_src, ns)
clean_exit = ns["clean_exit"]

@clean_exit
async def failing_async():
    raise ValueError("dataset error")

try:
    asyncio.run(failing_async())
except (SystemExit, Exception):
    pass

# wandb.finish should have been called with exit_code=1
if 1 in finish_calls:
    print("PASS: wandb.finish(exit_code=1) called on error")
    sys.exit(0)
else:
    print(f"FAIL: wandb.finish calls were: {finish_calls}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[wandb_cleanup]=1 && echo "TEST wandb_cleanup: PASS" || echo "TEST wandb_cleanup: FAIL"

# ========== REGRESSION: Success path still works (0.10) ==========
# [repo_tests] (0.10): pass-to-pass — clean_exit on success must return normally
python3 << PYEOF
$EXTRACT_AND_EXEC

# Test async success path
@clean_exit
async def success_async():
    return 42

result = asyncio.run(success_async())
if result != 42:
    print(f"FAIL: async success returned {result} instead of 42")
    sys.exit(1)

# Test sync success path
@clean_exit
def success_sync():
    return "ok"

result = success_sync()
if result != "ok":
    print(f"FAIL: sync success returned {result} instead of 'ok'")
    sys.exit(1)

print("PASS: success path returns values correctly")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[p2p_success]=1 && echo "TEST p2p_success: PASS" || echo "TEST p2p_success: FAIL"

# ========== STRUCTURAL: Anti-stub via AST (0.15) ==========
# [pr_diff] (0.15): utils.py must not be stubbed out — clean_exit must have substantial implementation
python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/utils/utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# File must retain substantial content (not gutted)
non_blank = [l for l in source.strip().split("\n") if l.strip()]
if len(non_blank) < 50:
    print(f"FAIL: utils.py has only {len(non_blank)} non-blank lines (likely stubbed)")
    sys.exit(1)

# Find clean_exit function
clean_exit_node = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "clean_exit":
        clean_exit_node = node
        break

if clean_exit_node is None:
    print("FAIL: clean_exit function not found")
    sys.exit(1)

# clean_exit must have inner function definitions (the wrappers)
inner_funcs = []
for node in ast.walk(clean_exit_node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name != "clean_exit":
        inner_funcs.append(node)

if len(inner_funcs) < 2:
    print(f"FAIL: clean_exit has only {len(inner_funcs)} inner functions (need >=2 for async+sync wrappers)")
    sys.exit(1)

# At least one inner function must be async
has_async = any(isinstance(f, ast.AsyncFunctionDef) for f in inner_funcs)
if not has_async:
    print("FAIL: clean_exit has no async inner function")
    sys.exit(1)

# Inner functions must have try/except/finally (not trivial stubs)
has_try = False
for func in inner_funcs:
    for node in ast.walk(func):
        if isinstance(node, ast.Try):
            has_try = True
            break
    if has_try:
        break

if not has_try:
    print("FAIL: inner wrappers have no try/except (likely stubbed)")
    sys.exit(1)

# Must reference destroy_process_group somewhere in the function (AST attribute check)
has_dpg = False
for node in ast.walk(clean_exit_node):
    if isinstance(node, ast.Attribute) and node.attr == "destroy_process_group":
        has_dpg = True
        break

if not has_dpg:
    print("FAIL: destroy_process_group not referenced in clean_exit")
    sys.exit(1)

print("PASS: clean_exit has expected structure (AST verified)")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ========== SCORE ==========
SCORE=$(python3 -c "
w={
    'async_exit':${WEIGHTS[async_exit]},
    'sync_exit':${WEIGHTS[sync_exit]},
    'finally_cleanup':${WEIGHTS[finally_cleanup]},
    'wandb_cleanup':${WEIGHTS[wandb_cleanup]},
    'p2p_success':${WEIGHTS[p2p_success]},
    'antistub':${WEIGHTS[antistub]},
}
r={
    'async_exit':${RESULTS[async_exit]},
    'sync_exit':${RESULTS[sync_exit]},
    'finally_cleanup':${RESULTS[finally_cleanup]},
    'wandb_cleanup':${RESULTS[wandb_cleanup]},
    'p2p_success':${RESULTS[p2p_success]},
    'antistub':${RESULTS[antistub]},
}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
