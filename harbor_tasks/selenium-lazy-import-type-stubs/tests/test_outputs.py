"""Tests for selenium type stub PR.

This validates that:
1. Type stub files (.pyi) exist for lazy-imported modules
2. mypy can resolve real types (not Any) from these stubs
3. The import fix in remote_connection.py works correctly
4. pyproject.toml includes .pyi files in package data
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/selenium")
PY_DIR = REPO / "py"
SELENIUM_PKG = PY_DIR / "selenium"


# ============================================================================
# Fail-to-pass tests: these should FAIL on base commit, PASS with fix
# ============================================================================

def test_webdriver_init_stub_exists():
    """Type stub for webdriver/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"

    # Verify it exports Chrome class
    content = stub_path.read_text()
    assert "class Chrome" in content or "WebDriver as Chrome" in content, \
        "Stub should export Chrome class"


def test_chrome_stub_exists():
    """Type stub for chrome/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "chrome" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"

    content = stub_path.read_text()
    assert "options" in content, "Chrome stub should export options submodule"
    assert "webdriver" in content, "Chrome stub should export webdriver submodule"


def test_edge_stub_exists():
    """Type stub for edge/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "edge" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"


def test_firefox_stub_exists():
    """Type stub for firefox/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "firefox" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"

    content = stub_path.read_text()
    assert "firefox_profile" in content, "Firefox stub should export firefox_profile"


def test_safari_stub_exists():
    """Type stub for safari/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "safari" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"


def test_ie_stub_exists():
    """Type stub for ie/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "ie" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"


def test_webkitgtk_stub_exists():
    """Type stub for webkitgtk/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "webkitgtk" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"


def test_wpewebkit_stub_exists():
    """Type stub for wpewebkit/__init__.py must exist."""
    stub_path = SELENIUM_PKG / "webdriver" / "wpewebkit" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"


def test_mypy_can_resolve_webdriver_imports():
    """mypy should resolve real types from stubs, not Any via __getattr__.

    Without stubs, __getattr__ makes all webdriver attributes resolve to Any
    in mypy. With proper stubs, Chrome/ChromeOptions resolve to real types.
    We verify this by checking that mypy catches deliberate type mismatches.
    """
    test_code = """
from selenium.webdriver import Chrome, ChromeOptions

# If stubs provide real types, these return-type mismatches are caught.
# If types fall back to Any (no stubs), mypy won't flag them.
def check_chrome() -> int:
    return Chrome  # error: incompatible return type

def check_opts() -> int:
    return ChromeOptions  # error: incompatible return type
"""
    test_file = PY_DIR / "_test_type_resolve.py"
    test_file.write_text(test_code)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(test_file), "--ignore-missing-imports",
             "--disable-error-code", "unused-ignore", "--no-error-summary"],
            capture_output=True, text=True, timeout=60, cwd=str(PY_DIR)
        )
        output = result.stdout + result.stderr
        error_lines = [l for l in output.split("\n")
                       if "error" in l.lower() and "return" in l.lower()]
        assert len(error_lines) >= 2, (
            f"Expected mypy to catch return-type errors (stubs may resolve to Any):\n{output}"
        )
    finally:
        test_file.unlink(missing_ok=True)


def test_pyproject_includes_pyi():
    """pyproject.toml should include *.pyi in package data."""
    pyproject_path = PY_DIR / "pyproject.toml"
    content = pyproject_path.read_text()
    assert '"*.pyi"' in content or "'*.pyi'" in content, \
        "pyproject.toml should include '*.pyi' in package-data"


def test_webdriver_stub_has_all_exports():
    """Main webdriver stub should export all expected classes."""
    stub_path = SELENIUM_PKG / "webdriver" / "__init__.pyi"
    assert stub_path.exists(), f"Missing type stub: {stub_path}"

    content = stub_path.read_text()
    expected = [
        "Chrome", "ChromeOptions", "ChromeService",
        "Firefox", "FirefoxOptions", "FirefoxService",
        "Edge", "EdgeOptions", "EdgeService",
        "Safari", "SafariOptions",
        "Remote",
        "ActionChains", "Keys",
    ]
    missing = [e for e in expected if e not in content]
    assert not missing, f"Stub missing exports: {missing}"


# ============================================================================
# Pass-to-pass tests: repo quality checks that should always pass
# ============================================================================

def test_selenium_package_imports():
    """Basic selenium package should be importable."""
    result = subprocess.run(
        [sys.executable, "-c", "import selenium; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=str(PY_DIR)
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"


def test_webdriver_package_imports():
    """selenium.webdriver package should be importable."""
    result = subprocess.run(
        [sys.executable, "-c", "from selenium import webdriver; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=str(PY_DIR)
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"


def test_import_desired_capabilities_directly():
    """Import DesiredCapabilities from common submodule directly."""
    code = """
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
print("OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30, cwd=str(PY_DIR)
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "OK" in result.stdout


def test_mypy_can_resolve_submodule_stubs():
    """mypy should resolve submodule types via stub files (pass_to_pass)."""
    test_code = """
from selenium.webdriver import chrome

def check_submodule() -> int:
    return chrome  # type error: module vs int
"""
    test_file = PY_DIR / "_test_submod_resolve.py"
    test_file.write_text(test_code)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(test_file), "--ignore-missing-imports",
             "--disable-error-code", "unused-ignore", "--no-error-summary"],
            capture_output=True, text=True, timeout=60, cwd=str(PY_DIR)
        )
        output = result.stdout + result.stderr
        error_lines = [l for l in output.split("\n")
                       if "error" in l.lower() and "return" in l.lower()]
        assert len(error_lines) >= 1, (
            f"Expected mypy to catch return-type error:\n{output}"
        )
    finally:
        test_file.unlink(missing_ok=True)


def test_repo_validate_pyproject():
    """Repo's pyproject.toml passes validation (pass_to_pass)."""
    r = subprocess.run(
        ["validate-pyproject", "./pyproject.toml"],
        capture_output=True, text=True, timeout=60, cwd=str(PY_DIR),
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr}"


def test_repo_ruff_check():
    """Repo's Python code passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "selenium", "--output-format=concise"],
        capture_output=True, text=True, timeout=120, cwd=str(PY_DIR),
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}"


def test_repo_python_compileall():
    """All Python files in repo have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "compileall", "selenium", "-q"],
        capture_output=True, text=True, timeout=120, cwd=str(PY_DIR),
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_remote_connection_unit_tests():
    """Repo's unit tests for remote_connection module pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/unit/selenium/webdriver/remote/remote_connection_tests.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=str(PY_DIR),
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}"


def test_repo_chrome_edge_options_unit_tests():
    """Repo's unit tests for Chrome and Edge options pass (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/unit/selenium/webdriver/chrome/chrome_options_tests.py", "test/unit/selenium/webdriver/edge/edge_options_tests.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=str(PY_DIR),
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}"


def test_repo_import_modified_modules():
    """Modified chrome/edge remote_connection modules are importable (pass_to_pass)."""
    code = """
from selenium.webdriver.chrome.remote_connection import ChromeRemoteConnection
from selenium.webdriver.edge.remote_connection import EdgeRemoteConnection
print("All modified modules import successfully")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30, cwd=str(PY_DIR),
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
    assert "import successfully" in r.stdout
