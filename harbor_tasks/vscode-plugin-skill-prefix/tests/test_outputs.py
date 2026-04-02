"""
Task: vscode-plugin-skill-prefix
Repo: vscode @ 559cb3e74d075670b9a03f84751e8fdcd3c52443
PR:   307305

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"

PLUGIN_SERVICE = "src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts"
PROMPTS_SERVICE = "src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts"


def _read(rel_path: str) -> str:
    return Path(f"{REPO}/{rel_path}").read_text()


def _extract_method(source: str, method_name: str) -> str:
    """Extract a method body from TypeScript class source by brace-matching."""
    pattern = rf"(private|public|protected)?\s*(async\s+)?{re.escape(method_name)}\s*\("
    match = re.search(pattern, source)
    if not match:
        return ""
    start = match.start()
    # Find the opening brace of the method body
    brace_pos = source.index("{", match.end())
    depth = 1
    i = brace_pos + 1
    while i < len(source) and depth > 0:
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
        i += 1
    return source[start:i]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript type checker passes on modified source files."""
    # Use VS Code's own type checker (tsgo --noEmit)
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"TypeScript type check failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_plugin_prefix_in_discovery():
    """Plugin skills get canonical plugin prefix applied during slash command discovery."""
    src = _read(PROMPTS_SERVICE)
    method_body = _extract_method(src, "computeSlashCommandDiscoveryInfo")
    assert method_body, "computeSlashCommandDiscoveryInfo method not found"

    # The method must call getCanonicalPluginCommandId to canonicalize plugin skill names.
    # On the base commit, this method does NOT call getCanonicalPluginCommandId at all —
    # it only computes `name` from header/promptPath/cleanName without any plugin prefix.
    assert "getCanonicalPluginCommandId" in method_body, (
        "computeSlashCommandDiscoveryInfo must call getCanonicalPluginCommandId "
        "to prefix plugin skill names with the plugin identifier"
    )

    # Verify the call uses the plugin URI, not an arbitrary value
    assert "pluginUri" in method_body, (
        "getCanonicalPluginCommandId call must use the plugin URI "
        "to derive the correct prefix"
    )


# [pr_diff] fail_to_pass
def test_frontmatter_override_prefixed():
    """Even when SKILL.md frontmatter overrides the name, plugin prefix is preserved."""
    src = _read(PROMPTS_SERVICE)
    method_body = _extract_method(src, "computeSlashCommandDiscoveryInfo")
    assert method_body, "computeSlashCommandDiscoveryInfo method not found"

    # The frontmatter name (parsedPromptFile?.header?.name) must be transformed for
    # plugin sources — it cannot flow directly to withPromptPathMetadata as the
    # final name. The fix must ensure that the header name goes through
    # canonicalization (getCanonicalPluginCommandId or similar) for plugin sources.
    #
    # On the base commit there is exactly one assignment:
    #   const name = parsedPromptFile?.header?.name ?? promptPath.name ?? getCleanPromptName(promptPath.uri);
    # and no subsequent transformation. After the fix, the code must either:
    #   (a) Assign header name to an intermediate variable, then derive `name` conditionally
    #   (b) Re-assign the name after initial computation for plugin sources
    #
    # We detect this by checking that there are at least TWO variable assignments
    # related to the name computation (the raw extraction + the canonical transformation),
    # OR that the header name variable is not directly named 'name' (renamed to rawName etc).

    header_pattern = re.compile(
        r"const\s+(\w+)\s*=\s*parsedPromptFile\?\.header\?\.name"
    )
    match = header_pattern.search(method_body)
    assert match, "Expected assignment from parsedPromptFile?.header?.name"
    header_var = match.group(1)

    # Check option (a): header goes to intermediate variable (not 'name')
    uses_intermediate = header_var != "name"

    # Check option (b): there's a second assignment that transforms the name for plugins
    # e.g. `const prefixedName = ... getCanonicalPluginCommandId ...` or reassignment
    has_transform = bool(re.search(
        r"(getCanonicalPluginCommandId|normalizePluginToken|basename)\s*\(",
        method_body[match.end():]
    ))

    assert uses_intermediate or has_transform, (
        f"Header name is assigned directly to '{header_var}' with no subsequent "
        "plugin prefix transformation. The frontmatter name must be canonicalized "
        "for plugin sources before being used as the final slash command name."
    )


# [pr_diff] fail_to_pass
def test_type_signature_widened():
    """getCanonicalPluginCommandId accepts a type wider than IAgentPlugin, or caller provides plugin prefix another way."""
    src_plugin = _read(PLUGIN_SERVICE)
    src_prompts = _read(PROMPTS_SERVICE)

    # The function on the base commit accepts only `IAgentPlugin`. To call it from
    # computeSlashCommandDiscoveryInfo (which only has a pluginUri, not a full
    # IAgentPlugin), the agent must do one of:
    #   (a) Widen the parameter type (e.g. `{ readonly uri: URI }`)
    #   (b) Write a new helper / inline the prefix logic
    #
    # We check: either (a) the function's first param is no longer IAgentPlugin,
    # or (b) the discovery method constructs the prefix without calling this function.

    func_pattern = re.compile(
        r"export\s+function\s+getCanonicalPluginCommandId\s*\(\s*(\w+)\s*:\s*([^,]+)"
    )
    match = func_pattern.search(src_plugin)
    assert match, "getCanonicalPluginCommandId export not found"

    param_type = match.group(2).strip()
    type_is_widened = param_type != "IAgentPlugin"

    # Alternative: discovery method applies the prefix inline, via a new function,
    # or by looking up the full plugin object from a service
    method_body = _extract_method(src_prompts, "computeSlashCommandDiscoveryInfo")
    has_alternative_prefix = (
        "pluginUri" in method_body
        and (
            "basename" in method_body
            or "normalize" in method_body
            or "prefix" in method_body.lower()
            or "getCanonicalPluginCommandId" in method_body  # using original fn with looked-up plugin
        )
    )

    assert type_is_widened or has_alternative_prefix, (
        f"getCanonicalPluginCommandId first param is still 'IAgentPlugin' and "
        f"computeSlashCommandDiscoveryInfo does not apply the prefix. "
        f"Either widen the type to accept {{ uri: URI }} or build the prefix another way."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_non_plugin_sources_unaffected():
    """Non-plugin sources still use unmodified name (no false prefix application)."""
    src = _read(PROMPTS_SERVICE)

    # The slashCommandsFromDiscoveryInfo method (which builds the final command list)
    # must still exist and produce results from the discovery info.
    # Also, the local-prompts code path in computeSlashCommandDiscoveryInfo must still
    # fall back to getCleanPromptName for non-plugin sources.
    assert "getCleanPromptName" in src, (
        "getCleanPromptName must still be used as fallback for non-plugin prompt names"
    )

    # slashCommandsFromDiscoveryInfo must still exist (regression guard)
    assert "slashCommandsFromDiscoveryInfo" in src, (
        "slashCommandsFromDiscoveryInfo method must still exist to convert discovery info to commands"
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:101-102
def test_no_arrow_function_for_export():
    """Exported function uses function keyword, not arrow expression."""
    src = _read(PLUGIN_SERVICE)

    # Check that getCanonicalPluginCommandId uses `export function`, not `export const ... = (`
    assert re.search(
        r"export\s+function\s+getCanonicalPluginCommandId", src
    ), (
        "getCanonicalPluginCommandId must use 'export function' declaration, "
        "not 'export const' arrow function (per copilot-instructions.md)"
    )
