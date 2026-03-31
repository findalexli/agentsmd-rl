#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[compilation]=0.10
WEIGHTS[no_legacy_events]=0.25
WEIGHTS[focus_blur_handlers]=0.20
WEIGHTS[enter_submit]=0.20
WEIGHTS[native_handlers]=0.15
WEIGHTS[antistub]=0.10

for key in compilation no_legacy_events focus_blur_handlers enter_submit native_handlers antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: File exists ----------
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET not found"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: target file exists"

# ---------- GATE: Valid Svelte syntax (compilation check) ----------
python3 << 'PYEOF'
import sys

# Read and validate basic Svelte structure
with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Must have script and template sections
if "<script" not in content:
    print("COMPILATION FAIL: missing script tag")
    sys.exit(1)

# Check for basic Svelte structure - balanced braces
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces == 0 or close_braces == 0:
    print("COMPILATION FAIL: no code blocks found")
    sys.exit(1)

# Check for unclosed blocks (basic check)
if open_braces < close_braces - 5 or open_braces > close_braces + 5:
    print(f"COMPILATION FAIL: brace imbalance ({open_braces} vs {close_braces})")
    sys.exit(1)

print("COMPILATION PASS: basic structural validity")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[compilation]=1
    echo "TEST compilation: PASS"
else
    echo "TEST compilation: FAIL"
    # Gate: require compilation to get other points
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY 1 (25%): No legacy on: event directives (FAIL-to-PASS) ----------
python3 << 'PYEOF'
import sys
import re
import itertools

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Parse script section separately from template
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
template_content = content
if script_match:
    script_start, script_end = script_match.span()
    template_content = content[:script_start] + content[script_end:]

# Check for legacy Svelte 4 on: directives that would break in Svelte 5
# Events that are commonly used in the original buggy file
legacy_event_pattern = r'\bon:(click|mousedown|mouseup|mousemove|change|focus|blur|keydown|keyup|input|submit)\b'

# Find all matches with line numbers for context
lines = template_content.split('\n')
legacy_events = []
for i, line in enumerate(lines):
    for match in re.finditer(legacy_event_pattern, line):
        # Check if it's in a comment
        comment_start = line.find('<!--')
        comment_end = line.find('-->')
        pos = match.start()
        in_comment = False
        # Simple comment check - refine if needed
        if '<!--' in line[:pos] and '-->' not in line[:pos]:
            in_comment = True
        if not in_comment:
            legacy_events.append((i+1, match.group(1), line.strip()[:60]))

if len(legacy_events) == 0:
    print("NO_LEGACY PASS: no legacy on:event directives found")
    sys.exit(0)
