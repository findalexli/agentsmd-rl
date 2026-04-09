"""
Task: opencode-tui-worker-sse-bypass
Repo: anomalyco/opencode @ 1d363fa19fe9c1445f635498da48211bf09cbc97
PR:   19183

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = "/repo"
WORKER = f"{REPO}/packages/opencode/src/cli/cmd/tui/worker.ts"

# Node.js global modules path — typescript installed via npm install -g
_NODE_ENV = {**os.environ, "NODE_PATH": "/usr/local/lib/node_modules"}

# Node.js AST analysis script — runs once via session fixture.
# Uses the TypeScript compiler API to walk real AST nodes (not string matching),
# so keyword stuffing in comments/strings won't game the checks.
_AST_SCRIPT = r"""
const ts = require("typescript");
const fs = require("fs");

const src = fs.readFileSync(process.argv[1], "utf8");
const sf = ts.createSourceFile("worker.ts", src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);

if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
  console.log(JSON.stringify({ syntax_error: true }));
  process.exit(0);
}

const checks = { syntax_ok: true };

function findVarDecl(name) {
  let result = null;
  function visit(node) {
    if (result) return;
    if (ts.isVariableDeclaration(node) &&
        ts.isIdentifier(node.name) &&
        node.name.text === name) {
      result = node;
    }
    ts.forEachChild(node, visit);
  }
  ts.forEachChild(sf, visit);
  return result;
}

function collectCalls(node) {
  const calls = [];
  function visit(n) {
    if (ts.isCallExpression(n)) calls.push(n.expression.getText(sf));
    ts.forEachChild(n, visit);
  }
  if (node) visit(node);
  return calls;
}

function collectNews(node) {
  const news = [];
  function visit(n) {
    if (ts.isNewExpression(n)) news.push(n.expression.getText(sf));
    ts.forEachChild(n, visit);
  }
  if (node) visit(node);
  return news;
}

function collectAccesses(node) {
  const acc = [];
  function visit(n) {
    if (ts.isPropertyAccessExpression(n)) acc.push(n.getText(sf));
    ts.forEachChild(n, visit);
  }
  if (node) visit(node);
  return acc;
}

function countMeaningful(node) {
  let count = 0;
  function visit(n) {
    if (ts.isExpressionStatement(n) || ts.isVariableStatement(n) ||
        ts.isIfStatement(n) || ts.isReturnStatement(n) ||
        ts.isWhileStatement(n) || ts.isForStatement(n) ||
        ts.isCallExpression(n) || ts.isNewExpression(n) ||
        ts.isAwaitExpression(n) || ts.isConditionalExpression(n)) {
      count++;
    }
    ts.forEachChild(n, visit);
  }
  if (node) visit(node);
  return count;
}

const streamDecl = findVarDecl("startEventStream");
checks.stream_exists = !!streamDecl;

if (!streamDecl || !streamDecl.initializer) {
  checks.bus_subscribe = false;
  checks.workspace_provide = false;
  checks.instance_provide = false;
  checks.instance_disposed = false;
  checks.sse_removed = true;
  checks.sdk_subscribe_removed = true;
  checks.bus_imported = false;
  checks.workspace_imported = false;
  checks.rpc_exports = false;
  checks.global_bus = false;
  checks.abort_cleanup = false;
  checks.not_stub = false;
  checks.no_any_type = true;
  checks.const_over_let = true;
  checks.no_else = true;
  checks.no_try_catch = true;
  console.log(JSON.stringify(checks));
  process.exit(0);
}

const streamInit = streamDecl.initializer;
const callsInStream = collectCalls(streamInit);
const accessesInStream = collectAccesses(streamInit);

const allCalls = collectCalls(sf);
const allNews = collectNews(sf);
const allAccesses = collectAccesses(sf);

// F2P: Bus.subscribe/subscribeAll in startEventStream
checks.bus_subscribe = callsInStream.some(c => /^Bus\s*\.\s*subscribe(All)?$/.test(c));

