"""Tests for ensuring logging is configured on remote task workers."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/prefect")
SRC = REPO / "src"


def test_ensure_logging_setup_exists():
    """Test that ensure_logging_setup function exists and is importable."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

# First check if the function exists in configuration module
from prefect.logging.configuration import PROCESS_LOGGING_CONFIG, setup_logging

# Try to import the new function
try:
    from prefect.logging.configuration import ensure_logging_setup
    print("SUCCESS: ensure_logging_setup imported successfully")
except ImportError as e:
    print(f"FAIL: Cannot import ensure_logging_setup: {e}")
    sys.exit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "SUCCESS: ensure_logging_setup imported successfully" in result.stdout


def test_ensure_logging_setup_is_idempotent():
    """Test that ensure_logging_setup can be called multiple times without error."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

from prefect.logging.configuration import ensure_logging_setup, PROCESS_LOGGING_CONFIG

# Clear any existing config to simulate fresh process
PROCESS_LOGGING_CONFIG.clear()

# First call should set up logging
try:
    ensure_logging_setup()
    print("First call succeeded")
except Exception as e:
    print(f"FAIL: First call failed: {e}")
    sys.exit(1)

# Subsequent calls should be no-ops (no error)
try:
    ensure_logging_setup()
    ensure_logging_setup()
    ensure_logging_setup()
    print("Subsequent calls succeeded")
except Exception as e:
    print(f"FAIL: Subsequent calls failed: {e}")
    sys.exit(1)

print("idempotent test passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "idempotent test passed" in result.stdout


def test_ensure_logging_setup_called_from_context():
    """Test that ensure_logging_setup is called from hydrated_context when serialized_context is present."""
    # Check that context.py imports ensure_logging_setup
    context_file = REPO / "src" / "prefect" / "context.py"
    content = context_file.read_text()

    has_import = "from prefect.logging.configuration import ensure_logging_setup" in content
    has_call = "ensure_logging_setup()" in content

    assert has_import, "context.py should import ensure_logging_setup"
    assert has_call, "context.py should call ensure_logging_setup()"


def test_ensure_logging_setup_skips_when_already_configured():
    """Test that ensure_logging_setup doesn't reconfigure if already configured."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

from prefect.logging.configuration import ensure_logging_setup, PROCESS_LOGGING_CONFIG, setup_logging
import prefect.logging.configuration as lc

# Clear config
PROCESS_LOGGING_CONFIG.clear()

# Track calls
original_setup_logging = lc.setup_logging
call_count = [0]

def mock_setup_logging(*args, **kwargs):
    call_count[0] += 1
    return original_setup_logging(*args, **kwargs)

lc.setup_logging = mock_setup_logging

try:
    # First call should trigger setup_logging
    ensure_logging_setup()
    first_count = call_count[0]
    assert first_count == 1, f"Expected 1 call after first ensure_logging_setup, got {first_count}"

    # Second call should not trigger setup_logging
    ensure_logging_setup()
    second_count = call_count[0]
    assert second_count == 1, f"Expected still 1 call after second ensure_logging_setup, got {second_count}"

    print("skip_when_configured test passed")
finally:
    lc.setup_logging = original_setup_logging
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "skip_when_configured test passed" in result.stdout


def test_configuration_module_has_ensure_logging_setup():
    """Test that ensure_logging_setup is defined in configuration.py."""
    config_file = REPO / "src" / "prefect" / "logging" / "configuration.py"
    content = config_file.read_text()

    assert "def ensure_logging_setup()" in content, "configuration.py should define ensure_logging_setup function"


def test_ensure_logging_setup_has_docstring():
    """Test that ensure_logging_setup has proper docstring."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

from prefect.logging.configuration import ensure_logging_setup

doc = ensure_logging_setup.__doc__
assert doc is not None, "ensure_logging_setup should have a docstring"
assert "logging" in doc.lower(), "docstring should mention logging"
assert "remote" in doc.lower() or "dask" in doc.lower() or "ray" in doc.lower() or "worker" in doc.lower(), \
    "docstring should mention remote execution environments (Dask/Ray/workers)"

print("docstring test passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "docstring test passed" in result.stdout


def test_context_py_has_ensure_logging_import():
    """Test that context.py has the ensure_logging_setup import."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

# Verify the import statement exists
with open('/workspace/prefect/src/prefect/context.py') as f:
    content = f.read()

# Check for the import
assert "from prefect.logging.configuration import ensure_logging_setup" in content, \
    "context.py should import ensure_logging_setup from configuration"

# Check for the call within hydrated_context (in the serialized_context block)
assert "ensure_logging_setup()" in content, \
    "context.py should call ensure_logging_setup()"

print("context_import test passed")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "context_import test passed" in result.stdout


# =============================================================================
# Pass-to-Pass Tests (repo_tests) - CI checks that should pass at base commit
# =============================================================================


def test_ruff_lint_check():
    """Ruff lint check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/prefect/logging/configuration.py", "src/prefect/context.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_ruff_format_check():
    """Ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prefect/logging/configuration.py", "src/prefect/context.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_python_syntax_valid():
    """Python syntax is valid for modified files (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "src/prefect/logging/configuration.py", "src/prefect/context.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_logging_setup_idempotent():
    """Logging setup can be called multiple times without error (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

from prefect.logging.configuration import setup_logging

# First call
setup_logging()

# Second call should not error
setup_logging()

# Third call should not error
setup_logging()

print("setup_logging idempotent test passed")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "setup_logging idempotent test passed" in r.stdout


def test_load_logging_config_works():
    """Loading default logging config works (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

from prefect.logging.configuration import load_logging_config, DEFAULT_LOGGING_SETTINGS_PATH

config = load_logging_config(DEFAULT_LOGGING_SETTINGS_PATH)
assert "version" in config
assert config["version"] == 1
assert "handlers" in config
assert "loggers" in config

print("load_logging_config test passed")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "load_logging_config test passed" in r.stdout


def test_context_imports_work():
    """Context module imports work correctly (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/prefect/src')

from prefect.context import hydrated_context
from prefect.context import FlowRunContext, TaskRunContext
from prefect.logging.configuration import setup_logging, load_logging_config

print("context imports test passed")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "context imports test passed" in r.stdout
