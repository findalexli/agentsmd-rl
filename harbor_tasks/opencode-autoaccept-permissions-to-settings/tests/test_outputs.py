"""
Task: opencode-autoaccept-permissions-to-settings
Repo: anomalyco/opencode @ c2d2ca352252a922354c89bfbdb135cf1abfe1b6
PR:   #21308

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PROMPT_INPUT = f"{REPO}/packages/app/src/components/prompt-input.tsx"
SETTINGS_GENERAL = f"{REPO}/packages/app/src/components/settings-general.tsx"
PACKAGES_APP = f"{REPO}/packages/app"


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
""" % ", ".join(f"'{f}'" for f in [PROMPT_INPUT, SETTINGS_GENERAL]))
    assert result == "1", "TypeScript parse errors in modified files"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_permissions_button_removed_from_composer():
    """prompt-input.tsx must NOT render a data-action="prompt-permissions" button.
    The auto-accept toggle should be moved out of the composer."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt-input.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let found = false;
function visit(node) {
  // Check for data-action="prompt-permissions" in JSX attributes
  if (ts.isJsxAttribute(node) && node.name.getText(sf) === 'data-action') {
    const init = node.initializer;
    if (init && ts.isStringLiteral(init) && init.text === 'prompt-permissions') {
      found = true;
    }
  }
  // Also check string literals that contain the selector
  if (ts.isStringLiteral(node) && node.text.includes('prompt-permissions')) {
    found = true;
  }
  if (ts.isNoSubstitutionTemplateLiteral(node) && node.text.includes('prompt-permissions')) {
    found = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(!found ? '1' : '0');
""" % PROMPT_INPUT)
    assert result == "1", "prompt-input.tsx still contains prompt-permissions data-action"


# [pr_diff] fail_to_pass
def test_auto_accept_toggle_in_settings():
    """settings-general.tsx must render a data-action="settings-auto-accept-permissions"
    element with a Switch component for the auto-accept toggle."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('settings-general.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasDataAction = false;
let hasSwitch = false;
function visit(node) {
  if (ts.isJsxAttribute(node) && node.name.getText(sf) === 'data-action') {
    const init = node.initializer;
    if (init && ts.isStringLiteral(init) && init.text === 'settings-auto-accept-permissions') {
      hasDataAction = true;
    }
  }
  if ((ts.isJsxSelfClosingElement(node) || ts.isJsxOpeningElement(node)) &&
      node.tagName.getText(sf) === 'Switch') {
    // Check if this Switch has an onChange or checked prop
    for (const attr of node.attributes.properties) {
      if (ts.isJsxAttribute(attr)) {
        const name = attr.name.getText(sf);
        if (name === 'checked' || name === 'onChange') hasSwitch = true;
      }
    }
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(hasDataAction && hasSwitch ? '1' : '0');
""" % SETTINGS_GENERAL)
    assert result == "1", (
        "settings-general.tsx missing auto-accept-permissions data-action or Switch component"
    )


# [pr_diff] fail_to_pass
def test_settings_uses_permission_context():
    """settings-general.tsx must import and use the permission context to read/write
    auto-accept state."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('settings-general.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let importsPermission = false;
let usesPermission = false;
function visit(node) {
  if (ts.isImportDeclaration(node)) {
    const mod = node.moduleSpecifier.getText(sf).replace(/["']/g, '');
    if (/permission/.test(mod)) {
      const clause = node.importClause;
      if (clause && clause.namedBindings && ts.isNamedImports(clause.namedBindings)) {
        for (const spec of clause.namedBindings.elements) {
          if (spec.name.text === 'usePermission') importsPermission = true;
        }
      }
    }
  }
  // Check for usePermission() call
  if (ts.isCallExpression(node) && node.expression.getText(sf) === 'usePermission') {
    usesPermission = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(importsPermission && usesPermission ? '1' : '0');
""" % SETTINGS_GENERAL)
    assert result == "1", "settings-general.tsx does not import/use usePermission"


