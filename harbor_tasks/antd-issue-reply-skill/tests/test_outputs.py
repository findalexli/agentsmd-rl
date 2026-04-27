"""Verify the issue-reply skill scaffold for ant-design/ant-design#57097.

This is a markdown_authoring task. Track 1 (this file) is a sanity gate
that confirms the SKILL.md was created at the expected location with the
expected structural elements. The deeper semantic comparison runs in
Track 2 via the Gemini diff judge over `config_edits` in the manifest.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/ant-design")
SKILL_DIR = REPO / ".claude/skills/issue-reply"
SKILL_PATH = SKILL_DIR / "SKILL.md"
REFS_PATH = SKILL_DIR / "references/labels-and-resources.md"
GITIGNORE = REPO / ".gitignore"


# ──────────────────────── fail_to_pass tests ────────────────────────

def test_skill_file_exists():
    assert SKILL_PATH.is_file(), (
        f"Skill file is missing: {SKILL_PATH.relative_to(REPO)}"
    )


def test_skill_has_yaml_frontmatter():
    """SKILL.md must open with a YAML frontmatter block delimited by ---."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    assert text.startswith("---\n"), (
        "SKILL.md must begin with a YAML frontmatter block (`---` on line 1)"
    )
    end = text.find("\n---\n", 4)
    assert end > 0, "frontmatter must be closed with a `---` line"
    fm = text[4:end]
    # Required keys
    assert re.search(r"^name:\s*\S", fm, re.MULTILINE), (
        "frontmatter must define a non-empty `name:` field"
    )
    assert re.search(r"^description:\s*\S", fm, re.MULTILINE), (
        "frontmatter must define a non-empty `description:` field"
    )


def test_skill_description_long_enough():
    """The description field must give Claude enough trigger context.

    SKILL.md descriptions need to enumerate when the skill applies — a
    one-line stub like `description: helps with issues` will not route
    Claude to the skill.
    """
    text = SKILL_PATH.read_text(encoding="utf-8")
    m = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z_-]+:|\n---)",
                  text, re.MULTILINE | re.DOTALL)
    assert m, "could not locate description field"
    desc = m.group(1).strip()
    assert len(desc) >= 80, (
        f"description is too short ({len(desc)} chars) — should describe "
        f"trigger conditions and scope"
    )


def test_skill_covers_required_topics():
    """The body must cover the topics enumerated in the task instruction."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    body = text.lower()

    # Each topic listed in the instruction must surface in the body.
    # We accept either Chinese or English wording for each topic so the
    # agent has flexibility on phrasing.
    required = {
        "duplicate_marker": ["duplicate of #"],
        "dosubot_handling": ["dosu"],
        "language_policy":  ["语言", "language"],
        "seven_day_rule":   ["7", "seven"],
        "bug_vs_feature":   ["feature request", "功能请求"],
    }
    missing = []
    for key, alternates in required.items():
        if not any(alt.lower() in body for alt in alternates):
            missing.append(key)
    assert not missing, (
        f"SKILL.md body is missing required topics: {missing}. "
        f"All of {list(required)} must be addressed."
    )


def test_references_doc_exists():
    """The skill must include the references file referenced from SKILL.md."""
    assert REFS_PATH.is_file(), (
        f"references file is missing: {REFS_PATH.relative_to(REPO)}"
    )
    assert REFS_PATH.stat().st_size > 200, (
        "references file looks empty — should list labels and resources"
    )


def test_references_link_from_skill():
    """SKILL.md must point at the references doc."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    assert "references/labels-and-resources.md" in text, (
        "SKILL.md should reference the labels-and-resources.md helper file"
    )


def test_gitignore_unignores_skills_dir():
    """.gitignore must allow .claude/skills/ to be tracked.

    The base .gitignore had `.claude/` (ignoring everything under it).
    The fix must replace or relax that pattern so files under
    .claude/skills/ can be committed, while keeping the rest of
    .claude/ ignored if desired.
    """
    text = GITIGNORE.read_text(encoding="utf-8")
    negation_lines = [
        line.strip() for line in text.splitlines()
        if line.strip().startswith("!") and "skills" in line and ".claude" in line
    ]
    assert len(negation_lines) >= 1, (
        f".gitignore must contain a `!` negation pattern that allows "
        f".claude/skills/ to be tracked. Found 0 such lines. "
        f"Current .gitignore contains: {text!r}"
    )


def test_skill_file_not_gitignored():
    """git check-ignore must report the SKILL.md path as NOT ignored."""
    r = subprocess.run(
        ["git", "check-ignore", "-v", "--no-index",
         ".claude/skills/issue-reply/SKILL.md"],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    # exit 0 = ignored (bad). exit 1 = not ignored (good). exit 128 = error.
    assert r.returncode == 1, (
        f"`.claude/skills/issue-reply/SKILL.md` is still gitignored "
        f"(returncode={r.returncode}, output={r.stdout!r}). "
        f"`.gitignore` must un-ignore .claude/skills/."
    )


# ──────────────────────── pass_to_pass tests ────────────────────────

def test_package_json_intact():
    """package.json must remain valid JSON with the expected name (regression
    guard: agent must not damage the build manifest)."""
    pkg_path = REPO / "package.json"
    assert pkg_path.is_file(), "package.json is missing — repo damaged"
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert pkg.get("name") == "antd", (
        f"package.json `name` is {pkg.get('name')!r}, expected 'antd'"
    )


def test_agents_md_intact():
    """AGENTS.md (root agent-instructions file) must remain present and
    non-empty (regression guard against agents that nuke the repo)."""
    r = subprocess.run(
        ["test", "-s", "AGENTS.md"],
        cwd=str(REPO), capture_output=True, timeout=10,
    )
    assert r.returncode == 0, "AGENTS.md is missing or empty"
