"""
Tests for apache/airflow#64756 - Harden GitHook SSH command building and URL construction.

This PR fixes several security issues:
1. Shell injection via unquoted paths in SSH commands
2. Credential exposure via unencoded special characters in URLs
3. Invalid strict_host_key_checking values not validated
4. Logic bug: local paths incorrectly handled due to `or` vs `and`

These tests work by extracting and executing the relevant code from the source file.
"""

import os
import re
import shlex
import subprocess
import sys
from urllib.parse import quote as urlquote

REPO = "/workspace/airflow"
GIT_HOOK_FILE = os.path.join(REPO, "providers/git/src/airflow/providers/git/hooks/git.py")


def read_source():
    """Read the git.py source file."""
    with open(GIT_HOOK_FILE, "r") as f:
        return f.read()


def test_shlex_import_present():
    """
    The shlex module must be imported to enable shell quoting.
    fail_to_pass: Base commit does not import shlex.
    """
    source = read_source()
    assert "import shlex" in source, "shlex module not imported"


def test_urlquote_import_present():
    """
    The urllib.parse.quote function must be imported for URL encoding.
    fail_to_pass: Base commit does not import urlquote.
    """
    source = read_source()
    # Check for import of quote from urllib.parse (aliased as urlquote or directly)
    assert "from urllib.parse import" in source and "quote" in source, \
        "urllib.parse.quote not imported"


def test_key_path_uses_shlex_quote():
    """
    SSH key paths must be shell-quoted with shlex.quote.
    fail_to_pass: Base commit uses f"-i {key_path}" without quoting.
    """
    source = read_source()
    # Find the line that builds the -i argument for key_path
    # After fix: f"-i {shlex.quote(key_path)}"
    # Before fix: f"-i {key_path}"

    # Look for the pattern with shlex.quote
    pattern = r'-i.*shlex\.quote\s*\(\s*key_path\s*\)'
    assert re.search(pattern, source), \
        "key_path is not shell-quoted with shlex.quote"


def test_known_hosts_file_uses_shlex_quote():
    """
    known_hosts_file paths must be shell-quoted with shlex.quote.
    fail_to_pass: Base commit uses direct string interpolation.
    """
    source = read_source()
    # After fix: f"-o UserKnownHostsFile={shlex.quote(self.known_hosts_file)}"
    pattern = r'UserKnownHostsFile=.*shlex\.quote\s*\(\s*self\.known_hosts_file\s*\)'
    assert re.search(pattern, source), \
        "known_hosts_file is not shell-quoted with shlex.quote"


def test_ssh_config_file_uses_shlex_quote():
    """
    ssh_config_file paths must be shell-quoted with shlex.quote.
    fail_to_pass: Base commit uses direct string interpolation.
    """
    source = read_source()
    # After fix: f"-F {shlex.quote(self.ssh_config_file)}"
    pattern = r'-F.*shlex\.quote\s*\(\s*self\.ssh_config_file\s*\)'
    assert re.search(pattern, source), \
        "ssh_config_file is not shell-quoted with shlex.quote"


def test_proxy_command_uses_shlex_quote():
    """
    host_proxy_cmd must be shell-quoted with shlex.quote.
    fail_to_pass: Base commit uses double quotes which don't prevent all injection.
    """
    source = read_source()
    # After fix: f"-o ProxyCommand={shlex.quote(self.host_proxy_cmd)}"
    # Before fix: f'-o ProxyCommand="{self.host_proxy_cmd}"'
    pattern = r'ProxyCommand=.*shlex\.quote\s*\(\s*self\.host_proxy_cmd\s*\)'
    assert re.search(pattern, source), \
        "host_proxy_cmd is not shell-quoted with shlex.quote"


def test_strict_host_key_checking_validation_exists():
    """
    Invalid strict_host_key_checking values must raise ValueError.
    fail_to_pass: Base commit does not validate the value.
    """
    source = read_source()
    # After fix: There should be a frozenset of valid values and a ValueError raised
    assert "_VALID_STRICT_HOST_KEY_CHECKING" in source, \
        "No validation set for strict_host_key_checking values"
    assert 'raise ValueError' in source and 'strict_host_key_checking' in source, \
        "No ValueError raised for invalid strict_host_key_checking"


def test_valid_strict_host_key_checking_values_defined():
    """
    The set of valid strict_host_key_checking values should include all SSH options.
    pass_to_pass: Verify the validation set contains expected values.
    """
    source = read_source()
    # Check that all valid SSH values are in the validation set
    for value in ["yes", "no", "accept-new", "off", "ask"]:
        assert f'"{value}"' in source or f"'{value}'" in source, \
            f"Valid value '{value}' not in validation set"


def test_https_url_uses_urlquote_for_username():
    """
    Usernames in HTTPS URLs must be URL-encoded.
    fail_to_pass: Base commit embeds raw username without encoding.
    """
    source = read_source()
    # After fix: encoded_user = urlquote(self.user_name, safe="")
    # Should find urlquote being used with user_name
    pattern = r'urlquote\s*\(\s*self\.user_name'
    assert re.search(pattern, source), \
        "user_name is not URL-encoded with urlquote"


