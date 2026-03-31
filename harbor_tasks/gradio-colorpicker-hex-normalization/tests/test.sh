#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/gradio

##############################################################################
# GATE: utils.ts must be parseable (balanced braces)
##############################################################################
# [pr_diff] (gate): utils.ts must not have syntax errors
node -e "
const fs = require('fs');
const src = fs.readFileSync('js/colorpicker/shared/utils.ts', 'utf8');
let depth = 0;
for (const ch of src) {
    if (ch === '{') depth++;
    if (ch === '}') depth--;
    if (depth < 0) process.exit(1);
}
if (depth !== 0) process.exit(1);
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: js/colorpicker/shared/utils.ts has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# Helper: strip TS types so we can eval utils.ts in Node
##############################################################################
EVAL_UTILS='
const fs = require("fs");
const tinycolor = require("/workspace/gradio/js/colorpicker/node_modules/tinycolor2");
const src = fs.readFileSync("js/colorpicker/shared/utils.ts", "utf8");
let js = src
    .replace(/import tinycolor from ["\x27]tinycolor2["\x27];?/g, "")
    .replace(/export function/g, "function")
    .replace(/hsva:\s*\{[^}]*\}/g, "hsva")
    .replace(/:\s*string/g, "")
    .replace(/:\s*number/g, "")
    .replace(/mode:\s*"hex"\s*\|\s*"rgb"\s*\|\s*"hsl"/g, "mode");
'

