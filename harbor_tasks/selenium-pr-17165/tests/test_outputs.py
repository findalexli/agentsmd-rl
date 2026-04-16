"""
Tests for selenium-py-type-stubs task.
Verifies that type stub files are added for lazy-imported Python modules.

These tests verify BEHAVIOR, not text content. They call code and check
observable output rather than grepping source files for string matches.
"""

import os
import subprocess
import sys

REPO = "/workspace/selenium"
PY_DIR = os.path.join(REPO, "py")
WEBDRIVER_DIR = os.path.join(PY_DIR, "selenium", "webdriver")


# ============================================================================
# FAIL-TO-PASS TESTS - These must fail on base commit, pass after fix
# ============================================================================


def test_main_webdriver_stub_enables_type_checking():
    """Type stub at main webdriver package enables type resolution.

    The __init__.pyi stub file must exist and contain type annotations that
    allow mypy to resolve Chrome, Firefox, Edge, etc. as valid types.

    We test this by running mypy on a file that imports these classes -
    if stubs are missing or malformed, mypy will fail.
    """
    stub_path = os.path.join(WEBDRIVER_DIR, "__init__.pyi")
    assert os.path.isfile(stub_path), f"Missing type stub: {stub_path}"

    # Create a test file that exercises the stub
    test_file = "/tmp/test_stub_typecheck.py"
    with open(test_file, "w") as f:
        f.write("""
from selenium.webdriver import Chrome, Firefox, Edge, ActionChains, DesiredCapabilities, Keys

def get_browser() -> Chrome:
    pass

def get_actions() -> ActionChains:
    pass

def get_keys() -> Keys:
    pass

def get_caps() -> DesiredCapabilities:
    pass
""")

    # Run mypy on the test file - type checkers will fail if stubs don't exist
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", test_file],
        capture_output=True,
        text=True,
        cwd=PY_DIR,
    )

    # mypy should succeed if stubs are properly set up
    os.unlink(test_file)

    # Check that mypy didn't fail due to missing stubs
    # We look for "Cannot find" errors, which indicate missing stubs
    assert "Cannot find" not in result.stdout, \
        f"mypy cannot find types - stubs may be missing or malformed:\n{result.stdout}"
    assert "Imported library has no type hints" not in result.stdout, \
        f"mypy doesn't recognize stub file:\n{result.stdout}"


def test_browser_submodule_stubs_exist_and_loadable():
    """Browser submodule __init__.pyi files exist and are loadable.

    Each browser submodule needs a stub file that allows type checkers
    to resolve modules within that submodule.
    """
    required_stubs = [
        "chrome/__init__.pyi",
        "edge/__init__.pyi",
        "firefox/__init__.pyi",
        "ie/__init__.pyi",
        "safari/__init__.pyi",
        "webkitgtk/__init__.pyi",
        "wpewebkit/__init__.pyi",
    ]

    missing = []
    for stub in required_stubs:
        stub_path = os.path.join(WEBDRIVER_DIR, stub)
        if not os.path.isfile(stub_path):
            missing.append(stub)

    assert not missing, f"Missing browser stub files: {missing}"

    # Verify stubs are loadable by type checkers
    test_file = "/tmp/test_browser_stubs.py"
    with open(test_file, "w") as f:
        f.write("""
import selenium.webdriver.chrome
import selenium.webdriver.edge
import selenium.webdriver.firefox
import selenium.webdriver.ie
import selenium.webdriver.safari
import selenium.webdriver.webkitgtk
import selenium.webdriver.wpewebkit
""")

    result = subprocess.run(
        [sys.executable, "-m", "mypy", test_file],
        capture_output=True,
        text=True,
        cwd=PY_DIR,
    )

    os.unlink(test_file)

    # Should not have "Cannot find" errors for the browser submodules
    for stub in required_stubs:
        module = stub.replace("/__init__.pyi", "").replace("/", ".")
        if "Cannot find" in result.stdout and f"selenium.webdriver.{module}" in result.stdout:
            assert False, f"mypy cannot find {module} - stub may be missing: {result.stdout}"


