"""
Task: remix-refactor-update-interaction-setup-functions
Repo: remix-run/remix @ 0b0ca631198af88cda1ecceef5a51d20e1b3b3e2
PR:   10952

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"
INTERACTION_PKG = f"{REPO}/packages/interaction"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces and are non-empty."""
    files = [
        f"{INTERACTION_PKG}/src/lib/interaction.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/form.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/keys.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/popover.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/press.ts",
    ]
    for f in files:
        p = Path(f)
        assert p.exists(), f"{f} does not exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} appears empty or truncated"
        assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"


# [static] pass_to_pass
def test_interaction_setup_type_exported():
    """InteractionSetup type must still be exported from interaction.ts."""
    content = Path(f"{INTERACTION_PKG}/src/lib/interaction.ts").read_text()
    assert re.search(r"export\s+type\s+InteractionSetup", content), \
        "InteractionSetup type is not exported"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interaction_setup_type_uses_parameter():
    """InteractionSetup type must use parameter style, not 'this' context."""
    content = Path(f"{INTERACTION_PKG}/src/lib/interaction.ts").read_text()
    # Find the InteractionSetup type definition line
    match = re.search(r"export\s+type\s+InteractionSetup\s*=\s*(.+)", content)
    assert match, "InteractionSetup type definition not found"
    type_def = match.group(1)
    # Must NOT use 'this: Interaction' pattern
    assert "this:" not in type_def and "this :" not in type_def, \
        f"InteractionSetup still uses 'this' context: {type_def}"
    # Must have Interaction as a regular parameter
    assert "Interaction" in type_def, \
        f"InteractionSetup must reference Interaction type: {type_def}"


# [pr_diff] fail_to_pass
def test_runtime_call_uses_direct_invocation():
    """Setup functions must be called directly, not via .call()."""
    content = Path(f"{INTERACTION_PKG}/src/lib/interaction.ts").read_text()
    # The old code used: interaction.call(interactionContext)
    # The new code uses: interaction(interactionContext)
    assert "interaction.call(" not in content, \
        "Still using interaction.call() — should use direct invocation interaction()"
    # Verify direct call pattern exists
    assert re.search(r"interaction\(interactionContext\)", content), \
        "Direct invocation interaction(interactionContext) not found"


# [pr_diff] fail_to_pass
def test_builtin_setup_functions_use_handle():
    """All built-in interaction setup functions must use parameter, not 'this' context."""
    setup_files = [
        f"{INTERACTION_PKG}/src/lib/interactions/form.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/keys.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/popover.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/press.ts",
    ]
    for filepath in setup_files:
        content = Path(filepath).read_text()
        fname = Path(filepath).name
        # Must not use 'this: Interaction' in function signatures
        assert "this: Interaction" not in content, \
            f"{fname} still uses 'this: Interaction' — must use a regular parameter"
        # Must not use 'this.target' or 'this.on(' to access the interaction handle
        assert "this.target" not in content, \
            f"{fname} still uses 'this.target' — must use parameter-based access"
        assert "this.on(" not in content, \
            f"{fname} still uses 'this.on()' — must use parameter-based access"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # The Custom Interactions section must exist
    assert "Custom Interactions" in content, "README missing Custom Interactions section"

    # Extract the Custom Interactions section (up to next ## heading or end)
    ci_match = re.search(
        r"## Custom Interactions(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    assert ci_match, "Could not extract Custom Interactions section"
    ci_section = ci_match.group(1)

    # Extract code blocks from the section
    code_blocks = re.findall(r"```[\w]*\n(.*?)```", ci_section, re.DOTALL)
    assert len(code_blocks) > 0, "No code examples in Custom Interactions section"

    # No code block should show the old 'this: Interaction' pattern
    for block in code_blocks:
        assert "this: Interaction" not in block, \
            "README code example still uses 'this: Interaction' — must use parameter"
        assert "this.target" not in block, \
            "README code example still uses 'this.target' — must use parameter access"
        assert "this.on(" not in block, \
            "README code example still uses 'this.on()' — must use parameter access"

    # At least one code block must show a parameter-based Interaction pattern
    # (the parameter receives the Interaction handle, regardless of name)
    has_param_pattern = any(
        # Match patterns like (handle: Interaction) or (ctx: Interaction)
        re.search(r"\(\w+:\s*Interaction\)", block)
        for block in code_blocks
    )
    assert has_param_pattern, \
        "README Custom Interactions code examples must show parameter-based Interaction pattern"


# [config_edit] fail_to_pass

    # Find non-README markdown files
    changeset_files = [
        f for f in changes_dir.glob("*.md") if f.name.lower() != "readme.md"
    ]

    # At least one changeset must describe the handle/parameter change
    found = False
    for cf in changeset_files:
        content = cf.read_text()
        content_lower = content.lower()
        # Check that it mentions both the concept of handle/parameter AND interaction
        if ("handle" in content_lower or "parameter" in content_lower) and \
           "interaction" in content_lower:
            found = True
            # Per AGENTS.md: v0.x breaking changes should start with "BREAKING CHANGE:"
            assert content.strip().startswith("BREAKING CHANGE"), \
                f"Changeset {cf.name} should start with 'BREAKING CHANGE:' " \
                f"per AGENTS.md convention for v0.x breaking changes"
            break

    assert found, \
        "No changeset file found documenting the handle parameter change for interaction"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md rule compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:17 @ 0b0ca631
