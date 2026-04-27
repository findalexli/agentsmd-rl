"""Behavioural tests for the suggesting-data-imports SKILL.md authoring task.

The PR adds a new agent-instruction file at
``products/data_warehouse/skills/suggesting-data-imports/SKILL.md``.
We grade the agent on whether the file:

* exists at the conventional path
* parses as a valid PostHog skill (YAML frontmatter with ``name`` and
  ``description``)
* matches the structural / content rules defined in
  ``.agents/skills/writing-skills/SKILL.md``
* covers the workflow described in the task (existing-source check,
  source-type identification, hand-off to the related setup skill,
  use of ``posthog:`` prefixed MCP tool references).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

REPO = Path("/workspace/posthog")
SKILL_PATH = REPO / "products/data_warehouse/skills/suggesting-data-imports/SKILL.md"
WRITING_SKILLS = REPO / ".agents/skills/writing-skills/SKILL.md"
SETUP_SKILL = REPO / "products/data_warehouse/skills/setting-up-a-data-warehouse-source/SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from a SKILL.md.

    Frontmatter MUST start on the first line with ``---`` and end with
    another ``---`` line, per the writing-skills SKILL.md.
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    assert m, "SKILL.md must start with a YAML frontmatter block delimited by `---`"
    fm = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return fm, body


# --------------------------------------------------------------------------- #
# pass_to_pass — sanity that the surrounding repo state is intact             #
# --------------------------------------------------------------------------- #


def test_repo_checked_out():
    """The base commit is present (sanity)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "f8208b0d7194bdfdccb95cc8d0060978734bb981"


def test_writing_skills_meta_skill_parses():
    """Meta-skill that defines authoring rules parses (pass_to_pass)."""
    assert WRITING_SKILLS.exists(), f"missing meta skill {WRITING_SKILLS}"
    fm, body = _split_frontmatter(_read(WRITING_SKILLS))
    assert fm.get("name") == "writing-skills"
    assert "description" in fm and fm["description"]
    assert "## Key rules" in body


def test_existing_setup_skill_parses():
    """Sibling skill (the one we hand off to) is present and parses (pass_to_pass)."""
    assert SETUP_SKILL.exists(), f"missing sibling skill {SETUP_SKILL}"
    fm, _ = _split_frontmatter(_read(SETUP_SKILL))
    assert fm.get("name") == "setting-up-a-data-warehouse-source"


# --------------------------------------------------------------------------- #
# fail_to_pass — the actual change                                            #
# --------------------------------------------------------------------------- #


def test_skill_file_exists_at_conventional_path():
    """The new SKILL.md must live under products/data_warehouse/skills/<slug>/."""
    assert SKILL_PATH.exists(), (
        f"expected new skill at {SKILL_PATH.relative_to(REPO)}; the directory "
        "products/{product}/skills/{skill-name}/SKILL.md is the only layout "
        "the build pipeline collects"
    )


def test_skill_frontmatter_has_required_fields():
    """Frontmatter must declare `name` and `description` (writing-skills rule)."""
    fm, _ = _split_frontmatter(_read(SKILL_PATH))
    assert "name" in fm and isinstance(fm["name"], str) and fm["name"], (
        "frontmatter is missing required `name` field"
    )
    assert "description" in fm and isinstance(fm["description"], str) and fm["description"], (
        "frontmatter is missing required `description` field"
    )


def test_skill_name_matches_directory_and_format():
    """`name` must match the directory slug, kebab-case, no `posthog-` prefix."""
    fm, _ = _split_frontmatter(_read(SKILL_PATH))
    name = fm["name"]
    assert name == "suggesting-data-imports", (
        f"frontmatter name {name!r} must match the directory slug "
        "'suggesting-data-imports'"
    )
    assert re.fullmatch(r"[a-z][a-z0-9-]*", name), (
        f"name {name!r} must be lowercase kebab-case"
    )
    assert not name.startswith("posthog-"), (
        "skill names must never be prefixed with `posthog-` (writing-skills rule)"
    )


