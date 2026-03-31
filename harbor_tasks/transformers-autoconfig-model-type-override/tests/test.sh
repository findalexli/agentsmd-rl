#!/usr/bin/env bash
set +e

CONFIG_UTILS="/workspace/transformers/src/transformers/configuration_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# Weight budget: behavioral=0.70, p2p=0.10, structural=0.10, config=0.10
WEIGHTS[behav_override]=0.35
WEIGHTS[behav_warning]=0.20
WEIGHTS[behav_no_override_same]=0.15
WEIGHTS[p2p_normal_load]=0.10
WEIGHTS[structural_antistub]=0.10
WEIGHTS[config_style]=0.10

for key in behav_override behav_warning behav_no_override_same p2p_normal_load structural_antistub config_style; do
    RESULTS[$key]=0
done

# ---------- GATE: Syntax check ----------
python3 -c "import ast; ast.parse(open('$CONFIG_UTILS').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "GATE FAIL: configuration_utils.py syntax error"; echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: configuration_utils.py parses"

# ---------- BEHAVIORAL 1 (0.35): model_type kwarg overrides config_dict ----------
# [pr_diff] (0.35): Passing model_type kwarg overrides the value from config.json
python3 << 'PYEOF'
import json, os, sys, tempfile

# Create a fake local checkpoint with a wrong model_type
tmpdir = tempfile.mkdtemp()
config = {"model_type": "wrong_type", "architectures": ["WrongModel"]}
with open(os.path.join(tmpdir, "config.json"), "w") as f:
    json.dump(config, f)

from transformers import PretrainedConfig
config_dict, kwargs = PretrainedConfig._get_config_dict(tmpdir, model_type="correct_type")

if config_dict is None:
    print("FAIL: config_dict is None")
    sys.exit(1)

if config_dict.get("model_type") == "correct_type":
    print("PASS: model_type was overridden to 'correct_type'")
    sys.exit(0)
else:
    print(f"FAIL: model_type is '{config_dict.get('model_type')}', expected 'correct_type'")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_override]=1; echo "behav_override: PASS"; else echo "behav_override: FAIL"; fi

# ---------- BEHAVIORAL 2 (0.20): Warning is emitted when overriding ----------
# [pr_diff] (0.20): A warning is logged when model_type is overridden
python3 << 'PYEOF'
import json, logging, os, sys, tempfile

# Create a fake local checkpoint
tmpdir = tempfile.mkdtemp()
config = {"model_type": "old_type", "architectures": ["OldModel"]}
with open(os.path.join(tmpdir, "config.json"), "w") as f:
    json.dump(config, f)

# Capture warnings from the transformers logger
import transformers.utils.logging as tf_logging
tf_logging.set_verbosity_warning()

# Use a custom handler to capture log output
captured = []
handler = logging.Handler()
handler.emit = lambda record: captured.append(record.getMessage())
logger = logging.getLogger("transformers.configuration_utils")
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

from transformers import PretrainedConfig
config_dict, kwargs = PretrainedConfig._get_config_dict(tmpdir, model_type="new_type")

# Check that a warning was emitted mentioning the override
warning_found = any("old_type" in msg and "new_type" in msg for msg in captured)
if warning_found:
    print("PASS: Warning emitted about model_type override")
    sys.exit(0)
else:
    print(f"FAIL: No override warning found in captured messages: {captured}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_warning]=1; echo "behav_warning: PASS"; else echo "behav_warning: FAIL"; fi

# ---------- BEHAVIORAL 3 (0.15): No override when model_type matches ----------
# [pr_diff] (0.15): Passing matching model_type does not trigger override or warning
python3 << 'PYEOF'
import json, logging, os, sys, tempfile

tmpdir = tempfile.mkdtemp()
config = {"model_type": "same_type", "architectures": ["SameModel"]}
with open(os.path.join(tmpdir, "config.json"), "w") as f:
    json.dump(config, f)

captured = []
handler = logging.Handler()
handler.emit = lambda record: captured.append(record.getMessage())
logger = logging.getLogger("transformers.configuration_utils")
logger.addHandler(handler)
logger.setLevel(logging.WARNING)

from transformers import PretrainedConfig
config_dict, kwargs = PretrainedConfig._get_config_dict(tmpdir, model_type="same_type")

if config_dict.get("model_type") != "same_type":
    print(f"FAIL: model_type changed to '{config_dict.get('model_type')}'")
    sys.exit(1)

override_warnings = [m for m in captured if "same_type" in m and "overrode" in m.lower()]
if override_warnings:
    print("FAIL: Warning emitted even though model_type matches")
    sys.exit(1)

print("PASS: No override when model_type matches")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behav_no_override_same]=1; echo "behav_no_override_same: PASS"; else echo "behav_no_override_same: FAIL"; fi

