"""
Tests for credential leak fix in callback event logging.

This PR fixes a vulnerability where callback processors logged full Event objects
(including API keys in plaintext) to production logs.

The fix introduces `redact_text_secrets()` to redact sensitive information before logging.
"""

import sys
import os
import subprocess
import logging
import re
import asyncio
import io
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock

# Add the repo to path
REPO = "/workspace/OpenHands"
sys.path.insert(0, REPO)


# -----------------------------------------------------------------------------
# Fail-to-pass tests: These should FAIL on base commit, PASS after fix
# -----------------------------------------------------------------------------

def test_redact_text_secrets_exists():
    """The redact_text_secrets function must exist in the new module."""
    try:
        from openhands.utils._redact_compat import redact_text_secrets
        assert callable(redact_text_secrets), "redact_text_secrets must be callable"
    except ImportError:
        raise AssertionError("openhands.utils._redact_compat module does not exist")


def test_redact_api_keys_in_text():
    """API keys must be redacted from text containing them."""
    from openhands.utils._redact_compat import redact_text_secrets

    test_cases = [
        # (input, expected_pattern) - pattern to check after redaction
        ("api_key='sk-abc123secret'", "api_key='<redacted>'"),
        ('api_key="Bearer token123"', 'api_key="<redacted>"'),
        # gsk_ needs 20+ chars: gsk_[A-Za-z0-9]{20,}
        ("My API key is gsk_abc123def456ghi789jkl here", "<redacted>"),
        # sk-or-v1- needs 20+ chars after hyphen
        ("sk-or-v1-abc123def456ghi789jkl sensitive data", "<redacted>"),
    ]

    for text, expected_substring in test_cases:
        result = redact_text_secrets(text)
        assert expected_substring in result, \
            f"Expected '{expected_substring}' in redacted text, got: {result}"


def test_redact_sensitive_dict_entries():
    """Dict entries with sensitive keys must be redacted."""
    from openhands.utils._redact_compat import redact_text_secrets

    text = "{'API_KEY': 'secret123', 'OTHER': 'visible'}"
    result = redact_text_secrets(text)
    assert "<redacted>" in result, f"Sensitive dict value should be redacted, got: {result}"
    assert "visible" in result, f"Non-sensitive value should remain, got: {result}"


def test_redact_url_query_params():
    """Sensitive URL query parameters must be redacted."""
    from openhands.utils._redact_compat import redact_text_secrets

    urls = [
        # Check for api_key pattern (included in the regex patterns)
        ("https://example.com?api_key=secret123", "api_key=<redacted>"),
        # token is in SENSITIVE_URL_PARAMS
        ("https://example.com?token=secrettoken", "token=<redacted>"),
        # Check secret is redacted
        ("https://example.com?secret=secretvalue", "secret=<redacted>"),
    ]

    for url, expected in urls:
        result = redact_text_secrets(url)
        assert expected in result, f"Expected '{expected}' in {result}"


def test_event_callback_logging_uses_redaction():
    """LoggingCallbackProcessor logging must redact secrets from events.

    This is a behavioral test: we call the actual processor with a mock event
    containing a secret, capture the log output, and verify the secret is redacted.
    """
    from openhands.app_server.event_callback.event_callback_models import (
        LoggingCallbackProcessor,
    )

    # Capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    logger = logging.getLogger("openhands.app_server.event_callback.event_callback_models")
    logger.addHandler(handler)
    original_level = logger.level
    logger.setLevel(logging.INFO)

    try:
        # Create a mock event whose string representation contains a secret API key
        secret_key = "gsk_abc123def456ghi789jkl012mno"
        mock_event = Mock()
        mock_event.id = str(uuid4())
        mock_event.__str__ = lambda self: f"MessageEvent(content='secret: {secret_key}')"

        # Create a mock callback with valid UUID id
        mock_callback = Mock()
        mock_callback.id = str(uuid4())

        # Use LoggingCallbackProcessor which has the actual implementation
        processor = LoggingCallbackProcessor()

        # Run the async processor synchronously
        # Note: May fail with ValidationError after logging due to mock limitations
        conversation_id = uuid4()
        try:
            asyncio.run(processor(conversation_id, mock_callback, mock_event))
        except Exception:
            # Ignore exceptions after logging - we only care about the log content
            pass

        # Check that the logged output has the secret REDACTED
        log_output = log_stream.getvalue()
        assert secret_key not in log_output, (
            f"Secret API key '{secret_key}' should NOT appear in logs. "
            f"Got: {log_output}"
        )
        assert "<redacted>" in log_output, (
            f"Expected '<redacted>' to appear in logs. Got: {log_output}"
        )
    finally:
        logger.removeHandler(handler)
        handler.close()
        logger.setLevel(original_level)


