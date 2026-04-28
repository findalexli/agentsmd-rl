"""Behavioral tests for ant-design changelog-collect SKILL.md frontmatter."""
import re
import subprocess
from pathlib import Path

import yaml

REPO = Path("/workspace/ant-design")
SKILL_PATH = REPO / ".agents/skills/changelog-collect/SKILL.md"


def _split_frontmatter(text: str):
    """Return (frontmatter_dict, body) or (None, text) if no frontmatter."""
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text
    rest = text[4:] if text.startswith("---\n") else text[5:]
    m = re.search(r"^---\s*$", rest, flags=re.MULTILINE)
    if not m:
        return None, text
    fm_block = rest[: m.start()]
    body = rest[m.end():]
    if body.startswith("\n"):
        body = body[1:]
    try:
        data = yaml.safe_load(fm_block)
    except yaml.YAMLError:
        return None, text
    if not isinstance(data, dict):
        return None, text
    return data, body


def _read_skill():
    assert SKILL_PATH.is_file(), f"SKILL.md not found at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


def test_repo_present():
    """Repo clone is intact (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git failed: {r.stderr}"
    assert len(r.stdout.strip()) == 40


def test_skill_file_exists():
    """The SKILL.md file is still in place (pass_to_pass)."""
    assert SKILL_PATH.is_file()
    assert SKILL_PATH.stat().st_size > 0


def test_skill_md_has_yaml_frontmatter():
    """SKILL.md must start with a YAML frontmatter block (fail_to_pass)."""
    text = _read_skill()
    assert text.startswith("---\n") or text.startswith("---\r\n"), (
        "SKILL.md must begin with a YAML frontmatter delimiter '---' on the first line"
    )
    fm, _body = _split_frontmatter(text)
    assert fm is not None, "Frontmatter block is malformed or missing closing '---' delimiter"
    assert isinstance(fm, dict), "Frontmatter must parse to a YAML mapping"


def test_frontmatter_name_field_correct():
    """The frontmatter's `name` field must equal 'changelog-collect' (fail_to_pass)."""
    fm, _ = _split_frontmatter(_read_skill())
    assert fm is not None, "No frontmatter found"
    assert "name" in fm, "Frontmatter missing required `name` field"
    assert fm["name"] == "changelog-collect", (
        f"`name` field must be 'changelog-collect' (matching the skill's directory name "
        f"'.agents/skills/changelog-collect/'), got: {fm['name']!r}"
    )


def test_frontmatter_description_present_and_substantive():
    """The frontmatter's `description` field must exist and be substantive (fail_to_pass)."""
    fm, _ = _split_frontmatter(_read_skill())
    assert fm is not None, "No frontmatter found"
    assert "description" in fm, "Frontmatter missing required `description` field"
    desc = fm["description"]
    assert isinstance(desc, str), f"description must be a string, got {type(desc).__name__}"
    assert len(desc.strip()) >= 30, (
        f"description is too short ({len(desc.strip())} chars). It must convey "
        f"the skill's purpose so the loader can decide when to invoke this skill."
    )


def test_skill_body_preserved():
    """The original skill body content is preserved unchanged (pass_to_pass)."""
    text = _read_skill()
    fm, body = _split_frontmatter(text)
    if fm is None:
        body = text
    assert "# Changelog 收集工具" in body, (
        "Original SKILL.md heading '# Changelog 收集工具' must be preserved"
    )
    # The original SKILL.md body is ~7KB; preservation means the substantive
    # workflow content is still there, not just a stub.
    assert len(body) > 5000, (
        f"Body content shrank from ~7KB to {len(body)} chars — workflow "
        f"content must be preserved verbatim"
    )


def test_sibling_skills_unchanged():
    """Sibling SKILL.md files must remain valid and unchanged (pass_to_pass)."""
    siblings = ["commit-msg", "create-pr", "issue-reply", "version-release"]
    for name in siblings:
        path = REPO / ".agents/skills" / name / "SKILL.md"
        assert path.is_file(), f"sibling skill missing: {path}"
        text = path.read_text(encoding="utf-8")
        fm, _ = _split_frontmatter(text)
        assert fm is not None, f"{name}: sibling lost its frontmatter"
        assert "name" in fm and "description" in fm, (
            f"{name}: sibling frontmatter must still have name+description"
        )


def test_git_diff_only_touches_target_skill():
    """Only the changelog-collect SKILL.md should be modified (pass_to_pass)."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    changed = [line for line in r.stdout.splitlines() if line.strip()]
    unexpected = [
        f for f in changed
        if f != ".agents/skills/changelog-collect/SKILL.md"
    ]
    assert not unexpected, f"Unexpected files modified: {unexpected}"

# === CI-mined tests (taskforge.ci_check_miner) ===
# Dropped: test_ci_build_project_run_script (requires yarn, node, network)
# Dropped: test_ci_test_image_generate_image_snapshots (requires puppeteer, Chromium)