def test_skill_description_length_and_specificity():
    """Description must be specific (covers trigger terms) and ≤ 1024 chars."""
    fm, _ = _split_frontmatter(_read(SKILL_PATH))
    desc = fm["description"]
    assert len(desc) <= 1024, f"description is {len(desc)} chars; max 1024"
    assert len(desc) >= 80, (
        f"description is only {len(desc)} chars; it must include trigger terms "
        "and a 'when to use' summary so the agent can route to it"
    )
    lowered = desc.lower()
    # The description should mention the trigger domains the PR cares about.
    domain_terms = ["revenue", "subscriptions", "billing", "crm", "support"]
    matches = [t for t in domain_terms if t in lowered]
    assert len(matches) >= 3, (
        "description must mention at least three of the trigger domains "
        f"(revenue, subscriptions, billing, CRM, support); found {matches}"
    )


def test_skill_body_under_500_lines():
    """SKILL.md is the entry point — keep under 500 lines (writing-skills rule)."""
    text = _read(SKILL_PATH)
    assert text.count("\n") < 500, (
        f"SKILL.md has {text.count(chr(10))} lines; meta-skill says keep entry "
        "point under 500 lines"
    )


def test_skill_references_data_warehouse_mcp_tools():
    """Body must reference the `posthog:` prefixed MCP tools used in the workflow."""
    body = _read(SKILL_PATH).lower()
    required_tools = [
        "posthog:external-data-sources-list",
        "posthog:external-data-schemas-list",
        "posthog:read-data-warehouse-schema",
    ]
    missing = [t for t in required_tools if t.lower() not in body]
    assert not missing, (
        "SKILL.md must reference the data-warehouse MCP tools the workflow "
        f"uses; missing: {missing}"
    )


def test_skill_hands_off_to_setup_skill():
    """A 'Related skills' / hand-off section must point at the existing setup skill."""
    body = _read(SKILL_PATH)
    assert "setting-up-a-data-warehouse-source" in body, (
        "SKILL.md must reference `setting-up-a-data-warehouse-source` for the "
        "actual setup workflow — that skill already covers wizard / db-schema "
        "/ create and we should not duplicate it"
    )


def test_skill_includes_source_type_lookup_table():
    """Body must include a markdown table mapping user need → source type."""
    body = _read(SKILL_PATH)
    # Markdown pipe table — at least one row separator with three columns.
    assert re.search(r"\|.*\|.*\|.*\|", body), (
        "SKILL.md must include a markdown table mapping business needs "
        "(revenue, CRM, support, etc.) to source types and key tables"
    )
    lowered = body.lower()
    expected_sources = ["stripe", "hubspot", "zendesk", "postgres"]
    missing_sources = [s for s in expected_sources if s not in lowered]
    assert not missing_sources, (
        "lookup table must cover the common source types named in the task; "
        f"missing: {missing_sources}"
    )


def test_skill_describes_when_to_use():
    """Body must include a 'When to use this skill' style section."""
    body = _read(SKILL_PATH).lower()
    assert "when to use" in body, (
        "SKILL.md must include a 'When to use' section so the agent can route to it"
    )


def test_skill_yaml_parses_clean():
    """Run a separate YAML-only parse via subprocess to catch frontmatter syntax bugs."""
    script = (
        "import re,sys,yaml,pathlib\n"
        f"p=pathlib.Path({str(SKILL_PATH)!r}).read_text(encoding='utf-8')\n"
        "m=re.match(r'^---\\s*\\n(.*?)\\n---\\s*\\n', p, re.DOTALL)\n"
        "assert m, 'no frontmatter'\n"
        "fm=yaml.safe_load(m.group(1))\n"
        "assert isinstance(fm, dict), 'frontmatter must parse to a mapping'\n"
        "assert 'name' in fm and 'description' in fm\n"
        "print('ok')\n"
    )
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"YAML parse failed:\n{r.stderr}"
    assert "ok" in r.stdout
