#!/usr/bin/env bash
set -uo pipefail

HANDLER="scripts/ci/utils/slash_command_handler.py"
WORKFLOW=".github/workflows/rerun-ut.yml"
TOTAL=0.0
REWARD=0.0
DETAILS=""

add() {
    local weight=$1 desc="$2" pass=$3
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    if [ "$pass" = "1" ]; then
        REWARD=$(python3 -c "print(round($REWARD + $weight, 4))")
        DETAILS="${DETAILS}  PASS ($weight): $desc\n"
    else
        DETAILS="${DETAILS}  FAIL ($weight): $desc\n"
    fi
}

gate_fail() {
    echo "GATE FAIL: $1"
    echo "0.0" > /logs/verifier/reward.txt
    echo "{\"reward\": 0.0, \"behavioral\": 0.0, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json
    exit 0
}

cd /repo

########################################
# GATE: Syntax checks
########################################

# [pr_diff] (gate): Python file must parse
python3 -c "import ast; ast.parse(open('$HANDLER').read())" 2>/dev/null || gate_fail "slash_command_handler.py has syntax errors"

# [pr_diff] (gate): YAML file must be valid
python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW'))" 2>/dev/null || gate_fail "rerun-ut.yml has YAML syntax errors"

########################################
# BEHAVIORAL: Fail-to-pass tests (0.65)
########################################

