#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/button/Index.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[gate]=0.00
WEIGHTS[f2p_scale_binding]=0.40
WEIGHTS[f2p_props_removal]=0.25
WEIGHTS[structural_interface]=0.15
WEIGHTS[antistub]=0.20

for key in gate f2p_scale_binding f2p_props_removal structural_interface antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists and is valid Svelte ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# Check for basic file validity (has script tag)
if ! grep -q '<script' "$TARGET"; then
    echo "GATE FAIL: No script tag found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

RESULTS[gate]=1
echo "GATE PASS: Valid Svelte file found"

# ---------- FAIL-TO-PASS 1 (40%): scale binding uses gradio.shared, not gradio.props ----------
# [pr_diff] (0.40): Button reads scale from gradio.shared.scale not gradio.props.scale
python3 << 'PYEOF'
import sys
import re

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# Remove comments to avoid false positives from comment injection
# This handles both // and /* */ style comments
content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)

# STRONG CHECK: Parse Button component invocation to find scale= binding
# Look for <Button ... scale={...} ...> pattern
button_tags = re.findall(r'<Button\s+([^>]*)/?>', content_no_comments, re.DOTALL)

found_correct_scale = False
found_wrong_scale = False

for tag_content in button_tags:
    # Find scale= assignment within Button tag
    scale_match = re.search(r'scale\s*=\s*\{([^}]+)\}', tag_content)
    if scale_match:
        scale_val = scale_match.group(1).strip()
        # Check if it uses gradio.shared.scale (correct)
        if re.match(r'^gradio\.shared\.scale$', scale_val):
            found_correct_scale = True
        # Check if it uses gradio.props.scale (buggy)
        elif re.match(r'^gradio\.props\.scale$', scale_val):
            found_wrong_scale = True
        # Check for destructured or aliased usage - accept if not props.scale
        elif 'gradio.props.scale' not in scale_val:
            # Alternative valid approaches (destructured, etc.)
            found_correct_scale = True

if found_wrong_scale:
    print("F2P_SCALE_BINDING FAIL: Still using gradio.props.scale (bug not fixed)")
    sys.exit(1)
elif found_correct_scale:
    print("F2P_SCALE_BINDING PASS: scale correctly bound to gradio.shared.scale or equivalent")
    sys.exit(0)
else:
    print("F2P_SCALE_BINDING FAIL: Could not find scale binding in Button component")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[f2p_scale_binding]=1
    echo "TEST f2p_scale_binding: PASS"
else
    echo "TEST f2p_scale_binding: FAIL"
fi

# ---------- FAIL-TO-PASS 2 (25%): scale removed from ButtonProps interface ----------
# [pr_diff] (0.25): scale field removed from ButtonProps TypeScript interface
python3 << 'PYEOF'
import sys
import re

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# Remove comments
content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)

# Find interface ButtonProps or type ButtonProps definition
# Try interface first
interface_match = re.search(r'interface\s+ButtonProps\s*\{([^}]*)\}', content_no_comments, re.DOTALL)
type_match = re.search(r'type\s+ButtonProps\s*=\s*\{([^}]*)\}', content_no_comments, re.DOTALL)

props_block = None
if interface_match:
    props_block = interface_match.group(1)
elif type_match:
    props_block = type_match.group(1)

if props_block is None:
    # Check if interface was renamed or removed via destructuring pattern
    # Look for: let { ... }: { ... } destructuring with scale
    destruct_match = re.search(r'let\s*\{[^}]*\}\s*:\s*\{([^}]*)\}', content_no_comments, re.DOTALL)
    if destruct_match:
        props_block = destruct_match.group(1)
    else:
        # No interface/type found - could mean complete refactor
        # Check there's no other place where scale is defined as a prop
        if re.search(r'\bscale\s*:\s*(number|float|int)', content_no_comments):
            print("F2P_PROPS_REMOVAL FAIL: scale still typed as a prop somewhere")
            sys.exit(1)
        else:
            print("F2P_PROPS_REMOVAL PASS: No ButtonProps with scale found (may be refactored)")
            sys.exit(0)

# Check if scale is in the props block (as a property definition, not a value)
# Look for scale: type pattern
if re.search(r'\bscale\s*:', props_block):
    print("F2P_PROPS_REMOVAL FAIL: scale still present in props type definition")
    sys.exit(1)