##############################################################################
# BEHAVIORAL F2P: hsva_to_rgba returns CORRECT hex values (0.35)
##############################################################################
# [pr_diff] (0.35): hsva_to_rgba must return correct hex color values, not rgba() strings
add_total 0.35
HSVA_RESULT=$(node -e "
${EVAL_UTILS}
const fn = new Function('tinycolor', js + '; return hsva_to_rgba;');
const hsva_to_rgba = fn(tinycolor);

// Test with known color conversions and verify EXACT correctness
const tests = [
    [{ h: 0,   s: 1, v: 1, a: 1 }, '#ff0000'],  // pure red
    [{ h: 120, s: 1, v: 1, a: 1 }, '#00ff00'],  // pure green
    [{ h: 240, s: 1, v: 1, a: 1 }, '#0000ff'],  // pure blue
    [{ h: 0,   s: 0, v: 0, a: 1 }, '#000000'],  // black
    [{ h: 0,   s: 0, v: 1, a: 1 }, '#ffffff'],  // white
];

let passed = 0;
for (const [input, expected] of tests) {
    const result = hsva_to_rgba(input);
    if (typeof result !== 'string' || !/^#[0-9a-f]{6}$/i.test(result)) {
        console.error('FORMAT FAIL: hsva_to_rgba(' + JSON.stringify(input) + ') = ' + result);
        continue;
    }
    // Compare via tinycolor to allow minor rounding differences
    const resultRgb = tinycolor(result).toRgb();
    const expectedRgb = tinycolor(expected).toRgb();
    const dr = Math.abs(resultRgb.r - expectedRgb.r);
    const dg = Math.abs(resultRgb.g - expectedRgb.g);
    const db = Math.abs(resultRgb.b - expectedRgb.b);
    if (dr <= 1 && dg <= 1 && db <= 1) {
        passed++;
    } else {
        console.error('VALUE FAIL: hsva_to_rgba(' + JSON.stringify(input) + ') = ' + result + ', expected ' + expected);
    }
}
console.log(passed + '/' + tests.length);
" 2>/dev/null)

HSVA_PASS=$(echo "$HSVA_RESULT" | tail -1 | cut -d/ -f1)
HSVA_TOTAL=$(echo "$HSVA_RESULT" | tail -1 | cut -d/ -f2)
if [ "$HSVA_PASS" = "$HSVA_TOTAL" ] && [ "$HSVA_TOTAL" = "5" ]; then
    echo "PASS: hsva_to_rgba returns correct hex values"
    add_score 0.35
elif [ -n "$HSVA_PASS" ] && [ "$HSVA_PASS" -ge 3 ] 2>/dev/null; then
    echo "PARTIAL: hsva_to_rgba returns correct hex for $HSVA_PASS/$HSVA_TOTAL cases"
    add_score 0.20
else
    echo "FAIL: hsva_to_rgba does not return correct hex values"
fi

##############################################################################
# BEHAVIORAL F2P: Text input normalization to hex (0.25)
# Tests the BEHAVIOR: any color string fed through the utils produces hex.
# Does NOT require a specific function name — finds any exported function
# that accepts a color string and returns hex.
##############################################################################
# [pr_diff] (0.25): Color strings (rgb, hsl, named, shorthand hex) must be normalized to #rrggbb
add_total 0.25
NORM_RESULT=$(node -e "
${EVAL_UTILS}

// Discover all functions in utils.ts that take a string and return hex
const fn = new Function('tinycolor', js + ';' +
    'const exports = {};' +
    // Collect all function names from the source
    js.replace(/function\\s+(\\w+)/g, (m, name) => {
        try { eval('exports[\"' + name + '\"] = ' + name); } catch(e) {}
        return m;
    }) + ';' +
    'return exports;'
);
const fns = fn(tinycolor);

// Find a function that normalizes color strings to hex (any name)
let normalizer = null;
for (const [name, func] of Object.entries(fns)) {
    if (typeof func !== 'function') continue;
    // Skip format_color (takes 2 args) and hsva_to_rgba (takes object)
    if (name === 'format_color' || name === 'hsva_to_rgba') continue;
    try {
        const r = func('red');
        if (typeof r === 'string' && /^#[0-9a-f]{6}$/i.test(r)) {
            normalizer = func;
            break;
        }
    } catch(e) {}
}

if (!normalizer) {
    // Fallback: check if format_color in hex mode acts as normalizer
    try {
        const fc = fns['format_color'];
        if (fc && typeof fc === 'function') {
            const r = fc('rgb(255,0,0)', 'hex');
            if (r === '#ff0000') {
                normalizer = (c) => fc(c, 'hex');
            }
        }
    } catch(e) {}
}

if (!normalizer) {
    console.log('NO_NORMALIZER');
    process.exit(0);
}

// Behavioral tests: various input formats must produce correct hex output
const tests = [
    ['rgb(255, 0, 0)', '#ff0000'],
    ['hsl(0, 100%, 50%)', '#ff0000'],
    ['red', '#ff0000'],
    ['#f00', '#ff0000'],
    ['#FF0000', '#ff0000'],
    ['rgb(0, 128, 0)', '#008000'],
    ['blue', '#0000ff'],
];

let passed = 0;
for (const [input, expected] of tests) {
    try {
        const result = normalizer(input);
        if (result === expected) {
            passed++;
        } else {
            console.error('FAIL: normalize(' + input + ') = ' + result + ', expected ' + expected);
        }
    } catch(e) {
        console.error('ERROR: normalize(' + input + ') threw: ' + e.message);
    }
}
console.log(passed + '/' + tests.length);
" 2>/dev/null)

if [ "$NORM_RESULT" = "NO_NORMALIZER" ]; then
    echo "FAIL: no color normalization function found in utils.ts"
else
    NORM_PASS=$(echo "$NORM_RESULT" | tail -1 | cut -d/ -f1)
    NORM_TOTAL=$(echo "$NORM_RESULT" | tail -1 | cut -d/ -f2)
    if [ "$NORM_PASS" = "$NORM_TOTAL" ] && [ "$NORM_TOTAL" = "7" ]; then
        echo "PASS: color normalization function converts all formats to hex"
        add_score 0.25
    elif [ -n "$NORM_PASS" ] && [ "$NORM_PASS" -ge 4 ] 2>/dev/null; then
        echo "PARTIAL: normalization converts $NORM_PASS/$NORM_TOTAL formats"
        add_score 0.15
    else
        echo "FAIL: color normalization function does not convert formats correctly"
    fi
fi

##############################################################################
# BEHAVIORAL F2P: Invalid color input handling (0.10)
# Again, discovers the normalizer by behavior, not by name.
##############################################################################
# [pr_diff] (0.10): Normalization must not crash on invalid color strings
add_total 0.10
INVALID_RESULT=$(node -e "
${EVAL_UTILS}

const fn = new Function('tinycolor', js + ';' +
    'const exports = {};' +
    js.replace(/function\\s+(\\w+)/g, (m, name) => {
        try { eval('exports[\"' + name + '\"] = ' + name); } catch(e) {}
        return m;
    }) + ';' +
    'return exports;'
);
const fns = fn(tinycolor);

let normalizer = null;
for (const [name, func] of Object.entries(fns)) {
    if (typeof func !== 'function') continue;
    if (name === 'format_color' || name === 'hsva_to_rgba') continue;
    try {
        const r = func('red');
        if (typeof r === 'string' && /^#[0-9a-f]{6}$/i.test(r)) {
            normalizer = func;
            break;
        }
    } catch(e) {}
}

if (!normalizer) { console.log('SKIP'); process.exit(0); }

let ok = true;
for (const bad of ['notacolor', '', 'xyz123', '###']) {
    try {
        const r = normalizer(bad);
        if (typeof r !== 'string') { ok = false; break; }
    } catch(e) {
        ok = false;
        break;
    }
}
console.log(ok ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$INVALID_RESULT" = "PASS" ]; then
    echo "PASS: normalization handles invalid input gracefully"
    add_score 0.10
elif [ "$INVALID_RESULT" = "SKIP" ]; then
    echo "SKIP: no standalone normalizer found"
else
    echo "FAIL: normalization crashes on invalid input"
fi

##############################################################################
# PASS-TO-PASS: format_color still works correctly (0.10)
##############################################################################
# [repo_tests] (0.10): Existing format_color function must not be broken
add_total 0.10
P2P_RESULT=$(node -e "
${EVAL_UTILS}
const fn = new Function('tinycolor', js + '; return format_color;');
const format_color = fn(tinycolor);

const tests = [
    ['#ff0000', 'hex', '#ff0000'],
    ['#ff0000', 'rgb', 'rgb(255, 0, 0)'],
    ['#ff0000', 'hsl', 'hsl(0, 100%, 50%)'],
    ['red', 'hex', '#ff0000'],
];

let allPass = true;
for (const [color, mode, expected] of tests) {
    const result = format_color(color, mode);
    if (result !== expected) {
        allPass = false;
        console.error('FAIL: format_color(' + color + ', ' + mode + ') = ' + result);
    }
}
console.log(allPass ? 'PASS' : 'FAIL');
" 2>/dev/null)

if [ "$P2P_RESULT" = "PASS" ]; then
    echo "PASS: format_color still works correctly"
    add_score 0.10
else
    echo "FAIL: format_color is broken"
fi

##############################################################################
# BEHAVIORAL: Svelte component imports/uses normalization (0.15)
# Check that Colorpicker.svelte actually calls a normalizer on text input.
# We look for ANY import from utils + usage in the onchange area — not a
# specific function name or pattern.
##############################################################################
# [pr_diff] (0.15): Text input handler must normalize color value before setting it
add_total 0.15
SVELTE_RESULT=$(node -e "
const fs = require('fs');
const src = fs.readFileSync('js/colorpicker/shared/Colorpicker.svelte', 'utf8');

// Check 1: Svelte imports something from utils beyond original format_color
const importMatch = src.match(/import\\s*\\{([^}]+)\\}\\s*from\\s*['\"]\\.\\/utils/);
if (!importMatch) {
    console.log('FAIL_NO_IMPORT');
    process.exit(0);
}

const imports = importMatch[1].split(',').map(s => s.trim());
const originalImports = new Set(['format_color', 'hsva_to_rgba']);
const newImports = imports.filter(i => !originalImports.has(i) && i.length > 0);

// Check 2: The text input change handler area references normalization
// Find any handler that deals with currentTarget or text input value
const hasValueNormalization =
    // Pattern: imported function wrapping currentTarget.value
    newImports.some(fn => src.includes(fn)) &&
    (src.includes('currentTarget') || src.includes('target.value') || src.includes('input_value')) ||
    // Pattern: tinycolor used inline on input value
    /tinycolor\s*\([^)]*(?:currentTarget|target|value)/.test(src) ||
    /(?:currentTarget|target|value)[^;]*\.toHex/.test(src);

if (hasValueNormalization || newImports.length > 0) {
    console.log('PASS');
} else {
    console.log('FAIL');
}
" 2>/dev/null)

if [ "$SVELTE_RESULT" = "PASS" ]; then
    echo "PASS: Svelte component uses normalization for text input"
    add_score 0.15
else
    echo "FAIL: Svelte component does not normalize text input values"
fi

##############################################################################
# CONFIG-DERIVED: Code style consistency (0.05)
##############################################################################
# [agent_config] (0.05): "Be consistent with the style of the surrounding code." — AGENTS.md:45
add_total 0.05
STYLE_OK=true

# Check utils.ts still uses tinycolor
if ! node -e "
const src = require('fs').readFileSync('js/colorpicker/shared/utils.ts','utf8');
process.exit(src.includes('tinycolor') ? 0 : 1);
" 2>/dev/null; then
    STYLE_OK=false
    echo "STYLE: tinycolor usage missing from utils.ts"
fi

# Check Svelte file still uses TypeScript
if ! node -e "
const src = require('fs').readFileSync('js/colorpicker/shared/Colorpicker.svelte','utf8');
process.exit(/lang=['\"]ts['\"]/.test(src) ? 0 : 1);
" 2>/dev/null; then
    STYLE_OK=false
    echo "STYLE: Svelte script tag should use lang=ts"
fi

if [ "$STYLE_OK" = true ]; then
    echo "PASS: code style is consistent"
    add_score 0.05
else
    echo "PARTIAL: some style issues found"
    add_score 0.02
fi

##############################################################################
# Final score
##############################################################################
REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute sub-scores
BEHAVIORAL=$(python3 -c "print(round(min($SCORE, 0.80), 4))")
REGRESSION=$(python3 -c "s=$SCORE; print(round(max(0, min(s - 0.70, 0.10)), 4))")
CONFIG=$(python3 -c "s=$SCORE; print(round(max(0, min(s - 0.95, 0.05)), 4))")
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
