"""
Task: gradio-connection-lost-error-handling
Repo: gradio-app/gradio @ ac29df82a735c72c021c07e0816f78001147671b
PR:   12907

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All checks are structural (regex on source files) because the target
files are TypeScript/Svelte in a monorepo that requires a full pnpm install
+ build pipeline to compile. The Dockerfile only has node:22-slim without
the monorepo's dependency tree installed.
"""

import re
from pathlib import Path

REPO = "/workspace/gradio"

SUBMIT_TS = Path(REPO) / "client/js/src/utils/submit.ts"
DEPENDENCY_TS = Path(REPO) / "js/core/src/dependency.ts"
BLOCKS_SVELTE = Path(REPO) / "js/core/src/Blocks.svelte"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Structural check because: TypeScript requires full monorepo build (pnpm + all deps)
def test_submit_flags_connection_errors_as_broken():
    """submit.ts must detect BROKEN_CONNECTION_MSG and set broken flag dynamically."""
    content = SUBMIT_TS.read_text()

    # The fix compares output.error (or response.error) against BROKEN_CONNECTION_MSG
    # and passes the result as the `broken` field in fire_event.
    # Base code has `broken: false` hardcoded — no dynamic check in the error paths.

    # Must reference BROKEN_CONNECTION_MSG near a broken: assignment (not just anywhere)
    # Find all fire_event blocks with `broken:` and check at least one is computed
    broken_assignments = re.findall(r"broken\s*:\s*(\S+)", content)
    dynamic_broken = [
        v for v in broken_assignments if v.rstrip(",") not in ("false", "true")
    ]
    assert len(dynamic_broken) >= 1, (
        f"broken flag must be set dynamically (not just hardcoded); "
        f"found assignments: {broken_assignments}"
    )

    # The dynamic value must be derived from checking BROKEN_CONNECTION_MSG
    # (i.e., there must be a comparison against it somewhere before the fire_event)
    assert re.search(
        r"===?\s*BROKEN_CONNECTION_MSG|BROKEN_CONNECTION_MSG\s*===?",
        content,
    ), "Must compare error against BROKEN_CONNECTION_MSG to detect connection errors"


# [pr_diff] fail_to_pass
# Structural check because: TypeScript requires full monorepo build (pnpm + all deps)
def test_dispatch_short_circuits_on_connection_lost():
    """DependencyManager.dispatch() must return early when connection is lost."""
    content = DEPENDENCY_TS.read_text()

    # Find the dispatch method
    dispatch_match = re.search(
        r"async\s+dispatch\s*\([^)]*\)\s*(?::\s*Promise<void>\s*)?\{",
        content,
    )
    assert dispatch_match, "dispatch method not found in dependency.ts"

    # Get the first ~20 lines of the dispatch body (early return should be near top)
    dispatch_start = dispatch_match.end()
    dispatch_head = content[dispatch_start : dispatch_start + 500]

    # The fix adds `if (this.connection_lost) return;` near the top of dispatch.
    assert re.search(
        r"if\s*\(\s*this\.\w*connection\w*\s*\)\s*return",
        dispatch_head,
        re.IGNORECASE,
    ), "dispatch() must short-circuit with early return when connection is lost"


# [pr_diff] fail_to_pass
# Structural check because: TypeScript requires full monorepo build (pnpm + all deps)
def test_dependency_detects_broken_errors_and_sets_connection_lost():
    """DependencyManager must detect broken/session errors and set connection_lost."""
    content = DEPENDENCY_TS.read_text()

    # Must have a connection_lost boolean property initialized to false
    assert re.search(
        r"connection_lost\s*[=:]\s*false", content
    ), "DependencyManager must have a connection_lost property initialized to false"

    # Must check result.broken in the error handler
    assert re.search(
        r"result\.broken", content
    ), "Error handler must check result.broken to detect connection errors"

    # Must set connection_lost = true when a broken error is detected
    assert re.search(
        r"this\.connection_lost\s*=\s*true", content
    ), "Must set connection_lost = true when a broken error is detected"

    # Must have an on_connection_lost callback (called when connection is first lost)
    assert re.search(
        r"on_connection_lost|connection_lost_cb|connectionLost",
        content,
        re.IGNORECASE,
    ), "Must have a callback for notifying when connection is lost"


