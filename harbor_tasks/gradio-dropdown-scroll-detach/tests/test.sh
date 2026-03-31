#!/usr/bin/env bash
set +e

REWARD=0
FILE="/workspace/gradio/js/dropdown/shared/DropdownOptions.svelte"

echo "=== Gradio Dropdown Scroll Detach Tests ==="

add() { REWARD=$(python3 -c "print(round($REWARD + $1, 2))"); }

# ---------- GATE: file must exist ----------
if [ ! -f "$FILE" ]; then
    echo "GATE FAIL: $FILE does not exist"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: File exists"

# ---------- FAIL-TO-PASS: buggy bare declarations removed + $state added ----------
# Each check requires BOTH: (1) buggy bare declaration is gone, (2) variable uses $state.
# This prevents gaming via deletion AND ensures the actual fix is present.

# [pr_diff] (0.20): distance_from_top must be reactive
# Buggy code: `let distance_from_top: number;` (bare, non-reactive)
# Fixed: any line with `distance_from_top` and `$state` in a let declaration
BUGGY_DFT=$(grep -cP '^\s*let\s+distance_from_top\s*:\s*\w+\s*;' "$FILE" || true)
FIXED_DFT=$(grep -cP '^\s*let\s+distance_from_top\b.*\$state' "$FILE" || true)
if [ "$BUGGY_DFT" -eq 0 ] && [ "$FIXED_DFT" -gt 0 ]; then
    echo "PASS (0.20): distance_from_top is reactive (bug gone + \$state present)"
    add 0.20
else
    echo "FAIL (0.20): distance_from_top not fixed (buggy=$BUGGY_DFT, \$state=$FIXED_DFT)"
fi

# [pr_diff] (0.20): distance_from_bottom must be reactive
BUGGY_DFB=$(grep -cP '^\s*let\s+distance_from_bottom\s*:\s*\w+\s*;' "$FILE" || true)
FIXED_DFB=$(grep -cP '^\s*let\s+distance_from_bottom\b.*\$state' "$FILE" || true)
if [ "$BUGGY_DFB" -eq 0 ] && [ "$FIXED_DFB" -gt 0 ]; then
    echo "PASS (0.20): distance_from_bottom is reactive (bug gone + \$state present)"
    add 0.20
else
    echo "FAIL (0.20): distance_from_bottom not fixed (buggy=$BUGGY_DFB, \$state=$FIXED_DFB)"
fi

# [pr_diff] (0.20): input_height must be reactive
BUGGY_IH=$(grep -cP '^\s*let\s+input_height\s*:\s*\w+\s*;' "$FILE" || true)
FIXED_IH=$(grep -cP '^\s*let\s+input_height\b.*\$state' "$FILE" || true)
if [ "$BUGGY_IH" -eq 0 ] && [ "$FIXED_IH" -gt 0 ]; then
    echo "PASS (0.20): input_height is reactive (bug gone + \$state present)"
    add 0.20
else
    echo "FAIL (0.20): input_height not fixed (buggy=$BUGGY_IH, \$state=$FIXED_IH)"
fi

# ---------- PASS-TO-PASS: existing reactive variables and functions intact ----------

# [pr_diff] (0.05): input_width must remain reactive ($state was already used pre-fix)
if grep -qP '^\s*let\s+input_width\b.*\$state' "$FILE"; then
    echo "PASS (0.05): input_width still reactive"
    add 0.05
else
    echo "FAIL (0.05): input_width reactivity broken"
fi

# [pr_diff] (0.05): calculate_window_distance function exists
if grep -q 'function calculate_window_distance' "$FILE"; then
    echo "PASS (0.05): calculate_window_distance exists"
    add 0.05
else
    echo "FAIL (0.05): calculate_window_distance missing"
fi

# [pr_diff] (0.05): scroll_listener function exists
if grep -q 'function scroll_listener' "$FILE"; then
    echo "PASS (0.05): scroll_listener exists"
    add 0.05
else
    echo "FAIL (0.05): scroll_listener missing"
fi

# [pr_diff] (0.05): $effect block must still be present (it consumes the reactive vars)
if grep -qP '\$effect' "$FILE"; then
    echo "PASS (0.05): \$effect block present"
    add 0.05
else
    echo "FAIL (0.05): \$effect block missing"
fi

# [pr_diff] (0.05): dropdown options list rendering intact (ul element with options)
if grep -q 'bind:this={listElement}' "$FILE" || grep -q '<ul' "$FILE"; then
    echo "PASS (0.05): dropdown list element rendering intact"
    add 0.05
else
    echo "FAIL (0.05): dropdown list element missing"
fi

# ---------- ANTI-STUB ----------

# [pr_diff] (0.05): File has meaningful content (>50 lines)
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -gt 50 ]; then
    echo "PASS (0.05): File has $LINE_COUNT lines (not stubbed)"
    add 0.05
else
    echo "FAIL (0.05): File only has $LINE_COUNT lines (likely stubbed)"
fi

# [pr_diff] (0.05): File has multiple function definitions (not gutted)
FUNC_COUNT=$(grep -cP '^\s*function\s+\w+' "$FILE" || true)
if [ "$FUNC_COUNT" -ge 2 ]; then
    echo "PASS (0.05): File has $FUNC_COUNT functions (not gutted)"
    add 0.05
else
    echo "FAIL (0.05): File only has $FUNC_COUNT functions (likely gutted)"
fi

# ---------- Summary ----------
echo ""
echo "Score: $REWARD / 1.0"
echo "$REWARD" > /logs/verifier/reward.txt

# JSON output
python3 -c "
import json
r = $REWARD
json.dump({
    'reward': r,
    'behavioral': min(r, 0.60),
    'regression': min(max(r - 0.60, 0), 0.30),
    'config': 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
