"""Markdown-authoring oracle for ant-design CLAUDE.md rule clarification.

Track 1: structural signal-line check that the substantive rule was added
to CLAUDE.md. The real evaluation signal is Track 2 (Gemini judges semantic
diff against config_edits in eval_manifest.yaml).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
CLAUDE_MD = REPO / "CLAUDE.md"


def _read_claude_md() -> str:
    assert CLAUDE_MD.is_file(), f"CLAUDE.md not found at {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


def test_pr_body_language_flexibility_rule_added():
    """The clarification that PR body language can follow the user's
    language preference must appear in CLAUDE.md."""
    text = _read_claude_md()
    assert "可根据用户语言习惯决定使用中文或英文" in text, (
        "CLAUDE.md must clarify that PR body language can follow the "
        "user's language preference (expected the verbatim phrase from "
        "the instruction)."
    )


def test_pr_body_rule_in_pr_section():
    """The new clarification belongs in the existing 'PR 规范' >
    '标题与内容' section (next to the existing PR-title rule)."""
    text = _read_claude_md()
    pr_section_start = text.find("## PR 规范")
    assert pr_section_start != -1, "Section '## PR 规范' is missing"
    # The next top-level section starts with '\n## ' or '\n---\n'
    rest = text[pr_section_start:]
    next_section = rest.find("\n---\n")
    pr_section = rest[: next_section if next_section != -1 else len(rest)]
    assert "可根据用户语言习惯决定使用中文或英文" in pr_section, (
        "The PR-body language clarification must live inside the "
        "'## PR 规范' section, not elsewhere in the file."
    )


def test_existing_pr_title_rule_preserved():
    """Existing PR-title rule must remain intact (regression guard)."""
    text = _read_claude_md()
    assert "PR 标题始终使用英文，格式：`类型: 简短描述`" in text, (
        "Pre-existing PR-title rule was unintentionally removed."
    )
    assert "fix: fix button style issues in Safari browser" in text, (
        "Pre-existing PR-title example was unintentionally removed."
    )


def test_claude_md_well_formed_markdown():
    """CLAUDE.md must remain well-formed: no unterminated tables, balanced
    fences, and the top-level title preserved."""
    text = _read_claude_md()
    assert text.startswith("# Ant Design 项目开发指南"), (
        "Top-level title was changed or removed."
    )
    # Code fences must be balanced.
    assert text.count("```") % 2 == 0, "Unbalanced ``` code fences."
    # Sanity: the file is non-trivial.
    assert len(text.splitlines()) >= 100, "CLAUDE.md was truncated."


def test_git_repo_intact():
    """Sanity: agent edits should leave the git working tree usable."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git status failed:\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_compile():
    """pass_to_pass | CI job 'build' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_check_build_files():
    """pass_to_pass | CI job 'build' → step 'check build files'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut test:dekko'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'check build files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && "$EVENT" == "pull_request" ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_project_run_script():
    """pass_to_pass | CI job 'Build Project' → step 'Run Script'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash ./scripts/ci-mock-project-build.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Script' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")