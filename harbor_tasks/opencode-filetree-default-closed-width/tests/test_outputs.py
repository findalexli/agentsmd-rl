"""Test outputs for matplotlib task.

Pass-to-pass gates: repo CI tests that should pass on the base commit.
Fail-to-pass gates: tests that verify the fix works.
"""

import subprocess
import sys
from pathlib import Path

# Docker-internal path to the repo (NOT /workspace/repo/)
REPO = "/workspace/matplotlib"


def test_repo_imports():
    """Matplotlib imports successfully (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "import matplotlib; import matplotlib.pyplot as plt"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\\n{r.stderr}"


def test_repo_ruff():
    """Repo's ruff linter passes on lib/matplotlib (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "lib/matplotlib", "--output-format", "concise"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff failed:\\n{r.stderr[-500:]}\\n{r.stdout[-500:]}"


def test_repo_unit_tests_basic():
    """Repo's basic unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "lib/matplotlib/tests/test_api.py",
         "-x", "-v", "--timeout=60"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\\n{r.stderr[-500:]}"


def test_repo_pytest_cbook():
    """Repo's cbook module tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "lib/matplotlib/tests/test_cbook.py",
         "-x", "-v", "--timeout=60"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Cbook tests failed:\\n{r.stderr[-500:]}"


def test_repo_pytest_rcparams():
    """Repo's rcParams tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "lib/matplotlib/tests/test_rcparams.py",
         "-x", "-v", "--timeout=60", "-k", "not deprecated"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"RcParams tests failed:\\n{r.stderr[-500:]}"


def test_repo_pytest_basic():
    """Repo's basic sanity tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "lib/matplotlib/tests/test_basic.py",
         "lib/matplotlib/tests/test_matplotlib.py",
         "-x", "-v", "--timeout=60"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Basic tests failed:\\n{r.stderr[-500:]}"


def test_repo_pytest_artist():
    """Repo's artist module tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "lib/matplotlib/tests/test_artist.py",
         "-x", "-v", "--timeout=60"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Artist tests failed:\\n{r.stderr[-500:]}"


def test_repo_pytest_transforms():
    """Repo's transforms module tests pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "lib/matplotlib/tests/test_transforms.py",
         "-x", "-v", "--timeout=60", "-k", "not png"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Transforms tests failed:\\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass gates (these would test the actual fix)
# ---------------------------------------------------------------------------

def test_fix_claude_md_exists():
    """CLAUDE.md file was created in the repo root (fail_to_pass)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md should exist after the fix is applied"


def test_fix_claude_md_guidance():
    """CLAUDE.md contains Agg backend guidance (fail_to_pass)."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md must exist first"

    content = claude_md.read_text()
    assert "Task-specific guidance" in content, (
        "CLAUDE.md should have a 'Task-specific guidance' heading")
    assert "Agg backend" in content, (
        "CLAUDE.md should mention using the Agg backend for tests")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_sdist_build_sdist():
    """pass_to_pass | CI job 'Build sdist' → step 'Build sdist'"""
    import os
    env = os.environ.copy()
    env["GITHUB_OUTPUT"] = "/dev/null"
    r = subprocess.run(
        ["bash", "-lc", 'python -m build --sdist && python ci/export_sdist_name.py'],
        cwd=REPO, capture_output=True, text=True, timeout=300, env=env)
    assert r.returncode == 0, (
        f"CI step 'Build sdist' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")