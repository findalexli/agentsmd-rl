"""
Task: openclaw-http-tool-invoke-auth
Repo: openclaw/openclaw @ ae703ab0e7528ae215b6dd8e20dfa9b64f05a11e
PR:   57773

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"

MODIFIED_FILES = [
    "src/gateway/tools-invoke-http.ts",
    "src/security/dangerous-tools.ts",
]


def _run_node(script: str, timeout: int = 30) -> str:
    """Run a Node.js script in the repo context and return stdout."""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if r.returncode != 0:
        raise RuntimeError(f"node failed (exit {r.returncode}):\n{r.stderr[:2000]}")
    return r.stdout.strip()


def _get_deny_list() -> list[str]:
    """Transpile dangerous-tools.ts and return the exported deny list array."""
    return json.loads(_run_node("""
        const esbuild = require('esbuild');
        const result = esbuild.buildSync({
            entryPoints: ['src/security/dangerous-tools.ts'],
            bundle: false, write: false, format: 'cjs',
            loader: { '.ts': 'ts' },
        });
        const code = new TextDecoder().decode(result.outputFiles[0].contents);
        const mod = { exports: {} };
        new Function('exports', 'require', 'module', code)(mod.exports, require, mod);
        console.log(JSON.stringify(Array.from(mod.exports.DEFAULT_GATEWAY_HTTP_TOOL_DENY || [])));
    """))


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must transpile without errors."""
    for f in MODIFIED_FILES:
        _run_node(
            "const esbuild = require('esbuild');"
            f"esbuild.transformSync(require('fs').readFileSync('{f}', 'utf8'), {{ loader: 'ts' }});"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — deny list behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_deny_list_blocks_execution_tools():
    """Direct execution tools (exec, spawn, shell) must be in HTTP deny list."""
    deny = _get_deny_list()
    for tool in ["exec", "spawn", "shell"]:
        assert tool in deny, f"'{tool}' missing from DEFAULT_GATEWAY_HTTP_TOOL_DENY"


# [pr_diff] fail_to_pass
def test_deny_list_blocks_fs_mutation_tools():
    """File mutation tools must be in HTTP deny list."""
    deny = _get_deny_list()
    for tool in ["fs_write", "fs_delete", "fs_move", "apply_patch"]:
        assert tool in deny, f"'{tool}' missing from DEFAULT_GATEWAY_HTTP_TOOL_DENY"


# [pr_diff] fail_to_pass
def test_deny_list_blocks_node_relay():
    """Node command relay tool must be in HTTP deny list."""
    deny = _get_deny_list()
    assert "nodes" in deny, "'nodes' missing from DEFAULT_GATEWAY_HTTP_TOOL_DENY"


# [pr_diff] fail_to_pass
def test_deny_list_sufficient_entries():
    """Deny list must have at least 10 entries after adding high-risk tools."""
    deny = _get_deny_list()
    assert len(deny) >= 10, f"Deny list too small ({len(deny)} entries, need >= 10)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — handler authorization wiring (BEHAVIORAL)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scope_authorization_imports():
    """Handler must import scope authorization functions from correct modules."""
    handler_code = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()

    # Check imports are present (not regex on transpiled code - actual source)
    assert "resolveGatewayRequestedOperatorScopes" in handler_code, \
        "resolveGatewayRequestedOperatorScopes not imported from http-auth-helpers"
    assert "authorizeOperatorScopesForMethod" in handler_code, \
        "authorizeOperatorScopesForMethod not imported from method-scopes"

    # Check they come from the right modules
    http_auth_helpers_import = re.search(
        r'import\s*\{[^}]*authorizeGatewayBearerRequestOrReply[^}]*\}\s*from\s*["\']\.\/http-auth-helpers(?:\.js)?["\']',
        handler_code
    )
    assert http_auth_helpers_import, \
        "authorizeGatewayBearerRequestOrReply not imported from http-auth-helpers"

    method_scopes_import = re.search(
        r'import\s*\{[^}]*authorizeOperatorScopesForMethod[^}]*\}\s*from\s*["\']\.\/method-scopes(?:\.js)?["\']',
        handler_code
    )
    assert method_scopes_import, \
        "authorizeOperatorScopesForMethod not imported from method-scopes"


# [pr_diff] fail_to_pass
def test_scope_authorization_called():
    """Handler must call authorizeOperatorScopesForMethod with 'agent' method."""
    handler_code = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()

    # Must call resolveGatewayRequestedOperatorScopes to get requested scopes
    assert "resolveGatewayRequestedOperatorScopes(req)" in handler_code or \
           re.search(r'resolveGatewayRequestedOperatorScopes\s*\(\s*req\s*\)', handler_code), \
        "resolveGatewayRequestedOperatorScopes(req) not called"

    # Must call authorizeOperatorScopesForMethod with 'agent' as first argument
    assert re.search(r'authorizeOperatorScopesForMethod\s*\(\s*["\']agent["\']\s*,', handler_code), \
        "authorizeOperatorScopesForMethod not called with 'agent' as first argument"


# [pr_diff] fail_to_pass
def test_scope_authorization_returns_403():
    """Handler must return 403 when scope authorization fails."""
    handler_code = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()

    # Check for 403 status in scope auth failure path
    scope_auth_section = re.search(
        r'authorizeOperatorScopesForMethod.*?if\s*\(\s*!?\s*\w+\.allowed\s*\)(.*?)(?:return|const|let|var|\})',
        handler_code,
        re.DOTALL
    )

    # Look for 403 in the code around scope authorization
    assert "403" in handler_code, "No 403 status code found in handler"

    # Check for forbidden error type
    assert '"forbidden"' in handler_code or "'forbidden'" in handler_code or \
           re.search(r'type\s*:\s*["\']forbidden["\']', handler_code), \
        "No 'forbidden' error type found in handler"

    # Check for missing scope message
    assert "missing scope" in handler_code.lower() or \
           re.search(r'missing[\s._]*scope', handler_code, re.IGNORECASE), \
        "No 'missing scope' error message found in handler"


# [pr_diff] fail_to_pass
def test_owner_only_filtering_import():
    """Handler must import applyOwnerOnlyToolPolicy function."""
    handler_code = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()

    # Check import from tool-policy module
    assert "applyOwnerOnlyToolPolicy" in handler_code, \
        "applyOwnerOnlyToolPolicy not found in handler"

    # Verify it's imported from the correct module (tool-policy or tool-policy-pipeline)
    pipeline_import = re.search(
        r'import\s*\{[^}]*applyOwnerOnlyToolPolicy[^}]*\}\s*from\s*["\'].*tool-policy(?:-pipeline)?(?:\.js)?["\']',
        handler_code
    )
    assert pipeline_import, \
        "applyOwnerOnlyToolPolicy not imported from tool-policy module"


# [pr_diff] fail_to_pass
def test_owner_only_filtering_called():
    """Handler must call applyOwnerOnlyToolPolicy with false for owner flag."""
    handler_code = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()

    # Must call applyOwnerOnlyToolPolicy with false as the second argument
    # This indicates HTTP surface doesn't have an owner identity
    assert re.search(r'applyOwnerOnlyToolPolicy\s*\([^,]+,\s*false\s*\)', handler_code), \
        "applyOwnerOnlyToolPolicy not called with 'false' as second argument (owner flag)"


# [pr_diff] fail_to_pass
def test_owner_only_filtering_order():
    """Owner-only filtering must happen before gateway deny filtering."""
    handler_code = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()

    # Find the variable that holds owner-filtered tools
    # Pattern: const ownerFiltered = applyOwnerOnlyToolPolicy(...)
    owner_filtered_match = re.search(
        r'const\s+(\w+)\s*=\s*applyOwnerOnlyToolPolicy',
        handler_code
    )
    assert owner_filtered_match, \
        "No variable assigned from applyOwnerOnlyToolPolicy result"

    owner_var = owner_filtered_match.group(1)

    # The owner-filtered variable must be used in the gateway filter step
    # Pattern: gatewayFiltered = ownerFiltered.filter(...)
    gateway_filter_pattern = rf'{owner_var}\.filter\s*\(\s*\(?\s*\w+\s*\)?\s*=>\s*!gatewayDenySet\.has'
    assert re.search(gateway_filter_pattern, handler_code), \
        f"Owner-filtered variable '{owner_var}' not used before gateway deny filtering"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_deny_entries_preserved():
    """Original deny list entries must not be removed."""
    deny = _get_deny_list()
    for tool in ["sessions_spawn", "sessions_send", "cron", "gateway", "whatsapp_login"]:
        assert tool in deny, f"Original entry '{tool}' removed from deny list"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_check():
    """Repo's full CI check (pnpm check) passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"CI check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's oxlint (pnpm lint) passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_security_audit():
    """Repo's security audit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.unit.config.ts", "src/security/audit.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Security audit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_modified_files_formatted():
    """Modified files are correctly formatted (pass_to_pass)."""
    for f in MODIFIED_FILES:
        r = subprocess.run(
            ["npx", "oxfmt", "--check", f],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"File {f} is not correctly formatted:\n{r.stderr[-200:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript type check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "tsgo"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript type check failed:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_method_scopes_unit():
    """Repo's method-scopes unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.gateway.config.ts", "src/gateway/method-scopes.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"method-scopes unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_http_auth_helpers_unit():
    """Repo's http-auth-helpers unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.gateway.config.ts", "src/gateway/http-auth-helpers.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"http-auth-helpers unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tools_invoke_http_unit():
    """Repo's tools-invoke-http unit tests pass (pass_to_pass)."""
    # Exclude test that expects gateway.tools.allow to bypass owner-only restriction,
    # since the security fix requires owner-only tools to be filtered for HTTP surface.
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.gateway.config.ts",
         "src/gateway/tools-invoke-http.test.ts",
         "-t", "^(?!.*allows gateway tool via HTTP when explicitly enabled)"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"tools-invoke-http unit tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ ae703ab0e7528ae215b6dd8e20dfa9b64f05a11e
def test_no_ts_nocheck():
    """Modified files must not contain @ts-nocheck directive."""
    for f in MODIFIED_FILES:
        content = Path(f"{REPO}/{f}").read_text()
        assert "@ts-nocheck" not in content, f"@ts-nocheck found in {f}"


# [agent_config] pass_to_pass — CLAUDE.md:144,147 @ ae703ab0e7528ae215b6dd8e20dfa9b64f05a11e
def test_no_any_type():
    """Modified files must not introduce new bare 'any' type annotations or disable no-explicit-any."""
    # Pre-existing `as any` in tools-invoke-http.ts (lines 276, 278, 323, 345) are baseline.
    # We check dangerous-tools.ts fully (clean baseline) and that tools-invoke-http.ts
    # doesn't INCREASE its `any` count beyond the known 4.
    for f in MODIFIED_FILES:
        content = Path(f"{REPO}/{f}").read_text()
        assert not re.search(
            r"(eslint-disable|oxlint-ignore).*no-explicit-any", content
        ), f"no-explicit-any suppression found in {f}"

    # dangerous-tools.ts must have zero `any` usages
    dt = Path(f"{REPO}/src/security/dangerous-tools.ts").read_text()
    any_matches = re.findall(r"(?::\s*any\b|\bas\s+any\b)", dt)
    assert len(any_matches) == 0, f"'any' type found in dangerous-tools.ts"

    # tools-invoke-http.ts baseline has exactly 4 `as any` casts; must not increase
    handler = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()
    any_count = len(re.findall(r"\bas\s+any\b", handler))
    assert any_count <= 4, (
        f"tools-invoke-http.ts has {any_count} 'as any' casts (baseline 4, must not increase)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:146 @ ae703ab0e7528ae215b6dd8e20dfa9b64f05a11e
def test_no_lint_suppression():
    """Modified files must not add eslint-disable or oxlint-ignore comments."""
    for f in MODIFIED_FILES:
        content = Path(f"{REPO}/{f}").read_text()
        for pattern, name in [
            (r"eslint-disable", "eslint-disable"),
            (r"oxlint-ignore", "oxlint-ignore"),
        ]:
            assert not re.search(pattern, content), f"{name} found in {f}"


# [agent_config] pass_to_pass — CLAUDE.md:152 @ ae703ab0e7528ae215b6dd8e20dfa9b64f05a11e
def test_no_magic_sentinels():
    """Modified files must not introduce new magic sentinels (?? 0, ?? '', ?? {})."""
    # Pre-existing sentinels in tools-invoke-http.ts: `?? {}` (line 175), `?? ""` (line 214).
    # dangerous-tools.ts must have zero; handler must not increase beyond baseline 2.
    dt = Path(f"{REPO}/src/security/dangerous-tools.ts").read_text()
    for line in dt.splitlines():
        stripped = re.sub(r"//.*$", "", line)
        assert not re.search(r'\?\?\s*(?:0\b|""|\'\'|\{\s*\})', stripped), (
            f"Magic sentinel in dangerous-tools.ts: {line.strip()}"
        )

    handler = Path(f"{REPO}/src/gateway/tools-invoke-http.ts").read_text()
    sentinel_count = 0
    for line in handler.splitlines():
        stripped = re.sub(r"//.*$", "", line)
        sentinel_count += len(re.findall(r'\?\?\s*(?:0\b|""|\'\'|\{\s*\})', stripped))
    assert sentinel_count <= 2, (
        f"tools-invoke-http.ts has {sentinel_count} magic sentinels (baseline 2, must not increase)"
    )