# ---------- PASS-TO-PASS (0.10): Normal config loading still works ----------
# [pr_diff] (0.10): Loading config without model_type kwarg works unchanged
python3 << 'PYEOF'
import json, os, sys, tempfile

tmpdir = tempfile.mkdtemp()
config = {"model_type": "bert", "hidden_size": 768}
with open(os.path.join(tmpdir, "config.json"), "w") as f:
    json.dump(config, f)

from transformers import PretrainedConfig
config_dict, kwargs = PretrainedConfig._get_config_dict(tmpdir)

if config_dict is None:
    print("FAIL: config_dict is None")
    sys.exit(1)

if config_dict.get("model_type") == "bert" and config_dict.get("hidden_size") == 768:
    print("PASS: Normal config loading works")
    sys.exit(0)
else:
    print(f"FAIL: Unexpected config_dict: {config_dict}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_normal_load]=1; echo "p2p_normal_load: PASS"; else echo "p2p_normal_load: FAIL"; fi

# ---------- STRUCTURAL (0.05): Anti-stub check ----------
# [pr_diff] (0.05): File is not stubbed out
python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/configuration_utils.py") as f:
    lines = len(f.readlines())

if lines < 800:
    print(f"FAIL: configuration_utils.py only has {lines} lines (expected >= 800)")
    sys.exit(1)

print(f"PASS: configuration_utils.py has {lines} lines")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural_antistub]=1; echo "structural_antistub: PASS"; else echo "structural_antistub: FAIL"; fi

# ---------- CONFIG-DERIVED (0.05): Code style — minimize diff ----------
# [agent_config] (0.05): "PRs should be as brief as possible" — .github/copilot-instructions.md:12 @ ce4a791
python3 << 'PYEOF'
import subprocess, sys

result = subprocess.run(
    ["git", "diff", "HEAD", "--stat", "--", "src/transformers/configuration_utils.py"],
    capture_output=True, text=True, cwd="/workspace/transformers"
)
diff_stat = result.stdout.strip()

if not diff_stat:
    # Maybe committed
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "--stat", "--", "src/transformers/configuration_utils.py"],
        capture_output=True, text=True, cwd="/workspace/transformers"
    )
    diff_stat = result.stdout.strip()

if not diff_stat:
    print("FAIL: No changes detected")
    sys.exit(1)

# Count insertions — the fix should be small (< 30 lines added)
result2 = subprocess.run(
    ["git", "diff", "HEAD", "--numstat", "--", "src/transformers/configuration_utils.py"],
    capture_output=True, text=True, cwd="/workspace/transformers"
)
numstat = result2.stdout.strip()
if not numstat:
    result2 = subprocess.run(
        ["git", "diff", "HEAD~1", "--numstat", "--", "src/transformers/configuration_utils.py"],
        capture_output=True, text=True, cwd="/workspace/transformers"
    )
    numstat = result2.stdout.strip()

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
    print("PASS: Could not parse numstat, skipping")
    sys.exit(0)
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
for key in behav_override behav_warning behav_no_override_same p2p_normal_load structural_antistub config_style; do
    STATUS="FAIL"
    if [ "${RESULTS[$key]}" -eq 1 ]; then STATUS="PASS"; fi
    echo "  $key (${WEIGHTS[$key]}): $STATUS"
done
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
