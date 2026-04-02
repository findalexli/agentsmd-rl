"""
Task: openclaw-subagent-tool-resolution
Repo: openclaw/openclaw @ 6883f688e8da11481a5d0f91dfab4e4ba6e9f871
PR:   56240

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = Path(REPO) / "src" / "plugins" / "tools.ts"
PLUGINS_DIR = Path(REPO) / "src" / "plugins"


def _ensure_deps():
    """Ensure node_modules exist (idempotent)."""
    if not Path(REPO, "node_modules").exists():
        subprocess.run(
            ["npm", "install", "--ignore-scripts"],
            cwd=REPO, capture_output=True, timeout=120,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """src/plugins/tools.ts must parse without TypeScript errors."""
    _ensure_deps()
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "src/plugins/tools.ts"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    if r.returncode == 0:
        return
    # Fall back to esbuild parse
    r = subprocess.run(
        ["npx", "esbuild", "src/plugins/tools.ts",
         "--platform=node", "--format=esm", "--outfile=/dev/null"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, (
        f"tools.ts has syntax/type errors:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral / structural checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_active_registry_import():
    """tools.ts must import getActivePluginRegistry from ./runtime.js.

    On the base commit, tools.ts does not reference getActivePluginRegistry.
    The fix must import it so sub-agents can reuse the gateway's active registry.
    """
    content = TARGET.read_text()
    assert "getActivePluginRegistry" in content, (
        "tools.ts does not reference getActivePluginRegistry -- "
        "sub-agent sessions need the active registry fallback"
    )
    # Verify it's an actual import, not just a comment
    assert re.search(
        r'''import\s*\{[^}]*getActivePluginRegistry[^}]*\}\s*from\s*["']\.\/runtime''',
        content,
    ), (
        "getActivePluginRegistry must be imported from ./runtime.js"
    )


# [pr_diff] fail_to_pass
def test_registry_selection_logic():
    """Registry selection must branch on allowGatewaySubagentBinding and prefer active registry.

    The fix must implement logic equivalent to:
      if (allowGatewaySubagentBinding) {
        return getActivePluginRegistry() ?? resolveRuntimePluginRegistry(loadOptions);
      }
      return resolveRuntimePluginRegistry(loadOptions);

    This ensures sub-agent sessions reuse the gateway's active registry when available,
    while non-sub-agent paths continue to use the loader directly.
    """
    content = TARGET.read_text()

    # All three elements must be present
    assert "getActivePluginRegistry" in content, "Missing getActivePluginRegistry"
    assert "resolveRuntimePluginRegistry" in content, "Missing resolveRuntimePluginRegistry"
    assert "allowGatewaySubagentBinding" in content, "Missing allowGatewaySubagentBinding"

    # getActivePluginRegistry must be CALLED (not just imported)
    assert re.search(r"getActivePluginRegistry\s*\(", content), (
        "getActivePluginRegistry is imported but never called"
    )

    # The call to getActivePluginRegistry() must appear in a context that
    # also references allowGatewaySubagentBinding -- verifying they're logically connected.
    # Extract all function bodies that call getActivePluginRegistry()
    # and verify at least one also references allowGatewaySubagentBinding.
    lines = content.splitlines()
    call_lines = [i for i, l in enumerate(lines) if "getActivePluginRegistry(" in l]
    assert call_lines, "getActivePluginRegistry() is never called"

    # Check a window around each call site for allowGatewaySubagentBinding
    found_connection = False
    for call_line in call_lines:
        window_start = max(0, call_line - 15)
        window_end = min(len(lines), call_line + 5)
        window = "\n".join(lines[window_start:window_end])
        if "allowGatewaySubagentBinding" in window:
            found_connection = True
            break
    assert found_connection, (
        "getActivePluginRegistry() call is not connected to "
        "allowGatewaySubagentBinding -- the registry fallback must be conditional "
        "on the subagent binding context"
    )

    # The fallback pattern: getActivePluginRegistry() must have a fallback to
    # resolveRuntimePluginRegistry (via ?? or || or if/else)
    for call_line in call_lines:
        window_start = max(0, call_line - 2)
        window_end = min(len(lines), call_line + 3)
        window = "\n".join(lines[window_start:window_end])
        if "resolveRuntimePluginRegistry" in window:
            found_connection = True
            break
    else:
        # Check for conditional pattern (if/else with both calls)
        content_no_ws = re.sub(r"\s+", " ", content)
        has_conditional = (
            re.search(r"getActivePluginRegistry\s*\(\s*\)\s*\?\?", content_no_ws)
            or re.search(r"getActivePluginRegistry\s*\(\s*\)\s*\|\|", content_no_ws)
            or ("getActivePluginRegistry" in content and "resolveRuntimePluginRegistry" in content)
        )
        assert has_conditional, (
            "getActivePluginRegistry() must have a fallback to "
            "resolveRuntimePluginRegistry when no active registry exists"
        )


# [pr_diff] fail_to_pass
def test_resolve_tools_delegates_registry():
    """resolvePluginTools must not call resolveRuntimePluginRegistry directly at the assignment site.

    On the base commit, resolvePluginTools has:
      const registry = resolveRuntimePluginRegistry(loadOptions);

    The fix must route through a helper (resolvePluginToolRegistry or equivalent)
    that conditionally uses the active registry. Verify the direct call is replaced.
    """
    content = TARGET.read_text()

    # Find the resolvePluginTools function body
    match = re.search(
        r"export\s+function\s+resolvePluginTools\s*\([^)]*\)\s*(?::\s*\S+\s*)?\{",
        content,
    )
    assert match, "resolvePluginTools function not found"

    # Extract the function body (approximate: find matching braces)
    start = match.end()
    depth = 1
    pos = start
    while pos < len(content) and depth > 0:
        if content[pos] == "{":
            depth += 1
        elif content[pos] == "}":
            depth -= 1
        pos += 1
    fn_body = content[start:pos]

    # The function body should NOT have a direct `= resolveRuntimePluginRegistry(` assignment.
    # It should delegate to a helper that handles the active registry fallback.
    direct_call = re.search(
        r"=\s*resolveRuntimePluginRegistry\s*\(",
        fn_body,
    )
    assert not direct_call, (
        "resolvePluginTools still calls resolveRuntimePluginRegistry directly -- "
        "it must delegate to a helper that checks the active registry for sub-agent sessions"
    )

    # But resolveRuntimePluginRegistry must still exist somewhere in the file
    # (used by the helper function, not removed entirely)
    assert "resolveRuntimePluginRegistry" in content, (
        "resolveRuntimePluginRegistry was removed entirely -- "
        "it's still needed as the fallback in the helper"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_optional_tool_tests():
    """Existing vitest tests in tools.optional.test.ts still pass."""
    _ensure_deps()
    r = subprocess.run(
        ["npx", "vitest", "run", "src/plugins/tools.optional.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"tools.optional.test.ts failed:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_loader_regression():
    """Upstream plugin loader tests still pass after the fix."""
    _ensure_deps()
    r = subprocess.run(
        ["npx", "vitest", "run", "src/plugins/loader.test.ts",
         "--reporter=verbose"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"loader.test.ts regression:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- CLAUDE.md:146 @ 6883f688
def test_no_ts_nocheck():
    """No @ts-nocheck directives in src/plugins/ (CLAUDE.md:146)."""
    violations = []
    for ts_file in PLUGINS_DIR.rglob("*.ts"):
        if ts_file.name.endswith(".d.ts") or ".test." in ts_file.name:
            continue
        content = ts_file.read_text()
        if "@ts-nocheck" in content:
            violations.append(str(ts_file.relative_to(REPO)))
    assert not violations, (
        f"@ts-nocheck found in: {', '.join(violations)} -- "
        "fix root causes instead (CLAUDE.md:146)"
    )


# [agent_config] pass_to_pass -- CLAUDE.md:146 @ 6883f688
def test_no_unexplained_lint_suppressions():
    """No eslint-disable or oxlint-ignore without explanatory comment (CLAUDE.md:146).

    Suppressions are allowed only when accompanied by a comment explaining why.
    """
    violations = []
    for ts_file in PLUGINS_DIR.rglob("*.ts"):
        if ts_file.name.endswith(".d.ts") or ".test." in ts_file.name:
            continue
        lines = ts_file.read_text().splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if re.search(r"(eslint-disable|oxlint-ignore)", stripped):
                after_directive = re.split(r"eslint-disable\S*|oxlint-ignore\S*", stripped)[-1]
                if not re.search(r"--\s*\S|because|reason|TODO", after_directive, re.IGNORECASE):
                    rel = ts_file.relative_to(REPO)
                    violations.append(f"{rel}:{i}")
    assert not violations, (
        f"Unexplained lint suppressions at: {', '.join(violations)} -- "
        "add a comment explaining why (CLAUDE.md:146)"
    )


# [agent_config] pass_to_pass -- CLAUDE.md:153 @ 6883f688
def test_no_prototype_mutation():
    """No prototype mutation in tools.ts (CLAUDE.md:153).

    Use explicit inheritance/composition instead of .prototype manipulation.
    Scoped to the modified file only.
    """
    content = TARGET.read_text()
    assert not re.search(r"\.\bprototype\b\s*[.=\[]", content), (
        "Prototype mutation found in tools.ts -- "
        "use inheritance/composition (CLAUDE.md:153)"
    )


# [agent_config] pass_to_pass -- CLAUDE.md:148 @ 6883f688
def test_no_mixed_static_dynamic_imports():
    """No module is both statically and dynamically imported in tools.ts (CLAUDE.md:148).

    Mixing await import("x") and static import from "x" for the same module
    in production code paths is forbidden.
    """
    content = TARGET.read_text()
    static_imports = set(re.findall(r'import\s+.*?from\s+["\']([^"\']+)["\']', content))
    dynamic_imports = set(re.findall(r'await\s+import\s*\(\s*["\']([^"\']+)["\']\s*\)', content))
    overlap = static_imports & dynamic_imports
    assert not overlap, (
        f"Module(s) both statically and dynamically imported in tools.ts: {overlap} -- "
        "pick one import style per module (CLAUDE.md:148)"
    )


# [agent_config] pass_to_pass -- CLAUDE.md:42 @ 6883f688
def test_no_deep_plugin_internal_imports():
    """tools.ts must not deep-import bundled plugin internals (CLAUDE.md:42).

    Core code must not import from extensions/<id>/src/** directly.
    """
    content = TARGET.read_text()
    deep_imports = re.findall(r'from\s+["\'].*extensions/[^"\']+/src/[^"\']+["\']', content)
    assert not deep_imports, (
        f"Deep plugin internal imports found: {deep_imports} -- "
        "use public SDK exports instead (CLAUDE.md:42)"
    )


# [agent_config] pass_to_pass -- CLAUDE.md:147 @ 6883f688
def test_no_explicit_any_disable():
    """tools.ts must not disable no-explicit-any (CLAUDE.md:147).

    Prefer real types, unknown, or a narrow adapter/helper instead.
    """
    content = TARGET.read_text()
    assert not re.search(r"no-explicit-any", content), (
        "no-explicit-any suppression found in tools.ts -- "
        "prefer real types or unknown (CLAUDE.md:147)"
    )
