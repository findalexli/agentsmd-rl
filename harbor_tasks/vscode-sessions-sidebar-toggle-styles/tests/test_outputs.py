"""
Task: vscode-sessions-sidebar-toggle-styles
Repo: microsoft/vscode @ d11c632ba8e972176f1bfbe1048b41efbad0b691
PR:   306304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CSS_FILE = Path(f"{REPO}/src/vs/sessions/browser/parts/media/sidebarPart.css")

# Node.js script that parses CSS into structured rules (selector + properties).
# More robust than Python regex: handles comments, multi-line selectors, etc.
_CSS_PARSER_JS = r"""
const fs = require('fs');
const css = fs.readFileSync(process.argv[2], 'utf-8');
const noComments = css.replace(/\/\*[\s\S]*?\*\//g, '');
const rules = [];
let i = 0;
while (i < noComments.length) {
    const openBrace = noComments.indexOf('{', i);
    if (openBrace === -1) break;
    const selector = noComments.slice(i, openBrace).trim();
    if (!selector || selector.includes('@')) { i = openBrace + 1; continue; }
    let depth = 1, j = openBrace + 1;
    while (j < noComments.length && depth > 0) {
        if (noComments[j] === '{') depth++;
        if (noComments[j] === '}') depth--;
        j++;
    }
    const body = noComments.slice(openBrace + 1, j - 1).trim();
    const props = {};
    body.split(';').forEach(decl => {
        const colon = decl.indexOf(':');
        if (colon > 0) {
            const prop = decl.slice(0, colon).trim();
            const val = decl.slice(colon + 1).trim();
            if (prop && val) props[prop] = val;
        }
    });
    rules.push({ selector, properties: props });
    i = j;
}
console.log(JSON.stringify(rules));
"""


def _parse_css_rules() -> list[dict]:
    """Run Node.js to parse the CSS file into structured rules."""
    script = Path(REPO) / "_eval_css_parser.cjs"
    script.write_text(_CSS_PARSER_JS)
    try:
        r = subprocess.run(
            ["node", str(script), str(CSS_FILE)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"CSS parser failed: {r.stderr}"
        return json.loads(r.stdout.strip())
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_css_file_exists():
    """CSS file must exist at the expected path."""
    assert CSS_FILE.exists(), f"CSS file not found: {CSS_FILE}"


def test_css_balanced_braces():
    """CSS must have balanced curly braces (no syntax error)."""
    content = CSS_FILE.read_text()
    assert content.count("{") == content.count("}"), "CSS has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js CSS parsing
# ---------------------------------------------------------------------------

def test_checked_state_styles():
    """Checked toggle button must have active background and border-radius."""
    rules = _parse_css_rules()
    # Find .action-label.checked rules (excluding :hover/:focus variants)
    base_rules = [
        r for r in rules
        if ".action-label.checked" in r["selector"]
        and ":hover" not in r["selector"]
        and ":focus" not in r["selector"]
    ]
    assert base_rules, "No .action-label.checked rule found (excluding :hover/:focus)"

    has_bg = any(
        "var(--vscode-toolbar-activeBackground)" in r["properties"].get("background", "")
        for r in base_rules
    )
    assert has_bg, "Checked state missing background: var(--vscode-toolbar-activeBackground)"

    has_radius = any(
        "var(--vscode-cornerRadius-medium)" in r["properties"].get("border-radius", "")
        for r in base_rules
    )
    assert has_radius, "Checked state missing border-radius: var(--vscode-cornerRadius-medium)"


def test_hover_focus_preserve_background():
    """Hover and focus on checked toggle must preserve active background."""
    rules = _parse_css_rules()

    hover_rules = [
        r for r in rules
        if ".action-label.checked:hover" in r["selector"]
    ]
    assert hover_rules, "No .action-label.checked:hover rule found"
    assert any(
        "var(--vscode-toolbar-activeBackground)" in r["properties"].get("background", "")
        for r in hover_rules
    ), "Hover state does not preserve active background"

    focus_rules = [
        r for r in rules
        if ".action-label.checked:focus" in r["selector"]
    ]
    assert focus_rules, "No .action-label.checked:focus rule found"
    assert any(
        "var(--vscode-toolbar-activeBackground)" in r["properties"].get("background", "")
        for r in focus_rules
    ), "Focus state does not preserve active background"


def test_selector_scoped_to_agent_sessions_sidebar():
    """Checked selector must be scoped to .agent-sessions-workbench .part.sidebar."""
    rules = _parse_css_rules()
    checked_rules = [
        r for r in rules
        if ".action-label.checked" in r["selector"]
    ]
    assert checked_rules, "No .action-label.checked rule found"
    assert any(
        ".agent-sessions-workbench" in r["selector"] and ".part.sidebar" in r["selector"]
        for r in checked_rules
    ), "Checked selector not scoped to .agent-sessions-workbench .part.sidebar"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — .github/copilot-instructions.md
# ---------------------------------------------------------------------------

def test_css_uses_tabs_not_spaces():
    """CSS indentation must use tabs, not spaces.

    Rule from .github/copilot-instructions.md:72 "We use tabs, not spaces."
    Skips block comment lines.
    """
    content = CSS_FILE.read_text()
    in_block_comment = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("/*"):
            in_block_comment = True
        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue
        if line and line[0] == " ":
            raise AssertionError(
                f"Line {i} uses space indentation (expected tab): {line!r}"
            )
