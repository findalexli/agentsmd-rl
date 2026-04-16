"""
Tests for TanStack Router PR #6929: Fix retained promise refs

This PR fixes a memory leak where promise references were retained during
route loads and commits. The fix involves:
1. Changing const to let for promise variables
2. Setting promise references to undefined after resolution
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/router")
LOAD_MATCHES_FILE = REPO / "packages/router-core/src/load-matches.ts"
ROUTER_FILE = REPO / "packages/router-core/src/router.ts"


def test_load_matches_prevLoadPromise_cleanup():
    """
    Verify that prevLoadPromise is set to undefined after resolution in executeBeforeLoad.

    The fix changes const to let and adds cleanup to prevent retained reference.
    (fail_to_pass)
    """
    content = LOAD_MATCHES_FILE.read_text()

    # Find the executeBeforeLoad function section with the prevLoadPromise pattern
    # The fix requires:
    # 1. let prevLoadPromise (not const)
    # 2. prevLoadPromise = undefined inside the callback

    # Look for the pattern where prevLoadPromise is captured and then cleared
    pattern = r"let\s+prevLoadPromise\s*=\s*match\._nonReactive\.loadPromise"
    assert re.search(pattern, content), \
        "prevLoadPromise should be declared with 'let' (not const) to allow cleanup"

    # Verify the cleanup assignment exists
    assert "prevLoadPromise = undefined" in content, \
        "prevLoadPromise should be set to undefined after resolution"


def test_load_matches_loadPromise_cleanup_in_try_block():
    """
    Verify loadPromise is set to undefined after resolution in loadRouteMatch try block.

    The try block around line 836 should clean up loadPromise.
    (fail_to_pass)
    """
    content = LOAD_MATCHES_FILE.read_text()

    # Find the section with loaderPromise and loadPromise cleanup
    # The pattern should have both undefined assignments together
    lines = content.split('\n')

    found_cleanup = False
    for i, line in enumerate(lines):
        # Look for the pattern where both are cleaned up
        if "match._nonReactive.loaderPromise = undefined" in line:
            # Check nearby lines for loadPromise cleanup
            context = '\n'.join(lines[max(0, i-3):min(len(lines), i+5)])
            if "match._nonReactive.loadPromise = undefined" in context:
                found_cleanup = True
                break

    assert found_cleanup, \
        "loadPromise should be set to undefined alongside loaderPromise in the try block"


def test_load_matches_loadPromise_cleanup_after_sync_load():
    """
    Verify loadPromise is cleaned up after synchronous loader completion.

    Around line 928-930, when loaderIsRunningAsync is false, loadPromise should be cleared.
    (fail_to_pass)
    """
    content = LOAD_MATCHES_FILE.read_text()

    # Look for the pattern: after resolving loadPromise, set it to undefined
    # if (!loaderIsRunningAsync) {
    #   match._nonReactive.loaderPromise?.resolve()
    #   match._nonReactive.loadPromise?.resolve()
    #   match._nonReactive.loadPromise = undefined  <-- this should exist
    # }

    # Find the section with !loaderIsRunningAsync
    pattern = r"if\s*\(\s*!loaderIsRunningAsync\s*\)"
    match = re.search(pattern, content)
    assert match, "Could not find loaderIsRunningAsync check"

    # Get content after this match
    start_pos = match.end()
    section = content[start_pos:start_pos + 500]

    # Should have loadPromise cleanup
    assert "match._nonReactive.loadPromise = undefined" in section, \
        "loadPromise should be set to undefined after sync load completion"


def test_router_previousCommitPromise_cleanup():
    """
    Verify previousCommitPromise is set to undefined after resolution in router.ts.

    The fix changes const to let and adds cleanup.
    (fail_to_pass)
    """
    content = ROUTER_FILE.read_text()

    # The fix requires:
    # 1. let previousCommitPromise (not const)
    # 2. previousCommitPromise = undefined inside the callback

    pattern = r"let\s+previousCommitPromise\s*=\s*this\.commitLocationPromise"
    assert re.search(pattern, content), \
        "previousCommitPromise should be declared with 'let' (not const) to allow cleanup"

    assert "previousCommitPromise = undefined" in content, \
        "previousCommitPromise should be set to undefined after resolution"


def test_router_core_builds():
    """
    Verify the router-core package builds successfully after changes.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**__import__('os').environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-1000:]}"


def test_router_core_type_check():
    """
    Verify TypeScript types are correct.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**__import__('os').environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stderr[-1000:]}"


def test_router_core_lint():
    """
    Verify ESLint passes.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**__import__('os').environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-1000:]}"


def test_router_core_unit_tests():
    """
    Verify router-core unit tests pass, including load.test.ts which tests the
    promise handling code in load-matches.ts.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**__import__('os').environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"


def test_router_core_build_check():
    """
    Verify package build quality with publint and attw.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**__import__('os').environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, f"Build check failed:\n{result.stderr[-1000:]}"
