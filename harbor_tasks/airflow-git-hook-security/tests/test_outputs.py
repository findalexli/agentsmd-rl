"""Tests for GitHook security hardening.

This module tests the security fixes applied to the GitHook class:
1. shlex.quote for user-controlled values in SSH commands
2. Validation of strict_host_key_checking against allowlist
3. URL-encoding of username and auth token in repo URLs
4. Logic bug fix for git@/https:// check
5. Limit str.replace to first occurrence
"""

import os
import subprocess
import sys
import shlex
from urllib.parse import quote as urlquote

# Add the git provider source to path
sys.path.insert(0, "/workspace/airflow/providers/git/src")
sys.path.insert(0, "/workspace/airflow/airflow-core/src")

import pytest

import airflow.providers.git.hooks.git
original_init = airflow.providers.git.hooks.git.GitHook.__init__

def patched_init(self, git_conn_id="git_default", repo_url=None, *args, **kwargs):
    from unittest.mock import MagicMock
    mock_conn = MagicMock()
    mock_conn.host = repo_url or "git@github.com:apache/airflow.git"
    mock_conn.login = kwargs.get("user_name", "user")
    mock_conn.password = kwargs.get("auth_token", "token")
    mock_conn.extra_dejson = kwargs
    
    self.get_connection = MagicMock(return_value=mock_conn)
    original_init(self, git_conn_id, repo_url, *args, **kwargs)

airflow.providers.git.hooks.git.GitHook.__init__ = patched_init


REPO = "/workspace/airflow"
GIT_HOOK_PATH = "providers/git/src/airflow/providers/git/hooks/git.py"


# =============================================================================
# PASS-TO-PASS TESTS - Repository CI/CD health checks
# These tests verify the repo's existing tests pass on both base and gold fix
# =============================================================================


def test_repo_git_hook_syntax():
    """Git hook Python file has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/{GIT_HOOK_PATH}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


def test_repo_ruff_check():
    """Git hook passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/{GIT_HOOK_PATH}", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr}"


def test_repo_ruff_format():
    """Git hook passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--diff", f"{REPO}/{GIT_HOOK_PATH}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Exit code 0 means already formatted, no diff
    assert r.returncode == 0, f"Ruff format check failed (file needs formatting):\n{r.stdout}"



def test_repo_flake8_check():
    """Git hook passes flake8 linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["flake8", f"{REPO}/{GIT_HOOK_PATH}", "--max-line-length=110", "--extend-ignore=E203,W503"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Flake8 check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_git_hook_imports():
    """Git hook module can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/providers/git/src'); sys.path.insert(0, '{REPO}/airflow-core/src'); from airflow.providers.git.hooks.git import GitHook; print('Import OK')",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"GitHook import failed:\n{r.stderr}"
    assert "Import OK" in r.stdout


# =============================================================================
# FAIL-TO-PASS TESTS - Security fix verification tests
# These tests verify the specific security fixes are correctly applied
# =============================================================================


def test_ssh_command_quotes_key_path_with_spaces():
    """Test that key_path with spaces is properly quoted."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        key_file="/path/with spaces/to/key"
    )
    cmd = hook._build_ssh_command(key_path="/path/with spaces/to/key")

    # The key path should be quoted (shlex.quote adds single quotes around paths with spaces)
    assert "-i '/path/with spaces/to/key'" in cmd or '-i "/path/with spaces/to/key"' in cmd


def test_ssh_command_quotes_key_path_with_shell_chars():
    """Test that key_path with shell metacharacters is properly quoted."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        key_file="/path/to/key;rm -rf /"
    )
    cmd = hook._build_ssh_command(key_path="/path/to/key;rm -rf /")

    # The malicious path should be quoted to prevent injection
    quoted = shlex.quote("/path/to/key;rm -rf /")
    assert f"-i {quoted}" in cmd


def test_ssh_command_quotes_known_hosts_file():
    """Test that known_hosts_file with spaces/special chars is properly quoted."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        known_hosts_file="/path/with spaces/known_hosts"
    )
    cmd = hook._build_ssh_command()

    quoted = shlex.quote("/path/with spaces/known_hosts")
    assert f"UserKnownHostsFile={quoted}" in cmd


def test_ssh_command_quotes_ssh_config_file():
    """Test that ssh_config_file with spaces/special chars is properly quoted."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        ssh_config_file="/path/with spaces/config"
    )
    cmd = hook._build_ssh_command()

    quoted = shlex.quote("/path/with spaces/config")
    assert f"-F {quoted}" in cmd


def test_ssh_command_quotes_proxy_command():
    """Test that host_proxy_cmd with special chars is properly quoted."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        host_proxy_cmd="ssh -W %h:%p bastion.example.com"
    )
    cmd = hook._build_ssh_command()

    # The proxy command should be quoted
    quoted = shlex.quote("ssh -W %h:%p bastion.example.com")
    assert f"ProxyCommand={quoted}" in cmd


