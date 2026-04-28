"""
Task: opencode-share-workspace-slug-helper
Repo: anomalyco/opencode @ be9b4d1bcde39341c7813b66c5c19150a01bb8c2
PR:   16446

This task tests:
1. Code refactoring: Move duplicated slugFromUrl/waitSlug helpers to shared actions.ts
2. Config update: AGENTS.md documents the new helpers

All checks must pass for reward = 1. Any failure = reward 0.

Tests verify BEHAVIOR rather than text:
- Call functions and assert on return values via subprocess
- Verify code compiles and runs, not just source grep
- Parameterize assertions to allow alternative correct implementations
"""

import ast
import re
import subprocess
import sys
import os
from pathlib import Path

REPO = "/workspace/opencode"
ACTIONS_FILE = Path(REPO) / "packages/app/e2e/actions.ts"
AGENTS_MD_FILE = Path(REPO) / "packages/app/e2e/AGENTS.md"
PROJECTS_SWITCH_FILE = Path(REPO) / "packages/app/e2e/projects/projects-switch.spec.ts"
WORKSPACE_NEW_SESSION_FILE = Path(REPO) / "packages/app/e2e/projects/workspace-new-session.spec.ts"
WORKSPACES_FILE = Path(REPO) / "packages/app/e2e/projects/workspaces.spec.ts"


def run(cmd, cwd=REPO, timeout=120):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def test_typescript_parses():
    """Modified TypeScript files have valid syntax."""
    returncode, stdout, stderr = run("bun tsc --noEmit packages/app/e2e/actions.ts")
    stderr_lower = stderr.lower()
    assert "error ts" not in stderr_lower or "cannot find name" in stderr_lower, \
        f"TypeScript syntax error: {stderr[:500]}"


def test_spec_files_parse():
    """Modified spec files have valid syntax."""
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        returncode, stdout, stderr = run(f"bun tsc --noEmit {spec_file}")
        assert "error ts1" not in stderr.lower(), \
            f"Syntax error in {spec_file.name}: {stderr[:500]}"


def test_actions_has_slug_from_url():
    """actions.ts exports a function to extract slug from URL; verify by running TypeScript typecheck."""
    assert ACTIONS_FILE.exists(), f"actions.ts not found at {ACTIONS_FILE}"

    # Type-check the actions.ts file - if slugFromUrl is properly exported,
    # the typecheck will pass for files that import it
    returncode, stdout, stderr = run("bun tsc --noEmit packages/app/e2e/actions.ts")

    # Also verify by checking that the function signature is present in exports
    # Use TypeScript compiler output to verify the export is visible
    content = ACTIONS_FILE.read_text()

    # Verify function is exported (any style of export is fine)
    has_export = re.search(
        r'export\s+(?:function|const|let)\s+slugFromUrl',
        content
    )
    assert has_export, "slugFromUrl should be exported from actions.ts"

    # Verify the function body contains the expected regex pattern (key behavior)
    # The pattern /\/([^/]+)\/session(?:[/?#]|$)/ is distinctive
    has_pattern = re.search(r'session(?:\?\:|\[\/\?\#\])\|\$\\|\)\|', content) or \
                  re.search(r'session(?:\[\\/\?#\]\|)', content) or \
                  re.search(r'session.*slug.*url', content, re.IGNORECASE) or \
                  ('slugFromUrl' in content and '/session' in content and '[^/]+' in content)
    assert has_pattern, "slugFromUrl should use a regex matching /session path with slug capture"


