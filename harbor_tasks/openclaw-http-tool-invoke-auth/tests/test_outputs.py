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


def _get_handler_transpiled() -> str:
    """Transpile tools-invoke-http.ts and return comment-stripped ESM code."""
    raw = _run_node("""
        const esbuild = require('esbuild');
        const result = esbuild.buildSync({
            entryPoints: ['src/gateway/tools-invoke-http.ts'],
            bundle: false, write: false, format: 'esm',
            loader: { '.ts': 'ts' },
        });
        console.log(new TextDecoder().decode(result.outputFiles[0].contents));
    """)
    # Strip comments to prevent comment-only "fixes"
    code = re.sub(r"//.*$", "", raw, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


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
# Fail-to-pass (pr_diff) — handler authorization wiring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scope_authorization_in_handler():
    """Handler must import and call scope authorization, returning 403 on failure."""
    code = _get_handler_transpiled()
    assert re.search(
        r"import\s*\{[^}]*\bauthorizeOperatorScopesForMethod\b[^}]*\}\s*from", code
    ), "authorizeOperatorScopesForMethod not imported"
    assert re.search(
        r"import\s*\{[^}]*\bresolveGatewayRequestedOperatorScopes\b[^}]*\}\s*from", code
    ), "resolveGatewayRequestedOperatorScopes not imported"
    assert re.search(
        r"""\bauthorizeOperatorScopesForMethod\s*\(\s*["']agent["']""", code
    ), "authorizeOperatorScopesForMethod not called with 'agent'"
    assert "403" in code, "No 403 status code in handler"
    assert re.search(r"\bforbidden\b", code, re.IGNORECASE) or re.search(
        r"missing[\s._]*scope", code, re.IGNORECASE
    ), "No forbidden/missing-scope error message in handler"


# [pr_diff] fail_to_pass
def test_owner_only_filtering_in_handler():
    """Handler must filter owner-only tools from HTTP surface."""
    code = _get_handler_transpiled()
    # Approach A: import + call applyOwnerOnlyToolPolicy(_, false)
    approach_a = bool(
        re.search(r"import\s*\{[^}]*\bapplyOwnerOnlyToolPolicy\b[^}]*\}\s*from", code)
        and re.search(r"\bapplyOwnerOnlyToolPolicy\s*\([^)]*,\s*false\s*\)", code)
    )
    # Approach B: manual .filter on ownerOnly property
    approach_b = bool(re.search(r"\.filter\s*\([^)]*\.ownerOnly\b", code))
    # Approach C: any owner-related call with false + filter
    approach_c = bool(
        re.search(r"\b\w+[Oo]wner\w*\s*\([^)]*,\s*false\s*\)", code)
        and re.search(r"\bfilter\b", code)
    )
    assert approach_a or approach_b or approach_c, (
        "No owner-only tool filtering found in handler"
    )


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
