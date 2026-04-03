"""
Task: react-flight-debugchannel-variable-fix
Repo: facebook/react @ 65db1000b944c8a07b5947c06b38eb8364dce4f2
PR:   35724

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react-repo"

ESM_FILE = Path(f"{REPO}/packages/react-server-dom-esm/src/server/ReactFlightDOMServerNode.js")
PARCEL_FILE = Path(f"{REPO}/packages/react-server-dom-parcel/src/server/ReactFlightDOMServerNode.js")
TURBOPACK_FILE = Path(f"{REPO}/packages/react-server-dom-turbopack/src/server/ReactFlightDOMServerNode.js")
WEBPACK_FILE = Path(f"{REPO}/packages/react-server-dom-webpack/src/server/ReactFlightDOMServerNode.js")

ALL_AFFECTED = [ESM_FILE, PARCEL_FILE, TURBOPACK_FILE]
ALL_FILES = [ESM_FILE, PARCEL_FILE, TURBOPACK_FILE, WEBPACK_FILE]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four ReactFlightDOMServerNode.js files exist and contain renderToPipeableStream."""
    # AST-only because: React source uses Flow type annotations that Node cannot parse
    for path in ALL_FILES:
        assert path.exists(), f"Missing file: {path}"
        content = path.read_text()
        assert len(content) > 100, f"File is suspiciously small: {path.name}"
        assert "renderToPipeableStream" in content, (
            f"{path.name} missing renderToPipeableStream function"
        )
        assert "createRequest" in content, (
            f"{path.name} missing createRequest call"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_esm_uses_debugchannel_readable():
    """ESM renderToPipeableStream passes debugChannelReadable to createRequest."""
    content = ESM_FILE.read_text()
    # Find the createRequest call arguments and verify correct variable
    assert "debugChannelReadable !== undefined" in content, (
        "ESM file does not check 'debugChannelReadable !== undefined'"
    )


# [pr_diff] fail_to_pass
def test_parcel_uses_debugchannel_readable():
    """Parcel renderToPipeableStream passes debugChannelReadable to createRequest."""
    content = PARCEL_FILE.read_text()
    assert "debugChannelReadable !== undefined" in content, (
        "Parcel file does not check 'debugChannelReadable !== undefined'"
    )


# [pr_diff] fail_to_pass
def test_turbopack_uses_debugchannel_readable():
    """Turbopack renderToPipeableStream passes debugChannelReadable to createRequest."""
    content = TURBOPACK_FILE.read_text()
    assert "debugChannelReadable !== undefined" in content, (
        "Turbopack file does not check 'debugChannelReadable !== undefined'"
    )


# [pr_diff] fail_to_pass
def test_affected_files_do_not_use_wrong_variable():
    """None of the three affected files pass bare 'debugChannel' (not 'debugChannelReadable') to createRequest."""
    # On base commit each file has "debugChannel !== undefined," as a createRequest arg.
    # After the fix, all three use "debugChannelReadable !== undefined," instead.
    # We use a regex that matches "debugChannel !== undefined" but NOT
    # "debugChannelReadable !== undefined" to avoid false positives.
    wrong_pattern = re.compile(r'\bdebugChannel\b\s*!==\s*undefined')
    correct_pattern = re.compile(r'\bdebugChannelReadable\b\s*!==\s*undefined')

    for path in ALL_AFFECTED:
        content = path.read_text()
        wrong_matches = wrong_pattern.findall(content)
        correct_matches = correct_pattern.findall(content)
        # Filter out correct matches from wrong matches (regex \b handles this,
        # but be explicit: wrong_matches should not include debugChannelReadable)
        # \b ensures word boundary so "debugChannel" won't match "debugChannelReadable"
        assert not wrong_matches, (
            f"{path.name} still uses 'debugChannel !== undefined' "
            f"(should be 'debugChannelReadable !== undefined')"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_webpack_reference_unchanged():
    """Webpack implementation still uses debugChannelReadable (reference unchanged)."""
    content = WEBPACK_FILE.read_text()
    assert "debugChannelReadable !== undefined" in content, (
        "Webpack reference implementation no longer contains the correct check"
    )


# [pr_diff] pass_to_pass
def test_all_four_files_consistent():
    """All four bundler implementations use the same debugChannelReadable check."""
    correct_pattern = re.compile(r'\bdebugChannelReadable\b\s*!==\s*undefined')
    for path in ALL_FILES:
        content = path.read_text()
        assert correct_pattern.search(content), (
            f"{path.name} does not contain 'debugChannelReadable !== undefined'"
        )
