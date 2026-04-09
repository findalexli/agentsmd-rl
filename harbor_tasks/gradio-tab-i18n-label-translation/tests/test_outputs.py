"""
Task: gradio-tab-i18n-label-translation
Repo: gradio-app/gradio @ d720b25b575fb9817311212e1c0afa82abf27468
PR:   12903

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/repo"
FILE = "js/core/src/init.svelte.ts"


# ---------------------------------------------------------------------------
# Pass-to-pass: Repo CI checks (must pass on both base and gold)
# ---------------------------------------------------------------------------


def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\\n{r.stderr[-500:]}"


def test_repo_core_tests():
    """Repo's js/core unit tests pass (pass_to_pass)."""
    # Build client dependency first
    r = subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Client build failed:\\n{r.stderr[-500:]}"

    # Run core module tests
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--config", ".config/vitest.config.ts", "js/core"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Core tests failed:\\n{r.stderr[-500:]}\\n{r.stdout[-1000:]}"

# ---------------------------------------------------------------------------
# Helper: extract _gather_initial_tabs from source, strip TS types, run in Node
# ---------------------------------------------------------------------------

_EXTRACT_JS = textwrap.dedent(r"""
    const fs = require("fs");
    const src = fs.readFileSync(process.env.FILE_PATH, "utf-8");

    const fnRe = /function\s+_gather_initial_tabs\s*\(/;
    const m = fnRe.exec(src);
    if (!m) { console.error("function not found"); process.exit(99); }
    const start = m.index;

    let depth = 0, bodyStart = -1, bodyEnd = -1;
    for (let i = start; i < src.length; i++) {
        if (src[i] === "{") { if (depth === 0) bodyStart = i; depth++; }
        if (src[i] === "}") { depth--; if (depth === 0) { bodyEnd = i + 1; break; } }
    }
    if (bodyEnd === -1) { console.error("unbalanced braces"); process.exit(99); }

    let fnSrc = src.substring(start, bodyEnd);

    // Strip TypeScript type annotations so Node can evaluate
    fnSrc = fnSrc
        .replace(/:\s*ProcessedComponentMeta/g, "")
        .replace(/:\s*Record<[^>]+>/g, "")
        .replace(/:\s*number\s*\|\s*null/g, "")
        .replace(/:\s*void/g, "")
        .replace(/:\s*\(\([^)]*\)\s*=>\s*\w+\)\s*\|\s*\w+/g, "")
        // as casts: complex function types, union types, simple types
        .replace(/\s+as\s+\(\([^)]*\)\s*=>\s*\w+\)\s*\|\s*\w+/g, "")
        .replace(/\s+as\s+\w+\s*\|\s*\w+/g, "")
        .replace(/\s+as\s+\w+(\[\])?/g, "");

    const wrapped = fnSrc + "\nmodule.exports = _gather_initial_tabs;";
    fs.writeFileSync("/tmp/_gather_initial_tabs.js", wrapped);
    console.log("OK");
""")


def _extract_function():
    """Extract and prepare the JS function. Returns True on success."""
    file_path = Path(REPO) / FILE
    assert file_path.exists(), f"{FILE} does not exist"
    r = subprocess.run(
        ["node", "-e", _EXTRACT_JS],
        env={"FILE_PATH": str(file_path), "PATH": "/usr/local/bin:/usr/bin:/bin"},
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Extraction failed: {r.stderr.decode()}"


def _run_node(script: str) -> subprocess.CompletedProcess:
    """Run a Node.js script that uses the extracted function."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=15,
    )
    return r


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """Target file js/core/src/init.svelte.ts must exist and contain _gather_initial_tabs."""
    file_path = Path(REPO) / FILE
    assert file_path.exists(), f"{FILE} does not exist"
    content = file_path.read_text()
    assert "_gather_initial_tabs" in content, "function _gather_initial_tabs not found"


# [static] pass_to_pass
def test_function_extractable():
    """_gather_initial_tabs can be extracted and loaded by Node."""
    _extract_function()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_i18n_translation_applied():
    """Tab label is translated when i18n function is present on the tab node."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");
        const translations = { lion: "Leon", cat: "Gato" };
        const i18nFn = (s) => translations[s] || s;

        function makeTab(id, label) {
            return {
                type: "tabitem", id,
                props: {
                    shared_props: { label, elem_id: "t-"+id, visible: true, interactive: true, scale: null },
                    props: { id: String(id), i18n: i18nFn }
                },
                children: []
            };
        }

        const tabsNode = {
            type: "tabs", id: 100,
            props: { shared_props: {}, props: {} },
            children: [makeTab(1, "lion"), makeTab(2, "cat")]
        };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        const tabs = initial_tabs[100] || [];
        const result = { labels: tabs.map(t => t.label), count: tabs.length };
        console.log(JSON.stringify(result));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["count"] == 2, f"Expected 2 tabs, got {result['count']}"
    assert result["labels"] == ["Leon", "Gato"], f"Labels not translated: {result['labels']}"


