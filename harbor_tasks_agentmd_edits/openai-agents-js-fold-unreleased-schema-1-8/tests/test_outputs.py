"""
Task: openai-agents-js-fold-unreleased-schema-1-8
Repo: openai/openai-agents-js @ 4e6b3fbd3355709831a1bb64472b3c947b694690
PR:   1075

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/openai-agents-js"
RUN_STATE = Path(REPO) / "packages" / "agents-core" / "src" / "runState.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """runState.ts must have balanced braces and valid string literals."""
    content = RUN_STATE.read_text()
    # Basic brace balance check for TS
    assert content.count("{") == content.count("}"), \
        "runState.ts has unbalanced curly braces"
    assert content.count("[") == content.count("]"), \
        "runState.ts has unbalanced square brackets"
    # Check that CURRENT_SCHEMA_VERSION is assigned a string literal
    assert re.search(r"export const CURRENT_SCHEMA_VERSION\s*=\s*'[^']+'\s*as\s*const", content), \
        "CURRENT_SCHEMA_VERSION must be a valid string const assignment"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_current_schema_version_is_1_8():
    """CURRENT_SCHEMA_VERSION must be '1.8', not '1.9' (unreleased version folded)."""
    content = RUN_STATE.read_text()
    m = re.search(r"export const CURRENT_SCHEMA_VERSION\s*=\s*'([^']+)'", content)
    assert m is not None, "Could not find CURRENT_SCHEMA_VERSION assignment"
    version = m.group(1)
    assert version == "1.8", \
        f"CURRENT_SCHEMA_VERSION should be '1.8' (fold unreleased changes), got '{version}'"


# [pr_diff] fail_to_pass
def test_version_1_9_not_referenced():
    """Schema version '1.9' must not appear as a version string in runState.ts."""
    content = RUN_STATE.read_text()
    # Look for '1.9' as a string literal used as a version
    version_refs = re.findall(r"'1\.9'", content)
    assert len(version_refs) == 0, \
        "Version '1.9' should not appear in runState.ts — unreleased changes should be folded into 1.8"


# [pr_diff] fail_to_pass
def test_version_1_8_comment_includes_batched_computer_actions():
    """The 1.8 version comment must describe batched computer actions (folded from 1.9)."""
    content = RUN_STATE.read_text()
    # Find the comment line for version 1.8
    m = re.search(r"\*\s*-\s*1\.8:(.+?)(?:\n\s*\*\s*-\s*\d|\n\s*\*/)", content, re.DOTALL)
    assert m is not None, "Could not find version 1.8 comment in version history"
    comment_1_8 = m.group(1).lower()
    assert "batched computer action" in comment_1_8 or "computer tool" in comment_1_8, \
        "Version 1.8 comment must mention batched computer actions (folded from former 1.9)"
    assert "tool search" in comment_1_8, \
        "Version 1.8 comment must still mention tool search item variants"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — agent config/doc update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [agent_config] pass_to_pass — AGENTS.md:29-30 @ 4e6b3fbd
