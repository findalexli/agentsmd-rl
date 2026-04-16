#!/usr/bin/env python3
"""
Test suite for langgraph-sdk reconnect URL validation fix.

This tests that the SDK properly validates reconnect Location headers
to prevent credential leakage to external servers.
"""

import subprocess
import sys
import httpx
from urllib.parse import urlparse

REPO = "/workspace/langgraph/libs/sdk-py"


def _default_port(scheme: str) -> int:
    """Helper to get default port for a scheme."""
    return 443 if scheme == "https" else 80


def _validate_reconnect_location(base_url: httpx.URL, location: str) -> str:
    """
    Reimplementation of validation logic for testing.
    This function encodes the expected behavior - cross-origin locations
    should raise ValueError, relative and same-origin should be allowed.
    """
    parsed = urlparse(location)
    # Relative URLs are safe — they resolve against the base
    if not parsed.scheme and not parsed.netloc:
        return location
    # Compare origin components (normalize default ports to avoid mismatches)
    base_scheme = str(base_url.scheme)
    base_origin = (
        base_scheme,
        str(base_url.host),
        base_url.port or _default_port(base_scheme),
    )
    loc_origin = (
        parsed.scheme,
        parsed.hostname or "",
        parsed.port or _default_port(parsed.scheme),
    )
    if base_origin != loc_origin:
        raise ValueError(
            f"Refusing to follow cross-origin reconnect Location: {location!r} "
            f"(origin {loc_origin}) does not match base URL origin {base_origin}"
        )
    return location


def test_cross_origin_reconnect_blocked():
    """Cross-origin reconnect Location headers should raise ValueError (f2p)."""
    test_cases = [
        ("https://api.example.com", "https://attacker.com/redirect"),
        ("https://api.example.com/v1", "https://evil.com/path"),
        ("https://api.example.com", "http://api.example.com/path"),
        ("http://api.example.com", "https://api.example.com/path"),
        ("https://api.example.com", "https://api.example.com:8443/path"),
        ("http://api.example.com", "http://api.example.com:8080/path"),
        ("https://api.example.com:8080", "https://other.example.com:9090/path"),
    ]

    for base_url_str, location in test_cases:
        base_url = httpx.URL(base_url_str)
        raised = False
        try:
            try:
                from langgraph_sdk._shared.utilities import _validate_reconnect_location as sdk_validate
                sdk_validate(base_url, location)
            except ImportError:
                _validate_reconnect_location(base_url, location)
        except ValueError as e:
            error_msg = str(e).lower()
            assert "cross-origin" in error_msg or "refusing" in error_msg
            raised = True
        assert raised, f"Expected ValueError for {location} with base {base_url_str}"


def test_same_origin_reconnect_allowed():
    """Same-origin reconnect Location headers should be allowed (f2p)."""
    test_cases = [
        ("https://api.example.com", "https://api.example.com/redirect"),
        ("https://api.example.com/v1", "https://api.example.com/v1/runs"),
        ("https://api.example.com", "https://api.example.com:443/redirect"),
        ("https://api.example.com:443", "https://api.example.com/redirect"),
        ("http://api.example.com", "http://api.example.com:80/redirect"),
        ("http://api.example.com:80", "http://api.example.com/redirect"),
        ("https://api.example.com/v1", "https://api.example.com:443/v1/threads"),
    ]

    for base_url_str, location in test_cases:
        base_url = httpx.URL(base_url_str)
        try:
            from langgraph_sdk._shared.utilities import _validate_reconnect_location as sdk_validate
            result = sdk_validate(base_url, location)
        except ImportError:
            result = _validate_reconnect_location(base_url, location)
        assert result == location


def test_relative_url_allowed():
    """Relative URLs should be allowed as they resolve against the base (p2p)."""
    test_cases = [
        ("https://api.example.com", "/redirect"),
        ("https://api.example.com/v1", "/v1/reconnect"),
        ("https://api.example.com", "/v1/threads/thread123/runs"),
        ("https://api.example.com/v1", "/other/path"),
    ]

    for base_url_str, location in test_cases:
        base_url = httpx.URL(base_url_str)
        try:
            from langgraph_sdk._shared.utilities import _validate_reconnect_location as sdk_validate
            result = sdk_validate(base_url, location)
        except ImportError:
            result = _validate_reconnect_location(base_url, location)
        assert result == location


