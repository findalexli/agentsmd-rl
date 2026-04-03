"""
Task: maui-tryfix-skill-apply-multimodel-review
Repo: dotnet/maui @ f6bafa6e590e1d1dba4b2df2e4dc20a6bad67b7a
PR:   33762

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"
SKILL_MD = Path(REPO) / ".github/skills/try-fix/SKILL.md"
PS1_SCRIPT = Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-try-fix-comment.ps1"
OUTPUT_STRUCTURE_MD = Path(REPO) / ".github/skills/try-fix/references/output-structure.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass

    # Extract the DryRun/preview code path (the block after "if ($DryRun)")
    # On base, this path simply replaces the entire TRY-FIX section.
    # A correct fix must extract existing content and handle attempt deduplication.
    dryrun_idx = content.find("if ($DryRun)")
    assert dryrun_idx != -1, "Script must have a DryRun code path"
    dryrun_section = content[dryrun_idx:]

    # The preview path must use regex capture to extract existing TRY-FIX content.
    # On base, $Matches is NOT used in the DryRun section (only in the GitHub comment path).
    assert "$Matches" in dryrun_section, \
        "DryRun path must use regex capture ($Matches) to extract existing TRY-FIX content"

    # The preview path must reference AttemptNumber for attempt-aware deduplication.
    # On base, AttemptNumber is not referenced in the DryRun section.
    assert "AttemptNumber" in dryrun_section, \
        "DryRun path must reference AttemptNumber for attempt-aware updates"


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass

    # The separate reference file should be deleted
    assert not OUTPUT_STRUCTURE_MD.exists(), \
        "references/output-structure.md must be deleted (content moved to SKILL.md)"

    # SKILL.md must NOT reference the deleted file
    assert "references/output-structure.md" not in content, \
        "SKILL.md must not reference the deleted output-structure.md"

    # SKILL.md must now contain the output structure info inline
    # Check for key content that was in the deleted file: required files table
    assert "baseline.log" in content, \
        "SKILL.md must document baseline.log as a required output file"
    assert "approach.md" in content, \
        "SKILL.md must document approach.md as a required output file"
    assert "result.txt" in content, \
        "SKILL.md must document result.txt as a required output file"


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass
def test_ps1_github_comment_path_intact():
    """PS1 script must still handle the GitHub comment update path (non-preview)."""
    content = PS1_SCRIPT.read_text()
    assert "gh api --method PATCH" in content or "gh api --method POST" in content, \
        "Script must still have the GitHub API comment posting path"
    assert "existingComment" in content, \
        "Script must still handle existing comment updates"
