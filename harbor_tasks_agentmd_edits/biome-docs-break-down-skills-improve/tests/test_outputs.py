"""
Task: biome-docs-break-down-skills-improve
Repo: biomejs/biome @ eb57e3a1df36bf1bbe612f84a68ded658d9b7d00
PR:   9613

Break down and improve agent skills: extract changeset and pull-request
into dedicated skills, add Code Comments guidance to biome-developer,
add non-interactive changeset command to justfile.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/biome"

CHANGESET_FM_CHECK = r"""
import re
text = open("/workspace/biome/.claude/skills/changeset/SKILL.md").read()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m, "No YAML frontmatter found in changeset/SKILL.md"
fm = {}
for line in m.group(1).split("\n"):
    if ":" in line:
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
assert fm.get("name") == "changeset", "Expected name=changeset, got " + str(fm.get("name"))
assert "description" in fm, "Missing 'description' in frontmatter"
assert "compatibility" in fm, "Missing 'compatibility' in frontmatter"
body = text[m.end():]
assert "## Purpose" in body, "Missing ## Purpose section"
assert "just new-changeset-empty" in body, "Must reference 'just new-changeset-empty'"
print("PASS")
"""

PR_FM_CHECK = r"""
import re
text = open("/workspace/biome/.claude/skills/pull-request/SKILL.md").read()
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m, "No YAML frontmatter found in pull-request/SKILL.md"
fm = {}
for line in m.group(1).split("\n"):
    if ":" in line:
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
assert fm.get("name") == "pull-request", "Expected name=pull-request, got " + str(fm.get("name"))
assert "description" in fm, "Missing 'description' in frontmatter"
assert "compatibility" in fm, "Missing 'compatibility' in frontmatter"
body = text[m.end():]
assert "## AI Assistance Disclosure" in body, "Missing AI disclosure section"
assert "## Choose the Target Branch" in body, "Missing target branch section"
assert "## PR Title" in body, "Missing PR title section"
assert "## Pre-PR Checklist" in body, "Missing pre-PR checklist section"
print("PASS")
"""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_justfile_syntax():
    """justfile must be parseable (no syntax errors introduced)."""
    content = Path(f"{REPO}/justfile").read_text()
    assert "new-changeset:" in content, "justfile missing existing new-changeset recipe"
    assert "ready:" in content, "justfile missing existing ready recipe"


def test_existing_skills_intact():
    """Other existing skill files should still be present."""
    for skill_dir in ["biome-developer", "testing-codegen", "lint-rule-development",
                      "formatter-development", "parser-development"]:
        skill_path = Path(f"{REPO}/.claude/skills/{skill_dir}/SKILL.md")
        assert skill_path.exists(), f"Existing skill {skill_dir}/SKILL.md should still exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------


def test_justfile_new_changeset_empty_recipe():
    """justfile must define new-changeset-empty recipe invoking pnpm changeset --empty."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re
text = open("/workspace/biome/justfile").read()
pattern = r'^new-changeset-empty:\s*\n((?:\s+.*\n)*)'
m = re.search(pattern, text, re.MULTILINE)
assert m, "new-changeset-empty recipe not found in justfile"
body = m.group(1)
assert "pnpm" in body, "Recipe should invoke pnpm, got: " + repr(body)
assert "changeset" in body, "Recipe should mention changeset, got: " + repr(body)
assert "--empty" in body, "Recipe should pass --empty flag, got: " + repr(body)
print("PASS")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Recipe validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_changeset_skill_valid_frontmatter():
    """changeset/SKILL.md must exist with valid YAML frontmatter (name, description, compatibility)."""
    skill_path = Path(f"{REPO}/.claude/skills/changeset/SKILL.md")
    assert skill_path.exists(), "changeset/SKILL.md must exist"
    r = subprocess.run(
        ["python3", "-c", CHANGESET_FM_CHECK],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Changeset frontmatter validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pull_request_skill_valid_frontmatter():
    """pull-request/SKILL.md must exist with valid YAML frontmatter (name, description, compatibility)."""
    skill_path = Path(f"{REPO}/.claude/skills/pull-request/SKILL.md")
    assert skill_path.exists(), "pull-request/SKILL.md must exist"
    r = subprocess.run(
        ["python3", "-c", PR_FM_CHECK],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Pull-request frontmatter validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_changeset_skill_has_writing_guidelines():
    """changeset/SKILL.md must include writing guidelines for changeset descriptions."""
    r = subprocess.run(
        ["python3", "-c", r"""
text = open("/workspace/biome/.claude/skills/changeset/SKILL.md").read()
assert "## Writing Guidelines" in text, "Missing Writing Guidelines section"
assert "patch" in text, "Must mention patch change type"
assert "minor" in text, "Must mention minor change type"
assert "major" in text, "Must mention major change type"
assert "## Changeset Format" in text, "Missing Changeset Format section"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Changeset guidelines check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_biome_developer_code_comments_section():
    """biome-developer/SKILL.md must have a Code Comments section with DO/DON'T guidance."""
    r = subprocess.run(
        ["python3", "-c", r"""
text = open("/workspace/biome/.claude/skills/biome-developer/SKILL.md").read()
assert "### Code Comments" in text, "Missing '### Code Comments' heading"
assert "**DO:**" in text, "Missing **DO:** guidance"
assert "**DON'T:**" in text, "Missing **DON'T:** guidance"
lower = text.lower()
assert "next developer" in lower or "future reader" in lower, \
    "Should mention the future-reader principle"
assert "WRONG" in text and "CORRECT" in text, "Should have WRONG/CORRECT code examples"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Code comments section check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_testing_codegen_changeset_section_removed():
    """testing-codegen/SKILL.md must NOT have a 'Create Changeset' subsection and must reference new skill."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re
text = open("/workspace/biome/.claude/skills/testing-codegen/SKILL.md").read()
assert "### Create Changeset" not in text, \
    "testing-codegen should NOT have '### Create Changeset' section (extracted to changeset skill)"
assert "changeset/SKILL.md" in text, \
    "testing-codegen should reference changeset/SKILL.md"
m = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
assert m, "No frontmatter found"
for line in m.group(1).split("\n"):
    if "description:" in line:
        desc = line.split("description:", 1)[1].strip()
        assert "changeset" not in desc.lower(), \
            "Frontmatter description should not mention changesets, got: " + desc
print("PASS")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Testing-codegen changeset removal check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_lists_new_skills():
    """Skills README.md must list changeset and pull-request skills and update testing-codegen description."""
    r = subprocess.run(
        ["python3", "-c", r"""
text = open("/workspace/biome/.claude/skills/README.md").read()
assert "changeset" in text, "README should list the changeset skill"
assert "pull-request" in text, "README should list the pull-request skill"
for line in text.split("\n"):
    if "testing-codegen" in line:
        assert "create changesets" not in line.lower(), \
            "testing-codegen table entry should not mention 'create changesets'"
assert "changeset/" in text, "README directory tree should list changeset/"
assert "pull-request/" in text, "README directory tree should list pull-request/"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"README skills listing check failed: {r.stderr}"
    assert "PASS" in r.stdout