// F2P: WorkspaceContext.provide in startEventStream
checks.workspace_provide = callsInStream.some(c => /^WorkspaceContext\s*\.\s*provide$/.test(c));

// F2P: Instance.provide in startEventStream
checks.instance_provide = callsInStream.some(c => /^Instance\s*\.\s*provide$/.test(c));

// F2P: InstanceDisposed referenced in startEventStream
checks.instance_disposed = accessesInStream.some(a => /InstanceDisposed/.test(a));

// F2P: createOpencodeClient removed from entire file
checks.sse_removed = !allCalls.some(c => c === "createOpencodeClient");

// F2P: sdk.event.subscribe removed from startEventStream
checks.sdk_subscribe_removed = !callsInStream.some(c =>
  /^sdk\s*\.\s*event\s*\.\s*subscribe$/.test(c));

// F2P: Bus imported from real @/bus module
let busMod = "";
let wsMod = "";
ts.forEachChild(sf, n => {
  if (ts.isImportDeclaration(n)) {
    const spec = n.moduleSpecifier;
    if (ts.isStringLiteral(spec)) {
      const modPath = spec.text;
      const importText = n.getText(sf);
      if (/\/bus/.test(modPath) && /\bBus\b/.test(importText) && !/GlobalBus/.test(importText)) {
        busMod = modPath;
      }
      if (/workspace/.test(modPath) && /WorkspaceContext/.test(importText)) {
        wsMod = modPath;
      }
    }
  }
});

