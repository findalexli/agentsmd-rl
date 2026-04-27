"""Tests for the prql-claude-md-releases-pointer task.

The task asks the agent to add a "Releases & Environment" section to
CLAUDE.md that points readers to the project's development documentation
file. These tests verify both the structural addition (f2p) and that the
existing CLAUDE.md content was not mangled (p2p).
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/prql")
CLAUDE_MD = REPO / "CLAUDE.md"
REFERENCED_DOC = REPO / "web/book/src/project/contributing/development.md"


def _read_claude_md() -> str:
    return CLAUDE_MD.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass — these MUST fail at the base commit and pass after the fix.
# ---------------------------------------------------------------------------

def test_releases_environment_section_added():
    """CLAUDE.md must contain a new top-level section named '## Releases & Environment'."""
    content = _read_claude_md()
    assert "## Releases & Environment" in content, (
        "CLAUDE.md is missing the '## Releases & Environment' section header."
    )


def test_section_points_to_development_md():
    """The new section must reference the path to the development documentation file."""
    content = _read_claude_md()
    assert "web/book/src/project/contributing/development.md" in content, (
        "CLAUDE.md must mention the path 'web/book/src/project/contributing/development.md' "
        "so Claude knows where to look for release/environment details."
    )


def test_section_describes_releases_or_environment_topic():
    """The new section's prose must describe the releases/environment topic.

    Either the explicit phrase 'releases or environment' is used, or two
    independent mentions of 'release(s)' and 'environment' appear in the
    section body. This guards against an agent only adding a heading with
    no substantive pointer.
    """
    content = _read_claude_md().lower()
    # Locate the new section.
    idx = content.find("## releases & environment")
    assert idx >= 0, "Section header not found"
    body = content[idx:]
    explicit = "releases or environment" in body
    has_release = "release" in body
    has_env = "environment" in body
    assert explicit or (has_release and has_env), (
        "The new section must describe releases and environment as the "
        "topic and explain where to find more information."
    )


def test_referenced_file_actually_exists_in_repo():
    """Sanity: the path the agent points to must really exist in the repo."""
    r = subprocess.run(
        ["test", "-f", str(REFERENCED_DOC)],
        capture_output=True,
    )
    assert r.returncode == 0, (
        f"The file {REFERENCED_DOC} does not exist in the repo; the new "
        "section must point to an existing path."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — these must already pass at the base commit and continue
# passing after the change. They guard against an agent mangling the file.
# ---------------------------------------------------------------------------

def test_claude_md_top_heading_preserved():
    """CLAUDE.md must still start with the '# Claude' top-level heading."""
    content = _read_claude_md()
    first_heading_line = next(
        (ln for ln in content.splitlines() if ln.startswith("# ")),
        "",
    )
    assert first_heading_line.strip() == "# Claude", (
        f"Top-level heading was changed; expected '# Claude' but found "
        f"'{first_heading_line!r}'."
    )


def test_existing_sections_preserved():
    """The original second-level sections must still be present."""
    content = _read_claude_md()
    expected_sections = [
        "## Development Workflow",
        "## Tests",
        "## Running the CLI",
        "## Linting",
        "## Documentation",
    ]
    missing = [s for s in expected_sections if s not in content]
    assert not missing, (
        f"The following pre-existing sections were removed: {missing}"
    )


def test_claude_md_still_tracked_by_git():
    """CLAUDE.md is still tracked by git in the repo."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "--error-unmatch", "CLAUDE.md"],
        capture_output=True,
    )
    assert r.returncode == 0, "CLAUDE.md is no longer tracked by git."
