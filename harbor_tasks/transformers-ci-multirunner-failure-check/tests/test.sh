#!/usr/bin/env bash
set +e

WORKSPACE="/workspace/transformers"
REWARD=0

log() { echo "[test.sh] $*"; }
add() {
    local w=$1 label=$2 pass=$3
    if [ "$pass" = "1" ]; then
        REWARD=$(python3 -c "print($REWARD + $w)")
        log "PASS ($w): $label"
    else
        log "FAIL ($w): $label"
    fi
}

mkdir -p /logs/verifier

# ============================================================
# GATE: Syntax checks
# ============================================================
log "GATE: Python syntax"
if ! python3 -c "import py_compile; py_compile.compile('$WORKSPACE/utils/check_bad_commit.py', doraise=True)" 2>/dev/null; then
    log "GATE FAILED: check_bad_commit.py syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

log "GATE: YAML syntax"
if ! python3 -c "import yaml; yaml.safe_load(open('$WORKSPACE/.github/workflows/check_failed_tests.yml'))" 2>/dev/null; then
    log "GATE FAILED: check_failed_tests.yml YAML error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
log "GATE: passed"

# ============================================================
# Create test fixtures: mock failures JSON + patched script
# ============================================================
python3 << 'PYEOF'
import json

# 12 tests across 3 models
failures = {
    "model_a": {"single-gpu": [{"line": f"tests/test_a_{i}.py::test_{i}"} for i in range(5)]},
    "model_b": {"single-gpu": [{"line": f"tests/test_b_{i}.py::test_{i}"} for i in range(4)]},
    "model_c": {"single-gpu": [{"line": f"tests/test_c_{i}.py::test_{i}"} for i in range(3)]},
}
with open("/tmp/test_failures.json", "w") as f:
    json.dump(failures, f)

# Create patched script: mock find_bad_commit and get_commit_info to avoid git bisect
with open("/workspace/transformers/utils/check_bad_commit.py") as f:
    source = f.read()

mock = '''
# === TEST MOCKS (inserted by test harness) ===
def find_bad_commit(target_test, start_commit, end_commit):
    return {"bad_commit": "abc123def456", "status": "found"}

def get_commit_info(commit, pr_number=None):
    return {"commit": commit, "author": "test_author", "pr_number": "42"}
# === END MOCKS ===
'''

idx = source.find('if __name__')
if idx == -1:
    raise RuntimeError("Cannot find if __name__ block in check_bad_commit.py")
patched = source[:idx] + mock + source[idx:]
with open("/tmp/check_bad_commit_patched.py", "w") as f:
    f.write(patched)
PYEOF

if [ $? -ne 0 ]; then
    log "FATAL: could not create test fixtures"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ============================================================
# BEHAVIORAL: Fail-to-pass tests (0.70)
# ============================================================

# [pr_diff] (0.35): Script partitions work across runners via run_idx/n_runners env vars
# Buggy code: processes ALL tests regardless of env vars. Fixed: each runner gets a slice.
log "F2P: Script partitions tests across multiple runners..."
F2P_PARTITION=0
python3 << 'PYEOF'
import json, os, subprocess, sys

n_runners = 3
all_tests = []
runner_counts = []