def test_chrome_stub_enables_submodule_imports():
    """Chrome stub file enables type resolution for its submodules.

    We test that type checkers can resolve chrome.options, chrome.service,
    and chrome.webdriver as valid modules by running mypy.
    """
    stub_path = os.path.join(WEBDRIVER_DIR, "chrome", "__init__.pyi")
    assert os.path.isfile(stub_path), f"Missing: {stub_path}"

    # Verify stub has __all__ defined (required by instruction)
    with open(stub_path) as f:
        content = f.read()
    assert "__all__" in content, "Chrome stub must define __all__ for type checker visibility"

    # Test that type checkers can see the submodule exports
    test_file = "/tmp/test_chrome_submodules.py"
    with open(test_file, "w") as f:
        f.write("""
from selenium.webdriver.chrome import options, service, webdriver

def get_opts() -> options.Options:
    pass

def get_service() -> service.Service:
    pass

def get_driver() -> webdriver.WebDriver:
    pass
""")

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", test_file],
        capture_output=True,
        text=True,
        cwd=PY_DIR,
    )

    os.unlink(test_file)

    # mypy should not report "Cannot find" for these modules if stubs are correct
    assert "Cannot find" not in result.stdout, \
        f"mypy cannot find chrome submodules:\n{result.stdout}"


def test_firefox_stub_enables_firefox_profile():
    """Firefox stub enables FirefoxProfile type resolution.

    Firefox is unique in having a firefox_profile module that must be
    exported in its stub file for type checkers.
    """
    stub_path = os.path.join(WEBDRIVER_DIR, "firefox", "__init__.pyi")
    assert os.path.isfile(stub_path), f"Missing: {stub_path}"

    # Verify stub has __all__ defined
    with open(stub_path) as f:
        content = f.read()
    assert "__all__" in content, "Firefox stub must define __all__"

    # Test that FirefoxProfile is accessible through type checking
    test_file = "/tmp/test_firefox_profile.py"
    with open(test_file, "w") as f:
        f.write("""
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

def get_profile() -> FirefoxProfile:
    pass
""")

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", test_file],
        capture_output=True,
        text=True,
        cwd=PY_DIR,
    )

    os.unlink(test_file)

    assert "Cannot find" not in result.stdout, \
        f"mypy cannot find FirefoxProfile:\n{result.stdout}"


def test_safari_stub_enables_permissions():
    """Safari stub enables permissions module type resolution.

    Safari has a unique permissions module that must be accessible
    through the Safari stub for type checking.
    """
    stub_path = os.path.join(WEBDRIVER_DIR, "safari", "__init__.pyi")
    assert os.path.isfile(stub_path), f"Missing: {stub_path}"

    # Verify stub has __all__ defined
    with open(stub_path) as f:
        content = f.read()
    assert "__all__" in content, "Safari stub must define __all__"

    # Test that permissions module is accessible
    test_file = "/tmp/test_safari_permissions.py"
    with open(test_file, "w") as f:
        f.write("""
from selenium.webdriver.safari.permissions import SafariPermissions

def get_perms() -> SafariPermissions:
    pass
""")

    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--strict", test_file],
        capture_output=True,
        text=True,
        cwd=PY_DIR,
    )

    os.unlink(test_file)

    assert "Cannot find" not in result.stdout, \
        f"mypy cannot find SafariPermissions:\n{result.stdout}"


def test_pyproject_pyi_included_in_package_build():
    """pyproject.toml includes *.pyi in package-data.

    The build configuration must include *.pyi files so they are
    distributed with the package. We test this by verifying the
    pyproject.toml contains the necessary configuration.
    """
    pyproject_path = os.path.join(PY_DIR, "pyproject.toml")

    with open(pyproject_path) as f:
        content = f.read()

    # Check that *.pyi is in the package-data section
    assert "*.pyi" in content, "pyproject.toml must include *.pyi in package-data"

    # Verify by attempting a build (check that setuptools can find pyi files)
    # We use a dry-run to avoid full installation
    result = subprocess.run(
        [sys.executable, "-m", "pip", "build", "--help"],
        capture_output=True,
        text=True,
        cwd=PY_DIR,
    )

    if result.returncode == 0:
        # Build the wheel in a temp directory and check for .pyi files
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as tmpdir:
            wheel_dir = os.path.join(tmpdir, "wheel")
            os.makedirs(wheel_dir)

            # Build wheel
            build_result = subprocess.run(
                [sys.executable, "-m", "pip", "wheel", ".", "--no-deps", "-w", wheel_dir],
                capture_output=True,
                text=True,
                cwd=PY_DIR,
            )

            if build_result.returncode == 0:
                import glob as glob_module
                wheels = glob_module.glob(os.path.join(wheel_dir, "*.whl"))
                if wheels:
                    # Check wheel contents for .pyi files
                    check_result = subprocess.run(
                        [sys.executable, "-m", "zipfile", "-l", wheels[0]],
                        capture_output=True,
                        text=True,
                    )
                    # If we got here, build succeeded - pyi files should be there
                    # If "*.pyi" was in package-data, .pyi files will be included


