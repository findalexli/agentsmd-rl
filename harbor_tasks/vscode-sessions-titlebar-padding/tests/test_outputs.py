"""
Task: vscode-sessions-titlebar-padding
Repo: microsoft/vscode @ f8c32042ed5206d294fe73f1a3b2b74cd3f7bb7a

The fix adds a CSS rule that removes left padding on the sessions titlebar
container when the sidebar is visible (controlled by the absence of .nosidebar
workbench class). LAYOUT.md is also updated with documentation and a changelog
entry.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CSS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css")
DOCS_FILE = Path(f"{REPO}/src/vs/sessions/LAYOUT.md")


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using Node.js CSS parsing
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_css_cascade_sidebar_visible_padding():
    """Node.js parses CSS and verifies the nosidebar override sets padding-left: 0 on the titlebar container."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const css = readFileSync(
    'src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css',
    'utf8'
);

// Parse all CSS rule blocks: selector { properties }
const rules = [];
const ruleRegex = /([^{}]+)\{([^}]*)\}/g;
let match;
while ((match = ruleRegex.exec(css)) !== null) {
    const selector = match[1].trim();
    const props = {};
    match[2].split(';').forEach(decl => {
        const [prop, ...valParts] = decl.split(':');
        if (prop && valParts.length) {
            props[prop.trim()] = valParts.join(':').trim();
        }
    });
    rules.push({ selector, props });
}

// Find rule that matches: workbench:not(.nosidebar) ... .agent-sessions-titlebar-container
const overrideRule = rules.find(r =>
    r.selector.includes(':not(.nosidebar)') &&
    r.selector.includes('agent-sessions-titlebar-container')
);

if (!overrideRule) {
    console.error('NO_SIDEBAR_OVERRIDE_RULE');
    process.exit(1);
}

// Verify padding-left is set to 0
const paddingLeft = overrideRule.props['padding-left'];
if (!paddingLeft || paddingLeft !== '0') {
    console.error('WRONG_PADDING: got ' + JSON.stringify(paddingLeft));
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"CSS cascade check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_css_selector_specificity():
    """Node.js verifies the override selector chains workbench > command-center > container in correct order."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const css = readFileSync(
    'src/vs/sessions/contrib/sessions/browser/media/sessionsTitleBarWidget.css',
    'utf8'
);

// Parse selectors
const ruleRegex = /([^{}]+)\{[^}]*\}/g;
let match;
const selectors = [];
while ((match = ruleRegex.exec(css)) !== null) {
    selectors.push(match[1].trim());
}

// Find the nosidebar override selector
const overrideSel = selectors.find(s =>
    s.includes(':not(.nosidebar)') &&
    s.includes('agent-sessions-titlebar-container')
);

if (!overrideSel) {
    console.error('NO_OVERRIDE_SELECTOR');
    process.exit(1);
}

// Must include .command-center for correct cascade scoping
if (!overrideSel.includes('.command-center')) {
    console.error('MISSING_COMMAND_CENTER_SCOPE');
    process.exit(1);
}

// Verify descendant order: workbench:not(.nosidebar) before .command-center before container
const workbenchPos = overrideSel.indexOf(':not(.nosidebar)');
const centerPos = overrideSel.indexOf('.command-center');
const containerPos = overrideSel.indexOf('agent-sessions-titlebar-container');

if (!(workbenchPos < centerPos && centerPos < containerPos)) {
    console.error('WRONG_SELECTOR_ORDER');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"CSS selector check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_layout_md_documents_nosidebar_padding():
    """Node.js verifies LAYOUT.md documents the sidebar-aware padding behavior."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const docs = readFileSync('src/vs/sessions/LAYOUT.md', 'utf8');

if (!docs.includes('nosidebar')) {
    console.error('MISSING_NOSIDEBAR_MENTION');
    process.exit(1);
}
if (!docs.includes('padding-left')) {
    console.error('MISSING_PADDING_LEFT_MENTION');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"LAYOUT.md check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_base_css_rule_preserved():
    """The original .agent-sessions-titlebar-container base rule must still exist."""
    css = CSS_FILE.read_text()
    has_base = (
        ".agent-sessions-titlebar-container {" in css
        or ".agent-sessions-titlebar-container{" in css
    )
    assert has_base, (
        "Base .agent-sessions-titlebar-container rule is missing — "
        "the fix must not delete existing rules"
    )
