"""
Task: vscode-sessions-sidebar-layout
Repo: microsoft/vscode @ 837894c2410fb23371e591be89f64f9a89f73efe

Fix: Sessions sidebar re-layout when toolbar items change dynamically.
Three files changed: aiCustomizationShortcutsWidget.ts, sessionsViewPane.css, sessionsView.ts.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
WIDGET_TS = f"{REPO}/src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts"
SESSIONS_VIEW_TS = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts"
CSS_FILE = f"{REPO}/src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css"


def _run_node(js: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write JavaScript to a temp .cjs file and execute with Node.js."""
    script = Path(f"{REPO}/_eval_tmp.cjs")
    script.write_text(js)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

def test_toolbar_stored_in_variable():
    """MenuWorkbenchToolBar instance stored in const variable so event subscription is possible."""
    r = _run_node("""
const fs = require("fs");
const src = fs.readFileSync("%s", "utf8");

// Walk lines to find a const toolbar declaration that creates a MenuWorkbenchToolBar
const lines = src.split("\\n");
let found = false;
for (const line of lines) {
    if (line.match(/const\\s+toolbar\\s*=/) && line.includes("MenuWorkbenchToolBar")) {
        found = true;
        break;
    }
}
if (!found) {
    console.error("FAIL: MenuWorkbenchToolBar must be stored in a const toolbar variable");
    process.exit(1);
}
console.log("PASS");
""" % WIDGET_TS)
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_toolbar_listens_for_menu_item_changes():
    """Widget subscribes to toolbar.onDidChangeMenuItems to re-layout when items appear/disappear."""
    r = _run_node("""
const fs = require("fs");
const src = fs.readFileSync("%s", "utf8");

// Verify the toolbar event is registered for proper disposal
if (!src.includes("this._register(toolbar.onDidChangeMenuItems")) {
    console.error("FAIL: must register toolbar.onDidChangeMenuItems via this._register for disposal");
    process.exit(1);
}

// Extract the section around onDidChangeMenuItems and verify callback invokes layout change
const start = src.indexOf("toolbar.onDidChangeMenuItems");
const end = src.indexOf(");", start);
if (start === -1 || end === -1) {
    console.error("FAIL: could not locate onDidChangeMenuItems subscription");
    process.exit(1);
}
const subscription = src.slice(start, end);
if (!subscription.includes("onDidChangeLayout")) {
    console.error("FAIL: onDidChangeMenuItems callback must invoke onDidChangeLayout");
    process.exit(1);
}
console.log("PASS");
""" % WIDGET_TS)
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_interface_option_renamed_to_on_did_change_layout():
    """Interface option renamed from onDidToggleCollapse to onDidChangeLayout in widget."""
    r = _run_node("""
const fs = require("fs");
const src = fs.readFileSync("%s", "utf8");

// Parse out the interface body for IAICustomizationShortcutsWidgetOptions
const ifaceMatch = src.match(
    /interface\\s+IAICustomizationShortcutsWidgetOptions\\s*\\{([^}]*)\\}/
);
if (!ifaceMatch) {
    console.error("FAIL: could not find IAICustomizationShortcutsWidgetOptions interface");
    process.exit(1);
}
const ifaceBody = ifaceMatch[1];

if (!ifaceBody.includes("onDidChangeLayout")) {
    console.error("FAIL: interface must expose onDidChangeLayout option");
    process.exit(1);
}
if (ifaceBody.includes("onDidToggleCollapse")) {
    console.error("FAIL: old onDidToggleCollapse must be fully removed from interface");
    process.exit(1);
}
console.log("PASS");
""" % WIDGET_TS)
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_sessions_view_passes_on_did_change_layout():
    """SessionsView passes onDidChangeLayout callback (not old onDidToggleCollapse) to widget."""
    r = _run_node("""
const fs = require("fs");
const src = fs.readFileSync("%s", "utf8");

if (!src.includes("onDidChangeLayout:")) {
    console.error("FAIL: SessionsView must pass onDidChangeLayout: to widget constructor");
    process.exit(1);
}
if (src.includes("onDidToggleCollapse:")) {
    console.error("FAIL: SessionsView must not use old onDidToggleCollapse: key");
    process.exit(1);
}
console.log("PASS");
""" % SESSIONS_VIEW_TS)
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_css_margin_bottom_reduced():
    """CSS margin-bottom for sessions list container reduced from 12px to 6px."""
    r = _run_node("""
const fs = require("fs");
const src = fs.readFileSync("%s", "utf8");

if (!src.includes("margin-bottom: 6px")) {
    console.error("FAIL: sessionsViewPane.css must have margin-bottom: 6px");
    process.exit(1);
}
if (src.includes("margin-bottom: 12px")) {
    console.error("FAIL: old margin-bottom: 12px must be replaced with 6px");
    process.exit(1);
}
console.log("PASS");
""" % CSS_FILE)
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# ---------------------------------------------------------------------------

