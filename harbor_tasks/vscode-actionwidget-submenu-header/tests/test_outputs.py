"""
Task: vscode-actionwidget-submenu-header
Repo: microsoft/vscode @ ee6bfc559a9089feb8b73962fd4fb5a306821ef4
PR:   306327 — actionWidget: fix submenu group label rendered as item description

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
ACTION_LIST = f"{REPO}/src/vs/platform/actionWidget/browser/actionList.ts"
WORKSPACE_PICKER = f"{REPO}/src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_header_item_pushed_for_labeled_group():
    """actionList.ts pushes ActionListItemKind.Header when a submenu group has a label."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('src/vs/platform/actionWidget/browser/actionList.ts', 'utf8');
const lines = src.split('\n');

let found = false;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].match(/for\s*\(.*groupsWithActions/)) {
        const block = lines.slice(i, i + 30).join('\n');
        if (/if\s*\(\s*group\.label\s*\)/.test(block) &&
            block.includes('submenuItems.push') &&
            block.includes('ActionListItemKind.Header')) {
            found = true;
            break;
        }
    }
}

if (!found) {
    console.error('FAIL: Expected Header push inside if (group.label) in submenu groups loop');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Header push check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_description_no_longer_uses_group_label():
    """Behavioral: evaluates the description expression with mock inputs to verify correct behavior."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('src/vs/platform/actionWidget/browser/actionList.ts', 'utf8');
const lines = src.split('\n');

// Extract the description expression from the inner loop over group.actions
let descExpr = null;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('for (let ci = 0; ci < group.actions.length')) {
        for (let j = i; j < Math.min(i + 15, lines.length); j++) {
            const m = lines[j].match(/^\s*description:\s*(.+?),\s*$/);
            if (m) {
                descExpr = m[1].trim();
                break;
            }
        }
        break;
    }
}

if (!descExpr) {
    console.error('FAIL: Could not extract description expression from submenu item loop');
    process.exit(1);
}

// Evaluate the extracted expression with mock inputs
function evalDescription(ci, child, group) {
    try {
        const fn = new Function('ci', 'child', 'group', 'return ' + descExpr);
        return fn(ci, child, group);
    } catch (e) {
        console.error('FAIL: Cannot evaluate expression: ' + descExpr + ' - ' + e.message);
        process.exit(1);
    }
}

// Test 1: First child (ci=0) with tooltip, group has label
// OLD behavior: returns group.label (wrong)
// NEW behavior: returns child.tooltip (correct)
const r1 = evalDescription(0, { tooltip: 'My Tooltip' }, { label: 'Group Label' });
if (r1 !== 'My Tooltip') {
    console.error('FAIL: ci=0 with tooltip should return tooltip, not group label. Got: ' + r1);
    process.exit(1);
}

// Test 2: Non-first child with tooltip
const r2 = evalDescription(1, { tooltip: 'Other' }, { label: 'Group Label' });
if (r2 !== 'Other') {
    console.error('FAIL: ci=1 should return child.tooltip. Got: ' + r2);
    process.exit(1);
}

// Test 3: Child with no tooltip should return undefined
const r3 = evalDescription(0, { tooltip: undefined }, { label: 'Group Label' });
if (r3 !== undefined) {
    console.error('FAIL: No tooltip should return undefined. Got: ' + r3);
    process.exit(1);
}

// Test 4: Empty string tooltip should also give undefined (empty || undefined)
const r4 = evalDescription(0, { tooltip: '' }, { label: 'Group Label' });
if (r4 !== undefined) {
    console.error('FAIL: Empty tooltip should return undefined. Got: ' + r4);
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Description behavioral test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_workspace_picker_provider_label_moved_to_tooltip():
    """sessionWorkspacePicker.ts: provider.label moved from SubmenuAction label to first-child tooltip."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/chat/browser/sessionWorkspacePicker.ts', 'utf8');

const browseIdx = src.indexOf('workspacePicker.browse');
if (browseIdx === -1) {
    console.error('FAIL: workspacePicker.browse not found');
    process.exit(1);
}

const context = src.substring(browseIdx, browseIdx + 500);

// SubmenuAction label arg must be '' (empty string), not provider.label
if (!/new\s+SubmenuAction\s*\(\s*`[^`]+`,\s*''/.test(context)) {
    console.error('FAIL: SubmenuAction label should be empty string');
    process.exit(1);
}

// provider.label must appear as tooltip for first child (ci === 0)
if (!context.includes("ci === 0 ? provider.label")) {
    console.error('FAIL: provider.label not used as tooltip for first child');
    process.exit(1);
}

// The .map callback must accept ci parameter
if (!/\.map\s*\(\s*\([^)]*\bci\b/.test(context)) {
    console.error('FAIL: .map callback missing ci index parameter');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Workspace picker check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_submenu_action_structure_preserved():
    """sessionWorkspacePicker.ts: SubmenuAction instantiation still exists with browse IDs."""
    src = Path(WORKSPACE_PICKER).read_text()
    assert "new SubmenuAction" in src, "SubmenuAction must still be used in sessionWorkspacePicker.ts"
    assert "workspacePicker.browse" in src, "workspacePicker.browse action IDs must still be present"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ ee6bfc559a9089feb8b73962fd4fb5a306821ef4
def test_tab_indentation_in_modified_file():
    """actionList.ts uses tab indentation as required by VS Code coding guidelines."""
    src = Path(ACTION_LIST).read_text()
    indented_lines = [l for l in src.splitlines() if l and l[0] in ("\t", " ")]
    tab_lines = [l for l in indented_lines if l.startswith("\t")]
    assert len(tab_lines) > 100, (
        f"actionList.ts must use tab indentation (found only {len(tab_lines)} tab-indented lines)"
    )
    space_only_lines = [l for l in indented_lines if l.startswith("    ") and not l.startswith("\t")]
    assert len(tab_lines) > len(space_only_lines) * 10, (
        f"Tab indentation must dominate: {len(tab_lines)} tab lines vs "
        f"{len(space_only_lines)} space-only lines"
    )
