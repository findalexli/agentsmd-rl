#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-/workspace}"
SCORE="0.0"

EVAL_UTILS="$REPO_ROOT/src/prime_rl/orchestrator/eval_utils.py"
VF_UTILS="$REPO_ROOT/src/prime_rl/orchestrator/vf_utils.py"

add_score() {
    SCORE=$(python3 -c "print(round($SCORE + $1, 4))")
}

########################################
# GATE: Syntax check
########################################
echo "=== GATE: Syntax check ==="
python3 -c "compile(open('$EVAL_UTILS').read(), '$EVAL_UTILS', 'exec')" || {
    echo "FAIL: eval_utils.py has syntax errors"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
}
python3 -c "compile(open('$VF_UTILS').read(), '$VF_UTILS', 'exec')" || {
    echo "FAIL: vf_utils.py has syntax errors"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
}
echo "PASS: syntax OK"

# Allow individual test failures without aborting the script
set +e

########################################
# [pr_diff] (0.35): generate() catches per-group exceptions and returns successful results
# Behavioral F2P. Mocking justification: generate() requires verifiers library
# (vf.Environment, vf.ClientConfig) and ZMQ worker infrastructure unavailable in test.
########################################
echo "=== TEST: generate catches per-group exceptions ==="
python3 << 'PYEOF'
import sys, types, asyncio
from unittest.mock import MagicMock

