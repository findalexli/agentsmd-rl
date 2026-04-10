"""
Task: gradio-html-gallery-fixed-css-iframe
Repo: gradio-app/gradio @ 380d35ae1164289c85c253eefefda6d8511e614e
PR:   12941

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/gradio"
UTILS = f"{REPO}/js/_website/src/routes/custom-components/html-gallery/utils.ts"
PAGE = f"{REPO}/js/_website/src/routes/custom-components/html-gallery/+page.svelte"
ENTRY = f"{REPO}/js/_website/src/routes/custom-components/html-gallery/ComponentEntry.svelte"
GUIDE = f"{REPO}/guides/03_building-with-blocks/06_custom-HTML-components.md"


def _run_node(js_code: str, timeout: int = 10) -> str:
    """Load utils.ts functions and execute JS test code using Node 22 native TS stripping."""
    src = Path(UTILS).read_text()

    # Replace ES module imports with mocks (Svelte-specific imports won't resolve)
    import re
    src = re.sub(r'^import\s+.*$', '', src, flags=re.MULTILINE)
    # Remove export keywords
    src = re.sub(r'^export\s+', '', src, flags=re.MULTILINE)
    # Add themeCSS mock at the top
    src = 'const themeCSS: string = "body { margin: 0; font-family: sans-serif; }";\n' + src

    full_code = src + "\n" + js_code

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(full_code)
        tmp_path = f.name

    try:
        r = subprocess.run(
            ["node", "--experimental-strip-types", tmp_path],
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "NODE_NO_WARNINGS": "1"},
        )
        if r.returncode != 0 and not r.stdout.strip():
            return f"ERROR: {r.stderr.strip()}"
        return r.stdout.strip()
    finally:
        os.unlink(tmp_path)


def _ensure_deps():
    """Ensure pnpm is installed and dependencies are installed."""
    # Install pnpm if needed
    try:
        subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, check=True)
    
    # Check if node_modules exists
    if not Path(f"{REPO}/node_modules").exists():
        subprocess.run(
            ["pnpm", "install"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — target file must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_utils_file_exists():
    """utils.ts must exist (gate for all behavioral tests)."""
    assert Path(UTILS).exists(), "utils.ts is missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — needs_iframe function
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_needs_iframe_detects_fixed_css():
    """needs_iframe returns true for position:fixed CSS with varied spacing/casing."""
    result = _run_node("""
if (typeof needs_iframe !== 'function') { console.log('MISSING'); process.exit(0); }
const cases: [string, boolean][] = [
    ['div { position: fixed; top: 0; }', true],
    ['div { position:fixed; left: 0; }', true],
    ['.overlay { POSITION : FIXED; }', true],
    ['div { position:  fixed; }', true],
    ['body { position: fixed; width: 100%; }', true],
];
let pass = true;
for (const [input, expected] of cases) {
    if (needs_iframe(input) !== expected) { pass = false; }
}
console.log(pass ? 'PASS' : 'FAIL');
""")
    assert result == "PASS", f"needs_iframe failed to detect position:fixed: {result}"


# [pr_diff] fail_to_pass
def test_needs_iframe_rejects_non_fixed_css():
    """needs_iframe returns false for non-fixed CSS — verifies both directions."""
    result = _run_node("""
if (typeof needs_iframe !== 'function') { console.log('MISSING'); process.exit(0); }
const falseTests: [string, boolean][] = [
    ['div { position: relative; margin: 10px; }', false],
    ['div { position: absolute; top: 0; }', false],
    ['div { position: static; }', false],
    ['.box { display: flex; color: red; }', false],
    ['', false],
];
const trueTests: [string, boolean][] = [
    ['nav { position: FIXED; z-index: 999; }', true],
];
let pass = true;
for (const [input, expected] of [...falseTests, ...trueTests]) {
    if (needs_iframe(input) !== expected) { pass = false; }
}
console.log(pass ? 'PASS' : 'FAIL');
""")
    assert result == "PASS", f"needs_iframe bidirectional check failed: {result}"


# [pr_diff] fail_to_pass
def test_needs_iframe_handles_falsy_input():
    """needs_iframe returns false for undefined/null/empty without crashing."""
    result = _run_node("""
