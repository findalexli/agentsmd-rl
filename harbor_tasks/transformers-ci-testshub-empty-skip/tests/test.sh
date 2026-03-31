#!/usr/bin/env bash
set +e

FETCHER="/workspace/transformers/utils/tests_fetcher.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.75, p2p=0.10, structural=0.05, config=0.10
WEIGHTS[behav_core_f2p]=0.50
WEIGHTS[behav_multi_jobs]=0.15
WEIGHTS[behav_hub_content]=0.10
WEIGHTS[p2p_other_jobs]=0.10
WEIGHTS[structural_antistub]=0.05
WEIGHTS[config_style]=0.10

for key in behav_core_f2p behav_multi_jobs behav_hub_content p2p_other_jobs structural_antistub config_style; do
    RESULTS[$key]=0
done

# ---------- GATE: Syntax check ----------
python3 -c "import ast; ast.parse(open('$FETCHER').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "GATE FAIL: tests_fetcher.py syntax error"; echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: tests_fetcher.py parses"

# ---------- BEHAVIORAL 1 (0.50): Core fail-to-pass — combined empty/non-empty ----------
# [pr_diff] (0.50): Empty test list => no tests_hub; non-empty => tests_hub exists
# Both conditions must hold — a no-op that never writes files cannot score here.
python3 << 'PYEOF'
import importlib.util, os, sys, tempfile, shutil

spec = importlib.util.spec_from_file_location("tests_fetcher", "/workspace/transformers/utils/tests_fetcher.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["tests_fetcher"] = mod
spec.loader.exec_module(mod)

passed = True

# Part A: Empty test list → tests_hub must NOT be written
tmpdir_a = tempfile.mkdtemp()
try:
    mod.create_test_list_from_filter([], tmpdir_a)
    hub_file = os.path.join(tmpdir_a, "tests_hub_test_list.txt")
    if os.path.exists(hub_file):
        print("FAIL part A: tests_hub_test_list.txt written despite empty test list")
        passed = False
    else:
        print("PASS part A: tests_hub not written for empty list")
finally:
    shutil.rmtree(tmpdir_a)

# Part B: Non-empty test list → tests_hub MUST be written
tmpdir_b = tempfile.mkdtemp()
try:
    test_files = ["tests/models/bert/test_modeling_bert.py"]
    mod.create_test_list_from_filter(test_files, tmpdir_b)
    hub_file = os.path.join(tmpdir_b, "tests_hub_test_list.txt")
    if not os.path.exists(hub_file):
        print("FAIL part B: tests_hub_test_list.txt not written despite real tests")
        passed = False
    else:
        print("PASS part B: tests_hub written for non-empty list")
finally:
    shutil.rmtree(tmpdir_b)

sys.exit(0 if passed else 1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_core_f2p]=1; echo "behav_core_f2p: PASS"; else echo "behav_core_f2p: FAIL"; fi

# ---------- BEHAVIORAL 2 (0.15): Multiple job matches => hub + others present ----------
# [pr_diff] (0.15): With multiple matching jobs, tests_hub and other jobs all get files
python3 << 'PYEOF'
import importlib.util, os, sys, tempfile, shutil

spec = importlib.util.spec_from_file_location("tests_fetcher", "/workspace/transformers/utils/tests_fetcher.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["tests_fetcher"] = mod
spec.loader.exec_module(mod)

tmpdir = tempfile.mkdtemp()
try:
    test_files = [
        "tests/models/bert/test_modeling_bert.py",
        "tests/models/bert/test_tokenization_bert.py",
        "tests/repo_utils/test_check_config_docstrings.py",
    ]
    mod.create_test_list_from_filter(test_files, tmpdir)

    hub_file = os.path.join(tmpdir, "tests_hub_test_list.txt")
    torch_file = os.path.join(tmpdir, "tests_torch_test_list.txt")

    if not os.path.exists(hub_file):
        print("FAIL: tests_hub_test_list.txt missing with multiple matching jobs")
        sys.exit(1)
    if not os.path.exists(torch_file):
        print("FAIL: tests_torch_test_list.txt missing")
        sys.exit(1)

    print("PASS: tests_hub and tests_torch files both written with multiple matches")
    sys.exit(0)
finally:
    shutil.rmtree(tmpdir)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_multi_jobs]=1; echo "behav_multi_jobs: PASS"; else echo "behav_multi_jobs: FAIL"; fi

# ---------- BEHAVIORAL 3 (0.10): tests_hub content is correct when written ----------
# [pr_diff] (0.10): When tests_hub is written, it should contain "tests"
python3 << 'PYEOF'
import importlib.util, os, sys, tempfile, shutil

spec = importlib.util.spec_from_file_location("tests_fetcher", "/workspace/transformers/utils/tests_fetcher.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["tests_fetcher"] = mod
spec.loader.exec_module(mod)

tmpdir = tempfile.mkdtemp()
try:
    test_files = ["tests/models/bert/test_modeling_bert.py"]
    mod.create_test_list_from_filter(test_files, tmpdir)
    hub_file = os.path.join(tmpdir, "tests_hub_test_list.txt")
    if not os.path.exists(hub_file):
        print("FAIL: tests_hub_test_list.txt not written")
        sys.exit(1)
    content = open(hub_file).read().strip()
    if content == "tests":
        print("PASS: tests_hub content is 'tests'")
        sys.exit(0)
    else:
        print(f"FAIL: tests_hub content is '{content}', expected 'tests'")
        sys.exit(1)
finally:
    shutil.rmtree(tmpdir)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_hub_content]=1; echo "behav_hub_content: PASS"; else echo "behav_hub_content: FAIL"; fi

# ---------- PASS-TO-PASS (0.10): Non-hub jobs still get correct files ----------
# [pr_diff] (0.10): Other job test lists are unaffected by the fix
python3 << 'PYEOF'
import importlib.util, os, sys, tempfile, shutil

spec = importlib.util.spec_from_file_location("tests_fetcher", "/workspace/transformers/utils/tests_fetcher.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["tests_fetcher"] = mod
spec.loader.exec_module(mod)

tmpdir = tempfile.mkdtemp()
try:
    test_files = [
        "tests/models/bert/test_modeling_bert.py",
        "tests/repo_utils/test_check_config_docstrings.py",
    ]
    mod.create_test_list_from_filter(test_files, tmpdir)

    torch_file = os.path.join(tmpdir, "tests_torch_test_list.txt")
    if not os.path.exists(torch_file):
        print("FAIL: tests_torch_test_list.txt not written")
        sys.exit(1)

    content = open(torch_file).read().strip()
    if "tests/models/bert/test_modeling_bert.py" in content:
        print("PASS: tests_torch contains expected test file")
        sys.exit(0)
    else:
        print(f"FAIL: tests_torch content unexpected: {content}")
        sys.exit(1)
finally:
    shutil.rmtree(tmpdir)
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_other_jobs]=1; echo "p2p_other_jobs: PASS"; else echo "p2p_other_jobs: FAIL"; fi

# ---------- STRUCTURAL (0.05): Anti-stub check ----------
# [pr_diff] (0.05): File is not stubbed out
python3 << 'PYEOF'
import sys

with open("/workspace/transformers/utils/tests_fetcher.py") as f:
    lines = len(f.readlines())

if lines < 800:
    print(f"FAIL: tests_fetcher.py only has {lines} lines (expected >= 800)")
    sys.exit(1)

print(f"PASS: tests_fetcher.py has {lines} lines")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural_antistub]=1; echo "structural_antistub: PASS"; else echo "structural_antistub: FAIL"; fi

