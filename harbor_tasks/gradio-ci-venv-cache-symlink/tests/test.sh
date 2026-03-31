#!/usr/bin/env bash
set +e

TOTAL=0
PASS=0

add()   { TOTAL=$(python3 -c "print($TOTAL + $1)"); }
award() { PASS=$(python3 -c "print($PASS  + $1)"); }

cd /workspace/gradio

ACTION_FILE=".github/actions/install-all-deps/action.yml"
TEST_FILE="js/textbox/Textbox.test.ts"

########################################
# GATE: YAML syntax — abort on failure
########################################
# [pr_diff] (0.00): action.yml must be valid YAML
python3 -c "
import yaml, sys
try:
    yaml.safe_load(open('$ACTION_FILE'))
    print('GATE PASS: valid YAML')
except Exception as e:
    print(f'GATE FAILED: {e}')
    sys.exit(1)
" 2>&1
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# Fail-to-pass: Behavioral tests (0.65)
########################################

# [pr_diff] (0.25): Create-env step must execute AFTER cache-restore step
# WHY structural: GitHub Actions composite actions cannot be executed locally.
# BEHAVIORAL INTENT: If venv is created before cache restore, the cache overwrites
# the freshly created venv with stale symlinks.
add 0.25
python3 -c "
import yaml, sys

data = yaml.safe_load(open('$ACTION_FILE'))
steps = data.get('runs', {}).get('steps', [])

# Locate 'Create env' (or any step running 'uv venv') and cache-restore steps
create_env_idx = None
cache_idx = None
for i, step in enumerate(steps):
    name = str(step.get('name', ''))
    run_cmd = str(step.get('run', ''))
    uses = str(step.get('uses', ''))

    if create_env_idx is None and ('uv venv' in run_cmd):
        create_env_idx = i
    if cache_idx is None and 'actions/cache' in uses:
        cache_idx = i

if create_env_idx is None:
    print('FAIL: no step with \"uv venv\" found')
    sys.exit(1)
if cache_idx is None:
    print('FAIL: no actions/cache step found')
    sys.exit(1)
if create_env_idx < cache_idx:
    print(f'FAIL: venv creation (step {create_env_idx}) runs BEFORE cache restore (step {cache_idx})')
    sys.exit(1)

print(f'PASS: venv creation (step {create_env_idx}) runs AFTER cache restore (step {cache_idx})')
" 2>&1
[ $? -eq 0 ] && award 0.25

# [pr_diff] (0.20): Cache key must include the EXACT installed python version
# (not just the requested minor version from inputs.python_version).
# Accepts: steps.<id>.outputs.python-version, env.pythonLocation, any step
# output with "version", or hashFiles referencing a python-version file.
# Rejects: literal text without GHA expression syntax, bare inputs.python_version only.
add 0.20
python3 << 'PYEOF'
import sys, re

raw = open(".github/actions/install-all-deps/action.yml").read()

# Extract the raw key: line from the cache block
in_cache = False
key_line = ""
for line in raw.splitlines():
    s = line.strip()
    if "actions/cache" in s:
        in_cache = True
    if in_cache and s.startswith("key:"):
        key_line = s
        break

if not key_line:
    print("FAIL: no cache key found")
    sys.exit(1)

# Accept any of these patterns that embed exact python version info:
patterns = [
    r'steps\.\w[\w-]*\.outputs\.python-version',     # setup-python output
    r'steps\.\w[\w-]*\.outputs\.\w*version',          # any step version output
    r'env\.pythonLocation',                            # built-in env var
    r'hashFiles.*\.python-version',                    # .python-version file hash
]

for pat in patterns:
    if re.search(pat, key_line, re.IGNORECASE):
        print("PASS: cache key includes exact python version reference")
        sys.exit(0)

print(f"FAIL: cache key has no exact-version reference")
print(f"  key: {key_line[:200]}")
sys.exit(1)
PYEOF
CHECK2=$?
[ $CHECK2 -eq 0 ] && award 0.20

# [pr_diff] (0.10): If cache key references steps.<id>.outputs.*, that step id must exist.
# Only checked when check 2 passed (there IS a version reference to validate).
add 0.10
if [ $CHECK2 -ne 0 ]; then
    echo "SKIP: check 3 depends on check 2 (exact version ref)"
else
python3 << 'PYEOF'
import yaml, sys, re

data = yaml.safe_load(open(".github/actions/install-all-deps/action.yml"))
steps = data.get("runs", {}).get("steps", [])
raw = open(".github/actions/install-all-deps/action.yml").read()

# Find step output references anywhere in the file
step_refs = set(re.findall(r'steps\.(\w[\w-]*)\.outputs', raw))

if not step_refs:
    # No step output refs — env-var or hashFiles approach, no id needed
    print("PASS: no step output references (env-var or hashFiles approach)")
    sys.exit(0)

# Verify each referenced step id exists
step_ids = {str(s.get("id", "")) for s in steps if s.get("id")}
missing = [ref for ref in step_refs if ref not in step_ids]

if missing:
    print(f"FAIL: references step(s) {missing} but no step has that id")
    sys.exit(1)

print(f"PASS: all referenced step ids {sorted(step_refs)} exist")
PYEOF
[ $? -eq 0 ] && award 0.10
fi

# [pr_diff] (0.10): await tick() must be active (not commented) in the textbox copy test
# WHY structural: vitest + Svelte requires full pnpm frontend build chain unavailable in container
add 0.10
python3 -c "
import sys

content = open('$TEST_FILE').read()
lines = content.split('\n')

