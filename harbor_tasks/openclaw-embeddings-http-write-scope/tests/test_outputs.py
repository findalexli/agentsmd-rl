"""
Task: openclaw-embeddings-http-write-scope
Repo: openclaw/openclaw @ 85647949a484957ba6bac00e47653b0acd4a92d7
PR:   #57721

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import functools
import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/openclaw")
SRC = REPO / "src/gateway/embeddings-http.ts"
BASE_COMMIT = "85647949a484957ba6bac00e47653b0acd4a92d7"

# AST-only because: TypeScript module with heavy Node/gateway deps that can't be imported in pytest.
# Single AST analysis script — extracts all needed facts in one pass via the
# TypeScript compiler API.
_AST_SCRIPT = r"""
const ts = require("typescript");
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
const sf = ts.createSourceFile("test.ts", src, ts.ScriptTarget.Latest, true);

const R = {
  parseErrors: 0,
  hasHandler: false,
  handlerExported: false,
  bodyStatements: 0,
  callsHelper: false,
  hasRequiredOperatorMethod: false,
  requiredOperatorMethodValue: null,
  pathnameValue: null,
  hasAwait: false,
  hasReturn: false,
  callCount: 0,
  anyKeywordCount: 0,
};

R.parseErrors = (sf.parseDiagnostics || []).filter(d => d.category === 1).length;

function propInObject(obj, name) {
  if (!obj || !ts.isObjectLiteralExpression(obj)) return null;
  for (const p of obj.properties) {
    if (ts.isPropertyAssignment(p) && ts.isIdentifier(p.name) && p.name.text === name) return p;
    if (ts.isShorthandPropertyAssignment(p) && p.name.text === name) return p;
  }
  return null;
}

function visitBody(node) {
  if (ts.isAwaitExpression(node)) R.hasAwait = true;
  if (ts.isReturnStatement(node)) R.hasReturn = true;
  if (ts.isCallExpression(node)) {
    R.callCount++;
    const name = ts.isIdentifier(node.expression)
      ? node.expression.text
      : ts.isPropertyAccessExpression(node.expression)
        ? node.expression.name.text
        : "";
    if (name === "handleGatewayPostJsonEndpoint") {
      R.callsHelper = true;
      for (const arg of node.arguments) {
        if (ts.isObjectLiteralExpression(arg)) {
          const rom = propInObject(arg, "requiredOperatorMethod");
          if (rom) {
            R.hasRequiredOperatorMethod = true;
            if (ts.isPropertyAssignment(rom) && ts.isStringLiteral(rom.initializer))
              R.requiredOperatorMethodValue = rom.initializer.text;
          }
          const pn = propInObject(arg, "pathname");
          if (pn && ts.isPropertyAssignment(pn) && ts.isStringLiteral(pn.initializer))
            R.pathnameValue = pn.initializer.text;
          // Accept requiredOperatorMethod via spread
          for (const p of arg.properties) {
            if (ts.isSpreadAssignment(p) && src.includes("requiredOperatorMethod"))
              R.hasRequiredOperatorMethod = true;
          }
        }
      }
    }
  }
  ts.forEachChild(node, visitBody);
}

function visit(node) {
  if (ts.isFunctionDeclaration(node) && node.name &&
      node.name.text === "handleOpenAiEmbeddingsHttpRequest") {
    R.hasHandler = true;
    if (node.modifiers)
      for (const m of node.modifiers)
        if (m.kind === ts.SyntaxKind.ExportKeyword) R.handlerExported = true;
    if (node.body) {
      R.bodyStatements = node.body.statements.length;
      ts.forEachChild(node.body, visitBody);
    }
  }
  if (ts.isExportDeclaration(node) && node.exportClause &&
      ts.isNamedExports(node.exportClause))
    for (const s of node.exportClause.elements)
      if (s.name.text === "handleOpenAiEmbeddingsHttpRequest")
        R.handlerExported = true;
  if (node.kind === ts.SyntaxKind.AnyKeyword) R.anyKeywordCount++;
  ts.forEachChild(node, visit);
}

