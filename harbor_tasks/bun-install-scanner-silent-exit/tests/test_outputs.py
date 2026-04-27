#!/usr/bin/env python3
"""
Task: bun-install-scanner-silent-exit
Repo: oven-sh/bun @ 1d50d640f8fec6ce2d144f0cfd204e30da373c64
PR:   28196

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import tempfile
import os
import shutil
from pathlib import Path

REPO = "/workspace/bun"
IWM = f"{REPO}/src/install/PackageManager/install_with_manager.zig"
SS = f"{REPO}/src/install/PackageManager/security_scanner.zig"
REGRESSION_TEST = f"{REPO}/test/regression/issue/28193.test.ts"


def _read_file(path):
    """Read file content as text."""
    try:
        return Path(path).read_text()
    except FileNotFoundError:
        return None


def _extract_switch_body(text, catch_match):
    """Extract the switch(err) body from a catch block."""
    start_pos = catch_match.end()
    switch_match = re.search(r"switch\s*\(\s*err\s*\)\s*\{", text[start_pos:])
    assert switch_match, "Could not find switch(err) statement"

    switch_start = start_pos + switch_match.end()
    brace_count = 1
    switch_end = switch_start
    for i, char in enumerate(text[switch_start:]):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                switch_end = switch_start + i
                break

    return text[switch_start:switch_end]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests that verify error handling flow
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_bun_install_produces_error_message():
    """
    bun install with broken security scanner config must print an error
    message to stderr (not silently exit with code 1).

    Behavior verified: Running 'bun install' with an invalid scanner produces
    stderr output containing 'security scanner', proving the fix produces output.
    """
    # Create a temp directory with a broken scanner config
    tmpdir = tempfile.mkdtemp(prefix="bun-test-28193-")
    try:
        # Write package.json
        pkg_json = os.path.join(tmpdir, "package.json")
        with open(pkg_json, "w") as f:
            f.write('{"name": "test-28193", "dependencies": {"is-even": "1.0.0"}}')

        # Write bunfig.toml with invalid scanner
        bunfig = os.path.join(tmpdir, "bunfig.toml")
        with open(bunfig, "w") as f:
            f.write('[install.security]\nscanner = "@nonexistent-scanner/does-not-exist"\n')

        # Run bun install and capture stderr
        r = subprocess.run(
            ["bun", "install"],
            capture_output=True, text=True, timeout=60,
            cwd=tmpdir,
            env={**os.environ, "BUN_INSTALL_CACHE_DIR": os.path.join(tmpdir, ".cache")}
        )

        # The fix should produce error output to stderr
        # Bug: silent exit with no stderr output
        # Fix: stderr contains "security scanner" error message
        stderr_lower = r.stderr.lower()
        has_error_output = "security scanner" in stderr_lower or "scanner" in stderr_lower

        assert has_error_output, (
            f"No error message about security scanner in stderr. "
            f"stderr was: {r.stderr[:500]!r}, returncode={r.returncode}"
        )
        assert r.returncode != 0, f"Expected non-zero exit code, got {r.returncode}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# [pr_diff] fail_to_pass
def test_catch_all_produces_output():
    """
    The catch block for security scanner errors must produce output for
    ANY error, not silently swallow it.

    Behavior verified: When a security scanner error is caught, something
    is printed to inform the user (not an empty block).
    """
    text = _read_file(IWM)
    assert text is not None, f"Could not read {IWM}"

    # Find the catch block for performSecurityScanAfterResolution
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    switch_body = _extract_switch_body(text, catch_match)

    # Check that empty else => {} is NOT present (this was the bug)
    if re.search(r"else\s*=>\s*\{\s*\}", switch_body):
        raise AssertionError("Bug found: empty else => {} present - errors would exit silently")

    # The switch body must have at least one Output.* call for error reporting
    has_output = re.search(r"Output\.\w+\s*\(", switch_body)
    assert has_output, "Switch body must have at least one Output.* call for error reporting"


# [pr_diff] fail_to_pass
def test_error_variant_coverage():
    """
    Error handling must handle ALL error variants, not just named ones.

    Behavior verified: The error switch either has a catch-all branch that
    captures unknown errors and produces output, or has enough named error
    cases to cover all important variants — ensuring no error is silently
    swallowed.
    """
    text = _read_file(IWM)
    assert text is not None, f"Could not read {IWM}"

    # Find the catch block
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    switch_body = _extract_switch_body(text, catch_match)

    # Check for empty catch-all else => {} (this was the bug)
    if re.search(r"else\s*=>\s*\{\s*\}", switch_body):
        raise AssertionError(
            "Bug found: empty 'else => {}' catch-all present. "
            "Unknown error variants would be silently swallowed."
        )

    # Check for comprehensive error coverage via either approach:
    # (a) A capturing catch-all (else => |e|) that produces output, OR
    # (b) Enough named error cases (>= 3) to cover the important variants
    has_capturing_else = re.search(r"else\s*=>\s*\|\w+\|", switch_body)
    named_cases = re.findall(r"error\.\w+\s*=>", switch_body)

    if has_capturing_else:
        # Verify the else branch produces output
        else_branch_match = re.search(
            r"else\s*=>\s*\|\w+\|\s*\{([^}]*)\}",
            switch_body,
            re.DOTALL
        )
        if else_branch_match:
            else_content = else_branch_match.group(1)
            has_output = re.search(r"Output\.\w+\s*\(", else_content)
            assert has_output, (
                "Catch-all else branch captures error but does not produce output. "
                "Unknown errors would not be reported to the user."
            )
    elif len(named_cases) >= 3:
        # Enough named cases to cover the important error variants
        pass
    else:
        raise AssertionError(
            f"Error handling must cover all variants. Need either a capturing "
            f"catch-all (else => |e|) or at least 3 named error cases. "
            f"Found {len(named_cases)} named cases and no capturing catch-all."
        )


# [pr_diff] fail_to_pass
def test_error_printing_centralized():
    """
    Error printing for security scanner errors must be centralized in
    install_with_manager.zig, not scattered across both files.

    Behavior verified: The catch block switch has multiple Output.* calls
    across multiple error-handling branches, ensuring errors are printed
    centrally in the catch handler.
    """
    iwm_text = _read_file(IWM)
    assert iwm_text is not None, f"Could not read {IWM}"

    # Find the catch block for performSecurityScanAfterResolution
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, iwm_text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    switch_body = _extract_switch_body(iwm_text, catch_match)

    # Count Output.* calls in the switch body (any Output method is acceptable:
    # errGeneric, err, prettyErrorln, etc.)
    output_calls = re.findall(r"Output\.\w+\s*\(", switch_body)

    # Count error-handling branches: named cases + capturing else
    named_cases = re.findall(r"error\.\w+\s*=>", switch_body)
    has_else_handler = bool(re.search(r"else\s*=>\s*\|", switch_body))
    total_handlers = len(named_cases) + (1 if has_else_handler else 0)

    # Centralization means multiple error cases are handled here with output
    assert total_handlers >= 2, (
        f"Error printing should be centralized: need at least 2 error-handling branches. "
        f"Found {len(named_cases)} named cases and "
        f"{'a' if has_else_handler else 'no'} catch-all handler."
    )

    assert len(output_calls) >= 2, (
        f"Need at least 2 Output.* calls for centralized error reporting. "
        f"Found {len(output_calls)}."
    )


# [pr_diff] fail_to_pass
def test_error_variant_propagated():
    """
    The error result from the retry mechanism must be propagated as-is,
    not collapsed into a single generic error.

    Behavior verified: The retry result handling does NOT collapse all
    non-success cases into a single error. Instead, the .error case is
    handled separately (or the result is passed through).
    """
    ss_text = _read_file(SS)
    assert ss_text is not None, f"Could not read {SS}"

    # Find performSecurityScanAfterResolution function body
    fn_name = "performSecurityScanAfterResolution"
    pos = ss_text.find(fn_name)
    assert pos >= 0, "Could not find performSecurityScanAfterResolution function"

    # Find the opening paren of parameters
    paren_start = ss_text.find('(', pos + len(fn_name))
    assert paren_start >= 0, "Could not find opening paren"

    # Find matching closing paren
    paren_depth = 1
    scan_pos = paren_start + 1
    while scan_pos < len(ss_text) and paren_depth > 0:
        c = ss_text[scan_pos]
        if c == '(':
            paren_depth += 1
        elif c == ')':
            paren_depth -= 1
        scan_pos += 1

    # Find opening brace for function body
    brace_pos = ss_text.find('{', scan_pos)
    assert brace_pos >= 0, "Could not find opening brace"

    # Extract function body by counting braces
    brace_count = 1
    body_start = brace_pos + 1
    body_end = body_start
    while body_end < len(ss_text) and brace_count > 0:
        c = ss_text[body_end]
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
        body_end += 1

    func_body = ss_text[body_start:body_end-1]

    # Check for the buggy pattern: else => return error.SecurityScannerRetryFailed
    # This collapses ALL non-success results into one error, losing information
    has_collapse_pattern = re.search(
        r"else\s*=>\s*return\s+error\.SecurityScannerRetryFailed",
        func_body
    )
    if has_collapse_pattern:
        raise AssertionError(
            "Bug found: Using 'else => return error.SecurityScannerRetryFailed' "
            "which collapses all non-success errors into one generic error. "
            "The original error should be preserved and propagated."
        )

    # Check for proper propagation: the switch must handle the error case
    # in a way that preserves the original error information
    has_error_propagation = (
        # Explicit .@"error" case (captures or returns the error)
        re.search(r'\.\@"error"\s*=>', func_body) or
        # Explicit .error case with capture
        re.search(r"\.error\s*=>\s*\|\w+\|", func_body) or
        # Else with capture (inline or not) — propagates the error
        re.search(r"(?:inline\s+)?else\s*=>\s*\|\w+\|", func_body) or
        # Separate named cases for each variant
        (re.search(r"\.needs_install\s*=>", func_body) and
         re.search(r'\.(?:\@"error"|error)\s*=>', func_body))
    )

    assert has_error_propagation, (
        "No error propagation pattern found. The switch must handle the error "
        "case separately (e.g. .@\"error\" => |e|, inline else => |e|, or "
        "explicit named cases) to preserve the original error."
    )


# [pr_diff] fail_to_pass
def test_uses_err_generic():
    """
    Error messages in the catch block must use appropriate error output
    functions, NOT Output.pretty with raw <red> styling.

    Behavior verified: deprecated Output.pretty("<red>") is NOT used,
    and an appropriate Output.* error function IS used instead.
    """
    text = _read_file(IWM)
    assert text is not None, f"Could not read {IWM}"

    # Find the catch block for security scanner errors
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    switch_body = _extract_switch_body(text, catch_match)

    # Check for deprecated pattern: Output.pretty with <red>
    has_pretty_red = re.search(r"Output\.pretty\s*\(\s*\"<red>", switch_body)
    if has_pretty_red:
        raise AssertionError(
            "Using deprecated Output.pretty with <red> styling. "
            "Should use an appropriate error output function instead."
        )

    # Verify that appropriate error output functions are used
    # Accept any Output.* method (errGeneric, err, prettyErrorln, etc.)
    has_err_output = re.search(r"Output\.\w+\s*\(", switch_body)
    assert has_err_output, (
        "No error output functions found. "
        "Error messages should use an appropriate Output.* function."
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — regression test validation via file checks
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass
def test_regression_test_location():
    """Regression test at test/regression/issue/28193.test.ts with valid test structure."""
    test_file = Path(REGRESSION_TEST)
    if not test_file.exists():
        raise AssertionError(f"Regression test file not found at {REGRESSION_TEST}")

    content = test_file.read_text()
    lines = content.split("\n")
    if len(lines) <= 5:
        raise AssertionError(f"Test file too short: {len(lines)} lines (need > 5)")

    tests = len(re.findall(r"\btest\(", content))
    expects = len(re.findall(r"\bexpect\(", content))

    if tests == 0:
        raise AssertionError("No test definitions found (test() calls)")

    # Verify the test imports from harness
    if not re.search(r'from\s+["\']harness["\']', content):
        raise AssertionError("Regression test must import from 'harness'")


# [agent_config] fail_to_pass
def test_regression_test_uses_harness():
    """Regression test imports bunExe and bunEnv from 'harness'."""
    test_file = Path(REGRESSION_TEST)
    if not test_file.exists():
        raise AssertionError(f"Regression test file not found at {REGRESSION_TEST}")

    content = test_file.read_text()

    # Check harness import
    if not re.search(r'from\s+["\']harness["\']', content):
        raise AssertionError("Must import from 'harness'")

    if "bunExe" not in content:
        raise AssertionError("Must use bunExe from harness")

    if "bunEnv" not in content:
        raise AssertionError("Must use bunEnv from harness")


# [agent_config] fail_to_pass
def test_regression_test_uses_tempdir():
    """Regression test uses tempDir from 'harness', not tmpdirSync/mkdtempSync."""
    test_file = Path(REGRESSION_TEST)
    if not test_file.exists():
        raise AssertionError(f"Regression test file not found at {REGRESSION_TEST}")

    content = test_file.read_text()

    if "tempDir" not in content:
        raise AssertionError("Must use tempDir from harness")

    if "tmpdirSync" in content:
        raise AssertionError("Must NOT use tmpdirSync from node:fs")

    if "mkdtempSync" in content:
        raise AssertionError("Must NOT use mkdtempSync from node:fs")


# ---------------------------------------------------------------------------
# Pass-to-pass — preserved from original
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_workspace_error_preserved():
    """SecurityScannerInWorkspace error handling still present in install_with_manager.zig."""
    text = Path(IWM).read_text()
    assert "SecurityScannerInWorkspace" in text, "SecurityScannerInWorkspace error type missing"


# [pr_diff] pass_to_pass
def test_error_types_preserved():
    """security_scanner.zig still returns proper error types."""
    text = Path(SS).read_text()
    expected = ["InvalidPackageID", "PartialInstallFailed", "NoPackagesInstalled", "SecurityScannerInWorkspace"]
    found = sum(1 for e in expected if f"return error.{e}" in text)
    assert found >= 3, f"Only {found}/4 expected error types still returned"


# [static] pass_to_pass
def test_anti_stub():
    """Both Zig source files have substantial content."""
    assert len(Path(IWM).read_text().splitlines()) > 200, "install_with_manager.zig too short"
    assert len(Path(SS).read_text().splitlines()) > 50, "security_scanner.zig too short"


# [agent_config] pass_to_pass
def test_exit_code_assertion_last():
    """Regression test asserts content before exit code (CLAUDE.md:101)."""
    test_file = Path(REGRESSION_TEST)
    assert test_file.exists(), "Regression test file missing"
    lines = test_file.read_text().splitlines()
    exit_lines = [i for i, l in enumerate(lines) if re.search(r"expect\s*\(\s*exitCode\s*\)", l)]
    content_lines = [i for i, l in enumerate(lines) if re.search(r"expect\s*\(\s*std(?:out|err)\s*\)", l)]
    assert exit_lines, "No exit code assertions found"
    assert content_lines, "No content assertions found"
    for ec in exit_lines:
        assert any(ca < ec for ca in content_lines), "exit code assertion comes before content assertion"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_banned_words():
    """Repo banned words check passes (CI check from package.json scripts.banned)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_glob_sources():
    """Repo glob-sources script passes (CI check from package.json scripts.glob-sources)."""
    r = subprocess.run(
        ["bun", "run", "glob-sources"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Glob sources failed:\n{r.stderr[-500:]}"
    # Verify output contains expected "Globbed" message
    assert "Globbed" in r.stdout, f"Expected 'Globbed' in output, got:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repo Prettier formatting check passes on package.json."""
    r = subprocess.run(
        ["bunx", "--bun", "prettier@latest", "--check", "package.json"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Prettier exits 0 if files are formatted correctly
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid():
    """Repo package.json is valid JSON and parseable by bun."""
    r = subprocess.run(
        ["bun", "-e", "const d = JSON.parse(require('fs').readFileSync('package.json', 'utf8')); console.log('name:', d.name, 'version:', d.version)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json validation failed:\n{r.stderr[-500:]}"
    assert "name: bun" in r.stdout and "version:" in r.stdout, "package.json not properly parsed"


# [repo_tests] pass_to_pass
def test_repo_tsconfig_valid():
    """Repo tsconfig.json is valid JSON and parseable by node."""
    r = subprocess.run(
        ["node", "-e", "const d = JSON.parse(require('fs').readFileSync('tsconfig.json', 'utf8')); console.log('compilerOptions:', !!d.compilerOptions)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"tsconfig.json validation failed:\n{r.stderr[-500:]}"
    assert "compilerOptions: true" in r.stdout, "tsconfig.json not properly parsed"


# [repo_tests] pass_to_pass
def test_repo_harness_imports():
    """Test harness imports resolve correctly (bun:test and harness)."""
    r = subprocess.run(
        ["bun", "-e", "import('bun:test').then(m => console.log('bun:test ok')); import('./test/harness.ts').then(m => console.log('harness ok')).catch(e => console.log('harness not needed'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Harness imports check failed:\n{r.stderr[-500:]}"
    assert "bun:test ok" in r.stdout, "bun:test import failed"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — File structure and content checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass - uses Path.read_text() not subprocess
def test_repo_source_files_valid():
    """Modified source files exist and have valid content structure."""
    # Verify install_with_manager.zig exists and has substantial content
    iwm_file = Path(IWM)
    assert iwm_file.exists(), "install_with_manager.zig not found"
    iwm_lines = len(iwm_file.read_text().splitlines())
    assert iwm_lines > 200, f"install_with_manager.zig has only {iwm_lines} lines (expected > 200)"

    # Verify security_scanner.zig exists and has substantial content
    ss_file = Path(SS)
    assert ss_file.exists(), "security_scanner.zig not found"
    ss_lines = len(ss_file.read_text().splitlines())
    assert ss_lines > 50, f"security_scanner.zig has only {ss_lines} lines (expected > 50)"


# [static] pass_to_pass - uses Path.read_text() not subprocess
def test_repo_zig_files_valid():
    """Zig source files have valid structure with expected keywords."""
    # Check install_with_manager.zig for basic syntax validity
    iwm_content = Path(IWM).read_text()
    assert "pub fn" in iwm_content or "const" in iwm_content, "install_with_manager.zig doesn't look like valid Zig"
    assert "installWithManager" in iwm_content, "install_with_manager.zig missing expected function"

    # Check security_scanner.zig for basic syntax validity
    ss_content = Path(SS).read_text()
    assert "pub fn" in ss_content or "const" in ss_content, "security_scanner.zig doesn't look like valid Zig"
    assert "performSecurityScanAfterResolution" in ss_content, "security_scanner.zig missing expected function"


# [static] pass_to_pass - file existence check, should pass even if not found on base
def test_repo_typescript_check():
    """TypeScript regression test location is valid (file may not exist on base commit)."""
    rt_file = Path(REGRESSION_TEST)
    if rt_file.exists():
        content = rt_file.read_text()
        assert "import" in content, "No imports in regression test"
        assert "test(" in content or "describe(" in content, "No test definitions found"
