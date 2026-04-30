"""Oracle tests for apache/airflow PR #65509.

These tests verify the OpenSearch task-log handler no longer leaks
``user:password@`` credentials embedded in the ``[opensearch] host`` config
when it is used as the log-source label fallback.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")
HANDLER_REL = "providers/opensearch/src/airflow/providers/opensearch/log/os_task_handler.py"
HANDLER = REPO / HANDLER_REL


# ---------------------------------------------------------------------------
# Behavioral fail-to-pass tests
# ---------------------------------------------------------------------------

STRIP_USERINFO_CASES = [
    # (input host URL, expected stripped output)
    ("https://user:pass@opensearch.example.com:9200", "https://opensearch.example.com:9200"),
    ("http://USER:PASS@opensearch.example.com", "http://opensearch.example.com"),
    ("https://opensearch.example.com:9200", "https://opensearch.example.com:9200"),
    ("http://localhost:9200", "http://localhost:9200"),
    ("https://user@opensearch.example.com", "https://opensearch.example.com"),
    ("not-a-url", "not-a-url"),
    ("", ""),
    # Extra cases agents will not have memorized from upstream test fixtures.
    ("https://admin:secret123@logs.internal:443/", "https://logs.internal:443/"),
    ("http://u:p@127.0.0.1:9200", "http://127.0.0.1:9200"),
]


@pytest.mark.parametrize(("url", "expected"), STRIP_USERINFO_CASES)
def test_strip_userinfo_returns_redacted_url(url, expected):
    """Helper exists in os_task_handler and removes userinfo without changing the rest of the URL."""
    from airflow.providers.opensearch.log import os_task_handler as mod

    helper = getattr(mod, "_strip_userinfo", None)
    assert callable(helper), (
        "Expected a module-level URL-redaction helper in os_task_handler "
        "(such as `_strip_userinfo`) but it is missing."
    )
    assert helper(url) == expected


def test_strip_userinfo_drops_password_without_username():
    """A password-only userinfo (rare but legal) is also stripped."""
    from airflow.providers.opensearch.log import os_task_handler as mod

    helper = getattr(mod, "_strip_userinfo", None)
    assert callable(helper)
    assert helper("https://:secret@opensearch.example.com") == "https://opensearch.example.com"


def test_task_handler_group_logs_by_host_strips_credentials():
    """OpensearchTaskHandler._group_logs_by_host must not leak user:password in fallback key."""
    script = textwrap.dedent(
        """
        import sys
        from collections import defaultdict
        from airflow.providers.opensearch.log.os_task_handler import OpensearchTaskHandler

        # Construct a bare instance without running __init__ (which needs a live cluster).
        h = OpensearchTaskHandler.__new__(OpensearchTaskHandler)
        h.host = "https://elastic:supersecret@opensearch.example.com:9200"
        h.host_field = "host"

        class _FakeHit:
            def __getitem__(self, k):
                raise KeyError(k)

        # Iterating the response yields hits; each hit carries no host attribute,
        # so the fallback (the configured host URL) is used as the dict key.
        response = [_FakeHit(), _FakeHit()]
        grouped = h._group_logs_by_host(response)

        keys = list(grouped.keys())
        assert len(keys) == 1, f"expected exactly one fallback key, got {keys!r}"
        key = keys[0]
        assert "supersecret" not in key, f"password leaked into log-source key: {key!r}"
        assert "elastic:" not in key, f"username:password leaked into log-source key: {key!r}"
        assert "opensearch.example.com" in key, f"hostname missing from key: {key!r}"
        print("OK", key)
        """
    )
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        "OpensearchTaskHandler._group_logs_by_host still leaks credentials.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_remote_log_io_group_logs_by_host_strips_credentials():
    """OpensearchRemoteLogIO._group_logs_by_host must also redact credentials in fallback key."""
    script = textwrap.dedent(
        """
        from airflow.providers.opensearch.log.os_task_handler import OpensearchRemoteLogIO

        h = OpensearchRemoteLogIO.__new__(OpensearchRemoteLogIO)
        h.host = "https://elastic:topsecret@opensearch.example.com:9200"
        h.host_field = "host"

        class _FakeHit:
            def __getitem__(self, k):
                raise KeyError(k)

        response = [_FakeHit()]
        grouped = h._group_logs_by_host(response)

        keys = list(grouped.keys())
        assert len(keys) == 1, f"expected exactly one fallback key, got {keys!r}"
        key = keys[0]
        assert "topsecret" not in key, f"password leaked: {key!r}"
        assert "elastic:" not in key, f"credentials leaked: {key!r}"
        assert "opensearch.example.com" in key
        print("OK", key)
        """
    )
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        "OpensearchRemoteLogIO._group_logs_by_host still leaks credentials.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_clean_host_passes_through_unchanged():
    """When host has no userinfo, _group_logs_by_host's fallback equals the configured host."""
    script = textwrap.dedent(
        """
        from airflow.providers.opensearch.log.os_task_handler import OpensearchTaskHandler

        h = OpensearchTaskHandler.__new__(OpensearchTaskHandler)
        h.host = "https://opensearch.example.com:9200"
        h.host_field = "host"

        class _FakeHit:
            def __getitem__(self, k):
                raise KeyError(k)

        grouped = h._group_logs_by_host([_FakeHit()])
        keys = list(grouped.keys())
        assert keys == ["https://opensearch.example.com:9200"], f"clean host changed: {keys!r}"
        print("OK")
        """
    )
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"Clean host passthrough failed.\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass repo CI checks
# ---------------------------------------------------------------------------


def test_handler_module_imports_cleanly():
    """The patched module continues to import (catches typos / accidental syntax errors)."""
    r = subprocess.run(
        [sys.executable, "-c", "import airflow.providers.opensearch.log.os_task_handler"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"os_task_handler import broken.\nstderr:\n{r.stderr}"
    )


def test_ruff_check_handler_file():
    """The repo's lint config (ruff) must pass on the modified handler file."""
    r = subprocess.run(
        ["ruff", "check", HANDLER_REL],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"ruff check failed on {HANDLER_REL}:\n{r.stdout}\n{r.stderr}"
    )


def test_ruff_format_handler_file():
    """The repo's formatter (ruff format --check) must pass on the modified handler file."""
    r = subprocess.run(
        ["ruff", "format", "--check", HANDLER_REL],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"ruff format --check failed on {HANDLER_REL}:\n{r.stdout}\n{r.stderr}"
    )
