"""Structural checks for the CLAUDE.md authoring task.

The gold answer adds a single new file at the repo root: CLAUDE.md.
Each test below maps 1:1 to a check in eval_manifest.yaml.
"""
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
CLAUDE_MD = REPO / "CLAUDE.md"


def _read():
    assert CLAUDE_MD.is_file(), f"CLAUDE.md missing at {CLAUDE_MD}"
    return CLAUDE_MD.read_text(encoding="utf-8")


def test_claude_md_exists_at_repo_root():
    """CLAUDE.md must be a tracked file at the project root."""
    # Use git to confirm the file exists in the working tree, not just on disk.
    r = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "CLAUDE.md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    untracked = r.stdout.strip()
    r2 = subprocess.run(
        ["git", "ls-files", "--", "CLAUDE.md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    tracked = r2.stdout.strip()
    assert CLAUDE_MD.is_file(), "CLAUDE.md is missing from the repo root."
    # Either tracked, or untracked-but-present is acceptable for our oracle.
    assert tracked or untracked, "CLAUDE.md is not visible to git."


def test_references_agents_md():
    """File must point readers at AGENTS.md for the full spec."""
    text = _read()
    assert "AGENTS.md" in text, (
        "CLAUDE.md must reference AGENTS.md so readers know where the full"
        " development spec lives."
    )


def test_lists_core_npm_commands():
    """File must list the project's core npm scripts."""
    text = _read()
    required = ["npm start", "npm run build", "npm test", "npm run lint", "npm run format"]
    missing = [cmd for cmd in required if cmd not in text]
    assert not missing, f"CLAUDE.md is missing required npm commands: {missing}"


def test_lists_pr_template_paths():
    """File must list both the English and Chinese PR template paths."""
    text = _read()
    required = [
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/PULL_REQUEST_TEMPLATE_CN.md",
    ]
    missing = [p for p in required if p not in text]
    assert not missing, f"CLAUDE.md must list PR template paths; missing: {missing}"


def test_lists_changelog_files():
    """File must list both changelog filenames (en + zh)."""
    text = _read()
    required = ["CHANGELOG.en-US.md", "CHANGELOG.zh-CN.md"]
    missing = [p for p in required if p not in text]
    assert not missing, f"CLAUDE.md must reference both changelog files; missing: {missing}"


def test_states_open_not_visible_convention():
    """The 'use `open`, avoid `visible`' panel-state convention must be stated."""
    text = _read()
    assert "`open`" in text and "`visible`" in text, (
        "CLAUDE.md must state the convention that panel open state uses `open`"
        " instead of `visible`."
    )


def test_repo_agents_md_unchanged():
    """Pass-to-pass: AGENTS.md was not modified by this task."""
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "AGENTS.md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    assert r.stdout.strip() == "", (
        f"AGENTS.md should not be modified by this task, but git reports:"
        f" {r.stdout!r}"
    )


def test_repo_clone_intact():
    """Pass-to-pass: base commit is an ancestor of HEAD (no destructive git ops)."""
    base = "2129ad4461103ec0bbe025cfd8bd26bf4e8b780b"
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Base commit {base[:12]} is not an ancestor of HEAD."
        f" The repo may have been corrupted."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && \\\n      "$EVENT" == "push" && \\\n      ( "$BRANCH" == "master" || \\\n        "$BRANCH" == "feature" || \\\n        "$BRANCH" == "next" ) ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
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