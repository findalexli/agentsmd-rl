"""Structural checks for the make-pr skill markdown authoring task."""

import subprocess

REPO = "/workspace/remix"


def test_make_pr_skill_file_exists():
    """Skills/make-pr/SKILL.md was created with correct frontmatter."""
    r = subprocess.run(
        ["grep", "-c", "name: make-pr", f"{REPO}/skills/make-pr/SKILL.md"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"skills/make-pr/SKILL.md missing or lacks 'name: make-pr'"


def test_agents_md_references_make_pr():
    """AGENTS.md lists the make-pr skill with a description and file path."""
    r = subprocess.run(
        ["grep", "-c", "make-pr.*Create GitHub pull requests", f"{REPO}/AGENTS.md"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, "AGENTS.md missing make-pr skill reference"


def test_openai_config_exists():
    """Skills/make-pr/agents/openai.yaml was created with display name."""
    r = subprocess.run(
        ["grep", "-c", "Make PR", f"{REPO}/skills/make-pr/agents/openai.yaml"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, "skills/make-pr/agents/openai.yaml missing or lacks 'Make PR'"


def test_supersede_pr_skill_intact():
    """Existing supersede-pr skill was not damaged by the changes."""
    r = subprocess.run(
        ["grep", "-c", "name: supersede-pr", f"{REPO}/skills/supersede-pr/SKILL.md"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, "supersede-pr SKILL.md was accidentally modified or removed"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")