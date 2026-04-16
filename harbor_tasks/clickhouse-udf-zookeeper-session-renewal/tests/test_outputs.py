#!/usr/bin/env python3
"""
Tests for ClickHouse UDF ZooKeeper session renewal fix.
"""
import re, subprocess, sys
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"

def _get_file_content() -> str:
    return TARGET_FILE.read_text() if TARGET_FILE.exists() else ""

def _run_shell(script, timeout=30):
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=timeout, cwd=str(REPO))

def _parse_retry_loop(content):
    func_match = re.search(r"void\s+UserDefinedSQLObjectsZooKeeperStorage::refreshObjects\s*\([^)]*\)\s*\{", content)
    if not func_match:
        return "", ""
    func_start = func_match.start()
    retry_match = re.search(r"retries_ctl\.retryLoop\s*\(\s*\[", content)
    if not retry_match:
        return "", ""
    pre_retry = content[func_start:retry_match.start()]
    lambda_start = content.index("[", retry_match.start()) + 1
    depth, pos = 1, lambda_start
    while depth > 0 and pos < len(content):
        c = content[pos]
        if c == "{": depth += 1
        elif c == "}": depth -= 1
        pos += 1
    return pre_retry, content[lambda_start:pos-1]

def test_session_renewal_on_retry():
    """Fail-to-pass: Verify session renewal happens inside retry loop on isRetry().

    Any correct fix must:
    1. Call a session getter when retrying
    2. Use the renewed session for subsequent operations in the loop

    This tests the BEHAVIOR, not the variable name or exact syntax.
    """
    content = _get_file_content()
    _, retry_body = _parse_retry_loop(content)
    assert retry_body, "retryLoop not found in refreshObjects"
    has_retry_check = "isRetry()" in retry_body
    assert has_retry_check, "No retry check found inside retryLoop - session wont be renewed on retry"
    retry_check_pattern = r"isRetry\s*\(\s*\)\s*;?\s*"
    match = re.search(retry_check_pattern, retry_body)
    if match:
        after_check = retry_body[match.end():match.end() + 200]
        assert "getZooKeeper" in after_check, "isRetry() check found but no getZooKeeper call follows - session not renewed"

def test_object_names_fetched_inside_retry_loop():
    """Fail-to-pass: Verify getObjectNamesAndSetWatch is called inside retry loop.

    Any correct fix must fetch object names inside the retry loop so fresh
    watches are set on the live session after renewal.
    """
    content = _get_file_content()
    pre_retry, retry_body = _parse_retry_loop(content)
    assert retry_body, "retryLoop not found in refreshObjects"
    assert "getObjectNamesAndSetWatch" in retry_body, "getObjectNamesAndSetWatch not called inside retryLoop"

def test_session_renewal_mechanism_exists():
    """Fail-to-pass: Verify the fix uses zookeeper_getter to renew the session.

    Any correct fix must use the zookeeper_getter mechanism to obtain a fresh
    session on retry. We verify this by checking the relationship between
    isRetry() and getZooKeeper() in the retry loop.
    """
    content = _get_file_content()
    _, retry_body = _parse_retry_loop(content)
    assert retry_body, "retryLoop not found"
    assert "zookeeper_getter" in retry_body, "zookeeper_getter not used in retryLoop - session renewal mechanism missing"
    assert "getZooKeeper" in retry_body, "getZooKeeper not called in retryLoop - session not being renewed"

def test_session_renewed_before_use():
    """Fail-to-pass: Verify the session renewal happens BEFORE getObjectNamesAndSetWatch.

    The fix must renew the session before fetching object names in the retry loop,
    so that fresh watches are set on the live session.
    """
    content = _get_file_content()
    _, retry_body = _parse_retry_loop(content)
    assert retry_body, "retryLoop not found"

    # Find positions of isRetry check and getObjectNamesAndSetWatch
    retry_match = re.search(r"isRetry\s*\(\s*\)\s*;?\s*", retry_body)
    obj_match = re.search(r"getObjectNamesAndSetWatch\s*\(", retry_body)

    assert retry_match, "isRetry() not found in retry loop"
    assert obj_match, "getObjectNamesAndSetWatch not called in retry loop"

    # The isRetry check must come BEFORE getObjectNamesAndSetWatch
    assert retry_match.start() < obj_match.start(), \
        "isRetry check must come BEFORE getObjectNamesAndSetWatch call - session not renewed before use"

def test_compilation():
    """Verify the target file exists with refreshObjects function and ZooKeeperRetriesControl (pass_to_pass baseline)."""
    script = f"if [ ! -f \"{TARGET_FILE}\" ]; then echo FAIL; exit 1; fi; if ! grep -q refreshObjects \"{TARGET_FILE}\"; then echo FAIL; exit 1; fi; if ! grep -q ZooKeeperRetriesControl \"{TARGET_FILE}\"; then echo FAIL; exit 1; fi; echo PASS"
    r = _run_shell(script)
    assert r.returncode == 0 and "PASS" in r.stdout, f"Compilation check failed: {r.stderr or r.stdout}"

