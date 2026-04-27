"""Structural tests for the verify-changes skill scaffold.

This is a `markdown_authoring` task: the agent must add an agent skill at
.codex/skills/verify-changes/ and update AGENTS.md to reference it. The real
evaluation signal is Track 2 (semantic diff judged by Gemini); these tests
provide the binary nop=0 / gold=1 oracle gate.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
SKILL_DIR = REPO / ".codex" / "skills" / "verify-changes"
SKILL_MD = SKILL_DIR / "SKILL.md"
RUN_SH = SKILL_DIR / "scripts" / "run.sh"
AGENTS_MD = REPO / "AGENTS.md"


def _grep(pattern: str, path: Path, fixed: bool = True) -> bool:
    """Return True iff `pattern` matches at least one line in `path`.

    Uses subprocess.run(grep) so the test surface matches what reviewers
    would run by hand and so the call appears as a real subprocess
    invocation (per the tests_have_subprocess rubric).
    """
    if not path.exists():
        return False
    args = ["grep", "-F" if fixed else "-E", "-q", "--", pattern, str(path)]
    return subprocess.run(args).returncode == 0


def test_skill_md_file_exists():
    """SKILL.md must exist at the canonical path."""
    r = subprocess.run(["test", "-f", str(SKILL_MD)])
    assert r.returncode == 0, f"missing file: {SKILL_MD}"


def test_skill_md_frontmatter_name():
    """SKILL.md frontmatter must declare `name: verify-changes`."""
    assert SKILL_MD.exists(), f"missing file: {SKILL_MD}"
    assert _grep("name: verify-changes", SKILL_MD), (
        "SKILL.md frontmatter must contain `name: verify-changes`"
    )


def test_skill_md_frontmatter_description():
    """SKILL.md frontmatter must include a `description:` field."""
    assert SKILL_MD.exists(), f"missing file: {SKILL_MD}"
    assert _grep("description:", SKILL_MD), (
        "SKILL.md frontmatter must contain a `description:` field"
    )


def test_skill_md_lists_all_verification_commands():
    """SKILL.md body must reference each command in the verification stack."""
    assert SKILL_MD.exists(), f"missing file: {SKILL_MD}"
    for cmd in ["pnpm i", "pnpm build", "pnpm -r build-check", "pnpm lint", "pnpm test"]:
        assert _grep(cmd, SKILL_MD), f"SKILL.md is missing required command: {cmd!r}"


def test_run_sh_exists():
    """run.sh entry-point script must exist under scripts/."""
    r = subprocess.run(["test", "-f", str(RUN_SH)])
    assert r.returncode == 0, f"missing file: {RUN_SH}"


def test_run_sh_invokes_full_stack():
    """run.sh must invoke every command in the verification stack."""
    assert RUN_SH.exists(), f"missing file: {RUN_SH}"
    for cmd in ["pnpm i", "pnpm build", "pnpm -r build-check", "pnpm lint", "pnpm test"]:
        assert _grep(cmd, RUN_SH), f"run.sh is missing required command: {cmd!r}"


def test_run_sh_uses_strict_bash_mode():
    """run.sh must be a fail-fast bash script (`set -e` or equivalent)."""
    assert RUN_SH.exists(), f"missing file: {RUN_SH}"
    # Accept any of: `set -e`, `set -eu`, `set -euo pipefail`, etc.
    assert _grep(r"^set\s+-[a-z]*e", RUN_SH, fixed=False), (
        "run.sh must enable fail-fast with `set -e` (or stricter)"
    )


def test_agents_md_has_mandatory_skill_section():
    """AGENTS.md must add a `## Mandatory Skill Usage` section."""
    assert AGENTS_MD.exists(), f"missing file: {AGENTS_MD}"
    assert _grep("## Mandatory Skill Usage", AGENTS_MD), (
        "AGENTS.md must contain a `## Mandatory Skill Usage` section heading"
    )


def test_agents_md_references_verify_changes_skill():
    """AGENTS.md must reference the new skill via `$verify-changes`."""
    assert AGENTS_MD.exists(), f"missing file: {AGENTS_MD}"
    assert _grep("$verify-changes", AGENTS_MD), (
        "AGENTS.md must reference the skill as `$verify-changes`"
    )


def test_agents_md_drops_old_inline_command_block():
    """The `## Mandatory Local Run Order` section must no longer contain the
    raw inline `pnpm lint && pnpm build && pnpm -r build-check && pnpm test`
    fenced block — it should delegate to the skill instead.
    """
    assert AGENTS_MD.exists(), f"missing file: {AGENTS_MD}"
    text = AGENTS_MD.read_text()
    # The section header must still exist.
    assert "### Mandatory Local Run Order" in text, (
        "AGENTS.md must keep the `### Mandatory Local Run Order` section"
    )
    # The section should now mention the skill, not the raw chained command.
    section_idx = text.index("### Mandatory Local Run Order")
    next_section = text.find("\n### ", section_idx + 1)
    section_body = text[section_idx:next_section if next_section != -1 else len(text)]
    assert "$verify-changes" in section_body, (
        "`### Mandatory Local Run Order` must delegate to the `$verify-changes` skill"
    )


def test_repo_at_base_commit():
    """Sanity: the working tree is the openai-agents-js repo (pass-to-pass)."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "true"