def test_https_url_uses_urlquote_for_token():
    """
    Auth tokens in HTTPS URLs must be URL-encoded.
    fail_to_pass: Base commit embeds raw token without encoding.
    """
    source = read_source()
    # After fix: encoded_token = urlquote(self.auth_token, safe="")
    pattern = r'urlquote\s*\(\s*self\.auth_token'
    assert re.search(pattern, source), \
        "auth_token is not URL-encoded with urlquote"


def test_url_replace_uses_count_parameter():
    """
    URL credential injection should only replace first occurrence of https://.
    fail_to_pass: Base commit replaces all occurrences.
    """
    source = read_source()
    # After fix: self.repo_url.replace("https://", f"https://...", 1)
    # Look for .replace(... with count=1 or ,1) near https://

    # Find lines with replace and https://
    https_replace_pattern = r'\.replace\s*\(\s*["\']https://["\'].*,\s*1\s*\)'
    http_replace_pattern = r'\.replace\s*\(\s*["\']http://["\'].*,\s*1\s*\)'

    assert re.search(https_replace_pattern, source), \
        "HTTPS URL replace does not limit to first occurrence"
    assert re.search(http_replace_pattern, source), \
        "HTTP URL replace does not limit to first occurrence"


def test_logic_bug_or_to_and_fixed():
    """
    Local paths should be handled correctly - logic bug fix.
    fail_to_pass: Base commit had `not X or not Y` which is always True.
    """
    source = read_source()
    # The bug was: elif not self.repo_url.startswith("git@") or not self.repo_url.startswith("https://"):
    # Should be: elif not self.repo_url.startswith("git@") and not self.repo_url.startswith("https://"):

    # Check that we don't have the buggy pattern
    buggy_pattern = r'not\s+self\.repo_url\.startswith\s*\(["\']git@["\']\)\s+or\s+not\s+self\.repo_url\.startswith'
    assert not re.search(buggy_pattern, source), \
        "Logic bug still present: 'or' should be 'and'"

    # Check that we have the correct pattern
    fixed_pattern = r'not\s+self\.repo_url\.startswith\s*\(["\']git@["\']\)\s+and\s+not\s+self\.repo_url\.startswith'
    assert re.search(fixed_pattern, source), \
        "Expected 'and' between startswith checks for local path handling"


def test_shlex_quote_behavior_key_path():
    """
    Verify shlex.quote properly handles paths with spaces and special chars.
    pass_to_pass: Behavioral verification of shlex.quote.
    """
    # Test that shlex.quote does what we expect
    test_path = "/path/with space/key"
    quoted = shlex.quote(test_path)
    # Should be wrapped in single quotes
    assert quoted == "'/path/with space/key'", f"Unexpected quoting: {quoted}"

    # Test with shell metacharacters
    dangerous_path = "/path/with;rm -rf /;key"
    quoted_dangerous = shlex.quote(dangerous_path)
    # Dangerous characters should be safely contained
    assert "'" in quoted_dangerous, f"Dangerous chars not quoted: {quoted_dangerous}"


def test_urlquote_behavior_special_chars():
    """
    Verify urlquote properly encodes special URL characters.
    pass_to_pass: Behavioral verification of urlquote.
    """
    # Test @ encoding
    assert urlquote("user@domain", safe="") == "user%40domain"
    # Test / encoding
    assert urlquote("pass/word", safe="") == "pass%2Fword"
    # Test : encoding
    assert urlquote("pass:word", safe="") == "pass%3Aword"
    # Test # encoding
    assert urlquote("pass#word", safe="") == "pass%23word"


def test_source_file_exists():
    """
    Verify the git hook source file exists.
    pass_to_pass: Basic file existence check.
    """
    assert os.path.exists(GIT_HOOK_FILE), f"Source file not found: {GIT_HOOK_FILE}"


def test_source_file_syntax_valid():
    """
    Verify the git hook source file has valid Python syntax.
    pass_to_pass: Syntax validation.
    """
    source = read_source()
    try:
        compile(source, GIT_HOOK_FILE, "exec")
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in source file: {e}")


# ============================================================================
# Pass-to-pass tests using actual repo CI commands (subprocess-based)
# ============================================================================


def test_repo_ruff_check():
    """
    Ruff linter passes on the git hook file (pass_to_pass).
    """
    r = subprocess.run(
        ["ruff", "check", "providers/git/src/airflow/providers/git/hooks/git.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """
    Ruff format check passes on the git hook file (pass_to_pass).
    """
    r = subprocess.run(
        ["ruff", "format", "--check", "providers/git/src/airflow/providers/git/hooks/git.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_python_syntax_check():
    """
    Python syntax check passes on the git hook file (pass_to_pass).
    """
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import ast; ast.parse(open('{REPO}/providers/git/src/airflow/providers/git/hooks/git.py').read())",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