for idx in range(1, n_runners + 1):
    env = os.environ.copy()
    env["run_idx"] = str(idx)
    env["n_runners"] = str(n_runners)

    outfile = f"/tmp/runner_{idx}_output.json"
    result = subprocess.run(
        ["python3", "/tmp/check_bad_commit_patched.py",
         "--start_commit", "aaa", "--end_commit", "bbb",
         "--file", "/tmp/test_failures.json",
         "--output_file", outfile],
        env=env, capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        print(f"Runner {idx} failed (rc={result.returncode}): {result.stderr[:500]}")
        sys.exit(1)

    with open(outfile) as f:
        out = json.load(f)

    tests = []
    for model, data in out.items():
        for t in data.get("single-gpu", []):
            tests.append(t.get("test", t.get("line", "")))

    runner_counts.append(len(tests))
    all_tests.extend(tests)
    print(f"Runner {idx}: {len(tests)} tests")

# Each runner must get a SUBSET, not all 12
if max(runner_counts) >= 12:
    print(f"FAIL: runner processed all 12 tests — no partitioning in effect")
    sys.exit(1)

# Together, all runners must cover exactly all 12 tests
if len(set(all_tests)) != 12:
    print(f"FAIL: expected 12 unique tests across all runners, got {len(set(all_tests))}")
    sys.exit(1)

# No duplicates
if len(all_tests) != 12:
    print(f"FAIL: {len(all_tests)} total tests (expected 12, no duplicates)")
    sys.exit(1)

# Each runner should get at least 1 test
if min(runner_counts) == 0:
    print(f"FAIL: a runner got 0 tests — unbalanced partitioning")
    sys.exit(1)

print(f"PASS: 12 tests partitioned across 3 runners: {runner_counts}")
PYEOF
[ $? -eq 0 ] && F2P_PARTITION=1
add 0.35 "Script partitions tests across runners (fail-to-pass)" "$F2P_PARTITION"

# [pr_diff] (0.10): Output from each runner is keyed by model name
# Buggy code: uses flat list. Fixed: accumulates by model.
log "F2P: Runner output is keyed by model name..."
F2P_MODEL=0
python3 << 'PYEOF'
import json, os, subprocess, sys

# Run with a single runner so all tests are included
env = os.environ.copy()
env["run_idx"] = "1"
env["n_runners"] = "1"

outfile = "/tmp/runner_modelkey_output.json"
result = subprocess.run(
    ["python3", "/tmp/check_bad_commit_patched.py",
     "--start_commit", "aaa", "--end_commit", "bbb",
     "--file", "/tmp/test_failures.json",
     "--output_file", outfile],
    env=env, capture_output=True, text=True, timeout=30
)

if result.returncode != 0:
    print(f"Failed: {result.stderr[:300]}")
    sys.exit(1)

with open(outfile) as f:
    out = json.load(f)

# Output must be a dict keyed by model name
if not isinstance(out, dict):
    print(f"FAIL: output is {type(out).__name__}, expected dict keyed by model")
    sys.exit(1)

# Each model with tests should appear as a key
expected_models = {"model_a", "model_b", "model_c"}
if not expected_models.issubset(set(out.keys())):
    print(f"FAIL: expected models {expected_models}, got keys {set(out.keys())}")
    sys.exit(1)

# Each model should have single-gpu with enriched test entries
for model in expected_models:
    sg = out[model].get("single-gpu", [])
    if len(sg) == 0:
        print(f"FAIL: model '{model}' has no single-gpu tests")
        sys.exit(1)
    # Each entry should have 'test' key (added by the script)
    for entry in sg:
        if "test" not in entry and "line" not in entry:
            print(f"FAIL: entry in {model} missing 'test' key: {entry}")
            sys.exit(1)

total = sum(len(v.get("single-gpu", [])) for v in out.values())
if total != 12:
    print(f"FAIL: expected 12 total tests with n_runners=1, got {total}")
    sys.exit(1)

print("PASS: output correctly keyed by model name with all tests")
PYEOF
[ $? -eq 0 ] && F2P_MODEL=1
add 0.10 "Runner output keyed by model (fail-to-pass)" "$F2P_MODEL"

# [pr_diff] (0.10): Workflow uses dynamic matrix (not hardcoded [1])
# Buggy: run_idx: [1]. Fixed: fromJson or expression referencing setup job.
log "F2P: Workflow dynamic matrix..."
F2P_MATRIX=0
python3 << 'PYEOF'
import yaml, sys

with open("/workspace/transformers/.github/workflows/check_failed_tests.yml") as f:
    wf = yaml.safe_load(f)

jobs = wf.get("jobs", {})

# Find check_new_failures job
check_job = None
for name, defn in jobs.items():
    if "check_new_failures" in name and "process" not in name and "setup" not in name:
        check_job = defn
        break

if check_job is None:
    print("FAIL: no check_new_failures job found")
    sys.exit(1)

strategy = check_job.get("strategy", {})
matrix = strategy.get("matrix", {})
run_idx = matrix.get("run_idx")

# Buggy baseline: [1] hardcoded. Any other value is a fix.
if run_idx == [1]:
    print("FAIL: run_idx is still hardcoded to [1]")
    sys.exit(1)

if run_idx is None:
    print("FAIL: no run_idx in strategy.matrix")
    sys.exit(1)

# Must depend on a setup job
needs = check_job.get("needs", [])
if isinstance(needs, str):
    needs = [needs]
if not any("setup" in n for n in needs):
    print("FAIL: check_new_failures does not depend on a setup job")
    sys.exit(1)

print(f"PASS: dynamic matrix with run_idx={str(run_idx)[:60]}")
PYEOF
[ $? -eq 0 ] && F2P_MATRIX=1
add 0.10 "Workflow uses dynamic matrix (fail-to-pass)" "$F2P_MATRIX"

# [pr_diff] (0.10): Merge step combines results from multiple runners
# Buggy: cp ..._1.json. Fixed: iterates over multiple files and merges JSON.
log "F2P: Merge step combines multi-runner results..."
F2P_MERGE=0
python3 << 'PYEOF'
import yaml, sys

with open("/workspace/transformers/.github/workflows/check_failed_tests.yml") as f:
    wf = yaml.safe_load(f)

jobs = wf.get("jobs", {})

# Find the process/merge job
merge_job = None
for name, defn in jobs.items():
    if "process_new_failures" in name:
        merge_job = defn
        break

if merge_job is None:
    print("FAIL: no process_new_failures job found")
    sys.exit(1)

steps = merge_job.get("steps", [])

# Find merge step by name
merge_step = None
for step in steps:
    sname = step.get("name", "").lower()
    if "merge" in sname:
        merge_step = step
        break

if merge_step is None:
    print("FAIL: no merge step found in process_new_failures job")
    sys.exit(1)

run_cmd = merge_step.get("run", "")

# Buggy baseline: just copies _1.json with a simple cp
# Check it's NOT a simple single-file copy
lines = [l.strip() for l in run_cmd.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
if len(lines) == 1 and lines[0].startswith("cp ") and "_1.json" in lines[0]:
    print("FAIL: merge step is still a simple cp of _1.json")
    sys.exit(1)

# Should handle multiple files (loop, glob, python script, etc.)
has_iteration = any(kw in run_cmd for kw in ["for ", "while ", "python", "*.json", "glob"])
if not has_iteration:
    print(f"FAIL: merge step doesn't iterate over multiple runner files")
    sys.exit(1)

print("PASS: merge step handles multiple runner outputs")
PYEOF
[ $? -eq 0 ] && F2P_MERGE=1
add 0.10 "Merge step combines multi-runner results (fail-to-pass)" "$F2P_MERGE"

# [pr_diff] (0.05): Workflow has max_num_runners input
log "F2P: max_num_runners workflow input..."
F2P_MAXRUNNERS=0
python3 << 'PYEOF'
import yaml, sys

with open("/workspace/transformers/.github/workflows/check_failed_tests.yml") as f:
    wf = yaml.safe_load(f)

on = wf.get("on", wf.get(True, {}))
inputs = on.get("workflow_call", {}).get("inputs", {})

if "max_num_runners" not in inputs:
    print("FAIL: max_num_runners input not found in workflow_call inputs")
    sys.exit(1)

inp = inputs["max_num_runners"]
if inp.get("type") not in ("number", "integer"):
    print(f"FAIL: max_num_runners type should be number, got {inp.get('type')}")
    sys.exit(1)

if inp.get("default") is None:
    print("FAIL: max_num_runners should have a default value")
    sys.exit(1)

print(f"PASS: max_num_runners input, type={inp['type']}, default={inp['default']}")
PYEOF
[ $? -eq 0 ] && F2P_MAXRUNNERS=1
add 0.05 "max_num_runners workflow input (fail-to-pass)" "$F2P_MAXRUNNERS"

# ============================================================
# PASS-TO-PASS (0.15)
# ============================================================

# [pr_diff] (0.10): Script still processes all tests when run_idx/n_runners are NOT set
log "P2P: Script works without partition env vars..."
P2P_COMPAT=0
python3 << 'PYEOF'
import json, os, subprocess, sys

env = os.environ.copy()
env.pop("run_idx", None)
env.pop("n_runners", None)

outfile = "/tmp/runner_noenv_output.json"
result = subprocess.run(
    ["python3", "/tmp/check_bad_commit_patched.py",
     "--start_commit", "aaa", "--end_commit", "bbb",
     "--file", "/tmp/test_failures.json",
     "--output_file", outfile],
    env=env, capture_output=True, text=True, timeout=30
)

if result.returncode != 0:
    print(f"Failed: {result.stderr[:500]}")
    sys.exit(1)

with open(outfile) as f:
    out = json.load(f)

total = sum(len(v.get("single-gpu", [])) for v in out.values())
if total != 12:
    print(f"FAIL: without env vars should process all 12 tests, got {total}")
    sys.exit(1)

print("PASS: processes all 12 tests when partitioning env vars not set")
PYEOF
[ $? -eq 0 ] && P2P_COMPAT=1
add 0.10 "Script backwards-compatible without env vars (pass-to-pass)" "$P2P_COMPAT"

# [pr_diff] (0.05): Workflow preserves existing jobs and required inputs
log "P2P: Workflow structural integrity..."
P2P_STRUCT=0
python3 << 'PYEOF'
import yaml, sys

with open("/workspace/transformers/.github/workflows/check_failed_tests.yml") as f:
    wf = yaml.safe_load(f)

jobs = wf.get("jobs", {})

# Must still have both core jobs
has_check = any("check_new_failures" in n for n in jobs)
has_process = any("process_new_failures" in n for n in jobs)
if not has_check or not has_process:
    print(f"FAIL: missing jobs (check={has_check}, process={has_process})")
    sys.exit(1)

# Must still have workflow_call trigger with docker and job inputs
on = wf.get("on", wf.get(True, {}))
if "workflow_call" not in on:
    print("FAIL: missing workflow_call trigger")
    sys.exit(1)

inputs = on["workflow_call"].get("inputs", {})
for required in ("docker", "job"):
    if required not in inputs:
        print(f"FAIL: missing required input '{required}'")
        sys.exit(1)

print("PASS: workflow structure preserved")
PYEOF
[ $? -eq 0 ] && P2P_STRUCT=1
add 0.05 "Workflow structure preserved (pass-to-pass)" "$P2P_STRUCT"

# ============================================================
# CONFIG (0.05)
# ============================================================

# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 882ffdbb
log "Config: code style check..."
STYLE=0
if command -v ruff &>/dev/null; then
    ruff check "$WORKSPACE/utils/check_bad_commit.py" --select E,W --quiet 2>/dev/null && STYLE=1
else
    STYLE=1
fi
add 0.05 "Code style (ruff)" "$STYLE"

# ============================================================
# FINAL SCORE
# ============================================================
log "Final score: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
r = $REWARD
data = {
    'reward': r,
    'behavioral': round(min(r, 0.70), 4),
    'regression': round(min(max(0, r - 0.70), 0.15), 4),
    'config': round(min(max(0, r - 0.85), 0.05), 4),
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