def test_sidebar_customizations_menu_preserved():
    """Menus.SidebarCustomizations must still be used — toolbar menu ID must not change."""
    content = Path(WIDGET_TS).read_text()
    assert "SidebarCustomizations" in content, (
        "Widget must continue to use Menus.SidebarCustomizations as the toolbar menu; "
        "this identifier should not be removed or renamed by the fix"
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify repo integrity on base commit
# -----------------------------------------------------------------------------

def test_repo_package_json_valid():
    """Root package.json is valid JSON (pass_to_pass)."""
    r = _run_node("""
const fs = require("fs");
try {
    const content = fs.readFileSync("package.json", "utf8");
    JSON.parse(content);
    console.log("PASS");
} catch (e) {
    console.error("FAIL: package.json is not valid JSON:", e.message);
    process.exit(1);
}
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_modified_typescript_files_valid():
    """Modified TypeScript files have valid syntax (pass_to_pass)."""
    r = _run_node("""
const fs = require("fs");
const files = [
    "%s",
    "%s"
];
for (const file of files) {
    try {
        const content = fs.readFileSync(file, "utf8");
        // Basic syntax check: look for obviously broken patterns
        const openBraces = (content.match(/\\{/g) || []).length;
        const closeBraces = (content.match(/\\}/g) || []).length;
        const openParens = (content.match(/\\(/g) || []).length;
        const closeParens = (content.match(/\\)/g) || []).length;
        if (Math.abs(openBraces - closeBraces) > 5) {
            console.error("FAIL: " + file + " has mismatched braces");
            process.exit(1);
        }
        if (Math.abs(openParens - closeParens) > 5) {
            console.error("FAIL: " + file + " has mismatched parentheses");
            process.exit(1);
        }
    } catch (e) {
        console.error("FAIL: Could not read " + file + ": " + e.message);
        process.exit(1);
    }
}
console.log("PASS");
""" % (WIDGET_TS, SESSIONS_VIEW_TS))
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_modified_files_have_copyright():
    """Modified source files have Microsoft copyright header (pass_to_pass)."""
    r = _run_node("""
const fs = require("fs");
const files = [
    "%s",
    "%s",
    "%s"
];
const copyrightPattern = /Copyright.*Microsoft Corporation.*All rights reserved/s;
for (const file of files) {
    try {
        const content = fs.readFileSync(file, "utf8");
        if (!copyrightPattern.test(content)) {
            console.error("FAIL: " + file + " missing Microsoft copyright header");
            process.exit(1);
        }
    } catch (e) {
        console.error("FAIL: Could not read " + file + ": " + e.message);
        process.exit(1);
    }
}
console.log("PASS");
""" % (WIDGET_TS, SESSIONS_VIEW_TS, CSS_FILE))
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_css_files_valid():
    """CSS files have valid syntax (pass_to_pass)."""
    r = _run_node("""
const fs = require("fs");
const cssFile = "%s";
try {
    const content = fs.readFileSync(cssFile, "utf8");
    // Basic CSS validation: check for balanced braces
    const openBraces = (content.match(/\\{/g) || []).length;
    const closeBraces = (content.match(/\\}/g) || []).length;
    if (openBraces !== closeBraces) {
        console.error("FAIL: CSS file has mismatched braces (" + openBraces + " open, " + closeBraces + " close)");
        process.exit(1);
    }
    // Check for unclosed comments
    const openComments = (content.match(/\\/\\*/g) || []).length;
    const closeComments = (content.match(/\\*\\//g) || []).length;
    if (openComments !== closeComments) {
        console.error("FAIL: CSS file has unclosed comments");
        process.exit(1);
    }
    console.log("PASS");
} catch (e) {
    console.error("FAIL: Could not validate CSS:", e.message);
    process.exit(1);
}
""" % CSS_FILE)
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout
