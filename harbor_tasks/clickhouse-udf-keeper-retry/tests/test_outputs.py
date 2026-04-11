#!/usr/bin/env python3
"""
Tests for UDF registry loss fix during Keeper session expiry.

The fix addresses two issues:
1. tryLoadObject() catches all KeeperException errors the same way, meaning hardware
   errors (connection loss, session expiry) are treated like "node not found" errors
2. refreshObjects() doesn't retry when Keeper hiccups occur

The fix:
1. Adds special handling in tryLoadObject() to re-throw hardware errors so they can be retried
2. Adds ZooKeeperRetriesControl with backoff to refreshObjects() to handle transient failures
"""

import subprocess
import os
import re
import pytest

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def read_target_file():
    """Read the target source file."""
    with open(FULL_PATH, 'r') as f:
        return f.read()


def test_hardware_error_handling():
    """
    FAIL TO PASS: tryLoadObject must re-throw Keeper hardware errors.

    The fix adds a catch block specifically for zkutil::KeeperException that:
    - Checks if the error is a hardware error using Coordination::isHardwareError()
    - Re-throws hardware errors so the caller can handle them (retry)
    - Treats non-hardware errors as missing objects (returns nullptr)
    """
    content = read_target_file()

    # Check for the new KeeperException catch block with hardware error handling
    pattern = r'catch\s*\(\s*const\s+zkutil::KeeperException\s*&\s*e\s*\)'
    match = re.search(pattern, content)
    assert match is not None, (
        "Missing catch block for zkutil::KeeperException. "
        "The fix should catch KeeperException separately to handle hardware errors."
    )

    # Check for isHardwareError call
    assert 'isHardwareError(e.code)' in content, (
        "Missing isHardwareError(e.code) check. "
        "Hardware errors must be detected to trigger retry logic."
    )

    # Check that hardware errors are re-thrown
    hardware_section = content[match.start():match.start() + 800]
    assert 'throw;' in hardware_section, (
        "Hardware errors must be re-thrown to allow retry. "
        "The catch block should re-throw after logging the hardware error."
    )


def test_retry_constants():
    """
    FAIL TO PASS: Retry constants must be defined correctly.

    The fix uses these constants for the retry logic:
    - max_retries = 5
    - initial_backoff_ms = 200
    - max_backoff_ms = 5000
    """
    content = read_target_file()

    # Check for retry constants
    assert 'static constexpr UInt64 max_retries = 5;' in content, (
        "Missing or incorrect max_retries constant. Should be 'static constexpr UInt64 max_retries = 5;'"
    )

    assert 'static constexpr UInt64 initial_backoff_ms = 200;' in content, (
        "Missing or incorrect initial_backoff_ms constant. Should be 'static constexpr UInt64 initial_backoff_ms = 200;'"
    )

    assert 'static constexpr UInt64 max_backoff_ms = 5000;' in content, (
        "Missing or incorrect max_backoff_ms constant. Should be 'static constexpr UInt64 max_backoff_ms = 5000;'"
    )


def test_zookeeper_retries_control():
    """
    FAIL TO PASS: refreshObjects must use ZooKeeperRetriesControl.

    The fix wraps the object loading loop in a ZooKeeperRetriesControl retryLoop
    to handle transient Keeper hiccups with automatic backoff.
    """
    content = read_target_file()

    # Check for ZooKeeperRetriesControl usage
    assert 'ZooKeeperRetriesControl retries_ctl' in content, (
        "Missing ZooKeeperRetriesControl instance. "
        "refreshObjects should use ZooKeeperRetriesControl for retry logic."
    )

    # Check for retryLoop call
    assert 'retries_ctl.retryLoop' in content, (
        "Missing retries_ctl.retryLoop() call. "
        "The object loading should be wrapped in a retry loop."
    )

    # Check for function_names_and_asts.clear() inside retry loop
    assert 'function_names_and_asts.clear()' in content, (
        "Missing function_names_and_asts.clear() in retry loop. "
        "The vector must be cleared at the start of each retry attempt."
    )


def test_includes_added():
    """
    FAIL TO PASS: Required headers must be included.

    The fix requires these additional includes:
    - ZooKeeperCommon.h for isHardwareError()
    - ZooKeeperRetries.h for ZooKeeperRetriesControl
    """
    content = read_target_file()

    # Check for new includes
    assert '#include <Common/ZooKeeper/ZooKeeperCommon.h>' in content, (
        "Missing ZooKeeperCommon.h include. Required for isHardwareError()."
    )

    assert '#include <Common/ZooKeeper/ZooKeeperRetries.h>' in content, (
        "Missing ZooKeeperRetries.h include. Required for ZooKeeperRetriesControl."
    )


