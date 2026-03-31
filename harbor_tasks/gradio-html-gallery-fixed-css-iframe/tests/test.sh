#!/usr/bin/env bash
set +e

REPO="/workspace/gradio"
UTILS="$REPO/js/_website/src/routes/custom-components/html-gallery/utils.ts"
PAGE="$REPO/js/_website/src/routes/custom-components/html-gallery/+page.svelte"
ENTRY="$REPO/js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte"
GUIDE="$REPO/guides/03_building-with-blocks/06_custom-HTML-components.md"
REWARD=0

mkdir -p /logs/verifier

# === GATE: Target files must exist ===
if [ ! -f "$UTILS" ]; then
    echo "GATE FAIL: utils.ts missing"
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi

# Helper: strip TS type annotations from utils.ts so Node can execute it
# Replaces import with mock, strips type annotations, removes export keywords
strip_ts() {
    node -e "
const fs = require('fs');
let src = fs.readFileSync('$UTILS', 'utf8');

// Remove all import lines
src = src.replace(/^import\b.*$/gm, '');
// Remove 'export' keyword but keep the rest
src = src.replace(/^export\s+/gm, '');
// Remove TS return type annotations on functions: ): boolean { -> ) {
src = src.replace(/\)\s*:\s*[a-zA-Z<>\[\]|{},\s]+\{/g, ') {');
// Remove TS parameter type annotations: param: Type -> param
// Handle complex types like Record<string, any>, {key: val}, string | undefined
src = src.replace(/(\w)\s*:\s*(string|boolean|number|void|null|undefined|Record<[^>]*>|\{[^}]*\}|HTMLDivElement)(\s*\|\s*(string|boolean|number|void|null|undefined))*/g, '\$1');
// Handle remaining TS-specific: 'as' casts, generics on calls
src = src.replace(/\bas\s+\w+/g, '');

// Provide mock for themeCSS
src = 'const themeCSS = \"body { margin: 0; }\";\n' + src;

process.stdout.write(src);
" 2>/dev/null
}

# ============================================================
# FAIL-TO-PASS BEHAVIORAL TESTS (0.65 total)
# These call the actual functions and check behavior.
# On buggy code: needs_iframe/build_srcdoc don't exist → tests fail.
# On correct fix: functions exist and behave correctly.
# ============================================================

echo "=== Fail-to-pass: needs_iframe function ==="

