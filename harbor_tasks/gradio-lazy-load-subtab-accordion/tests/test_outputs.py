"""
Task: gradio-lazy-load-subtab-accordion
Repo: gradio-app/gradio @ ccff8b8cacffe36a270fcea9fc8ba29b78c31c8d
PR:   12906

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
INIT_SVELTE = Path(REPO) / "js/core/src/init.svelte.ts"
INIT_TS = Path(REPO) / "js/core/src/_init.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js (CommonJS mode for sloppy eval)."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared boilerplate: extracts make_visible_if_not_rendered from source,
# strips TypeScript annotations, evals it into scope.
_EXTRACT_FN = r"""
const fs = require('fs');
const src = fs.readFileSync('js/core/src/init.svelte.ts', 'utf8');

const marker = 'function make_visible_if_not_rendered';
const startIdx = src.indexOf(marker);
if (startIdx === -1) {
    console.log(JSON.stringify({ error: 'function not found in source' }));
    process.exit(0);
}

// Extract function body via brace counting
let depth = 0, started = false, endIdx = startIdx;
for (let i = startIdx; i < src.length; i++) {
    if (src[i] === '{') { depth++; started = true; }
    if (src[i] === '}') { depth--; }
    if (started && depth === 0) { endIdx = i + 1; break; }
}

let fn = src.substring(startIdx, endIdx);

// Strip TypeScript type annotations to produce valid JS
fn = fn.replace(/:\s*ProcessedComponentMeta/g, '');
fn = fn.replace(/:\s*Set<number>/g, '');
fn = fn.replace(/:\s*void\b/g, '');
fn = fn.replace(/:\s*boolean\b/g, '');

try { eval(fn); } catch(e) {
    console.log(JSON.stringify({ error: 'eval failed: ' + e.message }));
    process.exit(0);
}

function mockNode(id, type, props, children) {
    return {
        id: id,
        type: type,
        props: { shared_props: { visible: false }, props: props || {} },
        children: children || [],
    };
}

function collectVisible(node) {
    const vis = [];
    if (node.props.shared_props.visible) vis.push(node.id);
    (node.children || []).forEach(c => vis.push(...collectVisible(c)));
    return vis;
}
"""


def _eval_make_visible(test_js: str) -> dict:
    """Run extraction boilerplate + given test code, return parsed JSON."""
    r = _run_node(_EXTRACT_FN + test_js)
    assert r.returncode == 0, f"Node.js failed:\n{r.stderr}"
    lines = r.stdout.strip().splitlines()
    assert lines, f"No output from Node.js. stderr: {r.stderr}"
    result = json.loads(lines[-1])
    if "error" in result:
        raise AssertionError(f"Function extraction error: {result['error']}")
    return result


# ---------------------------------------------------------------------------
# Fail-to-pass — tabs should only load selected tab's children
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tabs_selective_visibility():
    """Tabs node with selected='tab-1': only tab-1's children become visible.
    Bug: base commit recurses into ALL children, loading every sub-tab."""
    result = _eval_make_visible(r"""
const t1c = mockNode(101, 'textbox', {}, []);
const t2c = mockNode(201, 'textbox', {}, []);
const t3c = mockNode(301, 'textbox', {}, []);
const tab1 = mockNode(10, 'tabitem', { id: 'tab-1' }, [t1c]);
const tab2 = mockNode(20, 'tabitem', { id: 'tab-2' }, [t2c]);
const tab3 = mockNode(30, 'tabitem', { id: 'tab-3' }, [t3c]);
const tabs = mockNode(1, 'tabs', { selected: 'tab-1' }, [tab1, tab2, tab3]);

const hidden = new Set([1, 10, 20, 30, 101, 201, 301]);
make_visible_if_not_rendered(tabs, hidden);

console.log(JSON.stringify({
    t1c_visible: t1c.props.shared_props.visible,
    t2c_visible: t2c.props.shared_props.visible,
    t3c_visible: t3c.props.shared_props.visible,
    visible_ids: collectVisible(tabs),
}));
""")
    assert result["t1c_visible"] is True, (
        f"Selected tab-1 child should be visible. Visible: {result['visible_ids']}"
    )
    assert result["t2c_visible"] is not True, (
        f"Unselected tab-2 child should NOT be visible. Visible: {result['visible_ids']}"
    )
    assert result["t3c_visible"] is not True, (
        f"Unselected tab-3 child should NOT be visible. Visible: {result['visible_ids']}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass — closed accordion should not load children
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_closed_accordion_lazy_load():
    """Accordion with open=false: children should NOT become visible.
    Bug: base commit always recurses into all children regardless of type."""
    result = _eval_make_visible(r"""
