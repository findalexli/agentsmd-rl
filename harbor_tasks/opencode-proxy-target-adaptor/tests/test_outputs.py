"""
Task: opencode-proxy-target-adaptor
Repo: anomalyco/opencode @ 3c31d046669ca8df09798f690ef5c9cf17021ddd
PR:   #21239

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
TYPES = "packages/opencode/src/control-plane/types.ts"
WORKTREE = "packages/opencode/src/control-plane/adaptors/worktree.ts"
WORKSPACE = "packages/opencode/src/control-plane/workspace.ts"
PROXY = "packages/opencode/src/server/proxy.ts"
ROUTER = "packages/opencode/src/server/router.ts"


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

# [static] pass_to_pass — repo's typecheck (from package.json)
def test_typecheck():
    """All modified packages must pass type checking."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass — repo's typecheck via turbo (from GitHub CI)
def test_repo_typecheck():
    """Repo's bun typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Repo typecheck failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_target_type_defined():
    """Target discriminated union with local and remote variants must exist in types.ts."""
    r = _bun_check(f"""
        const ts = require('typescript');
        const fs = require('fs');
        const src = fs.readFileSync('{TYPES}', 'utf8');
        const sf = ts.createSourceFile('types.ts', src, ts.ScriptTarget.Latest, true);
        let hasLocal = false;
        let hasRemote = false;
        function visit(n) {{
            if (ts.isTypeLiteralNode(n)) {{
                const text = src.substring(n.pos, n.end);
                if (text.includes('"local"') || text.includes("'local'")) hasLocal = true;
                if (text.includes('"remote"') || text.includes("'remote'")) hasRemote = true;
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!hasLocal) {{ console.error('Target missing local variant'); process.exit(1); }}
        if (!hasRemote) {{ console.error('Target missing remote variant'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Target type not properly defined:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_adaptor_has_target_not_fetch():
    """Adaptor interface must have target() method and not fetch()."""
    r = _bun_check(f"""
        const ts = require('typescript');
        const fs = require('fs');
        const src = fs.readFileSync('{TYPES}', 'utf8');
        const sf = ts.createSourceFile('types.ts', src, ts.ScriptTarget.Latest, true);
        let hasTarget = false;
        let hasFetch = false;
        function visit(n) {{
            if (ts.isTypeAliasDeclaration(n) && n.name.text === 'Adaptor') {{
                const body = src.substring(n.pos, n.end);
                if (/\\btarget\\s*\\(/.test(body)) hasTarget = true;
                if (/\\bfetch\\s*\\(/.test(body)) hasFetch = true;
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!hasTarget) {{ console.error('Adaptor missing target() method'); process.exit(1); }}
        if (hasFetch) {{ console.error('Adaptor still has fetch() method'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"Adaptor interface wrong:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_worktree_target_returns_local():
    """WorktreeAdaptor must implement target() returning an object with type 'local'."""
    r = _bun_check(f"""
        const ts = require('typescript');
        const fs = require('fs');
        const src = fs.readFileSync('{WORKTREE}', 'utf8');
        const sf = ts.createSourceFile('worktree.ts', src, ts.ScriptTarget.Latest, true);
        let hasTarget = false;
        let returnsLocal = false;
        function visit(n) {{
            if (ts.isMethodDeclaration(n) || ts.isPropertyAssignment(n)) {{
                const name = n.name ? src.substring(n.name.pos, n.name.end).trim() : '';
                if (name === 'target') {{
                    hasTarget = true;
                    const body = src.substring(n.pos, n.end);
                    if (body.includes('"local"') || body.includes("'local'")) returnsLocal = true;
                }}
            }}
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!hasTarget) {{ console.error('WorktreeAdaptor missing target()'); process.exit(1); }}
        if (!returnsLocal) {{ console.error('target() does not return local type'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"WorktreeAdaptor.target() wrong:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_proxy_module_exports():
    """ServerProxy module must export http() and websocket() functions."""
    proxy_path = Path(f"{REPO}/{PROXY}")
    assert proxy_path.exists(), "proxy.ts must be created"
    r = _bun_check(f"""
        const mod = await import('./{PROXY}');
        if (!mod.ServerProxy) {{ console.error('ServerProxy not exported'); process.exit(1); }}
        if (typeof mod.ServerProxy.http !== 'function') {{
            console.error('ServerProxy.http not a function'); process.exit(1);
        }}
        if (typeof mod.ServerProxy.websocket !== 'function') {{
            console.error('ServerProxy.websocket not a function'); process.exit(1);
        }}
    """)
    assert r.returncode == 0, f"ServerProxy exports wrong:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_proxy_strips_hop_headers():
    """HTTP proxy must strip hop-by-hop headers (connection, transfer-encoding, etc.)."""
    proxy_path = Path(f"{REPO}/{PROXY}")
    assert proxy_path.exists(), "proxy.ts must be created"
    src = proxy_path.read_text().lower()
    # RFC 2616 hop-by-hop headers that MUST be stripped
    required_hops = ["connection", "transfer-encoding"]
    for h in required_hops:
        assert h in src, f"Proxy must strip hop-by-hop header: {h}"
    # Must strip at least 4 different hop-by-hop headers total
    all_hops = [
        "connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailer",
        "transfer-encoding", "upgrade", "host",
    ]
    found = sum(1 for h in all_hops if h in src)
    assert found >= 4, f"Proxy only handles {found} hop-by-hop headers, need at least 4"


# [pr_diff] fail_to_pass
def test_workspace_uses_target():
    """workspaceEventLoop must use adaptor.target() and return early for local targets."""
    r = _bun_check(f"""
        const ts = require('typescript');
        const fs = require('fs');
        const src = fs.readFileSync('{WORKSPACE}', 'utf8');
        const sf = ts.createSourceFile('workspace.ts', src, ts.ScriptTarget.Latest, true);
        let usesTarget = false;
        let checksLocal = false;
        function visit(n) {{
            if (ts.isCallExpression(n)) {{
                const text = src.substring(n.expression.pos, n.expression.end).trim();
                if (text.includes('.target')) usesTarget = true;
            }}
            if (ts.isStringLiteral(n) && n.text === 'local') checksLocal = true;
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (!usesTarget) {{ console.error('workspace does not call adaptor.target()'); process.exit(1); }}
        if (!checksLocal) {{ console.error('workspace does not check for local target'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"workspace.ts not using target():\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_router_branches_on_target():
    """Router must branch on target.type instead of workspace.type for routing."""
    src = Path(f"{REPO}/{ROUTER}").read_text()
    # Must use target.type for routing decisions (not present on base)
    assert "target.type" in src, "Router must use target.type for routing decisions"
    # Must NOT compare workspace.type to "worktree" (old routing pattern)
    assert 'workspace.type === "worktree"' not in src, \
        "Router must not use workspace.type === 'worktree' (use target.type instead)"


# [pr_diff] fail_to_pass
def test_router_websocket_proxy():
    """Router must delegate websocket upgrades through the proxy module."""
    src = Path(f"{REPO}/{ROUTER}").read_text()
    assert "websocket" in src.lower(), "Router must handle websocket upgrades"
    assert "ServerProxy" in src or "Proxy" in src, "Router must use proxy module for websocket"
    # Must check for upgrade header
    assert "upgrade" in src.lower(), "Router must check for websocket upgrade header"


# [pr_diff] fail_to_pass
def test_router_workspace_header():
    """Router must accept workspace ID from x-opencode-workspace header."""
    src = Path(f"{REPO}/{ROUTER}").read_text()
    # Must READ the header (via .header() call), not just delete it
    # Base only has headers.delete("x-opencode-workspace") which is not reading it
    assert '.header("x-opencode-workspace")' in src or \
           ".header('x-opencode-workspace')" in src, \
        "Router must read x-opencode-workspace header for workspace resolution"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:12 @ 3c31d046669ca8df09798f690ef5c9cf17021ddd
def test_no_try_catch_in_proxy():
    """New proxy module must not use try/catch (AGENTS.md: 'Avoid try/catch where possible')."""
    proxy_path = Path(f"{REPO}/{PROXY}")
    assert proxy_path.exists(), "proxy.ts must be created"
    r = _bun_check(f"""
        const ts = require('typescript');
        const fs = require('fs');
        const src = fs.readFileSync('{PROXY}', 'utf8');
        const sf = ts.createSourceFile('proxy.ts', src, ts.ScriptTarget.Latest, true);
        let count = 0;
        function visit(n) {{
            if (n.kind === ts.SyntaxKind.TryStatement) count++;
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (count > 0) {{ console.error(count + ' try/catch block(s) found in proxy.ts'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"try/catch found in proxy.ts:\n{r.stderr}"


# [agent_config] fail_to_pass — AGENTS.md:84 @ 3c31d046669ca8df09798f690ef5c9cf17021ddd
def test_no_else_in_proxy():
    """New proxy module must not use else statements (AGENTS.md: 'Avoid else statements')."""
    proxy_path = Path(f"{REPO}/{PROXY}")
    assert proxy_path.exists(), "proxy.ts must be created"
    r = _bun_check(f"""
        const ts = require('typescript');
        const fs = require('fs');
        const src = fs.readFileSync('{PROXY}', 'utf8');
        const sf = ts.createSourceFile('proxy.ts', src, ts.ScriptTarget.Latest, true);
        let count = 0;
        function visit(n) {{
            if (n.kind === ts.SyntaxKind.IfStatement && n.elseStatement) count++;
            ts.forEachChild(n, visit);
        }}
        visit(sf);
        if (count > 0) {{ console.error(count + ' else statement(s) found in proxy.ts'); process.exit(1); }}
    """)
    assert r.returncode == 0, f"else statements found in proxy.ts:\n{r.stderr}"