# [pr_diff] (0.20): needs_iframe detects position:fixed CSS
RESULT=$(node -e "
$(strip_ts)

if (typeof needs_iframe !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

// Core behavioral test: position:fixed must be detected
const tests = [
    ['div { position: fixed; top: 0; }', true],
    ['div { position:fixed; left: 0; }', true],
    ['.overlay { POSITION : FIXED; }', true],
    ['div { position:  fixed; }', true],
];

let pass = true;
for (const [input, expected] of tests) {
    const result = needs_iframe(input);
    if (result !== expected) {
        console.log('FAIL:' + input + ' expected ' + expected + ' got ' + result);
        pass = false;
    }
}
console.log(pass ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: needs_iframe detects position:fixed variations"
    REWARD=$(python3 -c "print($REWARD + 0.20)")
else
    echo "FAIL: needs_iframe position:fixed detection ($RESULT)"
fi

# [pr_diff] (0.10): needs_iframe returns false for non-fixed CSS
RESULT=$(node -e "
$(strip_ts)

if (typeof needs_iframe !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

const tests = [
    ['div { position: relative; margin: 10px; }', false],
    ['div { position: absolute; top: 0; }', false],
    ['div { position: static; }', false],
    ['.box { display: flex; color: red; }', false],
    ['', false],
];

let pass = true;
for (const [input, expected] of tests) {
    const result = needs_iframe(input);
    if (result !== expected) {
        console.log('FAIL:' + input + ' expected ' + expected + ' got ' + result);
        pass = false;
    }
}
console.log(pass ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: needs_iframe returns false for non-fixed CSS"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: needs_iframe false-negative check ($RESULT)"
fi

# [pr_diff] (0.05): needs_iframe handles undefined/null without crashing
RESULT=$(node -e "
$(strip_ts)

if (typeof needs_iframe !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

try {
    const r1 = needs_iframe(undefined);
    const r2 = needs_iframe(null);
    const r3 = needs_iframe('');
    if (r1 === false && r2 === false && r3 === false) {
        console.log('PASS');
    } else {
        console.log('FAIL: expected false for falsy inputs');
    }
} catch(e) {
    console.log('FAIL: crashed on falsy input: ' + e.message);
}
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: needs_iframe handles falsy input gracefully"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: needs_iframe falsy input handling ($RESULT)"
fi

echo ""
echo "=== Fail-to-pass: build_srcdoc function ==="

# [pr_diff] (0.15): build_srcdoc produces valid HTML document with essential structure
RESULT=$(node -e "
$(strip_ts)

if (typeof build_srcdoc !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

const component = {
    html_template: '<div>\${value}</div>',
    css_template: 'div { position: fixed; top: 0; }',
    js_on_load: 'console.log(\"loaded\")',
    head: '<link rel=\"stylesheet\" href=\"test.css\">',
    default_props: { value: 'Hello' },
};
const props = { value: 'Hello' };

const html = build_srcdoc(component, props, false);

if (typeof html !== 'string') {
    console.log('FAIL: build_srcdoc did not return a string');
    process.exit(0);
}

// Must be a complete HTML document
const checks = [
    [/<!doctype html>/i.test(html), 'has DOCTYPE'],
    [/<html/i.test(html), 'has <html>'],
    [/<head>/i.test(html), 'has <head>'],
    [/<body>/i.test(html), 'has <body>'],
    [/<script>/i.test(html), 'has <script>'],
    [html.includes('Hello'), 'rendered template with props'],
];

let pass = true;
for (const [ok, desc] of checks) {
    if (!ok) {
        console.log('FAIL: ' + desc);
        pass = false;
    }
}
console.log(pass ? 'PASS' : 'FAIL');
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: build_srcdoc produces complete HTML document"
    REWARD=$(python3 -c "print($REWARD + 0.15)")
else
    echo "FAIL: build_srcdoc HTML structure ($RESULT)"
fi

# [pr_diff] (0.05): build_srcdoc adds dark class when dark=true
RESULT=$(node -e "
$(strip_ts)

if (typeof build_srcdoc !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

const component = {
    html_template: '<div>test</div>',
    css_template: 'div { color: red; }',
    default_props: {},
};

const darkHtml = build_srcdoc(component, {}, true);
const lightHtml = build_srcdoc(component, {}, false);

// Dark mode: html element should have dark indication (class, data-attr, etc.)
const hasDarkIndicator = /class=\"[^\"]*dark[^\"]*\"/.test(darkHtml) || /data-theme=\"dark\"/.test(darkHtml);
const lightHasDark = /class=\"[^\"]*dark[^\"]*\"/.test(lightHtml);

if (hasDarkIndicator && !lightHasDark) {
    console.log('PASS');
} else {
    console.log('FAIL: dark=' + hasDarkIndicator + ' light_clean=' + !lightHasDark);
}
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: build_srcdoc dark mode support"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: build_srcdoc dark mode ($RESULT)"
fi

# [pr_diff] (0.10): build_srcdoc escapes </script in JS content to prevent injection
RESULT=$(node -e "
$(strip_ts)

if (typeof build_srcdoc !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

const component = {
    html_template: '<div>test</div>',
    css_template: 'div { color: red; }',
    js_on_load: 'var x = \"</script><script>alert(1)</script>\";',
    default_props: { payload: '</script>' },
};
const props = { payload: '</script>' };

const html = build_srcdoc(component, props, false);

// The output should NOT contain a literal </script> inside the <script> block
// (except the actual closing </script> tag). Check that the JS content is escaped.
// Split on <script> and </script> to find the script body
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/i);
if (!scriptMatch) {
    console.log('FAIL: no script block found');
    process.exit(0);
}
const scriptBody = scriptMatch[1];
// The script body should not contain literal </script (unescaped)
if (scriptBody.includes('</script')) {
    console.log('FAIL: unescaped </script found in script body');
} else {
    console.log('PASS');
}
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: build_srcdoc escapes </script injection"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: build_srcdoc script escaping ($RESULT)"
fi

echo ""
echo "=== Svelte component behavioral checks ==="

# [pr_diff] (0.10): Svelte components have iframe conditional rendering path
# We check that both files import/use needs_iframe and have an iframe element.
# This is structural (can't run Svelte) but tests the integration, not implementation details.
PAGE_IFRAME=0
ENTRY_IFRAME=0

# Check PAGE: must have iframe element AND conditional logic using needs_iframe
if [ -f "$PAGE" ]; then
    PAGE_SRC=$(cat "$PAGE")
    # Must have an <iframe that's used for component rendering (not just any iframe)
    if echo "$PAGE_SRC" | grep -q '<iframe' && echo "$PAGE_SRC" | grep -q 'needs_iframe\|use_iframe\|srcdoc'; then
        PAGE_IFRAME=1
    fi
fi

# Check ENTRY: same
if [ -f "$ENTRY" ]; then
    ENTRY_SRC=$(cat "$ENTRY")
    if echo "$ENTRY_SRC" | grep -q '<iframe' && echo "$ENTRY_SRC" | grep -q 'needs_iframe\|use_iframe\|srcdoc'; then
        ENTRY_IFRAME=1
    fi
fi

if [ "$PAGE_IFRAME" -eq 1 ] && [ "$ENTRY_IFRAME" -eq 1 ]; then
    echo "PASS: Both Svelte components use iframe rendering"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
elif [ "$PAGE_IFRAME" -eq 1 ] || [ "$ENTRY_IFRAME" -eq 1 ]; then
    echo "PARTIAL: Only one Svelte component has iframe rendering"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: No iframe rendering in Svelte components"
fi

# [pr_diff] (0.05): Components with @children slot get child content
# Check that both files have a rendering branch for templates with @children
CHILDREN_OK=0
if [ -f "$PAGE" ] && [ -f "$ENTRY" ]; then
    PAGE_CHILDREN=$(grep -c 'children' "$PAGE" 2>/dev/null || echo "0")
    ENTRY_CHILDREN=$(grep -c 'children' "$ENTRY" 2>/dev/null || echo "0")
    if [ "$PAGE_CHILDREN" -ge 1 ] && [ "$ENTRY_CHILDREN" -ge 1 ]; then
        CHILDREN_OK=1
    fi
fi

if [ "$CHILDREN_OK" -eq 1 ]; then
    echo "PASS: Both Svelte files handle @children slot"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: @children slot not handled in both files"
fi

echo ""
echo "=== Pass-to-pass: Existing functionality ==="

# [pr_diff] (0.10): clickOutside function still exists and is callable
RESULT=$(node -e "
$(strip_ts)

if (typeof clickOutside !== 'function') {
    console.log('MISSING');
    process.exit(0);
}

// Verify it takes two args (element, callback) — basic sanity
if (clickOutside.length >= 2) {
    console.log('PASS');
} else {
    console.log('FAIL: wrong arity ' + clickOutside.length);
}
" 2>/dev/null || echo "ERROR")

if [ "$RESULT" = "PASS" ]; then
    echo "PASS: clickOutside function preserved and callable"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "FAIL: clickOutside function ($RESULT)"
fi

echo ""
echo "=== Config-derived: Documentation ==="

# [agent_config] (0.03): Guide documents push_to_hub — AGENTS.md:45 @ 380d35ae
if [ -f "$GUIDE" ] && grep -q 'push_to_hub' "$GUIDE" 2>/dev/null; then
    echo "PASS: Guide documents push_to_hub"
    REWARD=$(python3 -c "print($REWARD + 0.03)")
else
    echo "FAIL: Guide missing push_to_hub"
fi

# [agent_config] (0.02): Guide documents authentication — AGENTS.md:45 @ 380d35ae
if [ -f "$GUIDE" ] && grep -qE 'token|login|auth' "$GUIDE" 2>/dev/null; then
    echo "PASS: Guide documents authentication"
    REWARD=$(python3 -c "print($REWARD + 0.02)")
else
    echo "FAIL: Guide missing authentication docs"
fi

echo ""
echo "=== Final Score ==="
# Clamp to [0, 1]
REWARD=$(python3 -c "print(min(1.0, max(0.0, round($REWARD, 2))))")
echo "Total: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Breakdown for debugging
python3 -c "
import json
r = $REWARD
json.dump({
    'reward': r,
    'behavioral': min(r, 0.65),
    'structural': 0.15 if r > 0.65 else 0.0,
    'config': 0.05 if r > 0.80 else 0.0,
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
