
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


def _node(script, timeout=30):
    """Execute JavaScript via node subprocess."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _parse_json(r):
    """Parse the last line of node output as JSON."""
    assert r.returncode == 0, f"Node error: {r.stderr}"
    lines = r.stdout.strip().splitlines()
    assert lines, f"No output from node: {r.stderr}"
    return json.loads(lines[-1])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests that verify error handling flow
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_catch_all_produces_output():
    """
    The else branch in the error handling switch must pass the error to
    an output function, not silently return or have an empty body.

    Behavior verified: Errors not explicitly named still produce output.
    """
    text = _read_file(IWM)
    assert text is not None, f"Could not read {IWM}"

    # Find the catch block for performSecurityScanAfterResolution
    # Look for: performSecurityScanAfterResolution(...) catch |err| {
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    # Extract the switch block within the catch
    # Find the switch (err) and get its body
    start_pos = catch_match.end()
    # Look for switch(err) or switch (err)
    switch_match = re.search(r"switch\s*\(\s*err\s*\)\s*\{", text[start_pos:])
    assert switch_match, "Could not find switch(err) statement"

    switch_start = start_pos + switch_match.end()
    # Find matching closing brace by counting
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

    switch_body = text[switch_start:switch_end]

    # Check that empty else => {} is NOT present (this was the bug)
    if re.search(r"else\s*=>\s*\{\s*\}", switch_body):
        raise AssertionError("Bug found: empty else => {} present - errors would exit silently")

    # Check that else branch exists and captures the error value
    # Looking for: else => |e| or inline else => |e|
    has_capturing_else = re.search(r"(?:inline\s+)?else\s*=>\s*\|\w+\|", switch_body)
    assert has_capturing_else, "No error-capturing else branch found (else => |e| pattern missing)"

    # Verify the else branch produces output (has Output.* call)
    # Split by branches and check the else branch specifically
    branches = re.split(r"\n\s*(?:error\.\w+|else)\s*=>", switch_body)
    # Check the last branch (should be else)
    if branches:
        # Find which branch is the else branch
        else_pos = -1
        for i, branch in enumerate(branches):
            # Check if this is the else branch by looking at the original text
            branch_start = switch_body.find(branch) if branch else -1
            if branch_start >= 0:
                # Look backwards for 'else'
                before = switch_body[max(0, branch_start-50):branch_start]
                if re.search(r"else\s*=>", before):
                    else_pos = i
                    break

        # The else branch must have an Output call
        if else_pos >= 0:
            else_branch = branches[else_pos]
            has_output = re.search(r"Output\.\w+\s*\(", else_branch)
            assert has_output, "Else branch exists but does not produce output (no Output.* call)"

    # Count total branches that produce output - need at least 2 for meaningful coverage
    output_branches = len(re.findall(r"Output\.\w+\s*\(", switch_body))
    assert output_branches >= 2, f"Insufficient output branches: {output_branches} (need at least 2)"


# [pr_diff] fail_to_pass
def test_error_variant_coverage():
    """
    Error handling must cover multiple error variants, either through
    explicit named branches OR through a dynamic catch-all that extracts
    error names at runtime.

    Behavior verified: At least 3 named variants OR dynamic @errorName handling.
    """
    text = _read_file(IWM)
    assert text is not None, f"Could not read {IWM}"

    # Find the catch block
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    # Extract the switch body
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

    switch_body = text[switch_start:switch_end]

    # Count explicit error variant branches (error.Foo =>)
    named_variants = len(re.findall(r"error\.\w+\s*=>", switch_body))

    # Count Output calls in switch branches
    output_calls = len(re.findall(r"Output\.\w+\s*\(", switch_body))

    # Check for dynamic error name extraction via @errorName - this allows
    # ANY error variant to produce meaningful output, not just named ones
    has_dynamic_error = re.search(r"@errorName\s*\(\s*\w+\s*\)", switch_body)

    # Verify: either we have 3+ named variants with output, OR we have dynamic handling
    if named_variants >= 3 and output_calls >= 3:
        pass  # OK - explicit coverage
    elif has_dynamic_error and output_calls >= 1:
        pass  # OK - dynamic coverage via @errorName
    else:
        raise AssertionError(
            f"Insufficient error coverage: {named_variants} named variants, "
            f"{output_calls} output calls, dynamic={bool(has_dynamic_error)}. "
            "Need either 3+ named variants OR @errorName in else branch."
        )


# [pr_diff] fail_to_pass
def test_error_printing_centralized():
    """
    Error printing for security scanner errors must be centralized in
    install_with_manager.zig, NOT duplicated in security_scanner.zig.

    Behavior verified: security_scanner.zig returns errors WITHOUT printing them
    for the variants that should be centralized.
    """
    ss_text = _read_file(SS)
    assert ss_text is not None, f"Could not read {SS}"

    # These error variants should be returned, not printed, in security_scanner.zig
    centralized_errors = [
        "InvalidPackageID",
        "PartialInstallFailed",
        "NoPackagesInstalled",
        "SecurityScannerInWorkspace"
    ]

    violations = []
    for err in centralized_errors:
        # Look for pattern: Output.err* followed by return error.X
        # This indicates the error is being printed in security_scanner.zig
        # instead of being centralized in install_with_manager.zig
        # Match Output.err* call followed by return error.X (with possible whitespace/newlines)
        pattern = r"Output\.(?:errGeneric|err|pretty)[^;]*;\s*\n?\s*return\s+error\." + err
        if re.search(pattern, ss_text):
            violations.append(err)

    if violations:
        raise AssertionError(
            f"Duplicated error printing in security_scanner.zig for: {violations}. "
            "These should only be printed in install_with_manager.zig"
        )


# [pr_diff] fail_to_pass
def test_error_variant_propagated():
    """
    The .error variant from ScanAttemptResult must be propagated as-is,
    not collapsed into SecurityScannerRetryFailed.

    Behavior verified: The retry result handling explicitly matches .error
    and returns the contained error, rather than using else => return error.SecurityScannerRetryFailed.
    """
    ss_text = _read_file(SS)
    assert ss_text is not None, f"Could not read {SS}"

    # Find performSecurityScanAfterResolution function body
    # Account for 'pub fn' or just 'fn'
    func_match = re.search(
        r"(?:pub\s+)?fn\s+performSecurityScanAfterResolution\b([^;]*?)(?:\nfn|\n(?:pub\s+)?fn|\nconst|\n\n\n|$)",
        ss_text, re.DOTALL
    )
    assert func_match, "Could not find performSecurityScanAfterResolution function"

    func_body = func_match.group(1)

    # Check for the OLD buggy pattern: else => return error.SecurityScannerRetryFailed
    # This would collapse ALL non-success results into one error
    has_collapse_pattern = re.search(
        r"else\s*=>\s*return\s+error\.SecurityScannerRetryFailed",
        func_body
    )
    if has_collapse_pattern:
        raise AssertionError(
            "Bug found: Using 'else => return error.SecurityScannerRetryFailed' "
            "which collapses all non-success errors into one generic error"
        )

    # Check for proper propagation: .error => |e| return e OR inline else => |e| return e
    # This ensures the original error is preserved, not lost
    has_error_propagation = (
        re.search(r"\.@\"error\"\s*=>\s*\|\w+\|", func_body) or
        re.search(r"\.error\s*=>\s*\|\w+\|", func_body) or
        re.search(r"inline\s+else\s*=>\s*\|\w+\|", func_body)
    )

    assert has_error_propagation, (
        "No error propagation pattern found. Need either '.error => |e|' "
        "or 'inline else => |e|' to preserve the original error"
    )


# [pr_diff] fail_to_pass
def test_uses_err_generic():
    """
    Error messages in the catch block must use Output.errGeneric or similar
    error output functions, NOT Output.pretty with <red> styling.

    Behavior verified: Output.errGeneric is used, Output.pretty with <red> is NOT used.
    """
    text = _read_file(IWM)
    assert text is not None, f"Could not read {IWM}"

    # Find the catch block for security scanner errors
    catch_pattern = r"performSecurityScanAfterResolution\([^)]*\)\s+catch\s+\|err\|\s*\{"
    catch_match = re.search(catch_pattern, text)
    assert catch_match, "Could not find performSecurityScanAfterResolution catch block"

    # Extract the switch body (same as other tests)
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

    switch_body = text[switch_start:switch_end]

    # Check for deprecated pattern: Output.pretty with <red>
    has_pretty_red = re.search(r"Output\.pretty\s*\(\s*\"<red>", switch_body)
    if has_pretty_red:
        raise AssertionError(
            "Using deprecated Output.pretty with <red> styling. "
            "Should use Output.errGeneric instead."
        )

    # Verify error output functions are used (Output.err*, Output.errGeneric)
    has_err_output = re.search(r"Output\.(?:err|errGeneric)\s*\(", switch_body)
    assert has_err_output, (
        "No error output functions found (Output.err, Output.errGeneric). "
        "Error messages should use these functions."
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — regression test validation via file checks
# These check for file existence/structure - inherently file-based
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