# [pr_diff] fail_to_pass
# Structural check because: Svelte requires full monorepo build (pnpm + all deps)
def test_blocks_has_reconnection_handler():
    """Blocks.svelte must have a connection-lost handler with reconnection logic."""
    content = BLOCKS_SVELTE.read_text()

    # Must define a connection lost handler function
    assert re.search(
        r"(?:function|const|let)\s+\w*connection.?lost\w*",
        content,
        re.IGNORECASE,
    ), "Blocks.svelte must define a connection lost handler function"

    # Must use setInterval for periodic reconnection attempts
    assert re.search(
        r"setInterval\s*\(", content
    ), "Must use setInterval for reconnection polling"

    # Must call reconnect() to check if server is back
    assert re.search(
        r"\.reconnect\s*\(", content
    ), "Must call reconnect() to detect server recovery"

    # Must reload the page when connection is restored
    assert re.search(
        r"(?:location\.reload|window\.location\.reload)\s*\(", content
    ), "Must reload the page when server connection is restored"


# [pr_diff] fail_to_pass
# Structural check because: TypeScript/Svelte requires full monorepo build
def test_connection_lost_callback_wired():
    """Blocks.svelte must pass connection-lost handler to DependencyManager."""
    dep_content = DEPENDENCY_TS.read_text()
    blocks_content = BLOCKS_SVELTE.read_text()

    # DependencyManager constructor must accept the callback parameter
    # Look for the callback in the constructor parameter list or assignment
    assert re.search(
        r"on_connection_lost|connection_lost_cb|connectionLost",
        dep_content,
        re.IGNORECASE,
    ), "DependencyManager constructor must accept a connection-lost callback"

    # Blocks.svelte must pass a connection-related handler to DependencyManager
    # The fix passes handle_connection_lost as arg to `new DependencyManager(...)`
    # Use greedy match to capture the full multi-line constructor call (includes nested parens)
    dm_construction = re.search(
        r"new\s+DependencyManager\s*\(([\s\S]*?)\);", blocks_content
    )
    assert dm_construction, "Must construct DependencyManager in Blocks.svelte"
    args = dm_construction.group(1)
    assert re.search(
        r"connection.?lost|handle_connection|on_connection",
        args,
        re.IGNORECASE,
    ), "Must pass a connection-lost handler to DependencyManager constructor"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """All three modified files must exist."""
    for path in [SUBMIT_TS, DEPENDENCY_TS, BLOCKS_SVELTE]:
        assert path.is_file(), f"Required file not found: {path}"


# [static] pass_to_pass
def test_files_not_stub():
    """Modified files must have substantial implementation (not stubs)."""
    for path in [SUBMIT_TS, DEPENDENCY_TS, BLOCKS_SVELTE]:
        content = path.read_text()
        lines = [
            line
            for line in content.splitlines()
            if line.strip()
            and not line.strip().startswith("//")
            and not line.strip().startswith("/*")
            and not line.strip().startswith("*")
        ]
        assert len(lines) >= 50, (
            f"{path.name} has only {len(lines)} non-empty non-comment lines — likely a stub"
        )


# [pr_diff] fail_to_pass
def test_reconnect_interval_cleanup():
    """Blocks.svelte must clean up reconnection interval on teardown."""
    content = BLOCKS_SVELTE.read_text()

    # Must have clearInterval to prevent memory leaks
    assert re.search(
        r"clearInterval\s*\(", content
    ), "Must call clearInterval to clean up reconnection polling"
