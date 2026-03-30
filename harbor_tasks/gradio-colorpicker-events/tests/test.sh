#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_no_legacy_events]=0.30
WEIGHTS[behavioral_focus_blur]=0.20
WEIGHTS[behavioral_submit_enter]=0.15
WEIGHTS[structural_native_handlers]=0.15
WEIGHTS[antistub]=0.20

for key in behavioral_no_legacy_events behavioral_focus_blur behavioral_submit_enter structural_native_handlers antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target file exists"

# ---------- PRIMARY 1 (30%): Behavioral - No legacy on: event directives ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Check for legacy Svelte 4 on: directives (on:click, on:mousedown, etc.)
# These should NOT exist -- they must be converted to onclick, onmousedown, etc.
legacy_events = re.findall(r'\bon:(click|mousedown|mouseup|mousemove|change|focus|blur)\b', content)

if len(legacy_events) == 0:
    print("BEHAVIORAL_NO_LEGACY PASS: no legacy on: event directives found")
    sys.exit(0)
else:
    print(f"BEHAVIORAL_NO_LEGACY FAIL: found {len(legacy_events)} legacy on: directives: {legacy_events}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_no_legacy_events]=1
    echo "TEST behavioral_no_legacy_events: PASS"
else
    echo "TEST behavioral_no_legacy_events: FAIL"
fi

# ---------- PRIMARY 2 (20%): Behavioral - Focus/blur handlers on dialog button ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# The dialog button needs onfocus and onblur handlers
has_onfocus = bool(re.search(r'onfocus\s*=\s*\{', content))
has_onblur = bool(re.search(r'onblur\s*=\s*\{', content))

if has_onfocus and has_onblur:
    print("BEHAVIORAL_FOCUS_BLUR PASS: onfocus and onblur handlers present")
    sys.exit(0)
elif has_onfocus or has_onblur:
    print("BEHAVIORAL_FOCUS_BLUR PARTIAL: only one of onfocus/onblur present")
    sys.exit(0)
else:
    print("BEHAVIORAL_FOCUS_BLUR FAIL: neither onfocus nor onblur handlers found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_focus_blur]=1
    echo "TEST behavioral_focus_blur: PASS"
else
    echo "TEST behavioral_focus_blur: FAIL"
fi

# ---------- PRIMARY 3 (15%): Behavioral - Enter key triggers submit ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Check for onkeydown handler that checks for Enter key
has_keydown = bool(re.search(r'onkeydown\s*=\s*\{', content))
has_enter_check = bool(re.search(r'["\']Enter["\']', content))
has_submit = bool(re.search(r'on_submit', content))

if has_keydown and has_enter_check and has_submit:
    print("BEHAVIORAL_SUBMIT PASS: Enter key handler triggers on_submit")
    sys.exit(0)
elif has_enter_check and has_submit:
    print("BEHAVIORAL_SUBMIT PASS: Enter check and on_submit present")
    sys.exit(0)
else:
    missing = []
    if not has_keydown: missing.append("onkeydown")
    if not has_enter_check: missing.append("Enter check")
    if not has_submit: missing.append("on_submit")
    print(f"BEHAVIORAL_SUBMIT FAIL: missing {', '.join(missing)}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_submit_enter]=1
    echo "TEST behavioral_submit_enter: PASS"
else
    echo "TEST behavioral_submit_enter: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): Structural - Native event handlers used ----------
python3 << 'PYEOF'
import sys, re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Check that native Svelte 5 event handlers are present
native_handlers = ["onclick", "onmousedown", "onmousemove", "onmouseup", "onchange"]
found = 0
for handler in native_handlers:
    if re.search(rf'\b{handler}\s*=', content):
        found += 1

if found >= 4:
    print(f"STRUCTURAL PASS: {found}/{len(native_handlers)} native event handlers found")
    sys.exit(0)
else:
    print(f"STRUCTURAL FAIL: only {found}/{len(native_handlers)} native event handlers found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural_native_handlers]=1
    echo "TEST structural_native_handlers: PASS"
else
    echo "TEST structural_native_handlers: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
LINE_COUNT=$(wc -l < "$TARGET")
HAS_COLOR=$(grep -c "color" "$TARGET" 2>/dev/null || echo "0")
HAS_DIALOG=$(grep -c "dialog" "$TARGET" 2>/dev/null || echo "0")
if [ "$LINE_COUNT" -gt 50 ] && [ "$HAS_COLOR" -ge 3 ] && [ "$HAS_DIALOG" -ge 1 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_no_legacy_events': ${WEIGHTS[behavioral_no_legacy_events]}, 'behavioral_focus_blur': ${WEIGHTS[behavioral_focus_blur]}, 'behavioral_submit_enter': ${WEIGHTS[behavioral_submit_enter]}, 'structural_native_handlers': ${WEIGHTS[structural_native_handlers]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_no_legacy_events': ${RESULTS[behavioral_no_legacy_events]}, 'behavioral_focus_blur': ${RESULTS[behavioral_focus_blur]}, 'behavioral_submit_enter': ${RESULTS[behavioral_submit_enter]}, 'structural_native_handlers': ${RESULTS[structural_native_handlers]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_no_legacy_events (${WEIGHTS[behavioral_no_legacy_events]}): ${RESULTS[behavioral_no_legacy_events]}"
echo "  behavioral_focus_blur       (${WEIGHTS[behavioral_focus_blur]}): ${RESULTS[behavioral_focus_blur]}"
echo "  behavioral_submit_enter     (${WEIGHTS[behavioral_submit_enter]}): ${RESULTS[behavioral_submit_enter]}"
echo "  structural_native_handlers  (${WEIGHTS[structural_native_handlers]}): ${RESULTS[structural_native_handlers]}"
echo "  antistub                    (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
