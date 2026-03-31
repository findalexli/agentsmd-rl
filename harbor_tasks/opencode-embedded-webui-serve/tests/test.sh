#!/usr/bin/env bash
set -uo pipefail

TOTAL=0
EARNED=0

check() {
  local weight=$1 desc=$2
  shift 2
  TOTAL=$(python3 -c "print($TOTAL + $weight)")
  if "$@" >/dev/null 2>&1; then
    EARNED=$(python3 -c "print($EARNED + $weight)")
    echo "PASS ($weight): $desc"
  else
    echo "FAIL ($weight): $desc"
  fi
}

gate() {
  local desc=$1
  shift
  if ! "$@" >/dev/null 2>&1; then
    echo "GATE FAIL: $desc"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
  fi
  echo "GATE PASS: $desc"
}

cd /repo

# ── GATE: syntax check ──────────────────────────────────────────────
# [pr_diff] (gate): All changed files must parse without syntax errors
gate "flag.ts parses" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/flag/flag.ts', 'utf8');
  ts.createSourceFile('flag.ts', src, ts.ScriptTarget.Latest, true);
"

gate "server.ts parses" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);
"

gate "build.ts parses" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/script/build.ts', 'utf8');
  ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);
"

# ── Fail-to-pass: behavioral tests ─────────────────────────────────

# [pr_diff] (0.20): Flag module exports OPENCODE_DISABLE_EMBEDDED_WEB_UI
# Behavioral: import the module, verify export exists and is falsy by default
check 0.20 "Flag OPENCODE_DISABLE_EMBEDDED_WEB_UI exported and falsy by default" bun eval "
  const { Flag } = await import('./packages/opencode/src/flag/flag.ts');
  if (typeof Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI === 'undefined') {
    throw new Error('OPENCODE_DISABLE_EMBEDDED_WEB_UI not exported from Flag namespace');
  }
  // Should be falsy by default when env var is not set
  if (Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI) {
    throw new Error('Flag should be falsy when env var is not set');
  }
"