# Set up mock modules BEFORE importing vf_utils
vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('Env', (), {})
vf_mock.ClientConfig = type('CC', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock

workers_mock = types.ModuleType('verifiers.workers')
workers_mock.ZMQEnvClient = MagicMock
workers_mock.ZMQEnvServer = MagicMock
sys.modules['verifiers.workers'] = workers_mock

envs_mock = types.ModuleType('verifiers.envs')
sys.modules['verifiers.envs'] = envs_mock
envs_env_mock = types.ModuleType('verifiers.envs.environment')
envs_env_mock.EnvClient = MagicMock
sys.modules['verifiers.envs.environment'] = envs_env_mock

utils_mock = types.ModuleType('verifiers.utils')
sys.modules['verifiers.utils'] = utils_mock
wu_mock = types.ModuleType('verifiers.utils.worker_utils')
wu_mock.get_free_port_pair = lambda: 12345
sys.modules['verifiers.utils.worker_utils'] = wu_mock

for mod_name in ['prime_rl', 'prime_rl.utils']:
    sys.modules[mod_name] = types.ModuleType(mod_name)

mock_logger = MagicMock()
logger_mod = types.ModuleType('prime_rl.utils.logger')
logger_mod.get_logger = lambda: mock_logger
logger_mod.InterceptHandler = MagicMock
logger_mod.ProgressTracker = MagicMock
sys.modules['prime_rl.utils.logger'] = logger_mod

sys.path.insert(0, '/workspace/src')
import importlib
vf_utils = importlib.import_module('prime_rl.orchestrator.vf_utils')

# Mock run_group: succeeds for first 3 examples, raises for the 4th
call_count = 0
async def mock_run_group(env, client, model_name, example, rollouts_per_example,
                         max_retries, state_columns, sampling_args):
    global call_count
    call_count += 1
    if example.get('fail'):
        raise RuntimeError("Simulated group failure")
    return [{'example_id': example['id'], 'reward': 1.0}]

vf_utils.run_group = mock_run_group

examples = [{'id': 0}, {'id': 1}, {'id': 2}, {'fail': True, 'id': 3}]

async def get_client():
    return MagicMock()

try:
    results = asyncio.run(vf_utils.generate(
        env=MagicMock(), model_name='m', examples=examples,
        rollouts_per_example=1, sampling_args={},
        get_client=get_client,
    ))
except Exception as e:
    print(f"FAIL: generate() crashed instead of handling group failure: {e}")
    sys.exit(1)

# Should have 3 successful results
assert len(results) == 3, f"Expected 3 results, got {len(results)}"
# Verify the successful example IDs are present
result_ids = {r['example_id'] for r in results}
assert result_ids == {0, 1, 2}, f"Expected example IDs {{0,1,2}}, got {result_ids}"
# Verify all 4 groups were attempted (not short-circuited)
assert call_count == 4, f"Expected 4 run_group calls, got {call_count}"
print("PASS: generate() catches per-group exceptions, returns 3/4 results")
PYEOF
if [ $? -eq 0 ]; then add_score 0.35; else echo "FAIL"; fi

########################################
# [pr_diff] (0.20): generate() attempts all groups even when all fail, returns []
# Behavioral F2P. Same mocking justification.
# Anti-stub: verifies run_group was called for every example (blocks `return []`).
########################################
echo "=== TEST: generate attempts all groups, filters failures ==="
python3 << 'PYEOF'
import sys, types, asyncio
from unittest.mock import MagicMock

# Fresh mock setup
for mod in list(sys.modules.keys()):
    if mod.startswith(('prime_rl', 'verifiers')):
        del sys.modules[mod]

vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('Env', (), {})
vf_mock.ClientConfig = type('CC', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock

workers_mock = types.ModuleType('verifiers.workers')
workers_mock.ZMQEnvClient = MagicMock
workers_mock.ZMQEnvServer = MagicMock
sys.modules['verifiers.workers'] = workers_mock

envs_mock = types.ModuleType('verifiers.envs')
sys.modules['verifiers.envs'] = envs_mock
envs_env_mock = types.ModuleType('verifiers.envs.environment')
envs_env_mock.EnvClient = MagicMock
sys.modules['verifiers.envs.environment'] = envs_env_mock

utils_mock = types.ModuleType('verifiers.utils')
sys.modules['verifiers.utils'] = utils_mock
wu_mock = types.ModuleType('verifiers.utils.worker_utils')
wu_mock.get_free_port_pair = lambda: 12345
sys.modules['verifiers.utils.worker_utils'] = wu_mock

for mod_name in ['prime_rl', 'prime_rl.utils']:
    sys.modules[mod_name] = types.ModuleType(mod_name)

mock_logger = MagicMock()
logger_mod = types.ModuleType('prime_rl.utils.logger')
logger_mod.get_logger = lambda: mock_logger
logger_mod.InterceptHandler = MagicMock
logger_mod.ProgressTracker = MagicMock
sys.modules['prime_rl.utils.logger'] = logger_mod

sys.path.insert(0, '/workspace/src')
import importlib
vf_utils = importlib.import_module('prime_rl.orchestrator.vf_utils')

# ALL groups fail
call_count = 0
async def mock_run_group(env, client, model_name, example, rollouts_per_example,
                         max_retries, state_columns, sampling_args):
    global call_count
    call_count += 1
    raise RuntimeError("All fail")

vf_utils.run_group = mock_run_group

async def get_client():
    return MagicMock()

num_examples = 5
results = asyncio.run(vf_utils.generate(
    env=MagicMock(), model_name='m',
    examples=[{'id': i} for i in range(num_examples)],
    rollouts_per_example=1, sampling_args={},
    get_client=get_client,
))

assert results == [], f"Expected empty list when all groups fail, got {results}"
# Anti-stub: verify generate actually attempted all groups, not just returned []
assert call_count == num_examples, \
    f"Expected {num_examples} run_group calls, got {call_count} (stub detected)"
print("PASS: generate() attempts all 5 groups, returns [] when all fail")
PYEOF
if [ $? -eq 0 ]; then add_score 0.20; else echo "FAIL"; fi

########################################
# [pr_diff] (0.20): evaluate_env early returns on empty outputs
# Behavioral F2P. Mocking justification: evaluate_env chains through
# evaluate() -> generate() -> verifiers ZMQ infrastructure.
# Anti-stub: verifies evaluate() was actually called (blocks log-only stubs).
########################################
echo "=== TEST: evaluate_env handles empty outputs ==="
python3 << 'PYEOF'
import sys, types, asyncio
from unittest.mock import MagicMock, AsyncMock

# Clean modules
for mod in list(sys.modules.keys()):
    if mod.startswith(('prime_rl', 'verifiers')):
        del sys.modules[mod]

vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('Env', (), {})
vf_mock.ClientConfig = type('CC', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock

for m in ['verifiers.workers', 'verifiers.envs', 'verifiers.envs.environment',
          'verifiers.utils', 'verifiers.utils.worker_utils']:
    sys.modules[m] = MagicMock()

for mod_name in ['prime_rl', 'prime_rl.configs', 'prime_rl.configs.orchestrator',
                 'prime_rl.utils', 'prime_rl.orchestrator']:
    sys.modules[mod_name] = types.ModuleType(mod_name)
sys.modules['prime_rl.configs.orchestrator'].EvalSamplingConfig = MagicMock

mock_logger = MagicMock()
logger_mod = types.ModuleType('prime_rl.utils.logger')
logger_mod.get_logger = lambda: mock_logger
logger_mod.InterceptHandler = MagicMock
logger_mod.ProgressTracker = MagicMock
sys.modules['prime_rl.utils.logger'] = logger_mod

mock_monitor = MagicMock()
monitor_mod = types.ModuleType('prime_rl.utils.monitor')
monitor_mod.get_monitor = lambda: mock_monitor
sys.modules['prime_rl.utils.monitor'] = monitor_mod

utils_mod = types.ModuleType('prime_rl.utils.utils')
utils_mod.capitalize = lambda s: s.capitalize()
sys.modules['prime_rl.utils.utils'] = utils_mod

# Mock vf_utils.evaluate to return empty list (all rollouts failed)
mock_evaluate = AsyncMock(return_value=[])
vf_utils_mod = types.ModuleType('prime_rl.orchestrator.vf_utils')
vf_utils_mod.evaluate = mock_evaluate
vf_utils_mod.get_completion_len = lambda x: 0
sys.modules['prime_rl.orchestrator.vf_utils'] = vf_utils_mod

sys.path.insert(0, '/workspace/src')
import importlib
eval_utils = importlib.import_module('prime_rl.orchestrator.eval_utils')

try:
    asyncio.run(eval_utils.evaluate_env(
        env=MagicMock(), env_name='test_env', model_name='m',
        sampling_args={}, num_examples=5, rollouts_per_example=2,
        max_retries=0, ckpt_step=100, step=50, get_client=AsyncMock(),
    ))
except Exception as e:
    print(f"FAIL: evaluate_env crashed on empty outputs: {e}")
    sys.exit(1)

# Anti-stub: verify evaluate() was actually called (not a stub that just logs)
assert mock_evaluate.called, \
    "FAIL: evaluate() was never called — evaluate_env appears to be a stub"

# Verify a warning was logged about empty/failed rollouts
warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
has_warning = any(kw in w.lower() for w in warning_calls
                  for kw in ('fail', 'skip', 'empty', 'no '))
assert has_warning, f"No warning about failed/empty rollouts. Warnings: {warning_calls}"
print("PASS: evaluate_env calls evaluate(), handles empty outputs with warning")
PYEOF
if [ $? -eq 0 ]; then add_score 0.20; else echo "FAIL"; fi

########################################
# [repo_tests] (0.10): compute_eval_ckpt_step regression (pure function, called directly)
########################################
echo "=== TEST: compute_eval_ckpt_step regression ==="
python3 << 'PYEOF'
import sys, types
from unittest.mock import MagicMock

# Clean and mock
for mod in list(sys.modules.keys()):
    if mod.startswith(('prime_rl', 'verifiers')):
        del sys.modules[mod]

vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('E', (), {})
vf_mock.ClientConfig = type('C', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock
for m in ['verifiers.workers', 'verifiers.envs', 'verifiers.envs.environment',
          'verifiers.utils', 'verifiers.utils.worker_utils',
          'prime_rl', 'prime_rl.configs', 'prime_rl.configs.orchestrator',
          'prime_rl.utils', 'prime_rl.utils.logger', 'prime_rl.utils.monitor',
          'prime_rl.utils.utils', 'prime_rl.orchestrator',
          'prime_rl.orchestrator.vf_utils']:
    sys.modules[m] = MagicMock()

sys.path.insert(0, '/workspace/src')
import importlib
eu = importlib.import_module('prime_rl.orchestrator.eval_utils')

f = eu.compute_eval_ckpt_step
assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
assert f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25) is None
assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=True) == 0
assert f(ckpt_step=25, prev_ckpt_step=25, last_eval_step=0, interval=25) is None
assert f(ckpt_step=76, prev_ckpt_step=24, last_eval_step=0, interval=25) == 75
print("PASS: compute_eval_ckpt_step regression tests pass")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL"; fi

########################################
# [agent_config] (0.10): No bare except blocks & no process-explanatory comments
# AGENTS.md:5 (no bare except) + AGENTS.md:7 (no process comments) @ 60f01a0
########################################
echo "=== TEST: Code quality (AGENTS.md rules) ==="
python3 << 'PYEOF'
import ast, re

for filepath in [
    "/workspace/src/prime_rl/orchestrator/eval_utils.py",
    "/workspace/src/prime_rl/orchestrator/vf_utils.py",
]:
    source = open(filepath).read()
    fname = filepath.split('/')[-1]
    tree = ast.parse(source)

    # [agent_config] AGENTS.md:5 — no bare except (must catch specific exceptions)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    raise AssertionError(
                        f"{fname}: bare except at line {node.lineno} — AGENTS.md:5")

    # [agent_config] AGENTS.md:7 — no process-explanatory comments
    for pattern in [r'(?i)#.*used to.*but now', r'(?i)#.*old code',
                    r'(?i)#.*previously.*now', r'(?i)#.*changed from',
                    r'(?i)#.*was originally', r'(?i)#.*refactored from']:
        matches = re.findall(pattern, source)
        if matches:
            raise AssertionError(
                f"{fname}: process-explanatory comment: {matches[0]} — AGENTS.md:7")

print("PASS: No bare excepts, no process-explanatory comments")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL"; fi

########################################
# [pr_diff] (0.05): evaluate() still calls generate (AST regression)
# AST justification: evaluate() requires full verifiers async ZMQ stack to invoke.
########################################
echo "=== TEST: evaluate() calls generate ==="
python3 << 'PYEOF'
import ast

source = open("/workspace/src/prime_rl/orchestrator/vf_utils.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'evaluate':
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if (isinstance(func, ast.Name) and func.id == 'generate') or \
                   (isinstance(func, ast.Attribute) and func.attr == 'generate'):
                    print("PASS: evaluate() calls generate()")
                    break
        else:
            raise AssertionError("evaluate() doesn't call generate()")
        break
else:
    raise AssertionError("evaluate() function not found")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; else echo "FAIL"; fi

########################################
# Final score
########################################
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "/logs/verifier/reward.txt"

python3 -c "
import json
score = float('$SCORE')
json.dump({
    'reward': score,
    'max_score': 1.0,
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