visit(sf);
process.stdout.write(JSON.stringify(R));
"""


def _run_ast(filepath: str) -> dict:
    """Run TypeScript AST analysis on a file."""
    r = subprocess.run(
        ["node", "-e", _AST_SCRIPT, "--", filepath],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"AST analysis failed:\n{r.stderr}"
    return json.loads(r.stdout)


@functools.lru_cache()
def _ast() -> dict:
    """Run TypeScript AST analysis on current file and cache."""
    return _run_ast(str(SRC))


@functools.lru_cache()
def _base_any_count() -> int:
    """Count any keywords in the base commit version of the file."""
    r = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:src/gateway/embeddings-http.ts"],
        capture_output=True, text=True, timeout=10, cwd=str(REPO),
    )
    if r.returncode != 0:
        return 999  # can't get baseline, skip comparison
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".ts")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(r.stdout)
        base = _run_ast(path)
        return base["anyKeywordCount"]
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — file must parse
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_file_parses():
    """embeddings-http.ts must parse without fatal TypeScript errors."""
    assert SRC.exists(), f"{SRC} not found"
    a = _ast()
    assert a["parseErrors"] <= 5, f"{a['parseErrors']} fatal parse errors"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_embeddings_handler_enforces_scope():
    """handleGatewayPostJsonEndpoint call must include requiredOperatorMethod."""
    a = _ast()
    assert a["callsHelper"], (
        "handleGatewayPostJsonEndpoint is not called in the handler"
    )
    assert a["hasRequiredOperatorMethod"], (
        "requiredOperatorMethod not passed to handleGatewayPostJsonEndpoint — "
        "embeddings endpoint has no scope enforcement"
    )


# [pr_diff] fail_to_pass
def test_scope_method_is_chat_send():
    """requiredOperatorMethod must be 'chat.send' (the canonical write-gated method)."""
    a = _ast()
    assert a["requiredOperatorMethodValue"] == "chat.send", (
        f"Expected requiredOperatorMethod='chat.send', "
        f"got {a['requiredOperatorMethodValue']!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_handler_is_exported():
    """handleOpenAiEmbeddingsHttpRequest must remain an exported function."""
    a = _ast()
    assert a["hasHandler"], "handleOpenAiEmbeddingsHttpRequest function not found"
    assert a["handlerExported"], "handleOpenAiEmbeddingsHttpRequest is not exported"


# [pr_diff] pass_to_pass
def test_pathname_preserved():
    """Helper call must still register pathname '/v1/embeddings'."""
    a = _ast()
    assert a["pathnameValue"] == "/v1/embeddings", (
        f"Expected pathname='/v1/embeddings', got {a['pathnameValue']!r}"
    )


# [static] pass_to_pass
def test_handler_not_stub():
    """Handler must retain substantial logic (not be gutted to a stub)."""
    a = _ast()
    assert a["bodyStatements"] > 8, (
        f"Handler has only {a['bodyStatements']} statements — likely a stub"
    )
    assert a["hasAwait"], "Handler is missing await expressions — likely a stub"
    assert a["hasReturn"], "Handler is missing return statements — likely a stub"
    assert a["callCount"] > 1, (
        f"Handler makes only {a['callCount']} call(s) — likely a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_ts_nocheck():
    """Must not add @ts-nocheck directive (CLAUDE.md:146)."""
    content = SRC.read_text()
    assert "@ts-nocheck" not in content, "@ts-nocheck found in embeddings-http.ts"


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_lint_suppressions():
    """Must not add inline lint suppression comments (CLAUDE.md:146)."""
    content = SRC.read_text()
    base_r = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:src/gateway/embeddings-http.ts"],
        capture_output=True, text=True, timeout=10, cwd=str(REPO),
    )
    base_lines = set(base_r.stdout.splitlines()) if base_r.returncode == 0 else set()
    new_lines = [l for l in content.splitlines() if l not in base_lines]
    suppressions = [
        pat for line in new_lines
        for pat in ("@ts-ignore", "@ts-expect-error", "eslint-disable", "oxlint-ignore")
        if pat in line
    ]
    assert not suppressions, (
        f"Lint suppression(s) found in new lines: {suppressions}"
    )


# [agent_config] pass_to_pass — CLAUDE.md:144 @ 85647949a484957ba6bac00e47653b0acd4a92d7
def test_no_new_explicit_any():
    """Must not introduce new explicit 'any' type annotations (CLAUDE.md:144)."""
    a = _ast()
    baseline = _base_any_count()
    assert a["anyKeywordCount"] <= baseline, (
        f"New 'any' type annotations added: was {baseline}, now {a['anyKeywordCount']}"
    )
