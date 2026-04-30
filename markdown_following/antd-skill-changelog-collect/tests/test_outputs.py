"""Behavioural / structural tests for the changelog-collect skill task.

Track 1 sanity gate: confirm the agent created a non-trivial SKILL.md at the
expected path and updated AGENTS.md with the required clarifications. The
real semantic evaluation is Track 2 (Gemini judge over config_edits).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL_PATH = REPO / ".claude/skills/changelog-collect/SKILL.md"
AGENTS_PATH = REPO / "AGENTS.md"


def _read(p: Path) -> str:
    assert p.exists(), f"required file missing: {p}"
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass — must FAIL on base commit, PASS after the gold patch
# ---------------------------------------------------------------------------

def test_skill_file_created_at_expected_path():
    """A SKILL.md exists at .claude/skills/changelog-collect/."""
    assert SKILL_PATH.exists(), (
        f"Skill file not created at {SKILL_PATH.relative_to(REPO)}. "
        "The skill must live under .claude/skills/changelog-collect/SKILL.md."
    )


def test_skill_file_is_substantial():
    """Skill file documents a real workflow, not a stub."""
    text = _read(SKILL_PATH)
    assert len(text) >= 800, (
        f"SKILL.md is too short ({len(text)} chars); expected a documented "
        "multi-phase workflow."
    )
    # Must have a top-level heading.
    assert text.lstrip().startswith("#"), "SKILL.md must begin with a Markdown heading."


def test_skill_documents_gh_pr_view_collection():
    """Skill must document collecting PR info via the GitHub CLI."""
    text = _read(SKILL_PATH)
    assert "gh pr view" in text, (
        "SKILL.md must document using `gh pr view` to fetch PR details."
    )


def test_skill_documents_git_log_between_versions():
    """Skill must document iterating commits between two refs via git log."""
    text = _read(SKILL_PATH)
    assert "git log" in text, (
        "SKILL.md must document using `git log` to enumerate commits between "
        "the two versions/branches being compared."
    )


def test_skill_writes_to_both_changelog_files():
    """Skill must reference both the Chinese and English changelog files."""
    text = _read(SKILL_PATH)
    assert "CHANGELOG.zh-CN.md" in text, (
        "SKILL.md must reference CHANGELOG.zh-CN.md as a write target."
    )
    assert "CHANGELOG.en-US.md" in text, (
        "SKILL.md must reference CHANGELOG.en-US.md as a write target."
    )


def test_agents_md_clarifies_backticked_attribute_examples():
    """AGENTS.md backtick rule is clarified with `picture-card`/`defaultValue` examples."""
    text = _read(AGENTS_PATH)
    assert "picture-card" in text, (
        "AGENTS.md must include `picture-card` as an example of an attribute "
        "name that should remain backticked."
    )
    assert "defaultValue" in text, (
        "AGENTS.md must include `defaultValue` as an example of an attribute "
        "name that should remain backticked."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — repo-state regression checks
# ---------------------------------------------------------------------------

def test_existing_skills_preserved():
    """Pre-existing skill files must not be removed by the agent."""
    for name in ("commit-msg", "create-pr", "issue-reply"):
        p = REPO / ".claude/skills" / name / "SKILL.md"
        assert p.exists(), f"Pre-existing skill file removed: {p.relative_to(REPO)}"


def test_agents_md_still_well_formed():
    """AGENTS.md still has its top-level header and changelog section anchor."""
    text = _read(AGENTS_PATH)
    assert text.startswith("# AGENTS.md"), "AGENTS.md top-level header was modified"
    assert "Changelog 规范" in text, "AGENTS.md `Changelog 规范` section is missing"
    assert "组件名要求" in text, "AGENTS.md `组件名要求` rule heading is missing"


def test_repo_git_clean_state():
    """Sanity: ant-design repo is intact (HEAD reachable, .git present)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse HEAD failed: {r.stderr}"
    assert len(r.stdout.strip()) == 40, f"unexpected HEAD output: {r.stdout!r}"
