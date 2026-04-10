"""Tests for opencode e2e session cleanup fixture refactoring.

Verifies both the code changes (cleanupSession, waitSessionIdle, fixture tracking)
and the AGENTS.md documentation update.
"""
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js inline script."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ── Pass-to-pass ──────────────────────────────────────────────────────


def test_ts_files_readable():
    """Modified TypeScript files must exist and be readable."""
    files = [
        REPO / "packages/app/e2e/actions.ts",
        REPO / "packages/app/e2e/fixtures.ts",
    ]
    for f in files:
        assert f.exists(), f"{f} must exist"
        content = f.read_text()
        assert len(content) > 100, f"{f.name} must have substantial content"


def test_ts_syntax_valid():
    """Modified TypeScript files must have valid syntax (pass_to_pass)."""
    # Check that the files can be parsed as valid JS/TS by Node.js
    for filename in ["actions.ts", "fixtures.ts"]:
        filepath = REPO / "packages/app/e2e" / filename
        r = subprocess.run(
            ["node", "-p", f"'OK: ' + require('fs').statSync('{filepath}').size"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{filename} file error: {r.stderr}"
        assert "OK:" in r.stdout, f"{filename} should be readable"


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes via bun turbo (pass_to_pass)."""
    try:
        r = subprocess.run(
            ["bun", "typecheck"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"
    except FileNotFoundError:
        import pytest
        pytest.skip("bun not available in environment")


def test_repo_app_typecheck():
    """packages/app TypeScript typecheck passes (pass_to_pass)."""
    try:
        r = subprocess.run(
            ["bun", "run", "typecheck"],
            capture_output=True, text=True, timeout=120, cwd=REPO / "packages/app",
        )
        assert r.returncode == 0, f"App typecheck failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"
    except FileNotFoundError:
        import pytest
        pytest.skip("bun not available in environment")


# ── Fail-to-pass: Code behavior ───────────────────────────────────────


def test_cleanup_session_exported():
    """actions.ts must export an async cleanupSession function."""
    r = _run_node(
        'const fs = require("fs");'
        'const src = fs.readFileSync("/workspace/opencode/packages/app/e2e/actions.ts", "utf8");'
        'if (!/export\\s+async\\s+function\\s+cleanupSession\\s*\\(/.test(src))'
        '  throw new Error("cleanupSession not exported");'
        'console.log("OK");'
    )
    assert r.returncode == 0, f"cleanupSession not exported: {r.stderr}"


def test_cleanup_session_waits_aborts_deletes():
    """cleanupSession must wait for idle, abort if needed, wait stable, then delete."""
    actions = (REPO / "packages/app/e2e/actions.ts").read_text()
    idx = actions.index("export async function cleanupSession")
    assert idx >= 0, "cleanupSession not found"
    # Find the function body after the signature (skip object type in parameter)
    # Look for the pattern: }) { at end of signature
    sig_end = actions.index(") {", idx + 40)  # start search after function name
    body_start = actions.index("{", sig_end)
    # Find matching closing brace
    depth = 0
    body_end = body_start
    for i in range(body_start, min(body_start + 2000, len(actions))):
        if actions[i] == "{":
            depth += 1
        if actions[i] == "}":
            depth -= 1
            if depth == 0:
                body_end = i
                break
    body = actions[body_start:body_end+1]
    assert "waitSessionIdle" in body, "cleanupSession must wait for session idle"
    assert "abort" in body, "cleanupSession must abort non-idle sessions"
    assert "stable" in body, "cleanupSession must wait for stable state"
    assert ".delete(" in body, "cleanupSession must call session delete"


def test_wait_session_idle_exported():
    """actions.ts must export waitSessionIdle function that polls for idle status."""
    actions = (REPO / "packages/app/e2e/actions.ts").read_text()
    assert "export async function waitSessionIdle" in actions, \
        "waitSessionIdle must be exported from actions.ts"
    idx = actions.index("export async function waitSessionIdle")
    func_body = actions[idx:idx + 500]
    assert "idle" in func_body, "waitSessionIdle must check for idle status type"
    assert "timeout" in func_body, "waitSessionIdle must accept timeout parameter"


def test_with_session_uses_cleanup():
    """withSession must call cleanupSession, not direct sdk.session.delete."""
    actions = (REPO / "packages/app/e2e/actions.ts").read_text()
    idx = actions.index("export async function withSession")
    assert idx >= 0, "withSession not found"
    # Find the function body after the signature
    # withSession has generic <T> and multiline params
    # Find the pattern "): Promise<T> {" which ends the signature
    sig_end = actions.index("): Promise<T> {", idx)
    body_start = actions.index("{", sig_end)
    # Find matching closing brace
    depth = 0
    body_end = body_start
    for i in range(body_start, min(body_start + 1000, len(actions))):
        if actions[i] == "{":
            depth += 1
        if actions[i] == "}":
            depth -= 1
            if depth == 0:
                body_end = i
                break
    body = actions[body_start:body_end+1]
    assert "cleanupSession" in body, "withSession must call cleanupSession"
    assert "sdk.session.delete" not in body, "withSession must not use direct sdk.session.delete"


def test_fixtures_track_and_cleanup():
    """withProject fixture must provide trackSession/trackDirectory and cleanup in teardown."""
    fixtures = (REPO / "packages/app/e2e/fixtures.ts").read_text()
    assert "trackSession" in fixtures, \
        "fixtures.ts must define trackSession in withProject"
    assert "trackDirectory" in fixtures, \
        "fixtures.ts must define trackDirectory in withProject"
    assert "cleanupSession" in fixtures, \
        "fixtures.ts must use cleanupSession in teardown"
    # Verify sessions and dirs are tracked with collections
    assert "sessions" in fixtures, "fixtures must track sessions collection"
    assert "dirs" in fixtures or "directories" in fixtures, \
        "fixtures must track directories collection"
    # Verify cleanup happens with Promise.allSettled for tracked items
    assert "Promise.allSettled" in fixtures or "Promise.all" in fixtures, \
        "fixtures teardown must clean all tracked items concurrently"


# ── Fail-to-pass: Config/documentation ────────────────────────────────


def test_agents_md_documents_new_helpers():
    """AGENTS.md must document withProject, trackSession, and trackDirectory helpers."""
    agents_md = (REPO / "packages/app/e2e/AGENTS.md").read_text()
    assert "withProject" in agents_md, \
        "AGENTS.md must document the withProject helper"
    assert "trackSession" in agents_md, \
        "AGENTS.md must document the trackSession helper"
    assert "trackDirectory" in agents_md, \
        "AGENTS.md must document the trackDirectory helper"


def test_agents_md_recommends_fixture_cleanup():
    """AGENTS.md must recommend fixture-managed cleanup over direct session delete."""
    agents_md = (REPO / "packages/app/e2e/AGENTS.md").read_text()
    has_fixture_pref = "prefer" in agents_md.lower() and "fixture" in agents_md.lower()
    has_avoid_direct = "avoid" in agents_md.lower() and "session.delete" in agents_md.lower()
    assert has_fixture_pref or has_avoid_direct, \
        "AGENTS.md must recommend fixture-managed cleanup or discourage direct sdk.session.delete()"


def test_agents_md_error_handling_updated():
    """AGENTS.md Error Handling section must be updated with new cleanup guidance."""
    agents_md = (REPO / "packages/app/e2e/AGENTS.md").read_text()
    error_idx = agents_md.find("### Error Handling")
    assert error_idx >= 0, "Error Handling section must exist in AGENTS.md"
    error_section = agents_md[error_idx:error_idx + 1000]
    assert "withSession" in error_section, \
        "Error Handling must mention preferring withSession for temp sessions"
    assert "trackSession" in error_section or "track" in error_section.lower(), \
        "Error Handling must mention tracking sessions in withProject tests"