function resolveImport(modPath) {
  const base = "packages/opencode/src/";
  let resolved = modPath.replace(/^@\//, base);
  for (const ext of [".ts", ".tsx", "/index.ts", "/index.tsx", ".js", "/index.js"]) {
    if (fs.existsSync(resolved + ext)) return true;
  }
  return fs.existsSync(resolved);
}

checks.bus_imported = busMod !== "" && resolveImport(busMod);
checks.workspace_imported = wsMod !== "" && resolveImport(wsMod);

// P2P: RPC exports intact
const rpcDecl = findVarDecl("rpc");
let rpcText = "";
if (rpcDecl && rpcDecl.initializer) rpcText = rpcDecl.initializer.getText(sf);
const rpcMethods = ["fetch", "snapshot", "server", "checkUpgrade", "reload", "shutdown"];
checks.rpc_exports = rpcMethods.every(m => rpcText.includes(m));

// P2P: GlobalBus.on event forwarding
checks.global_bus = allCalls.some(c => /^GlobalBus\s*\.\s*on$/.test(c));

// P2P: AbortController + signal cleanup
checks.abort_cleanup = allNews.includes("AbortController") &&
  allAccesses.some(a => /\bsignal\b/.test(a));

// Anti-stub: >= 15 meaningful AST nodes
checks.not_stub = countMeaningful(streamInit) >= 15;

// --- agent_config checks (scoped to startEventStream) ---

// No `any` type annotations in startEventStream (AGENTS.md:13)
{
  let anyCount = 0;
  function visitAny(n) {
    if (n.kind === ts.SyntaxKind.AnyKeyword) anyCount++;
    ts.forEachChild(n, visitAny);
  }
  visitAny(streamInit);
  checks.no_any_type = anyCount === 0;
}

// Prefer const over let in startEventStream (AGENTS.md:70)
{
  let letCount = 0;
  function visitLet(n) {
    if (ts.isVariableDeclarationList(n) && !(n.flags & ts.NodeFlags.Const)) {
      // count let/var declarations
      letCount += n.declarations.length;
    }
    ts.forEachChild(n, visitLet);
  }
  visitLet(streamInit);
  // The gold patch uses exactly 1 `let` (settled), which is acceptable
  // since it requires reassignment. Flag if > 3 lets (excessive mutability).
  checks.const_over_let = letCount <= 3;
}

// Avoid else statements in startEventStream (AGENTS.md:84)
{
  let elseCount = 0;
  function visitElse(n) {
    if (ts.isIfStatement(n) && n.elseStatement) elseCount++;
    ts.forEachChild(n, visitElse);
  }
  visitElse(streamInit);
  checks.no_else = elseCount === 0;
}

// No try/catch in startEventStream (AGENTS.md:12)
{
  let tryCatchCount = 0;
  function visitTry(n) {
    if (ts.isTryStatement(n)) tryCatchCount++;
    ts.forEachChild(n, visitTry);
  }
  visitTry(streamInit);
  checks.no_try_catch = tryCatchCount === 0;
}

console.log(JSON.stringify(checks));
"""


@pytest.fixture(scope="session")
def ast_checks():
    """Run TypeScript AST analysis once, share results across all tests."""
    assert Path(WORKER).is_file(), f"worker.ts not found at {WORKER}"

    r = subprocess.run(
        ["node", "-e", _AST_SCRIPT, WORKER],
        capture_output=True, text=True, timeout=30, cwd=REPO,
        env=_NODE_ENV,
    )
    assert r.returncode == 0, f"AST analysis failed:\n{r.stderr}"

    data = json.loads(r.stdout.strip())
    assert not data.get("syntax_error"), "TypeScript syntax errors in worker.ts"
    return data


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_parses(ast_checks):
    """worker.ts must parse as valid TypeScript without syntax errors."""
    assert ast_checks["syntax_ok"]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bus_subscribe_in_stream(ast_checks):
    """startEventStream must call Bus.subscribe or Bus.subscribeAll (AST-verified)."""
    assert ast_checks["bus_subscribe"], \
        "Bus.subscribe/subscribeAll not found as a call expression in startEventStream"


# [pr_diff] fail_to_pass
def test_workspace_context_wrapping(ast_checks):
    """startEventStream must call WorkspaceContext.provide to set workspace scope."""
    assert ast_checks["workspace_provide"], \
        "WorkspaceContext.provide not called in startEventStream"


# [pr_diff] fail_to_pass
def test_instance_context_wrapping(ast_checks):
    """startEventStream must call Instance.provide to set up instance context."""
    assert ast_checks["instance_provide"], \
        "Instance.provide not called in startEventStream"


# [pr_diff] fail_to_pass
def test_sse_client_removed(ast_checks):
    """createOpencodeClient and sdk.event.subscribe must be removed entirely."""
    assert ast_checks["sse_removed"], \
        "createOpencodeClient still called in file"
    assert ast_checks["sdk_subscribe_removed"], \
        "sdk.event.subscribe still called in startEventStream"


# [pr_diff] fail_to_pass
def test_event_bus_imports_resolve(ast_checks):
    """Bus and WorkspaceContext must be imported from modules that exist on disk."""
    assert ast_checks["bus_imported"], \
        "Bus not imported from a resolvable @/bus module"
    assert ast_checks["workspace_imported"], \
        "WorkspaceContext not imported from a resolvable workspace module"


# [pr_diff] fail_to_pass
def test_instance_disposed_handling(ast_checks):
    """Bus.InstanceDisposed must be referenced in startEventStream for reconnection."""
    assert ast_checks["instance_disposed"], \
        "InstanceDisposed not referenced in startEventStream — reconnection on disposal missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_rpc_exports_intact(ast_checks):
    """All RPC methods (fetch, snapshot, server, checkUpgrade, reload, shutdown) still exported."""
    assert ast_checks["rpc_exports"], \
        "One or more required RPC methods missing from the rpc variable"


# [pr_diff] pass_to_pass
def test_global_bus_forwarding(ast_checks):
    """GlobalBus.on must still be called for cross-context event forwarding."""
    assert ast_checks["global_bus"], \
        "GlobalBus.on call not found — event forwarding broken"


# [pr_diff] pass_to_pass
def test_abort_cleanup(ast_checks):
    """AbortController must be instantiated and signal used for cleanup."""
    assert ast_checks["abort_cleanup"], \
        "AbortController + signal cleanup pattern missing"


# [static] pass_to_pass
def test_not_stub(ast_checks):
    """startEventStream must have >= 15 meaningful AST nodes (rejects trivial stubs)."""
    assert ast_checks["not_stub"], \
        "startEventStream has too few meaningful AST nodes — likely a stub"


# ---------------------------------------------------------------------------
# Repo CI-derived (pass_to_pass) — repository integrity checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — TypeScript syntax validation
def test_repo_typescript_syntax():
    """Repo TypeScript files must parse without syntax errors (pass_to_pass)."""
    script = r"""
const ts = require("typescript");
const fs = require("fs");
const files = ["/repo/packages/opencode/src/cli/cmd/tui/worker.ts"]
    .filter(f => fs.existsSync(f));
if (files.length === 0) {
    console.log("REPO_NOT_MOUNTED");
    process.exit(0);
}
let errors = [];
for (const file of files) {
    try {
        const src = fs.readFileSync(file, "utf8");
        const sf = ts.createSourceFile(file, src, ts.ScriptTarget.Latest, true);
        if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
            errors.push(file + ": " + sf.parseDiagnostics[0].messageText);
        }
    } catch (e) {
        errors.push(file + ": " + e.message);
    }
}
if (errors.length > 0) {
    console.log("SYNTAX_ERRORS: " + errors.join("; "));
    process.exit(1);
}
console.log("OK");
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
        env={**os.environ, "NODE_PATH": "/usr/local/lib/node_modules"},
    )
    if "REPO_NOT_MOUNTED" in r.stdout:
        pytest.skip("Repo not mounted")
    assert r.returncode == 0, f"TypeScript syntax errors:\n{r.stdout}{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 1d363fa
