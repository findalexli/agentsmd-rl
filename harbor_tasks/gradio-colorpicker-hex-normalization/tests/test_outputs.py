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
# Gate (pass_to_pass, static) — utils.ts must be parseable
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hsva_to_rgba_returns_hex():
    """hsva_to_rgba must return #rrggbb hex strings for known color inputs."""
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
    # that converts 'red' → '#ff0000'
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
console.log(JSON.stringify({ found: true, results }));
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
# Fail-to-pass (pr_diff) — integration check
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Structural-only because: Svelte component requires browser runtime to execute
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
        "Text input handler does not normalize color value — "
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_normalize_color_has_typescript_types():
    """normalize_color must have explicit TypeScript parameter and return type annotations."""
    src = Path(UTILS_TS).read_text()
    # Expect: function normalize_color(color: string): string
    assert re.search(
        r'function\s+normalize_color\s*\(\s*\w+\s*:\s*string\s*\)\s*:\s*string',
        src,
    ), (
        "normalize_color must declare TypeScript types: (color: string): string — "
        "js/README.md line 81 requires static types on JavaScript/TypeScript code"
    )


# [repo_tests] pass_to_pass
def test_format_color_regression():
    """Existing format_color function must still produce correct output."""
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