else:
    print(f"NO_LEGACY FAIL: found {len(legacy_events)} legacy on: directives:")
    for line, evt, ctx in legacy_events[:5]:
        print(f"  Line {line}: on:{evt}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[no_legacy_events]=1
    echo "TEST no_legacy_events: PASS"
else
    echo "TEST no_legacy_events: FAIL"
fi

# ---------- PRIMARY 2 (20%): Focus and blur handlers on dialog button ----------
python3 << 'PYEOF'
import sys
import re
import ast

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Extract script to find handler function names
def extract_handler_names(source):
    """Extract names of functions assigned to props like on_focus, on_blur."""
    handlers = {}
    try:
        tree = ast.parse(source)
        # Look for destructuring: {on_focus = () => {}, on_blur = () => {}}
        # This is TypeScript/Svelte, so ast won't fully parse it, but can find patterns
    except:
        pass
    return handlers

# Find the dialog button element and check for onfocus/onblur
# The dialog button has class="dialog-button"

# Match dialog button with attributes spread across lines
button_pattern = r'<button\s+([^>]*\bdialog-button\b[^>]*)>'
button_match = re.search(button_pattern, content, re.DOTALL)

if not button_match:
    print("FOCUS_BLUR FAIL: dialog button not found")
    sys.exit(1)

button_attrs = button_match.group(1)

# Check for onfocus and onblur (native Svelte 5 handlers)
# Accept: onfocus={handler}, onfocus={() => ...}, onfocus={()=>{...}}
onfocus_pattern = r'\bonfocus\s*=\s*\{'
onblur_pattern = r'\bonblur\s*=\s*\{'

has_onfocus = bool(re.search(onfocus_pattern, button_attrs))
has_onblur = bool(re.search(onblur_pattern, button_attrs))

# Also check general content for these handlers in context of dialog-button
# Backup: check if onfocus/onblur exist anywhere and call relevant handlers
general_onfocus = False
general_onblur = False

# Check for patterns like onfocus={on_focus} or onfocus={() => on_focus()}
if re.search(r'\bonfocus\s*=\s*\{\s*on_focus\b', content):
    general_onfocus = True
if re.search(r'\bonblur\s*=\s*\{\s*on_blur\b', content):
    general_onblur = True

# Check for arrow function patterns that call on_focus/on_blur
if re.search(r'\bonfocus\s*=\s*\{[^}]*\(\)\s*=>\s*[^}]*on_focus\b', content):
    general_onfocus = True
if re.search(r'\bonblur\s*=\s*\{[^}]*\(\)\s*=>\s*[^}]*on_blur\b', content):
    general_onblur = True

final_onfocus = has_onfocus or general_onfocus
final_onblur = has_onblur or general_onblur

if final_onfocus and final_onblur:
    print("FOCUS_BLUR PASS: onfocus and onblur handlers found calling prop functions")
    sys.exit(0)
else:
    missing = []
    if not final_onfocus: missing.append("onfocus with on_focus call")
    if not final_onblur: missing.append("onblur with on_blur call")
    print(f"FOCUS_BLUR FAIL: missing {', '.join(missing)}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[focus_blur_handlers]=1
    echo "TEST focus_blur_handlers: PASS"
else
    echo "TEST focus_blur_handlers: FAIL"
fi

# ---------- PRIMARY 3 (20%): Enter key triggers submit ----------
python3 << 'PYEOF'
import sys
import re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Find the text input element (type="text")
# Look for input with bind:value={color_string} or similar

input_pattern = r'<input\s+[^>]*type=["\']text["\'][^>]*>'
inputs = re.findall(input_pattern, content, re.DOTALL)

if not inputs:
    # Try without type="text" (might be default)
    input_pattern = r'<input\s+[^>]*bind:value\s*=\s*\{[^}]*color[^}]*\}'
    inputs = re.findall(input_pattern, content, re.DOTALL)

has_enter_handler = False
has_submit_call = False

# Check for Enter key handling - various valid patterns
enter_patterns = [
    # onkeydown with e.key === "Enter"
    r'\bonkeydown\s*=\s*\{[^}]*["\']Enter["\'][^}]*\}',
    # onkeydown with e.key === 'Enter'
    r"\bonkeydown\s*=\s*\{[^}]*['\"]Enter['\"][^}]*\}",
    # onkeydown with destructured event
    r'\bonkeydown\s*=\s*\{[^}]*\.key\s*===?\s*["\']Enter["\'][^}]*\}',
    # onkeyup with Enter
    r'\bonkeyup\s*=\s*\{[^}]*["\']Enter["\'][^}]*\}',
    # onkeydown with keyCode === 13
    r'\bonkeydown.*keyCode\s*===?\s*13',
    # onkeydown with .keyCode == 13
    r'\bonkeydown.*\.keyCode\s*==?\s*13',
]

for pattern in enter_patterns:
    if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
        has_enter_handler = True
        break

# Check that on_submit is actually called somewhere
# Pattern: on_submit() or on_submit?.()
submit_patterns = [
    r'\bon_submit\s*\(\s*\)',
    r'\bon_submit\?*\.\s*\(\s*\)',
]

for pattern in submit_patterns:
    if re.search(pattern, content):
        has_submit_call = True
        break

# Look for arrow functions that call on_submit
if re.search(r'\(\s*e\s*\)\s*=>\s*\{[^}]*on_submit\s*\(', content):
    has_submit_call = True

if has_enter_handler and has_submit_call:
    print("ENTER_SUBMIT PASS: Enter key handler triggers on_submit")
    sys.exit(0)
else:
    missing = []
    if not has_enter_handler: missing.append("Enter key handler")
    if not has_submit_call: missing.append("on_submit call")
    print(f"ENTER_SUBMIT FAIL: missing {', '.join(missing)}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[enter_submit]=1
    echo "TEST enter_submit: PASS"
else
    echo "TEST enter_submit: FAIL"
fi

# ---------- SUPPLEMENTARY (15%): Native Svelte 5 event handlers used ----------
python3 << 'PYEOF'
import sys
import re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Key native handlers that should exist in a working color picker
# Format: (handler_name, min_count, description)
required_handlers = [
    ('onclick', 1, 'click handler'),
    ('onchange', 1, 'change handler'),
]

bonus_handlers = [
    ('onmousedown', 1, 'mousedown handler'),
    ('onmouseup', 1, 'mouseup handler'),
    ('onmousemove', 1, 'mousemove handler'),
    ('onkeydown', 1, 'keydown handler'),
    ('onfocus', 1, 'focus handler'),
    ('onblur', 1, 'blur handler'),
]

found_required = 0
found_bonus = 0

for handler, min_count, desc in required_handlers:
    # Pattern: handler={...} or handler={() => ...}
    pattern = rf'\b{handler}\s*=\s*\{{'
    matches = len(re.findall(pattern, content))
    if matches >= min_count:
        found_required += 1
    # Check svelte:window handlers too
    window_pattern = rf'<svelte:window[^/]*{handler}\s*='
    if re.search(window_pattern, content):
        found_required += 1

for handler, min_count, desc in bonus_handlers:
    pattern = rf'\b{handler}\s*=\s*\{{'
    matches = len(re.findall(pattern, content))
    if matches >= min_count:
        found_bonus += 1
    # Check svelte:window
    window_pattern = rf'<svelte:window[^/]*{handler}\s*='
    if re.search(window_pattern, content):
        found_bonus += 1

# Must have at least required, gets points for bonus
total_handlers = found_required + found_bonus
if total_handlers >= 3:
    print(f"NATIVE HANDLERS PASS: found {found_required} required, {found_bonus} bonus handlers")
    sys.exit(0)
else:
    print(f"NATIVE HANDLERS FAIL: only found {total_handlers} native handlers (need 3)")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[native_handlers]=1
    echo "TEST native_handlers: PASS"
else
    echo "TEST native_handlers: FAIL"
fi

# ---------- Anti-stub check (10%): Substantial implementation ----------
python3 << 'PYEOF'
import sys
import re

with open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte") as f:
    content = f.read()

# Line count check
lines = content.split('\n')
line_count = len(lines)

# Must have substantial template (not just stub)
template_start = content.find('</script>')
if template_start == -1:
    template_start = content.find('>') + 1 if '<script' in content else 0
template = content[template_start:]

# Count non-comment, non-empty lines in template
template_lines = [l for l in template.split('\n') if l.strip() and not l.strip().startswith('<!--')]
template_line_count = len(template_lines)

# Must have key content indicators
has_dialog = 'dialog' in content.lower() or 'dialog_open' in content
has_color = content.lower().count('color') >= 3
has_button = content.count('<button') >= 1
has_input = '<input' in content

# AST depth check - look for actual logic
# Count function definitions, effect blocks, variable assignments in script
script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
script_content = script_match.group(1) if script_match else ""

# Count "/" for meaningful expressions (rough proxy)
expr_indicators = [
    'function ',
    '=> {',
    '$effect',
    '$state',
    '$props',
    '.',
]
meaningful_count = 0
for indicator in expr_indicators:
    meaningful_count += script_content.count(indicator)

score = 0
if line_count > 100: score += 1
if template_line_count > 20: score += 1
if has_dialog: score += 1
if has_color: score += 1
if has_button and has_input: score += 1
if meaningful_count > 10: score += 1

if score >= 5:
    print(f"ANTISTUB PASS: score {score}/6")
    sys.exit(0)
else:
    print(f"ANTISTUB FAIL: score {score}/6 (looks like stub)")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'compilation': ${WEIGHTS[compilation]}, 'no_legacy_events': ${WEIGHTS[no_legacy_events]}, 'focus_blur_handlers': ${WEIGHTS[focus_blur_handlers]}, 'enter_submit': ${WEIGHTS[enter_submit]}, 'native_handlers': ${WEIGHTS[native_handlers]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'compilation': ${RESULTS[compilation]}, 'no_legacy_events': ${RESULTS[no_legacy_events]}, 'focus_blur_handlers': ${RESULTS[focus_blur_handlers]}, 'enter_submit': ${RESULTS[enter_submit]}, 'native_handlers': ${RESULTS[native_handlers]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  compilation           (${WEIGHTS[compilation]}): ${RESULTS[compilation]}"
echo "  no_legacy_events      (${WEIGHTS[no_legacy_events]}): ${RESULTS[no_legacy_events]}"
echo "  focus_blur_handlers   (${WEIGHTS[focus_blur_handlers]}): ${RESULTS[focus_blur_handlers]}"
echo "  enter_submit          (${WEIGHTS[enter_submit]}): ${RESULTS[enter_submit]}"
echo "  native_handlers       (${WEIGHTS[native_handlers]}): ${RESULTS[native_handlers]}"
echo "  antistub              (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
