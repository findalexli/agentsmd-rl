"""Behavioral checks for the ant-design CLAUDE.md import-rules task.

This is a markdown_authoring task: the agent must add two new top-level
sections to CLAUDE.md describing absolute-import rules for demo files and
relative-import rules for test files. Each test asserts on a distinctive
literal that an agent following the instruction must produce.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
CLAUDE_MD = REPO / "CLAUDE.md"


def _read_claude() -> str:
    assert CLAUDE_MD.is_file(), f"{CLAUDE_MD} does not exist"
    return CLAUDE_MD.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# fail_to_pass: each new signal must appear in CLAUDE.md
# ---------------------------------------------------------------------------


def test_demo_section_heading_present():
    """The Demo import-rules section must be added with the exact heading."""
    text = _read_claude()
    assert re.search(r"(?m)^## Demo 导入规范\s*$", text), (
        "Expected a top-level (`##`) section titled `Demo 导入规范` in CLAUDE.md, "
        "but it was not found."
    )


def test_test_section_heading_present():
    """The Test import-rules section must be added with the exact heading."""
    text = _read_claude()
    assert re.search(r"(?m)^## Test 导入规范\s*$", text), (
        "Expected a top-level (`##`) section titled `Test 导入规范` in CLAUDE.md, "
        "but it was not found."
    )


def test_demo_section_scope_documented():
    """Demo section must scope to `components/**/demo/` and `.dumi/`."""
    text = _read_claude()
    demo_idx = text.find("## Demo 导入规范")
    assert demo_idx >= 0, "Demo 导入规范 section is missing"
    test_idx = text.find("## Test 导入规范", demo_idx)
    end_idx = test_idx if test_idx > 0 else len(text)
    body = text[demo_idx:end_idx]
    assert "components/**/demo/" in body, (
        "Demo section must mention scope `components/**/demo/`."
    )
    assert ".dumi/" in body, "Demo section must mention scope `.dumi/`."


def test_demo_section_lists_absolute_import_patterns():
    """Demo section must enumerate the allowed absolute-import forms."""
    text = _read_claude()
    demo_idx = text.find("## Demo 导入规范")
    assert demo_idx >= 0
    test_idx = text.find("## Test 导入规范", demo_idx)
    end_idx = test_idx if test_idx > 0 else len(text)
    body = text[demo_idx:end_idx]
    for pattern in ("antd/es/*", "antd/lib/*", "antd/locale/*", ".dumi/*", "@@/*"):
        assert pattern in body, (
            f"Demo section must list `{pattern}` among the allowed absolute-import "
            f"forms; did not find it."
        )


def test_test_section_scope_documented():
    """Test section must scope to `components/**/__tests__/`."""
    text = _read_claude()
    test_idx = text.find("## Test 导入规范")
    assert test_idx >= 0, "Test 导入规范 section is missing"
    body = text[test_idx:]
    assert "components/**/__tests__/" in body, (
        "Test section must mention scope `components/**/__tests__/`."
    )


def test_test_section_forbids_absolute_aliases():
    """Test section must list the forbidden absolute / alias forms."""
    text = _read_claude()
    test_idx = text.find("## Test 导入规范")
    assert test_idx >= 0
    body = text[test_idx:]
    for pattern in ("antd/es/*", "antd/lib/*", "antd/locale/*", ".dumi/*", "@@/*"):
        assert pattern in body, (
            f"Test section must list `{pattern}` among the forbidden absolute / "
            f"alias forms; did not find it."
        )


def test_demo_and_test_sections_are_chinese_prose():
    """Both sections must be written in Chinese to match the rest of CLAUDE.md."""
    text = _read_claude()
    for heading in ("## Demo 导入规范", "## Test 导入规范"):
        idx = text.find(heading)
        assert idx >= 0, f"Missing heading: {heading}"
        # Walk forward 600 chars or until next `## ` heading.
        end = text.find("\n## ", idx + len(heading))
        if end < 0:
            end = idx + 800
        body = text[idx:end]
        # Heuristic: the body must contain CJK characters (the file is Chinese).
        cjk = re.findall(r"[一-鿿]", body)
        assert len(cjk) >= 20, (
            f"Section {heading!r} body has {len(cjk)} CJK characters; the new "
            f"sections must be written in Chinese to match the existing file style."
        )


def test_demo_section_appears_before_test_section():
    """Demo section must come before Test section."""
    text = _read_claude()
    demo_idx = text.find("## Demo 导入规范")
    test_idx = text.find("## Test 导入规范")
    assert demo_idx >= 0 and test_idx >= 0
    assert demo_idx < test_idx, (
        "Demo section must appear before Test section in CLAUDE.md."
    )


# ---------------------------------------------------------------------------
# pass_to_pass: existing CLAUDE.md content must be preserved
# ---------------------------------------------------------------------------


def test_existing_doc_section_preserved():
    """The pre-existing `## 文档规范` section must remain in CLAUDE.md."""
    text = _read_claude()
    assert re.search(r"(?m)^## 文档规范\s*$", text), (
        "The existing `## 文档规范` section disappeared from CLAUDE.md."
    )


def test_existing_pr_section_preserved():
    """The pre-existing `## PR 规范` section must remain in CLAUDE.md."""
    text = _read_claude()
    assert re.search(r"(?m)^## PR 规范\s*$", text), (
        "The existing `## PR 规范` section disappeared from CLAUDE.md."
    )


def test_existing_changelog_section_preserved():
    """The pre-existing `## Changelog 规范` section must remain in CLAUDE.md."""
    text = _read_claude()
    assert re.search(r"(?m)^## Changelog 规范\s*$", text), (
        "The existing `## Changelog 规范` section disappeared from CLAUDE.md."
    )


def test_repo_git_clean_other_files():
    """Only CLAUDE.md (and possibly nothing else under VCS) must be modified.

    Uses `git status --porcelain` to confirm the agent did not silently edit
    other tracked files in the repo.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    changed = [
        line[3:].strip()
        for line in r.stdout.splitlines()
        if line.strip() and not line.startswith("??")
    ]
    unexpected = [p for p in changed if p != "CLAUDE.md"]
    assert not unexpected, (
        f"Unexpected modifications to tracked files outside CLAUDE.md: {unexpected}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && \\\n      "$EVENT" == "push" && \\\n      ( "$BRANCH" == "master" || \\\n        "$BRANCH" == "feature" || \\\n        "$BRANCH" == "next" ) ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")