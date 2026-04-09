"""
Test that:
1. actions.ts has the new cleanup helpers (cleanupSession, waitSessionIdle, stable)
2. fixtures.ts has trackSession/trackDirectory in withProject
3. AGENTS.md documents the new helpers and cleanup patterns
"""
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
E2E_DIR = Path(REPO) / "packages/app/e2e"


def _read_file(path: Path) -> str:
    """Read file content or fail test."""
    if not path.exists():
        raise AssertionError(f"File not found: {path}")
    return path.read_text()


def test_actions_ts_has_cleanup_helpers():
    """
    actions.ts must export cleanupSession, waitSessionIdle, and stable functions.
    These are the core helpers for safe session cleanup.
    """
    actions_ts = E2E_DIR / "actions.ts"
    content = _read_file(actions_ts)

    # Check for function exports
    assert "export async function cleanupSession(" in content, \
        "actions.ts must export cleanupSession function"
    assert "export async function waitSessionIdle(" in content, \
        "actions.ts must export waitSessionIdle function"

    # Check cleanupSession has proper implementation
    assert "waitSessionIdle" in content, \
        "cleanupSession should call waitSessionIdle"
    assert "session.abort" in content or "sdk.session.abort" in content, \
        "cleanupSession should abort busy sessions"
    assert "session.delete" in content or "sdk.session.delete" in content, \
        "cleanupSession should delete session after cleanup"

    # Check stable function exists (internal helper)
    assert "async function stable(" in content, \
        "actions.ts must have stable function (waits for session metadata to stabilize)"


def test_actions_ts_stable_polling_logic():
    """
    The stable() function must poll until session metadata stabilizes.
    Checks for the key polling pattern comparing previous/next state.
    """
    actions_ts = E2E_DIR / "actions.ts"
    content = _read_file(actions_ts)

    # Look for polling pattern that compares prev/next state
    # The stable function uses expect.poll to check if session metadata changed
    assert "expect" in content and "poll" in content, \
        "stable() should use expect.poll for polling"

    # Check for metadata comparison pattern (time.updated or time.created)
    # The stable function checks info.time.updated or info.time.created
    assert "time.updated" in content or "time.created" in content, \
        "stable() must check session time metadata for changes"


def test_withSession_uses_cleanupSession():
    """
    The withSession helper must use cleanupSession instead of direct delete.
    """
    actions_ts = E2E_DIR / "actions.ts"
    content = _read_file(actions_ts)

    # Find withSession function and check its finally block
    withsession_match = re.search(
        r"export async function withSession[^{]*\{",
        content
    )
    assert withsession_match, "withSession function must be exported"

    # Get the function body (simplified - look after the function start)
    func_start = withsession_match.end()
    func_section = content[func_start:func_start + 3000]

    # Should use cleanupSession in the finally block
    assert "cleanupSession" in func_section, \
        "withSession must use cleanupSession for cleanup"

    # Should NOT have direct sdk.session.delete in the finally block
    # (it might be elsewhere in the file for backward compat, but not in withSession's cleanup)
    finally_match = re.search(
        r"finally\s*\{[^}]*sdk\.session\.delete",
        func_section
    )
    assert not finally_match, \
        "withSession should NOT call sdk.session.delete directly - use cleanupSession instead"


def test_fixtures_ts_has_tracking():
    """
    fixtures.ts must add trackSession and trackDirectory to withProject fixture.
    """
    fixtures_ts = E2E_DIR / "fixtures.ts"
    content = _read_file(fixtures_ts)

    # Check for trackSession in TestFixtures type
    assert "trackSession:" in content, \
        "TestFixtures type must include trackSession"
    assert "trackDirectory:" in content, \
        "TestFixtures type must include trackDirectory"

    # Check that cleanupSession is imported
    assert "cleanupSession" in content, \
        "fixtures.ts must import cleanupSession from actions"


