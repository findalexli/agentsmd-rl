"""
Task: opencode-session-context-prompt-footer
Repo: anomalyco/opencode @ 15a8c22a263b072a23e2fc0b2e840b2e12c220aa
PR:   #19486

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
PROMPT_FILE = f"{REPO}/packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx"
SESSION_FILE = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
HEADER_FILE = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/header.tsx"
APP_FILE = f"{REPO}/packages/opencode/src/cli/cmd/tui/app.tsx"


def _node(script: str) -> str:
    """Run a node -e script and return stdout, stripped."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=30, text=True,
    )
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified files must parse as valid TypeScript (no syntax errors)."""
    result = _node("""
const ts = require('typescript');
const fs = require('fs');
let ok = true;
for (const f of [%s]) {
  if (!fs.existsSync(f)) continue;
  const src = fs.readFileSync(f, 'utf8');
  const sf = ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
    console.error('Parse error in ' + f + ': ' + sf.parseDiagnostics[0].messageText);
    ok = false;
  }
}
console.log(ok ? '1' : '0');
""" % ", ".join(f"'{f}'" for f in [PROMPT_FILE, SESSION_FILE, APP_FILE]))
    assert result == "1", "TypeScript parse errors in modified files"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: header removal
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_header_file_deleted():
    """header.tsx must be deleted — the core refactor removes this file."""
    assert not Path(HEADER_FILE).exists(), (
        f"header.tsx still exists at {HEADER_FILE}"
    )


# [pr_diff] fail_to_pass
def test_session_no_header_import():
    """session/index.tsx must not import or render the Header component."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('session.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasHeaderImport = false;
