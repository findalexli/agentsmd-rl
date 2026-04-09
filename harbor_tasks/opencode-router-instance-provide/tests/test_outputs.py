"""
Task: opencode-router-instance-provide
Repo: anomalyco/opencode @ e5f0e813b6e2f9305fc27d432689f95a56beea51
PR:   #19455

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
ROUTER = "packages/opencode/src/server/router.ts"
INSTANCE = "packages/opencode/src/server/instance.ts"
SERVER = "packages/opencode/src/server/server.ts"
OLD_MW = "packages/opencode/src/control-plane/workspace-router-middleware.ts"
WORKTREE = "packages/opencode/src/control-plane/adaptors/worktree.ts"


def _bun_check(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a bun -e script in the repo directory."""
    return subprocess.run(
        ["bun", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_router_exports_middleware():
    """router.ts must exist and export WorkspaceRouterMiddleware as a function."""
    r = _bun_check(f"""
        const mod = await import('./{ROUTER}');
        if (typeof mod.WorkspaceRouterMiddleware !== 'function') {{
            console.error('not a function: ' + typeof mod.WorkspaceRouterMiddleware);
            process.exit(1);
        }}
    """)
    assert r.returncode == 0, f"router.ts not importable or bad export:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_instance_provide_in_router():
    """Router calls Instance.provide with InstanceBootstrap for directory-based routing."""
    # The new router must contain Instance.provide({...init: InstanceBootstrap...})
    # Verify via AST so string-in-comment doesn't fool us.
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let provide = 0;
        let bootstrap = false;
        function visit(n) {{
            if (ts.isCallExpression(n)) {{
                const e = n.expression;
                if (ts.isPropertyAccessExpression(e) &&
                    e.name.text === 'provide' &&
                    ts.isIdentifier(e.expression) &&
                    e.expression.text === 'Instance') {{
                    provide++;
                    const argText = src.substring(n.arguments[0]?.pos || 0, n.arguments[0]?.end || 0);
                    if (argText.includes('InstanceBootstrap')) bootstrap = true;
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (provide < 1) {{ console.error('no Instance.provide call'); process.exit(1); }}
        if (!bootstrap) {{ console.error('no InstanceBootstrap in provide args'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Instance.provide+InstanceBootstrap not in router.ts AST:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_instance_provide_removed_from_instance_ts():
    """Instance.provide middleware must be removed from instance.ts (moved to router)."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{INSTANCE}', 'utf8');
        const sf = ts.createSourceFile('instance.ts', src, ts.ScriptTarget.Latest, true);
        let found = false;
        function visit(n) {{
            if (ts.isCallExpression(n)) {{
                const e = n.expression;
                if (ts.isPropertyAccessExpression(e) &&
                    e.name.text === 'provide' &&
                    ts.isIdentifier(e.expression) &&
                    e.expression.text === 'Instance') found = true;
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (found) {{ console.error('Instance.provide still in instance.ts'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Instance.provide not removed from instance.ts:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_workspace_routing_branches():
    """Router handles no-workspace, worktree, and remote workspace cases."""
    # Must have >=2 Instance.provide calls (no-workspace + worktree),
    # workspace param extraction, and adaptor.fetch for remote.
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let provideCount = 0;
        let hasWorkspace = false;
        let hasAdaptorFetch = false;
        function visit(n) {{
            if (ts.isCallExpression(n)) {{
                const e = n.expression;
                if (ts.isPropertyAccessExpression(e) &&
                    e.name.text === 'provide' &&
                    ts.isIdentifier(e.expression) &&
                    e.expression.text === 'Instance') provideCount++;
                if (ts.isPropertyAccessExpression(e) && e.name.text === 'fetch') {{
                    const t = src.substring(n.pos, n.end);
                    if (t.includes('adaptor') || t.includes('Adaptor')) hasAdaptorFetch = true;
                }}
            }}
            if (ts.isStringLiteral(n) && n.text === 'workspace') hasWorkspace = true;
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (provideCount < 2) {{ console.error('need >=2 Instance.provide, got ' + provideCount); process.exit(1); }}
        if (!hasWorkspace) {{ console.error('no workspace param extraction'); process.exit(1); }}
        if (!hasAdaptorFetch) {{ console.error('no adaptor.fetch for remote'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Missing routing branches in router.ts:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_old_middleware_deleted():
    """workspace-router-middleware.ts must be deleted (consolidated into router.ts)."""
    assert not Path(f"{REPO}/{OLD_MW}").exists(), \
        f"{OLD_MW} still exists — should be deleted"


# [pr_diff] fail_to_pass
def test_server_imports_from_router():
    """server.ts must import WorkspaceRouterMiddleware from ./router, not control-plane."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{SERVER}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);
        let fromRouter = false;
        let fromControlPlane = false;
        function visit(n) {{
            if (ts.isImportDeclaration(n) && ts.isStringLiteral(n.moduleSpecifier)) {{
                const spec = n.moduleSpecifier.text;
                const txt = src.substring(n.pos, n.end);
                if (txt.includes('WorkspaceRouterMiddleware')) {{
                    if (spec.includes('control-plane')) fromControlPlane = true;
                    else fromRouter = true;
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (fromControlPlane) {{ console.error('still imports from control-plane'); process.exit(1); }}
        if (!fromRouter) {{ console.error('not imported from new location'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"server.ts import not updated:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_directory_resolution_in_router():
    """Router resolves directory from query param and x-opencode-directory header."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let hasDirectoryQuery = false;
        let hasDirectoryHeader = false;
        function visit(n) {{
            if (ts.isStringLiteral(n) && n.text === 'x-opencode-directory') hasDirectoryHeader = true;
            if (ts.isCallExpression(n) && ts.isPropertyAccessExpression(n.expression)) {{
                if (n.expression.name.text === 'query' && n.arguments.length > 0) {{
                    const arg = n.arguments[0];
                    if (ts.isStringLiteral(arg) && arg.text === 'directory') hasDirectoryQuery = true;
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!hasDirectoryQuery) {{ console.error('no .query("directory")'); process.exit(1); }}
        if (!hasDirectoryHeader) {{ console.error('no x-opencode-directory header'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Directory resolution missing in router.ts:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_instance_routes_importable():
    """InstanceRoutes is still exported from instance.ts."""
    r = _bun_check(f"""
        const mod = await import('./{INSTANCE}');
        if (typeof mod.InstanceRoutes !== 'function') {{
            console.error('InstanceRoutes not a function');
            process.exit(1);
        }}
    """)
    assert r.returncode == 0, f"InstanceRoutes not importable:\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_worktree_adaptor_importable():
    """WorktreeAdaptor is still exported with a fetch method."""
    r = _bun_check(f"""
        const mod = await import('./{WORKTREE}');
        if (!mod.WorktreeAdaptor || typeof mod.WorktreeAdaptor !== 'object') {{
            console.error('WorktreeAdaptor not exported');
            process.exit(1);
        }}
        if (typeof mod.WorktreeAdaptor.fetch !== 'function') {{
            console.error('fetch not a function');
            process.exit(1);
        }}
    """)
    assert r.returncode == 0, f"WorktreeAdaptor not importable:\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_router_delegates_to_instance_routes():
    """Router imports and delegates to InstanceRoutes via routes().fetch()."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let importsIt = false;
        let callsFetch = false;
        function visit(n) {{
            if (ts.isImportDeclaration(n) && ts.isStringLiteral(n.moduleSpecifier)) {{
                const txt = src.substring(n.pos, n.end);
                if (txt.includes('InstanceRoutes') && n.moduleSpecifier.text.includes('instance'))
                    importsIt = true;
            }}
            if (ts.isCallExpression(n) && ts.isPropertyAccessExpression(n.expression)) {{
                if (n.expression.name.text === 'fetch') {{
                    const inner = n.expression.expression;
                    if (ts.isCallExpression(inner)) {{
                        const t = src.substring(inner.pos, inner.end);
                        if (t.includes('routes') || t.includes('InstanceRoutes')) callsFetch = true;
                    }}
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!importsIt) {{ console.error('no InstanceRoutes import'); process.exit(1); }}
        if (!callsFetch) {{ console.error('no routes().fetch() call'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Router doesn't delegate to InstanceRoutes:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:13 @ e5f0e813b6e2f9305fc27d432689f95a56beea51
def test_no_any_type_in_router():
    """Router must not use the `any` type (AGENTS.md:13)."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let found = false;
        function visit(n) {{
            if (n.kind === ts.SyntaxKind.AnyKeyword) found = true;
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (found) {{ console.error('any keyword found in router.ts'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"`any` type found in router.ts:\n{r.stderr}"


# [agent_config] fail_to_pass — AGENTS.md:70 @ e5f0e813b6e2f9305fc27d432689f95a56beea51
def test_const_over_let_in_router():
    """Router must prefer const over let (AGENTS.md:70)."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let count = 0;
        function visit(n) {{
            if (ts.isVariableDeclarationList(n) && !(n.flags & ts.NodeFlags.Const)) {{
                if (n.flags & ts.NodeFlags.Let) count++;
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (count > 0) {{ console.error(count + ' let declarations found'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"`let` declarations found in router.ts:\n{r.stderr}"


# [agent_config] fail_to_pass — AGENTS.md:84 @ e5f0e813b6e2f9305fc27d432689f95a56beea51
def test_no_else_in_router():
    """Router must not use else statements; prefer early returns (AGENTS.md:84)."""
    r = _bun_check(f"""
        const fs = require('fs');
        const ts = require('typescript');
        const src = fs.readFileSync('{ROUTER}', 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let count = 0;
        function visit(n) {{
            if (n.kind === ts.SyntaxKind.IfStatement && n.elseStatement) count++;
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (count > 0) {{ console.error(count + ' else statement(s) found'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"`else` statements found in router.ts:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass, repo_tests) — ensure repo's own tests pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "turbo", "typecheck"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests for opencode package pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"
