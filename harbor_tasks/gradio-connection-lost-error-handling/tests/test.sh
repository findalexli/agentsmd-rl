#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_dep]=0.25
WEIGHTS[behavioral_submit]=0.20
WEIGHTS[behavioral_blocks]=0.20
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15

for key in behavioral_dep behavioral_submit behavioral_blocks structural antistub; do
    RESULTS[$key]=0
done

SUBMIT_TS="/workspace/gradio/client/js/src/utils/submit.ts"
DEPENDENCY_TS="/workspace/gradio/js/core/src/dependency.ts"
BLOCKS_SVELTE="/workspace/gradio/js/core/src/Blocks.svelte"

# ---------- GATE: All files exist ----------
for f in "$SUBMIT_TS" "$DEPENDENCY_TS" "$BLOCKS_SVELTE"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f not found"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS: all target files exist"

# ---------- PRIMARY 1 (25%): Behavioral - DependencyManager has connection_lost tracking ----------
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/js/core/src/dependency.ts") as f:
    content = f.read()

# The DependencyManager class must:
# 1. Have a connection_lost property
# 2. Have an on_connection_lost_cb callback
# 3. Short-circuit dispatch when connection is lost
checks = [
    ("connection_lost" in content, "connection_lost property exists"),
    ("on_connection_lost_cb" in content, "on_connection_lost_cb callback exists"),
]

failures = [desc for ok, desc in checks if not ok]
if failures:
    print(f"BEHAVIORAL_DEP FAIL: {', '.join(failures)}")
    sys.exit(1)

# Check that dispatch method checks connection_lost
import re
dispatch_match = re.search(r'async\s+dispatch\s*\([^)]*\)[^{]*\{([\s\S]*?)(?=\n\t[^\t]|\n\s*async\s|\n\s*\/\*\*)', content)
if dispatch_match:
    dispatch_body = dispatch_match.group(1)
    if "connection_lost" in dispatch_body:
        print("BEHAVIORAL_DEP PASS: dispatch checks connection_lost")
        sys.exit(0)
    else:
        print("BEHAVIORAL_DEP FAIL: dispatch does not check connection_lost")
        sys.exit(1)
else:
    # Fallback: just check that connection_lost is used near dispatch
    if content.count("connection_lost") >= 2:
        print("BEHAVIORAL_DEP PASS: connection_lost used multiple times")
        sys.exit(0)
    print("BEHAVIORAL_DEP FAIL: connection_lost not sufficiently integrated")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_dep]=1
    echo "TEST behavioral_dep: PASS"
else
    echo "TEST behavioral_dep: FAIL"
fi

# ---------- PRIMARY 2 (20%): Behavioral - submit.ts sets broken flag on connection errors ----------
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/client/js/src/utils/submit.ts") as f:
    content = f.read()

# Check that error events include broken flag based on connection error detection
# The fix should detect BROKEN_CONNECTION_MSG and set broken: true
if "BROKEN_CONNECTION_MSG" in content and "broken" in content:
    # Check for the pattern: broken: is_connection_error or broken: true tied to BROKEN_CONNECTION_MSG
    import re
    # Look for is_connection_error or similar pattern
    has_connection_check = bool(re.search(r'is_connection_error|BROKEN_CONNECTION_MSG.*broken|broken.*BROKEN_CONNECTION_MSG', content, re.DOTALL))
    if has_connection_check:
        print("BEHAVIORAL_SUBMIT PASS: submit.ts detects connection errors and sets broken flag")
        sys.exit(0)

print("BEHAVIORAL_SUBMIT FAIL: submit.ts does not properly detect/flag connection errors")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_submit]=1
    echo "TEST behavioral_submit: PASS"
else
    echo "TEST behavioral_submit: FAIL"
fi

# ---------- PRIMARY 3 (20%): Behavioral - Blocks.svelte has connection lost handler ----------
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/js/core/src/Blocks.svelte") as f:
    content = f.read()

# Check for connection lost handling and reconnection logic
checks = [
    ("handle_connection_lost" in content or "connection_lost" in content, "connection lost handler"),
    ("reconnect" in content, "reconnect logic"),
    ("setInterval" in content or "reconnect_interval" in content, "reconnection interval"),
]

failures = [desc for ok, desc in checks if not ok]
if failures:
    print(f"BEHAVIORAL_BLOCKS FAIL: missing {', '.join(failures)}")
    sys.exit(1)

print("BEHAVIORAL_BLOCKS PASS: Blocks.svelte has connection lost handler with reconnection")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_blocks]=1
    echo "TEST behavioral_blocks: PASS"
else
    echo "TEST behavioral_blocks: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - DependencyManager constructor accepts callback ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/core/src/dependency.ts") as f:
    content = f.read()

# Check constructor signature includes on_connection_lost callback
constructor_match = re.search(r'constructor\s*\(([\s\S]*?)\)\s*\{', content)
if constructor_match:
    params = constructor_match.group(1)
    if "on_connection_lost" in params or "connection_lost" in params:
        print("STRUCTURAL PASS: DependencyManager constructor accepts connection lost callback")
        sys.exit(0)

# Alternative: check if it's set as a property
if "on_connection_lost_cb" in content:
    print("STRUCTURAL PASS: on_connection_lost_cb property exists")
    sys.exit(0)

print("STRUCTURAL FAIL: no connection lost callback in DependencyManager")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (15%) ----------
ALL_EXIST=1
for f in "$SUBMIT_TS" "$DEPENDENCY_TS" "$BLOCKS_SVELTE"; do
    LINE_COUNT=$(wc -l < "$f")
    if [ "$LINE_COUNT" -lt 50 ]; then
        echo "TEST antistub: FAIL ($f too small: $LINE_COUNT lines)"
        ALL_EXIST=0
        break
    fi
done
if [ "$ALL_EXIST" -eq 1 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_dep': ${WEIGHTS[behavioral_dep]}, 'behavioral_submit': ${WEIGHTS[behavioral_submit]}, 'behavioral_blocks': ${WEIGHTS[behavioral_blocks]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_dep': ${RESULTS[behavioral_dep]}, 'behavioral_submit': ${RESULTS[behavioral_submit]}, 'behavioral_blocks': ${RESULTS[behavioral_blocks]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_dep    (${WEIGHTS[behavioral_dep]}): ${RESULTS[behavioral_dep]}"
echo "  behavioral_submit (${WEIGHTS[behavioral_submit]}): ${RESULTS[behavioral_submit]}"
echo "  behavioral_blocks (${WEIGHTS[behavioral_blocks]}): ${RESULTS[behavioral_blocks]}"
echo "  structural        (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub          (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
