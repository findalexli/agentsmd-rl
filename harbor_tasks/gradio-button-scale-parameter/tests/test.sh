#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/button/Index.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_shared]=0.35
WEIGHTS[behavioral_no_props_scale]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.20

for key in behavioral_shared behavioral_no_props_scale structural antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target file exists"

# ---------- PRIMARY 1 (35%): Behavioral - scale reads from gradio.shared ----------
# The fix changes gradio.props.scale to gradio.shared.scale
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# The key behavioral check: scale= should reference gradio.shared.scale
# (not gradio.props.scale which is always undefined)
if "gradio.shared.scale" in content:
    # Verify it's used in the scale= binding
    import re
    match = re.search(r'scale\s*=\s*\{?\s*gradio\.shared\.scale\s*\}?', content)
    if match:
        print("BEHAVIORAL_SHARED PASS: scale reads from gradio.shared.scale")
        sys.exit(0)
    else:
        print("BEHAVIORAL_SHARED FAIL: gradio.shared.scale found but not in scale= binding")
        sys.exit(1)
else:
    print("BEHAVIORAL_SHARED FAIL: gradio.shared.scale not found in file")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_shared]=1
    echo "TEST behavioral_shared: PASS"
else
    echo "TEST behavioral_shared: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - scale NOT read from gradio.props ----------
python3 << 'PYEOF'
import sys, re

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# The bug was: scale={gradio.props.scale}
# Check that this pattern is NOT present
match = re.search(r'scale\s*=\s*\{?\s*gradio\.props\.scale\s*\}?', content)
if match:
    print("BEHAVIORAL_NO_PROPS_SCALE FAIL: still reading scale from gradio.props.scale")
    sys.exit(1)
else:
    print("BEHAVIORAL_NO_PROPS_SCALE PASS: no longer using gradio.props.scale for scale binding")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_no_props_scale]=1
    echo "TEST behavioral_no_props_scale: PASS"
else
    echo "TEST behavioral_no_props_scale: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - scale removed from ButtonProps interface ----------
python3 << 'PYEOF'
import sys, re

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# Check that ButtonProps interface no longer contains 'scale'
# The interface is in the <script> section within an interface block
# Look for the props type definition area
props_block = re.search(r'interface\s+ButtonProps[^{]*\{([^}]*)\}', content, re.DOTALL)
if props_block is None:
    # Try the let { ... }: { ... } destructuring pattern
    props_block = re.search(r'let\s*\{[^}]*\}\s*:\s*\{([^}]*)\}', content, re.DOTALL)

if props_block:
    props_content = props_block.group(1)
    # Check that scale is NOT defined in the props
    if re.search(r'\bscale\b', props_content):
        print("STRUCTURAL FAIL: scale still present in ButtonProps interface")
        sys.exit(1)
    else:
        print("STRUCTURAL PASS: scale removed from ButtonProps interface")
        sys.exit(0)
else:
    # If we can't find the props block, just check that the file doesn't
    # have scale in an interface/type definition context
    print("STRUCTURAL PASS: could not find ButtonProps interface (may have been refactored)")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
if [ -f "$TARGET" ]; then
    LINE_COUNT=$(wc -l < "$TARGET")
    HAS_BUTTON=$(grep -ci "<button\|<BaseButton\|<Block" "$TARGET" 2>/dev/null || echo "0")
    HAS_GRADIO=$(grep -c "gradio" "$TARGET" 2>/dev/null || echo "0")
    if [ "$LINE_COUNT" -gt 20 ] && [ "$HAS_BUTTON" -ge 1 ] && [ "$HAS_GRADIO" -ge 1 ]; then
        RESULTS[antistub]=1
        echo "TEST antistub: PASS"
    else
        echo "TEST antistub: FAIL"
    fi
else
    echo "TEST antistub: FAIL (file missing)"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_shared': ${WEIGHTS[behavioral_shared]}, 'behavioral_no_props_scale': ${WEIGHTS[behavioral_no_props_scale]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_shared': ${RESULTS[behavioral_shared]}, 'behavioral_no_props_scale': ${RESULTS[behavioral_no_props_scale]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_shared         (${WEIGHTS[behavioral_shared]}): ${RESULTS[behavioral_shared]}"
echo "  behavioral_no_props_scale (${WEIGHTS[behavioral_no_props_scale]}): ${RESULTS[behavioral_no_props_scale]}"
echo "  structural                (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub                  (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
