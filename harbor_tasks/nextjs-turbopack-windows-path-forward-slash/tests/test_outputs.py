"""
Task: nextjs-turbopack-windows-path-forward-slash
Repo: vercel/next.js @ a21f3f4008a7d4c1778649d533de76b62dffabaa
PR:   92076

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

These tests validate the WINDOWS_PATH regex fix using actual code execution
to verify the behavior, not just pattern matching.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

# Use /workspace/next.js if it exists (Docker environment), else /workspace/repo
REPO = "/workspace/next.js" if Path("/workspace/next.js").exists() else "/workspace/repo"
PARSE_RS = Path(REPO) / "turbopack/crates/turbopack-core/src/resolve/parse.rs"


def _get_windows_path_regex_pattern() -> str:
    """Extract the WINDOWS_PATH regex pattern from parse.rs."""
    src = PARSE_RS.read_text()
    match = re.search(
        r'static\s+WINDOWS_PATH\s*:.*?Regex::new\(r"([^"]+)"\)',
        src,
        re.DOTALL,
    )
    assert match, "Could not find WINDOWS_PATH regex definition in parse.rs"
    return match.group(1)


def _check_regex_behavior(pattern: str, test_cases: list, should_match: bool) -> list:
    """
    Execute Python code via subprocess to test regex behavior.
    Returns list of failures.
    """
    failures = []
    for test_input in test_cases:
        code = f'''
import re
pattern = r"{pattern}"
regex = re.compile(pattern)
result = regex.search(r"{test_input}")
print("MATCH" if result else "NO_MATCH")
'''
        r = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            failures.append(f"{test_input}: subprocess error: {r.stderr}")
            continue
        output = r.stdout.strip()
        if should_match and output != "MATCH":
            failures.append(f"{test_input}: expected MATCH, got {output}")
        elif not should_match and output != "NO_MATCH":
            failures.append(f"{test_input}: expected NO_MATCH, got {output}")
    return failures


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests using subprocess
# ---------------------------------------------------------------------------


def test_forward_slash_windows_path():
    """
    Windows paths with forward slashes (e.g. C:/Users/...) must be recognized.

    This test uses subprocess.run() to execute Python code that validates
    the regex behavior. The fix changes the regex from:
        ^[A-Za-z]:\\\\|\\\\\\
    to:
        ^[A-Za-z]:[/\\\\]|^\\\\\\
    The key change is adding [/\\\\] to match both forward and backward slashes.
    """
    pattern = _get_windows_path_regex_pattern()

    # Test cases that should match after the fix
    test_cases = [
        "C:/Users/demo/src/index.ts",
        "D:/project/file.js",
        "c:/lowercase/drive.txt",
        "Z:/single",
        "E:/path/to/file",
    ]

    failures = _check_regex_behavior(pattern, test_cases, should_match=True)
    assert not failures, f"Forward slash paths not recognized: {failures}"


def test_unc_path_not_mid_string():
    """
    Double-backslash should NOT match when embedded in the middle of a string.

    The fix anchors the UNC path pattern with ^ so it only matches at start.
    Before fix: ^[A-Za-z]:\\\\|\\\\\\\n    After fix:  ^[A-Za-z]:[/\\\\]|^\\\\\\

    The second alternation now has ^ anchor, preventing mid-string matches.
    """
    pattern = _get_windows_path_regex_pattern()

    # Test cases that should NOT match (embedded backslashes)
    test_cases = [
        "foo\\\\bar",  # embedded in middle
        "some/module\\\\internal",  # after normal path
        "path\\\\to\\\\file",  # multiple embedded
    ]

    failures = _check_regex_behavior(pattern, test_cases, should_match=False)
    assert not failures, f"Embedded backslashes incorrectly matched: {failures}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks using subprocess
# ---------------------------------------------------------------------------


def test_backslash_windows_path():
    """
    Traditional C:\\\\path format must still be recognized (regression test).

    The fix should not break existing backslash path support.
    """
    pattern = _get_windows_path_regex_pattern()

    test_cases = [
        "C:\\\\Users\\\\demo\\\\src\\\\index.ts",
        "D:\\\\project\\\\file.js",
        "e:\\\\lower",
        "X:\\\\path",
    ]

    failures = _check_regex_behavior(pattern, test_cases, should_match=True)
    assert not failures, f"Backslash paths not recognized: {failures}"


def test_unc_path_at_start():
    """
    UNC paths (\\\\server\\\\share) at start of string must still match.

    The fix preserves UNC path matching by anchoring it to start with ^.
    """
    pattern = _get_windows_path_regex_pattern()

    test_cases = [
        "\\\\\\\\server\\\\share",
        "\\\\\\\\localhost\\\\c$",
        "\\\\\\\\network\\\\resource",
    ]

    failures = _check_regex_behavior(pattern, test_cases, should_match=True)
    assert not failures, f"UNC paths not recognized: {failures}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural validation
# ---------------------------------------------------------------------------


def test_regex_valid_and_nontrivial():
    """The WINDOWS_PATH regex must have non-trivial content with proper structure."""
    pattern = _get_windows_path_regex_pattern()

    # Pattern must contain a drive-letter matcher
    assert "[A-Za-z]" in pattern or "[a-zA-Z]" in pattern, (
        "regex should contain a drive-letter character class"
    )
    # Should have alternation for drive vs UNC paths
    assert "|" in pattern, "regex should have alternation (|) for drive vs UNC paths"
    # Should anchor to start
    assert "^" in pattern, "regex should anchor to start of string"
    # Should be non-trivial length
    assert len(pattern) >= 10, (
        f"regex pattern too short ({len(pattern)} chars) — likely a stub"
    )


def test_regex_has_forward_slash_support():
    """
    The regex must explicitly support forward slashes in Windows paths.

    The fix adds [/\\\\] character class to match both / and \\\\ after drive letter.
    """
    pattern = _get_windows_path_regex_pattern()

    # Check for forward slash support in the pattern
    assert "[/\\\\\\\\]" in pattern or "[\\\\\\\\/]" in pattern or "/" in pattern, (
        f"regex should support forward slashes: {pattern}"
    )


def test_regex_has_proper_unc_anchor():
    """
    The UNC path alternation must be anchored to start of string.

    The fix changes \\|\\\\\\\\ to |^\\\\\\\\, adding the ^ anchor.
    """
    pattern = _get_windows_path_regex_pattern()

    # The pattern should have ^ anchor before the UNC part
    # Looking for pattern like |^\\\\ or ^[A-Za-z]:...|^\\\\
    unc_parts = pattern.split("|")
    assert len(unc_parts) >= 2, "regex should have alternation for UNC paths"

    # Second alternation (UNC) should start with ^
    unc_pattern = unc_parts[1]
    assert unc_pattern.startswith("^"), (
        f"UNC pattern should be anchored with ^: {unc_pattern}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository quality gates
# ---------------------------------------------------------------------------


def test_turbopack_core_crate_structure():
    """Turbopack-core crate has expected structure with src/ and Cargo.toml."""
    crate_dir = Path(REPO) / "turbopack/crates/turbopack-core"
    assert crate_dir.is_dir(), f"turbopack-core crate dir missing: {crate_dir}"
    assert (crate_dir / "Cargo.toml").is_file(), "Cargo.toml missing"
    assert (crate_dir / "src").is_dir(), "src/ directory missing"
    assert (crate_dir / "src/resolve/parse.rs").is_file(), "parse.rs missing"


def test_parse_rs_has_unit_tests():
    """parse.rs contains inline unit tests (#[cfg(test)] mod tests)."""
    src = PARSE_RS.read_text()
    assert "#[cfg(test)]" in src, "parse.rs missing #[cfg(test)] module"
    assert "mod tests" in src, "parse.rs missing tests module"
    test_fns = re.findall(r"#\[test\]\s*\n\s*fn\s+(\w+)", src)
    assert len(test_fns) >= 2, f"Expected at least 2 test functions, found: {len(test_fns)}"


def test_request_enum_variants():
    """Request enum has expected variants including Windows variant."""
    src = PARSE_RS.read_text()
    enum_match = re.search(r"pub enum Request\s*\{(.+?)\n\}", src, re.DOTALL)
    assert enum_match, "Could not find Request enum definition"
    enum_body = enum_match.group(1)
    variants_with_body = ["Windows", "Module", "Relative", "Raw"]
    for variant in variants_with_body:
        pattern = rf"\b{variant}\s*\{{"
        assert re.search(pattern, enum_body), f"Request enum missing {variant} variant"
    assert re.search(r"\bEmpty\s*,", enum_body), "Request enum missing Empty variant"


def test_windows_path_regex_well_formed():
    """WINDOWS_PATH regex definition follows expected patterns for Windows paths."""
    pattern = _get_windows_path_regex_pattern()

    assert "[A-Za-z]" in pattern or "[a-zA-Z]" in pattern, (
        "WINDOWS_PATH should match drive letters"
    )
    assert ":" in pattern, "WINDOWS_PATH should expect colon after drive letter"
    assert "|" in pattern, "WINDOWS_PATH should have alternation (|) for drive vs UNC paths"
    assert "^" in pattern, "WINDOWS_PATH should anchor to start of string"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Cargo/rustc availability check
# ---------------------------------------------------------------------------


def test_cargo_available():
    """
    Cargo/rustc are available for building and testing.

    This is a lightweight check that the Rust toolchain is installed.
    If cargo is not available, subsequent cargo-based tests will skip.
    """
    # Find cargo in PATH or common locations
    cargo_paths = ["cargo"]
    home = Path.home()
    if (home / ".cargo/bin/cargo").exists():
        cargo_paths.insert(0, str(home / ".cargo/bin/cargo"))

    for cargo_path in cargo_paths:
        try:
            r = subprocess.run(
                [cargo_path, "--version"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if r.returncode == 0:
                assert "cargo" in r.stdout.lower(), f"Unexpected cargo output: {r.stdout}"
                return
        except FileNotFoundError:
            continue

    pytest.skip("Cargo not available in PATH")


def test_parse_rs_compiles():
    """
    parse.rs compiles without syntax errors.

    Uses cargo check to verify the file is syntactically valid Rust.
    This test runs cargo check on the turbopack-core crate.
    """
    # Find cargo in PATH or common locations
    cargo_paths = ["cargo"]
    home = Path.home()
    if (home / ".cargo/bin/cargo").exists():
        cargo_paths.insert(0, str(home / ".cargo/bin/cargo"))

    cargo_path = None
    for path in cargo_paths:
        try:
            subprocess.run([path, "--version"], capture_output=True, timeout=5)
            cargo_path = path
            break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if cargo_path is None:
        pytest.skip("Cargo not available for compilation")

    r = subprocess.run(
        [cargo_path, "check", "--package", "turbopack-core", "--lib"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    if r.returncode != 0:
        # Check if it's a linker issue (expected in some environments)
        if "linker" in r.stderr.lower() and "not found" in r.stderr.lower():
            pytest.skip(f"Linker not available for compilation: {r.stderr}")
        assert r.returncode == 0, f"cargo check failed: {r.stderr[-1000:]}"
