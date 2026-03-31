#!/usr/bin/env bash
set -uo pipefail

SCORE=0
REPO="/workspace/slime"

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): All modified files must be valid Python
for f in slime/rollout/rm_hub/gpqa.py slime/router/router.py slime/ray/rollout.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        echo "FAIL: Syntax error in $f"
        echo "0.0" > /logs/verifier/reward.txt
        exit 0
    fi
done
echo "PASS: Syntax OK"

echo ""
echo "=== Behavioral: GPQA letter range (fail-to-pass) ==="

# [pr_diff] (0.20): Integer label 8 (letter I) must score correctly
python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.rollout.rm_hub.gpqa import compute_gpqa_reward

# Label 8 = 9th option = letter 'I' (zero-indexed)
# With only 8 valid letters (A-H), index 8 is out of bounds and returns 0.0
reward = compute_gpqa_reward('The answer is I', 8)
assert reward == 1.0, f'Expected 1.0 for label=8 (letter I), got {reward}'
print('PASS: Label 8 (letter I) scored correctly')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

# [pr_diff] (0.15): Integer label 9 (letter J) must score correctly
python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.rollout.rm_hub.gpqa import compute_gpqa_reward

reward = compute_gpqa_reward('The answer is J', 9)
assert reward == 1.0, f'Expected 1.0 for label=9 (letter J), got {reward}'
print('PASS: Label 9 (letter J) scored correctly')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

echo ""
echo "=== Behavioral: GPQA pass-to-pass (A-H still work) ==="

# [pr_diff] (0.10): Existing A-H labels must still return correct rewards
python3 -c "
import sys
sys.path.insert(0, '$REPO')
from slime.rollout.rm_hub.gpqa import compute_gpqa_reward

# Integer labels 0-7 (A-H) should still work
for idx, letter in enumerate('ABCDEFGH'):
    reward = compute_gpqa_reward(f'The answer is {letter}', idx)
    assert reward == 1.0, f'Expected 1.0 for label={idx} (letter {letter}), got {reward}'

# Wrong answer should score 0
reward = compute_gpqa_reward('The answer is A', 1)
assert reward == 0.0, f'Expected 0.0 for wrong answer, got {reward}'
print('PASS: A-H labels still work correctly')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Behavioral: WorkerType PLACEHOLDER enum (fail-to-pass) ==="

# [pr_diff] (0.15): WorkerType enum must include PLACEHOLDER
# Cannot import router.py directly (needs httpx/uvicorn/fastapi), so extract
# the Enum class and exec it. This is behavioral — the enum is instantiated.
python3 -c "
import ast, enum, re

source = open('$REPO/slime/router/router.py').read()
tree = ast.parse(source)

# Find WorkerType class definition
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'WorkerType':
        # Extract source lines for this class
        start = node.lineno - 1
        end = node.end_lineno
        lines = source.splitlines()[start:end]
        cls_source = '\n'.join(lines)
        # Exec with required imports
        ns = {'Enum': enum.Enum, 'str': str}
        exec(cls_source, ns)
        WorkerType = ns['WorkerType']
        assert 'PLACEHOLDER' in WorkerType.__members__, \
            f'WorkerType missing PLACEHOLDER, has: {list(WorkerType.__members__)}'
        assert WorkerType.PLACEHOLDER.value == 'placeholder', \
            f'PLACEHOLDER value should be \"placeholder\", got {WorkerType.PLACEHOLDER.value}'
        print('PASS: WorkerType.PLACEHOLDER exists with correct value')
        exit(0)