let hasHeaderJsx = false;
function visit(node) {
  if (ts.isImportDeclaration(node)) {
    const mod = node.moduleSpecifier.getText(sf).replace(/["']/g, '');
    if (/header/i.test(mod)) hasHeaderImport = true;
  }
  if (ts.isJsxSelfClosingElement(node) || ts.isJsxOpeningElement(node)) {
    const tag = node.tagName.getText(sf);
    if (tag === 'Header') hasHeaderJsx = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(!hasHeaderImport && !hasHeaderJsx ? '1' : '0');
""" % SESSION_FILE)
    assert result == "1", "session/index.tsx still has Header import or JSX"


# [pr_diff] fail_to_pass
def test_session_no_header_toggle():
    """session/index.tsx must not have header toggle state (showHeader/header_visible)."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('session.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let found = false;
function visit(node) {
  if (ts.isCallExpression(node)) {
    const text = node.getText(sf);
    if (/header_visible/.test(text) || /showHeader/.test(text)) found = true;
  }
  if (ts.isVariableDeclaration(node) && /showHeader|setShowHeader/.test(node.name.getText(sf))) {
    found = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(!found ? '1' : '0');
""" % SESSION_FILE)
    assert result == "1", "session/index.tsx still has header toggle state"


# [pr_diff] fail_to_pass
def test_session_no_toggle_header_command():
    """session/index.tsx must not have the toggle header command palette entry."""
    src = Path(SESSION_FILE).read_text()
    assert "session.toggle.header" not in src, (
        "session/index.tsx still has session.toggle.header command"
    )


# [pr_diff] fail_to_pass
def test_variant_cycle_not_hidden():
    """variant.cycle command must not be hidden in app.tsx."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('app.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let result = '0';
function visit(node) {
  if (ts.isObjectLiteralExpression(node)) {
    let isVariantCycle = false;
    let isHidden = false;
    for (const prop of node.properties) {
      if (ts.isPropertyAssignment(prop)) {
        const name = prop.name.getText(sf);
        const val = prop.initializer.getText(sf);
        if (name === 'value' && /variant\.cycle/.test(val)) isVariantCycle = true;
        if (name === 'hidden' && val === 'true') isHidden = true;
      }
    }
    if (isVariantCycle && !isHidden) result = '1';
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(result);
""" % APP_FILE)
    assert result == "1", "variant.cycle command is still hidden in app.tsx"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — prompt footer functionality
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prompt_has_usage_computation():
    """prompt/index.tsx must compute token usage (tokens, context %, aggregation).
    AST-only because: SolidJS TUI component with reactive runtime — cannot import/call outside Solid context."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

function checkBody(node) {
  const text = node.getText(sf);
  const hasTokenRef = /token|usage|input_tokens|output_tokens|cache_read|cache_write/.test(text);
  const hasArith = /[\+\-\*\/]|reduce|sum|total|forEach|\.map/.test(text);
  let stmtCount = 0;
  function countStmts(n) {
    if (ts.isExpressionStatement(n) || ts.isVariableStatement(n) ||
        ts.isReturnStatement(n) || ts.isIfStatement(n) ||
        ts.isForStatement(n) || ts.isForOfStatement(n)) stmtCount++;
    ts.forEachChild(n, countStmts);
  }
  countStmts(node);
  return hasTokenRef && hasArith && stmtCount >= 3;
}

let found = false;
function visit(node) {
  if (ts.isCallExpression(node)) {
    const callee = node.expression.getText(sf);
    if (/createMemo|createEffect|createComputed/.test(callee) && node.arguments.length > 0) {
      if (checkBody(node.arguments[0])) found = true;
    }
  }
  if ((ts.isArrowFunction(node) || ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node)) && node.body) {
    if (checkBody(node.body)) found = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(found ? '1' : '0');
""" % PROMPT_FILE)
    assert result == "1", "prompt/index.tsx missing token usage computation"


# [pr_diff] fail_to_pass
def test_prompt_formats_cost_as_currency():
    """prompt/index.tsx must format cost as currency (USD)."""
    src = Path(PROMPT_FILE).read_text()
    # Strip comments
    code = re.sub(r'//.*$', '', src, flags=re.MULTILINE)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)

    has_intl = bool(re.search(r'Intl\.NumberFormat[^;]*currency', code, re.DOTALL))
    has_locale = bool(re.search(r'toLocaleString[^;]*currency', code, re.DOTALL))
    has_format = bool(re.search(r'\.format\(', code) and re.search(r'currency', code, re.IGNORECASE))

    assert has_intl or has_locale or has_format, (
        "prompt/index.tsx has no currency formatting (expected Intl.NumberFormat or toLocaleString with currency)"
    )


# [pr_diff] fail_to_pass
def test_prompt_displays_usage_in_footer():
    """prompt/index.tsx must render usage data (context/cost) in the footer area.
    The PR adds a conditional display: show usage when available, fall back to hints."""
    src = Path(PROMPT_FILE).read_text()
    code = re.sub(r'//.*$', '', src, flags=re.MULTILINE)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)

    # The footer must reference computed usage/context/cost in JSX
    has_usage_ref = bool(re.search(r'usage\(\)|context\(\)|cost\(\)', code))
    # Must have some conditional rendering (Switch/Match, Show, or ternary) around usage
    has_conditional = bool(re.search(r'<(Match|Show)\s+when=\{.*?(usage|context|cost)', code, re.DOTALL))
    # Fallback: also accept ternary-based conditional rendering
    has_ternary = bool(re.search(r'(usage|context|cost)\(\)\s*[?&]', code))

    assert has_usage_ref and (has_conditional or has_ternary), (
        "prompt/index.tsx does not display usage data in footer (expected conditional rendering of usage/context/cost)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (regression + anti-stub)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_prompt_exports_prompt_function():
    """prompt/index.tsx must export the Prompt function."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let found = false;
function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'Prompt') {
    const mods = ts.getModifiers(node) || [];
    if (mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) found = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(found ? '1' : '0');
""" % PROMPT_FILE)
    assert result == "1", "prompt/index.tsx does not export Prompt function"


# [static] pass_to_pass
def test_session_exports_session_function():
    """session/index.tsx must export the Session function."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('session.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let found = false;
function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'Session') {
    const mods = ts.getModifiers(node) || [];
    if (mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) found = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(found ? '1' : '0');
""" % SESSION_FILE)
    assert result == "1", "session/index.tsx does not export Session function"


# [static] pass_to_pass
def test_prompt_not_stubbed():
    """prompt/index.tsx must have substantial content (>500 lines)."""
    lines = Path(PROMPT_FILE).read_text().splitlines()
    assert len(lines) > 500, f"prompt/index.tsx only has {len(lines)} lines — likely stubbed"


# [static] pass_to_pass
def test_session_not_stubbed():
    """session/index.tsx must have substantial content (>300 lines)."""
    lines = Path(SESSION_FILE).read_text().splitlines()
    assert len(lines) > 300, f"session/index.tsx only has {len(lines)} lines — likely stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:12 @ 15a8c22a263b072a23e2fc0b2e840b2e12c220aa
def test_no_try_catch_in_new_code():
    """Avoid try/catch where possible (AGENTS.md:12). New usage computation should not use try/catch.
    AST-only because: SolidJS TUI component — checking structural constraint on new code."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let tryCatchCount = 0;
function visit(node) {
  if (ts.isTryStatement(node)) tryCatchCount++;
  ts.forEachChild(node, visit);
}
visit(sf);
// Allow at most 2 try/catch in the whole file (some may pre-exist)
console.log(tryCatchCount <= 2 ? '1' : '0');
""" % PROMPT_FILE)
    assert result == "1", "prompt/index.tsx has excessive try/catch blocks (AGENTS.md:12 says avoid)"


# [agent_config] pass_to_pass — AGENTS.md:13 @ 15a8c22a263b072a23e2fc0b2e840b2e12c220aa
def test_minimal_any_type():
    """New/modified code should avoid using the `any` type (AGENTS.md:13)."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let count = 0;
function visit(node) {
  if (node.kind === ts.SyntaxKind.AnyKeyword) count++;
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(count < 5 ? '1' : '0');
""" % PROMPT_FILE)
    assert result == "1", "prompt/index.tsx uses `any` type excessively"


# [agent_config] pass_to_pass — AGENTS.md:70 @ 15a8c22a263b072a23e2fc0b2e840b2e12c220aa
def test_const_preferred_over_let():
    """New/modified code should prefer const over let (AGENTS.md:70)."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let letCount = 0, constCount = 0;
function visit(node) {
  if (ts.isVariableDeclarationList(node)) {
    if (node.flags & ts.NodeFlags.Let) letCount++;
    if (node.flags & ts.NodeFlags.Const) constCount++;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(constCount > letCount ? '1' : '0');
""" % PROMPT_FILE)
    assert result == "1", "prompt/index.tsx uses let more than const"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 15a8c22a263b072a23e2fc0b2e840b2e12c220aa
def test_no_else_in_prompt():
    """Avoid else statements; prefer early returns (AGENTS.md:84).
    AST-only because: SolidJS TUI component — checking structural constraint."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let elseCount = 0;
function visit(node) {
  if (ts.isIfStatement(node) && node.elseStatement) {
    // Allow else-if chains, only count plain else blocks
    if (!ts.isIfStatement(node.elseStatement)) elseCount++;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
// Allow at most 3 plain else blocks in the whole file (some may pre-exist)
console.log(elseCount <= 3 ? '1' : '0');
""" % PROMPT_FILE)
    assert result == "1", "prompt/index.tsx has excessive else blocks (AGENTS.md:84 says prefer early returns)"