if (typeof needs_iframe !== 'function') { console.log('MISSING'); process.exit(0); }
try {
    const r1 = needs_iframe(undefined);
    const r2 = needs_iframe(null);
    const r3 = needs_iframe('');
    console.log(r1 === false && r2 === false && r3 === false ? 'PASS' : 'FAIL');
} catch(e) { console.log('FAIL: ' + (e as Error).message); }
""")
    assert result == "PASS", f"needs_iframe falsy input handling failed: {result}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — build_srcdoc function
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_srcdoc_produces_valid_html():
    """build_srcdoc returns complete HTML documents with rendered props (varied inputs)."""
    result = _run_node("""
if (typeof build_srcdoc !== 'function') { console.log('MISSING'); process.exit(0); }

const comp1 = {
    html_template: '<div>${value}</div>',
    css_template: 'div { position: fixed; top: 0; }',
    js_on_load: 'console.log("loaded")',
    head: '<link rel="stylesheet" href="test.css">',
    default_props: { value: 'Alpha' },
};
const html1 = build_srcdoc(comp1, { value: 'Alpha' }, false);

const comp2 = {
    html_template: '<span>${name}</span>',
    css_template: 'span { color: blue; }',
    default_props: { name: 'BetaTest' },
};
const html2 = build_srcdoc(comp2, { name: 'BetaTest' }, false);

let pass = true;
for (const [html, label] of [[html1, 'comp1'], [html2, 'comp2']] as const) {
    if (typeof html !== 'string') { pass = false; continue; }
    if (!/<!doctype html>/i.test(html)) pass = false;
    if (!/<html/i.test(html)) pass = false;
    if (!/<head>/i.test(html)) pass = false;
    if (!/<body>/i.test(html)) pass = false;
}
if (!html1.includes('Alpha')) pass = false;
if (!html2.includes('BetaTest')) pass = false;
if (html2.includes('Alpha')) pass = false;  // cross-check: not hardcoded
console.log(pass ? 'PASS' : 'FAIL');
""")
    assert result == "PASS", f"build_srcdoc HTML structure failed: {result}"


# [pr_diff] fail_to_pass
def test_build_srcdoc_dark_mode():
    """build_srcdoc adds dark class when dark=true, omits it for light."""
    result = _run_node("""
if (typeof build_srcdoc !== 'function') { console.log('MISSING'); process.exit(0); }
const comp = { html_template: '<div>test</div>', css_template: 'div { color: red; }', default_props: {} };
const darkHtml = build_srcdoc(comp, {}, true);
const lightHtml = build_srcdoc(comp, {}, false);
const hasDark = /class="[^"]*dark[^"]*"/.test(darkHtml) || /data-theme="dark"/.test(darkHtml);
const lightHasDark = /class="[^"]*dark[^"]*"/.test(lightHtml);
console.log(hasDark && !lightHasDark ? 'PASS' : 'FAIL');
""")
    assert result == "PASS", f"build_srcdoc dark mode failed: {result}"


# [pr_diff] fail_to_pass
def test_build_srcdoc_escapes_script_tags():
    """build_srcdoc escapes </script in JS content without dropping the code."""
    result = _run_node(r"""
if (typeof build_srcdoc !== 'function') { console.log('MISSING'); process.exit(0); }
const comp = {
    html_template: '<div>esc</div>',
    css_template: 'div { color: red; }',
    js_on_load: 'var x = "</scr' + 'ipt><img src=x>"; console.log(x);',
    default_props: {},
};
const html = build_srcdoc(comp, {}, false);
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/i);
if (!scriptMatch) { console.log('FAIL: no script block'); process.exit(0); }
const body = scriptMatch[1];
if (body.includes('</script')) { console.log('FAIL: unescaped </script'); process.exit(0); }
if (!body.includes('console.log')) { console.log('FAIL: JS dropped'); process.exit(0); }
console.log('PASS');
""")
    assert result == "PASS", f"build_srcdoc script escaping failed: {result}"


# [pr_diff] fail_to_pass
def test_build_srcdoc_includes_head_and_css():
    """build_srcdoc includes component CSS and head content in output."""
    result = _run_node("""