print('FAIL: WorkerType class not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

echo ""
echo "=== Behavioral: nodes_per_engine filters placeholder groups (fail-to-pass) ==="

# [pr_diff] (0.20): nodes_per_engine must ignore placeholder groups
# Cannot import rollout.py (needs ray/torch), so extract the property logic
# and test it with mock objects. This is behavioral — the property is called.
python3 -c "
import ast

source = open('$REPO/slime/ray/rollout.py').read()
tree = ast.parse(source)

# Find the RolloutServer class (has the nodes_per_engine property that
# iterates over self.server_groups)
prop_source = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for item in node.body:
            if (isinstance(item, ast.FunctionDef)
                and item.name == 'nodes_per_engine'
                and any(isinstance(d, ast.Name) and d.id == 'property'
                        for d in item.decorator_list)):
                # Check if it iterates self.server_groups (RolloutServer, not ServerGroup)
                src = ast.get_source_segment(source, item)
                if src and 'self.server_groups' in src:
                    prop_source = src
                    break
    if prop_source:
        break

assert prop_source is not None, 'Could not find RolloutServer.nodes_per_engine property'

# Build a test harness: create mock groups and a mock self
class FakeGroup:
    def __init__(self, npe, wtype):
        self.nodes_per_engine = npe
        self.worker_type = wtype

class FakeSelf:
    def __init__(self, groups):
        self.server_groups = groups

# Scenario: regular group (npe=1) + placeholder group (npe=4)
# Buggy code includes placeholder → {1, 4} → ValueError
# Fixed code excludes placeholder → {1} → returns 1
self_obj = FakeSelf([FakeGroup(1, 'regular'), FakeGroup(4, 'placeholder')])

# Extract the function body and call it
import textwrap, types

# Dedent and fix indentation for standalone execution
func_lines = prop_source.splitlines()
# Remove @property decorator if present
body_lines = [l for l in func_lines if not l.strip().startswith('@')]
func_code = textwrap.dedent('\n'.join(body_lines))

# Compile the method and bind it
exec_ns = {}
exec(func_code, exec_ns)
method = exec_ns['nodes_per_engine']

result = method(self_obj)
assert result == 1, f'Expected nodes_per_engine=1 (ignoring placeholder), got {result}'
print('PASS: nodes_per_engine correctly ignores placeholder groups')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

echo ""
echo "=== Structural: _get_metrics_router_addr method exists ==="

# [pr_diff] (0.05): RolloutManager must have _get_metrics_router_addr method
# Justified: cannot import rollout.py due to ray/torch dependencies
python3 -c "
import ast

source = open('$REPO/slime/ray/rollout.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'RolloutManager':
        methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        assert '_get_metrics_router_addr' in methods, \
            f'RolloutManager missing _get_metrics_router_addr, has: {methods}'
        print('PASS: _get_metrics_router_addr method exists in RolloutManager')
        exit(0)
print('FAIL: RolloutManager class not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

echo ""
echo "=== Structural: init_tracking called after server launch ==="

# [pr_diff] (0.10): init_tracking must not be called before servers are set up
# Justified: cannot import rollout.py due to ray/torch dependencies
python3 -c "
import ast

source = open('$REPO/slime/ray/rollout.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'RolloutManager':
        init_method = None
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_method = item
                break
        assert init_method is not None, 'RolloutManager.__init__ not found'

        # Walk the __init__ body in order, track positions of key calls
        init_tracking_line = None
        server_setup_line = None

        for child in ast.walk(init_method):
            if isinstance(child, ast.Call):
                func = child.func
                # Check for init_tracking call
                if isinstance(func, ast.Name) and func.id == 'init_tracking':
                    init_tracking_line = child.lineno
                # Check for start_rollout_servers call
                if isinstance(func, ast.Name) and func.id == 'start_rollout_servers':
                    server_setup_line = child.lineno
                # Check for init_http_client call (also before servers in original)
                if isinstance(func, ast.Name) and func.id == 'init_http_client':
                    if server_setup_line is None:
                        server_setup_line = child.lineno

        assert init_tracking_line is not None, 'init_tracking call not found in __init__'
        assert server_setup_line is not None, 'start_rollout_servers call not found in __init__'
        assert init_tracking_line > server_setup_line, \
            f'init_tracking (line {init_tracking_line}) must be after start_rollout_servers (line {server_setup_line})'
        print('PASS: init_tracking called after server launch')
        exit(0)
print('FAIL: RolloutManager not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Structural: Anti-stub check ==="

# [pr_diff] (0.05): _get_metrics_router_addr must not be a trivial stub
python3 -c "
import ast

source = open('$REPO/slime/ray/rollout.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'RolloutManager':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_get_metrics_router_addr':
                # Must have more than just 'return None' or 'pass'
                stmts = [n for n in ast.walk(item) if isinstance(n, ast.stmt) and not isinstance(n, ast.FunctionDef)]
                assert len(stmts) >= 4, \
                    f'_get_metrics_router_addr looks like a stub ({len(stmts)} statements)'
                print(f'PASS: _get_metrics_router_addr has {len(stmts)} statements (not a stub)')
                exit(0)
print('FAIL: method not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

echo ""
echo "==================================="
echo "Total: $SCORE / 1.00"
echo "==================================="

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = float('$SCORE')
behavioral = min(score, 0.80)
regression = min(max(score - 0.80, 0), 0.05)
structural = min(max(score - 0.85, 0), 0.15)
json.dump({
    'reward': score,
    'behavioral': behavioral,
    'regression': regression,
    'structural': structural,
    'config': 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
