"""
Task: gradio-dropdown-scroll-detach
Repo: gradio-app/gradio @ 7fb33fc3b80b421817c1d1ddea19c8858a9f2924
PR:   #12994

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
FILE = Path(REPO) / "js/dropdown/shared/DropdownOptions.svelte"
POSITIONING_VARS = ["distance_from_top", "distance_from_bottom", "input_height"]
_SVELTE_DIR = "/tmp/_eval_svelte"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _ensure_svelte():
    """Install svelte compiler if not already cached."""
    marker = Path(_SVELTE_DIR) / "node_modules" / "svelte" / "package.json"
    if marker.exists():
        return
    subprocess.run(
        ["npm", "init", "-y", "--prefix", _SVELTE_DIR],
        capture_output=True, timeout=10,
    )
    r = subprocess.run(
        ["npm", "install", "--prefix", _SVELTE_DIR, "svelte@5"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to install svelte: {r.stderr}"


def _read_script_block():
    """Extract the <script> content from the Svelte file."""
    src = FILE.read_text()
    match = re.search(r"<script[^>]*>([\s\S]*?)</script>", src)
    assert match, "Could not find <script> block in DropdownOptions.svelte"
    return match.group(1)


def _extract_block(text: str, max_chars: int = 3000) -> str:
    """Extract the first balanced { ... } block from *text*."""
    depth = 0
    buf = []
    started = False
    for ch in text[:max_chars]:
        if ch == "{":
            depth += 1
            started = True
        if ch == "}":
            depth -= 1
        if started:
            buf.append(ch)
        if started and depth == 0:
            break
    return "".join(buf)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------


def test_positioning_vars_use_state():
    """Svelte compiler parses the component; all 3 positioning variables are
    declared with $state() — confirmed via AST analysis of the parsed tree,
    not text grep."""
    _ensure_svelte()
    r = _run_node(f"""
import {{ createRequire }} from 'module';
const require = createRequire(import.meta.url);
const {{ parse }} = require('{_SVELTE_DIR}/node_modules/svelte/compiler');
import {{ readFileSync }} from 'fs';

const src = readFileSync('js/dropdown/shared/DropdownOptions.svelte', 'utf8');

let ast;
try {{
    ast = parse(src);
}} catch (e) {{
    console.log(JSON.stringify({{ error: e.message }}));
    process.exit(0);
}}

const instance = ast.instance;
if (!instance) {{
    console.log(JSON.stringify({{ error: 'no instance script' }}));
    process.exit(0);
}}

const body = instance.body || instance.content?.body || instance.content;
if (!body) {{
    console.log(JSON.stringify({{ error: 'no script body', keys: Object.keys(instance) }}));
    process.exit(0);
}}

// Recursively collect all VariableDeclarations
function find_var_decls(node, results = []) {{
    if (!node || typeof node !== 'object') return results;
    if (node.type === 'VariableDeclaration') {{
        for (const d of (node.declarations || [])) {{
            results.push({{
                name: d.id?.name,
                init_type: d.init?.type,
                callee_name: d.init?.callee?.name,
                has_init: d.init !== null && d.init !== undefined,
            }});
        }}
    }}
    for (const val of Object.values(node)) {{
        if (Array.isArray(val)) {{
            val.forEach(v => find_var_decls(v, results));
        }} else if (typeof val === 'object' && val !== null) {{
            find_var_decls(val, results);
        }}
    }}
    return results;
}}

const decls = find_var_decls(body);
const targets = {json.dumps(POSITIONING_VARS)};
const missing = [];

for (const v of targets) {{
    const d = decls.find(x => x.name === v);
    if (!d) {{
        missing.push(v + ': not declared');
    }} else if (d.callee_name !== '$state') {{
        missing.push(v + ': not $state (got ' + (d.callee_name || 'no init') + ')');
    }}
}}

if (missing.length > 0) {{
    console.log(JSON.stringify({{ missing }}));
}} else {{
    console.log(JSON.stringify({{ pass: true }}));
}}
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    result = json.loads(r.stdout.strip().splitlines()[-1])
    if "error" in result:
        assert False, f"Svelte parse error: {result['error']}"
    if "missing" in result:
        assert False, f"Non-reactive positioning vars: {result['missing']}"
    assert result.get("pass"), "Positioning vars not declared with $state()"


def test_no_bare_positioning_declarations():
    """The old buggy pattern — bare 'let <var>: type;' with no initialiser —
    must be absent for all 3 positioning variables. Verified by running Node.js
    to parse and inspect the script block programmatically."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('js/dropdown/shared/DropdownOptions.svelte', 'utf8');
const m = src.match(/<script[^>]*>([\\s\\S]*?)<\\/script>/);
if (!m) {
    console.log(JSON.stringify({ error: 'no script block' }));
    process.exit(0);
}
const script = m[1];
const vars = ['distance_from_top', 'distance_from_bottom', 'input_height'];
const bare = [];

for (const v of vars) {
    // Look for bare declaration: let varName: type; (no = assignment)
    const lines = script.split('\\n');
    for (const line of lines) {
        const trimmed = line.trim();
        // Match: let varName: SomeType;
        // Must NOT contain '=' (that would be an initializer like $state)
        if (trimmed.startsWith('let ' + v) && trimmed.includes(':') && !trimmed.includes('=')) {
            bare.push(v);
            break;
        }
    }
}

if (bare.length > 0) {
    console.log(JSON.stringify({ bare }));
} else {
    console.log(JSON.stringify({ pass: true }));
}
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    result = json.loads(r.stdout.strip().splitlines()[-1])
    if "error" in result:
        assert False, f"Parse error: {result['error']}"
    if "bare" in result:
        assert False, f"Bare declarations remain: {result['bare']}"
    assert result.get("pass"), "Bare declarations still present"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_input_width_still_reactive():
    """input_width was already $state before the fix and must remain so."""
    script = _read_script_block()
    assert re.search(r"let\s+input_width\b[^;\n]*=\s*\$state", script), (
        "input_width lost its $state reactivity"
    )


# [pr_diff] pass_to_pass
def test_effect_reads_positioning_vars():
    """$effect (or $effect.pre) block must reference at least one positioning
    variable so CSS properties update when the reactive values change."""
    script = _read_script_block()
    effect_match = re.search(r"\$effect(?:\.pre)?\s*\(", script)
    assert effect_match, "$effect block not found"
    body = _extract_block(script[effect_match.start():])
    refs = sum(1 for v in POSITIONING_VARS if v in body)
    assert refs >= 1, (
        "$effect does not reference any positioning variables — "
        "CSS won't update on scroll"
    )


# [pr_diff] pass_to_pass
def test_template_structure_intact():
    """Dropdown template must render a <ul> list with CSS positioning and a
    show_options visibility guard."""
    src = FILE.read_text()
    after_script = src[src.index("</script>") + 9:]
    assert re.search(r"<ul\b", after_script), "Missing <ul> list element in template"
    assert (
        re.search(r"style[=:].*top|top\s*:", after_script)
    ), "Missing top/bottom positioning in template styles"
    assert "show_options" in src, "Missing show_options visibility guard"


# [static] pass_to_pass
def test_not_stubbed():
    """File must have substantial content — not a gutted replacement."""
    script = _read_script_block()
    src = FILE.read_text()
    lines = len(src.strip().splitlines())
    funcs = len(re.findall(r"function\s+\w+", script))
    assert lines > 50, f"Only {lines} lines — file appears stubbed"
    assert funcs >= 2, f"Only {funcs} functions — file appears stubbed"
