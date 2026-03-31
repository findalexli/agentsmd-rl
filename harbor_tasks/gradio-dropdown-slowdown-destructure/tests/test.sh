#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/dropdown/shared/Dropdown.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[no_array_destructure]=0.35
WEIGHTS[proper_state_management]=0.35
WEIGHTS[selected_indices_derived]=0.10
WEIGHTS[template_usage]=0.10
WEIGHTS[antistub]=0.10

for key in no_array_destructure proper_state_management selected_indices_derived template_usage antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target file exists"

# ---------- CHECK 1 (35%): Fail-to-pass - No array destructuring from $derived.by for input_text/selected_index ----------
# [pr_diff] (0.35): Bug fix removes array destructuring that caused performance issues
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# The buggy pattern that MUST be removed:
# let [input_text, selected_index] = $derived.by(...)
# This exact pattern causes performance issues in Svelte 5

buggy_pattern = re.compile(
    r'let\s*\[\s*[^\]]*input_text[^\]]*,[^\]]*selected_index[^\]]*\]\s*=\s*\$derived\.by',
    re.DOTALL
)

# Also check for any array destructuring involving these specific variables from $derived
alt_buggy = re.compile(
    r'\$derived\.by\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*return\s*\[[^\]]*input_text[^\]]*,[^\]]*selected_index[^\]]*\]',
    re.DOTALL
)

if buggy_pattern.search(content) or alt_buggy.search(content):
    print("FAIL: Array destructuring from $derived.by still present - the core bug is not fixed")
    sys.exit(1)
else:
    print("PASS: No array destructuring from $derived.by for input_text/selected_index")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[no_array_destructure]=1
    echo "TEST no_array_destructure: PASS"
else
    echo "TEST no_array_destructure: FAIL"
fi

# ---------- CHECK 2 (35%): Proper state management for input_text and selected_index ----------
# [pr_diff] (0.35): Variables must be reactively declared with proper Svelte 5 patterns
python3 << 'PYEOF'
import sys, re, ast

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# Extract the script content (remove template)
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
if not script_match:
    print("FAIL: No script tag found")
    sys.exit(1)

script_content = script_match.group(1)

# Remove TypeScript type annotations for parsing
# Simple removal: strip :Type annotations
ts_stripped = re.sub(r':\s*\??\s*\{[^}]+\}', '', script_content)  # object types
# Keep other type annotations minimal - we're doing pattern detection, not full TS parsing

# Check 1: input_text must be declared as a reactive variable
# Acceptable patterns:
# - let input_text = $state(...)
# - let input_text = $derived(...)
# - let input_text: string = $state(...)
# - etc.
input_text_reactive = bool(re.search(r'let\s+input_text\s*(?::\s*\w+\s*)?=\s*\$(?:state|derived)', script_content))

# Check 2: selected_index must be declared as a reactive variable
selected_index_reactive = bool(re.search(r'let\s+selected_index\s*(?::\s*[^=]+)?=\s*\$(?:state|derived)', script_content))

# Check 3: There must be logic that UPDATES these variables based on value/choices changes
# This can be via $effect OR via $derived logic OR via event handlers
# The fix requires these to track external state (value prop and choices)

# Look for evidence the variables respond to changes
has_update_logic = False

# Pattern A: $effect that assigns to these variables
if re.search(r'\$effect\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*input_text\s*=', script_content, re.DOTALL):
    has_update_logic = True

# Pattern B: $derived that computes based on value/choices
if re.search(r'input_text\s*=\s*\$derived\s*\([^)]*value|choices', script_content, re.DOTALL):
    has_update_logic = True

# Pattern C: $derived.by with value/choices reference
if re.search(r'input_text\s*=\s*\$derived\.by\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*value', script_content, re.DOTALL):
    has_update_logic = True

if input_text_reactive and selected_index_reactive and has_update_logic:
    print("PASS: input_text and selected_index properly react to external changes")
    sys.exit(0)
else:
    if not input_text_reactive:
        print("FAIL: input_text not declared with $state or $derived")
    elif not selected_index_reactive:
        print("FAIL: selected_index not declared with $state or $derived")
    else:
        print("FAIL: No logic found that updates variables based on value/choices changes")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[proper_state_management]=1
    echo "TEST proper_state_management: PASS"
else
    echo "TEST proper_state_management: FAIL"
fi

