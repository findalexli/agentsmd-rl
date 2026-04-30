"""Behavioral tests for the BTA AGENTS.md authoring task.

Each test maps 1:1 to a check in eval_manifest.yaml. All tests inspect the
markdown files the agent must author and verify the structural content.
The track-2 (Gemini) judge handles semantic-quality scoring of the prose.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/kotlin")
AGENTS_MD = REPO / "compiler/build-tools/AGENTS.md"
CLAUDE_MD = REPO / "compiler/build-tools/CLAUDE.md"
GUIDELINES = REPO / ".ai/guidelines.md"


def _read(path: Path) -> str:
    assert path.exists(), f"{path} does not exist"
    return path.read_text(encoding="utf-8")


def test_agents_md_authored():
    """compiler/build-tools/AGENTS.md must exist and be substantive."""
    content = _read(AGENTS_MD)
    nonblank = [line for line in content.splitlines() if line.strip()]
    assert len(nonblank) >= 30, (
        f"AGENTS.md is too short ({len(nonblank)} non-blank lines); "
        "an area doc must describe modules, architecture, and how to run tests"
    )


def test_claude_md_redirects_to_agents_md():
    """compiler/build-tools/CLAUDE.md must contain only the '@AGENTS.md' redirect.

    .ai/guidelines.md states explicitly:
        "Adding new area docs: Create AGENTS.md with content and CLAUDE.md
        containing only @AGENTS.md"
    """
    content = _read(CLAUDE_MD).strip()
    assert content == "@AGENTS.md", (
        f"CLAUDE.md must contain only '@AGENTS.md', got: {content!r}"
    )


def test_guidelines_table_has_build_tools_api_row():
    """`.ai/guidelines.md` table must include a 'Build Tools API' row pointing
    to the new compiler/build-tools/AGENTS.md."""
    content = _read(GUIDELINES)
    rows = [line for line in content.splitlines() if "Build Tools API" in line]
    assert rows, "no row mentioning 'Build Tools API' added to .ai/guidelines.md"
    assert any("compiler/build-tools/AGENTS.md" in r for r in rows), (
        "Build Tools API row must link to ../compiler/build-tools/AGENTS.md"
    )
    # Row must follow the markdown-table format used by neighboring rows.
    assert any(r.lstrip().startswith("|") and r.rstrip().endswith("|") for r in rows), (
        "Build Tools API entry must be a Markdown-table row (pipe-delimited)"
    )


def test_guidelines_row_position_under_areas_section():
    """The new row must sit inside the existing Areas table (alphabetical
    placement is conventional but not required); the check is that it shares
    the same table as the other area rows."""
    content = _read(GUIDELINES)
    lines = content.splitlines()
    bta_idx = next((i for i, ln in enumerate(lines) if "Build Tools API" in ln), -1)
    assert bta_idx >= 0
    # The closest "## Areas" header above must appear before the row.
    headers_above = [i for i, ln in enumerate(lines[:bta_idx]) if ln.strip().startswith("## ")]
    assert headers_above, "no section header before the new row"
    nearest_header = lines[headers_above[-1]].strip().lower()
    assert "area" in nearest_header, (
        f"BTA row is under section {nearest_header!r}, "
        f"expected to be inside the Areas section"
    )


def test_agents_md_describes_bta_modules():
    """AGENTS.md must reference the BTA module names that exist on disk under
    compiler/build-tools/.

    The agent can discover these by listing the directory; the area doc
    is meaningful only if the modules it describes match what's there.
    """
    content = _read(AGENTS_MD)
    # These are real submodules under compiler/build-tools/ at base commit.
    # Any agent doc that ignores them is failing its job.
    must_mention = [
        "kotlin-build-tools-api",
        "kotlin-build-tools-impl",
    ]
    missing = [k for k in must_mention if k not in content]
    assert not missing, (
        f"AGENTS.md does not mention these BTA modules: {missing}. "
        "An area doc must enumerate the modules the area contains."
    )


def test_agents_md_links_or_codes_module_names():
    """Module names should appear as code (\\`name\\`) or as Markdown links —
    bare prose mentions alone don't help an agent navigate."""
    content = _read(AGENTS_MD)
    # At least one of the canonical module names must be either backticked
    # or used as a Markdown link target.
    code_or_link = re.compile(
        r"`kotlin-build-tools-(?:api|impl)`|"
        r"\[[^\]]*kotlin-build-tools-(?:api|impl)[^\]]*\]\([^)]*\)"
    )
    assert code_or_link.search(content), (
        "module names must appear as backticked code or Markdown links"
    )


def test_no_unrelated_files_modified():
    """The agent's task touches only the three markdown files we asked for.
    Any other modification to the repo is out of scope."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    changed = []
    for line in r.stdout.splitlines():
        # Status output: "XY path"
        if not line.strip():
            continue
        path = line[3:].strip()
        # Strip surrounding quotes if present (rename targets have "old -> new")
        if " -> " in path:
            path = path.split(" -> ")[-1]
        path = path.strip('"')
        changed.append(path)
    allowed = {
        ".ai/guidelines.md",
        "compiler/build-tools/AGENTS.md",
        "compiler/build-tools/CLAUDE.md",
    }
    extra = [p for p in changed if p not in allowed]
    assert not extra, f"unexpected files modified: {extra}"


def test_guidelines_unrelated_rows_intact():
    """Editing the table must not delete or corrupt existing area rows.

    Spot-check that pre-existing rows (Analysis API, FIR, PSI, KGP) still
    point to the same AGENTS.md they did at base commit.
    """
    content = _read(GUIDELINES)
    expected_rows = [
        ("Analysis API", "../analysis/AGENTS.md"),
        ("FIR (K2 frontend)", "../compiler/AGENTS.md"),
        ("PSI", "../compiler/psi/AGENTS.md"),
        ("Kotlin Gradle Plugin", "../libraries/tools/kotlin-gradle-plugin/AGENTS.md"),
    ]
    for area, link in expected_rows:
        rows = [ln for ln in content.splitlines() if ln.startswith("|") and area in ln]
        assert rows, f"existing area row '{area}' missing from guidelines.md"
        assert any(link in r for r in rows), (
            f"area '{area}' row no longer links to {link}"
        )