const child1 = mockNode(10, 'textbox', {}, []);
const child2 = mockNode(20, 'image', {}, []);
const accordion = mockNode(1, 'accordion', { open: false }, [child1, child2]);

const hidden = new Set([1, 10, 20]);
make_visible_if_not_rendered(accordion, hidden);

console.log(JSON.stringify({
    accordion_visible: accordion.props.shared_props.visible,
    child1_visible: child1.props.shared_props.visible,
    child2_visible: child2.props.shared_props.visible,
}));
""")
    assert result["accordion_visible"] is True, "Accordion node itself should be visible"
    assert result["child1_visible"] is not True, (
        "Closed accordion's child1 should NOT be visible"
    )
    assert result["child2_visible"] is not True, (
        "Closed accordion's child2 should NOT be visible"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass — tabs initial_tabs fallback selection
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tab_initial_tabs_fallback():
    """Tabs without explicit selected prop should fall back to initial_tabs[0].
    Only that tab's children should be visible."""
    result = _eval_make_visible(r"""
const t1c = mockNode(101, 'textbox', {}, []);
const t2c = mockNode(201, 'textbox', {}, []);
const tab1 = mockNode(10, 'tabitem', { id: 'first-tab' }, [t1c]);
const tab2 = mockNode(20, 'tabitem', { id: 'second-tab' }, [t2c]);
// No 'selected' prop; initial_tabs points to second-tab
const tabs = mockNode(1, 'tabs', { initial_tabs: [{ id: 'second-tab' }] }, [tab1, tab2]);

const hidden = new Set([1, 10, 20, 101, 201]);
make_visible_if_not_rendered(tabs, hidden);

console.log(JSON.stringify({
    t1c_visible: t1c.props.shared_props.visible,
    t2c_visible: t2c.props.shared_props.visible,
}));
""")
    assert result["t2c_visible"] is True, (
        "initial_tabs[0] tab child should be visible"
    )
    assert result["t1c_visible"] is not True, (
        "Non-initial tab child should NOT be visible"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — open accordion still works
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_open_accordion_children_visible():
    """Accordion with open=true (or no open prop): children should still
    become visible — regression check."""
    result = _eval_make_visible(r"""
const child1 = mockNode(10, 'textbox', {}, []);
const acc = mockNode(1, 'accordion', { open: true }, [child1]);
const hidden = new Set([1, 10]);
make_visible_if_not_rendered(acc, hidden);

// Also test with no open prop (default should load children)
const child2 = mockNode(20, 'textbox', {}, []);
const acc2 = mockNode(2, 'accordion', {}, [child2]);
const hidden2 = new Set([2, 20]);
make_visible_if_not_rendered(acc2, hidden2);

console.log(JSON.stringify({
    child1_visible: child1.props.shared_props.visible,
    child2_visible: child2.props.shared_props.visible,
}));
""")
    assert result["child1_visible"] is True, (
        "Open accordion's children should be visible"
    )
    assert result["child2_visible"] is True, (
        "Accordion without explicit open prop should have visible children"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Both modified files exist and have substantial implementations."""
    assert INIT_SVELTE.exists(), "init.svelte.ts not found"
    assert INIT_TS.exists(), "_init.ts not found"

    svelte_src = INIT_SVELTE.read_text()
    assert "make_visible_if_not_rendered" in svelte_src, (
        "make_visible_if_not_rendered not found in init.svelte.ts"
    )
    assert "hidden_on_startup" in svelte_src, (
        "hidden_on_startup parameter not found"
    )

    init_src = INIT_TS.read_text()
    assert "determine_visible_components" in init_src, (
        "determine_visible_components not found in _init.ts"
    )
    assert len(init_src.strip().splitlines()) > 100, "_init.ts appears stubbed"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_vitest_core():
    """Repo's core init tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--config", ".config/vitest.config.ts", "js/core/src/init.test.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Core tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_build():
    """Repo's client package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\n{r.stderr[-500:]}"