# ---------- CONFIG-DERIVED (0.10): Code style — minimize diff ----------
# [agent_config] (0.10): "PRs should be as brief as possible" — .github/copilot-instructions.md:12 @ c9faacd
python3 << 'PYEOF'
import subprocess, sys

result = subprocess.run(
    ["git", "diff", "HEAD", "--numstat", "--", "utils/tests_fetcher.py"],
    capture_output=True, text=True, cwd="/workspace/transformers"
)
numstat = result.stdout.strip()
if not numstat:
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--numstat", "--", "utils/tests_fetcher.py"],
        capture_output=True, text=True, cwd="/workspace/transformers"
    )
    numstat = result.stdout.strip()

if numstat:
    parts = numstat.split()
    added = int(parts[0])
    if added <= 30:
        print(f"PASS: Minimal diff ({added} lines added)")
        sys.exit(0)
    else:
        print(f"FAIL: Too many lines added ({added}), expected <= 30")
        sys.exit(1)
else:
    print("FAIL: No changes detected in tests_fetcher.py")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[config_style]=1; echo "config_style: PASS"; else echo "config_style: FAIL"; fi

# ---------- COMPUTE SCORE ----------
SCORE="0.0"
for key in "${!WEIGHTS[@]}"; do
    if [ "${RESULTS[$key]}" -eq 1 ]; then
        SCORE=$(python3 -c "print(round($SCORE + ${WEIGHTS[$key]}, 4))")
    fi
done

echo ""
echo "=== FINAL SCORE ==="
for key in behav_core_f2p behav_multi_jobs behav_hub_content p2p_other_jobs structural_antistub config_style; do
    STATUS="FAIL"
    if [ "${RESULTS[$key]}" -eq 1 ]; then STATUS="PASS"; fi
    echo "  $key (${WEIGHTS[$key]}): $STATUS"
done
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