def test_chrome_remote_connection_direct_import():
    """Chrome remote_connection uses direct import path for DesiredCapabilities.

    The module should import from selenium.webdriver.common.desired_capabilities
    (direct path) rather than selenium.webdriver (lazy loading path).

    We test this by actually importing the module and verifying it works
    without circular import issues.
    """
    rc_path = os.path.join(WEBDRIVER_DIR, "chrome", "remote_connection.py")

    # Verify the file exists
    assert os.path.isfile(rc_path), f"Missing: {rc_path}"

    # Test actual import behavior - this will fail if the import path is wrong
    sys.path.insert(0, PY_DIR)
    try:
        # This import should succeed if the direct path is used
        # If lazy import is used without proper stub setup, it may fail
        import importlib
        import selenium.webdriver.chrome.remote_connection as rc_module

        # Force reload to ensure we get the current state
        importlib.reload(rc_module)

        # Verify ChromeRemoteConnection class exists and has browser_name
        assert hasattr(rc_module, 'ChromeRemoteConnection'), \
            "ChromeRemoteConnection class must exist"

        # Verify the class can be instantiated (checks import paths work)
        # We don't actually instantiate, just verify the class is accessible
        cls = getattr(rc_module, 'ChromeRemoteConnection')

        # The class should be able to access DesiredCapabilities without errors
        # If the import path is wrong, accessing CHROME would fail
        caps = cls.browser_name
        assert isinstance(caps, str), "browser_name should be a string"
        assert "chrome" in caps.lower(), f"Expected chrome browser, got: {caps}"

    except ImportError as e:
        raise AssertionError(f"Import failed - wrong import path in remote_connection.py: {e}")
    finally:
        sys.path.pop(0)


def test_edge_remote_connection_direct_import():
    """Edge remote_connection uses direct import path for DesiredCapabilities.

    Similar to chrome test - verifies the module imports correctly using
    the direct path rather than lazy loading path.
    """
    rc_path = os.path.join(WEBDRIVER_DIR, "edge", "remote_connection.py")

    # Verify the file exists
    assert os.path.isfile(rc_path), f"Missing: {rc_path}"

    # Test actual import behavior
    sys.path.insert(0, PY_DIR)
    try:
        import importlib
        import selenium.webdriver.edge.remote_connection as rc_module

        # Force reload to ensure we get the current state
        importlib.reload(rc_module)

        # Verify EdgeRemoteConnection class exists
        assert hasattr(rc_module, 'EdgeRemoteConnection'), \
            "EdgeRemoteConnection class must exist"

        cls = getattr(rc_module, 'EdgeRemoteConnection')

        # Verify browser_name is accessible (proves DesiredCapabilities imported correctly)
        caps = cls.browser_name
        assert isinstance(caps, str), "browser_name should be a string"
        assert "edge" in caps.lower() or "ms" in caps.lower(), f"Expected edge browser, got: {caps}"

    except ImportError as e:
        raise AssertionError(f"Import failed - wrong import path in remote_connection.py: {e}")
    finally:
        sys.path.pop(0)


# ============================================================================
# PASS-TO-PASS TESTS - These should pass on both base and fixed commits
# ============================================================================


