#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/dropdown/shared/Dropdown.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_no_destructure]=0.30
WEIGHTS[behavioral_state_vars]=0.25
WEIGHTS[behavioral_derived_indices]=0.15
WEIGHTS[structural_effect_update]=0.10
WEIGHTS[antistub]=0.20

for key in behavioral_no_destructure behavioral_state_vars behavioral_derived_indices structural_effect_update antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target file exists"

# ---------- PRIMARY 1 (30%): Behavioral - No array destructuring from $derived.by ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# The bug pattern: let [input_text, selected_index] = $derived.by(...)
# This should NOT be present after the fix
has_destructure = bool(re.search(r'let\s*\[\s*input_text\s*,\s*selected_index\s*\]\s*=\s*\$derived', content))

if not has_destructure:
    print("BEHAVIORAL_NO_DESTRUCTURE PASS: no array destructuring from $derived")
    sys.exit(0)
else:
    print("BEHAVIORAL_NO_DESTRUCTURE FAIL: still destructuring [input_text, selected_index] from $derived")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_no_destructure]=1
    echo "TEST behavioral_no_destructure: PASS"
else
    echo "TEST behavioral_no_destructure: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - input_text and selected_index are $state() ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

has_input_text_state = bool(re.search(r'let\s+input_text\s*=\s*\$state\(', content))
has_selected_index_state = bool(re.search(r'let\s+selected_index[^=]*=\s*\$state\(', content))

if has_input_text_state and has_selected_index_state:
    print("BEHAVIORAL_STATE PASS: both input_text and selected_index use $state()")
    sys.exit(0)
elif has_input_text_state or has_selected_index_state:
    print("BEHAVIORAL_STATE PARTIAL: one of the variables uses $state()")
    sys.exit(0)
else:
    print("BEHAVIORAL_STATE FAIL: neither input_text nor selected_index uses $state()")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_state_vars]=1
    echo "TEST behavioral_state_vars: PASS"
else
    echo "TEST behavioral_state_vars: FAIL"
fi

# ---------- PRIMARY 3 (15%): Behavioral - selected_indices is $derived, not inline ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# Check that selected_indices is a separate $derived variable
has_derived_indices = bool(re.search(r'let\s+selected_indices\s*=\s*\$derived\(', content))

# Check that the inline pattern is NOT used in template
has_inline_indices = bool(re.search(r'selected_indices=\{selected_index\s*===\s*null', content))

if has_derived_indices and not has_inline_indices:
    print("BEHAVIORAL_DERIVED_INDICES PASS: selected_indices is $derived, not inline")
    sys.exit(0)
elif has_derived_indices:
    print("BEHAVIORAL_DERIVED_INDICES PARTIAL: selected_indices is $derived but inline also exists")
    sys.exit(0)
else:
    print("BEHAVIORAL_DERIVED_INDICES FAIL: selected_indices not found as $derived")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_derived_indices]=1
    echo "TEST behavioral_derived_indices: PASS"
else
    echo "TEST behavioral_derived_indices: FAIL"
fi

# ---------- SUPPLEMENTARY (10%): Structural - $effect updates input_text/selected_index ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/dropdown/shared/Dropdown.svelte") as f:
    content = f.read()

# The fix uses $effect() to update input_text and selected_index
# Look for an $effect block that assigns to input_text
has_effect_with_assignment = bool(re.search(r'\$effect\(\(\)\s*=>\s*\{[^}]*input_text\s*=', content, re.DOTALL))

if has_effect_with_assignment:
    print("STRUCTURAL PASS: $effect updates input_text")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: no $effect found that updates input_text")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_effect_update]=1
    echo "TEST structural_effect_update: PASS"
else
    echo "TEST structural_effect_update: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
LINE_COUNT=$(wc -l < "$TARGET")
HAS_DROPDOWN=$(grep -c "dropdown\|Dropdown" "$TARGET" 2>/dev/null || echo "0")
HAS_CHOICES=$(grep -c "choices" "$TARGET" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -gt 50 ] && [ "$HAS_DROPDOWN" -ge 1 ] && [ "$HAS_CHOICES" -ge 1 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_no_destructure': ${WEIGHTS[behavioral_no_destructure]}, 'behavioral_state_vars': ${WEIGHTS[behavioral_state_vars]}, 'behavioral_derived_indices': ${WEIGHTS[behavioral_derived_indices]}, 'structural_effect_update': ${WEIGHTS[structural_effect_update]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_no_destructure': ${RESULTS[behavioral_no_destructure]}, 'behavioral_state_vars': ${RESULTS[behavioral_state_vars]}, 'behavioral_derived_indices': ${RESULTS[behavioral_derived_indices]}, 'structural_effect_update': ${RESULTS[structural_effect_update]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_no_destructure  (${WEIGHTS[behavioral_no_destructure]}): ${RESULTS[behavioral_no_destructure]}"
echo "  behavioral_state_vars      (${WEIGHTS[behavioral_state_vars]}): ${RESULTS[behavioral_state_vars]}"
echo "  behavioral_derived_indices (${WEIGHTS[behavioral_derived_indices]}): ${RESULTS[behavioral_derived_indices]}"
echo "  structural_effect_update   (${WEIGHTS[structural_effect_update]}): ${RESULTS[structural_effect_update]}"
echo "  antistub                   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