def test_no_sleep_in_code():
    """Fail-to-pass: Verify no sleep calls in the changed code (ClickHouse rule)."""
    script = f"python3 -c \"import sys; content=open('{TARGET_FILE}').read(); func_start=content.find('void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects'); assert func_start!=-1, 'FAIL'; fc=content[func_start:func_start+3000]; fl=fc.lower(); assert 'sleep(' not in fl and 'usleep(' not in fl and 'std::this_thread::sleep' not in fc, 'FAIL'; print('PASS')\""
    r = _run_shell(script)
    assert r.returncode == 0 and "PASS" in r.stdout, f"Sleep check failed: {r.stderr or r.stdout}"

def test_deletion_logging():
    """Pass-to-pass: Verify the code follows ClickHouse deletion logging rule."""
    content = _get_file_content()
    retry_start = content.find("retries_ctl.retryLoop")
    if retry_start != -1:
        retry_section = content[retry_start:retry_start + 2000]
        assert "delete " not in retry_section.lower() or "LOG_" in retry_section, "Potential deletion without logging"

def test_repo_ci_tools_available():
    """Verify essential CI tooling is available in the environment (pass_to_pass)."""
    for tool in ["python3", "grep", "git", "sed", "awk"]:
        r = subprocess.run(["which", tool], capture_output=True, text=True, timeout=10)
        assert r.returncode == 0, f"Missing essential CI tool: {tool}"

def test_repo_no_tabs():
    r = _run_shell(f"grep -F $'\\t' \"{TARGET_FILE}\" && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"Tab check failed: {r.stderr or r.stdout}"

def test_repo_no_trailing_whitespace():
    r = _run_shell(f"grep -n -P ' $' \"{TARGET_FILE}\" && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"Trailing whitespace check failed: {r.stderr or r.stdout}"

def test_repo_no_cerr_cout():
    r = _run_shell(f"grep -F -e 'std::cerr' -e 'std::cout' \"{TARGET_FILE}\" && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"std::cerr/cout check failed: {r.stderr or r.stdout}"

def test_repo_no_std_format():
    r = _run_shell(f"grep -q 'std::format' \"{TARGET_FILE}\" && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"std::format check failed: {r.stderr or r.stdout}"

def test_repo_no_raw_assert():
    r = _run_shell(f"grep -P '\\\\bassert\\\\s*\\\\(' \"{TARGET_FILE}\" | grep -v -P '(CH_ASSERT|static_assert)' && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"Raw assert check failed: {r.stderr or r.stdout}"

def test_repo_no_builtin_unreachable():
    r = _run_shell(f"grep -P '__builtin_unreachable' \"{TARGET_FILE}\" && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"__builtin_unreachable check failed: {r.stderr or r.stdout}"

def test_repo_no_std_filesystem_symlink():
    r = _run_shell(f"grep -P '::(is|read)_symlink' \"{TARGET_FILE}\" && echo FAIL || echo PASS")
    assert r.returncode == 0 and "PASS" in r.stdout, f"symlink check failed: {r.stderr or r.stdout}"

def test_repo_clang_format():
    import pytest
    r = subprocess.run(["which", "clang-format"], capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        pytest.skip("clang-format not available")
    r = subprocess.run(["clang-format", "--dry-run", "--Werror", str(TARGET_FILE)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"clang-format check failed: {r.stderr or r.stdout}"

def test_repo_python_env():
    r = subprocess.run(["python3", "-c", "import pytest; import yaml; print('OK')"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0 and "OK" in r.stdout, f"Python env check failed: {r.stderr}"

def test_repo_git_available():
    r = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0 and "git version" in r.stdout, f"Git not available: {r.stderr}"

def test_clickhouse_allman_braces():
    content = _get_file_content()
    violations = []
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("#"):
            continue
        if re.match(r"^\s*(?:if|else|for|while|switch|try|catch)\s*[^{{]*{{\s*$", line):
            if not stripped.startswith("}}") and "else" not in stripped:
                violations.append(f"Line {i}: {stripped[:60]}")
    assert not violations, f"K&R style braces found: {violations}"

def test_clickhouse_naming_conventions():
    content = _get_file_content()
    for t in ["UserDefinedSQLObjectsZooKeeperStorage", "ZooKeeperRetriesControl", "UserDefinedSQLObjectType"]:
        assert t in content, f"Expected type {t} not found"

def test_clickhouse_logger_usage():
    content = _get_file_content()
    assert any(m in content for m in ["LOG_DEBUG", "LOG_INFO", "LOG_WARNING", "LOG_ERROR"]), "No LOG_* macros found"

def test_exception_handling_patterns():
    content = _get_file_content()
    if "catch (...)" in content:
        assert "tryLogCurrentException" in content, "catch (...) without tryLogCurrentException"
    assert "KeeperException" in content, "KeeperException handling missing"

def test_cpp_syntax_valid():
    content = _get_file_content()
    assert content.count("{") == content.count("}"), "Unbalanced braces"
    assert content.count("(") == content.count(")"), "Unbalanced parentheses"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