def test_set_title_callback_logging_uses_redaction():
    """SetTitleCallbackProcessor logging must redact secrets from events.

    This is a behavioral test: we call the actual processor with a mock event
    containing a secret, capture the log output, and verify the secret is redacted.
    """
    from openhands.app_server.event_callback.set_title_callback_processor import (
        SetTitleCallbackProcessor,
    )
    from openhands.sdk import MessageEvent, Message

    # Capture log output
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    logger = logging.getLogger("openhands.app_server.event_callback.set_title_callback_processor")
    logger.addHandler(handler)
    original_level = logger.level
    logger.setLevel(logging.INFO)

    try:
        # Create a real MessageEvent (SetTitleCallbackProcessor checks isinstance)
        secret_key = "sk-or-v1-abc123def456ghi789jkl012mno"
        msg = Message(role='user', content=f'API key: {secret_key}')
        event = MessageEvent(
            id=str(uuid4()),
            timestamp='2024-01-01T00:00:00',
            source='user',
            llm_message=msg,
            llm_response_id='resp-123',
        )

        # Create a mock callback
        mock_callback = Mock()
        mock_callback.id = "test-title-callback-456"

        # Instantiate the processor
        processor = SetTitleCallbackProcessor()

        # Run the async processor synchronously
        # Note: The processor may fail with DockerException after logging due to
        # missing Docker daemon in test environment, but we only care about the log
        conversation_id = uuid4()
        try:
            asyncio.run(processor(conversation_id, mock_callback, event))
        except Exception:
            # Ignore exceptions after logging - we only care about the log content
            pass

        # Check that the logged output has the secret REDACTED
        log_output = log_stream.getvalue()
        assert secret_key not in log_output, (
            f"Secret API key '{secret_key}' should NOT appear in logs. "
            f"Got: {log_output}"
        )
        assert "<redacted>" in log_output, (
            f"Expected '<redacted>' to appear in logs. Got: {log_output}"
        )
    finally:
        logger.removeHandler(handler)
        handler.close()
        logger.setLevel(original_level)


def test_redact_api_key_literals_patterns():
    """Specific API key patterns must be redacted."""
    from openhands.utils._redact_compat import redact_api_key_literals

    # API key patterns require minimum character counts as per the regex
    api_keys = [
        # sk-or-v1- needs 20+ chars after hyphen
        "sk-or-v1-abc123def456ghi789jkl",
        # sk-proj- needs 20+ chars after hyphen (part of same regex group)
        "sk-proj-abc123def456ghi789jkl012mno345pq",
        # gsk_ needs 20+ chars
        "gsk_abc123def456ghi789jkl012mno",
        # hf_ needs 20+ chars
        "hf_abc123def456ghi789jkl012mno",
        # ghp_ needs 20+ chars
        "ghp_abc123def456ghi789jkl012mno",
    ]

    for key in api_keys:
        text = f"My key is {key} please use it"
        result = redact_api_key_literals(text)
        assert key not in result, f"API key {key} should be redacted, got: {result}"
        assert "<redacted>" in result, f"Expected '<redacted>' in result, got: {result}"


# -----------------------------------------------------------------------------
# Pass-to-pass tests: These should PASS on both base and fixed commits
# -----------------------------------------------------------------------------

# Note: test_non_sensitive_text_unchanged removed because it imports from
# openhands.utils._redact_compat which doesn't exist on the base commit.
# It would fail as a p2p test. The f2p tests already cover redaction behavior.


def test_repo_structure_intact():
    """The repository structure must be intact (pass_to_pass)."""
    assert os.path.exists(f"{REPO}/openhands"), "openhands directory must exist"
    assert os.path.exists(f"{REPO}/pyproject.toml"), "pyproject.toml must exist"


def test_python_syntax_valid():
    """Python files must have valid syntax (pass_to_pass)."""
    import py_compile

    files = [
        f"{REPO}/openhands/app_server/event_callback/event_callback_models.py",
        f"{REPO}/openhands/app_server/event_callback/set_title_callback_processor.py",
    ]

    for filepath in files:
        if os.path.exists(filepath):
            py_compile.compile(filepath, doraise=True)


def test_repo_utils_unit_tests():
    """Repo's utils unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/utils/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Utils unit tests failed:\n{r.stderr[-500:]}"


def test_repo_app_server_models():
    """Repo's app_server models test passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/app_server/test_models.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"App server models test failed:\n{r.stderr[-500:]}"


def test_repo_pytest_collection():
    """Repo's pytest can collect tests without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/unit/", "--collect-only", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Exit code 0 means collection succeeded, 5 means no tests collected (also ok)
    assert r.returncode in [0, 5], f"Pytest collection failed:\n{r.stderr[-500:]}"
    # Should have collected some tests
    assert "test session starts" in r.stdout or "no tests" in r.stderr or "collected" in r.stdout, \
        f"Unexpected pytest output:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    # Run all tests
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])