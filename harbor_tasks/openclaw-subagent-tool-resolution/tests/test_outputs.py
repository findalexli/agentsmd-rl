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

# ---------------------------------------------------------------------------
# Vitest test for behavioral verification of subagent tool resolution.
#
# On the base commit, resolvePluginTools calls resolveRuntimePluginRegistry
# directly, ignoring any active registry set during gateway startup.
# The fix adds a resolvePluginToolRegistry helper that checks
# getActivePluginRegistry() first when allowGatewaySubagentBinding is true,
# so sub-agent sessions reuse the gateway's active registry.
#
# This vitest test:
#   1. Mocks the loader (resolveRuntimePluginRegistry) to return undefined
#   2. Sets an active registry via the real runtime module
#   3. Calls resolvePluginTools with allowGatewaySubagentBinding=true
#   4. Asserts the tools come from the active registry (not the mock loader)
#   5. Asserts the mock loader was NOT called
#
# On base: loader IS called (returns undefined) -> empty tools -> FAIL
# On fix:  active registry IS used -> tools returned -> PASS
# ---------------------------------------------------------------------------
_VITEST_SUBAGENT_TEST = '''\
import { beforeEach, describe, expect, it, vi } from "vitest";

const resolveRuntimePluginRegistryMock = vi.fn();
const applyPluginAutoEnableMock = vi.fn();

vi.mock("./loader.js", () => ({
  resolveRuntimePluginRegistry: (params: unknown) =>
    resolveRuntimePluginRegistryMock(params),
}));

vi.mock("../config/plugin-auto-enable.js", () => ({
  applyPluginAutoEnable: (params: unknown) => applyPluginAutoEnableMock(params),
}));

let resolvePluginTools: typeof import("./tools.js").resolvePluginTools;
let resetPluginRuntimeStateForTest: typeof import("./runtime.js").resetPluginRuntimeStateForTest;
let setActivePluginRegistry: typeof import("./runtime.js").setActivePluginRegistry;

function makeTool(name: string) {
  return {
    name,
    description: `${name} tool`,
    parameters: { type: "object", properties: {} },
    async execute() {
      return { content: [{ type: "text", text: "ok" }] };
    },
  };
}

function createContext() {
  return {
    config: {
      plugins: {
        enabled: true,
        allow: ["optional-demo"],
        load: { paths: ["/tmp/plugin.js"] },
      },
    },
    workspaceDir: "/tmp",
  };
}

describe("subagent tool resolution", () => {
  beforeEach(async () => {
    vi.resetModules();
    resolveRuntimePluginRegistryMock.mockReset();
    resolveRuntimePluginRegistryMock.mockReturnValue(undefined);
    applyPluginAutoEnableMock.mockReset();
    applyPluginAutoEnableMock.mockImplementation(
      ({ config }: { config: unknown }) => ({ config, changes: [] }),
    );
    ({ resetPluginRuntimeStateForTest, setActivePluginRegistry } =
      await import("./runtime.js"));
    resetPluginRuntimeStateForTest();
    ({ resolvePluginTools } = await import("./tools.js"));
  });

  it("reuses active registry for gateway-bindable loads instead of calling loader", () => {
    const activeRegistry = {
      tools: [
        {
          pluginId: "optional-demo",
          optional: true,
          source: "/tmp/optional-demo.js",
          factory: () => makeTool("optional_tool"),
        },
      ],
      diagnostics: [] as Array<{
        level: string;
        pluginId: string;
        source: string;
        message: string;
      }>,
    };
    setActivePluginRegistry(activeRegistry as never, "gateway-startup");

    const tools = resolvePluginTools({
      context: createContext() as never,
      toolAllowlist: ["optional_tool"],
      allowGatewaySubagentBinding: true,
    });

    expect(tools.map((t) => t.name)).toEqual(["optional_tool"]);
    expect(resolveRuntimePluginRegistryMock).not.toHaveBeenCalled();
  });
});
'''

