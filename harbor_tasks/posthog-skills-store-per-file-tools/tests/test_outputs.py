"""Behavioural / structural tests for the skills-store SKILL.md update.

The PR teaches the agent-facing `products/llm_analytics/skills/skills-store/SKILL.md`
about the per-file edit primitives (`skill-file-create`, `skill-file-delete`,
`skill-file-rename`, plus the body `edits` and per-file `file_edits` payloads).
These tests verify the documentation surface area: the available-tools table,
the local /phs bridge's allowed-tools list, frontmatter sanity, and that
the writing-skills "<500 lines" convention still holds.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/posthog")
SKILL_PATH = REPO / "products/llm_analytics/skills/skills-store/SKILL.md"


def _read() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_skill_file_present() -> None:
    """The target SKILL.md exists at the expected path."""
    r = subprocess.run(
        ["test", "-f", str(SKILL_PATH)],
        cwd=str(REPO),
        capture_output=True,
    )
    assert r.returncode == 0, f"Expected SKILL.md at {SKILL_PATH}"


def test_tools_table_lists_per_file_create() -> None:
    """Available-tools table must list `posthog:skill-file-create`."""
    text = _read()
    assert "posthog:skill-file-create" in text, (
        "The Available tools table must list the new `posthog:skill-file-create` tool."
    )


def test_tools_table_lists_per_file_delete() -> None:
    """Available-tools table must list `posthog:skill-file-delete`."""
    text = _read()
    assert "posthog:skill-file-delete" in text, (
        "The Available tools table must list the new `posthog:skill-file-delete` tool."
    )


def test_tools_table_lists_per_file_rename() -> None:
    """Available-tools table must list `posthog:skill-file-rename`."""
    text = _read()
    assert "posthog:skill-file-rename" in text, (
        "The Available tools table must list the new `posthog:skill-file-rename` tool."
    )


def _bridge_allowed_tools(text: str) -> str:
    """Return the value of the bridge skill's `allowed-tools:` line."""
    m = re.search(r"^allowed-tools:\s*(.+)$", text, re.M)
    assert m, "Expected an `allowed-tools:` line in the local /phs bridge frontmatter"
    return m.group(1)


def test_bridge_allowed_tools_includes_skill_file_create() -> None:
    """Local /phs bridge's allowed-tools must grant skill-file-create."""
    allowed = _bridge_allowed_tools(_read())
    assert "mcp__posthog__skill-file-create" in allowed, (
        "Bridge `allowed-tools` must include `mcp__posthog__skill-file-create`."
    )


def test_bridge_allowed_tools_includes_skill_file_delete() -> None:
    """Local /phs bridge's allowed-tools must grant skill-file-delete."""
    allowed = _bridge_allowed_tools(_read())
    assert "mcp__posthog__skill-file-delete" in allowed, (
        "Bridge `allowed-tools` must include `mcp__posthog__skill-file-delete`."
    )


def test_bridge_allowed_tools_includes_skill_file_rename() -> None:
    """Local /phs bridge's allowed-tools must grant skill-file-rename."""
    allowed = _bridge_allowed_tools(_read())
    assert "mcp__posthog__skill-file-rename" in allowed, (
        "Bridge `allowed-tools` must include `mcp__posthog__skill-file-rename`."
    )


def test_per_file_edits_payload_documented() -> None:
    """Doc must teach the `file_edits` per-file patch payload by name."""
    text = _read()
    assert "file_edits" in text, (
        "Doc must teach the `file_edits` payload (per-file find/replace) by name."
    )


def test_frontmatter_skill_name_unchanged() -> None:
    """The top-level skill name remains `skills-store` (frontmatter sanity)."""
    text = _read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    assert m, "SKILL.md must start with YAML frontmatter delimited by `---` lines"
    fm = m.group(1)
    assert re.search(r"^name:\s*skills-store\s*$", fm, re.M), (
        "Top-level frontmatter `name:` must remain `skills-store` (this PR is documentation only)."
    )


def test_skill_under_500_lines() -> None:
    """SKILL.md stays under 500 lines (writing-skills convention)."""
    r = subprocess.run(
        ["wc", "-l", str(SKILL_PATH)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    n = int(r.stdout.split()[0])
    assert n < 500, (
        f"SKILL.md is {n} lines — the writing-skills convention requires bodies "
        "to stay under 500 lines (move detailed material into bundled files)."
    )


def test_no_files_array_replace_all_promoted_as_default() -> None:
    """The bulk-replace `files` shape should not be the recommended default any more.

    Before the PR, the only documented update path was a `skill-update` call
    that took `body`/`files` (replacing the whole bundle). The PR demotes that
    path: per-file edits should be the recommended primitive. We check that the
    doc no longer says `files` replace-all is the default carry-forward
    behaviour for updates.
    """
    text = _read()
    legacy_phrase = (
        "If you pass `files`, they replace the previous version's file set; "
        "if you omit `files`, they're carried forward"
    )
    assert legacy_phrase not in text, (
        "The original phrasing that promoted `files` replace-all as the default "
        "update shape should no longer appear — describe per-file edits as the "
        "preferred primitive instead."
    )
