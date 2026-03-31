#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/gradio

##############################################################################
# GATE: Syntax check — abort on failure
##############################################################################
# [pr_diff] (gate): Modified Python files must parse without syntax errors
python3 -c "import ast; ast.parse(open('gradio/chat_interface.py').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: gradio/chat_interface.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.35 total)
##############################################################################

# [pr_diff] (0.30): ChatInterface(fill_height=False) chatbot height must not be None
# Buggy code: height=400 if self.fill_height else None → sets height=None
# Any correct fix avoids setting height=None (remove kwarg, use constant, etc.)
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, fill_height=False)
if ci.chatbot.height is None:
    print("FAIL: chatbot height is None when fill_height=False (buggy behavior)", file=sys.stderr)
    sys.exit(1)

# Height should be a positive number
if not isinstance(ci.chatbot.height, (int, float)) or ci.chatbot.height <= 0:
    print(f"FAIL: chatbot height is {ci.chatbot.height}, expected positive number", file=sys.stderr)
    sys.exit(1)

print(f"PASS: chatbot height is {ci.chatbot.height} when fill_height=False")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.30
    echo "PASS [0.30]: ChatInterface(fill_height=False) chatbot has valid height"
else
    add_total 0.30
    echo "FAIL [0.30]: ChatInterface(fill_height=False) chatbot height is None"
fi

# [pr_diff] (0.05): ChatInterface(fill_height=False) chatbot height matches Chatbot default
# The fix should let Chatbot use its own default, not override with an arbitrary value
python3 - <<'PYEOF'
import sys
from gradio import Chatbot, ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

# Get the Chatbot's own default height
default_bot = Chatbot()
default_height = default_bot.height

ci = ChatInterface(fn=echo, fill_height=False)
if ci.chatbot.height != default_height:
    print(f"FAIL: chatbot height={ci.chatbot.height}, expected Chatbot default={default_height}", file=sys.stderr)
    sys.exit(1)

print(f"PASS: chatbot height matches Chatbot default ({default_height})")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: ChatInterface(fill_height=False) uses Chatbot default height"
else
    add_total 0.05
    echo "FAIL [0.05]: ChatInterface(fill_height=False) doesn't use Chatbot default height"
fi

##############################################################################
# BEHAVIORAL: Pass-to-pass tests (0.25 total)
##############################################################################

# [pr_diff] (0.10): ChatInterface(fill_height=True) basic functionality preserved
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, fill_height=True)
assert ci.chatbot is not None, "chatbot is None"
assert ci.chatbot.scale == 1, f"chatbot.scale={ci.chatbot.scale}, expected 1"
assert ci.chatbot.height is not None, "chatbot.height is None"

# Submit flow still works
history = ci._append_message_to_history("test", [], "user")
assert len(history) == 1
assert history[0]["content"] == "test"

print("PASS: ChatInterface(fill_height=True) basic functionality works")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: ChatInterface(fill_height=True) basic functionality"
else
    add_total 0.10
    echo "FAIL [0.10]: ChatInterface(fill_height=True) basic functionality broken"
fi

# [pr_diff] (0.10): Default ChatInterface config includes fill_height
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo)
# Default fill_height should be True
assert ci.fill_height is True, f"fill_height={ci.fill_height}, expected True"
# Config should include fill_height
config = ci.config
assert "fill_height" in config, f"fill_height not in config keys"
assert config["fill_height"] is True, f"config fill_height={config['fill_height']}"

print("PASS: Default ChatInterface has fill_height=True in config")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: Default ChatInterface config includes fill_height"
else
    add_total 0.10
    echo "FAIL [0.10]: Default ChatInterface config missing fill_height"
fi

# [pr_diff] (0.05): ChatInterface(fill_height=False) config reflects fill_height=False
python3 - <<'PYEOF'
import sys
from gradio import ChatInterface

def echo(msg, hist):
    return f"Echo: {msg}"

ci = ChatInterface(fn=echo, fill_height=False)
config = ci.config
fh = config.get("fill_height")
if fh is not False:
    print(f"FAIL: config fill_height={fh}, expected False", file=sys.stderr)
    sys.exit(1)

print("PASS: fill_height=False propagated to config")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "PASS [0.05]: ChatInterface(fill_height=False) config correct"
else
    add_total 0.05
    echo "FAIL [0.05]: ChatInterface(fill_height=False) config incorrect"
fi

##############################################################################
# STRUCTURAL: Frontend JavaScript checks (0.20 total)
# WHY structural: Svelte/TS files require a frontend build + browser to execute.
# Cannot call this code from Python — structural checks are the only option.
##############################################################################

# [pr_diff] (0.10): init.svelte.ts sets scale on root column based on fill_height
# Accepts any implementation where scale uses fill_height within the column context
python3 - <<'PYEOF'
import sys

with open("js/core/src/init.svelte.ts") as f:
    content = f.read()

lines = content.splitlines()
found = False