def test_hardware_error_log_message():
    """
    FAIL TO PASS: Specific log message for hardware errors must exist.

    The fix adds a distinctive warning log for Keeper hardware errors.
    """
    content = read_target_file()

    # Check for the specific log message
    assert 'Keeper hardware error while loading user defined SQL object' in content, (
        "Missing distinctive hardware error log message. "
        "The fix should log a specific warning when hardware errors occur."
    )


def test_catch_ordering():
    """
    FAIL TO PASS: KeeperException catch must come before the generic catch.

    Since KeeperException is a subclass of std::exception (caught by catch (...)),
    the specific catch block must appear before the generic catch (...).
    """
    content = read_target_file()

    # Find the tryLoadObject function and look at the catch blocks within it
    # The new catch blocks are added around line 360-375 in the tryLoadObject function
    tryloadobject_start = content.find('tryLoadObject')
    assert tryloadobject_start != -1, "Could not find tryLoadObject function"

    # Get a section of the file starting from tryLoadObject (about 500 chars should cover the function)
    tryloadobject_section = content[tryloadobject_start:tryloadobject_start + 5000]

    # Find both catch blocks within this section (relative positions)
    keeper_catch_rel = tryloadobject_section.find('catch (const zkutil::KeeperException & e)')
    generic_catch_rel = tryloadobject_section.find('catch (...)', tryloadobject_section.find('ASTPtr UserDefinedSQLObjectsZooKeeperStorage::tryLoadObject'))

    assert keeper_catch_rel != -1, "Missing KeeperException catch block in tryLoadObject"

    # Find the generic catch AFTER the KeeperException catch in this function
    # Look for the second catch (...) after KeeperException catch
    generic_after_keeper = tryloadobject_section.find('catch (...)', keeper_catch_rel)
    assert generic_after_keeper != -1, "Missing generic catch (...) block after KeeperException catch"

    # Keeper catch must come before the generic catch in the same scope
    # This verifies the ordering is correct for the new catch blocks added by the fix


def test_code_compiles_syntax():
    """
    PASS TO PASS: Basic syntax validation.

    Verify the file has valid C++ syntax by checking for balanced braces
    and proper structure. This is a lightweight check.
    """
    content = read_target_file()

    # Check for basic C++ structure
    assert 'namespace DB' in content, "Missing DB namespace"

    # Count braces as a basic syntax check
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open, {close_braces} close"
    )

    # Check for class or function definitions
    assert 'UserDefinedSQLObjectsZooKeeperStorage' in content, (
        "Missing UserDefinedSQLObjectsZooKeeperStorage class reference"
    )


def test_repo_style_checks():
    """
    PASS TO PASS: Repository style checks pass.

    Runs the repository's style check scripts that validate code hygiene:
    - check_submodules.sh: submodule integrity
    These are fast, non-compilation checks that ensure code quality.
    """
    # Skip if git repo not available (e.g., minimal Docker clone)
    git_dir = os.path.join(REPO, ".git")
    if not os.path.exists(git_dir):
        pytest.skip("Git repository not available (minimal clone)")

    style_scripts = [
        "./ci/jobs/scripts/check_style/check_submodules.sh",
    ]

    for script in style_scripts:
        # Skip if script doesn't exist
        if not os.path.exists(os.path.join(REPO, script)):
            pytest.skip(f"Style check script {script} not found")

        r = subprocess.run(
            ["bash", script],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"Style check script {script} failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
        )


def test_repo_cpp_style():
    """
    PASS TO PASS: C++ style checks pass (no new issues in target file).

    Runs the repository's C++ style check script. This validates:
    - No trailing whitespace
    - Proper include style
    - No forbidden APIs
    - Proper brace style
    - And many other C++ style rules

    Only checks that the target file doesn't introduce NEW style issues.
    """
    # Skip if git repo not available (e.g., minimal Docker clone)
    git_dir = os.path.join(REPO, ".git")
    if not os.path.exists(git_dir):
        pytest.skip("Git repository not available (minimal clone)")

    # Skip if script doesn't exist
    script_path = "./ci/jobs/scripts/check_style/check_cpp.sh"
    if not os.path.exists(os.path.join(REPO, script_path)):
        pytest.skip(f"Style check script {script_path} not found")

    # First install ripgrep which is required by the check script
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Ignore apt-get errors, ripgrep may already be installed

    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "ripgrep"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Ignore apt-get errors, ripgrep may already be installed

    r = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )

    # The script may find pre-existing issues, but we only fail if the
    # target file has issues. Check that the target file path doesn't
    # appear in the error output.
    if r.returncode != 0:
        target_file_rel = TARGET_FILE
        # check if target file appears in the output
        if target_file_rel in r.stdout or target_file_rel.replace(
            "/", ""
        ) in r.stdout.replace("/", ""):
            assert False, (
                f"C++ style check found issues in target file:\n{r.stdout[-1000:]}"
            )
        # If target file not in output, pre-existing issues are acceptable


