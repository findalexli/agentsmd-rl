"""
Task: vscode-submenu-header-label
Repo: microsoft/vscode @ 29f5047784335d81e143570a307f75f7800c603a
PR:   306327

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
ACTIONLIST = Path(f"{REPO}/src/vs/platform/actionWidget/browser/actionList.ts")
PICKER = Path(f"{REPO}/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts")


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Node.js code in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via TypeScript AST analysis
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_header_item_emitted_for_labeled_groups():
    """actionList.ts pushes a Header item when a submenu group has a label."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/platform/actionWidget/browser/actionList.ts', 'utf8');
const sf = ts.createSourceFile('actionList.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isIfStatement(node)) {
        const cond = src.substring(node.expression.getStart(sf), node.expression.end).trim();
        if (cond === 'group.label') {
            const body = src.substring(node.thenStatement.getStart(sf), node.thenStatement.end);
            if (body.includes('ActionListItemKind.Header') && body.includes('.push(')) {
                found = true;
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (found) console.log('PASS');
else { console.error('No if(group.label) block pushes a Header item'); process.exit(1); }
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_description_simplified_to_child_tooltip():
    """description field uses child.tooltip only, not ci===0 && group.label conditional."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/platform/actionWidget/browser/actionList.ts', 'utf8');
const sf = ts.createSourceFile('actionList.ts', src, ts.ScriptTarget.Latest, true);

let oldPatternFound = false;
let newPatternFound = false;

function visit(node) {
    if (ts.isPropertyAssignment(node)) {
        const name = node.name.getText(sf);
        if (name === 'description') {
            const val = node.initializer.getText(sf);
            if (val.includes('ci') && val.includes('group.label')) oldPatternFound = true;
            if (val.trim() === 'child.tooltip || undefined') newPatternFound = true;
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (oldPatternFound) { console.error('Old ci===0 && group.label pattern still in description'); process.exit(1); }
if (!newPatternFound) { console.error('Expected description: child.tooltip || undefined'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_session_picker_submenu_label_cleared():
    """SubmenuAction in sessionWorkspacePicker.ts uses empty string as label, not provider.label."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts', 'utf8');
const sf = ts.createSourceFile('picker.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isNewExpression(node) && node.expression.getText(sf) === 'SubmenuAction') {
        const args = node.arguments;
        if (args && args.length >= 2) {
            const secondArg = args[1].getText(sf).trim();
            if (secondArg === "''" || secondArg === '""') {
                found = true;
            } else if (secondArg.includes('provider.label')) {
                console.error('SubmenuAction still uses provider.label as label: ' + secondArg);
                process.exit(1);
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (found) console.log('PASS');
else { console.error('SubmenuAction second arg is not empty string'); process.exit(1); }
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_session_picker_provider_label_in_first_child_tooltip():
    """Provider label is passed as tooltip of the first child action (ci === 0)."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts', 'utf8');
const sf = ts.createSourceFile('picker.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isPropertyAssignment(node) && node.name.getText(sf) === 'tooltip') {
        const val = node.initializer.getText(sf).trim();
        if (val.includes('ci') && val.includes('provider.label')) {
            found = true;
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (found) console.log('PASS');
else { console.error('tooltip does not use ci === 0 ? provider.label pattern'); process.exit(1); }
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_header_push_uses_group_label_variable():
    """Header item uses group.label variable for both label and group.title (not hardcoded)."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/platform/actionWidget/browser/actionList.ts', 'utf8');
const sf = ts.createSourceFile('actionList.ts', src, ts.ScriptTarget.Latest, true);

let labelOk = false;
let titleOk = false;

function visit(node) {
    if (ts.isIfStatement(node)) {
        const cond = src.substring(node.expression.getStart(sf), node.expression.end).trim();
        if (cond === 'group.label') {
            const body = src.substring(node.thenStatement.getStart(sf), node.thenStatement.end);
            if (/label:\\s*group\\.label/.test(body)) labelOk = true;
            if (/title:\\s*group\\.label/.test(body)) titleOk = true;
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!labelOk) { console.error('Header push missing label: group.label'); process.exit(1); }
if (!titleOk) { console.error('Header push missing title: group.label'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — coding convention checks
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:113 @ 29f5047784335d81e143570a307f75f7800c603a
def test_conditional_uses_curly_braces():
    """if (group.label) block must use curly braces per VS Code coding guidelines."""
    content = ACTIONLIST.read_text()
    assert re.search(r'if\s*\(\s*group\.label\s*\)\s*\{', content), \
        "if (group.label) conditional missing required curly braces"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — indentation convention
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ 29f5047784335d81e143570a307f75f7800c603a
def test_indentation_uses_tabs():
    """actionList.ts uses tab indentation per VS Code coding guidelines (tabs, not spaces)."""
    content = ACTIONLIST.read_text()
    indented = [l for l in content.splitlines() if l and l[0] in (' ', '\t')]
    assert indented, "No indented lines found in actionList.ts"
    tab_lines = sum(1 for l in indented if l.startswith('\t'))
    space_lines = sum(1 for l in indented if l.startswith('    '))
    assert tab_lines > space_lines * 5, \
        f"File uses spaces instead of tabs: {tab_lines} tab-indented vs {space_lines} space-indented lines"
