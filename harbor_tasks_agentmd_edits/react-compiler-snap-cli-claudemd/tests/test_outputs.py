"""
Task: react-compiler-snap-cli-claudemd
Repo: facebook/react @ 2d8e7f1ce358e8cddc3aae862007269b6bac04ba
PR:   35537

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
SNAP_SRC = Path(REPO) / "compiler" / "packages" / "snap" / "src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_files_parseable():
    """Modified TypeScript files have balanced braces (basic structural validity)."""
    files = [
        SNAP_SRC / "constants.ts",
        SNAP_SRC / "fixture-utils.ts",
        SNAP_SRC / "runner.ts",
        SNAP_SRC / "runner-watch.ts",
    ]
    for f in files:
        content = f.read_text()
        # Basic structural check: balanced braces
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 1, (
            f"{f.name}: unbalanced braces ({opens} open, {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_file_mechanism_removed():
    """testfilter.txt-based filtering must be removed from snap."""
    constants = (SNAP_SRC / "constants.ts").read_text()
    assert "FILTER_FILENAME" not in constants, (
        "constants.ts should not export FILTER_FILENAME"
    )
    assert "FILTER_PATH" not in constants, (
        "constants.ts should not export FILTER_PATH"
    )
    assert "testfilter.txt" not in constants, (
        "constants.ts should not reference testfilter.txt"
    )

    fixture_utils = (SNAP_SRC / "fixture-utils.ts").read_text()
    assert "readTestFilter" not in fixture_utils, (
        "fixture-utils.ts should not export readTestFilter"
    )
    # The debug field should not be in TestFilter type
    # Match "debug" as a property in the TestFilter type definition
    assert not re.search(r"debug\s*:", fixture_utils), (
        "TestFilter type should not have a debug property"
    )


# [pr_diff] fail_to_pass
def test_filter_option_removed():
    """runner.ts must not have the old --filter boolean option."""
    runner = (SNAP_SRC / "runner.ts").read_text()
    # The old --filter boolean option must be gone
    assert ".boolean('filter')" not in runner and '.boolean("filter")' not in runner, (
        "runner.ts should not define --filter as a boolean option"
    )
    # readTestFilter must not be imported or called
    assert "readTestFilter" not in runner, (
        "runner.ts should not import or use readTestFilter"
    )
    # FILTER_PATH must not be imported
    assert "FILTER_PATH" not in runner, (
        "runner.ts should not import FILTER_PATH"
    )


# [pr_diff] fail_to_pass
def test_debug_cli_option():
    """runner.ts must define a --debug / -d CLI option via yargs."""
    runner = (SNAP_SRC / "runner.ts").read_text()
    # Check for --debug boolean option
    assert ".boolean('debug')" in runner or '.boolean("debug")' in runner, (
        "runner.ts should define --debug as a boolean option"
    )
    # Check for -d alias
    assert re.search(r"\.alias\(['\"]d['\"],\s*['\"]debug['\"]\)", runner), (
        "runner.ts should alias -d to debug"
    )


# [pr_diff] fail_to_pass
def test_interactive_watch_mode():
    """runner-watch.ts must support interactive pattern entry and debug toggle."""
    watch = (SNAP_SRC / "runner-watch.ts").read_text()

    # RunnerState must have inputMode and inputBuffer for interactive pattern entry
    assert "inputMode" in watch, (
        "runner-watch.ts should have inputMode in RunnerState"
    )
    assert "inputBuffer" in watch, (
        "runner-watch.ts should have inputBuffer in RunnerState"
    )

    # Must handle 'p' key for pattern entry
    assert re.search(r"key\.name\s*===\s*['\"]p['\"]", watch), (
        "runner-watch.ts should handle 'p' key for pattern entry"
    )
    # Must handle 'd' key for debug toggle
    assert re.search(r"key\.name\s*===\s*['\"]d['\"]", watch), (
        "runner-watch.ts should handle 'd' key for debug toggle"
    )
    # Must handle 'a' key for running all tests
    assert re.search(r"key\.name\s*===\s*['\"]a['\"]", watch), (
        "runner-watch.ts should handle 'a' key to run all tests"
    )


# [pr_diff] fail_to_pass
def test_watch_runner_signature_updated():
    """makeWatchRunner must accept debugMode and optional initialPattern params."""
    watch = (SNAP_SRC / "runner-watch.ts").read_text()

    # makeWatchRunner should accept debugMode parameter
    assert re.search(r"debugMode\s*:\s*boolean", watch), (
        "makeWatchRunner should accept a debugMode: boolean parameter"
    )
    # makeWatchRunner should accept initialPattern parameter
    assert re.search(r"initialPattern\s*\??\s*:\s*string", watch), (
        "makeWatchRunner should accept an initialPattern parameter"
    )
    # Should NOT use readTestFilter anymore
    assert "readTestFilter" not in watch, (
        "runner-watch.ts should not import or use readTestFilter"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_constants_still_exports_paths():
    """constants.ts must still export FIXTURES_PATH and SNAPSHOT_EXTENSION."""
    constants = (SNAP_SRC / "constants.ts").read_text()
    assert "FIXTURES_PATH" in constants, (
        "constants.ts should still export FIXTURES_PATH"
    )
    assert "SNAPSHOT_EXTENSION" in constants, (
        "constants.ts should still export SNAPSHOT_EXTENSION"
    )


# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md creation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass

    # Must document yarn snap as the test runner
    assert "yarn snap" in content, (
        "CLAUDE.md should document 'yarn snap' as the test command"
    )
    # Must document the -p / --pattern flag
    assert "-p" in content and "pattern" in content.lower(), (
        "CLAUDE.md should document the -p/--pattern flag for filtering"
    )
    # Must document the -d / --debug flag
    assert "-d" in content and "debug" in content.lower(), (
        "CLAUDE.md should document the -d/--debug flag"
    )
    # Must document the -u / --update flag
    assert "-u" in content, (
        "CLAUDE.md should document the -u/--update flag"
    )


# [config_edit] fail_to_pass

    # Must reference the main compiler package
    assert "babel-plugin-react-compiler" in content, (
        "CLAUDE.md should reference babel-plugin-react-compiler package"
    )
    # Must reference HIR (core compiler concept)
    assert "HIR" in content, (
        "CLAUDE.md should document HIR (High-level Intermediate Representation)"
    )
    # Must reference the test fixtures directory
    assert "fixtures" in content.lower(), (
        "CLAUDE.md should reference the test fixtures"
    )
