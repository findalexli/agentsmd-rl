"""Test outputs for the requests default_user_agent documentation task."""

import subprocess
import sys
from pathlib import Path

# Docker-internal repo path - this is where the repo lives INSIDE the container
REPO = "/workspace/requests"


def test_docstring_added_fail_to_pass():
    """The default_user_agent function has an updated docstring (fail_to_pass)."""
    utils_path = Path(f"{REPO}/src/requests/utils.py")
    content = utils_path.read_text()

    # Find the default_user_agent function and check its docstring
    in_function = False
    in_docstring = False
    docstring_content = []

    for line in content.split("\n"):
        if "def default_user_agent(" in line:
            in_function = True
            continue
        if in_function:
            if '"""' in line and not in_docstring:
                in_docstring = True
                docstring_content.append(line)
                if line.count('"""') == 2:  # One-line docstring
                    break
            elif '"""' in line and in_docstring:
                docstring_content.append(line)
                break
            elif in_docstring:
                docstring_content.append(line)

    full_docstring = "\n".join(docstring_content)

    # Check for the added documentation elements
    assert ":param name:" in full_docstring, "Missing parameter documentation for 'name'"
    assert "Example:" in full_docstring or "library name and version" in full_docstring, \
        "Missing usage example or detailed description"


# =============================================================================
# Pass-to-Pass Tests (repo CI commands)
# =============================================================================

def test_repo_ruff_check_pass_to_pass():
    """Repo's ruff linter passes on utils.py (pass_to_pass)."""
    result = subprocess.run(
        ["ruff", "check", "--no-cache", "src/requests/utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stderr[-500:]}"


def test_repo_utils_tests_pass_to_pass():
    """Repo's unit tests for utils module pass (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_utils.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Utils tests failed:\n{result.stderr[-500:]}"


def test_repo_package_imports_pass_to_pass():
    """Repo's package can be imported after installation (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "import requests; "
         "from requests.utils import default_user_agent; "
         "ua = default_user_agent(); "
         "assert 'python-requests' in ua; "
         "assert '/' in ua; "
         "print('Imports OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Import test failed:\n{result.stderr[-500:]}"


def test_repo_ruff_format_pass_to_pass():
    """Repo's code is properly formatted with ruff (pass_to_pass)."""
    result = subprocess.run(
        ["ruff", "format", "--check", "--no-cache", "src/requests/utils.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stderr[-500:]}"


def test_repo_extended_tests_pass_to_pass():
    """Repo's unit tests for utils, structures, and help modules pass (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_utils.py", "tests/test_structures.py", "tests/test_help.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Extended tests failed:\n{result.stderr[-500:]}"


def test_repo_doctests_pass_to_pass():
    """Repo's doctests in utils module pass (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--doctest-modules", "src/requests/utils.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Doctests failed:\n{result.stderr[-500:]}"


# =============================================================================
# Pass-to-Pass Tests (static - file content checks)
# =============================================================================

def test_code_structure_preserved_pass_to_pass():
    """The function signature remains unchanged (pass_to_pass)."""
    utils_path = Path(f"{REPO}/src/requests/utils.py")
    content = utils_path.read_text()

    # Check that function signature is preserved
    assert "def default_user_agent(name=\"python-requests\"):" in content, \
        "Function signature was modified unexpectedly"


def test_function_still_works_pass_to_pass():
    """The default_user_agent function still returns correct output (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from requests.utils import default_user_agent; "
         "ua = default_user_agent(); "
         "assert 'python-requests' in ua; "
         "print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Function test failed: {result.stderr}"