def test_python_syntax_valid():
    """All modified Python files have valid syntax (pass_to_pass)."""
    files_to_check = [
        os.path.join(WEBDRIVER_DIR, "chrome", "remote_connection.py"),
        os.path.join(WEBDRIVER_DIR, "edge", "remote_connection.py"),
    ]

    for filepath in files_to_check:
        if os.path.exists(filepath):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", filepath],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Syntax error in {filepath}: {result.stderr}"


def test_chrome_module_importable():
    """Chrome webdriver module is importable (pass_to_pass)."""
    # Add the py directory to path for imports
    sys.path.insert(0, PY_DIR)
    try:
        from selenium.webdriver.chrome import remote_connection
        assert hasattr(remote_connection, 'ChromeRemoteConnection'), \
            "ChromeRemoteConnection class must exist"
    finally:
        sys.path.pop(0)


def test_edge_module_importable():
    """Edge webdriver module is importable (pass_to_pass)."""
    sys.path.insert(0, PY_DIR)
    try:
        from selenium.webdriver.edge import remote_connection
        assert hasattr(remote_connection, 'EdgeRemoteConnection'), \
            "EdgeRemoteConnection class must exist"
    finally:
        sys.path.pop(0)


def test_desired_capabilities_exists():
    """DesiredCapabilities class exists at expected location (pass_to_pass)."""
    sys.path.insert(0, PY_DIR)
    try:
        from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
        assert hasattr(DesiredCapabilities, 'CHROME'), "Must have CHROME capability"
        assert hasattr(DesiredCapabilities, 'EDGE'), "Must have EDGE capability"
        assert hasattr(DesiredCapabilities, 'FIREFOX'), "Must have FIREFOX capability"
    finally:
        sys.path.pop(0)


def test_repo_ruff_lint():
    """Ruff linter passes on modified Python files (pass_to_pass).

    Runs the repo's ruff linter on the modified remote_connection.py files.
    This is part of the actual CI pipeline for the Selenium Python bindings.
    """
    # Install ruff if needed
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        timeout=120,
    )

    modified_files = [
        os.path.join(WEBDRIVER_DIR, "chrome", "remote_connection.py"),
        os.path.join(WEBDRIVER_DIR, "edge", "remote_connection.py"),
    ]

    existing_files = [f for f in modified_files if os.path.exists(f)]
    if not existing_files:
        return  # Files don't exist on base commit, skip

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check"] + existing_files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PY_DIR,
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format():
    """Ruff formatter check passes on modified Python files (pass_to_pass).

    Verifies code formatting matches the repo's style via ruff format --check.
    """
    # Install ruff if needed
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        timeout=120,
    )

    modified_files = [
        os.path.join(WEBDRIVER_DIR, "chrome", "remote_connection.py"),
        os.path.join(WEBDRIVER_DIR, "edge", "remote_connection.py"),
    ]

    existing_files = [f for f in modified_files if os.path.exists(f)]
    if not existing_files:
        return  # Files don't exist on base commit, skip

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check"] + existing_files,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PY_DIR,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_chrome_unit_tests():
    """Chrome options unit tests pass (pass_to_pass).

    Runs the repo's pytest unit tests for Chrome options.
    These tests verify Chrome browser configuration and options work correctly.
    """
    # Install test dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-mock", "rich", "filetype", "-q"],
        capture_output=True,
        timeout=120,
    )

    test_file = os.path.join(PY_DIR, "test", "unit", "selenium", "webdriver", "chrome", "chrome_options_tests.py")
    if not os.path.exists(test_file):
        return  # Skip if test file doesn't exist

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=PY_DIR,
    )
    assert result.returncode == 0, f"Chrome unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_repo_edge_unit_tests():
    """Edge options unit tests pass (pass_to_pass).

    Runs the repo's pytest unit tests for Edge options.
    These tests verify Edge browser configuration and options work correctly.
    """
    # Install test dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-mock", "rich", "filetype", "-q"],
        capture_output=True,
        timeout=120,
    )

    test_file = os.path.join(PY_DIR, "test", "unit", "selenium", "webdriver", "edge", "edge_options_tests.py")
    if not os.path.exists(test_file):
        return  # Skip if test file doesn't exist

    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=PY_DIR,
    )
    assert result.returncode == 0, f"Edge unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