in_copy_test = False
for i, line in enumerate(lines):
    if 'copy: emitted when copy button is clicked' in line:
        in_copy_test = True
    elif in_copy_test:
        stripped = line.strip()
        if 'await tick()' in stripped:
            if stripped.startswith('//'):
                print(f'FAIL: await tick() is commented out on line {i+1}')
                sys.exit(1)
            else:
                print(f'PASS: await tick() is active on line {i+1}')
                sys.exit(0)
        if stripped.startswith('test(') or stripped == '});':
            break

print('FAIL: await tick() not found in copy test')
sys.exit(1)
" 2>&1
[ $? -eq 0 ] && award 0.10

########################################
# Pass-to-pass: Regression (0.15)
########################################

# [repo_tests] (0.10): Core CI action steps still present and functional
add 0.10
python3 -c "
import yaml, sys

data = yaml.safe_load(open('$ACTION_FILE'))
steps = data.get('runs', {}).get('steps', [])
step_names = [str(s.get('name', '')) for s in steps]
step_uses  = [str(s.get('uses', '')) for s in steps]
all_runs   = ' '.join(str(s.get('run', '')) for s in steps)

required_names = ['Install Python', 'Install ffmpeg']
for req in required_names:
    if not any(req in name for name in step_names):
        print(f'FAIL: required step \"{req}\" missing')
        sys.exit(1)

all_uses = ' '.join(step_uses)
for action in ['actions/cache', 'setup-python']:
    if action not in all_uses:
        print(f'FAIL: {action} no longer used')
        sys.exit(1)

if 'uv venv' not in all_runs:
    print('FAIL: uv venv creation step missing')
    sys.exit(1)

print('PASS: all core CI steps present')
" 2>&1
[ $? -eq 0 ] && award 0.10

# [repo_tests] (0.05): Textbox copy test case still exists
add 0.05
python3 -c "
import sys
content = open('$TEST_FILE').read()
if 'copy: emitted when copy button is clicked' not in content:
    print('FAIL: copy test case was removed')
    sys.exit(1)
if 'toHaveBeenCalledTimes(1)' not in content:
    print('FAIL: copy assertion was removed')
    sys.exit(1)
print('PASS: copy test case intact')
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Config-derived (0.10)
########################################

# [agent_config] (0.05): "Be consistent with the style of the surrounding code." — AGENTS.md:40
add 0.05
python3 -c "
import yaml, sys

data = yaml.safe_load(open('$ACTION_FILE'))
steps = data.get('runs', {}).get('steps', [])

for step in steps:
    if 'run' in step:
        shell = step.get('shell', '')
        if shell and shell != 'bash':
            if 'windows' not in str(step.get('if', '')).lower():
                print(f'FAIL: step \"{step.get(\"name\", \"\")}\" uses shell={shell} instead of bash')
                sys.exit(1)

print('PASS: shell usage consistent')
" 2>&1
[ $? -eq 0 ] && award 0.05

# [agent_config] (0.05): "Frontend code is formatted with prettier" — AGENTS.md:39
add 0.05
python3 -c "
import sys
content = open('$TEST_FILE').read()
lines = content.split('\n')

in_copy_test = False
for i, line in enumerate(lines):
    if 'copy: emitted when copy button is clicked' in line:
        in_copy_test = True
    elif in_copy_test:
        if line.strip() == '});':
            break
        if line and not line[0] in ('\t', ' '):
            if line.strip():
                print(f'FAIL: inconsistent indentation on line {i+1}')
                sys.exit(1)

print('PASS: TS test formatting consistent')
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Anti-gaming: Sanity checks (0.10)
########################################

# [pr_diff] (0.05): The cache key must still include hashFiles for requirements
# (agent shouldn't have removed dependency tracking)
add 0.05
python3 -c "
import sys
raw = open('$ACTION_FILE').read()
if 'hashFiles' not in raw:
    print('FAIL: cache key no longer includes hashFiles for dependency tracking')
    sys.exit(1)
print('PASS: hashFiles still used in cache key')
" 2>&1
[ $? -eq 0 ] && award 0.05

# [pr_diff] (0.05): The cache paths must still include 'venv' directory
add 0.05
python3 -c "
import yaml, sys
data = yaml.safe_load(open('$ACTION_FILE'))
steps = data.get('runs', {}).get('steps', [])
for step in steps:
    if 'actions/cache' in str(step.get('uses', '')):
        path = str(step.get('with', {}).get('path', ''))
        if 'venv' in path:
            print('PASS: cache paths include venv')
            sys.exit(0)
        else:
            print(f'FAIL: cache paths do not include venv: {path}')
            sys.exit(1)
print('FAIL: cache step not found')
sys.exit(1)
" 2>&1
[ $? -eq 0 ] && award 0.05

########################################
# Compute final reward
########################################

REWARD=$(python3 -c "print(round($PASS, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

# Compute category breakdown
python3 -c "
import json
reward = $REWARD
# Behavioral: ordering(0.25) + key(0.20) + id-resolve(0.10) + tick(0.10) + anti-game(0.10) = 0.75 max
# Regression: core-steps(0.10) + copy-test(0.05) = 0.15 max
# Config: shell(0.05) + format(0.05) = 0.10 max
behavioral = min(reward, 0.75)
remaining = max(reward - 0.75, 0.0)
regression = min(remaining, 0.15)
remaining2 = max(remaining - 0.15, 0.0)
config = min(remaining2, 0.10)
print(json.dumps({
    'reward': round(reward, 2),
    'behavioral': round(behavioral, 2),
    'regression': round(regression, 2),
    'config': round(config, 2),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

echo "Total reward: $REWARD"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
