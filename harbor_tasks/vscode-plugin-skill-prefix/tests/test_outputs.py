"""
Task: vscode-plugin-skill-prefix
Repo: microsoft/vscode @ 559cb3e74d075670b9a03f84751e8fdcd3c52443
PR:   307305

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"

PLUGIN_SERVICE = "src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts"
PROMPTS_SERVICE = "src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts"


def _read(rel_path: str) -> str:
    return Path(f"{REPO}/{rel_path}").read_text()


def _extract_name_assignment_block(src: str) -> str:
    """Extract the ~30-line block around the name assignment in computeSlashCommandDiscoveryInfo.

    AST-only because: TypeScript source, not executable Python.

    We locate 'computeSlashCommandDiscoveryInfo' then find the name assignment
    region (parsedPromptFile?.header?.name) and return a bounded window.
    """
    lines = src.splitlines()
    # Find the method definition line
    method_start = None
    for i, line in enumerate(lines):
        if "computeSlashCommandDiscoveryInfo" in line and ("private" in line or "async" in line):
            method_start = i
            break
    if method_start is None:
        return ""

    # The relevant code (parseResults block with name assignment) is within
    # ~40 lines of the method start. Extract that bounded region.
    block = lines[method_start:method_start + 45]
    return "\n".join(block)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: TypeScript source files require full VS Code build infra
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_plugin_prefix_in_discovery():
    """Plugin skills get canonical plugin prefix applied during slash command discovery."""
    src = _read(PROMPTS_SERVICE)
    block = _extract_name_assignment_block(src)
    assert block, "computeSlashCommandDiscoveryInfo method not found"

    # The name assignment region must call getCanonicalPluginCommandId.
    # On the base commit, this block only has:
    #   const name = parsedPromptFile?.header?.name ?? promptPath.name ?? getCleanPromptName(...)
    # with no call to getCanonicalPluginCommandId.
    assert "getCanonicalPluginCommandId" in block, (
        "computeSlashCommandDiscoveryInfo must call getCanonicalPluginCommandId "
        "to prefix plugin skill names with the plugin identifier"
    )


# [pr_diff] fail_to_pass
def test_frontmatter_override_prefixed():
    """Even when SKILL.md frontmatter overrides the name, plugin prefix is preserved."""
    src = _read(PROMPTS_SERVICE)
    block = _extract_name_assignment_block(src)
    assert block, "computeSlashCommandDiscoveryInfo method not found"

    # On base commit the header name flows directly to `const name = ...`.
    # A correct fix must split this into raw extraction + conditional canonicalization.
    # Check: the header?.name value is NOT assigned directly to `const name`.
    lines_with_header = [
        l.strip() for l in block.splitlines()
        if "parsedPromptFile?.header?.name" in l or "parsedPromptFile.header?.name" in l
    ]
    assert lines_with_header, "Expected reference to parsedPromptFile?.header?.name"

    # The variable receiving the header name must not be called 'name' directly,
    # OR there must be a subsequent transformation step.
    header_line = lines_with_header[0]
    match = re.search(r"const\s+(\w+)\s*=", header_line)
    if match:
        var_name = match.group(1)
        uses_intermediate = var_name != "name"
    else:
        uses_intermediate = False

    has_transform = "getCanonicalPluginCommandId" in block

    assert uses_intermediate or has_transform, (
        "Header name is assigned directly to 'name' with no plugin prefix transformation. "
        "The frontmatter name must be canonicalized for plugin sources."
    )


# [pr_diff] fail_to_pass
def test_type_signature_widened():
    """getCanonicalPluginCommandId accepts a type wider than IAgentPlugin."""
    src_plugin = _read(PLUGIN_SERVICE)

    func_pattern = re.compile(
        r"export\s+function\s+getCanonicalPluginCommandId\s*\(\s*(\w+)\s*:\s*([^,)]+)"
    )
    match = func_pattern.search(src_plugin)
    assert match, "getCanonicalPluginCommandId export not found"

    param_type = match.group(2).strip()

    # On base commit the type is exactly `IAgentPlugin`.
    # The fix must widen it (e.g., `{ readonly uri: URI }`) so it can be called
    # from computeSlashCommandDiscoveryInfo which only has a pluginUri, not a full plugin.
    # Alternatively, the agent may inline the prefix logic without calling this function.
    type_is_widened = param_type != "IAgentPlugin"

    # Check alternative: inline prefix in discovery method
    src_prompts = _read(PROMPTS_SERVICE)
    discovery_block = _extract_name_assignment_block(src_prompts)
    has_inline_prefix = (
        "pluginUri" in discovery_block
        and ("basename" in discovery_block or "normalize" in discovery_block)
        and "getCanonicalPluginCommandId" not in discovery_block
    )

    assert type_is_widened or has_inline_prefix, (
        f"getCanonicalPluginCommandId first param is still 'IAgentPlugin' and "
        f"discovery method does not inline the prefix logic. "
        f"Either widen the type or build the prefix another way."
    )


# [pr_diff] fail_to_pass
def test_plugin_source_guard():
    """Prefix is only applied when source is Plugin, not for all prompt sources."""
    src = _read(PROMPTS_SERVICE)
    block = _extract_name_assignment_block(src)
    assert block, "computeSlashCommandDiscoveryInfo method not found"

    # The fix must guard the prefix application to plugin sources only.
    # On base commit there is no prefix application, so no guard is needed —
    # this test fails because neither condition is met.
    has_prefix = "getCanonicalPluginCommandId" in block or (
        "basename" in block and "pluginUri" in block
    )
    has_guard = bool(re.search(
        r"(PromptFileSource\.Plugin|\.source\s*===.*[Pp]lugin|isPlugin)",
        block
    ))

    assert has_prefix and has_guard, (
        "Prefix must be applied AND guarded to plugin sources only. "
        f"Has prefix: {has_prefix}, Has guard: {has_guard}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_non_plugin_sources_unaffected():
    """Non-plugin sources still use unmodified name (no false prefix application)."""
    src = _read(PROMPTS_SERVICE)

    assert "getCleanPromptName" in src, (
        "getCleanPromptName must still be used as fallback for non-plugin prompt names"
    )
    assert "slashCommandsFromDiscoveryInfo" in src, (
        "slashCommandsFromDiscoveryInfo method must still exist"
    )


# [static] pass_to_pass
def test_canonical_function_still_exported():
    """getCanonicalPluginCommandId remains exported and functional."""
    src = _read(PLUGIN_SERVICE)

    assert re.search(
        r"export\s+function\s+getCanonicalPluginCommandId", src
    ), "getCanonicalPluginCommandId must remain exported"

    # Function body must still reference basename and normalizePluginToken
    # Check in a bounded region after the function signature
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "getCanonicalPluginCommandId" in line and "export" in line:
            func_region = "\n".join(lines[i:i + 15])
            assert "basename" in func_region, (
                "getCanonicalPluginCommandId must still use basename"
            )
            assert "normalizePluginToken" in func_region, (
                "getCanonicalPluginCommandId must still use normalizePluginToken"
            )
            break


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:126
def test_no_arrow_function_for_export():
    """Exported function uses function keyword, not arrow expression."""
    src = _read(PLUGIN_SERVICE)

    assert re.search(
        r"export\s+function\s+getCanonicalPluginCommandId", src
    ), (
        "getCanonicalPluginCommandId must use 'export function' declaration, "
        "not 'export const' arrow function (per copilot-instructions.md)"
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72
def test_tab_indentation_in_modified_files():
    """Modified files use tab indentation as required by VS Code coding guidelines."""
    for rel_path in [PLUGIN_SERVICE, PROMPTS_SERVICE]:
        src = _read(rel_path)
        indented_lines = [l for l in src.splitlines() if l and l[0] in ("\t", " ")]
        tab_lines = [l for l in indented_lines if l.startswith("\t")]
        space_only = [l for l in indented_lines if l.startswith("    ") and not l.startswith("\t")]
        assert len(tab_lines) > len(space_only) * 10, (
            f"{rel_path}: must use tab indentation "
            f"({len(tab_lines)} tab lines vs {len(space_only)} space-only lines)"
        )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:94
def test_single_quotes_for_strings():
    """Non-localized strings use single quotes, not double quotes."""
    src = _read(PROMPTS_SERVICE)
    block = _extract_name_assignment_block(src)
    if not block:
        return

    non_localized_doubles = re.findall(
        r'(?<!localize\()\"[^"]+\"', block
    )
    single_quoted = re.findall(r"'[^']+'", block)

    if non_localized_doubles and single_quoted:
        assert len(single_quoted) >= len(non_localized_doubles), (
            "Non-localized strings should use single quotes per copilot-instructions.md"
        )