_EVAL_TEST_PATH = Path(REPO) / "src" / "plugins" / "_eval_subagent_binding.test.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """src/plugins/tools.ts must parse as valid TypeScript (balanced braces, no truncation)."""
    content = TARGET.read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 1, (
        f"Unbalanced braces in tools.ts ({opens} open, {closes} close) — likely truncated or corrupt"
    )
    assert len(content) > 500, "tools.ts is suspiciously short — likely stub or truncated"
    assert "export function resolvePluginTools" in content, (
        "resolvePluginTools export not found — file may be corrupt"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral + structural checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — behavioral (subprocess)
def test_subagent_uses_active_registry():
    """Sub-agent sessions must reuse the gateway's active plugin registry.

    Runs a vitest test that sets an active registry via the real runtime module,
    then calls resolvePluginTools with allowGatewaySubagentBinding=true.
    Verifies the tools come from the active registry and the loader mock was
    NOT called. Fails on the base commit where resolvePluginTools always calls
    resolveRuntimePluginRegistry directly (ignoring the active registry).
    """
    _EVAL_TEST_PATH.write_text(_VITEST_SUBAGENT_TEST)
    try:
        r = subprocess.run(
            ["pnpm", "exec", "vitest", "run", str(_EVAL_TEST_PATH),
             "--reporter=verbose", "--no-color"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"Subagent tool resolution does not reuse active registry:\n"
            f"{r.stdout[-2000:]}\n{r.stderr[-1000:]}"
        )
    finally:
        _EVAL_TEST_PATH.unlink(missing_ok=True)


# [pr_diff] fail_to_pass — structural
def test_active_registry_import():
    """tools.ts must import getActivePluginRegistry from ./runtime.js.

    On the base commit, tools.ts does not reference getActivePluginRegistry.
    The fix must import it so sub-agents can reuse the gateway's active registry.
    """
    content = TARGET.read_text()
    assert "getActivePluginRegistry" in content, (
        "tools.ts does not reference getActivePluginRegistry — "
        "sub-agent sessions need the active registry fallback"
    )
    # Verify it's an actual import, not just a comment
    assert re.search(
        r'''import\s*\{[^}]*getActivePluginRegistry[^}]*\}\s*from\s*["']\.\/runtime''',
        content,
    ), (
        "getActivePluginRegistry must be imported from ./runtime.js"
    )


# [pr_diff] fail_to_pass — structural
def test_resolve_tools_delegates_registry():
    """resolvePluginTools must not call resolveRuntimePluginRegistry directly at the assignment site.

    On the base commit, resolvePluginTools has:
      const registry = resolveRuntimePluginRegistry(loadOptions);

    The fix must route through a helper or conditional that uses the active registry.
    Verify the direct call is replaced with branching logic.
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
    # It should delegate to a helper or conditional that handles the active registry fallback.
    direct_call = re.search(
        r"=\s*resolveRuntimePluginRegistry\s*\(",
        fn_body,
    )
    assert not direct_call, (
        "resolvePluginTools still calls resolveRuntimePluginRegistry directly — "
        "it must delegate through logic that checks the active registry for sub-agent sessions"
    )

    # But resolveRuntimePluginRegistry must still exist somewhere in the file
    # (used by the helper/conditional, not removed entirely)
    assert "resolveRuntimePluginRegistry" in content, (
        "resolveRuntimePluginRegistry was removed entirely — "
        "it's still needed as the fallback when no active registry exists"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — verify repo's own checks pass on base AND gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — oxlint
def test_repo_oxlint():
    """Repo's oxlint passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "oxlint", "--type-aware"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — plugin unit tests
def test_repo_plugins_unit():
    """Repo's plugin unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", "vitest.unit.config.ts", "src/plugins/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — contracts tests
def test_repo_contracts():
    """Repo's contracts tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "--config", "vitest.contracts.config.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Contracts tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — format check
def test_repo_format_check():
    """Repo's formatting check passes on tools.ts (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "oxfmt", "--check", "src/plugins/tools.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — bundled plugin metadata check
def test_repo_bundled_plugin_metadata():
    """Repo's bundled plugin metadata check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/generate-bundled-plugin-metadata.mjs", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Bundled plugin metadata check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — bundled provider auth env vars check
def test_repo_bundled_provider_auth():
    """Repo's bundled provider auth env vars check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/generate-bundled-provider-auth-env-vars.mjs", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Bundled provider auth check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — no conflict markers check
def test_repo_no_conflict_markers():
    """Repo's no-conflict-markers check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-no-conflict-markers.mjs"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"No conflict markers check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / src/plugins/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:146 @ 6883f688
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
        f"@ts-nocheck found in: {', '.join(violations)} — "
        "fix root causes instead (CLAUDE.md:146)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 6883f688
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
        f"Unexplained lint suppressions at: {', '.join(violations)} — "
        "add a comment explaining why (CLAUDE.md:146)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:153 @ 6883f688
def test_no_prototype_mutation():
    """No prototype mutation in tools.ts (CLAUDE.md:153).

    Use explicit inheritance/composition instead of .prototype manipulation.
    """
    content = TARGET.read_text()
    assert not re.search(r"\.\bprototype\b\s*[.=\[]", content), (
        "Prototype mutation found in tools.ts — "
        "use inheritance/composition (CLAUDE.md:153)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:148 @ 6883f688
def test_no_mixed_static_dynamic_imports():
    """No module is both statically and dynamically imported in tools.ts (CLAUDE.md:148).

    Mixing await import("x") and static import from "x" for the same module
    in production code paths is forbidden.
    """
    content = TARGET.read_text()
    static_imports = set(re.findall(r'import\s+.*?from\s+["\'`]([^"\'`]+)["\'`]', content))
    dynamic_imports = set(re.findall(r'await\s+import\s*\(\s*["\'`]([^"\'`]+)["\'`]\s*\)', content))
    overlap = static_imports & dynamic_imports
    assert not overlap, (
        f"Module(s) both statically and dynamically imported in tools.ts: {overlap} — "
        "pick one import style per module (CLAUDE.md:148)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:42 @ 6883f688
def test_no_deep_plugin_internal_imports():
    """tools.ts must not deep-import bundled plugin internals (CLAUDE.md:42).

    Core code must not import from extensions/<id>/src/** directly.
    """
    content = TARGET.read_text()
    deep_imports = re.findall(r'from\s+["\'`].*extensions/[^"\'`]+/src/[^"\'`]+["\'`]', content)
    assert not deep_imports, (
        f"Deep plugin internal imports found: {deep_imports} — "
        "use public SDK exports instead (CLAUDE.md:42)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:147 @ 6883f688
def test_no_explicit_any_disable():
    """tools.ts must not disable no-explicit-any (CLAUDE.md:147).

    Prefer real types, unknown, or a narrow adapter/helper instead.
    """
    content = TARGET.read_text()
    assert not re.search(r"no-explicit-any", content), (
        "no-explicit-any suppression found in tools.ts — "
        "prefer real types or unknown (CLAUDE.md:147)"
    )


# [agent_config] pass_to_pass — src/plugins/CLAUDE.md:28-31 @ 6883f688
def test_no_direct_plugin_config_reads():
    """tools.ts must not read plugins.entries.<id>.config directly (src/plugins/CLAUDE.md:28-31).

    Prefer generic helpers, plugin runtime hooks, or manifest metadata.
    """
    content = TARGET.read_text()
    violations = re.findall(r"plugins\.entries\.\w+\.config", content)
    assert not violations, (
        f"Direct plugin config reads found: {violations} — "
        "use generic helpers or manifest metadata (src/plugins/CLAUDE.md:28-31)"
    )
