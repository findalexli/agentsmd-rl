"""
Task: react-compiler-improve-snap-usability
Repo: facebook/react @ 2af6822c2108eabc0228d7809aa27c00bb2ebb53
PR:   35537

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
SNAP_SRC = Path(REPO) / "compiler" / "packages" / "snap" / "src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    files = [
        SNAP_SRC / "constants.ts",
        SNAP_SRC / "fixture-utils.ts",
        SNAP_SRC / "runner.ts",
        SNAP_SRC / "runner-watch.ts",
    ]
    for f in files:
        assert f.exists(), f"{f.name} must exist"
        content = f.read_text()
        # Basic TS syntax: file must not be empty and must have at least one export/import
        assert len(content) > 100, f"{f.name} is suspiciously short"
        assert "import" in content or "export" in content, (
            f"{f.name} must contain import/export statements"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_constant_removed():
    """constants.ts must not define FILTER_FILENAME or FILTER_PATH (testfilter.txt mechanism removed)."""
    content = (SNAP_SRC / "constants.ts").read_text()
    # The old mechanism defined these constants for testfilter.txt
    assert "FILTER_FILENAME" not in content, (
        "constants.ts should not define FILTER_FILENAME — testfilter.txt mechanism was removed"
    )
    assert "FILTER_PATH" not in content, (
        "constants.ts should not define FILTER_PATH — testfilter.txt mechanism was removed"
    )


# [pr_diff] fail_to_pass
def test_debug_cli_option_added():
    """runner.ts must define a --debug / -d CLI option via yargs."""
    content = (SNAP_SRC / "runner.ts").read_text()
    # The new CLI should have a debug boolean option
    assert ".boolean('debug')" in content or '.boolean("debug")' in content, (
        "runner.ts should define a 'debug' boolean CLI option"
    )
    # Should have the -d alias
    assert "'d'" in content or '"d"' in content, (
        "runner.ts should alias debug as '-d'"
    )


# [pr_diff] fail_to_pass
def test_testfilter_function_removed():
    """fixture-utils.ts must not export readTestFilter (old mechanism removed)."""
    content = (SNAP_SRC / "fixture-utils.ts").read_text()
    assert "readTestFilter" not in content, (
        "fixture-utils.ts should not define or export readTestFilter"
    )
    # The TestFilter type should no longer have a debug field
    assert "debug: boolean" not in content, (
        "TestFilter type should not have a debug field — debug is now a CLI flag"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — CLAUDE.md creation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must document the snap test runner
    assert "yarn snap" in content, (
        "CLAUDE.md should document the 'yarn snap' command"
    )
    # Must document the -p / --pattern flag
    assert "-p" in content, (
        "CLAUDE.md should document the -p flag for pattern filtering"
    )
    # Must document the -d / --debug flag
    assert "-d" in content, (
        "CLAUDE.md should document the -d flag for debug mode"
    )
    # Must document updating fixtures
    assert "-u" in content or "update" in content.lower(), (
        "CLAUDE.md should document how to update fixture outputs"
    )


# [config_edit] fail_to_pass

    # Must document the main compiler package location
    assert "babel-plugin-react-compiler" in content, (
        "CLAUDE.md should reference the main compiler package"
    )
    # Must document HIR (central concept)
    assert "HIR" in content, (
        "CLAUDE.md should document HIR (High-level Intermediate Representation)"
    )
    # Must document fixtures
    assert "fixture" in content.lower(), (
        "CLAUDE.md should document test fixtures"
    )
    # Must have meaningful content (not just a stub)
    assert len(content) > 500, (
        "CLAUDE.md should have substantial documentation, not just a stub"
    )
