"""
Task: bun-install-scanner-silent-exit
Repo: oven-sh/bun @ 1d50d640f8fec6ce2d144f0cfd204e30da373c64
PR:   28196

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
IWM = Path(REPO) / "src/install/PackageManager/install_with_manager.zig"
SS = Path(REPO) / "src/install/PackageManager/security_scanner.zig"


def _get_scanner_error_block():
    """Extract the security scanner error switch block from install_with_manager.zig."""
    text = IWM.read_text()
    m = re.search(
        r"performSecurityScanAfterResolution.*?catch\s*\|err\|\s*\{(.*?)\n\s*Global\.exit",
        text,
        re.DOTALL,
    )
    assert m, "Could not find security scanner error switch in install_with_manager.zig"
    return m.group(1)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_catch_all_produces_output():
    """The empty else => {} catch-all must be replaced with Output.* error messages."""
    block = _get_scanner_error_block()

    # The buggy pattern: else => {} with no error output
    assert not re.search(
        r"else\s*=>\s*\{\s*\}", block
    ), "Catch-all else => {} is still empty — silent exit bug not fixed"

    # If an else branch exists, it must contain an Output.* call with a non-empty message
    else_m = re.search(r"else\s*=>\s*\|?\w*\|?\s*\{([^}]*)\}", block, re.DOTALL)
    if else_m:
        body = else_m.group(1).strip()
        assert body, "Catch-all else branch has empty body"
        assert re.search(
            r"Output\.\w+\s*\(", body
        ), "Catch-all else branch doesn't use Output.* for error messages"
        assert not re.search(
            r'Output\.\w+\(\s*""\s*,', body
        ), "Catch-all else prints an empty string message"

    # Must have at least 2 branches producing Output.* calls
    output_branches = len(
        re.findall(r"=>\s*(?:\|[^|]*\|)?\s*\{[^}]*Output\.\w+\s*\(", block)
    )
    assert output_branches >= 2, (
        f"Only {output_branches} error branch(es) produce Output.* — need at least 2"
    )


# [pr_diff] fail_to_pass
def test_error_variant_coverage():
    """All error variants must produce diagnostic output, either via named branches or dynamic formatting."""
    block = _get_scanner_error_block()

    # Strategy A: 3+ individually named error variants with Output calls
    named = set(re.findall(r"error\.(\w+)\s*=>", block))
    output_calls = len(re.findall(r"Output\.\w+\(", block))
    strategy_a = len(named) >= 3 and output_calls >= 3

    # Strategy B: catch-all that formats error name dynamically via @errorName
    strategy_b = bool(
        re.search(r"else\s*=>\s*\|(\w+)\|.*?@errorName\(\1\)", block, re.DOTALL)
    )

    assert strategy_a or strategy_b, (
        f"Insufficient error variant coverage: {len(named)} named variants, "
        f"{output_calls} Output calls, dynamic catch-all: {strategy_b}"
    )


# [pr_diff] fail_to_pass
def test_error_printing_centralized():
    """Error output must be centralized in install_with_manager.zig, not duplicated in security_scanner.zig."""
    text = SS.read_text()

    for err in [
        "InvalidPackageID",
        "PartialInstallFailed",
        "NoPackagesInstalled",
        "SecurityScannerInWorkspace",
    ]:
        pat = r"Output\.(?:errGeneric|pretty)\([^)]*\).*?\n[^}]*?return error\." + err
        assert not re.search(pat, text, re.DOTALL), (
            f"Duplicate error printing for {err} still in security_scanner.zig — "
            "error output should be centralized in the caller"
        )


# [pr_diff] fail_to_pass
def test_error_variant_propagated():
    """The .error variant from retry result must be propagated, not collapsed into SecurityScannerRetryFailed."""
    text = SS.read_text()

    m = re.search(
        r"fn performSecurityScanAfterResolution\b(.*?)(?:\nfn |\npub fn |\Z)",
        text,
        re.DOTALL,
    )
    assert m, "Could not find performSecurityScanAfterResolution function"
    func = m.group(1)

    # BAD: catch-all that collapses all variants into SecurityScannerRetryFailed
    has_collapse = bool(
        re.search(r"else\s*=>\s*return\s+error\.SecurityScannerRetryFailed", func)
    )
    assert not has_collapse, (
        ".error variant still collapsed into SecurityScannerRetryFailed — "
        "original error information is lost"
    )

    # GOOD: explicit error propagation
    has_prop = (
        bool(re.search(r'\.@"error"\s*=>\s*\|', func))
        or bool(re.search(r"\.error\s*=>\s*\|", func))
        or bool(re.search(r"inline\s+else\s*=>\s*\|", func))
    )
    # Either explicit propagation or collapse removed (partial fix) is acceptable
    assert has_prop or not has_collapse, (
        "No explicit error propagation pattern found in performSecurityScanAfterResolution"
    )


# [pr_diff] fail_to_pass
def test_uses_err_generic():
    """Error messages in the scanner switch must use Output.errGeneric, not Output.pretty with raw formatting."""
    block = _get_scanner_error_block()

    has_pretty_errors = bool(re.search(r'Output\.pretty\s*\(\s*"<red>', block))
    has_err_output = bool(re.search(r"Output\.err", block))

    assert has_err_output, "No Output.err* calls found in error handling block"
    assert not has_pretty_errors, (
        "Uses Output.pretty with <red> formatting for errors — "
        "should use Output.errGeneric per src/CLAUDE.md conventions"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_workspace_error_preserved():
    """SecurityScannerInWorkspace error handling must still be present in install_with_manager.zig."""
    text = IWM.read_text()
    assert "SecurityScannerInWorkspace" in text, (
        "SecurityScannerInWorkspace handling removed from install_with_manager.zig"
    )


# [pr_diff] pass_to_pass
def test_error_types_preserved():
    """security_scanner.zig must still return proper error types."""
    text = SS.read_text()
    expected_errors = [
        "InvalidPackageID",
        "PartialInstallFailed",
        "NoPackagesInstalled",
        "SecurityScannerInWorkspace",
    ]
    found = sum(1 for e in expected_errors if f"return error.{e}" in text)
    assert found >= 3, (
        f"Only {found}/4 expected error types still returned in security_scanner.zig"
    )


# [static] pass_to_pass
def test_anti_stub():
    """Both Zig source files must have substantial content (not stubbed out)."""
    iwm_lines = len(IWM.read_text().splitlines())
    ss_lines = len(SS.read_text().splitlines())
    assert iwm_lines > 200, (
        f"install_with_manager.zig has only {iwm_lines} lines — suspiciously small"
    )
    assert ss_lines > 50, (
        f"security_scanner.zig has only {ss_lines} lines — suspiciously small"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — CLAUDE.md:28 @ 1d50d640f8
def test_regression_test_location():
    """Regression test for issue #28193 must be placed in test/regression/issue/28193.test.ts per CLAUDE.md:28."""
    test_file = Path(REPO) / "test/regression/issue/28193.test.ts"
    assert test_file.exists(), (
        "No regression test at test/regression/issue/28193.test.ts — "
        "CLAUDE.md:28 requires issue tests at test/regression/issue/${issueNumber}.test.ts"
    )

    content = test_file.read_text()
    lines = content.splitlines()
    assert len(lines) > 5, f"Test file has only {len(lines)} lines — needs real content"

    test_keywords = len(re.findall(r"test\(|describe\(|expect\(|assert|it\(", content))
    assert test_keywords > 0, "Test file has no test keywords (test, describe, expect, assert, it)"