if (typeof build_srcdoc !== 'function') { console.log('MISSING'); process.exit(0); }
const comp = {
    html_template: '<div>headtest</div>',
    css_template: '.unique-test-cls { background: chartreuse; }',
    head: '<meta name="custom-gallery-head" content="present">',
    default_props: {},
};
const html = build_srcdoc(comp, {}, false);
let pass = true;
if (!html.includes('chartreuse')) pass = false;
if (!html.includes('custom-gallery-head')) pass = false;
console.log(pass ? 'PASS' : 'FAIL');
""")
    assert result == "PASS", f"build_srcdoc CSS/head inclusion failed: {result}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing functionality preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_click_outside_preserved():
    """clickOutside Svelte action returns {update, destroy} interface."""
    result = _run_node("""
if (typeof clickOutside !== 'function') { console.log('MISSING'); process.exit(0); }
// Mock a minimal DOM element and document.body for the action
const listeners: Record<string, Function> = {};
(globalThis as any).document = {
    body: {
        addEventListener: (ev: string, fn: Function) => { listeners[ev] = fn; },
        removeEventListener: (ev: string, fn: Function) => { delete listeners[ev]; },
    }
};
const mockEl = { contains: () => true };
let called = false;
const result = clickOutside(mockEl as any, () => { called = true; });
if (!result || typeof result.update !== 'function' || typeof result.destroy !== 'function') {
    console.log('FAIL: bad interface');
    process.exit(0);
}
try { result.destroy(); console.log('PASS'); }
catch(e) { console.log('FAIL: ' + (e as Error).message); }
""")
    assert result == "PASS", f"clickOutside function broken: {result}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "exec", "prettier", "--ignore-path", ".config/.prettierignore",
         "--check", "--config", ".config/.prettierrc.json",
         "--plugin", "prettier-plugin-svelte", "."],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    _ensure_deps()
    # Build client first (required for tests)
    r1 = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r1.returncode == 0, f"Client build failed:\n{r1.stderr[-500:]}"

    r2 = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r2.returncode == 0, f"Unit tests failed:\n{r2.stdout[-1000:]}{r2.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_tests():
    """Repo's client package tests pass (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "test"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Client tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Svelte component integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_svelte_components_use_iframe():
    """Both +page.svelte and ComponentEntry.svelte have iframe rendering paths."""
    for path, name in [(PAGE, "+page.svelte"), (ENTRY, "ComponentEntry.svelte")]:
        assert Path(path).exists(), f"{name} missing"
        src = Path(path).read_text()
        assert "<iframe" in src, f"{name} missing <iframe> element"
        assert any(k in src for k in ("needs_iframe", "use_iframe", "srcdoc")), \
            f"{name} missing iframe logic (needs_iframe/use_iframe/srcdoc)"


# [pr_diff] fail_to_pass
def test_svelte_components_handle_children_slot():
    """Both Svelte files handle @children slot for components that use it."""
    for path, name in [(PAGE, "+page.svelte"), (ENTRY, "ComponentEntry.svelte")]:
        assert Path(path).exists(), f"{name} missing"
        src = Path(path).read_text()
        assert "children" in src, f"{name} does not handle @children slot"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — guide documentation changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_guide_documents_push_to_hub():
    """Guide must document push_to_hub method for sharing components."""
    assert Path(GUIDE).exists(), "Guide file missing"
    content = Path(GUIDE).read_text()
    assert "push_to_hub" in content, "Guide does not document push_to_hub"


# [pr_diff] fail_to_pass
def test_guide_documents_authentication():
    """Guide must document authentication requirements for push_to_hub."""
    assert Path(GUIDE).exists(), "Guide file missing"
    content = Path(GUIDE).read_text()
    assert any(k in content.lower() for k in ("token", "login", "auth")), \
        "Guide does not document authentication"
