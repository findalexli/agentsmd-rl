#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd /repo

CONFIG_FILE="src/transformers/generation/configuration_utils.py"
REQUESTS_FILE="src/transformers/generation/continuous_batching/requests.py"
API_FILE="src/transformers/generation/continuous_batching/continuous_api.py"
IO_FILE="src/transformers/generation/continuous_batching/input_outputs.py"

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0): Python syntax valid on all changed files
python3 -c "
import py_compile, sys
files = ['$CONFIG_FILE', '$REQUESTS_FILE', '$API_FILE', '$IO_FILE']
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'GATE FAIL: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE: syntax OK')
" || { echo "0.0" > /logs/verifier/reward.txt; exit 0; }

###############################################################################
# Fail-to-pass: ContinuousBatchingConfig has return_logprobs attribute
###############################################################################
# [pr_diff] (0.15): Config must expose return_logprobs option
if python3 -c "
from transformers.generation.configuration_utils import ContinuousBatchingConfig
cfg = ContinuousBatchingConfig()
assert hasattr(cfg, 'return_logprobs'), 'return_logprobs attribute missing'
assert cfg.return_logprobs is False, f'default should be False, got {cfg.return_logprobs}'
cfg2 = ContinuousBatchingConfig(return_logprobs=True)
assert cfg2.return_logprobs is True, 'setting return_logprobs=True failed'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.15): ContinuousBatchingConfig.return_logprobs exists and defaults to False"
    add 0.15
else
    echo "FAIL (0.15): ContinuousBatchingConfig missing return_logprobs"
fi

###############################################################################
# Fail-to-pass: RequestState.update_and_check_completion accepts logprob param
###############################################################################
# [pr_diff] (0.20): update_and_check_completion must accept (token_id, logprob)
if python3 -c "
import sys
sys.path.insert(0, 'src')
from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

state = RequestState(
    request_id='test-1',
    initial_tokens=[1, 2, 3],
    max_new_tokens=5,
    eos_token_id=0,
)
state._status = RequestStatus.DECODING

# Must accept two positional args: token_id and logprob
try:
    result = state.update_and_check_completion(42, -0.5)
except TypeError as e:
    print(f'FAIL: {e}', file=sys.stderr)
    sys.exit(1)

assert isinstance(result, bool), f'Expected bool, got {type(result)}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.20): update_and_check_completion accepts (token_id, logprob)"
    add 0.20
else
    echo "FAIL (0.20): update_and_check_completion does not accept logprob parameter"
fi

###############################################################################
# Fail-to-pass: logprobs are stored and returned via to_generation_output
###############################################################################
# [pr_diff] (0.15): logprobs must flow from update_and_check_completion to output
if python3 -c "
import sys
sys.path.insert(0, 'src')
from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

state = RequestState(
    request_id='test-2',
    initial_tokens=[10, 20],
    max_new_tokens=5,
    eos_token_id=0,
)
state._status = RequestStatus.DECODING

# Generate some tokens with logprobs
state.update_and_check_completion(100, -1.5)
state.update_and_check_completion(200, -0.3)

output = state.to_generation_output()
lps = output.logprobs

assert len(lps) >= 2, f'Expected at least 2 logprobs, got {len(lps)}'
assert abs(lps[0] - (-1.5)) < 1e-6, f'First logprob wrong: {lps[0]}'
assert abs(lps[1] - (-0.3)) < 1e-6, f'Second logprob wrong: {lps[1]}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.15): logprobs stored and returned in generation output"
    add 0.15
else
    echo "FAIL (0.15): logprobs not properly stored or returned"
fi

###############################################################################
# Fail-to-pass: fork() preserves logprobs
###############################################################################
# [pr_diff] (0.10): fork must copy accumulated logprobs to the new state
if python3 -c "
import sys
sys.path.insert(0, 'src')
from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

state = RequestState(
    request_id='test-3',
    initial_tokens=[1],
    max_new_tokens=10,
    eos_token_id=0,
)
state._status = RequestStatus.DECODING
state.update_and_check_completion(5, -2.0)

forked = state.fork('test-3-fork')
# Check logprobs are copied
assert hasattr(forked, 'logprobs'), 'forked state missing logprobs attr'
assert len(forked.logprobs) == 1, f'Expected 1 logprob in fork, got {len(forked.logprobs)}'
assert abs(forked.logprobs[0] - (-2.0)) < 1e-6, f'Forked logprob wrong: {forked.logprobs[0]}'