def test_no_any_type(ast_checks):
    """No `any` type annotations in startEventStream (AGENTS.md:13)."""
    # AST-only because: TypeScript module requires full bun/effect runtime
    assert ast_checks["no_any_type"], \
        "Found `any` type annotation in startEventStream — AGENTS.md forbids it"


# [agent_config] pass_to_pass — AGENTS.md:70 @ 1d363fa
def test_const_over_let(ast_checks):
    """Prefer const over let in startEventStream (AGENTS.md:70). Allows <=3 lets for necessary mutation."""
    # AST-only because: TypeScript module requires full bun/effect runtime
    assert ast_checks["const_over_let"], \
        "Too many `let` declarations in startEventStream — prefer const (AGENTS.md:70)"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 1d363fa
def test_no_else(ast_checks):
    """No else statements in startEventStream (AGENTS.md:84). Use early returns instead."""
    # AST-only because: TypeScript module requires full bun/effect runtime
    assert ast_checks["no_else"], \
        "Found `else` statement in startEventStream — prefer early returns (AGENTS.md:84)"


# [agent_config] pass_to_pass — AGENTS.md:12 @ 1d363fa
def test_no_try_catch(ast_checks):
    """No try/catch blocks in startEventStream (AGENTS.md:12). Use .catch() on promises instead."""
    # AST-only because: TypeScript module requires full bun/effect runtime
    assert ast_checks["no_try_catch"], \
        "Found try/catch block in startEventStream — use .catch() instead (AGENTS.md:12)"


# ---------------------------------------------------------------------------
# Additional Repo CI-derived (pass_to_pass) — extended repository integrity
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Bus module files parse correctly
def test_repo_bus_module_syntax():
    """Bus module TypeScript files must parse without syntax errors (pass_to_pass)."""
    script = r"""
const ts = require("typescript");
const fs = require("fs");
const path = require("path");

const busDir = "/repo/packages/opencode/src/bus";
if (!fs.existsSync(busDir)) {
    console.log("REPO_NOT_MOUNTED");
    process.exit(0);
}

const files = [
    path.join(busDir, "index.ts"),
    path.join(busDir, "global.ts"),
    path.join(busDir, "bus-event.ts")
].filter(f => fs.existsSync(f));

let errors = [];
for (const file of files) {
    try {
        const src = fs.readFileSync(file, "utf8");
        const sf = ts.createSourceFile(file, src, ts.ScriptTarget.Latest, true);
        if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
            errors.push(file + ": " + sf.parseDiagnostics[0].messageText);
        }
    } catch (e) {
        errors.push(file + ": " + e.message);
    }
}
if (errors.length > 0) {
    console.log("SYNTAX_ERRORS: " + errors.join("; "));
    process.exit(1);
}
console.log("OK: " + files.length + " files parsed");
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
        env={**os.environ, "NODE_PATH": "/usr/local/lib/node_modules"},
    )
    if "REPO_NOT_MOUNTED" in r.stdout:
        pytest.skip("Repo not mounted")
    assert r.returncode == 0, f"Bus module syntax errors:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass — Control-plane module files parse correctly
def test_repo_control_plane_syntax():
    """Control-plane module TypeScript files must parse without syntax errors (pass_to_pass)."""
    script = r"""
