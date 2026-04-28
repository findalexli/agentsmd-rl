"""Behavioral tests for the antd commit-msg skill scaffolding task."""

import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL = REPO / ".claude/skills/commit-msg/SKILL.md"
REF = REPO / ".claude/skills/commit-msg/references/format-and-examples.md"


def _read(path: Path) -> str:
    assert path.exists(), f"required file is missing: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass tests — they fail at the base commit (files do not exist) and
# pass once the agent has authored the skill correctly.
# ---------------------------------------------------------------------------


def test_skill_file_exists():
    """SKILL.md is created at the canonical path used by Claude Code skills."""
    assert SKILL.is_file(), f"{SKILL} not found"


def test_reference_file_exists():
    """The reference doc lives next to SKILL.md under references/."""
    assert REF.is_file(), f"{REF} not found"


def test_skill_frontmatter_name():
    """Frontmatter `name` field identifies the skill as antd-commit-msg."""
    text = _read(SKILL)
    m = re.search(r"^---\s*\n(.*?)\n---", text, flags=re.DOTALL | re.MULTILINE)
    assert m, "SKILL.md must start with a YAML frontmatter block delimited by ---"
    front = m.group(1)
    assert re.search(r"^name:\s*antd-commit-msg\s*$", front, flags=re.MULTILINE), (
        "frontmatter must set `name: antd-commit-msg`"
    )


def test_skill_frontmatter_has_description():
    """Frontmatter description must mention the skill's purpose and triggers."""
    text = _read(SKILL)
    m = re.search(r"^---\s*\n(.*?)\n---", text, flags=re.DOTALL | re.MULTILINE)
    assert m, "SKILL.md must have YAML frontmatter"
    front = m.group(1)
    desc_match = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z_]+:|\Z)", front, flags=re.DOTALL | re.MULTILINE)
    assert desc_match, "frontmatter must include a `description:` field"
    desc = desc_match.group(1).strip()
    assert len(desc) >= 60, "description must be substantial enough to drive Claude's auto-trigger heuristics"
    lower = desc.lower()
    assert "commit" in lower, "description must mention commit context"
    # The three trigger phrases listed in the task instructions.
    assert "msg" in lower, 'description must reference the trigger word "msg"'
    assert "commit msg" in lower, 'description must reference the trigger phrase "commit msg"'
    assert "写提交信息" in desc, 'description must reference the Chinese trigger phrase "写提交信息"'


def test_skill_lists_required_git_commands():
    """The skill must instruct the agent to read staged changes and recent commits."""
    text = _read(SKILL)
    # All four commands listed in the instruction must appear in SKILL.md.
    for cmd in ["git status --short", "git diff --cached --stat", "git diff --cached", "git log --oneline -10"]:
        assert cmd in text, f"SKILL.md must mention `{cmd}`"


def test_skill_emits_single_line_rule():
    """The skill must require a single-line output and a 72-character soft limit."""
    text = _read(SKILL)
    # The 72 char limit appears verbatim in the gold spec.
    assert "72" in text, "SKILL.md must state a 72-character limit on commit subjects"
    # The skill must prohibit multi-line output / explanations.
    assert "一行" in text or "single" in text.lower() or "one line" in text.lower(), (
        "SKILL.md must require single-line output"
    )


def test_skill_lists_conventional_types():
    """The skill must enumerate the antd commit types (feat/fix/docs/...)."""
    text = _read(SKILL)
    for t in ["feat", "fix", "docs", "refactor", "test", "chore", "ci", "site"]:
        # Check inline-code style or plain occurrence.
        assert re.search(rf"\b{t}\b", text), f"SKILL.md must mention commit type `{t}`"


def test_skill_references_examples_doc():
    """SKILL.md must point readers at references/format-and-examples.md."""
    text = _read(SKILL)
    assert "references/format-and-examples.md" in text, (
        "SKILL.md must link to references/format-and-examples.md"
    )


def test_reference_examples_present():
    """The reference doc must contain commit-message examples in the requested formats."""
    text = _read(REF)
    # At least one example each of `type(scope): subject` and `scope: subject`.
    assert re.search(r"`(fix|feat|docs|chore|refactor|test|ci|site)\([A-Za-z]+\):\s.+`", text), (
        "references/format-and-examples.md must contain at least one `type(scope): subject` example"
    )
    assert re.search(r"`(site|docs|chore):\s.+`", text), (
        "references/format-and-examples.md must contain at least one `scope: subject` example"
    )


def test_reference_lists_types_table():
    """The reference doc must enumerate the antd type vocabulary."""
    text = _read(REF)
    for t in ["feat", "fix", "docs", "refactor", "chore", "site"]:
        assert re.search(rf"\b{t}\b", text), f"references/format-and-examples.md must list type `{t}`"


# ---------------------------------------------------------------------------
# pass_to_pass tests — these must hold both before and after the change. They
# verify the rest of the repository still parses as expected.
# ---------------------------------------------------------------------------


def test_repo_clone_present():
    """The base ant-design checkout exists and is a valid git repository."""
    assert (REPO / ".git").is_dir(), "ant-design clone is missing"
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    head = r.stdout.strip()
    assert len(head) == 40, f"unexpected HEAD format: {head!r}"


def test_existing_issue_reply_skill_intact():
    """The pre-existing issue-reply skill must still be present unchanged."""
    other = REPO / ".claude/skills/issue-reply/SKILL.md"
    assert other.is_file(), "pre-existing .claude/skills/issue-reply/SKILL.md disappeared"
    text = other.read_text(encoding="utf-8")
    assert "antd-issue-reply" in text, "issue-reply SKILL.md frontmatter name was modified"


def test_agents_md_intact():
    """AGENTS.md must remain in place at the repo root."""
    agents = REPO / "AGENTS.md"
    assert agents.is_file(), "AGENTS.md was removed"
    head = agents.read_text(encoding="utf-8").splitlines()[:1]
    assert head and head[0].strip().startswith("# AGENTS.md"), "AGENTS.md header changed"


# === CI regression guards ===
# The PR only touches .claude/skills/commit-msg/ so there are no code-level
# test suites to run.  These pass_to_pass tests verify that files the task
# must NOT touch are still present and intact.


def test_copilot_instructions_intact():
    """pass_to_pass | .github/copilot-instructions.md remains untouched."""
    ci = REPO / ".github/copilot-instructions.md"
    assert ci.is_file(), ".github/copilot-instructions.md was removed"
    text = ci.read_text(encoding="utf-8")
    assert "Ant Design Repository Copilot Instructions" in text, (
        "copilot-instructions.md content was modified"
    )


def test_issue_reply_labels_intact():
    """pass_to_pass | issue-reply references doc remains untouched."""
    labels = REPO / ".claude/skills/issue-reply/references/labels-and-resources.md"
    assert labels.is_file(), "labels-and-resources.md was removed"
    text = labels.read_text(encoding="utf-8")
    assert "标签" in text, "labels-and-resources.md content was modified"


def test_git_remote_configured():
    """pass_to_pass | git remote origin points at ant-design (analogous to CI trust check)."""
    r = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git remote get-url failed: {r.stderr}"
    assert "ant-design" in r.stdout, (
        f"git remote origin is misconfigured: {r.stdout.strip()}"
    )
