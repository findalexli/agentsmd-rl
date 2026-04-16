"""
Benchmark tests for superset-mcp-auth-valueerror-fallback task.

Tests verify behavior (not source text) of the MCP auth layer's ValueError
handler: it must propagate exceptions (fail-closed) instead of silently
falling back to g.user from middleware.
"""

import importlib.util
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, g

# Repository path
REPO = "/workspace/superset"
AUTH_FILE = os.path.join(REPO, "superset/mcp_service/auth.py")

# Import the auth module directly by file path to avoid pulling in
# the full superset package's heavy dependency tree (celery, etc.)
_spec = importlib.util.spec_from_file_location("auth", AUTH_FILE)
_auth = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_auth)


def test_valueerror_handler_removes_fallback_logic():
    """ValueError must propagate even when g.user is set by middleware (f2p).

    On the buggy base, the ValueError handler silently assigns user = g.user
    and breaks out of the retry loop. The fix must re-raise ValueError so
    the denied request is not authenticated as the middleware user.
    """
    app = Flask(__name__)
    with app.app_context():
        with app.test_request_context():
            middleware_user = MagicMock()
            middleware_user.username = "middleware_user"
            g.user = middleware_user

            with patch.object(_auth, "get_user_from_request",
                              side_effect=ValueError("user not found")):
                with pytest.raises(ValueError):
                    _auth._setup_user_context()


def test_valueerror_handler_clears_guser():
    """ValueError handler must clear g.user before re-raising (f2p).

    After user resolution fails with ValueError, the middleware-provided
    g.user must be cleared so error/audit logging does not attribute
    the denied request to the middleware identity.
    """
    app = Flask(__name__)
    with app.app_context():
        with app.test_request_context():
            middleware_user = MagicMock()
            middleware_user.username = "middleware_user"
            g.user = middleware_user

            with patch.object(_auth, "get_user_from_request",
                              side_effect=ValueError("user not found")):
                try:
                    _auth._setup_user_context()
                except ValueError:
                    pass

            assert g.get("user") is None, (
                "g.user must be cleared after ValueError in user resolution"
            )


def test_valueerror_handler_does_not_break():
    """ValueError handler must not silently succeed via break (f2p).

    On the buggy base, break exits the retry loop and the function
    returns successfully with the middleware user. The fix must raise
    ValueError instead of silently succeeding.
    """
    app = Flask(__name__)
    with app.app_context():
        with app.test_request_context():
            middleware_user = MagicMock()
            middleware_user.username = "middleware_user"
            g.user = middleware_user

            with patch.object(_auth, "get_user_from_request",
                              side_effect=ValueError("user not found")):
                raised = False
                try:
                    _auth._setup_user_context()
                except ValueError:
                    raised = True

                assert raised, (
                    "_setup_user_context must raise ValueError when user "
                    "resolution fails, not silently succeed via break"
                )


def test_valueerror_logs_error_not_warning():
    """ValueError handler must log at ERROR level, not WARNING (f2p).

    The buggy code logs at warning level about falling back. The fix must
    log at error level so monitoring and alerting systems properly surface
    the security-relevant denial.
    """
    app = Flask(__name__)
    with app.app_context():
        with app.test_request_context():
            middleware_user = MagicMock()
            middleware_user.username = "middleware_user"
            g.user = middleware_user

            with patch.object(_auth, "get_user_from_request",
                              side_effect=ValueError("user not found")):
                with patch.object(_auth.logger, "error") as mock_error:
                    try:
                        _auth._setup_user_context()
                    except ValueError:
                        pass

                    assert mock_error.called, (
                        "ValueError handler must call logger.error "
                        "(not logger.warning)"
                    )


def test_auth_module_syntax_valid():
    """Auth module has valid Python syntax (p2p)."""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", AUTH_FILE],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, (
        f"auth.py has syntax errors:\n{result.stderr}"
    )


def test_cleanup_session_called_on_db_error():
    """_cleanup_session_on_error must be called before final raise on retry failure (f2p).

    When get_user_from_request raises OperationalError on both attempts,
    cleanup must happen on the retry (attempt 0) AND before the final
    re-raise (attempt 1). The buggy code only calls cleanup on retry.
    """
    from sqlalchemy.exc import OperationalError

    app = Flask(__name__)
    with app.app_context():
        db_error = OperationalError(
            "SELECT 1", {}, Exception("connection lost")
        )
        with patch.object(_auth, "get_user_from_request",
                          side_effect=db_error):
            with patch.object(_auth, "_cleanup_session_on_error") as mock_cleanup:
                with pytest.raises(OperationalError):
                    _auth._setup_user_context()

                assert mock_cleanup.call_count >= 2, (
                    f"_cleanup_session_on_error should be called at least "
                    f"twice (retry + final raise), got {mock_cleanup.call_count}"
                )


def test_repo_ruff_check():
    """Repo's ruff linter passes on auth.py (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "ruff"],
        capture_output=True,
        timeout=120
    )

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", AUTH_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"ruff check failed on {AUTH_FILE}:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_ruff_format():
    """Repo's ruff formatter check passes on auth.py (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "ruff"],
        capture_output=True,
        timeout=120
    )

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", AUTH_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, (
        f"ruff format check failed on {AUTH_FILE}:\n{result.stdout}\n{result.stderr}"
    )
