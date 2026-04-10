"""
Task: vscode-chat-tip-sessions-window
Repo: microsoft/vscode @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
PR:   306611

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TIP_FILE = f"{REPO}/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts"


# ---------------------------------------------------------------------------
# Helpers — TypeScript AST extraction via subprocess
# ---------------------------------------------------------------------------

_TS_EXTRACT = r"""
const ts = require('typescript');
const fs = require('fs');

const content = fs.readFileSync('/workspace/vscode/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts', 'utf8');
const src = ts.createSourceFile('chatTipCatalog.ts', content, ts.ScriptTarget.Latest, true);

function findVar(node, name) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) && node.name.text === name && node.initializer) {
        return node.initializer;
    }
    let result;
    ts.forEachChild(node, child => {
        if (!result) result = findVar(child, name);
    });
    return result;
}

const catalog = findVar(src, 'TIP_CATALOG');
if (!catalog || !ts.isArrayLiteralExpression(catalog)) {
    process.stdout.write(JSON.stringify({error: 'TIP_CATALOG not found or not array'}));
    process.exit(0);
}

const entries = catalog.elements.filter(ts.isObjectLiteralExpression).map(elem => {
    const props = {};
    for (const prop of elem.properties) {
        if (!prop.name || !ts.isIdentifier(prop.name)) continue;
        const key = prop.name.text;
        if (ts.isPropertyAssignment(prop) && prop.initializer) {
            const init = prop.initializer;
            props[key] = ts.isStringLiteral(init) ? init.text : init.getText(src);
        } else if (ts.isMethodDeclaration(prop)) {
            props[key] = prop.getText(src);
        }
    }
    return props;
});

const imports = [];
for (const stmt of src.statements) {
    if (ts.isImportDeclaration(stmt) && stmt.importClause && stmt.importClause.namedBindings) {
        const bindings = stmt.importClause.namedBindings;
        if (ts.isNamedImports(bindings)) {
            for (const el of bindings.elements) {
                imports.push(el.name.text);
            }
        }
    }
}

process.stdout.write(JSON.stringify({entries, imports}));
"""


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    # Use .cjs extension to force CommonJS mode (VS Code uses ES modules by default)
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


_cached = None


def _parse_catalog():
    """Parse the TypeScript file via AST and return {entries, imports}."""
    global _cached
    if _cached is not None:
        return _cached
    r = _run_node(_TS_EXTRACT)
    assert r.returncode == 0, f"TypeScript AST extraction failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, f"AST error: {data['error']}"
    _cached = data
    return _cached


def _find_tip(tip_id: str):
    """Find a tip entry by id from the parsed AST."""
    for e in _parse_catalog()["entries"]:
        if e.get("id") == tip_id:
            return e
    return None


def _file_content():
    return Path(TIP_FILE).read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via TypeScript AST
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_tip_id_exists():
    """TIP_CATALOG must contain a tip with id 'tip.openSessionsWindow'."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip is not None, "tip.openSessionsWindow not found in TIP_CATALOG"


# [pr_diff] fail_to_pass
def test_tip_tier_qol():
    """The sessions window tip must have tier ChatTipTier.Qol."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    assert "ChatTipTier.Qol" in tip.get("tier", ""), (
        f"Expected tier ChatTipTier.Qol, got {tip.get('tier')!r}"
    )


# [pr_diff] fail_to_pass
def test_command_link_present():
    """buildMessage must link to workbench.action.openSessionsWindow."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    assert "command:workbench.action.openSessionsWindow" in tip.get("buildMessage", ""), (
        "buildMessage must contain a command link to workbench.action.openSessionsWindow"
    )


# [pr_diff] fail_to_pass
def test_command_link_descriptive_title():
    """Command link must include the title 'Open Sessions Window'."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    assert "Open Sessions Window" in tip.get("buildMessage", ""), (
        "Command link must include descriptive title 'Open Sessions Window'"
    )


# [pr_diff] fail_to_pass
def test_exclude_when_commands_executed():
    """Tip must be excluded once workbench.action.openSessionsWindow is executed."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    val = tip.get("excludeWhenCommandsExecuted", "")
    assert "workbench.action.openSessionsWindow" in val, (
        "excludeWhenCommandsExecuted must reference workbench.action.openSessionsWindow"
    )


# [pr_diff] fail_to_pass
def test_dismiss_when_commands_clicked():
    """Tip must be dismissed once workbench.action.openSessionsWindow is clicked."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    val = tip.get("dismissWhenCommandsClicked", "")
    assert "workbench.action.openSessionsWindow" in val, (
        "dismissWhenCommandsClicked must reference workbench.action.openSessionsWindow"
    )


# [pr_diff] fail_to_pass
def test_when_clause_non_stable():
    """Tip must only appear on non-stable builds via ProductQualityContext.notEqualsTo."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    when = tip.get("when", "")
    assert "ProductQualityContext" in when, (
        "when clause must reference ProductQualityContext"
    )
    assert re.search(r"notEqualsTo\(['\"]stable['\"]\)", when), (
        "when clause must include ProductQualityContext.notEqualsTo('stable')"
    )


