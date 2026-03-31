#!/usr/bin/env bash
set +e

SCORE=0
FILE="js/atoms/src/Block.svelte"

# ─── GATE: File exists and is valid Svelte ───
# [pr_diff] (gate): Block.svelte must exist and be valid Svelte
if [ ! -f "$FILE" ]; then
    echo "GATE FAIL: $FILE not found"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! grep -q '<script' "$FILE" || ! grep -q '<style>' "$FILE"; then
    echo "GATE FAIL: $FILE is not a valid Svelte component"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ─── Check 1 (0.30): Core bug — hide-container must NOT use CSS variable to zero border ───
# [pr_diff] (0.30): The root cause is --block-border-width: 0 in .hide-container which
# inherits to children via CSS custom property cascading. Any correct fix must stop this.
CHECK1=$(python3 -c "
import re, sys

with open('$FILE') as f:
    content = f.read()

style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print('NO_STYLE'); sys.exit(0)
style = style_match.group(1)

hide_re = re.compile(r'\.hide-container:not\(\.fullscreen\)\s*\{([^}]*)\}', re.DOTALL)
m = hide_re.search(style)
if not m:
    print('NO_RULE'); sys.exit(0)

rule_body = m.group(1)

# Must NOT set --block-border-width CSS custom property (causes inheritance to children)
if re.search(r'--block-border-width\s*:', rule_body):
    print('STILL_HAS_CSS_VAR')
else:
    print('OK')
")
if [ "$CHECK1" = "OK" ]; then
    SCORE=$(echo "$SCORE + 0.30" | bc)
    echo "PASS (0.30): .hide-container does not use --block-border-width CSS variable"
else
    echo "FAIL (0.30): .hide-container still uses --block-border-width CSS variable ($CHECK1)"
fi

# ─── Check 2 (0.30): hide-container must zero border directly ───
# [pr_diff] (0.30): The fix should zero the border on .hide-container using a direct
# CSS property. Accept border-width:0, border:none, border:0, border-width:0px.
CHECK2=$(python3 -c "
import re, sys

with open('$FILE') as f:
    content = f.read()

style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print('NO_STYLE'); sys.exit(0)
style = style_match.group(1)

hide_re = re.compile(r'\.hide-container:not\(\.fullscreen\)\s*\{([^}]*)\}', re.DOTALL)
m = hide_re.search(style)
if not m:
    print('NO_RULE'); sys.exit(0)

rule_body = m.group(1)

# Accept multiple valid CSS approaches to zero the border:
# - border-width: 0 (gold patch)
# - border: none (common shorthand)
# - border: 0 / border: 0px (another shorthand)
# Use negative lookbehind to avoid matching --block-border-width
has_direct_zero = (
    bool(re.search(r'(?<!\-)border-width\s*:\s*0', rule_body)) or
    bool(re.search(r'(?<!\-)border\s*:\s*none', rule_body)) or
    bool(re.search(r'(?<!\-)border\s*:\s*0(?:px)?\s*[;\n}]', rule_body))
)

if has_direct_zero:
    print('OK')
else:
    print('NO_DIRECT_ZERO')
")
if [ "$CHECK2" = "OK" ]; then
    SCORE=$(echo "$SCORE + 0.30" | bc)
    echo "PASS (0.30): .hide-container zeros border via direct CSS property"
else
    echo "FAIL (0.30): .hide-container does not directly zero border ($CHECK2)"
fi

# ─── Check 3 (0.15): Non-hidden blocks must retain border-width via non-inheriting path ───
# [pr_diff] (0.15): After the fix, normal blocks must still get border-width from
# somewhere that doesn't rely on the broken CSS variable inheritance. Accepts:
# A) .block CSS class has border-width (gold patch — moved from inline to class)
# B) inline style:border-width still present AND hide-container no longer uses CSS var
#    (minimal fix — just change hide-container, keep inline style)
# Buggy code fails because inline style IS present but hide-container still uses CSS var.
CHECK3=$(python3 -c "
import re, sys

with open('$FILE') as f:
    content = f.read()

style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
style = style_match.group(1) if style_match else ''

# Approach A: .block CSS class provides border-width
block_re = re.compile(r'(?<!\.)\.block\s*\{([^}]*)\}', re.DOTALL)
block_m = block_re.search(style)
block_has_bw = False
if block_m:
    block_body = block_m.group(1)
    block_has_bw = bool(re.search(r'(?<!\-)border-width\s*:', block_body))

# Approach B: inline style still present AND CSS var inheritance is fixed
has_inline_bw = bool(re.search(r'style:border-width', content))
hide_re = re.compile(r'\.hide-container:not\(\.fullscreen\)\s*\{([^}]*)\}', re.DOTALL)
hide_m = hide_re.search(style)
css_var_fixed = True
if hide_m:
    css_var_fixed = not bool(re.search(r'--block-border-width\s*:', hide_m.group(1)))

approach_b = has_inline_bw and css_var_fixed

if block_has_bw or approach_b:
    print('OK')
else:
    print('NO_SAFE_BORDER_SOURCE')
")
if [ "$CHECK3" = "OK" ]; then
    SCORE=$(echo "$SCORE + 0.15" | bc)
    echo "PASS (0.15): Non-hidden blocks have border-width via non-inheriting path"
else
    echo "FAIL (0.15): Non-hidden blocks lack safe border-width source ($CHECK3)"
fi

# ─── Check 4 (0.10): Pass-to-pass — .block CSS preserves essential properties ───
# [pr_diff] (0.10): Regression check that .block class retains its styling
CHECK4=$(python3 -c "
import re, sys

with open('$FILE') as f:
    content = f.read()

style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print('NO_STYLE'); sys.exit(0)
style = style_match.group(1)

block_re = re.compile(r'(?<!\.)\.block\s*\{([^}]*)\}', re.DOTALL)
m = block_re.search(style)
if not m:
    print('NO_BLOCK_RULE'); sys.exit(0)

body = m.group(1)
required = ['box-shadow', 'border-color', 'border-radius', 'background']
missing = [p for p in required if p not in body]
if missing:
    print('MISSING:' + ','.join(missing))
else:
    print('OK')
")
if [ "$CHECK4" = "OK" ]; then
    SCORE=$(echo "$SCORE + 0.10" | bc)
    echo "PASS (0.10): .block CSS preserves essential properties"
else
    echo "FAIL (0.10): .block CSS missing properties ($CHECK4)"
fi

# ─── Check 5 (0.10): Pass-to-pass — hide-container preserves its other resets ───
# [pr_diff] (0.10): The hide-container rule must keep its other CSS resets intact
CHECK5=$(python3 -c "
import re, sys

with open('$FILE') as f:
    content = f.read()

style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
if not style_match:
    print('NO_STYLE'); sys.exit(0)
style = style_match.group(1)

hide_re = re.compile(r'\.hide-container:not\(\.fullscreen\)\s*\{([^}]*)\}', re.DOTALL)
m = hide_re.search(style)
if not m:
    print('NO_RULE'); sys.exit(0)

body = m.group(1)
required = ['margin', 'box-shadow', 'background', 'padding', 'overflow']
missing = [p for p in required if p not in body]
if missing:
    print('MISSING:' + ','.join(missing))
else:
    print('OK')
")
if [ "$CHECK5" = "OK" ]; then
    SCORE=$(echo "$SCORE + 0.10" | bc)
    echo "PASS (0.10): hide-container preserves other CSS resets"
else
    echo "FAIL (0.10): hide-container missing CSS resets ($CHECK5)"
fi

# ─── Check 6 (0.05): Config — style consistency ───
# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:45
CHECK6=0
grep -q '<script' "$FILE" && grep -q '</script>' "$FILE" && \
grep -q '<style>' "$FILE" && grep -q '</style>' "$FILE" && \
grep -q 'class:hide-container' "$FILE" && CHECK6=1
if [ "$CHECK6" = "1" ]; then
    SCORE=$(echo "$SCORE + 0.05" | bc)
    echo "PASS (0.05): Svelte component structure preserved"
else
    echo "FAIL (0.05): Svelte component structure broken"
fi

# ─── Summary ───
echo ""
echo "Score: $SCORE / 1.00"
echo "$SCORE" > /logs/verifier/reward.txt

# Detailed breakdown for reward.json
python3 -c "
import json
score = float('$SCORE')
json.dump({
    'reward': score,
    'behavioral': min(score, 0.75),
    'regression': max(0, min(score - 0.75, 0.20)),
    'config': max(0, min(score - 0.95, 0.05)),
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