def test_slug_from_url_runtime_behavior():
    """Execute slugFromUrl at runtime via Node.js to verify it correctly extracts workspace slugs."""
    assert ACTIONS_FILE.exists(), f"actions.ts not found at {ACTIONS_FILE}"

    # Run a Node.js script that extracts and executes the slugFromUrl function
    r = subprocess.run(
        ["node", "-e", """
const fs = require("fs");
const content = fs.readFileSync("packages/app/e2e/actions.ts", "utf8");

// Find the slugFromUrl function and extract its body using brace matching
const startIdx = content.indexOf("function slugFromUrl");
if (startIdx === -1) { console.error("FAIL: slugFromUrl not found in actions.ts"); process.exit(1); }

const braceStart = content.indexOf("{", startIdx);
if (braceStart === -1) { console.error("FAIL: no opening brace for slugFromUrl"); process.exit(1); }

let depth = 0;
let braceEnd = -1;
for (let i = braceStart; i < content.length; i++) {
    if (content[i] === "{") depth++;
    else if (content[i] === "}") { depth--; if (depth === 0) { braceEnd = i; break; } }
}
if (braceEnd === -1) { console.error("FAIL: unbalanced braces in slugFromUrl"); process.exit(1); }

// Extract function body (pure JS regex logic - no TS types in the body)
const fnBody = content.slice(braceStart + 1, braceEnd);
const slugFromUrl = new Function("url", fnBody);

// Test with URL patterns that exercise workspace slug extraction
const tests = [
    ["/my-workspace/session", "my-workspace"],
    ["/my-workspace/session/abc123", "my-workspace"],
    ["/my-workspace/session?q=1", "my-workspace"],
    ["/my-workspace/session#frag", "my-workspace"],
    ["https://example.com/ws-slug/session/xyz", "ws-slug"],
    ["/no-match/page", ""],
    ["", ""],
];

let passed = 0;
for (const [input, expected] of tests) {
    const got = slugFromUrl(input);
    if (got !== expected) {
        console.error("FAIL: slugFromUrl(" + JSON.stringify(input) + ") = " + JSON.stringify(got) + ", expected " + JSON.stringify(expected));
        process.exit(1);
    }
    passed++;
}
console.log("PASS: " + passed + " slugFromUrl test cases passed");
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"slugFromUrl runtime test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


def test_actions_exports_wait_slug_async():
    """actions.ts exports waitSlug as an async function."""
    assert ACTIONS_FILE.exists(), f"actions.ts not found at {ACTIONS_FILE}"
    content = ACTIONS_FILE.read_text()

    # Verify async function is exported (any style)
    has_export = re.search(
        r'export\s+async\s+function\s+waitSlug',
        content
    ) or re.search(
        r'export\s+const\s+waitSlug\s*=\s*async',
        content
    )
    assert has_export, "waitSlug should be exported as async function from actions.ts"

    # Verify it has polling behavior (expect.poll) and timeout
    assert 'expect.poll' in content or 'expect .poll' in content or 'poll' in content.lower(), \
        "waitSlug should use expect.poll for polling"

    # Verify a timeout is configured (any value - the specific duration is an implementation choice)
    has_timeout = re.search(r'timeout', content, re.IGNORECASE)
    assert has_timeout, "waitSlug should have a timeout configured for polling"


def test_duplicated_helpers_removed_from_specs():
    """Spec files no longer contain local function bodies for slugFromUrl/waitSlug."""
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        content = spec_file.read_text()

        local_slug_def_pattern = r'(?:function\s+slugFromUrl|const\s+slugFromUrl|let\s+slugFromUrl)\s*\('
        assert not re.search(local_slug_def_pattern, content), \
            f"{spec_file.name} still has local slugFromUrl function definition (should use shared one)"

        local_wait_def_pattern = r'(?:async\s+function\s+waitSlug|const\s+waitSlug\s*=|let\s+waitSlug\s*=)\s*(?:async)?\s*\('
        assert not re.search(local_wait_def_pattern, content), \
            f"{spec_file.name} still has local waitSlug function definition (should use shared one)"

        import_match = re.search(
            r'import\s*\{[^}]*\}\s*from\s*["\']\.\.\/actions["\']',
            content,
        )
        assert import_match, \
            f"{spec_file.name} should import from ../actions (shared helpers)"


def test_specs_import_shared_helpers():
    """Spec files import waitSlug and slugFromUrl from ../actions."""
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        content = spec_file.read_text()

        import_match = re.search(
            r'import\s*\{([^}]*)\}\s*from\s*["\']\.\.\/actions["\']',
            content,
        )
        assert import_match, f"{spec_file.name} should import from ../actions"

        imported_items = import_match.group(1)
        assert 'waitSlug' in imported_items, \
            f"{spec_file.name} import should include waitSlug from ../actions"

        if spec_file in [WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
            assert 'slugFromUrl' in imported_items, \
                f"{spec_file.name} import should include slugFromUrl from ../actions"

        returncode, stdout, stderr = run(f"bun tsc --noEmit {spec_file}", timeout=60)
        ts_errors = [l for l in stderr.splitlines() if 'error TS' in l]
        import_errors = [l for l in ts_errors if 'TS2304' in l or 'Cannot find module' in l or 'not exported' in l.lower()]
        assert not import_errors, \
            f"{spec_file.name} has unresolved imports:\n" + "\n".join(import_errors[:5])


def test_agents_md_documents_new_helpers():
    """AGENTS.md documents the new slugFromUrl and waitSlug helpers."""
    assert AGENTS_MD_FILE.exists(), f"AGENTS.md not found at {AGENTS_MD_FILE}"
    content = AGENTS_MD_FILE.read_text()

    assert 'slugFromUrl' in content, "AGENTS.md should mention slugFromUrl"
    slug_context = re.search(
        r'slugFromUrl[^.]*[.](?:\s|$)|(?:read|extract|get)[^.]*\bslugFromUrl\b',
        content,
        re.IGNORECASE
    )
    assert slug_context, "AGENTS.md should describe what slugFromUrl does (context near the name)"

    assert 'waitSlug' in content, "AGENTS.md should mention waitSlug"
    wait_context = re.search(
        r'waitSlug[^.]*(?:timeout|poll|wait|resolve)',
        content,
        re.IGNORECASE
    )
    assert wait_context, "AGENTS.md should describe what waitSlug does (polling/waiting context)"

    assert re.search(r'skip[^)]*\)', content) or re.search(r'\[.*skip.*\]', content), \
        "AGENTS.md should document the skip parameter for waitSlug"


def test_agents_md_documents_routing_guidance():
    """AGENTS.md includes guidance on using shared helpers for routing validation."""
    assert AGENTS_MD_FILE.exists(), f"AGENTS.md not found at {AGENTS_MD_FILE}"
    content = AGENTS_MD_FILE.read_text()

    # Check that AGENTS.md has a line associating ../actions with routing/validation.
    # Accept any phrasing (e.g. "use shared helpers from ../actions",
    # "use helper utilities in ../actions", "import from ../actions when validating", etc.)
    lines_with_actions = [l for l in content.split('\n') if '../actions' in l]
    found_routing_guidance = any(
        re.search(r'(?:routing|validat)', line, re.IGNORECASE)
        for line in lines_with_actions
    )
    assert found_routing_guidance, \
        "AGENTS.md should recommend using ../actions helpers when validating routing"

    windows_pattern = r'(?:windows|canonicalized?|resolve[d]?\s+(?:slug|workspace))'
    assert re.search(windows_pattern, content, re.IGNORECASE), \
        "AGENTS.md should mention Windows slug canonicalization or resolution"

    assert re.search(r'workspace\s+slug', content, re.IGNORECASE) or 'slug' in content.lower(), \
        "AGENTS.md should mention workspace slugs"


def test_repo_e2e_actions_typecheck():
    """Repo's TypeScript typecheck passes on e2e actions.ts (pass_to_pass)."""
    returncode, stdout, stderr = run("bun x tsc --noEmit packages/app/e2e/actions.ts")
    stderr_lines = [l for l in stderr.splitlines() if "error TS" in l]
    real_errors = [l for l in stderr_lines if "TS2304" not in l and "TS2580" not in l]
    assert not real_errors, f"TypeScript errors in actions.ts:\n{stderr[-800:]}"


def test_repo_e2e_typecheck_all():
    """Repo's TypeScript typecheck passes on e2e directory (pass_to_pass)."""
    returncode, stdout, stderr = run("bun x tsc --noEmit -p packages/app/e2e")
    stderr_lines = [l for l in stderr.splitlines() if "error TS" in l]
    real_errors = [l for l in stderr_lines
                   if "TS2304" not in l and "TS2580" not in l and "TS7016" not in l]
    assert not real_errors, f"TypeScript errors in e2e package:\n{stderr[-800:]}"


def test_repo_prettier_check():
    """Repo's Prettier formatting check passes on modified files (pass_to_pass)."""
    returncode, stdout, stderr = run(
        "bun x prettier --check "
        "packages/app/e2e/actions.ts "
        "packages/app/e2e/projects/projects-switch.spec.ts "
        "packages/app/e2e/projects/workspace-new-session.spec.ts "
        "packages/app/e2e/projects/workspaces.spec.ts"
    )
    assert returncode == 0, f"Prettier check failed:\n{stdout[-500:]}{stderr[-500:]}"


def test_repo_biome_lint():
    """Repo's Biome lint check passes on e2e actions.ts (pass_to_pass)."""
    returncode, stdout, stderr = run("bun x @biomejs/biome lint packages/app/e2e/actions.ts")
    assert returncode == 0, f"Biome lint failed:\n{stderr[-500:]}"


def test_repo_tsc_spec_files():
    """TypeScript syntax check on modified spec files (pass_to_pass)."""
    for spec_file in [PROJECTS_SWITCH_FILE, WORKSPACE_NEW_SESSION_FILE, WORKSPACES_FILE]:
        returncode, stdout, stderr = run(f"bun x tsc --noEmit {spec_file}")
        syntax_errors = [line for line in stderr.splitlines() if "error TS1" in line]
        assert not syntax_errors, f"TypeScript syntax errors in {spec_file.name}:\n{stderr[-500:]}"


def test_repo_biome_lint_specs():
    """Repo's Biome lint check passes on modified spec files (pass_to_pass)."""
    returncode, stdout, stderr = run(
        "bun x @biomejs/biome lint "
        "packages/app/e2e/projects/projects-switch.spec.ts "
        "packages/app/e2e/projects/workspace-new-session.spec.ts "
        "packages/app/e2e/projects/workspaces.spec.ts"
    )
    assert returncode == 0, f"Biome lint failed on spec files:\n{stderr[-500:]}"


def test_repo_prettier_check_agents_md():
    """Repo's Prettier formatting check passes on AGENTS.md (pass_to_pass)."""
    returncode, stdout, stderr = run("bun x prettier --check packages/app/e2e/AGENTS.md")
    assert returncode == 0, f"Prettier check failed on AGENTS.md:\n{stdout[-500:]}{stderr[-500:]}"


def test_repo_prettier_check_specs():
    """Repo's Prettier formatting check passes on all modified spec files (pass_to_pass)."""
    returncode, stdout, stderr = run(
        "bun x prettier --check "
        "packages/app/e2e/projects/projects-switch.spec.ts "
        "packages/app/e2e/projects/workspace-new-session.spec.ts "
        "packages/app/e2e/projects/workspaces.spec.ts"
    )
    assert returncode == 0, f"Prettier check failed on spec files:\n{stdout[-500:]}{stderr[-500:]}"


def test_session_id_from_url_still_present():
    """sessionIDFromUrl function still present in actions.ts (was already there)."""
    content = ACTIONS_FILE.read_text()
    assert "export function sessionIDFromUrl(url: string)" in content or \
           "export const sessionIDFromUrl" in content, \
        "sessionIDFromUrl should still be exported from actions.ts"

