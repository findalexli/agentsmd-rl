import os
import stat
import subprocess
import pytest

REPO = "/workspace/openai-agents-js"


def _read_file(path):
    with open(os.path.join(REPO, path)) as f:
        return f.read()


# ---------------------------------------------------------------------------
# fail-to-pass: verify-changes skill files
# ---------------------------------------------------------------------------

def test_skill_md_exists():
    """SKILL.md exists at .codex/skills/verify-changes/SKILL.md."""
    path = os.path.join(REPO, ".codex/skills/verify-changes/SKILL.md")
    assert os.path.isfile(path), "SKILL.md missing"


def test_skill_md_has_frontmatter_name():
    """SKILL.md frontmatter includes name: verify-changes."""
    content = _read_file(".codex/skills/verify-changes/SKILL.md")
    assert "name: verify-changes" in content


def test_skill_md_has_description():
    """SKILL.md frontmatter includes a description key."""
    content = _read_file(".codex/skills/verify-changes/SKILL.md")
    assert "description:" in content


def test_run_sh_exists():
    """run.sh exists and is executable."""
    path = os.path.join(REPO, ".codex/skills/verify-changes/scripts/run.sh")
    assert os.path.isfile(path), "run.sh missing"
    assert os.access(path, os.X_OK), "run.sh not executable"


def test_run_sh_has_all_steps():
    """run.sh runs pnpm i, build, build-check, lint, test in order."""
    content = _read_file(".codex/skills/verify-changes/scripts/run.sh")
    steps = ["pnpm i", "pnpm build", "pnpm -r build-check", "pnpm lint", "pnpm test"]
    positions = [content.index(s) for s in steps]
    assert positions == sorted(positions), "pnpm steps not in correct order"


def test_run_ps1_exists():
    """run.ps1 exists."""
    path = os.path.join(REPO, ".codex/skills/verify-changes/scripts/run.ps1")
    assert os.path.isfile(path), "run.ps1 missing"


def test_agents_md_has_mandatory_skill_section():
    """AGENTS.md has a Mandatory Skill Usage section heading."""
    content = _read_file("AGENTS.md")
    assert "## Mandatory Skill Usage" in content


def test_agents_md_references_verify_changes_skill():
    """AGENTS.md references the $verify-changes skill."""
    content = _read_file("AGENTS.md")
    assert "$verify-changes" in content


def test_agents_md_no_inline_pnpm_chain():
    """AGENTS.md no longer contains the old inline pnpm lint && build && ... chain."""
    content = _read_file("AGENTS.md")
    assert "pnpm lint && pnpm build && pnpm -r build-check && pnpm test" not in content


def test_agents_md_mandatory_local_run_references_skill():
    """Mandatory Local Run Order section references the skill, not a raw bash block."""
    content = _read_file("AGENTS.md")
    assert "via the `$verify-changes` skill" in content


def test_agents_md_dev_workflow_references_skill():
    """Development Workflow step 4 references the skill."""
    content = _read_file("AGENTS.md")
    assert (
        "Run all checks using the `$verify-changes` skill" in content
        or "run the full verification stack" in content
    )


# ---------------------------------------------------------------------------
# pass-to-pass: repo structure / CI checks
# ---------------------------------------------------------------------------

def test_repo_package_json_exists():
    """Repo root has package.json."""
    assert os.path.isfile(os.path.join(REPO, "package.json"))


def test_repo_agents_md_exists():
    """Repo root has AGENTS.md."""
    assert os.path.isfile(os.path.join(REPO, "AGENTS.md"))


def test_repo_readme_exists():
    """Repo root has README.md."""
    assert os.path.isfile(os.path.join(REPO, "README.md"))


def test_pnpm_available():
    """pnpm is installed and usable."""
    r = subprocess.run(["pnpm", "--version"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"pnpm not available:\n{r.stderr}"


def test_git_repo_has_base_commit():
    """Repo is at the expected base commit."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "b54fc4a3222ea8b14b1c3a8e45457b4905354bee"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_run_build():
    """pass_to_pass | CI job 'build' → step 'Run build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")