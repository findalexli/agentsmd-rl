#!/usr/bin/env bash
set +e

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
python3 -c "compile(open('$EVAL_UTILS').read(), '$EVAL_UTILS', 'exec')" 2>/dev/null
EU_OK=$?
python3 -c "compile(open('$VF_UTILS').read(), '$VF_UTILS', 'exec')" 2>/dev/null
VU_OK=$?
if [ $EU_OK -ne 0 ] || [ $VU_OK -ne 0 ]; then
    echo "GATE FAIL: syntax errors"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "PASS: syntax OK"

########################################
# [pr_diff] (0.25): evaluate_env tracks failed rollouts in metrics
# Behavioral mock-based F2P test.
# Justification for mocking: evaluate_env depends on verifiers async
# orchestration + GPU-oriented deps that aren't available in CPU Docker.
# On buggy code: metrics dict has no failure key → FAIL
# On fixed code: metrics dict includes failed_rollouts count → PASS
########################################
echo "=== TEST: failed_rollouts in normal eval metrics ==="
python3 << 'PYEOF'
import sys, types, asyncio
from unittest.mock import MagicMock, AsyncMock

# Mock verifiers and prime_rl dependency tree
vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('Env', (), {})
vf_mock.ClientConfig = type('CC', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock
for m in ['verifiers.serve', 'verifiers.utils', 'verifiers.utils.serve_utils']:
    sys.modules[m] = types.ModuleType(m)
sys.modules['verifiers.serve'].EnvClient = MagicMock
sys.modules['verifiers.serve'].ZMQEnvClient = MagicMock
sys.modules['verifiers.serve'].ZMQEnvServer = MagicMock
sys.modules['verifiers.utils.serve_utils'].get_free_port = lambda: 12345

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

# Mock vf_utils.evaluate to return controlled outputs
vf_utils_mod = types.ModuleType('prime_rl.orchestrator.vf_utils')
mock_evaluate = AsyncMock()
vf_utils_mod.evaluate = mock_evaluate
vf_utils_mod.get_completion_len = lambda x: x.get('_clen', 50)
sys.modules['prime_rl.orchestrator.vf_utils'] = vf_utils_mod

sys.path.insert(0, '/workspace/src')
import importlib
eval_utils = importlib.import_module('prime_rl.orchestrator.eval_utils')

# Scenario: 10 inputs requested, 7 outputs returned (3 failed)
mock_env = MagicMock()
mock_env._get_eval_inputs.return_value = [{'id': i} for i in range(10)]

outputs = [
    {'example_id': i % 5, 'reward': 0.5, 'completion': 'x', 'is_truncated': False,
     'error': None, '_clen': 50,
     'trajectory': [{'tokens': {'prompt_ids': list(range(10)),
                                'completion_ids': list(range(50))}, 'response': {}}]}
    for i in range(7)
]
mock_evaluate.return_value = outputs
mock_monitor.reset_mock()

asyncio.run(eval_utils.evaluate_env(
    env=mock_env, env_name='test_env', model_name='m',
    sampling_args={}, num_examples=5, rollouts_per_example=2,
    max_retries=0, ckpt_step=100, step=50, get_client=AsyncMock(),
))

# Check monitor.log was called with a failure-related metric equal to 3
assert mock_monitor.log.called, "monitor.log was not called"
metrics = mock_monitor.log.call_args_list[0][0][0]
fail_keys = {k: v for k, v in metrics.items() if 'fail' in k.lower()}
assert fail_keys, f"No failure metric found in logged metrics: {list(metrics.keys())}"
assert any(v == 3 for v in fail_keys.values()), \
    f"Expected failure count of 3, got: {fail_keys}"
print("PASS: failed_rollouts=3 logged in normal eval metrics")
PYEOF
if [ $? -eq 0 ]; then add_score 0.25; echo "PASS (+0.25)"; else echo "FAIL"; fi

########################################
# [pr_diff] (0.20): All-fail case still logs failure count to monitor
# Behavioral mock-based F2P test.
# On buggy code: all-fail branch returns without calling monitor.log → FAIL
# On fixed code: monitor.log called with failure count → PASS
########################################
echo "=== TEST: all-fail case logs failure count to monitor ==="
python3 << 'PYEOF'
import sys, types, asyncio
from unittest.mock import MagicMock, AsyncMock

# Fresh mock setup (separate process)
vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('Env', (), {})
vf_mock.ClientConfig = type('CC', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock
for m in ['verifiers.serve', 'verifiers.utils', 'verifiers.utils.serve_utils']:
    sys.modules[m] = types.ModuleType(m)
sys.modules['verifiers.serve'].EnvClient = MagicMock
sys.modules['verifiers.serve'].ZMQEnvClient = MagicMock
sys.modules['verifiers.serve'].ZMQEnvServer = MagicMock
sys.modules['verifiers.utils.serve_utils'].get_free_port = lambda: 12345

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

vf_utils_mod = types.ModuleType('prime_rl.orchestrator.vf_utils')
mock_evaluate = AsyncMock(return_value=[])  # ALL fail
vf_utils_mod.evaluate = mock_evaluate
vf_utils_mod.get_completion_len = lambda x: 0
sys.modules['prime_rl.orchestrator.vf_utils'] = vf_utils_mod

sys.path.insert(0, '/workspace/src')
import importlib
eval_utils = importlib.import_module('prime_rl.orchestrator.eval_utils')

mock_env = MagicMock()
mock_env._get_eval_inputs.return_value = [{'id': i} for i in range(8)]
mock_monitor.reset_mock()

asyncio.run(eval_utils.evaluate_env(
    env=mock_env, env_name='math', model_name='m',
    sampling_args={}, num_examples=4, rollouts_per_example=2,
    max_retries=0, ckpt_step=200, step=100, get_client=AsyncMock(),
))

# Key check: monitor.log MUST be called even when all rollouts failed
assert mock_monitor.log.called, \
    "monitor.log not called in all-fail case (buggy: returns without logging)"
metrics = mock_monitor.log.call_args[0][0]
fail_keys = {k: v for k, v in metrics.items() if 'fail' in k.lower()}
assert fail_keys, f"No failure metric in all-fail metrics: {list(metrics.keys())}"
assert any(v == 8 for v in fail_keys.values()), \
    f"Expected failure count of 8, got: {fail_keys}"
print("PASS: all-fail case logs failure count=8 to monitor")
PYEOF
if [ $? -eq 0 ]; then add_score 0.20; echo "PASS (+0.20)"; else echo "FAIL"; fi

########################################
# [pr_diff] (0.20): generate() logs aggregate failed-groups warning
# Behavioral mock-based F2P test.
# Justification for mocking: generate() calls run_group which needs
# vf.Environment.run_group — full verifiers async infrastructure.
# We mock env.run_group to fail for 2 of 5 groups, then check that
# a summary warning (not just individual "Group failed:" messages) is logged.
# On buggy code: no summary warning → FAIL
# On fixed code: summary warning with count → PASS
########################################
echo "=== TEST: generate() aggregate failed-groups warning ==="
python3 << 'PYEOF'
import sys, types, asyncio
from unittest.mock import MagicMock, AsyncMock

# Mock verifiers
vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('Env', (), {})
vf_mock.ClientConfig = type('CC', (), {})
vf_mock.RolloutOutput = dict
vf_mock.RolloutInput = lambda **kw: kw
sys.modules['verifiers'] = vf_mock
for m in ['verifiers.serve', 'verifiers.utils', 'verifiers.utils.serve_utils']:
    sys.modules[m] = types.ModuleType(m)
sys.modules['verifiers.serve'].EnvClient = MagicMock
sys.modules['verifiers.serve'].ZMQEnvClient = MagicMock
sys.modules['verifiers.serve'].ZMQEnvServer = MagicMock
sys.modules['verifiers.utils.serve_utils'].get_free_port = lambda: 12345

# Mock logger — we inspect warnings on this
mock_logger = MagicMock()
logger_mod = types.ModuleType('prime_rl.utils.logger')
logger_mod.get_logger = lambda: mock_logger
logger_mod.InterceptHandler = MagicMock
logger_mod.ProgressTracker = MagicMock(return_value=MagicMock())
sys.modules['prime_rl.utils.logger'] = logger_mod

for mod_name in ['prime_rl', 'prime_rl.utils', 'prime_rl.orchestrator']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

sys.path.insert(0, '/workspace/src')
import importlib
vf_utils = importlib.import_module('prime_rl.orchestrator.vf_utils')

# Mock env: 3 groups succeed, 2 groups raise (simulating failures)
mock_env = MagicMock()
mock_env.run_group = AsyncMock(side_effect=[
    [{'reward': 0.5, 'example_id': 0}],
    [{'reward': 0.5, 'example_id': 1}],
    [{'reward': 0.5, 'example_id': 2}],
    RuntimeError("simulated failure A"),
    RuntimeError("simulated failure B"),
])

mock_logger.reset_mock()
examples = [{'id': i} for i in range(5)]
result = asyncio.run(vf_utils.generate(
    env=mock_env, model_name='test', examples=examples,
    rollouts_per_example=1, sampling_args={},
    get_client=AsyncMock(return_value=MagicMock()),
))

# Verify 3 successful outputs returned
assert len(result) == 3, f"Expected 3 outputs, got {len(result)}"

# Verify a SUMMARY warning about failed groups exists
# (distinguish from individual "Group failed: <exception>" messages)
summary_warnings = []
for w in mock_logger.warning.call_args_list:
    msg = str(w.args[0]) if w.args else ''
    # Individual failures say "Group failed: <exception msg>"
    if 'Group failed:' not in msg:
        summary_warnings.append(msg)

assert summary_warnings, \
    "No summary warning about failed groups (only individual failure messages found). " + \
    f"All warnings: {[str(w) for w in mock_logger.warning.call_args_list]}"
# Summary must mention the failure count (2)
assert any('2' in w for w in summary_warnings), \
    f"Summary warning doesn't mention failure count (2). Summaries: {summary_warnings}"
print("PASS: generate() logs aggregate warning about 2 failed groups")
PYEOF
if [ $? -eq 0 ]; then add_score 0.20; echo "PASS (+0.20)"; else echo "FAIL"; fi

########################################
# [regression] (0.10): compute_eval_ckpt_step regression
# Behavioral P2P test — pure function, called directly with known I/O pairs.
########################################
echo "=== TEST: compute_eval_ckpt_step regression ==="
python3 << 'PYEOF'
import sys, types
from unittest.mock import MagicMock

# Minimal mocks for import chain
vf_mock = types.ModuleType('verifiers')
vf_mock.Environment = type('E', (), {})
vf_mock.ClientConfig = type('C', (), {})
vf_mock.RolloutOutput = dict
sys.modules['verifiers'] = vf_mock
for m in ['verifiers.serve', 'verifiers.utils', 'verifiers.utils.serve_utils',
          'prime_rl', 'prime_rl.configs', 'prime_rl.configs.orchestrator',
          'prime_rl.utils', 'prime_rl.utils.logger', 'prime_rl.utils.monitor',
          'prime_rl.utils.utils', 'prime_rl.orchestrator',
          'prime_rl.orchestrator.vf_utils']:
    sys.modules[m] = MagicMock()

sys.path.insert(0, '/workspace/src')
import importlib
eu = importlib.import_module('prime_rl.orchestrator.eval_utils')

f = eu.compute_eval_ckpt_step
# Standard interval-aligned triggers
assert f(ckpt_step=25, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
assert f(ckpt_step=26, prev_ckpt_step=24, last_eval_step=0, interval=25) == 25
# Not yet at interval
assert f(ckpt_step=23, prev_ckpt_step=22, last_eval_step=0, interval=25) is None
# Base model eval
assert f(ckpt_step=0, prev_ckpt_step=-1, last_eval_step=-1, interval=25, eval_base_model=True) == 0
# No re-eval of same step
assert f(ckpt_step=25, prev_ckpt_step=25, last_eval_step=0, interval=25) is None
# Jump over multiple intervals
assert f(ckpt_step=76, prev_ckpt_step=24, last_eval_step=0, interval=25) == 75
print("PASS: compute_eval_ckpt_step regression OK")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; echo "PASS (+0.10)"; else echo "FAIL"; fi

########################################
# [pr_diff] (0.05): Anti-stub: evaluate_env is substantive
# Structural check — verifies evaluate_env has real logic, not a stub.
########################################
echo "=== TEST: Anti-stub check ==="
python3 << PYEOF
import ast

source = open("$EVAL_UTILS").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'evaluate_env':
        # Must have more than 5 statements (a stub would have fewer)
        assert len(node.body) > 5, f"evaluate_env has only {len(node.body)} statements — looks like a stub"
        func_src = '\n'.join(source.split('\n')[node.lineno-1:node.end_lineno]).lower()
        assert 'monitor' in func_src or 'log' in func_src, "No monitoring/logging logic"
        assert 'reward' in func_src or 'metric' in func_src, "No metrics logic"
        print("PASS: evaluate_env is substantive")
        break
else:
    raise AssertionError("evaluate_env function not found")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; echo "PASS (+0.05)"; else echo "FAIL"; fi

########################################
# [agent_config] (0.10): No bare except blocks — AGENTS.md:5 @ 18594ab
# Structural check — bare except: is a code smell flagged by AGENTS.md.
# Only flags bare `except:` (no exception type), not justified try/except.
########################################
echo "=== TEST: No bare except blocks ==="
python3 << PYEOF
import ast

for filepath in ["$EVAL_UTILS", "$VF_UTILS"]:
    source = open(filepath).read()
    tree = ast.parse(source)
    fname = filepath.split('/')[-1]

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    raise AssertionError(
                        f"{fname}: bare except at line {node.lineno} — "
                        "must specify exception type (AGENTS.md:5)")

print("PASS: No bare except blocks")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; echo "PASS (+0.10)"; else echo "FAIL"; fi

########################################
# [agent_config] (0.05): No process-explanatory comments — AGENTS.md:7 @ 18594ab
# Structural check — comments describing refactoring history are flagged.
########################################
echo "=== TEST: No process-explanatory comments ==="
python3 << 'PYEOF'
import re

BAD_PATTERNS = [
    r'(?i)#.*used to.*but now',
    r'(?i)#.*old code',
    r'(?i)#.*previously.*now',
    r'(?i)#.*changed from',
    r'(?i)#.*was originally',
    r'(?i)#.*refactored from',
]

for filepath in [
    "/workspace/src/prime_rl/orchestrator/eval_utils.py",
    "/workspace/src/prime_rl/orchestrator/vf_utils.py",
]:
    source = open(filepath).read()
    fname = filepath.split('/')[-1]
    for pattern in BAD_PATTERNS:
        matches = re.findall(pattern, source)
        if matches:
            raise AssertionError(
                f"{fname}: process-explanatory comment: {matches[0]} (AGENTS.md:7)")

print("PASS: No process-explanatory comments")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; echo "PASS (+0.05)"; else echo "FAIL"; fi

########################################
# [regression] (0.05): evaluate() in vf_utils calls generate
# Structural regression check — evaluate() must delegate to generate().
# Justification for AST: evaluate() depends on full verifiers async stack.
########################################
echo "=== TEST: evaluate() delegates to generate() ==="
python3 << PYEOF
import ast

source = open("$VF_UTILS").read()
tree = ast.parse(source)

eval_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'evaluate':
        eval_func = node
        break

assert eval_func, "evaluate() function not found in vf_utils.py"

# Check that evaluate() calls generate() somewhere in its body
func_src = '\n'.join(source.split('\n')[eval_func.lineno-1:eval_func.end_lineno])
found_generate_call = False
for node in ast.walk(eval_func):
    if isinstance(node, ast.Call):
        # Check for generate(...) or await generate(...)
        if isinstance(node.func, ast.Name) and node.func.id == 'generate':
            found_generate_call = True
            break

assert found_generate_call, "evaluate() does not call generate()"
print("PASS: evaluate() delegates to generate()")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; echo "PASS (+0.05)"; else echo "FAIL"; fi

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