# ---------- CHECK 3 (10%): selected_indices is declared as $derived ----------
# [agent_config] (0.10): Avoid inline computation in template - js/dropdown/shared/Dropdown.svelte
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# Extract script and template
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
script_content = script_match.group(1) if script_match else ""
template_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)

# Check that selected_indices is declared as $derived in script
has_derived_declaration = bool(re.search(r'let\s+selected_indices\s*=\s*\$derived', script_content))

if has_derived_declaration:
    print("PASS: selected_indices is declared as $derived")
    sys.exit(0)
else:
    print("FAIL: selected_indices not declared as $derived")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[selected_indices_derived]=1
    echo "TEST selected_indices_derived: PASS"
else
    echo "TEST selected_indices_derived: FAIL"
fi

# ---------- CHECK 4 (10%): Template uses selected_indices variable, not inline computation ----------
# [pr_diff] (0.10): Template should use {selected_indices} not {selected_index === null ? [] : [selected_index]}
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# Remove script tag to get template
template_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)

# Check for the inline pattern in template that causes performance issues
inline_pattern = re.search(r'selected_index\s*===\s*null\s*\?\s*\[\]\s*:\s*\[selected_index\]', template_content)

# Check that selected_indices is used in template (passed as prop or used directly)
uses_variable = bool(re.search(r'\{selected_indices\}', template_content))

# Check it's passed to DropdownOptions component
passed_to_component = bool(re.search(r'selected_indices\s*=', template_content))

if not inline_pattern and (uses_variable or passed_to_component):
    print("PASS: Template uses selected_indices variable instead of inline computation")
    sys.exit(0)
else:
    if inline_pattern:
        print("FAIL: Template still has inline selected_index computation")
    else:
        print("FAIL: Template doesn't use selected_indices variable")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[template_usage]=1
    echo "TEST template_usage: PASS"
else
    echo "TEST template_usage: FAIL"
fi

# ---------- Anti-stub check (10%) ----------
# [agent_config] (0.10): File must contain substantial implementation - js/dropdown/shared/Dropdown.svelte
LINE_COUNT=$(wc -l < "$TARGET")
HAS_DROPDOWN=$(grep -c "DropdownOptions\|dropdown\|handle_option_selected" "$TARGET" 2>/dev/null || echo "0")
HAS_REACTIVE=$(grep -cE '\$(state|derived|effect|props)' "$TARGET" 2>/dev/null || echo "0")
HAS_LOGIC=$(grep -c "choices\|filtered_indices\|value" "$TARGET" 2>/dev/null || echo "0")

if [ "$LINE_COUNT" -gt 100 ] && [ "$HAS_DROPDOWN" -ge 2 ] && [ "$HAS_REACTIVE" -ge 3 ] && [ "$HAS_LOGIC" -ge 5 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL (lines=$LINE_COUNT, dropdown_refs=$HAS_DROPDOWN, reactive=$HAS_REACTIVE, logic=$HAS_LOGIC)"
fi

# ---------- Gate: Both primary checks must pass ----------
if [ ${RESULTS[no_array_destructure]} -eq 0 ] || [ ${RESULTS[proper_state_management]} -eq 0 ]; then
    echo ""
    echo "=== GATED: Core bug fix checks failed ==="
    # Zero out non-gate checks if core fix not present
    RESULTS[selected_indices_derived]=0
    RESULTS[template_usage]=0
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'no_array_destructure': ${WEIGHTS[no_array_destructure]}, 'proper_state_management': ${WEIGHTS[proper_state_management]}, 'selected_indices_derived': ${WEIGHTS[selected_indices_derived]}, 'template_usage': ${WEIGHTS[template_usage]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'no_array_destructure': ${RESULTS[no_array_destructure]}, 'proper_state_management': ${RESULTS[proper_state_management]}, 'selected_indices_derived': ${RESULTS[selected_indices_derived]}, 'template_usage': ${RESULTS[template_usage]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  no_array_destructure      (${WEIGHTS[no_array_destructure]}): ${RESULTS[no_array_destructure]}"
echo "  proper_state_management   (${WEIGHTS[proper_state_management]}): ${RESULTS[proper_state_management]}"
echo "  selected_indices_derived  (${WEIGHTS[selected_indices_derived]}): ${RESULTS[selected_indices_derived]}"
echo "  template_usage            (${WEIGHTS[template_usage]}): ${RESULTS[template_usage]}"
echo "  antistub                  (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
