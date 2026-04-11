"""
Task: opencode-share-workspace-slug-helper
Repo: anomalyco/opencode @ be9b4d1bcde39341c7813b66c5c19150a01bb8c2
PR:   16446

This task tests:
1. Code refactoring: Move duplicated slugFromUrl/waitSlug helpers to shared actions.ts
2. Config update: AGENTS.md documents the new helpers

All checks must pass for reward = 1. Any failure = reward 0.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
ACTIONS_FILE = Path(REPO) / "packages/app/e2e/actions.ts"
AGENTS_MD_FILE = Path(REPO) / "packages/app/e2e/AGENTS.md"
PROJECTS_SWITCH_FILE = Path(REPO) / "packages/app/e2e/projects/projects-switch.spec.ts"
WORKSPACE_NEW_SESSION_FILE = Path(REPO) / "packages/app/e2e/projects/workspace-new-session.spec.ts"
WORKSPACES_FILE = Path(REPO) / "packages/app/e2e/projects/workspaces.spec.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_parses():
    """Modified TypeScript files have valid syntax."""
    # Use bun's typecheck to verify syntax
    result = subprocess.run(
        ["bun", "tsc", "--noEmit", "packages/app/e2e/actions.ts"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    # Allow non-zero exit if it's just type errors, but syntax should parse
    # A syntax error would cause a different exit code/message
    assert "error TS" not in result.stderr.decode() or "Cannot find name" in result.stderr.decode(), \
        f"TypeScript syntax error: {result.stderr.decode()}"


def test_spec_files_parse():
    """Modified spec files have valid syntax."""
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        result = subprocess.run(
            ["bun", "tsc", "--noEmit", str(spec_file)],
            cwd=REPO,
            capture_output=True,
            timeout=60,
        )
        assert "error TS1" not in result.stderr.decode(), \
            f"Syntax error in {spec_file.name}: {result.stderr.decode()[:500]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral/code tests
# ---------------------------------------------------------------------------

def test_actions_has_slug_from_url():
    """actions.ts exports slugFromUrl function."""
    assert ACTIONS_FILE.exists(), f"actions.ts not found at {ACTIONS_FILE}"
    content = ACTIONS_FILE.read_text()

    # Check for export function declaration
    assert "export function slugFromUrl(url: string)" in content, \
        "slugFromUrl function not exported from actions.ts"

    # Check for the regex pattern
    assert r"/\\/([^/]+)\\/session(?:[/?#]|$)/" in content, \
        "slugFromUrl regex pattern not found"


def test_actions_has_wait_slug():
    """actions.ts exports waitSlug async function."""
    assert ACTIONS_FILE.exists(), f"actions.ts not found at {ACTIONS_FILE}"
    content = ACTIONS_FILE.read_text()

    # Check for export async function declaration
    assert "export async function waitSlug(page: Page, skip: string[] = [])" in content, \
        "waitSlug function not exported from actions.ts with correct signature"

    # Check for polling logic
    assert "expect.poll" in content, "waitSlug should use expect.poll for polling"
    assert "45_000" in content or "45000" in content, \
        "waitSlug should have 45 second timeout"


def test_duplicated_helpers_removed_from_specs():
    """Duplicated slugFromUrl/waitSlug functions removed from spec files."""
    # These functions should NOT exist in spec files anymore (they're in actions.ts now)
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        content = spec_file.read_text()

        # Should not have local function definition anymore
        local_slug_def = "function slugFromUrl(url: string)" in content
        assert not local_slug_def, \
            f"{spec_file.name} still has local slugFromUrl function (should use shared one)"

        local_wait_def = "async function waitSlug(page: Page" in content or \
                        "async function waitSlug(page:" in content
        assert not local_wait_def, \
            f"{spec_file.name} still has local waitSlug function (should use shared one)"


def test_specs_import_shared_helpers():
    """Spec files import slugFromUrl and waitSlug from ../actions."""
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        content = spec_file.read_text()

        # Check the import statement includes these functions
        import_match = re.search(r'from "\.\./actions"', content)
        if not import_match:
            import_match = re.search(r"from '\.\./actions'", content)

        assert import_match, f"{spec_file.name} should import from ../actions"

        # Check that the import includes the helpers
        # Look for the import line and check it includes slugFromUrl and waitSlug
        lines = content.split('\n')
        for line in lines:
            if '../actions' in line and 'from' in line:
                assert 'slugFromUrl' in line, \
                    f"{spec_file.name} import should include slugFromUrl from ../actions"
                assert 'waitSlug' in line, \
                    f"{spec_file.name} import should include waitSlug from ../actions"
                break


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config file update tests (REQUIRED for agentmd-edit)
# ---------------------------------------------------------------------------

def test_agents_md_documents_new_helpers():
    """AGENTS.md documents the new slugFromUrl and waitSlug helpers."""
    assert AGENTS_MD_FILE.exists(), f"AGENTS.md not found at {AGENTS_MD_FILE}"
    content = AGENTS_MD_FILE.read_text()

    # Check for helper function documentation
    assert "`slugFromUrl(url)`" in content or "slugFromUrl(url)" in content, \
        "AGENTS.md should document slugFromUrl helper"

    assert "`waitSlug(page, skip?)`" in content or "waitSlug(page, skip?)" in content or \
           "`waitSlug(page,`" in content, \
        "AGENTS.md should document waitSlug helper with skip parameter"

    # Check it describes what they do
    assert "Read workspace slug from URL" in content or "workspace slug" in content.lower(), \
        "AGENTS.md should explain what slugFromUrl does (read workspace slug from URL)"

    assert "Wait for resolved workspace slug" in content or "resolved workspace slug" in content.lower(), \
        "AGENTS.md should explain what waitSlug does"


def test_agents_md_documents_routing_guidance():
    """AGENTS.md includes guidance on using shared helpers for routing validation."""
    assert AGENTS_MD_FILE.exists(), f"AGENTS.md not found at {AGENTS_MD_FILE}"
    content = AGENTS_MD_FILE.read_text()

    # Check for the Windows/canonicalization guidance
    assert "canonicalized on Windows" in content or "canonicalized" in content.lower(), \
        "AGENTS.md should mention Windows slug canonicalization"

    assert "shared helpers from `../actions`" in content or "shared helpers" in content.lower(), \
        "AGENTS.md should recommend using shared helpers from ../actions"

    assert "resolved workspace slugs" in content.lower() or "workspace slug" in content.lower(), \
        "AGENTS.md should mention resolved workspace slugs"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — additional verification
# ---------------------------------------------------------------------------

def test_session_id_from_url_still_present():
    """sessionIDFromUrl function still present in actions.ts (was already there)."""
    content = ACTIONS_FILE.read_text()
    assert "export function sessionIDFromUrl(url: string)" in content, \
        "sessionIDFromUrl should still be exported from actions.ts"
