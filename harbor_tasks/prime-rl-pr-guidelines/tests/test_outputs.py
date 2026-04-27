"""Structural checks for the AGENTS.md PR-guidelines edit.

The PR adds a new GitHub section to AGENTS.md. Because this is a markdown
authoring task, the deterministic Track 1 signal is the presence of a small
set of distinctive substrings the gold edit introduced. The semantic-diff
judgment (Track 2) is the primary evaluation signal — these tests are a
sanity gate.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/prime-rl")
AGENTS_MD = REPO / "AGENTS.md"


def _read_agents_md() -> str:
    assert AGENTS_MD.exists(), f"AGENTS.md missing at {AGENTS_MD}"
    return AGENTS_MD.read_text()


def test_github_section_added():
    """Gold adds a new ## GitHub section to AGENTS.md."""
    text = _read_agents_md()
    # Heading must be present as a top-level (h2) header
    assert re.search(r"(?m)^## GitHub\s*$", text), (
        "Expected a new '## GitHub' section heading in AGENTS.md"
    )


def test_draft_pr_command_documented():
    """Gold documents the exact `gh pr create --draft` command for draft PRs."""
    text = _read_agents_md()
    assert "gh pr create --draft" in text, (
        "Expected the literal command 'gh pr create --draft' to appear in AGENTS.md"
    )


def test_test_plan_rule_documented():
    """Gold adds a rule about not including a 'test plan' section in PR descriptions."""
    text = _read_agents_md()
    assert "test plan" in text.lower(), (
        "Expected a rule referencing 'test plan' in AGENTS.md"
    )


def test_github_section_below_git_section():
    """Sanity: the new GitHub section appears AFTER the existing Git section."""
    text = _read_agents_md()
    git_match = re.search(r"(?m)^## Git\s*$", text)
    github_match = re.search(r"(?m)^## GitHub\s*$", text)
    assert git_match, "Existing '## Git' section must remain"
    assert github_match, "New '## GitHub' section must be added"
    assert github_match.start() > git_match.start(), (
        "GitHub section should appear after the Git section"
    )


def test_repo_still_clones_cleanly():
    """pass_to_pass: working tree is intact and AGENTS.md still parses as text."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git status failed:\n{r.stderr}"
    # AGENTS.md must still be a real file with content
    text = _read_agents_md()
    assert text.strip(), "AGENTS.md must not be empty"
    assert "## Git" in text, "Existing '## Git' section must still exist"


def test_existing_branch_prefixes_preserved():
    """The existing branch-prefix guidance (feat/, fix/, chore/) is preserved."""
    text = _read_agents_md()
    for prefix in ("feat/", "fix/", "chore/"):
        assert prefix in text, f"Expected branch prefix '{prefix}' to remain documented"