# [pr_diff] (0.10): Flag responds to environment variable correctly
# Behavioral: run with env var set, verify truthy return
check 0.10 "Flag is truthy when OPENCODE_DISABLE_EMBEDDED_WEB_UI=1" bash -c '
  cd /repo && OPENCODE_DISABLE_EMBEDDED_WEB_UI=1 bun eval "
    const { Flag } = await import(\"./packages/opencode/src/flag/flag.ts\");
    if (!Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI) {
      throw new Error(\"Flag should be truthy when env var is set to 1\");
    }
  "
'

# [pr_diff] (0.20): Server catch-all route branches on embedded UI availability
# Structural via TS AST: verify .all("/*") callback has conditional branching + file serving
check 0.20 "Server catch-all has embedded UI branch with file serving" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

  // Find .all('/*', callback) via AST (not string search)
  let catchAllCb = null;
  function findAll(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
      if (node.expression.name.text === 'all' && node.arguments.length >= 2) {
        const first = node.arguments[0];
        if (ts.isStringLiteral(first) && first.text === '/*') {
          catchAllCb = node.arguments[1];
        }
      }
    }
    ts.forEachChild(node, findAll);
  }
  findAll(sf);
  if (!catchAllCb) throw new Error('No .all(\"/*\", ...) catch-all route found in AST');

  // Callback must have at least one if-statement (branching on embedded vs proxy)
  let hasIf = false;
  function findIf(node) {
    if (ts.isIfStatement(node) || ts.isConditionalExpression(node)) hasIf = true;
    ts.forEachChild(node, findIf);
  }
  ts.forEachChild(catchAllCb, findIf);
  if (!hasIf) throw new Error('Catch-all route has no conditional branching');

  // Callback must have file-serving via property access (Bun.file, .arrayBuffer, .body, .readFile etc.)
  let hasFileOp = false;
  function findFileOp(node) {
    if (ts.isPropertyAccessExpression(node)) {
      const n = node.name.text;
      if (['file','arrayBuffer','readFile','body','readFileSync','blob'].includes(n)) hasFileOp = true;
    }
    ts.forEachChild(node, findFileOp);
  }
  ts.forEachChild(catchAllCb, findFileOp);
  if (!hasFileOp) throw new Error('Catch-all route has no file-serving operation');
"

# [pr_diff] (0.10): Build script has --skip-embed-web-ui flag as actual code
# Structural via TS AST: verify string literal '--skip-embed-web-ui' exists in code (not comments)
check 0.10 "Build script parses --skip-embed-web-ui flag" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/script/build.ts', 'utf8');
  const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

  let found = false;
  function visit(node) {
    if (ts.isStringLiteral(node) && node.text === '--skip-embed-web-ui') found = true;
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (!found) throw new Error('No --skip-embed-web-ui string literal in build.ts AST');
"

# [pr_diff] (0.10): Build script has asset bundling function with file scanning
# Structural via TS AST: function/arrow with Glob/scan usage + substantial body
check 0.10 "Build script has asset bundling function" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/script/build.ts', 'utf8');
  const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

  // Find a function (declaration or arrow) that:
  // 1) Contains a 'Glob' or 'scan' or 'readdir' identifier in its body
  // 2) Has at least 3 statements (not a stub)
  let hasBundler = false;
  function visit(node) {
    const isFn = ts.isFunctionDeclaration(node) || ts.isArrowFunction(node) || ts.isFunctionExpression(node);
    if (isFn && node.body) {
      let hasFileScan = false;
      let stmtCount = 0;
      function inner(n) {
        if (ts.isIdentifier(n) && ['Glob','glob','scan','readdir','readdirSync'].includes(n.text)) {
          hasFileScan = true;
        }
        ts.forEachChild(n, inner);
      }
      inner(node.body);
      if (ts.isBlock(node.body)) stmtCount = node.body.statements.length;
      if (hasFileScan && stmtCount >= 3) hasBundler = true;
    }
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (!hasBundler) throw new Error('No asset-bundling function with file scanning and >=3 statements found');
"

# [pr_diff] (0.05): CSP header set for embedded HTML responses
# Structural via TS AST: 'Content-Security-Policy' string literal in code
check 0.05 "Content-Security-Policy header in server code" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

  let found = false;
  function visit(node) {
    if (ts.isStringLiteral(node) && node.text === 'Content-Security-Policy') found = true;
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (!found) throw new Error('No Content-Security-Policy string literal in server.ts AST');
"

# ── Pass-to-pass: existing behavior preserved ───────────────────────

# [pr_diff] (0.10): Proxy fallback to app.opencode.ai preserved
# Structural via TS AST: string literal containing 'app.opencode.ai' exists in code
check 0.10 "Proxy fallback to app.opencode.ai preserved" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

  let found = false;
  function visit(node) {
    if (ts.isStringLiteral(node) && node.text.includes('app.opencode.ai')) found = true;
    if (ts.isNoSubstitutionTemplateLiteral(node) && node.text.includes('app.opencode.ai')) found = true;
    if (ts.isTemplateHead(node) && node.text.includes('app.opencode.ai')) found = true;
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (!found) throw new Error('Proxy target app.opencode.ai not found as string literal in AST');
"

# [pr_diff] (0.05): SPA fallback to index.html in catch-all route
# Structural via TS AST: 'index.html' string literal exists in code
check 0.05 "SPA fallback to index.html" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

  let found = false;
  function visit(node) {
    if (ts.isStringLiteral(node) && node.text === 'index.html') found = true;
    ts.forEachChild(node, visit);
  }
  visit(sf);
  if (!found) throw new Error('No index.html string literal in server.ts AST');
"

# ── Config-derived checks ──────────────────────────────────────────

# [agent_config] (0.05): "Avoid try/catch where possible" — AGENTS.md:12
# Verify dynamic import uses .catch() promise chain, not try/catch block
check 0.05 "Embedded import uses .catch() not try/catch" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

  // Find dynamic import() call expressions
  let importNodes = [];
  function findImports(node) {
    if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
      importNodes.push(node);
    }
    ts.forEachChild(node, findImports);
  }
  findImports(sf);
  if (importNodes.length === 0) throw new Error('No dynamic import() found in server.ts');

  // Check that at least one dynamic import is in a .catch() call chain
  let hasCatchOnImport = false;
  function findCatch(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
      if (node.expression.name.text === 'catch') {
        // Walk the left side of .catch() to see if it contains import()
        let hasImport = false;
        function walkLeft(n) {
          if (ts.isCallExpression(n) && n.expression.kind === ts.SyntaxKind.ImportKeyword) hasImport = true;
          ts.forEachChild(n, walkLeft);
        }
        walkLeft(node.expression.expression);
        if (hasImport) hasCatchOnImport = true;
      }
    }
    ts.forEachChild(node, findCatch);
  }
  findCatch(sf);
  if (!hasCatchOnImport) throw new Error('Dynamic import is not followed by .catch() in promise chain');
"

# ── Structural: anti-stub ──────────────────────────────────────────

# [pr_diff] (0.05): Server catch-all is not a stub — callback has real depth
check 0.05 "Server catch-all route has sufficient complexity (anti-stub)" bun eval "
  const ts = require('typescript');
  const src = require('fs').readFileSync('packages/opencode/src/server/server.ts', 'utf8');
  const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

  let cbSize = 0;
  let stmtCount = 0;
  function findAll(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
      if (node.expression.name.text === 'all' && node.arguments.length >= 2) {
        const first = node.arguments[0];
        if (ts.isStringLiteral(first) && first.text === '/*') {
          const cb = node.arguments[1];
          cbSize = cb.end - cb.pos;
          // Count statements in callback body
          function countStmts(n) {
            if (ts.isExpressionStatement(n) || ts.isReturnStatement(n) ||
                ts.isVariableStatement(n) || ts.isIfStatement(n)) stmtCount++;
            ts.forEachChild(n, countStmts);
          }
          ts.forEachChild(cb, countStmts);
        }
      }
    }
    ts.forEachChild(node, findAll);
  }
  findAll(sf);
  if (cbSize < 200) throw new Error('Catch-all callback too small (' + cbSize + ' chars)');
  if (stmtCount < 4) throw new Error('Catch-all has only ' + stmtCount + ' statements — likely a stub');
"

# ── Compute reward ──────────────────────────────────────────────────

REWARD=$(python3 -c "print(round($EARNED / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $EARNED / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

cat > /logs/verifier/reward.json <<RJSON
{"reward": $REWARD, "behavioral": $(python3 -c "print(round(0.30 * $REWARD, 4))"), "regression": $(python3 -c "print(round(0.15 * $REWARD, 4))"), "config": $(python3 -c "print(round(0.05 * $REWARD, 4))"), "structural": $(python3 -c "print(round(0.50 * $REWARD, 4))")}
RJSON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
