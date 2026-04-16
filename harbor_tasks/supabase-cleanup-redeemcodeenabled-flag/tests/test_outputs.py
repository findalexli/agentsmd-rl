"""
Task: supabase-cleanup-redeemcodeenabled-flag
Repo: supabase @ 421eaedd508d86c7502f954c0a4f619d4458e844
PR:   44563

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"

CREDIT_FILE = (
    f"{REPO}/apps/studio/components/interfaces/Organization/"
    "BillingSettings/CreditCodeRedemption.tsx"
)
REDEEM_FILE = f"{REPO}/apps/studio/pages/redeem.tsx"


def _run_node(script: str) -> subprocess.CompletedProcess:
    """Execute a Node.js script and return the result."""
    env = {**os.environ, "NODE_PATH": "/usr/local/lib/node_modules"}
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30, env=env,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors (TypeScript parser)."""
    for fpath in [CREDIT_FILE, REDEEM_FILE]:
        script = (
            "const ts = require('typescript');\n"
            f"const source = require('fs').readFileSync({fpath!r}, 'utf8');\n"
            "const sf = ts.createSourceFile('file.tsx', source, "
            "ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
            "if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {\n"
            "  sf.parseDiagnostics.forEach(d => console.error(d.messageText));\n"
            "  process.exit(1);\n"
            "}\n"
            "console.log('OK');\n"
        )
        r = _run_node(script)
        assert r.returncode == 0, f"Parse error in {fpath}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_feature_flag_removed_from_credit_code_redemption():
    """CreditCodeRedemption must always render — no if-guard that returns null."""
    # Uses the TypeScript compiler API to walk the AST and detect any
    # if-statement whose body contains `return null` (the feature-flag
    # guard pattern).  Any correct fix removes this guard.
    script = (
        "const ts = require('typescript');\n"
        f"const source = require('fs').readFileSync({CREDIT_FILE!r}, 'utf8');\n"
        "const sf = ts.createSourceFile('file.tsx', source, "
        "ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        "let guardFound = false;\n"
        "function visit(node) {\n"
        "  if (ts.isIfStatement(node)) {\n"
        "    const body = node.thenStatement.getText(sf).trim();\n"
        "    if (/return\\s+null/.test(body)) guardFound = true;\n"
        "  }\n"
        "  ts.forEachChild(node, visit);\n"
        "}\n"
        "visit(sf);\n"
        "if (guardFound) {\n"
        "  console.error('FAIL: component has an if-guard that returns null');\n"
        "  process.exit(1);\n"
        "}\n"
        "console.log('PASS');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, (
        f"CreditCodeRedemption still has a guard returning null:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_feature_flag_removed_from_redeem_page():
    """Redeem page must show org cards unconditionally — no 'coming soon' fallback."""
    # 1. AST check: no string literal with "coming soon" (user-visible text).
    # 2. AST check: no ternary where org.map() is gated with Admonition fallback.
    script = (
        "const ts = require('typescript');\n"
        f"const source = require('fs').readFileSync({REDEEM_FILE!r}, 'utf8');\n"
        "const sf = ts.createSourceFile('file.tsx', source, "
        "ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        "\n"
        "let comingSoonFound = false;\n"
        "function visitText(node) {\n"
        "  if ((ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node))\n"
        "      && node.text.toLowerCase().includes('coming soon')) {\n"
        "    comingSoonFound = true;\n"
        "  }\n"
        "  if (ts.isJsxText(node) && node.text.toLowerCase().includes('coming soon')) {\n"
        "    comingSoonFound = true;\n"
        "  }\n"
        "  ts.forEachChild(node, visitText);\n"
        "}\n"
        "visitText(sf);\n"
        "if (comingSoonFound) {\n"
        "  console.error('FAIL: page still has coming-soon text');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "let gatedRendering = false;\n"
        "function visitGate(node) {\n"
        "  if (ts.isConditionalExpression(node)) {\n"
        "    const wt = node.whenTrue.getText(sf);\n"
        "    const wf = node.whenFalse.getText(sf);\n"
        "    if (wt.includes('.map(') && wf.includes('Admonition')) {\n"
        "      gatedRendering = true;\n"
        "    }\n"
        "  }\n"
        "  ts.forEachChild(node, visitGate);\n"
        "}\n"
        "visitGate(sf);\n"
        "if (gatedRendering) {\n"
        "  console.error('FAIL: org listing gated behind conditional with Admonition fallback');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "console.log('PASS');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, (
        f"Redeem page still has feature-flag gating:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_useflag_import_cleaned_up():
    """useFlag must not be imported from 'common' in the modified files."""
    # Parses import declarations via the TypeScript AST and checks that
    # no named import of 'useFlag' exists from the 'common' module.
    script = (
        "const ts = require('typescript');\n"
        "const fs = require('fs');\n"
        f"const files = [{CREDIT_FILE!r}, {REDEEM_FILE!r}];\n"
        "let fail = false;\n"
        "for (const fp of files) {\n"
        "  const source = fs.readFileSync(fp, 'utf8');\n"
        "  const sf = ts.createSourceFile('file.tsx', source, "
        "ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        "  ts.forEachChild(sf, node => {\n"
        "    if (ts.isImportDeclaration(node)) {\n"
        "      const mod = node.moduleSpecifier.getText(sf).replace(/['\"]/g, '');\n"
        "      if (mod === 'common') {\n"
        "        const clause = node.importClause;\n"
        "        if (clause && clause.namedBindings && ts.isNamedImports(clause.namedBindings)) {\n"
        "          for (const el of clause.namedBindings.elements) {\n"
        "            if (el.name.getText(sf) === 'useFlag') {\n"
        "              console.error('FAIL: useFlag still imported from common in ' + fp);\n"
        "              fail = true;\n"
        "            }\n"
        "          }\n"
        "        }\n"
        "      }\n"
        "    }\n"
        "  });\n"
        "}\n"
        "if (fail) process.exit(1);\n"
        "console.log('PASS');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"useFlag import not cleaned up:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def _install_deps():
    """Install dependencies using pnpm via corepack."""
    return subprocess.run(
        ["bash", "-c",
         "cd /workspace/supabase && corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Studio TypeScript typecheck passes (pass_to_pass)."""
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c",
         "NODE_OPTIONS='--max-old-space-size=4096' pnpm --filter studio run typecheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Studio typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Studio ESLint passes (pass_to_pass)."""
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "pnpm --filter studio run lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Studio lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_lint_ratchet():
    """Studio lint ratchet passes (pass_to_pass)."""
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "pnpm --filter studio run lint:ratchet"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Studio lint:ratchet failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Code formatting check passes (pass_to_pass)."""
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "pnpm run test:prettier"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Studio unit tests (stable subset) pass (pass_to_pass)."""
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c",
         "cd apps/studio && pnpm vitest run --exclude '**/Support/**'"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified components still have real rendering logic — not stubs."""
    # Walks JSX elements via the TypeScript AST to verify the components
    # still render their expected UI elements (Dialog, OrganizationCard).
    script = (
        "const ts = require('typescript');\n"
        "const fs = require('fs');\n"
        "\n"
        f"const creditSrc = fs.readFileSync({CREDIT_FILE!r}, 'utf8');\n"
        "const creditSf = ts.createSourceFile('file.tsx', creditSrc, "
        "ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        "let hasDialog = false, hasReturn = false;\n"
        "function vc(node) {\n"
        "  if (ts.isJsxOpeningElement(node) || ts.isJsxSelfClosingElement(node)) {\n"
        "    if (node.tagName.getText(creditSf) === 'Dialog') hasDialog = true;\n"
        "  }\n"
        "  if (ts.isReturnStatement(node)) hasReturn = true;\n"
        "  ts.forEachChild(node, vc);\n"
        "}\n"
        "vc(creditSf);\n"
        "if (!hasDialog) { console.error('FAIL: no Dialog in CreditCodeRedemption'); process.exit(1); }\n"
        "if (!hasReturn) { console.error('FAIL: no return in CreditCodeRedemption'); process.exit(1); }\n"
        "\n"
        f"const redeemSrc = fs.readFileSync({REDEEM_FILE!r}, 'utf8');\n"
        "const redeemSf = ts.createSourceFile('file.tsx', redeemSrc, "
        "ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        "let hasOrgCard = false;\n"
        "function vr(node) {\n"
        "  if (ts.isJsxOpeningElement(node) || ts.isJsxSelfClosingElement(node)) {\n"
        "    if (node.tagName.getText(redeemSf) === 'OrganizationCard') hasOrgCard = true;\n"
        "  }\n"
        "  ts.forEachChild(node, vr);\n"
        "}\n"
        "vr(redeemSf);\n"
        "if (!hasOrgCard) { console.error('FAIL: no OrganizationCard in redeem.tsx'); process.exit(1); }\n"
        "console.log('PASS');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"Components appear stubbed:\n{r.stderr}"