# [agent_config] fail_to_pass — test/CLAUDE.md:28 @ 1d50d640f8
def test_regression_test_uses_harness():
    """Regression test must import bunExe and bunEnv from 'harness' per test/CLAUDE.md:28."""
    test_file = Path(REPO) / "test/regression/issue/28193.test.ts"
    assert test_file.exists(), "Regression test file does not exist"
    content = test_file.read_text()

    assert re.search(r'from\s+"harness"', content), (
        "Test does not import from 'harness' — test/CLAUDE.md:28 requires bunExe/bunEnv from harness"
    )
    assert "bunExe" in content, (
        "Test does not use bunExe — test/CLAUDE.md:28 requires bunExe() when spawning Bun"
    )
    assert "bunEnv" in content, (
        "Test does not use bunEnv — test/CLAUDE.md:28 requires bunEnv when spawning Bun"
    )


# [agent_config] pass_to_pass — CLAUDE.md:101 @ 1d50d640f8
def test_exit_code_assertion_last():
    """Regression test must assert stdout/stderr content before asserting exit code (CLAUDE.md:101)."""
    test_file = Path(REPO) / "test/regression/issue/28193.test.ts"
    assert test_file.exists(), "Regression test file does not exist"
    content = test_file.read_text()
    lines = content.splitlines()

    exit_code_lines = [i for i, l in enumerate(lines) if re.search(r"expect\s*\(\s*exitCode\s*\)", l)]
    content_lines = [i for i, l in enumerate(lines) if re.search(r"expect\s*\(\s*std(?:out|err)\s*\)", l)]

    assert exit_code_lines, "No exit code assertions found in regression test"
    assert content_lines, "No stdout/stderr content assertions found in regression test"

    for ec_line in exit_code_lines:
        has_prior = any(ca < ec_line for ca in content_lines)
        assert has_prior, (
            f"exit code assertion at line {ec_line + 1} has no prior stdout/stderr assertion — "
            "CLAUDE.md:101 requires content assertions before exit code assertions"
        )


# [agent_config] fail_to_pass — CLAUDE.md:100 @ 1d50d640f8
def test_regression_test_uses_tempdir():
    """Regression test must use tempDir from 'harness', not tmpdirSync/mkdtempSync per CLAUDE.md:100."""
    test_file = Path(REPO) / "test/regression/issue/28193.test.ts"
    assert test_file.exists(), "Regression test file does not exist"
    content = test_file.read_text()

    assert "tempDir" in content, (
        "Test does not use tempDir — CLAUDE.md:100 requires tempDir from 'harness' for temp directories"
    )
    assert "tmpdirSync" not in content, (
        "Test uses tmpdirSync — CLAUDE.md:100 says use tempDir from 'harness' instead"
    )
    assert "mkdtempSync" not in content, (
        "Test uses mkdtempSync — CLAUDE.md:100 says use tempDir from 'harness' instead"
    )
