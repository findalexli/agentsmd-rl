"""
Task: openclaw-openresponses-http-owner-escalation
Repo: openclaw/openclaw @ 1a75906a6fe5191ea573758017834f200056500b
PR:   57778

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
SRC = f"{REPO}/src/gateway/openresponses-http.ts"


def _node(script: str) -> str:
    """Run a Node.js script and return stripped stdout."""
    r = subprocess.run(
        ["node", "-e", script], capture_output=True, text=True, timeout=30
    )
    return r.stdout.strip()


def _read_src() -> str:
    return Path(SRC).read_text()


# ---------------------------------------------------------------------------
# Helpers: reusable AST fragments
# ---------------------------------------------------------------------------

_FIND_HELPER = """
let helperFunc = null;
function findHelper(node) {
    if (ts.isFunctionDeclaration(node) && node.name?.text === 'runResponsesAgentCommand')
        helperFunc = node;
    if (ts.isVariableStatement(node)) {
        const d = node.declarationList.declarations[0];
        if (d?.name?.text === 'runResponsesAgentCommand') helperFunc = d.initializer;
    }
    ts.forEachChild(node, findHelper);
}
findHelper(sf);
"""

_PREAMBLE = f"""
const ts = require('typescript');
const source = require('fs').readFileSync('{SRC}', 'utf8');
const sf = ts.createSourceFile('src.ts', source, ts.ScriptTarget.Latest, true);
"""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified file must parse without TypeScript errors."""
    result = _node(f"""
const ts = require('typescript');
const src = require('fs').readFileSync('{SRC}', 'utf8');
const r = ts.transpileModule(src, {{compilerOptions: {{
    target: ts.ScriptTarget.ESNext,
    module: ts.ModuleKind.ESNext,
    jsx: ts.JsxEmit.Preserve
}}}});
console.log(r.outputText ? 'OK' : 'FAIL');
""")
    assert result == "OK", "TypeScript file has syntax errors"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_hardcoded_sender_is_owner_true():
    """Inside runResponsesAgentCommand, agentCommandFromIngress must not
    receive senderIsOwner as a literal `true`."""
    result = _node(_PREAMBLE + _FIND_HELPER + """
if (!helperFunc) { console.log('NO_FUNC'); process.exit(0); }

let hardcoded = false;
function walk(node) {
    if (ts.isCallExpression(node)) {
        const name = ts.isIdentifier(node.expression) ? node.expression.text : '';
        if (name === 'agentCommandFromIngress') {
            function check(n) {
                if (ts.isPropertyAssignment(n) && n.name?.text === 'senderIsOwner' &&
                    n.initializer.kind === ts.SyntaxKind.TrueKeyword) hardcoded = true;
                ts.forEachChild(n, check);
            }
            node.arguments.forEach(a => check(a));
        }
    }
    ts.forEachChild(node, walk);
}
walk(helperFunc);
console.log(hardcoded ? 'HARDCODED' : 'OK');
""")
    assert result == "OK", (
        f"agentCommandFromIngress still has hardcoded senderIsOwner: true ({result})"
    )


# [pr_diff] fail_to_pass
def test_sender_is_owner_flows_from_params():
    """runResponsesAgentCommand must receive senderIsOwner from callers
    (in params/type) and pass it through to agentCommandFromIngress."""
    result = _node(_PREAMBLE + _FIND_HELPER + """
if (!helperFunc) { console.log('NO_FUNC'); process.exit(0); }

let inParams = false, inBody = false;

function walkParams(node) {
    if (ts.isIdentifier(node) && node.text === 'senderIsOwner') inParams = true;
    ts.forEachChild(node, walkParams);
}
if (helperFunc.parameters) helperFunc.parameters.forEach(p => walkParams(p));

function walkBody(node) {
    if (ts.isCallExpression(node)) {
        const name = ts.isIdentifier(node.expression) ? node.expression.text : '';
        if (name === 'agentCommandFromIngress') {
            function check(n) {
                if (ts.isPropertyAssignment(n) && n.name?.text === 'senderIsOwner' &&
                    n.initializer.kind !== ts.SyntaxKind.TrueKeyword) inBody = true;
                if (ts.isShorthandPropertyAssignment(n) && n.name.text === 'senderIsOwner')
                    inBody = true;
                if (ts.isSpreadAssignment(n) || ts.isSpreadElement(n)) inBody = true;
                ts.forEachChild(n, check);
            }
            node.arguments.forEach(a => check(a));
        }
    }
    ts.forEachChild(node, walkBody);
}
if (helperFunc.body) walkBody(helperFunc.body);

if (inParams && inBody) console.log('OK');
else if (!inParams) console.log('NO_PARAM');
else console.log('NO_BODY');
""")
    assert result == "OK", (
        f"senderIsOwner does not flow from callers to helper ({result})"
    )


