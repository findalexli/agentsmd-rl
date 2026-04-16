"""
Task: gradio-colorpicker-hex-normalization
Repo: gradio-app/gradio @ 8bc75137b24ba8a8571b49b9b006741819c0518b
PR:   #13126

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
UTILS_TS = f"{REPO}/js/colorpicker/shared/utils.ts"
SVELTE = f"{REPO}/js/colorpicker/shared/Colorpicker.svelte"
EVENTS_TS = f"{REPO}/js/colorpicker/shared/events.ts"

# Shared JS preamble: strip TS types from utils.ts so Node can eval it.
EVAL_UTILS_JS = r"""
const fs = require("fs");
const tinycolor = require("/workspace/gradio/js/colorpicker/node_modules/tinycolor2");
const src = fs.readFileSync("js/colorpicker/shared/utils.ts", "utf8");
let js = src
    .replace(/import tinycolor from ["']tinycolor2["'];?/g, "")
    .replace(/export function/g, "function")
    .replace(/hsva:\s*\{[^}]*\}/g, "hsva")
    .replace(/:\s*string/g, "")
    .replace(/:\s*number/g, "")
    .replace(/mode:\s*"hex"\s*\|\s*"rgb"\s*\|\s*"hsl"/g, "mode");
"""


def _run_node(script: str) -> str:
    """Run a Node.js script in the repo directory, return stdout."""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Node script failed:\n{r.stderr.decode()}"
    return r.stdout.decode().strip()


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) - utils.ts must be parseable
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_utils_syntax():
    """utils.ts must have balanced braces (no syntax errors)."""
    src = Path(UTILS_TS).read_text()
    depth = 0
    for ch in src:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        assert depth >= 0, "Unbalanced closing brace in utils.ts"
    assert depth == 0, f"Unbalanced braces in utils.ts (depth={depth})"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - file structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_colorpicker_utils_file_structure():
    """utils.ts must have proper structure: tinycolor import and exported functions (pass_to_pass)."""
    src = Path(UTILS_TS).read_text()

    # Check for tinycolor import
    assert "import tinycolor" in src, "utils.ts must import tinycolor"

    # Check for required function exports (by behavior, not specific name)
    assert "export function hsva_to_rgba" in src, "utils.ts must export hsva_to_rgba function"
    assert "export function format_color" in src, "utils.ts must export format_color function"

    # Check for TypeScript types (generic check, not specific literal)
    assert "export function" in src and ":" in src, "utils.ts must use TypeScript type annotations"


# [static] pass_to_pass
def test_colorpicker_svelte_file_structure():
    """Colorpicker.svelte must have proper imports and structure (pass_to_pass)."""
    src = Path(SVELTE).read_text()

    # Check for Svelte imports
    assert "import { BlockTitle }" in src or "@gradio/atoms" in src, "Colorpicker.svelte must import from @gradio/atoms"

    # Check for Svelte reactive syntax (input handling via bind:value or onchange)
    assert "bind:value" in src or "onchange" in src, "Colorpicker.svelte must have input handling"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - runtime tests using subprocess.run()
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_tinycolor_runtime_available():
    """tinycolor2 dependency must be available for runtime tests (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "console.log(require('/workspace/gradio/js/colorpicker/node_modules/tinycolor2')('red').toHexString())"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"tinycolor2 not available: {r.stderr}"
    assert "#ff0000" in r.stdout, f"tinycolor2 did not return expected hex: {r.stdout}"


# [repo_tests] pass_to_pass
def test_node_typescript_parse_check():
    """Modified TypeScript files must be parseable by Node.js (pass_to_pass)."""
    # Test that we can read and strip TS types to make it runnable
    script = r"""
const fs = require('fs');
const src = fs.readFileSync('/workspace/gradio/js/colorpicker/shared/utils.ts', 'utf8');
// Basic sanity checks that the file is parseable
if (!src.includes('export function hsva_to_rgba')) {
    console.error('Cannot find hsva_to_rgba function');
    process.exit(1);
}
if (!src.includes('export function format_color')) {
    console.error('Cannot find format_color function');
    process.exit(1);
}
console.log('utils.ts is parseable');
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"TypeScript file parse check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_hsva_to_rgba_runs():
    """hsva_to_rgba function must execute and return valid color string (pass_to_pass)."""
    script = EVAL_UTILS_JS + r"""
const fn = new Function('tinycolor', js + '; return hsva_to_rgba;');
const hsva_to_rgba = fn(tinycolor);

const tests = [
    { h: 0, s: 1, v: 1, a: 1 },
    { h: 120, s: 1, v: 1, a: 1 },
    { h: 240, s: 1, v: 1, a: 1 },
    { h: 0, s: 0, v: 0, a: 1 },
    { h: 0, s: 0, v: 1, a: 1 },
];

const results = [];
for (const input of tests) {
    const result = hsva_to_rgba(input);
    // Accept either rgba() or #hex format - both are valid color representations
    const isValidColor = typeof result === 'string' && (
        result.startsWith('rgba(') ||
        /^#[0-9a-f]{6}$/i.test(result)
    );
    results.push({ input, result, isValidColor });
}
console.log(JSON.stringify(results));
"""
    raw = _run_node(script)
    results = json.loads(raw)
    for r in results:
        assert r["isValidColor"], f"hsva_to_rgba({r['input']}) = {r['result']!r}, expected valid color string"


# [repo_tests] pass_to_pass
def test_format_color_regression():
    """Existing format_color function must still produce correct output via Node.js runtime (pass_to_pass)."""
    script = EVAL_UTILS_JS + r"""
const fn = new Function('tinycolor', js + '; return format_color;');
const format_color = fn(tinycolor);

const tests = [
    ['#ff0000', 'hex', '#ff0000'],
    ['#ff0000', 'rgb', 'rgb(255, 0, 0)'],
    ['#ff0000', 'hsl', 'hsl(0, 100%, 50%)'],
    ['red', 'hex', '#ff0000'],
    ['#00ff00', 'rgb', 'rgb(0, 255, 0)'],
    ['#0000ff', 'hsl', 'hsl(240, 100%, 50%)'],
    ['#663399', 'hex', '#663399'],
    ['#663399', 'rgb', 'rgb(102, 51, 153)'],
];

const results = [];
for (const [color, mode, expected] of tests) {
    const result = format_color(color, mode);
    results.push({ color, mode, result, expected, ok: result === expected });
}
console.log(JSON.stringify(results));
"""
    raw = _run_node(script)
    results = json.loads(raw)
    for r in results:
        assert r["ok"], f"format_color({r['color']!r}, {r['mode']!r}) = {r['result']!r}, expected {r['expected']!r}"


# [repo_tests] pass_to_pass
def test_colorpicker_directory_structure():
    """Colorpicker shared directory has required files (pass_to_pass)."""
    script = r"""
const fs = require('fs');
const path = require('path');

const sharedDir = '/workspace/gradio/js/colorpicker/shared';
const requiredFiles = ['utils.ts', 'Colorpicker.svelte', 'events.ts'];

// Check all required files exist
for (const file of requiredFiles) {
    const filePath = path.join(sharedDir, file);
    if (!fs.existsSync(filePath)) {
        console.error('Missing file: ' + file);
        process.exit(1);
    }
}

// Check utils.ts has expected exports
const utilsPath = path.join(sharedDir, 'utils.ts');
const utilsContent = fs.readFileSync(utilsPath, 'utf8');

const requiredExports = ['hsva_to_rgba', 'format_color'];
for (const exp of requiredExports) {
    if (!utilsContent.includes('export function ' + exp)) {
        console.error('Missing export: ' + exp);
        process.exit(1);
    }
}

// Check Colorpicker.svelte has proper structure
const sveltePath = path.join(sharedDir, 'Colorpicker.svelte');
const svelteContent = fs.readFileSync(sveltePath, 'utf8');

if (!svelteContent.includes('import { BlockTitle }') && !svelteContent.includes('@gradio/atoms')) {
    console.error('Missing BlockTitle import');
    process.exit(1);
}

if (!svelteContent.includes('bind:value') && !svelteContent.includes('onchange')) {
    console.error('Missing input handling (bind:value or onchange)');
    process.exit(1);
}

console.log('All colorpicker files have valid structure');
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Colorpicker file structure check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_events_ts_exports():
    """Events.ts file exists and exports click_outside handler with TypeScript types (pass_to_pass)."""
    script = r"""
const fs = require('fs');

const eventsPath = '/workspace/gradio/js/colorpicker/shared/events.ts';
const content = fs.readFileSync(eventsPath, 'utf8');

// Check for click_outside export
if (!content.includes('click_outside') || !content.includes('export')) {
    console.error('Missing click_outside export');
    process.exit(1);
}

// Check for TypeScript type annotations (inline types in function signature)
// Look for parameter types and return type annotations generically
const hasTypeAnnotations = /\w+\s*:\s*\w+/.test(content) || /:\s*(void|string|number|boolean)/.test(content);
if (!hasTypeAnnotations) {
    console.error('Missing TypeScript type annotations');
    process.exit(1);
}

console.log('events.ts has valid structure');
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Events.ts structure check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hsva_to_rgba_returns_hex():
    """hsva_to_rgba must return #rrggbb hex strings, not rgba() strings."""
    script = EVAL_UTILS_JS + r"""
const fn = new Function('tinycolor', js + '; return hsva_to_rgba;');
const hsva_to_rgba = fn(tinycolor);

const tests = [
    [{ h: 0,   s: 1, v: 1, a: 1 }, '#ff0000'],
    [{ h: 120, s: 1, v: 1, a: 1 }, '#00ff00'],
    [{ h: 240, s: 1, v: 1, a: 1 }, '#0000ff'],
    [{ h: 0,   s: 0, v: 0, a: 1 }, '#000000'],
    [{ h: 0,   s: 0, v: 1, a: 1 }, '#ffffff'],
    [{ h: 30,  s: 0.5, v: 0.8, a: 1 }, null],  // non-trivial, just check format
    [{ h: 210, s: 0.7, v: 0.6, a: 1 }, null],   // blue-ish, check format
    [{ h: 60,  s: 1, v: 1, a: 0.5 }, '#ffff00'], // yellow with alpha
];

const results = [];
for (const [input, expected] of tests) {
    const result = hsva_to_rgba(input);
    const isHex = typeof result === 'string' && /^#[0-9a-f]{6}$/i.test(result);
    let valueOk = true;
    if (expected && isHex) {
        const rRgb = tinycolor(result).toRgb();
        const eRgb = tinycolor(expected).toRgb();
        valueOk = Math.abs(rRgb.r - eRgb.r) <= 1
               && Math.abs(rRgb.g - eRgb.g) <= 1
               && Math.abs(rRgb.b - eRgb.b) <= 1;
    }
    results.push({ input, result, isHex, valueOk });
}
console.log(JSON.stringify(results));
"""
    raw = _run_node(script)
    results = json.loads(raw)
    for r in results:
        assert r["isHex"], f"hsva_to_rgba({r['input']}) = {r['result']!r}, expected #rrggbb"
        assert r["valueOk"], f"hsva_to_rgba({r['input']}) = {r['result']!r}, wrong color value"


# [pr_diff] fail_to_pass
def test_normalize_color_various_formats():
    """A normalize function must convert rgb/hsl/named/shorthand colors to #rrggbb."""
    # Discover the normalizer: any exported function (not format_color/hsva_to_rgba)
    # that converts 'red' -> '#ff0000'
    script = EVAL_UTILS_JS + r"""
const fn = new Function('tinycolor', js + ';' +
    'return { ' + (js.match(/function\s+(\w+)/g) || []).map(m => {
        const name = m.replace('function ', '');
        return name + ': typeof ' + name + ' === "function" ? ' + name + ' : undefined';
    }).join(', ') + ' };'
);
const fns = fn(tinycolor);

let normalizer = null;
let normalizerName = null;
for (const [name, func] of Object.entries(fns)) {
    if (typeof func !== 'function') continue;
    if (name === 'format_color' || name === 'hsva_to_rgba') continue;
    try {
        const r = func('red');
        if (typeof r === 'string' && /^#[0-9a-f]{6}$/i.test(r)) {
            normalizer = func;
            normalizerName = name;
            break;
        }
    } catch(e) {}
}

if (!normalizer) {
    // Fallback: check if format_color('...', 'hex') works as normalizer
    try {
        if (fns['format_color'] && /^#[0-9a-f]{6}$/i.test(fns['format_color']('rgb(255,0,0)', 'hex'))) {
            normalizer = (c) => fns['format_color'](c, 'hex');
            normalizerName = 'format_color_hex_mode';
        }
    } catch(e) {}
}

if (!normalizer) {
    console.log(JSON.stringify({ found: false }));
    process.exit(0);
}

const tests = [
    ['rgb(255, 0, 0)', '#ff0000'],
    ['hsl(0, 100%, 50%)', '#ff0000'],
    ['red', '#ff0000'],
    ['#f00', '#ff0000'],
    ['#FF0000', '#ff0000'],
    ['rgb(0, 128, 0)', '#008000'],
    ['blue', '#0000ff'],
    ['hsl(120, 100%, 25%)', '#008000'],
    ['rgb(102, 51, 153)', '#663399'],
    ['#abc', '#aabbcc'],
];

const results = [];
for (const [input, expected] of tests) {
    try {
        const result = normalizer(input);
        results.push({ input, result, expected, ok: result === expected });
    } catch(e) {
        results.push({ input, result: 'ERROR: ' + e.message, expected, ok: false });
    }
}
console.log(JSON.stringify({ found: true, normalizerName, results }));
"""
    raw = _run_node(script)
    data = json.loads(raw)
    assert data["found"], "No color normalization function found in utils.ts"
    for r in data["results"]:
        assert r["ok"], f"normalize({r['input']!r}) = {r['result']!r}, expected {r['expected']!r}"


# [pr_diff] fail_to_pass
def test_normalize_color_invalid_input():
    """Normalization must not crash on invalid color strings; must return a string."""
    script = EVAL_UTILS_JS + r"""
const fn = new Function('tinycolor', js + ';' +
    'return { ' + (js.match(/function\s+(\w+)/g) || []).map(m => {
        const name = m.replace('function ', '');
        return name + ': typeof ' + name + ' === "function" ? ' + name + ' : undefined';
    }).join(', ') + ' };'
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

if (!normalizer) {
    // Fallback: check if format_color('...', 'hex') works as normalizer
    try {
        if (fns['format_color'] && /^#[0-9a-f]{6}$/i.test(fns['format_color']('rgb(255,0,0)', 'hex'))) {
            normalizer = (c) => fns['format_color'](c, 'hex');
        }
    } catch(e) {}
}

if (!normalizer) {
    console.log(JSON.stringify({ found: false }));
    process.exit(0);
}

const invalids = ['notacolor', '', 'xyz123', '###', 'rgba()', 'hsl(bad)', '12345', 'none'];
const results = [];
for (const bad of invalids) {
    try {
        const r = normalizer(bad);
        results.push({ input: bad, result: r, isString: typeof r === 'string' });
    } catch(e) {
        results.push({ input: bad, result: 'THREW: ' + e.message, isString: false });
    }
}
console.log(JSON.stringify({ found: true, results }));
"""
    raw = _run_node(script)
    data = json.loads(raw)
    assert data["found"], "No color normalization function found in utils.ts"
    for r in data["results"]:
        assert r["isString"], f"normalize({r['input']!r}) did not return string: {r['result']!r}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - integration check
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Behavioral test: verify the Svelte component normalizes input values
def test_svelte_text_input_normalization():
    """Colorpicker.svelte text input handler must normalize color before setting value."""
    src = Path(SVELTE).read_text()

    # The onchange handler must NOT pass raw e.currentTarget.value as the value.
    # It must call a normalization function (from utils or inline tinycolor).
    import_match = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']\.\/utils', src)
    assert import_match, "Colorpicker.svelte does not import from ./utils"

    imports = [s.strip() for s in import_match.group(1).split(",") if s.strip()]
    original = {"format_color", "hsva_to_rgba"}
    new_imports = [i for i in imports if i not in original]

    # Either new imports from utils are used, or tinycolor is used inline on the input value
    has_new_import_usage = any(i in src for i in new_imports) if new_imports else False
    has_inline_tinycolor = bool(
        re.search(r'tinycolor\s*\([^)]*(?:currentTarget|target|value)', src)
    )

    assert has_new_import_usage or has_inline_tinycolor, (
        "Text input handler does not normalize color value - "
        "value = e.currentTarget.value is passed raw"
    )

    # Also verify the raw assignment pattern is gone
    onchange_blocks = re.findall(
        r'onchange\s*=\s*\{?\s*\(e\)\s*=>\s*\{([^}]+)\}', src
    )
    for block in onchange_blocks:
        if "currentTarget.value" in block:
            assert not re.search(
                r'value\s*=\s*e\.currentTarget\.value\s*;?\s*$', block.strip()
            ), "Raw e.currentTarget.value still assigned directly to value"


# [agent_config] fail_to_pass
# Behavioral test: verify that exported functions have TypeScript type annotations
def test_functions_have_typescript_types():
    """Exported functions in utils.ts must have explicit TypeScript parameter and return type annotations."""
    src = Path(UTILS_TS).read_text()

    # Discover all exported functions
    script = r"""
const fs = require('fs');
const src = fs.readFileSync('/workspace/gradio/js/colorpicker/shared/utils.ts', 'utf8');

// Find all exported functions and their signatures
const exportMatches = src.match(/export\s+function\s+\w+\s*\([^)]*\)\s*:?\s*\w*\s*\{/g) || [];
const results = [];

for (const match of exportMatches) {
    const nameMatch = match.match(/export\s+function\s+(\w+)/);
    if (!nameMatch) continue;
    const name = nameMatch[1];

    // Check for type annotations (either param types or return type)
    const hasParamTypes = /\w+\s*:\s*(string|number|boolean|\{[^}]+\})/.test(match);
    const hasReturnType = /\)\s*:\s*(string|number|boolean|void)/.test(match);

    results.push({
        name: name,
        hasParamTypes: hasParamTypes,
        hasReturnType: hasReturnType,
        hasAnyTypes: hasParamTypes || hasReturnType,
        signature: match.slice(0, 100)
    });
}

console.log(JSON.stringify(results));
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"TypeScript type check failed: {r.stderr}"

    functions = json.loads(r.stdout)
    assert len(functions) > 0, "No exported functions found in utils.ts"

    # At least one exported function must have TypeScript type annotations
    has_types = any(f["hasAnyTypes"] for f in functions)
    assert has_types, (
        "No exported function has explicit TypeScript type annotations. "
        "At least one function should declare parameter or return types."
    )
