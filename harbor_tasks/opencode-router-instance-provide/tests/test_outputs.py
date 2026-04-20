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


def _glob_router_path() -> str:
    """Discover the router file path using glob (allows agent to place it in subdirectories)."""
    # Agent might put router.ts in server/ or in a subdirectory like server/routes/
    matches = list(Path(REPO).glob("packages/opencode/src/server/**/router.ts"))
    if matches:
        return str(matches[0].relative_to(REPO))
    return ROUTER  # fallback to default


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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — router.ts created by PR
def test_router_exports_middleware():
    """router.ts must exist and export WorkspaceRouterMiddleware as a function."""
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const mod = await import('./{router_path}');
        if (typeof mod.WorkspaceRouterMiddleware !== 'function') {{
            console.error('not a function: ' + typeof mod.WorkspaceRouterMiddleware);
            process.exit(1);
        }}
    """)
    assert r.returncode == 0, f"router.ts not importable or bad export:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_instance_provide_in_router():
    """Router calls Instance.provide with InstanceBootstrap for directory-based routing."""
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
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
    """Router handles workspace routing: no-workspace case, worktree case, and remote workspace case."""
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let provideCount = 0;
        let hasAdaptorFetch = false;
        let hasRoutesFetch = false;
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
                    if (t.includes('routes')) hasRoutesFetch = true;
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (provideCount < 1) {{ console.error('need >=1 Instance.provide, got ' + provideCount); process.exit(1); }}
        if (!hasAdaptorFetch) {{ console.error('no adaptor.fetch for remote workspace'); process.exit(1); }}
        if (!hasRoutesFetch) {{ console.error('no routes().fetch() delegation'); process.exit(1); }}
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
    """Router resolves directory from query param (any form) and x-opencode-directory header."""
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
        const sf = ts.createSourceFile('router.ts', src, ts.ScriptTarget.Latest, true);
        let hasDirectoryQuery = false;
        let hasDirectoryHeader = false;
        function visit(n) {{
            if (ts.isStringLiteral(n) && n.text === 'x-opencode-directory') hasDirectoryHeader = true;
            if (ts.isCallExpression(n) && ts.isPropertyAccessExpression(n.expression)) {{
                const meth = n.expression.name.text;
                const args = n.arguments;
                // Accept .query("directory") or .get("directory") or searchParams.get("directory")
                if ((meth === 'query' || meth === 'get') && args.length > 0) {{
                    const arg = args[0];
                    if (ts.isStringLiteral(arg) && arg.text === 'directory') hasDirectoryQuery = true;
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!hasDirectoryQuery) {{ console.error('no directory extraction from query'); process.exit(1); }}
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
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
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
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
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
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
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
    router_path = _glob_router_path()
    r = _bun_check(f"""
        const fs = require('fs');
        const router_path = '{router_path}';
        if (!fs.existsSync(router_path)) {{
            console.error('router not found at: ' + router_path);
            process.exit(1);
        }}
        const ts = require('typescript');
        const src = fs.readFileSync(router_path, 'utf8');
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
def test_repo_build_opencode():
    """Opencode package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "run", "build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_worktree_tests():
    """Worktree tests pass — covers worktree routing logic (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/project/worktree.test.ts", "test/project/worktree-remove.test.ts", "--timeout", "30000"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Worktree tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_server_tests():
    """Server tests pass — covers server routing and session handling (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/server/", "--timeout", "30000"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Server tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_control_plane_tests():
    """Control-plane tests pass — covers workspace adaptors and SSE (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/control-plane/", "--timeout", "30000"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Control-plane tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_project_tests():
    """Project tests pass — covers Instance.provide and bootstrap (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/project/project.test.ts", "--timeout", "60000"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Project tests failed:\n{r.stderr[-500:]}"