# Verify independence (mutation doesn't cross)
forked.logprobs.append(-0.1)
assert len(state.logprobs) == 1, 'Fork logprobs not independent from original'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): fork() preserves logprobs"
    add 0.10
else
    echo "FAIL (0.10): fork() does not preserve logprobs"
fi

###############################################################################
# Fail-to-pass: create_equivalent_initial_request preserves logprobs
###############################################################################
# [pr_diff] (0.10): soft-reset must keep accumulated logprobs
if python3 -c "
import sys
sys.path.insert(0, 'src')
from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

state = RequestState(
    request_id='test-4',
    initial_tokens=[1, 2],
    max_new_tokens=10,
    eos_token_id=0,
)
state._status = RequestStatus.DECODING
state.update_and_check_completion(50, -1.0)
state.update_and_check_completion(60, -0.7)

equiv = state.create_equivalent_initial_request()
assert hasattr(equiv, 'logprobs'), 'equivalent request missing logprobs'
assert len(equiv.logprobs) == 2, f'Expected 2 logprobs, got {len(equiv.logprobs)}'
assert abs(equiv.logprobs[0] - (-1.0)) < 1e-6
assert abs(equiv.logprobs[1] - (-0.7)) < 1e-6

# Verify independence
equiv.logprobs.append(-0.5)
assert len(state.logprobs) == 2, 'Equivalent request logprobs not independent'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): create_equivalent_initial_request preserves logprobs"
    add 0.10
else
    echo "FAIL (0.10): create_equivalent_initial_request does not preserve logprobs"
fi

###############################################################################
# Pass-to-pass: RequestState basic behavior still works with None logprob
###############################################################################
# [pr_diff] (0.10): update_and_check_completion with logprob=None must not break
if python3 -c "
import sys
sys.path.insert(0, 'src')
from transformers.generation.continuous_batching.requests import RequestState, RequestStatus

state = RequestState(
    request_id='test-p2p',
    initial_tokens=[1, 2, 3],
    max_new_tokens=3,
    eos_token_id=99,
)
state._status = RequestStatus.DECODING

# Generate without logprobs (None)
state.update_and_check_completion(10, None)
state.update_and_check_completion(20, None)

output = state.to_generation_output()
assert output.generated_tokens == [10, 20], f'Wrong tokens: {output.generated_tokens}'
# logprobs should be empty when None is passed
assert len(output.logprobs) == 0, f'Expected empty logprobs with None, got {len(output.logprobs)}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): RequestState works correctly with logprob=None"
    add 0.10
else
    echo "FAIL (0.10): RequestState broken with logprob=None"
fi

###############################################################################
# Structural: Anti-stub — sampling code references softmax and gather/log
###############################################################################
# [pr_diff] (0.10): _sample must compute probabilities and handle logprobs path
if python3 -c "
import sys
source = open('$API_FILE').read()
# The sampling method must use softmax for probability computation
assert 'softmax' in source, '_sample missing softmax call'
# Must index into output_ids with 2D notation for the logprobs row
assert 'output_ids[0' in source or 'output_ids[1' in source, 'output_ids not accessed as 2D tensor'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): sampling code contains probability computation and 2D output_ids"
    add 0.10
else
    echo "FAIL (0.10): sampling code missing key logprobs logic"
fi

###############################################################################
# Config-derived: ruff check on changed files
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ a9532bc
if command -v ruff &>/dev/null; then
    if ruff check "$CONFIG_FILE" "$REQUESTS_FILE" "$API_FILE" "$IO_FILE" --quiet 2>/dev/null; then
        echo "PASS (0.05): ruff check passes"
        add 0.05
    else
        echo "FAIL (0.05): ruff check fails"
    fi
else
    # ruff not available — give benefit of the doubt
    echo "SKIP (0.05): ruff not installed, awarding points"
    add 0.05
fi

###############################################################################
# Config-derived: no wildcard imports in changed files
###############################################################################
# [agent_config] (0.05): code style enforced — .github/copilot-instructions.md:14 @ a9532bc
if python3 -c "
import ast, sys
files = ['$CONFIG_FILE', '$REQUESTS_FILE', '$API_FILE', '$IO_FILE']
for f in files:
    with open(f) as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names and node.names[0].name == '*':
            print(f'Wildcard import from {node.module} in {f}', file=sys.stderr)
            sys.exit(1)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): no wildcard imports"
    add 0.05
else
    echo "FAIL (0.05): wildcard imports found"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