# [pr_diff] fail_to_pass
def test_when_clause_not_sessions_window():
    """Tip must be hidden when already in a Sessions Window via IsSessionsWindowContext.negate()."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    when = tip.get("when", "")
    assert "IsSessionsWindowContext" in when, (
        "when clause must reference IsSessionsWindowContext"
    )
    assert "negate()" in when, (
        "when clause must negate IsSessionsWindowContext"
    )


# [pr_diff] fail_to_pass
def test_required_imports():
    """ProductQualityContext and IsSessionsWindowContext must be imported."""
    data = _parse_catalog()
    assert "ProductQualityContext" in data["imports"], (
        "Missing import for ProductQualityContext"
    )
    assert "IsSessionsWindowContext" in data["imports"], (
        "Missing import for IsSessionsWindowContext"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_existing_tips_preserved():
    """Pre-existing tip IDs in TIP_CATALOG must still be present."""
    content = _file_content()
    expected_tips = [
        "tip.switchToAuto",
        "tip.createPrompt",
        "tip.planMode",
        "tip.attachFiles",
        "tip.subagents",
    ]
    for tip_id in expected_tips:
        assert tip_id in content, f"Existing tip removed: {tip_id}"


# [repo_tests] pass_to_pass
def test_repo_eslint_chat():
    """ESLint check on modified chat files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ts_parse_chat():
    """TypeScript file parses without syntax errors (pass_to_pass)."""
    code = """
const ts = require('typescript');
const fs = require('fs');
const file = 'src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts';
const content = fs.readFileSync(file, 'utf8');

// Parse with TypeScript - syntax only check
const src = ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true);

// Check for scanner errors (catches basic syntax issues)
const scanner = ts.createScanner(ts.ScriptTarget.Latest, false, ts.LanguageVariant.Standard, content);
let token = scanner.scan();
let errors = 0;

while (token !== ts.SyntaxKind.EndOfFileToken) {
    if (token === ts.SyntaxKind.Unknown) {
        errors++;
        console.error('Unknown token at position', scanner.getTextPos());
    }
    token = scanner.scan();
}

if (errors > 0) process.exit(1);
console.log('TypeScript parsing OK');
"""
    # Use .cjs extension to force CommonJS mode
    script = Path(REPO) / "_ts_parse_check.cjs"
    script.write_text(code)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"TypeScript parse failed:\n{r.stderr[-500:]}"
    finally:
        script.unlink(missing_ok=True)


# [repo_tests] pass_to_pass
def test_repo_import_check():
    """Import paths in modified file are valid (pass_to_pass)."""
    code = """
const fs = require('fs');
const path = require('path');
const file = 'src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts';
const content = fs.readFileSync(file, 'utf8');

// Extract import paths
const importRegex = /from\\s+['\"]([^'\"]+)['\"];/g;
let match;
const imports = [];
while ((match = importRegex.exec(content)) !== null) {
    imports.push(match[1]);
}

// Check that .js imports exist (without .js extension, as the actual .ts files exist)
const repoRoot = '/workspace/vscode';
let errors = 0;
for (const imp of imports) {
    if (imp.startsWith('.')) {
        // Relative import - resolve and check
        const dir = path.dirname(file);
        const resolved = path.resolve(repoRoot, dir, imp);
        // Check if the file exists (as .ts since we check source)
        const tsPath = resolved.replace(/\\.js$/, '.ts');
        try {
            fs.accessSync(tsPath);
        } catch (e) {
            console.error('Import not found:', imp, '->', tsPath);
            errors++;
        }
    }
}

if (errors > 0) process.exit(1);
console.log('Import check passed:', imports.length, 'imports verified');
"""
    # Use .cjs extension to force CommonJS mode
    script = Path(REPO) / "_import_check.cjs"
    script.write_text(code)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Import check failed:\n{r.stderr[-500:]}"
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — .github/copilot-instructions.md:83 @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
def test_user_facing_string_localized():
    """User-facing tip message must use localize() from vs/nls."""
    tip = _find_tip("tip.openSessionsWindow")
    assert tip, "tip.openSessionsWindow not found"
    assert "localize(" in tip.get("buildMessage", ""), (
        "User-facing strings must be externalized using localize() (copilot-instructions.md)"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:62 @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
def test_uses_tabs_not_spaces():
    """New code must use tabs for indentation, not spaces."""
    content = _file_content()
    idx = content.find("tip.openSessionsWindow")
    if idx == -1:
        raise AssertionError("tip.openSessionsWindow not found")
    start = content.rfind("{", 0, idx)
    end = content.find("}", idx)
    if start == -1 or end == -1:
        raise AssertionError("Could not find tip block boundaries")
    block_lines = content[start:end].split("\n")
    indented = [l for l in block_lines if l and l[0] in (" ", "\t")]
    assert indented, "No indented lines found in tip block"
    space_indented = [l for l in indented if l[0] == " "]
    assert not space_indented, (
        f"Must use tabs, not spaces for indentation (copilot-instructions.md). "
        f"Found {len(space_indented)} space-indented lines"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:119 @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
def test_no_duplicate_imports():
    """Never duplicate imports — reuse existing imports if present."""
    content = _file_content()
    import_lines = [l.strip() for l in content.split("\n") if l.strip().startswith("import ")]
    seen = set()
    for line in import_lines:
        assert line not in seen, (
            f"Duplicate import found: {line} (copilot-instructions.md)"
        )
        seen.add(line)
