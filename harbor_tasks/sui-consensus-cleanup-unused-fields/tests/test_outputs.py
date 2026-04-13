"""Test suite for requests library task."""

import subprocess
import sys

# Docker-internal path to the repo (from Dockerfile WORKDIR)
REPO = "/workspace/requests"


def test_agent_can_import_requests():
    """The requests library can be imported (fail_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "import requests; print(requests.__version__)"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed: {r.stderr}"
    assert "2." in r.stdout, f"Unexpected version: {r.stdout}"


def test_requests_http_get():
    """Basic HTTP GET works (fail_to_pass)."""
    code = """
import requests
try:
    r = requests.get('https://httpbin.org/get', timeout=10)
    print(f"Status: {r.status_code}")
    assert r.status_code == 200
except Exception as e:
    print(f"Error: {e}")
    exit(1)
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"HTTP GET failed: {r.stderr}"


# =============================================================================
# Pass-to-Pass Tests - Repo CI Commands
# =============================================================================


def test_repo_lint():
    """Repo's ruff linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/requests", "tests/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_ruff_format_src():
    """Repo's source code passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "src/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}"


def test_repo_pyproject_valid():
    """Repo's pyproject.toml is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml is invalid:\n{r.stderr[-500:]}"


def test_repo_src_structure():
    """Repo source structure is intact (pass_to_pass)."""
    # Check that key source files exist
    key_files = [
        "src/requests/__init__.py",
        "src/requests/api.py",
        "src/requests/sessions.py",
        "src/requests/models.py",
    ]
    for f in key_files:
        r = subprocess.run(
            ["test", "-f", f],
            capture_output=True,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Key file missing: {f}"


def test_repo_tests_structure():
    """Repo test structure is intact (pass_to_pass)."""
    # Check that key test files exist
    key_files = [
        "tests/test_utils.py",
        "tests/test_structures.py",
        "tests/test_requests.py",
        "tests/conftest.py",
    ]
    for f in key_files:
        r = subprocess.run(
            ["test", "-f", f],
            capture_output=True,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Key test file missing: {f}"


def test_repo_makefile_ci():
    """Repo's Makefile has ci target (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-q", "^ci:", "Makefile"],
        capture_output=True,
        cwd=REPO,
    )
    assert r.returncode == 0, "Makefile missing 'ci' target"