# [pr_diff] (0.20): find_workflow_run_url builds unique title when test_command is provided
# We call the title-building logic directly by extracting it from the function
TITLE_TEST=$(python3 -c "
import sys, io, unittest.mock as mock, time

# Mock external deps before importing
sys.modules['github'] = mock.MagicMock()
sys.modules['github.Auth'] = mock.MagicMock()
sys.modules['github.Github'] = mock.MagicMock()

# Mock requests.get to return empty runs (so the function exits after polling)
mock_resp = mock.MagicMock()
mock_resp.status_code = 200
mock_resp.json.return_value = {'workflow_runs': []}

with mock.patch('requests.get', return_value=mock_resp):
    with mock.patch('time.sleep'):
        # Capture printed output to see expected_title
        captured = io.StringIO()
        sys.stdout = captured
        from scripts.ci.utils.slash_command_handler import find_workflow_run_url
        mock_repo = mock.MagicMock()
        mock_repo.full_name = 'test/repo'
        find_workflow_run_url(
            mock_repo, 123, 'main', 'rerun-ut', 'token',
            time.time(), pr_head_sha=None, max_wait=5,
            test_command='test_foo.py'
        )
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        # Title should include test_command
        if 'test_foo.py' in output and '[rerun-ut]' in output:
            print('PASS')
        else:
            print('FAIL:' + output)
" 2>&1)
[ "$TITLE_TEST" = "PASS" ] && T1=1 || T1=0
add 0.20 "find_workflow_run_url includes test_command in expected title" $T1

# [pr_diff] (0.15): Different test_commands produce different expected titles
UNIQUE_TEST=$(python3 -c "
import sys, io, unittest.mock as mock, time

sys.modules['github'] = mock.MagicMock()
sys.modules['github.Auth'] = mock.MagicMock()
sys.modules['github.Github'] = mock.MagicMock()

mock_resp = mock.MagicMock()
mock_resp.status_code = 200
mock_resp.json.return_value = {'workflow_runs': []}

titles = []
with mock.patch('requests.get', return_value=mock_resp):
    with mock.patch('time.sleep'):
        from scripts.ci.utils.slash_command_handler import find_workflow_run_url
        for cmd in ['test_foo.py', 'test_bar.py']:
            captured = io.StringIO()
            sys.stdout = captured
            mock_repo = mock.MagicMock()
            mock_repo.full_name = 'test/repo'
            find_workflow_run_url(
                mock_repo, 123, 'main', 'rerun-ut', 'token',
                time.time(), pr_head_sha=None, max_wait=5,
                test_command=cmd
            )
            sys.stdout = sys.__stdout__
            titles.append(captured.getvalue())

if titles[0] != titles[1]:
    print('PASS')
else:
    print('FAIL')
" 2>&1)
[ "$UNIQUE_TEST" = "PASS" ] && T2=1 || T2=0
add 0.15 "Different test_commands produce different expected titles" $T2

# [pr_diff] (0.10): find_workflow_run_url with test_command + pr_head_sha builds correct title
SHA_TEST=$(python3 -c "
import sys, io, unittest.mock as mock, time

sys.modules['github'] = mock.MagicMock()
sys.modules['github.Auth'] = mock.MagicMock()
sys.modules['github.Github'] = mock.MagicMock()

mock_resp = mock.MagicMock()
mock_resp.status_code = 200
mock_resp.json.return_value = {'workflow_runs': []}

with mock.patch('requests.get', return_value=mock_resp):
    with mock.patch('time.sleep'):
        captured = io.StringIO()
        sys.stdout = captured
        from scripts.ci.utils.slash_command_handler import find_workflow_run_url
        mock_repo = mock.MagicMock()
        mock_repo.full_name = 'test/repo'
        find_workflow_run_url(
            mock_repo, 123, 'main', 'rerun-ut', 'token',
            time.time(), pr_head_sha='abc123', max_wait=5,
            test_command='test_foo.py'
        )
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        # Should contain both test_command and sha
        if 'test_foo.py' in output and 'abc123' in output and '[rerun-ut]' in output:
            print('PASS')
        else:
            print('FAIL:' + output)
" 2>&1)
[ "$SHA_TEST" = "PASS" ] && T3=1 || T3=0
add 0.10 "Title includes both test_command and pr_head_sha for fork PRs" $T3

# [pr_diff] (0.10): handle_rerun_ut passes test_command to find_workflow_run_url
# Check by inspecting the call site in the source (the function calls find_workflow_run_url with test_command kwarg)
PASS_TC=$(python3 -c "
import ast
with open('$HANDLER') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'handle_rerun_ut':
        src = ast.dump(node)
        # Look for test_command keyword in a call to find_workflow_run_url
        for call in ast.walk(node):
            if isinstance(call, ast.Call):
                func_name = ''
                if isinstance(call.func, ast.Name):
                    func_name = call.func.id
                elif isinstance(call.func, ast.Attribute):
                    func_name = call.func.attr
                if func_name == 'find_workflow_run_url':
                    kw_names = [kw.arg for kw in call.keywords]
                    if 'test_command' in kw_names:
                        print('PASS')
                        exit()
print('FAIL')
" 2>&1)
# Justify AST: handle_rerun_ut requires GitHub API objects (gh_repo, pr, comment) that can't be
# easily constructed for a unit test. Checking the call signature is the most reliable approach.
[ "$PASS_TC" = "PASS" ] && T4=1 || T4=0
add 0.10 "handle_rerun_ut passes test_command to find_workflow_run_url" $T4

# [pr_diff] (0.10): rerun-ut.yml run-name includes test_command input reference
YAML_TEST=$(python3 -c "
import yaml
with open('$WORKFLOW') as f:
    data = yaml.safe_load(f)
run_name = data.get('run-name', '')
if 'test_command' in run_name:
    print('PASS')
else:
    print('FAIL')
" 2>&1)
[ "$YAML_TEST" = "PASS" ] && T5=1 || T5=0
add 0.10 "rerun-ut.yml run-name includes test_command" $T5

########################################
# REGRESSION: Pass-to-pass (0.15)
########################################

# [pr_diff] (0.10): find_workflow_run_url without test_command still works (backward compat)
COMPAT_TEST=$(python3 -c "
import sys, io, unittest.mock as mock, time

sys.modules['github'] = mock.MagicMock()
sys.modules['github.Auth'] = mock.MagicMock()
sys.modules['github.Github'] = mock.MagicMock()

mock_resp = mock.MagicMock()
mock_resp.status_code = 200
mock_resp.json.return_value = {'workflow_runs': []}

with mock.patch('requests.get', return_value=mock_resp):
    with mock.patch('time.sleep'):
        captured = io.StringIO()
        sys.stdout = captured
        from scripts.ci.utils.slash_command_handler import find_workflow_run_url
        mock_repo = mock.MagicMock()
        mock_repo.full_name = 'test/repo'
        # Call without test_command — should still work
        find_workflow_run_url(
            mock_repo, 123, 'main', 'stage-b', 'token',
            time.time(), pr_head_sha='sha456', max_wait=5
        )
        sys.stdout = sys.__stdout__
        output = captured.getvalue()
        # Should produce '[stage-b] sha456' (no test_command suffix)
        if '[stage-b] sha456' in output:
            print('PASS')
        else:
            print('FAIL:' + output)
" 2>&1)
[ "$COMPAT_TEST" = "PASS" ] && T6=1 || T6=0
add 0.10 "find_workflow_run_url backward compat without test_command" $T6

# [pr_diff] (0.05): find_workflow_run_url function signature accepts test_command parameter
SIG_TEST=$(python3 -c "
import inspect, sys, unittest.mock as mock
sys.modules['github'] = mock.MagicMock()
sys.modules['github.Auth'] = mock.MagicMock()
sys.modules['github.Github'] = mock.MagicMock()
from scripts.ci.utils.slash_command_handler import find_workflow_run_url
sig = inspect.signature(find_workflow_run_url)
if 'test_command' in sig.parameters:
    print('PASS')
else:
    print('FAIL')
" 2>&1)
[ "$SIG_TEST" = "PASS" ] && T7=1 || T7=0
add 0.05 "find_workflow_run_url accepts test_command parameter" $T7

########################################
# STRUCTURAL: Anti-stub + comment consolidation (0.15)
########################################

# [pr_diff] (0.10): handle_rerun_ut consolidates trigger+URL into single comment
# In buggy code, there are separate create_issue_comment calls for trigger and URL.
# In fixed code, the success path should NOT have a standalone trigger comment before find_workflow_run_url.
CONSOL_TEST=$(python3 -c "
import ast

with open('$HANDLER') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'handle_rerun_ut':
        # Find the 'if success:' block
        src = open('$HANDLER').read()
        lines = src.split('\n')
        # Count create_issue_comment calls that contain 'Triggered' AND appear before find_workflow_run_url
        in_success = False
        found_pre_trigger = False
        found_find_url = False
        for i, line in enumerate(lines):
            if 'handle_rerun_ut' in line and 'def ' in line:
                in_success = False
            if in_success and 'find_workflow_run_url' in line:
                found_find_url = True
                break
            if in_success and 'create_issue_comment' in line and 'Triggered' in line and not found_find_url:
                found_pre_trigger = True
            if 'if success:' in line:
                in_success = True

        # In fixed code, there should be NO standalone trigger comment before find_workflow_run_url
        if not found_pre_trigger:
            print('PASS')
        else:
            print('FAIL')
        break
" 2>&1)
# Justify AST: This checks comment ordering/consolidation which is a structural property of the
# handler flow, not something callable.
[ "$CONSOL_TEST" = "PASS" ] && T8=1 || T8=0
add 0.10 "handle_rerun_ut consolidates trigger+URL into single comment" $T8

# [pr_diff] (0.05): handle_rerun_stage consolidates comments (no separate URL comment)
STAGE_CONSOL=$(python3 -c "
src = open('$HANDLER').read()
# In buggy code, handle_rerun_stage has a separate '🔗 [View workflow run]' comment
# In fixed code, the URL is embedded in the trigger comment
import re
# Find the handle_rerun_stage function body
match = re.search(r'def handle_rerun_stage\b.*?(?=\ndef \w|\Z)', src, re.DOTALL)
if match:
    body = match.group(0)
    # Check there's no standalone link comment line
    if '🔗' not in body:
        print('PASS')
    else:
        print('FAIL')
else:
    print('FAIL')
" 2>&1)
[ "$STAGE_CONSOL" = "PASS" ] && T9=1 || T9=0
add 0.05 "handle_rerun_stage consolidates comments (no separate link comment)" $T9

########################################
# CONFIG-DERIVED (0.05)
########################################

# [agent_config] (0.05): Slash command handler is documented as CI key file — .claude/skills/ci-workflow-guide/SKILL.md:31
# The CI workflow guide lists slash_command_handler.py as a key file for slash commands.
# Verify the handler file still exists and is importable (no broken refactors).
CONFIG_TEST=$(python3 -c "
import sys, unittest.mock as mock
sys.modules['github'] = mock.MagicMock()
sys.modules['github.Auth'] = mock.MagicMock()
sys.modules['github.Github'] = mock.MagicMock()
try:
    import scripts.ci.utils.slash_command_handler as m
    assert hasattr(m, 'find_workflow_run_url')
    assert hasattr(m, 'handle_rerun_ut')
    assert hasattr(m, 'handle_rerun_stage')
    print('PASS')
except Exception as e:
    print('FAIL:' + str(e))
" 2>&1)
[ "$CONFIG_TEST" = "PASS" ] && T10=1 || T10=0
add 0.05 "Handler exports find_workflow_run_url, handle_rerun_ut, handle_rerun_stage" $T10

########################################
# Summary
########################################

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Total weight: $TOTAL"
echo "Reward: $REWARD"

BEHAVIORAL=$(python3 -c "
b = 0.0
b += $T1 * 0.20  # title includes test_command
b += $T2 * 0.15  # unique titles
b += $T3 * 0.10  # title with sha
b += $T4 * 0.10  # handle_rerun_ut passes test_command
b += $T5 * 0.10  # YAML run-name
print(round(b, 4))
")

REGRESSION=$(python3 -c "
r = 0.0
r += $T6 * 0.10  # backward compat
r += $T7 * 0.05  # signature
print(round(r, 4))
")

STRUCTURAL=$(python3 -c "
s = 0.0
s += $T8 * 0.10  # rerun-ut consolidation
s += $T9 * 0.05  # rerun-stage consolidation
print(round(s, 4))
")

CONFIG=$(python3 -c "print(round($T10 * 0.05, 4))")

echo "$REWARD" > /logs/verifier/reward.txt
python3 -c "
import json
json.dump({
    'reward': $REWARD,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'config': $CONFIG,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