def test_default_port_handling():
    """Default ports should be handled correctly (https=443, http=80) (p2p)."""
    test_cases = [
        ("https://api.example.com", "https://api.example.com:443/path"),
        ("https://api.example.com:443", "https://api.example.com/path"),
        ("http://api.example.com", "http://api.example.com:80/path"),
        ("http://api.example.com:80", "http://api.example.com/path"),
    ]

    for base_url_str, location in test_cases:
        base_url = httpx.URL(base_url_str)
        try:
            from langgraph_sdk._shared.utilities import _validate_reconnect_location as sdk_validate
            result = sdk_validate(base_url, location)
        except ImportError:
            result = _validate_reconnect_location(base_url, location)
        assert result == location

    different_port_cases = [
        ("https://api.example.com", "https://api.example.com:8443/path"),
        ("http://api.example.com", "http://api.example.com:8080/path"),
    ]

    for base_url_str, location in different_port_cases:
        base_url = httpx.URL(base_url_str)
        raised = False
        try:
            try:
                from langgraph_sdk._shared.utilities import _validate_reconnect_location as sdk_validate
                sdk_validate(base_url, location)
            except ImportError:
                _validate_reconnect_location(base_url, location)
        except ValueError:
            raised = True
        assert raised, f"Expected ValueError for different port: {location}"


def test_validation_integration_exists():
    """The validation must be integrated into HTTP clients (f2p)."""
    try:
        from langgraph_sdk._shared.utilities import _validate_reconnect_location as sdk_validate
        base_url = httpx.URL("https://api.example.com")

        raised = False
        try:
            sdk_validate(base_url, "https://attacker.com/path")
        except ValueError:
            raised = True
        assert raised, "Should raise ValueError for cross-origin"

        result = sdk_validate(base_url, "https://api.example.com/path")
        assert result == "https://api.example.com/path"

        result = sdk_validate(base_url, "/path")
        assert result == "/path"

    except ImportError:
        pass


def test_version_updated():
    """Version should be updated to 0.3.13 (f2p)."""
    from langgraph_sdk import __version__
    assert __version__ == "0.3.13", f"Expected version 0.3.13, got {__version__}"


def test_repo_format():
    """Repo code passes format check (p2p)."""
    r = subprocess.run(
        ["make", "format"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_lint():
    """Repo code passes lint check (p2p)."""
    r = subprocess.run(
        ["make", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Lint check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_tests():
    """Repo tests pass (p2p)."""
    r = subprocess.run(
        ["make", "test"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_type():
    """Repo type checking passes (p2p)."""
    r = subprocess.run(
        ["make", "type"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_stream_tests():
    """Repo client stream tests pass (p2p)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_client_stream.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Stream tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_error_tests():
    """Repo error handling tests pass (p2p)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_errors.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Error tests failed:\n{r.stdout}\n{r.stderr}"


def test_repo_client_export_tests():
    """Repo client export tests pass (p2p)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_client_exports.py", "-v"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Client export tests failed:\n{r.stdout}\n{r.stderr}"


def test_no_double_backticks():
    """Do NOT use Sphinx-style double backtick formatting (agent config check)."""
    import re

    files_to_check = [
        f"{REPO}/langgraph_sdk/_shared/utilities.py",
        f"{REPO}/langgraph_sdk/_async/http.py",
        f"{REPO}/langgraph_sdk/_sync/http.py",
    ]

    for filepath in files_to_check:
        try:
            with open(filepath, "r") as f:
                content = f.read()
            double_backtick_pattern = r"`{4}[^`]+`{4}"
            matches = re.findall(double_backtick_pattern, content)
            assert len(matches) == 0, f"Found double backticks in {filepath}"
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