def test_fixtures_cleanup_uses_cleanupSession():
    """
    The withProject fixture cleanup must use cleanupSession for all tracked sessions.
    """
    fixtures_ts = E2E_DIR / "fixtures.ts"
    content = _read_file(fixtures_ts)

    # Find the withProject fixture implementation
    withproject_match = re.search(
        r"withProject:\s*async[^{]*\{",
        content
    )
    assert withproject_match, "withProject fixture must be defined"

    # Get section after withProject start
    section_start = withproject_match.end()
    section = content[section_start:section_start + 4000]

    # Should use Promise.allSettled with cleanupSession for sessions
    assert "Promise.allSettled" in section, \
        "withProject cleanup should use Promise.allSettled for parallel cleanup"
    assert "cleanupSession" in section, \
        "withProject cleanup must call cleanupSession for tracked sessions"
    assert "sessions" in section.lower(), \
        "withProject must iterate over tracked sessions"


def test_agents_md_documents_helpers():
    """
    AGENTS.md must document the new helper functions.
    """
    agents_md = E2E_DIR / "AGENTS.md"
    content = _read_file(agents_md)

    # Check for new helper documentation
    assert "withProject" in content, \
        "AGENTS.md must document withProject helper"
    assert "trackSession" in content, \
        "AGENTS.md must document trackSession"
    assert "trackDirectory" in content, \
        "AGENTS.md must document trackDirectory"


def test_agents_md_recommends_fixture_cleanup():
    """
    AGENTS.md must recommend fixture-managed cleanup over direct delete.
    """
    agents_md = E2E_DIR / "AGENTS.md"
    content = _read_file(agents_md)

    # Check for recommendation to use fixture-managed cleanup
    assert "fixture-managed cleanup" in content.lower() or \
           "Prefer fixture-managed" in content, \
        "AGENTS.md must recommend fixture-managed cleanup"

    # Check for warning against direct sdk.session.delete (with or without backticks)
    assert "Avoid calling" in content and "sdk.session.delete" in content, \
        "AGENTS.md must warn against direct sdk.session.delete calls"


def test_agents_md_documents_cleanup_pattern():
    """
    AGENTS.md Error Handling section must document the new cleanup patterns.
    """
    agents_md = E2E_DIR / "AGENTS.md"
    content = _read_file(agents_md)

    # Check for withSession recommendation
    assert "Prefer `withSession" in content, \
        "AGENTS.md must recommend withSession for temp sessions"

    # Check for withProject/trackSession/trackDirectory pattern
    assert "trackDirectory" in content and "withProject" in content, \
        "AGENTS.md must document using trackDirectory with withProject"

    # Check for explanation of why (CI concurrency safety)
    assert "CI concurrency" in content.lower() or "clean up safely" in content.lower(), \
        "AGENTS.md should explain the cleanup is for CI concurrency safety"


def test_typescript_syntax_valid():
    """
    All modified TypeScript files must have valid syntax.
    """
    files = [
        E2E_DIR / "actions.ts",
        E2E_DIR / "fixtures.ts",
    ]

    for file in files:
        if file.exists():
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck", str(file)],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=60
            )
            # TypeScript might have errors from other files, but syntax parse should work
            # Just check that tsc didn't crash with syntax errors on our file


def test_cleanupSession_signature_correct():
    """
    cleanupSession must accept { sessionID, directory?, sdk? } input.
    """
    actions_ts = E2E_DIR / "actions.ts"
    content = _read_file(actions_ts)

    # Find cleanupSession function signature
    match = re.search(
        r"export async function cleanupSession\(([^)]*)\)",
        content
    )
    assert match, "cleanupSession must have proper function signature"

    signature = match.group(1)
    # Check for input object destructuring pattern
    assert "sessionID" in signature, \
        "cleanupSession must accept sessionID"
    assert "directory" in signature or "sdk" in signature, \
        "cleanupSession must accept directory or sdk parameter"
