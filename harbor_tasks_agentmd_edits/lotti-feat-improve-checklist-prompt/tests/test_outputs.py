"""
Task: lotti-feat-improve-checklist-prompt
Repo: matthiasn/lotti @ 4978e0e2c96dd001d509380f100486a54ca4b811
PR:   2417

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/lotti"
PROMPTS_FILE = Path(REPO) / "lib/features/ai/util/preconfigured_prompts.dart"
README_FILE = Path(REPO) / "lib/features/ai/README.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_prompt_sections():
    """Split the prompts file into system and user message regions."""
    content = PROMPTS_FILE.read_text()
    # The file defines systemMessage: and userMessage: as named params.
    # We use these markers to roughly separate sections.
    return content


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dart_file_parseable():
    """preconfigured_prompts.dart is not corrupted (balanced braces, exists)."""
    content = PROMPTS_FILE.read_text()
    # Basic sanity: file exists and has balanced curly braces (Dart)
    assert len(content) > 1000, "File appears truncated"
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open vs {close_braces} close"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_system_message_entry_scoped_directives():
    """System message must contain an ENTRY-SCOPED DIRECTIVES section with
    ignore and plan-only directive phrases."""
    content = _read_prompt_sections()
    content_lower = content.lower()
    # Must have a dedicated directive section (case-insensitive header check)
    assert "entry-scoped directives" in content_lower or (
        "entry" in content_lower and "directive" in content_lower and "scope" in content_lower
    ), "System message must have an entry-scoped directives section"
    # Ignore directive phrase — the exact user-facing phrase that models detect
    assert "Ignore for checklist" in content, (
        "System message must document the 'Ignore for checklist' directive"
    )
    # Plan-only directive phrase
    assert "Single checklist item" in content, (
        "System message must document the 'Single checklist item' directive"
    )
    # Per-entry scope semantics
    assert "each entry" in content_lower or "per entry" in content_lower, (
        "System message must explain per-entry scoping"
    )


# [pr_diff] fail_to_pass
def test_directive_isolation_rule():
    """System message must instruct the model NOT to blend directives
    across entries — each entry is independent."""
    content = _read_prompt_sections()
    content_lower = content.lower()
    # Must tell the model directives don't cross entry boundaries
    has_blend = "blend directives" in content_lower
    has_not_mix = ("not" in content_lower or "don't" in content_lower) and (
        "mix" in content_lower or "blend" in content_lower or "cross" in content_lower
    ) and "entries" in content_lower
    has_independent = "independently" in content_lower and "entry" in content_lower
    assert has_blend or has_not_mix or has_independent, (
        "System message must tell the model not to blend/mix directives across entries"
    )
    # Plan-only directive must mention collapsing to a single item
    assert (
        "at most one" in content_lower
        or "at most 1" in content_lower
        or "only one" in content_lower
        or "single" in content_lower and "item" in content_lower
    ), "Plan-only directive must specify creating at most one checklist item"


# [pr_diff] fail_to_pass
def test_user_message_directive_reminder():
    """User message must include a directive reminder section referencing
    ignore and plan-only behaviors."""
    content = _read_prompt_sections()
    assert "Directive reminder" in content or "directive reminder" in content, (
        "User message must include a 'Directive reminder' section"
    )
    # The reminder should mention both directive types
    # Find content after "Directive reminder" (or similar)
    reminder_idx = content.lower().find("directive reminder")
    assert reminder_idx != -1
    after_reminder = content[reminder_idx:reminder_idx + 600]
    assert "Ignore for checklist" in after_reminder or "ignore for checklist" in after_reminder.lower(), (
        "Directive reminder must reference the ignore directive"
    )
    assert "implementation plan" in after_reminder.lower(), (
        "Directive reminder must reference plan-only directive"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/doc update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention per-entry or entry-scoped directive concept
    assert "per-entry" in content_lower or "per entry" in content_lower or "entry-scoped" in content_lower, (
        "README must document per-entry directive scoping"
    )

    # Must document the ignore directive — check for the concept near "entry"/"directive"
    # The exact phrase "ignore for checklist" is specific to this feature addition
    assert "ignore for checklist" in content_lower or "ignore" in content_lower and "directive" in content_lower, (
        "README must document the ignore-for-checklist directive"
    )

    # Must document the plan-only / single-item directive
    assert "plan-only" in content_lower or "single checklist item" in content_lower or (
        "single" in content_lower and "item" in content_lower and "plan" in content_lower
    ), "README must document the plan-only single-item directive"

    # Must mention isolation / independence of entries
    assert "independent" in content_lower or "isolation" in content_lower, (
        "README must explain that entries are processed independently"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / preservation
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [agent_config] pass_to_pass — AGENTS.md "Maintain feature READMEs"
def test_readme_checklist_section_preserved():
    """The existing 'Adding Checklist Items' section in the AI README
    must not be removed when adding new content."""
    content = README_FILE.read_text()
    assert "Adding Checklist Items" in content or "Checklist" in content, (
        "README must preserve the existing checklist section"
    )
    assert "Batch Processing" in content, (
        "README must preserve existing Batch Processing bullet"
    )
    assert "Error Recovery" in content, (
        "README must preserve existing Error Recovery bullet"
    )