else:
    print("F2P_PROPS_REMOVAL PASS: scale removed from ButtonProps")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[f2p_props_removal]=1
    echo "TEST f2p_props_removal: PASS"
else
    echo "TEST f2p_props_removal: FAIL"
fi

# ---------- STRUCTURAL (15%): Validate interface structure is reasonable ----------
# [agent_config] (0.15): ButtonProps interface should exist and have other required fields
python3 << 'PYEOF'
import sys
import re

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# Remove comments
content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)

# Check for reasonable ButtonProps definition
interface_match = re.search(r'interface\s+ButtonProps\s*\{([^}]*)\}', content_no_comments, re.DOTALL)
type_match = re.search(r'type\s+ButtonProps\s*=\s*\{([^}]*)\}', content_no_comments, re.DOTALL)

props_content = None
if interface_match:
    props_content = interface_match.group(1)
elif type_match:
    props_content = type_match.group(1)

if props_content:
    # Count property definitions (lines with : type)
    prop_lines = [l for l in props_content.split('\n') if re.search(r'\w+\s*:', l)]
    if len(prop_lines) >= 3:
        print("STRUCTURAL_INTERFACE PASS: ButtonProps has reasonable structure")
        sys.exit(0)
    else:
        print("STRUCTURAL_INTERFACE FAIL: ButtonProps has too few properties (< 3)")
        sys.exit(1)
else:
    # Check for destructuring pattern as alternative
    destruct_match = re.search(r'let\s*\{[^}]*props[^}]*\}\s*:\s*\{([^}]+)\}', content_no_comments, re.DOTALL)
    if destruct_match:
        print("STRUCTURAL_INTERFACE PASS: Props defined via destructuring pattern")
        sys.exit(0)
    else:
        print("STRUCTURAL_INTERFACE FAIL: No recognizable ButtonProps definition")
        sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_interface]=1
    echo "TEST structural_interface: PASS"
else
    echo "TEST structural_interface: FAIL"
fi

# ---------- Anti-stub check (20%): File has meaningful implementation ----------
# [agent_config] (0.20): File should have realistic Svelte component structure
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/js/button/Index.svelte"

with open(TARGET) as f:
    content = f.read()

# Gate: must pass gate first
if len(content) < 100:
    print("ANTISTUB FAIL: File too small (< 100 chars)")
    sys.exit(1)

# Must have actual Button component usage
if '<Button' not in content:
    print("ANTISTUB FAIL: No Button component usage found")
    sys.exit(1)

# Must have gradio usage
if 'gradio' not in content:
    print("ANTISTUB FAIL: No gradio reference found")
    sys.exit(1)

# Must have script section with meaningful content
import re
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if not script_match:
    print("ANTISTUB FAIL: No script section found")
    sys.exit(1)

script_content = script_match.group(1)
if len(script_content.strip()) < 50:
    print("ANTISTUB FAIL: Script section too small")
    sys.exit(1)

# Check for actual props handling (not just empty definitions)
if 'props' not in script_content and 'Props' not in script_content:
    print("ANTISTUB FAIL: No props handling in script")
    sys.exit(1)

print("ANTISTUB PASS: File has meaningful component implementation")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'gate': ${WEIGHTS[gate]}, 'f2p_scale_binding': ${WEIGHTS[f2p_scale_binding]}, 'f2p_props_removal': ${WEIGHTS[f2p_props_removal]}, 'structural_interface': ${WEIGHTS[structural_interface]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'gate': ${RESULTS[gate]}, 'f2p_scale_binding': ${RESULTS[f2p_scale_binding]}, 'f2p_props_removal': ${RESULTS[f2p_props_removal]}, 'structural_interface': ${RESULTS[structural_interface]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  gate                      (${WEIGHTS[gate]}): ${RESULTS[gate]}"
echo "  f2p_scale_binding         (${WEIGHTS[f2p_scale_binding]}): ${RESULTS[f2p_scale_binding]}"
echo "  f2p_props_removal         (${WEIGHTS[f2p_props_removal]}): ${RESULTS[f2p_props_removal]}"
echo "  structural_interface      (${WEIGHTS[structural_interface]}): ${RESULTS[structural_interface]}"
echo "  antistub                  (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