for i, line in enumerate(lines):
    stripped = line.strip()
    # Skip pure comment lines — require actual code
    if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
        continue
    if "scale" in line and "fill_height" in line:
        # Verify this is in the root column context (near component_class_id: "column")
        context_start = max(0, i - 40)
        context_end = min(len(lines), i + 20)
        context = "\n".join(lines[context_start:context_end])
        if "column" in context:
            found = True
            break

if not found:
    print("FAIL: init.svelte.ts missing scale assignment from fill_height in column context", file=sys.stderr)
    sys.exit(1)

print("PASS: init.svelte.ts sets scale from fill_height in column context")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: init.svelte.ts scale derived from fill_height"
else
    add_total 0.10
    echo "FAIL [0.10]: init.svelte.ts missing fill_height→scale propagation"
fi

# [pr_diff] (0.10): Blocks.svelte forwards fill_height in config to AppTree
# Must appear in at least 2 config-forwarding contexts (constructor + reload)
python3 - <<'PYEOF'
import sys

with open("js/core/src/Blocks.svelte") as f:
    content = f.read()

lines = content.splitlines()
config_contexts = 0
i = 0
while i < len(lines):
    stripped = lines[i].strip()
    # Skip pure comment lines
    if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
        i += 1
        continue
    if "fill_height" in lines[i]:
        # Check this is in a config-forwarding context (near known config properties)
        context_start = max(0, i - 15)
        context_end = min(len(lines), i + 15)
        context = "\n".join(lines[context_start:context_end])
        config_keywords = ["autoscroll", "api_prefix", "max_file_size", "version"]
        if sum(1 for kw in config_keywords if kw in context) >= 2:
            config_contexts += 1
            i += 20  # Skip ahead to avoid double-counting same block
            continue
    i += 1

if config_contexts < 2:
    print(f"FAIL: Blocks.svelte has fill_height in {config_contexts} config contexts, need >=2", file=sys.stderr)
    sys.exit(1)

print(f"PASS: Blocks.svelte forwards fill_height in {config_contexts} config contexts")
PYEOF
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "PASS [0.10]: Blocks.svelte forwards fill_height in config"
else
    add_total 0.10
    echo "FAIL [0.10]: Blocks.svelte missing fill_height in config forwarding"
fi

##############################################################################
# CONFIG-DERIVED: Agent config checks (0.05 total)
##############################################################################

# [agent_config] (0.05): "Python code is formatted with ruff" — AGENTS.md:43
if command -v ruff &>/dev/null; then
    ruff check gradio/chat_interface.py --select E,W --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        add_score 0.05
        echo "PASS [0.05]: ruff check passes on chat_interface.py"
    else
        add_total 0.05
        echo "FAIL [0.05]: ruff check fails on chat_interface.py"
    fi
else
    add_score 0.05
    echo "SKIP [0.05]: ruff not available, assuming pass"
fi

##############################################################################
# ANTI-STUB: Files are not empty stubs (0.10 total)
##############################################################################

# [pr_diff] (0.05): chat_interface.py is substantive (not stubbed)
PYLINES=$(wc -l < gradio/chat_interface.py)
if [ "$PYLINES" -gt 100 ]; then
    add_score 0.05
    echo "PASS [0.05]: chat_interface.py is substantive ($PYLINES lines)"
else
    add_total 0.05
    echo "FAIL [0.05]: chat_interface.py looks stubbed ($PYLINES lines)"
fi

# [pr_diff] (0.05): init.svelte.ts is substantive (not stubbed)
JSLINES=$(wc -l < js/core/src/init.svelte.ts)
if [ "$JSLINES" -gt 100 ]; then
    add_score 0.05
    echo "PASS [0.05]: init.svelte.ts is substantive ($JSLINES lines)"
else
    add_total 0.05
    echo "FAIL [0.05]: init.svelte.ts looks stubbed ($JSLINES lines)"
fi

##############################################################################
# SUMMARY
##############################################################################

FINAL=$(python3 -c "print(round($SCORE, 2))")
echo ""
echo "Total score: $FINAL / 1.0"
echo "$FINAL" > /logs/verifier/reward.txt

# Build reward.json with component scores
python3 - <<PYEOF
import json

score = $SCORE
# Behavioral: F2P (0.35) + P2P (0.25) = 0.60
behavioral = min(score, 0.60)
remaining = max(score - 0.60, 0.0)
# Regression/structural: JS checks (0.20) + anti-stub (0.10) = 0.30
regression = min(remaining, 0.30)
remaining = max(remaining - 0.30, 0.0)
# Config: 0.05
config = min(remaining, 0.05)

result = {
    "reward": round(score, 2),
    "behavioral": round(behavioral, 2),
    "regression": round(regression, 2),
    "config": round(config, 2),
    "style_rubric": 0.0
}
with open("/logs/verifier/reward.json", "w") as f:
    json.dump(result, f)
print(json.dumps(result))
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