# [pr_diff] fail_to_pass
def test_i18n_function_actually_called():
    """The i18n function is invoked (not just checked for existence) — spy verifies call count."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");

        let callCount = 0;
        const spy = (s) => { callCount++; return s.toUpperCase(); };

        const tabItem = {
            type: "tabitem", id: 50,
            props: {
                shared_props: { label: "hello", elem_id: "t-50", visible: true, interactive: true, scale: null },
                props: { id: "50", i18n: spy }
            },
            children: []
        };
        const tabsNode = { type: "tabs", id: 300, props: { shared_props: {}, props: {} }, children: [tabItem] };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        const tab = (initial_tabs[300] || [])[0];
        const result = { label: tab ? tab.label : null, calls: callCount };
        console.log(JSON.stringify(result));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["calls"] > 0, "i18n function was never called"
    assert result["label"] == "HELLO", f"Expected HELLO, got {result['label']}"


# [pr_diff] fail_to_pass
def test_multiple_tabs_all_translated():
    """Three tabs with different i18n translations all get translated correctly."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");
        const tr = { lion: "Leon", tiger: "Tigre", bear: "Oso" };
        const i18n = (s) => tr[s] || s;

        function makeTab(id, label) {
            return {
                type: "tabitem", id,
                props: {
                    shared_props: { label, elem_id: "t-"+id, visible: true, interactive: true, scale: null },
                    props: { id: String(id), i18n }
                },
                children: []
            };
        }

        const tabsNode = {
            type: "tabs", id: 200,
            props: { shared_props: {}, props: {} },
            children: [makeTab(1, "lion"), makeTab(2, "tiger"), makeTab(3, "bear")]
        };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        const labels = (initial_tabs[200] || []).map(t => t.label);
        console.log(JSON.stringify({ labels }));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["labels"] == ["Leon", "Tigre", "Oso"], f"Labels: {result['labels']}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_i18n_raw_label_preserved():
    """When no i18n function is present, the raw label is preserved (backward compat)."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");

        const tabItem = {
            type: "tabitem", id: 60,
            props: {
                shared_props: { label: "Settings", elem_id: "t-60", visible: true, interactive: true, scale: null },
                props: { id: "60" }  // NO i18n
            },
            children: []
        };
        const tabsNode = { type: "tabs", id: 400, props: { shared_props: {}, props: {} }, children: [tabItem] };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        const tab = (initial_tabs[400] || [])[0];
        console.log(JSON.stringify({ label: tab ? tab.label : null }));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["label"] == "Settings", f"Expected 'Settings', got {result['label']}"


# [pr_diff] pass_to_pass
def test_other_tab_properties_preserved():
    """All tab properties (id, elem_id, visible, interactive, component_id) still collected."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");

        const tabItem = {
            type: "tabitem", id: 70,
            props: {
                shared_props: { label: "Tab1", elem_id: "my-tab", visible: false, interactive: true, scale: 2 },
                props: { id: "70", i18n: (s) => "translated_" + s }
            },
            children: []
        };
        const tabsNode = { type: "tabs", id: 500, props: { shared_props: {}, props: {} }, children: [tabItem] };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        const tab = (initial_tabs[500] || [])[0];
        console.log(JSON.stringify(tab || null));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    tab = json.loads(r.stdout.decode().strip())
    assert tab is not None, "No tab collected"
    assert tab["id"] == "70"
    assert tab["elem_id"] == "my-tab"
    assert tab["visible"] is False
    assert tab["interactive"] is True
    assert tab["component_id"] == 70


# [pr_diff] pass_to_pass
def test_nested_tabs_traversal():
    """Nested tabs (tabs inside tabitem) are still collected correctly via recursive traversal."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");

        const innerTabItem = {
            type: "tabitem", id: 81,
            props: {
                shared_props: { label: "Inner", elem_id: "inner", visible: true, interactive: true, scale: null },
                props: { id: "81" }
            },
            children: []
        };
        const innerTabs = { type: "tabs", id: 80, props: { shared_props: {}, props: {} }, children: [innerTabItem] };
        const column = { type: "column", id: 79, props: { shared_props: {}, props: {} }, children: [innerTabs] };
        const outerTabItem = {
            type: "tabitem", id: 78,
            props: {
                shared_props: { label: "Outer", elem_id: "outer", visible: true, interactive: true, scale: null },
                props: { id: "78" }
            },
            children: [column]
        };
        const outerTabs = { type: "tabs", id: 77, props: { shared_props: {}, props: {} }, children: [outerTabItem] };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [outerTabs] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        console.log(JSON.stringify({
            outer: (initial_tabs[77] || []).map(t => t.label),
            inner: (initial_tabs[80] || []).map(t => t.label)
        }));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["outer"] == ["Outer"], f"Outer tabs: {result['outer']}"
    assert result["inner"] == ["Inner"], f"Inner tabs: {result['inner']}"


# [pr_diff] pass_to_pass
def test_non_tabitem_nodes_skipped():
    """Non-tabitem children of a tabs node are skipped without error."""
    _extract_function()
    r = _run_node(textwrap.dedent(r"""
        const fn = require("/tmp/_gather_initial_tabs.js");

        const rowChild = {
            type: "row", id: 90,
            props: { shared_props: { label: "NotATab" }, props: {} },
            children: []
        };
        const tabItem = {
            type: "tabitem", id: 91,
            props: {
                shared_props: { label: "RealTab", elem_id: "rt", visible: true, interactive: true, scale: null },
                props: { id: "91" }
            },
            children: []
        };
        const tabsNode = {
            type: "tabs", id: 600,
            props: { shared_props: {}, props: {} },
            children: [rowChild, tabItem]
        };
        const root = { type: "column", id: 0, props: { shared_props: {}, props: {} }, children: [tabsNode] };
        const initial_tabs = {};
        fn(root, initial_tabs, null, null);

        const tabs = initial_tabs[600] || [];
        console.log(JSON.stringify({ count: tabs.length, label: tabs[0] ? tabs[0].label : null }));
    """))
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    result = json.loads(r.stdout.decode().strip())
    assert result["count"] == 1, f"Expected 1 tab, got {result['count']}"
    assert result["label"] == "RealTab"
