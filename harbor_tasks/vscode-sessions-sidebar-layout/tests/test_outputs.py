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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

def test_toolbar_stored_in_variable():
    """MenuWorkbenchToolBar instance stored in const variable so event subscription is possible."""
    src = Path(WIDGET_TS).read_text()
    # Check for const toolbar declaration with MenuWorkbenchToolBar
    found = False
    for line in src.split("\n"):
        if "const" in line and "toolbar" in line and "MenuWorkbenchToolBar" in line:
            found = True
            break
    assert found, "MenuWorkbenchToolBar must be stored in a const toolbar variable"


def test_toolbar_listens_for_menu_item_changes():
    """Widget subscribes to toolbar.onDidChangeMenuItems to re-layout when items appear/disappear."""
    src = Path(WIDGET_TS).read_text()
    # Verify the toolbar event is registered
    assert "toolbar.onDidChangeMenuItems" in src, (
        "must register toolbar.onDidChangeMenuItems via this._register for disposal"
    )
    # Extract the section around onDidChangeMenuItems
    start = src.find("toolbar.onDidChangeMenuItems")
    end = src.find(");", start)
    assert start != -1 and end != -1, "could not locate onDidChangeMenuItems subscription"
    subscription = src[start:end]
    assert "onDidChangeLayout" in subscription, (
        "onDidChangeMenuItems callback must invoke onDidChangeLayout"
    )


def test_interface_option_renamed_to_on_did_change_layout():
    """Interface option renamed from onDidToggleCollapse to onDidChangeLayout in widget."""
    src = Path(WIDGET_TS).read_text()
    # Parse out the interface body
    import re
    iface_match = re.search(
        r"interface\s+IAICustomizationShortcutsWidgetOptions\s*\{([^}]*)\}",
        src, re.DOTALL
    )
    assert iface_match, "could not find IAICustomizationShortcutsWidgetOptions interface"
    iface_body = iface_match.group(1)
    assert "onDidChangeLayout" in iface_body, "interface must expose onDidChangeLayout option"
    assert "onDidToggleCollapse" not in iface_body, (
        "old onDidToggleCollapse must be fully removed from interface"
    )


def test_sessions_view_passes_on_did_change_layout():
    """SessionsView passes onDidChangeLayout callback (not old onDidToggleCollapse) to widget."""
    src = Path(SESSIONS_VIEW_TS).read_text()
    assert "onDidChangeLayout:" in src, (
        "SessionsView must pass onDidChangeLayout: to widget constructor"
    )
    assert "onDidToggleCollapse:" not in src, (
        "SessionsView must not use old onDidToggleCollapse: key"
    )


def test_css_margin_bottom_reduced():
    """CSS margin-bottom for sessions list container reduced from 12px to 6px."""
    src = Path(CSS_FILE).read_text()
    assert "margin-bottom: 6px" in src, "sessionsViewPane.css must have margin-bottom: 6px"
    assert "margin-bottom: 12px" not in src, (
        "old margin-bottom: 12px must be replaced with 6px"
    )


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
# Pass-to-pass (repo_tests) — CI-based repository integrity checks
# These use subprocess.run() with real Node.js commands that work in Docker
# -----------------------------------------------------------------------------

def test_repo_package_json_valid():
    """Root package.json is valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
try {
    const content = fs.readFileSync('package.json', 'utf8');
    JSON.parse(content);
    console.log('PASS');
} catch (e) {
    console.error('FAIL: package.json is not valid JSON:', e.message);
    process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"JSON validation failed:\n{r.stderr}"


def test_repo_modified_typescript_syntax():
    """Modified TypeScript files have valid syntax via Node.js brace/paren balance check (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const files = [
    'src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts',
    'src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts'
];
let allOk = true;
for (const file of files) {
    try {
        const content = fs.readFileSync(file, 'utf8');
        const openBraces = (content.match(/{/g) || []).length;
        const closeBraces = (content.match(/}/g) || []).length;
        const openParens = (content.match(/\\(/g) || []).length;
        const closeParens = (content.match(/\\)/g) || []).length;
        if (Math.abs(openBraces - closeBraces) > 5) {
            console.error('FAIL: ' + file + ' has mismatched braces');
            allOk = false;
        }
        if (Math.abs(openParens - closeParens) > 5) {
            console.error('FAIL: ' + file + ' has mismatched parentheses');
            allOk = false;
        }
    } catch (e) {
        console.error('FAIL: Could not read ' + file + ': ' + e.message);
        allOk = false;
    }
}
process.exit(allOk ? 0 : 1);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr}"


def test_repo_copyright_headers():
    """Modified source files have Microsoft copyright header (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const files = [
    'src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts',
    'src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts',
    'src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css'
];
const copyrightPattern = /Copyright.*Microsoft Corporation.*All rights reserved/s;
let allOk = true;
for (const file of files) {
    try {
        const content = fs.readFileSync(file, 'utf8');
        if (!copyrightPattern.test(content)) {
            console.error('FAIL: ' + file + ' missing Microsoft copyright header');
            allOk = false;
        }
    } catch (e) {
        console.error('FAIL: Could not read ' + file);
        allOk = false;
    }
}
process.exit(allOk ? 0 : 1);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Copyright check failed:\n{r.stderr}"


def test_repo_css_syntax():
    """CSS files have valid syntax - balanced braces and closed comments (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const cssFile = 'src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css';
try {
    const content = fs.readFileSync(cssFile, 'utf8');
    const openBraces = (content.match(/{/g) || []).length;
    const closeBraces = (content.match(/}/g) || []).length;
    const openComments = (content.match(/\\/\\*/g) || []).length;
    const closeComments = (content.match(/\\*\\//g) || []).length;
    if (openBraces !== closeBraces) {
        console.error('FAIL: CSS has mismatched braces');
        process.exit(1);
    }
    if (openComments !== closeComments) {
        console.error('FAIL: CSS has unclosed comments');
        process.exit(1);
    }
    console.log('PASS');
} catch (e) {
    console.error('FAIL: Could not validate CSS:', e.message);
    process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CSS validation failed:\n{r.stderr}"


def test_repo_node_version():
    """Node.js is available and meets minimum version requirement (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const version = process.version;
const major = parseInt(version.slice(1).split('.')[0]);
if (major < 18) {
    console.error('FAIL: Node.js version ' + version + ' is too old (need 18+)');
    process.exit(1);
}
console.log('PASS: Node.js ' + version);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node version check failed:\n{r.stderr}"


def test_repo_file_structure():
    """Modified files exist at expected paths (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const files = [
    'src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts',
    'src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts',
    'src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css',
    'package.json'
];
let allOk = true;
for (const file of files) {
    if (!fs.existsSync(file)) {
        console.error('FAIL: File does not exist: ' + file);
        allOk = false;
    }
}
process.exit(allOk ? 0 : 1);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"File structure check failed:\n{r.stderr}"