# [pr_diff] fail_to_pass
def test_settings_toggle_handles_session_and_directory():
    """settings-general.tsx must handle both session-level and directory-level
    permission toggling — it needs toggleAutoAcceptDirectory for the directory case
    and enableAutoAccept/disableAutoAccept (or toggleAutoAccept) for the session case."""
    src = Path(SETTINGS_GENERAL).read_text()
    has_directory = "toggleAutoAcceptDirectory" in src
    has_session = ("enableAutoAccept" in src and "disableAutoAccept" in src) or "toggleAutoAccept" in src
    assert has_directory, "settings-general.tsx missing directory-level permission toggle"
    assert has_session, "settings-general.tsx missing session-level permission toggle"


# [pr_diff] fail_to_pass
def test_prompt_toggle_accept_removed():
    """prompt-input.tsx must no longer define its own toggleAccept function
    or acceptLabel memo — these are moved to settings."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('prompt-input.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let hasToggleAccept = false;
let hasAcceptLabel = false;
function visit(node) {
  if (ts.isVariableDeclaration(node)) {
    const name = node.name.getText(sf);
    if (name === 'toggleAccept') hasToggleAccept = true;
    if (name === 'acceptLabel') hasAcceptLabel = true;
  }
  ts.forEachChild(node, visit);
}
visit(sf);
console.log(!hasToggleAccept && !hasAcceptLabel ? '1' : '0');
""" % PROMPT_INPUT)
    assert result == "1", "prompt-input.tsx still has toggleAccept or acceptLabel"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_prompt_input_not_stubbed():
    """prompt-input.tsx must have substantial content (>1000 lines)."""
    lines = Path(PROMPT_INPUT).read_text().splitlines()
    assert len(lines) > 1000, f"prompt-input.tsx only has {len(lines)} lines — likely stubbed"


# [static] pass_to_pass
def test_settings_general_not_stubbed():
    """settings-general.tsx must have substantial content (>100 lines)."""
    lines = Path(SETTINGS_GENERAL).read_text().splitlines()
    assert len(lines) > 100, f"settings-general.tsx only has {len(lines)} lines — likely stubbed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — bun typecheck
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes via bun typecheck (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "--cwd", PACKAGES_APP, "typecheck"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — prompt-input unit tests
def test_repo_prompt_input_tests():
    """prompt-input unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--preload", "./happydom.ts", "./src/components/prompt-input"],
        capture_output=True, text=True, timeout=60, cwd=PACKAGES_APP,
    )
    assert r.returncode == 0, f"prompt-input tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass — permission context unit tests
def test_repo_permission_tests():
    """permission context unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--preload", "./happydom.ts", "./src/context/permission-auto-respond.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PACKAGES_APP,
    )
    assert r.returncode == 0, f"permission tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ c2d2ca352252a922354c89bfbdb135cf1abfe1b6
def test_no_any_type_in_settings():
    """Avoid using the `any` type (AGENTS.md). settings-general.tsx should not
    introduce new `any` type annotations."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('settings-general.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let count = 0;
function visit(node) {
  if (node.kind === ts.SyntaxKind.AnyKeyword) count++;
  ts.forEachChild(node, visit);
}
visit(sf);
// Allow at most 2 (pre-existing), but no excessive any usage
console.log(count <= 2 ? '1' : '0');
""" % SETTINGS_GENERAL)
    assert result == "1", "settings-general.tsx uses `any` type excessively (AGENTS.md says avoid)"


# [agent_config] pass_to_pass — AGENTS.md:70 @ c2d2ca352252a922354c89bfbdb135cf1abfe1b6
def test_prefer_const_in_settings():
    """Prefer const over let (AGENTS.md). New code in settings-general.tsx should
    use const more than let."""
    result = _node(r"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('%s', 'utf8');
const sf = ts.createSourceFile('settings-general.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

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
""" % SETTINGS_GENERAL)
    assert result == "1", "settings-general.tsx uses let more than const (AGENTS.md says prefer const)"

# [repo_tests] pass_to_pass — prettier check
def test_repo_prettier_check():
    """Modified files are correctly formatted with prettier (pass_to_pass)."""
    r = subprocess.run(
        ["bunx", "prettier", "--check", 
         "packages/app/src/components/prompt-input.tsx",
         "packages/app/src/components/settings-general.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