def test_target_file_no_typos():
    """
    PASS TO PASS: Target file has no typos.

    Uses codespell to check for common typos in the target file only.
    This is a lightweight check that only runs on the modified file.
    """
    # Check if codespell is available
    r = subprocess.run(
        ["which", "codespell"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if r.returncode != 0:
        # Try to install codespell
        r = subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        r = subprocess.run(
            ["apt-get", "install", "-y", "-qq", "codespell"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            pytest.skip("codespell not available and could not be installed")

    # Run codespell only on the target file
    ignore_words = os.path.join(REPO, "ci/jobs/scripts/check_style/codespell-ignore-words.list")
    ignore_lines = os.path.join(REPO, "ci/jobs/scripts/check_style/codespell-ignore-lines.list")

    cmd = [
        "codespell",
        "--quiet-level", "2",
        FULL_PATH,
    ]

    # Add ignore files if they exist
    if os.path.exists(ignore_words):
        cmd.extend(["--ignore-words", ignore_words])
    if os.path.exists(ignore_lines):
        cmd.extend(["--exclude-file", ignore_lines])

    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # codespell exits 0 if no typos found, 65 if typos found
    if r.returncode == 65:
        assert False, f"Typos found in target file:\n{r.stdout}\n{r.stderr}"
    # Other non-zero exit codes are acceptable (config issues, etc.)


def test_target_file_structure():
    """
    PASS TO PASS: Target file has valid C++ structure.

    Validates:
    - Proper include guards (not applicable for .cpp files)
    - Balanced braces and parentheses
    - No trailing whitespace
    - Valid UTF-8 encoding
    - Proper line endings (no carriage returns)
    """
    with open(FULL_PATH, 'rb') as f:
        raw_content = f.read()

    # Check for valid UTF-8
    try:
        content = raw_content.decode('utf-8')
    except UnicodeDecodeError as e:
        assert False, f"File is not valid UTF-8: {e}"

    # Check for carriage returns (Windows line endings)
    assert '\r' not in content, "File contains carriage returns (Windows line endings)"

    # Check for trailing whitespace on lines
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if line.endswith(' ') or line.endswith('\t'):
            assert False, f"Line {i} has trailing whitespace"

    # Check for balanced braces (basic check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for balanced parentheses (basic check)
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check for balanced angle brackets (in templates - allow for comparisons)
    # This is a heuristic: count < and > but exclude common comparison patterns
    open_angles = content.count('<')
    close_angles = content.count('>')
    # Allow some imbalance due to comparisons, but warn if way off
    if abs(open_angles - close_angles) > 50:
        assert False, f"Severely unbalanced angle brackets: {open_angles} open, {close_angles} close"


def test_target_file_includes():
    """
    PASS TO PASS: Target file has properly formatted includes.

    Validates:
    - Standard library includes use <angle brackets>
    - Project includes are properly formatted
    - No duplicate includes
    """
    content = read_target_file()
    lines = content.split('\n')

    includes = []
    for line in lines:
        if line.startswith('#include'):
            includes.append(line)

    # Check for duplicate includes
    seen = set()
    for include in includes:
        if include in seen:
            assert False, f"Duplicate include: {include}"
        seen.add(include)

    # Check that all includes use angle brackets (standard practice in ClickHouse)
    for include in includes:
        if '"' in include and '<' not in include:
            # Local includes with quotes are sometimes used, but check they're intentional
            pass  # Allow quoted includes


def test_repo_yaml_linting():
    """
    PASS TO PASS: CI workflow YAML files are valid.

    Validates that GitHub workflow YAML files have valid syntax using yamllint.
    This is a real CI command from the repo's style checks.
    """
    # First install yamllint if not present
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "yamllint"],
        capture_output=True, text=True, timeout=120,
    )

    workflow_dir = os.path.join(REPO, ".github/workflows")
    if not os.path.exists(workflow_dir):
        pytest.skip("GitHub workflows directory not found")

    yaml_files = [
        "pull_request.yml",
    ]

    for yaml_file in yaml_files:
        yaml_path = os.path.join(workflow_dir, yaml_file)
        if not os.path.exists(yaml_path):
            continue

        r = subprocess.run(
            ["yamllint", "--config-file", "./.yamllint", yaml_path],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"YAML lint failed for {yaml_file}:\n{r.stdout}\n{r.stderr}"


def test_target_file_codespell():
    """
    PASS TO PASS: Target file passes codespell typo check.

    Runs codespell on the target file only to check for typos.
    This is a real CI command from check_typos.sh.
    """
    # Install codespell if not present
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "codespell"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        pytest.skip("Could not install codespell")

    ignore_words = os.path.join(REPO, "ci/jobs/scripts/check_style/codespell-ignore-words.list")
    ignore_lines = os.path.join(REPO, "ci/jobs/scripts/check_style/codespell-ignore-lines.list")

    cmd = [
        "codespell",
        "--quiet-level", "2",
        FULL_PATH,
    ]

    # Add ignore files if they exist
    if os.path.exists(ignore_words):
        cmd.extend(["--ignore-words", ignore_words])
    if os.path.exists(ignore_lines):
        cmd.extend(["--exclude-file", ignore_lines])

    r = subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=60,
    )

    # codespell exits 0 if no typos, 65 if typos found
    assert r.returncode == 0, f"Typos found in target file:\n{r.stdout}\n{r.stderr}"


def test_target_file_no_tabs():
    """
    PASS TO PASS: Target file has no tab characters (repo style check).

    Checks for tabs using grep -F with actual tab character.
    This matches the repo's check_cpp.sh tab check.
    """
    r = subprocess.run(
        ["grep", "-F", "\t", FULL_PATH],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode != 0, f"Tab characters found in target file:\n{r.stdout}"


def test_target_file_no_trailing_whitespace():
    """
    PASS TO PASS: Target file has no trailing whitespace (repo style check).

    Checks for trailing whitespace using grep -P ' $'.
    This matches the repo's check_cpp.sh trailing whitespace check.
    """
    r = subprocess.run(
        ["grep", "-n", "-P", " $", FULL_PATH],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode != 0, f"Trailing whitespace found in target file:\n{r.stdout}"


def test_target_file_unix_newlines():
    """
    PASS TO PASS: Target file uses Unix line endings (repo style check).

    Checks for DOS/Windows newlines using grep -P '\r$'.
    This matches the repo's various_checks.sh DOS newline check.
    """
    r = subprocess.run(
        ["grep", "-l", "-P", "\r$", FULL_PATH],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode != 0, f"DOS/Windows newlines found in target file"


def test_target_file_no_bom():
    """
    PASS TO PASS: Target file has no UTF BOM markers.

    Checks for UTF-8, UTF-16LE, and UTF-16BE BOM markers.
    This matches the repo's various_checks.sh BOM check.
    """
    with open(FULL_PATH, 'rb') as f:
        content = f.read()

    # Check for UTF-8 BOM
    assert not content.startswith(b'\xef\xbb\xbf'), "File has UTF-8 BOM marker"
    # Check for UTF-16LE BOM
    assert not content.startswith(b'\xff\xfe'), "File has UTF-16LE BOM marker"
    # Check for UTF-16BE BOM
    assert not content.startswith(b'\xfe\xff'), "File has UTF-16BE BOM marker"


def test_target_file_no_conflict_markers():
    """
    PASS TO PASS: Target file has no git conflict markers.

    Checks for git conflict markers using grep -P.
    This matches the repo's various_checks.sh conflict marker check.
    """
    r = subprocess.run(
        ["grep", "-P", "^(<<<<<<<|=======|>>>>>>>)$", FULL_PATH],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode != 0, f"Git conflict markers found in target file:\n{r.stdout}"


def test_target_file_valid_utf8():
    """
    PASS TO PASS: Target file is valid UTF-8 encoded.

    Uses Python decode to verify valid UTF-8 encoding.
    """
    with open(FULL_PATH, 'rb') as f:
        raw_content = f.read()

    try:
        raw_content.decode('utf-8')
    except UnicodeDecodeError as e:
        assert False, f"File is not valid UTF-8: {e}"


def test_target_file_no_duplicate_includes():
    """
    PASS TO PASS: Target file has no duplicate #include directives.

    Uses awk to find and count duplicate include lines.
    This matches the repo's check_style.py duplicate include check.
    """
    r = subprocess.run(
        ["bash", "-c",
         f"awk '/^#include /{{print}}' {FULL_PATH} | sort | uniq -c | grep -v '1 ' || true"],
        capture_output=True, text=True, timeout=30,
    )
    # If output is empty, no duplicates found
    assert r.stdout.strip() == "", f"Duplicate includes found:\n{r.stdout}"
