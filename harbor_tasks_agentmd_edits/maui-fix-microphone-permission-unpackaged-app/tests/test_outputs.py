"""
Task: maui-fix-microphone-permission-unpackaged-app
Repo: dotnet/maui @ 260770c977f376c9b0190c03ed1a41920725f079
PR:   33179

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/maui"
PERM_FILE = Path(REPO) / "src/Essentials/src/Permissions/Permissions.windows.cs"
COPILOT_MD = Path(REPO) / ".github/copilot-instructions.md"
SKILL_MD = Path(REPO) / ".github/skills/pr-finalize/SKILL.md"
EXAMPLE_MD = Path(REPO) / ".github/skills/pr-finalize/references/complete-example.md"


def _read(path: Path) -> str:
    assert path.exists(), f"File not found: {path}"
    return path.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_permissions_file_valid_structure():
    """Permissions file has well-formed C# structure (balanced braces)."""
    content = _read(PERM_FILE)
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open vs {close_braces} close"
    )
    assert "class Microphone" in content, "Microphone class must exist"
    assert "CheckStatusAsync" in content, "CheckStatusAsync method must exist"
    assert "RequestAsync" in content, "RequestAsync method must exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------


def test_check_status_guards_ensure_declared():
    """CheckStatusAsync must guard EnsureDeclared() with IsPackagedApp check."""
    content = _read(PERM_FILE)

    # Find the CheckStatusAsync method body
    match = re.search(
        r"public override Task<PermissionStatus>\s+CheckStatusAsync\(\)\s*\{(.*?)\n\t\t\t\}",
        content,
        re.DOTALL,
    )
    assert match, "CheckStatusAsync method not found"
    body = match.group(1)

    # Must have the IsPackagedApp guard
    assert "AppInfoUtils.IsPackagedApp" in body, (
        "CheckStatusAsync must check AppInfoUtils.IsPackagedApp"
    )
    # EnsureDeclared must be INSIDE the if block, not before it
    # Find if-block containing EnsureDeclared
    if_blocks = re.findall(r"if\s*\([^)]*IsPackagedApp[^)]*\)\s*\{([^}]*)\}", body)
    has_guarded = any("EnsureDeclared()" in block for block in if_blocks)
    assert has_guarded, (
        "EnsureDeclared() must be inside the IsPackagedApp if-block"
    )


def test_request_async_guards_ensure_declared():
    """RequestAsync must guard EnsureDeclared() with IsPackagedApp check."""
    content = _read(PERM_FILE)

    # Find the RequestAsync method body
    match = re.search(
        r"public override async Task<PermissionStatus>\s+RequestAsync\(\)\s*\{(.*?)\n\t\t\t\}",
        content,
        re.DOTALL,
    )
    assert match, "RequestAsync method not found"
    body = match.group(1)

    # Must have the IsPackagedApp guard
    assert "AppInfoUtils.IsPackagedApp" in body, (
        "RequestAsync must check AppInfoUtils.IsPackagedApp"
    )
    # EnsureDeclared must be inside the if block
    if_blocks = re.findall(r"if\s*\([^)]*IsPackagedApp[^)]*\)\s*\{([^}]*)\}", body)
    has_guarded = any("EnsureDeclared()" in block for block in if_blocks)
    assert has_guarded, (
        "EnsureDeclared() must be inside the IsPackagedApp if-block in RequestAsync"
    )


def test_try_request_permission_extracted():
    """TryRequestPermissionAsync method must be extracted from RequestAsync."""
    content = _read(PERM_FILE)
    assert "TryRequestPermissionAsync" in content, (
        "TryRequestPermissionAsync method must exist"
    )
    # Verify it's a proper method definition (not just a comment)
    assert re.search(
        r"async\s+Task<PermissionStatus>\s+TryRequestPermissionAsync\s*\(",
        content,
    ), "TryRequestPermissionAsync must be a proper async method returning Task<PermissionStatus>"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------


def test_copilot_instructions_no_opening_prs_section():
    """copilot-instructions.md must not have the Opening PRs section with NOTE block."""
    content = _read(COPILOT_MD)

    # The "Opening PRs" section with NOTE block must be removed
    assert "### Opening PRs" not in content, (
        "The '### Opening PRs' section must be removed from copilot-instructions.md"
    )
    # Verify the NOTE block template is gone
    assert (
        "test the resulting artifacts" not in content
    ), "The NOTE block about testing PR artifacts must be removed"


def test_pr_finalize_no_note_block_requirement():
    """pr-finalize SKILL.md must not require NOTE block in PR descriptions."""
    content = _read(SKILL_MD)

    # Must not list "Start with the required NOTE block" as a requirement
    assert "Start with the required NOTE block" not in content, (
        "SKILL.md must not require starting with NOTE block"
    )
    # The NOTE block template must be removed from examples
    assert (
        "test the resulting artifacts" not in content
    ), "The NOTE block about testing PR artifacts must be removed from SKILL.md"


def test_example_no_note_block():
    """complete-example.md must not contain the NOTE block."""
    content = _read(EXAMPLE_MD)

    assert (
        "test the resulting artifacts" not in content
    ), "The NOTE block about testing PR artifacts must be removed from the example"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_microphone_class_structure_preserved():
    """Core Microphone permission class structure is preserved after changes."""
    content = _read(PERM_FILE)

    # Essential methods must still exist
    assert "class Microphone" in content, "Microphone class must be preserved"
    assert "CheckStatus()" in content, "CheckStatus method must be preserved"
    assert "MediaCaptureInitializationSettings" in content, (
        "MediaCapture initialization logic must be preserved"
    )


def test_copilot_instructions_key_sections_preserved():
    """Key sections of copilot-instructions.md are preserved after NOTE removal."""
    content = _read(COPILOT_MD)

    # These sections should NOT be removed
    assert "Custom Agents and Skills" in content, (
        "Custom Agents and Skills section must be preserved"
    )
    assert "Development Workflow" in content, (
        "Development Workflow section must be preserved"
    )
    assert "Code Review Instructions" in content, (
        "Code Review Instructions must be preserved"
    )
