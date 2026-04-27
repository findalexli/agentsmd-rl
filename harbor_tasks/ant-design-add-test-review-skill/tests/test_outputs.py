"""Structural checks for the new antd-test-review skill file."""
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/ant-design"
SKILL_PATH = os.path.join(REPO, ".agents/skills/test-review/SKILL.md")


def _read_skill() -> str:
    return Path(SKILL_PATH).read_text(encoding="utf-8")


def test_skill_file_exists():
    """The new skill file must exist at the canonical path used by sibling skills."""
    r = subprocess.run(
        ["test", "-f", SKILL_PATH], capture_output=True
    )
    assert r.returncode == 0, f"Expected file at {SKILL_PATH}"


def test_skill_frontmatter_name():
    """Frontmatter must declare name: antd-test-review (matches PR scope)."""
    text = _read_skill()
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL | re.MULTILINE)
    assert m, "SKILL.md must start with a YAML frontmatter block"
    fm = m.group(1)
    assert re.search(r"^name:\s*antd-test-review\s*$", fm, re.MULTILINE), (
        "frontmatter must contain `name: antd-test-review`"
    )


def test_skill_frontmatter_description_field():
    """Frontmatter must contain a `description:` field (skill discovery key)."""
    text = _read_skill()
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL | re.MULTILINE)
    assert m, "SKILL.md must start with a YAML frontmatter block"
    fm = m.group(1)
    desc = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    assert desc, "frontmatter must contain a `description:` field"
    desc_text = desc.group(1).strip()
    assert len(desc_text) >= 20, (
        "description must be substantive (>=20 chars); "
        f"got {len(desc_text)} chars: {desc_text!r}"
    )


def test_skill_description_mentions_review_intent():
    """The description must signal a review/audit intent — not a generic skill."""
    text = _read_skill()
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL | re.MULTILINE)
    assert m, "SKILL.md must start with a YAML frontmatter block"
    fm = m.group(1)
    desc = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
    assert desc, "frontmatter must contain a `description:` field"
    desc_text = desc.group(1)
    # Description must cue the trigger — auditing/reviewing test cases.
    assert "审查" in desc_text or "review" in desc_text.lower(), (
        "description should signal review/audit intent (e.g. via 审查 / review)"
    )
    # And it should mention test cases / 测试 — this is a test-review skill.
    assert "测试" in desc_text, (
        "description should reference 测试 (the test cases being reviewed)"
    )


def test_skill_anti_pattern_keyword_present():
    """Body must articulate the central anti-pattern this skill detects:
    'using A to prove A' (用 A 证明 A) — the PR's stated motivation."""
    text = _read_skill()
    # Allow either uppercase or lowercase variant since the gold uses both.
    has_anti_pattern = ("用 A 证明 A" in text) or ("用 a 证明 a" in text)
    assert has_anti_pattern, (
        "skill body must reference the '用 A 证明 A' anti-pattern (the PR's motivation)"
    )


def test_skill_default_no_run_tests():
    """Body must encode the rule: do not run tests by default (静态审查 default)."""
    text = _read_skill()
    # The skill must say it defaults to static review, not running tests.
    has_static_default = ("静态审查" in text) and ("不默认运行" in text or "不主动" in text or "不运行" in text)
    assert has_static_default, (
        "skill must specify it defaults to static review and does not run tests by default"
    )


def test_skill_three_verdict_categories():
    """The skill prescribes a 3-way classification: keep / rewrite / drop.
    All three verdict labels must appear so reviewers have a fixed vocabulary."""
    text = _read_skill()
    assert "此用例可保留" in text, "must define the '可保留' (keep) verdict"
    assert "此用例需要改写" in text, "must define the '需要改写' (rewrite) verdict"
    assert "此用例无实际作用" in text, "must define the '无实际作用' (drop) verdict"


def test_skill_minimum_body_length():
    """The skill body (after frontmatter) must be substantive — not a stub."""
    text = _read_skill()
    parts = re.split(r"^---\s*$", text, maxsplit=2, flags=re.MULTILINE)
    assert len(parts) >= 3, "must have a frontmatter delimited by --- lines"
    body = parts[2]
    # Strip whitespace for a meaningful length check.
    body_stripped = body.strip()
    assert len(body_stripped) >= 1500, (
        f"skill body must be substantive (>=1500 chars); got {len(body_stripped)}"
    )


def test_existing_sibling_skills_unchanged():
    """Pass-to-pass: the PR adds a new skill, it must not break existing skills.
    Each existing SKILL.md must still be present at the base commit's path."""
    existing = [
        ".agents/skills/changelog-collect/SKILL.md",
        ".agents/skills/commit-msg/SKILL.md",
        ".agents/skills/create-pr/SKILL.md",
        ".agents/skills/issue-reply/SKILL.md",
        ".agents/skills/version-release/SKILL.md",
    ]
    for rel in existing:
        p = os.path.join(REPO, rel)
        r = subprocess.run(["test", "-f", p], capture_output=True)
        assert r.returncode == 0, f"existing skill missing: {rel}"


def test_repo_root_configs_intact():
    """Pass-to-pass: root-level agent configs (CLAUDE.md, AGENTS.md) must remain."""
    r = subprocess.run(
        ["git", "-C", REPO, "ls-files", "CLAUDE.md", "AGENTS.md"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"
    assert "CLAUDE.md" in r.stdout, "CLAUDE.md must be tracked"
    assert "AGENTS.md" in r.stdout, "AGENTS.md must be tracked"