const ts = require("typescript");
const fs = require("fs");
const path = require("path");

const cpDir = "/repo/packages/opencode/src/control-plane";
if (!fs.existsSync(cpDir)) {
    console.log("REPO_NOT_MOUNTED");
    process.exit(0);
}

const files = [
    path.join(cpDir, "workspace-context.ts"),
    path.join(cpDir, "schema.ts")
].filter(f => fs.existsSync(f));

if (files.length === 0) {
    console.log("FILES_NOT_FOUND");
    process.exit(0);
}

let errors = [];
for (const file of files) {
    try {
        const src = fs.readFileSync(file, "utf8");
        const sf = ts.createSourceFile(file, src, ts.ScriptTarget.Latest, true);
        if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
            errors.push(file + ": " + sf.parseDiagnostics[0].messageText);
        }
    } catch (e) {
        errors.push(file + ": " + e.message);
    }
}
if (errors.length > 0) {
    console.log("SYNTAX_ERRORS: " + errors.join("; "));
    process.exit(1);
}
console.log("OK: " + files.length + " files parsed");
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
        env={**os.environ, "NODE_PATH": "/usr/local/lib/node_modules"},
    )
    if "REPO_NOT_MOUNTED" in r.stdout or "FILES_NOT_FOUND" in r.stdout:
        pytest.skip("Repo not mounted or files not found")
    assert r.returncode == 0, f"Control-plane module syntax errors:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass — Import paths resolve to existing files
def test_repo_import_paths_resolve():
    """Import paths in worker.ts must resolve to files that exist on disk (pass_to_pass)."""
    script = r"""
const ts = require("typescript");
const fs = require("fs");
const path = require("path");

const workerPath = "/repo/packages/opencode/src/cli/cmd/tui/worker.ts";
const srcRoot = "/repo/packages/opencode/src";

if (!fs.existsSync(workerPath)) {
    console.log("REPO_NOT_MOUNTED");
    process.exit(0);
}

const src = fs.readFileSync(workerPath, "utf8");
const sf = ts.createSourceFile(workerPath, src, ts.ScriptTarget.Latest, true);

// Collect all @/ imports
const imports = [];
ts.forEachChild(sf, node => {
    if (ts.isImportDeclaration(node)) {
        const spec = node.moduleSpecifier;
        if (ts.isStringLiteral(spec) && spec.text.startsWith("@/")) {
            imports.push(spec.text);
        }
    }
});

let unresolved = [];
for (const imp of imports) {
    // Map @/path to src/path
    const basePath = imp.replace(/^@\//, srcRoot + "/");
    const possiblePaths = [
        basePath + ".ts",
        basePath + ".tsx",
        basePath + "/index.ts",
        basePath + "/index.tsx"
    ];
    const exists = possiblePaths.some(p => fs.existsSync(p));
    if (!exists) {
        unresolved.push(imp);
    }
}

if (unresolved.length > 0) {
    console.log("UNRESOLVED_IMPORTS: " + unresolved.join("; "));
    process.exit(1);
}
console.log("OK: " + imports.length + " imports resolved");
"""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
        env={**os.environ, "NODE_PATH": "/usr/local/lib/node_modules"},
    )
    if "REPO_NOT_MOUNTED" in r.stdout:
        pytest.skip("Repo not mounted")
    assert r.returncode == 0, f"Import path resolution failed:\n{r.stdout}{r.stderr}"
