"""
Task: supabase-studio-org-hook-noprojects
Repo: supabase/supabase @ e7bec24021de77053a9b9b05c06ab17789f1269b
PR:   44572

The NoProjectsOnPaidOrgInfo component was not receiving the 'organization' prop,
causing it to always return null. The fix switches to using an internal hook
to fetch organization data instead of receiving it via props.
"""

import subprocess
import json

REPO = "/workspace/supabase"
TARGET_FILE = "apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx"
FILE_PATH = f"{REPO}/{TARGET_FILE}"


def _run_ast_analysis(js_code: str) -> dict:
    """Run a Node.js script that uses the TypeScript compiler API to analyze
    the component file. Returns parsed JSON from stdout."""
    script = js_code.replace("__FILE_PATH__", FILE_PATH)
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST analysis script failed:\n{r.stderr[-500:]}"
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        raise AssertionError(f"Invalid JSON from analysis:\n{r.stdout[:500]}")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_valid():
    """Modified TypeScript/TSX file must parse without errors via TS compiler API."""
    r = subprocess.run(
        ["node", "-e", """
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('__FILE_PATH__', 'utf8');
const sf = ts.createSourceFile('test.tsx', content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const diags = sf.parseDiagnostics || [];
if (diags.length > 0) {
    console.error('Parse errors:', JSON.stringify(diags.map(d => d.messageText)));
    process.exit(1);
}
if (sf.statements.length === 0) {
    console.error('No statements found');
    process.exit(1);
}
console.log(JSON.stringify({ statements: sf.statements.length, valid: true }));
""".replace("__FILE_PATH__", FILE_PATH)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript parse failed:\n{r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result["statements"] > 0, "No statements found — possible parse error"
    assert result["valid"] is True


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_uses_org_hook_not_props():
    """Component must obtain organization data inside its body via a hook call,
    not receive it as a prop parameter."""
    analysis = _run_ast_analysis("""
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('__FILE_PATH__', 'utf8');
const sf = ts.createSourceFile('test.tsx', content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let result = null;

function visit(node) {
    if (ts.isVariableStatement(node)) {
        for (const decl of node.declarationList.declarations) {
            const name = decl.name.getText(sf);
            if (name === 'NoProjectsOnPaidOrgInfo' && decl.initializer && ts.isArrowFunction(decl.initializer)) {
                const arrow = decl.initializer;
                const params = Array.from(arrow.parameters).map(p => p.getText(sf));
                const hasOrgParam = params.some(p => p.includes('organization'));

                // Check if 'organization' is declared inside the function body
                // via a function/hook call (not a literal assignment)
                let orgFromCallInBody = false;

                function visitBody(n) {
                    if (ts.isVariableDeclaration(n) && n.initializer) {
                        const nameNode = n.name;
                        let declaresOrg = false;

                        // Check simple identifier: const organization = ...
                        if (ts.isIdentifier(nameNode) && nameNode.getText(sf) === 'organization') {
                            declaresOrg = true;
                        }
                        // Check object binding: const { data: organization } = ...
                        if (ts.isObjectBindingPattern(nameNode)) {
                            for (const el of nameNode.elements) {
                                const bindingName = el.name.getText(sf);
                                if (bindingName === 'organization') {
                                    declaresOrg = true;
                                }
                            }
                        }

                        if (declaresOrg) {
                            // Verify the initializer involves a function call
                            let hasCall = false;
                            function checkInit(initNode) {
                                if (ts.isCallExpression(initNode)) hasCall = true;
                                ts.forEachChild(initNode, checkInit);
                            }
                            checkInit(n.initializer);
                            if (hasCall) orgFromCallInBody = true;
                        }
                    }
                    ts.forEachChild(n, visitBody);
                }
                if (arrow.body) visitBody(arrow.body);

                result = {
                    paramCount: arrow.parameters.length,
                    hasOrgParam: hasOrgParam,
                    orgFromCallInBody: orgFromCallInBody
                };
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!result) { console.error('Component not found'); process.exit(1); }
console.log(JSON.stringify(result));
""")
    # Organization must NOT come from props
    assert not analysis["hasOrgParam"], \
        "Component should not receive organization as a prop parameter"

    # Organization must be obtained inside the function body via a call (hook)
    assert analysis["orgFromCallInBody"], \
        "Component must obtain organization data inside its body from a hook/function call"


# [pr_diff] fail_to_pass
def test_component_has_no_params():
    """Component function should take zero parameters (fetches data internally)."""
    analysis = _run_ast_analysis("""
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('__FILE_PATH__', 'utf8');
const sf = ts.createSourceFile('test.tsx', content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let result = null;

function visit(node) {
    if (ts.isVariableStatement(node)) {
        for (const decl of node.declarationList.declarations) {
            const name = decl.name.getText(sf);
            if (name === 'NoProjectsOnPaidOrgInfo' && decl.initializer && ts.isArrowFunction(decl.initializer)) {
                result = {
                    paramCount: decl.initializer.parameters.length,
                    paramTexts: Array.from(decl.initializer.parameters).map(p => p.getText(sf))
                };
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!result) { console.error('Component not found'); process.exit(1); }
console.log(JSON.stringify(result));
""")
    assert analysis["paramCount"] == 0, \
        f"Component should take 0 parameters but has {analysis['paramCount']}: {analysis['paramTexts']}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Component has real implementation logic — not a stub or empty return."""
    analysis = _run_ast_analysis("""
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('__FILE_PATH__', 'utf8');
const sf = ts.createSourceFile('test.tsx', content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

let result = null;

function visit(node) {
    if (ts.isVariableStatement(node)) {
        for (const decl of node.declarationList.declarations) {
            const name = decl.name.getText(sf);
            if (name === 'NoProjectsOnPaidOrgInfo' && decl.initializer && ts.isArrowFunction(decl.initializer)) {
                const bodyText = decl.initializer.body ? decl.initializer.body.getText(sf) : '';

                let stmtCount = 0;
                let hasJSX = false;
                let hookCalls = [];

                function visitBody(n) {
                    if (ts.isVariableStatement(n) || ts.isExpressionStatement(n) ||
                        ts.isReturnStatement(n) || ts.isIfStatement(n)) {
                        stmtCount++;
                    }
                    if (ts.isJsxElement(n) || ts.isJsxSelfClosingElement(n) || ts.isJsxFragment(n)) {
                        hasJSX = true;
                    }
                    if (ts.isCallExpression(n)) {
                        const callName = n.expression.getText(sf);
                        if (callName.startsWith('use')) {
                            hookCalls.push(callName);
                        }
                    }
                    ts.forEachChild(n, visitBody);
                }
                if (decl.initializer.body) visitBody(decl.initializer.body);

                result = {
                    stmtCount: stmtCount,
                    hasJSX: hasJSX,
                    hookCallCount: hookCalls.length,
                    bodyLength: bodyText.length
                };
            }
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!result) { console.error('Component not found'); process.exit(1); }
console.log(JSON.stringify(result));
""")
    assert analysis["stmtCount"] >= 3, \
        f"Component body should have real logic, found only {analysis['stmtCount']} statements"
    assert analysis["hasJSX"], \
        "Component should return JSX content (not just null)"
    assert analysis["hookCallCount"] >= 1, \
        "Component should use React hooks for data fetching"
    assert analysis["bodyLength"] > 100, \
        f"Component body too short ({analysis['bodyLength']} chars) — might be a stub"


# [static] pass_to_pass
def test_imports_correct():
    """Component imports required dependencies correctly (verified via AST)."""
    analysis = _run_ast_analysis("""
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('__FILE_PATH__', 'utf8');
const sf = ts.createSourceFile('test.tsx', content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);

const imports = [];

function visit(node) {
    if (ts.isImportDeclaration(node)) {
        const modSpec = node.moduleSpecifier.getText(sf).replace(/['"]/g, '');
        const names = [];
        const clause = node.importClause;
        if (clause) {
            if (clause.name) names.push(clause.name.getText(sf));
            if (clause.namedBindings) {
                if (ts.isNamedImports(clause.namedBindings)) {
                    for (const spec of clause.namedBindings.elements) {
                        names.push(spec.name.getText(sf));
                    }
                }
            }
        }
        imports.push({ module: modSpec, names: names });
    }
    ts.forEachChild(node, visit);
}
visit(sf);

console.log(JSON.stringify(imports));
""")
    all_names = []
    for imp in analysis:
        all_names.extend(imp["names"])

    assert "Link" in all_names, "Should import Link"
    assert "Admonition" in all_names, "Should import Admonition"
    assert "useOrgProjectsInfiniteQuery" in all_names, \
        "Should import useOrgProjectsInfiniteQuery"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression tests (subprocess)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript_parse():
    """TypeScript syntax check on the modified file passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "node",
            "-e",
            "const ts = require('typescript'); const fs = require('fs'); "
            "const content = fs.readFileSync('" + FILE_PATH + "', 'utf8'); "
            "const result = ts.createSourceFile('test.tsx', content, ts.ScriptTarget.Latest, true); "
            "console.log('TypeScript parsed successfully, statements:', result.statements.length); "
            "if (result.statements.length === 0) throw new Error('No statements found');",
        ],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript parse check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_billing_tests():
    """Repo's Billing component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/components/Billing/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Billing tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/unit/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_config_tests():
    """Repo's config tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/config/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Config tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's code formatting passes for modified file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", FILE_PATH],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_component_tests():
    """Repo's component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/components/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Component tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_features_tests():
    """Repo's feature tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/features/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Feature tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pages_tests():
    """Repo's pages tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "tests/pages/"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/apps/studio",
    )
    assert r.returncode == 0, f"Pages tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