# [pr_diff] fail_to_pass
def test_call_sites_pass_non_owner():
    """Both streaming and non-streaming call sites in handleOpenResponsesHttpRequest
    must pass senderIsOwner as something other than literal true."""
    result = _node(_PREAMBLE + """
let handlerFunc = null;
function findHandler(node) {
    if (ts.isFunctionDeclaration(node) && node.name?.text === 'handleOpenResponsesHttpRequest')
        handlerFunc = node;
    ts.forEachChild(node, findHandler);
}
findHandler(sf);

if (!handlerFunc) { console.log('0/0'); process.exit(0); }

let good = 0, total = 0;
function walk(node) {
    if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) &&
        node.expression.text === 'runResponsesAgentCommand') {
        total++;
        function check(n) {
            if (ts.isPropertyAssignment(n) && n.name?.text === 'senderIsOwner' &&
                n.initializer.kind !== ts.SyntaxKind.TrueKeyword) good++;
            if (ts.isShorthandPropertyAssignment(n) && n.name.text === 'senderIsOwner') good++;
            if (ts.isSpreadAssignment(n)) good++;
            ts.forEachChild(n, check);
        }
        node.arguments.forEach(a => check(a));
    }
    ts.forEachChild(node, walk);
}
walk(handlerFunc);
console.log(good + '/' + total);
""")
    parts = result.split("/")
    good = int(parts[0]) if parts[0].isdigit() else 0
    assert good >= 2, f"Not all call sites pass non-owner senderIsOwner ({result})"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_handler_exported():
    """handleOpenResponsesHttpRequest must remain exported."""
    result = _node(_PREAMBLE + """
let found = false;
function walk(node) {
    if (ts.isFunctionDeclaration(node) && node.name?.text === 'handleOpenResponsesHttpRequest' &&
        node.modifiers?.some(m => m.kind === ts.SyntaxKind.ExportKeyword)) found = true;
    ts.forEachChild(node, walk);
}
walk(sf);
console.log(found ? 'OK' : 'FAIL');
""")
    assert result == "OK", "handleOpenResponsesHttpRequest is no longer exported"


# [repo_tests] pass_to_pass
def test_ingress_call_preserved():
    """agentCommandFromIngress must still be called in the file."""
    src = _read_src()
    assert "agentCommandFromIngress(" in src, "agentCommandFromIngress call removed"


# [repo_tests] pass_to_pass
def test_model_override_preserved():
    """allowModelOverride: true must still be present."""
    src = _read_src()
    assert re.search(r"allowModelOverride:\s*true", src), "allowModelOverride: true removed"


# [static] pass_to_pass
def test_not_stub():
    """File must not be gutted and runResponsesAgentCommand must have a real body."""
    src = _read_src()
    lines = src.count("\n") + 1
    assert lines >= 400, f"File appears gutted ({lines} lines, expected >= 400)"

    result = _node(_PREAMBLE + _FIND_HELPER + """
let stmts = 0;
if (helperFunc?.body) stmts = helperFunc.body.statements.length;
console.log(stmts);
""")
    stmts = int(result) if result.isdigit() else 0
    assert stmts >= 3, f"runResponsesAgentCommand body is a stub ({stmts} statements)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:144 @ 1a75906
def test_strict_boolean_typing():
    """senderIsOwner must be typed as boolean (strict typing per CLAUDE.md)."""
    result = _node(_PREAMBLE + """
let typed = false;
function walk(node) {
    if (ts.isPropertySignature(node) && node.name?.text === 'senderIsOwner' && node.type) {
        function hasBoolean(t) {
            if (t.kind === ts.SyntaxKind.BooleanKeyword) return true;
            if (ts.isUnionTypeNode(t)) return t.types.some(hasBoolean);
            return false;
        }
        if (hasBoolean(node.type)) typed = true;
    }
    if (ts.isParameter(node) && node.name?.text === 'senderIsOwner' &&
        node.type?.kind === ts.SyntaxKind.BooleanKeyword) typed = true;
    ts.forEachChild(node, walk);
}
walk(sf);
console.log(typed ? 'OK' : 'FAIL');
""")
    assert result == "OK", "senderIsOwner is not explicitly typed as boolean"


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 1a75906
def test_no_ts_nocheck():
    """File must not contain @ts-nocheck or inline lint suppressions."""
    src = _read_src()
    assert "@ts-nocheck" not in src, "@ts-nocheck found in file"
    assert "eslint-disable" not in src, "eslint-disable suppression found"
    assert "oxlint-ignore" not in src, "oxlint-ignore suppression found"


# [agent_config] pass_to_pass — CLAUDE.md:147 @ 1a75906
def test_no_explicit_any():
    """senderIsOwner and its surrounding params type must not use `any`."""
    # AST-only because: TypeScript type analysis requires ts compiler API
    result = _node(_PREAMBLE + _FIND_HELPER + """
let anyFound = false;
function walk(node) {
    if (node.kind === ts.SyntaxKind.AnyKeyword) {
        // Check if this `any` is in the params type or senderIsOwner-related
        let parent = node.parent;
        while (parent) {
            if (ts.isPropertySignature(parent) && parent.name?.text === 'senderIsOwner') {
                anyFound = true; break;
            }
            if (ts.isParameter(parent)) {
                // Check if param is in runResponsesAgentCommand
                let pp = parent.parent;
                while (pp) {
                    if ((ts.isFunctionDeclaration(pp) || ts.isArrowFunction(pp) || ts.isFunctionExpression(pp)) &&
                        pp === helperFunc) { anyFound = true; break; }
                    pp = pp.parent;
                }
                break;
            }
            parent = parent.parent;
        }
    }
    ts.forEachChild(node, walk);
}
if (helperFunc) walk(helperFunc);
console.log(anyFound ? 'FOUND_ANY' : 'OK');
""")
    assert result == "OK", f"Explicit `any` found in helper params ({result})"


# [agent_config] fail_to_pass — CLAUDE.md:152 @ 1a75906
def test_no_sentinel_default():
    """senderIsOwner must not use a silent sentinel default like ?? true or ?? false."""
    src = _read_src()
    # Check for nullish coalescing on senderIsOwner that could silently change meaning
    assert not re.search(
        r"senderIsOwner\s*(\?\?|&&|\|\|)\s*(true|false)", src
    ), "senderIsOwner uses a silent sentinel default (e.g., ?? true)"
