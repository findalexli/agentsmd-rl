"""
Task: nextjs-turbopack-windows-path-forward-slash
Repo: vercel/next.js @ a21f3f4008a7d4c1778649d533de76b62dffabaa
PR:   92076

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The WINDOWS_PATH regex in turbopack's resolve/parse.rs determines whether
a request string is a Windows filesystem path.  We extract it and test
its matching behavior with Python's `re` module (which shares syntax with
Rust's `regex` crate for the patterns used here).
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
PARSE_RS = Path(REPO) / "turbopack/crates/turbopack-core/src/resolve/parse.rs"


def _get_windows_path_regex() -> re.Pattern:
    """Extract and compile the WINDOWS_PATH regex from parse.rs."""
    src = PARSE_RS.read_text()
    # The definition may span multiple lines due to formatting
    match = re.search(
        r'static\s+WINDOWS_PATH\s*:.*?Regex::new\(r"([^"]+)"\)',
        src,
        re.DOTALL,
    )
    assert match, "Could not find WINDOWS_PATH regex definition in parse.rs"
    return re.compile(match.group(1))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_forward_slash_windows_path():
    """Windows paths with forward slashes (e.g. C:/Users/...) must be recognized."""
    regex = _get_windows_path_regex()
    assert regex.search("C:/Users/demo/src/index.ts"), "C:/... should match"
    assert regex.search("D:/project/file.js"), "D:/... should match"
    assert regex.search("c:/lowercase/drive.txt"), "c:/... should match (lowercase)"
    assert regex.search("Z:/single"), "Z:/... should match"


# [pr_diff] fail_to_pass
def test_unc_path_not_mid_string():
    """Double-backslash should NOT match when embedded in the middle of a string."""
    regex = _get_windows_path_regex()
    # "foo\\bar" has two literal backslashes between foo and bar
    assert not regex.search("foo\\\\bar"), (
        "embedded \\\\ in middle of string should not be treated as a Windows/UNC path"
    )
    assert not regex.search("some/module\\\\internal"), (
        "embedded \\\\ after a normal path should not match"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_backslash_windows_path():
    """Traditional C:\\path format must still be recognized."""
    regex = _get_windows_path_regex()
    assert regex.search("C:\\Users\\demo\\src\\index.ts"), "C:\\ should match"
    assert regex.search("D:\\project\\file.js"), "D:\\ should match"
    assert regex.search("e:\\lower"), "e:\\ should match (lowercase)"


# [pr_diff] pass_to_pass
def test_unc_path_at_start():
    """UNC paths (\\\\server\\share) at start of string must still match."""
    regex = _get_windows_path_regex()
    assert regex.search("\\\\server\\share"), "\\\\server should match"
    assert regex.search("\\\\localhost\\c$"), "\\\\localhost should match"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_regex_valid_and_nontrivial():
    """The WINDOWS_PATH regex must compile and have non-trivial content."""
    regex = _get_windows_path_regex()
    # Pattern must contain a drive-letter matcher and a path separator
    assert "[A-Za-z]" in regex.pattern or "[a-zA-Z]" in regex.pattern, (
        "regex should contain a drive-letter character class"
    )
    assert len(regex.pattern) >= 10, (
        f"regex pattern too short ({len(regex.pattern)} chars) — likely a stub"
    )
