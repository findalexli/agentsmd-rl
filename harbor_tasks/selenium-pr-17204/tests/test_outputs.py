"""
Tests for Selenium Service log_output ownership fix.
PR: SeleniumHQ/selenium#17204
"""

import os
import sys
import subprocess
import tempfile
from io import StringIO, BytesIO

# Add the selenium package to path
sys.path.insert(0, "/workspace/selenium/py")

from selenium.webdriver.common.service import Service


class ConcreteService(Service):
    """Concrete implementation of Service for testing."""

    def command_line_args(self):
        return []


def create_service_with_stream(stream):
    """Create a service with an external stream, bypassing process creation."""
    service = ConcreteService.__new__(ConcreteService)
    # Initialize minimal attributes
    service._owns_log_output = getattr(service, '_owns_log_output', False)
    service.log_output = stream
    service.process = None  # Skip process termination in stop()
    return service


# =============================================================================
# FAIL-TO-PASS TESTS
# These tests fail on the base commit and pass after the fix
# =============================================================================

def test_external_stringio_not_closed_after_stop():
    """External StringIO stream should not be closed by Service.stop().

    Bug: Service.stop() closes ANY IOBase stream, even externally-provided ones.
    Fix: Only close streams that the Service opened itself (file path strings).
    """
    external_stream = StringIO()
    external_stream.write("test data")

    service = create_service_with_stream(external_stream)
    service.stop()

    # The stream should still be open and usable
    assert not external_stream.closed, "External StringIO was incorrectly closed by stop()"

    # Verify we can still write to it
    external_stream.write(" more data")
    assert external_stream.getvalue() == "test data more data"


def test_external_bytesio_not_closed_after_stop():
    """External BytesIO stream should not be closed by Service.stop()."""
    external_stream = BytesIO()
    external_stream.write(b"test bytes")

    service = create_service_with_stream(external_stream)
    service.stop()

    # The stream should still be open and usable
    assert not external_stream.closed, "External BytesIO was incorrectly closed by stop()"

    # Verify we can still write to it
    external_stream.write(b" more bytes")
    external_stream.seek(0)
    assert external_stream.read() == b"test bytes more bytes"


def test_sequential_services_with_shared_stream():
    """Multiple sequential services should be able to share the same stream.

    This is the core issue from #15629: when using sys.stdout or another shared
    stream for logging, the first service closes it, breaking subsequent services.
    """
    shared_stream = StringIO()

    # First service
    service1 = create_service_with_stream(shared_stream)
    shared_stream.write("service1 log\n")
    service1.stop()

    # Stream should still be usable
    assert not shared_stream.closed, "Stream was closed after first service stop"

    # Second service should work with same stream
    service2 = create_service_with_stream(shared_stream)
    shared_stream.write("service2 log\n")
    service2.stop()

    # Stream should still be open
    assert not shared_stream.closed, "Stream was closed after second service stop"

    # Verify all data is there
    assert shared_stream.getvalue() == "service1 log\nservice2 log\n"


def test_owns_log_output_false_for_external_stream():
    """Service should NOT own externally-provided streams.

    The fix introduces _owns_log_output flag that should be False when
    an external stream is provided.
    """
    external_stream = StringIO()

    # Create service properly through __init__
    service = ConcreteService(log_output=external_stream)

    # Check the ownership flag exists and is False
    assert hasattr(service, '_owns_log_output'), "_owns_log_output attribute missing"
    assert service._owns_log_output is False, "_owns_log_output should be False for external streams"


def test_owns_log_output_true_for_file_path():
    """Service should own streams it creates from file paths.

    When log_output is a string path, Service opens the file itself
    and should own (and close) that stream.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_path = f.name

    try:
        service = ConcreteService(log_output=temp_path)

        # Check the ownership flag exists and is True
        assert hasattr(service, '_owns_log_output'), "_owns_log_output attribute missing"
        assert service._owns_log_output is True, "_owns_log_output should be True for file paths"

        # Clean up
        service.process = None
        service.stop()
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


# =============================================================================
# PASS-TO-PASS TESTS
# These tests should pass on both base and fixed commits
# =============================================================================

def test_file_path_stream_properly_closed():
    """When log_output is a file path, the opened file should be closed by stop().

    This is existing correct behavior that must be preserved.
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_path = f.name

    try:
        service = ConcreteService(log_output=temp_path)
        log_stream = service.log_output

        # The file should be open initially
        assert not log_stream.closed, "Log file should be open after service creation"

        # Stop the service
        service.process = None
        service.stop()

        # The file should now be closed (service owns it)
        assert log_stream.closed, "Log file should be closed after stop() for file paths"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_devnull_log_output_no_error():
    """Using subprocess.DEVNULL for log_output should not cause errors."""
    service = ConcreteService(log_output=subprocess.DEVNULL)

    assert service.log_output == subprocess.DEVNULL

    # Stop should not raise
    service.process = None
    service.stop()


def test_none_log_output_defaults_to_devnull():
    """None log_output should default to subprocess.DEVNULL."""
    service = ConcreteService(log_output=None)

    assert service.log_output == subprocess.DEVNULL


def test_service_import():
    """Verify the Service class can be imported correctly."""
    from selenium.webdriver.common.service import Service
    assert Service is not None
    assert hasattr(Service, 'stop')
    assert hasattr(Service, 'start')


# =============================================================================
# REPO CI TESTS (pass_to_pass)
# These run actual repo CI commands via subprocess
# =============================================================================

REPO = "/workspace/selenium"


def test_repo_ruff_lint():
    """Repo's ruff linter passes on service.py (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "pip install -q ruff && cd py && ruff check selenium/webdriver/common/service.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on service.py (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "pip install -q ruff && cd py && ruff format --check selenium/webdriver/common/service.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_mypy_service():
    """Mypy type check passes on service.py (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "pip install -q mypy && cd py && python -m mypy selenium/webdriver/common/service.py --ignore-missing-imports"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"mypy check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_unit_firefox_service():
    """Firefox service unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "test/unit/selenium/webdriver/firefox/firefox_service_tests.py", "-v", "--noconftest"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/py",
    )
    assert r.returncode == 0, f"Firefox service unit tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_unit_common_options():
    """Common options unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "test/unit/selenium/webdriver/common/common_options_tests.py", "-v", "--noconftest"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/py",
    )
    assert r.returncode == 0, f"Common options unit tests failed:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