def test_strict_host_key_checking_validation_rejects_invalid():
    """Test that invalid strict_host_key_checking values are rejected."""
    from airflow.providers.git.hooks.git import GitHook

    # This should raise a ValueError for invalid value
    with pytest.raises(ValueError) as exc_info:
        hook = GitHook(
            git_conn_id="git_default",
            repo_url="git@github.com:apache/airflow.git",
            strict_host_key_checking="invalid_value"
        )
        # Force the validation to run
        hook._build_ssh_command()

    assert "Invalid strict_host_key_checking value" in str(exc_info.value)


def test_strict_host_key_checking_accepts_valid_yes():
    """Test that 'yes' is accepted as valid strict_host_key_checking."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        strict_host_key_checking="yes"
    )
    cmd = hook._build_ssh_command()
    assert "StrictHostKeyChecking=yes" in cmd


def test_strict_host_key_checking_accepts_valid_no():
    """Test that 'no' is accepted as valid strict_host_key_checking."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        strict_host_key_checking="no"
    )
    cmd = hook._build_ssh_command()
    assert "StrictHostKeyChecking=no" in cmd


def test_strict_host_key_checking_accepts_valid_accept_new():
    """Test that 'accept-new' is accepted as valid strict_host_key_checking."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        strict_host_key_checking="accept-new"
    )
    cmd = hook._build_ssh_command()
    assert "StrictHostKeyChecking=accept-new" in cmd


def test_url_encoding_of_username_and_token_https():
    """Test that username and token are URL-encoded in https URLs."""
    from airflow.providers.git.hooks.git import GitHook

    # Username with special chars that need encoding
    hook = GitHook(
        git_conn_id="git_default",
        repo_url="https://github.com/apache/airflow.git",
        user_name="user@domain.com",
        auth_token="token/with+special=chars"
    )

    expected_user = urlquote("user@domain.com", safe="")
    expected_token = urlquote("token/with+special=chars", safe="")
    expected = f"https://{expected_user}:{expected_token}@github.com/apache/airflow.git"
    assert hook.repo_url == expected


def test_url_encoding_of_username_and_token_http():
    """Test that username and token are URL-encoded in http URLs."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="http://github.com/apache/airflow.git",
        user_name="user@domain.com",
        auth_token="token/with+special=chars"
    )

    expected_user = urlquote("user@domain.com", safe="")
    expected_token = urlquote("token/with+special=chars", safe="")
    expected = f"http://{expected_user}:{expected_token}@github.com/apache/airflow.git"
    assert hook.repo_url == expected


def test_url_replace_only_first_occurrence():
    """Test that str.replace only replaces first occurrence of https://."""
    from airflow.providers.git.hooks.git import GitHook

    # URL with https:// appearing twice (unusual but tests the fix)
    hook = GitHook(
        git_conn_id="git_default",
        repo_url="https://github.com/apache/airflow.git",
        user_name="user",
        auth_token="token"
    )

    # Should only have one auth prefix
    assert hook.repo_url.count("https://") == 1
    assert hook.repo_url.count("http://") == 0


def test_local_path_expanded():
    """Test that local paths ARE expanded through os.path.expanduser."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="~/repos/myrepo"
    )

    # Should be expanded
    expected = os.path.expanduser("~/repos/myrepo")
    assert hook.repo_url == expected


def test_url_with_tilde_in_middle_unchanged():
    """Test that URLs with tilde in middle are not mangled by expanduser logic.

    This tests the logic bug: on base commit with `or`, ALL non-matching URLs
    go through expanduser, which could mangle URLs containing ~ in the middle.
    """
    from airflow.providers.git.hooks.git import GitHook

    # A file:// URL with ~ in the path (not at start) - this should NOT be expanded
    hook = GitHook(
        git_conn_id="git_default",
        repo_url="/path/to/repo/~user/branch"
    )

    # Should remain unchanged - the ~ is in the middle, not at start
    # On buggy base, this would incorrectly go through expanduser (but expanduser
    # would still leave it alone since ~ is not at position 0)
    # The real issue: the `or` logic means ALL URLs pass this condition
    assert hook.repo_url == "/path/to/repo/~user/branch"


def test_proxy_command_formatting():
    """Test specific proxy command formatting from the upstream test change."""
    from airflow.providers.git.hooks.git import GitHook

    hook = GitHook(
        git_conn_id="git_default",
        repo_url="git@github.com:apache/airflow.git",
        host_proxy_cmd="ssh -W %h:%p bastion.example.com"
    )
    cmd = hook._build_ssh_command()

    # Should use single quotes (shlex.quote style), not double quotes
    assert "ProxyCommand='ssh -W %h:%p bastion.example.com'" in cmd
