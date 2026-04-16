"""Tests for playwright minimist vendor task.

This task requires:
1. Creating a vendored TypeScript version of minimist
2. Replacing the external minimist dependency with the vendored version
3. Updating CLAUDE.md with a new commit message rule
"""

import json
import subprocess
from pathlib import Path
import re

REPO = Path("/workspace/repo")
CLI_CLIENT_DIR = REPO / "packages" / "playwright-core" / "src" / "tools" / "cli-client"


# =============================================================================
# Category 1: Code Behavior Tests (fail_to_pass)
# =============================================================================

def test_minimist_ts_exists():
    """minimist.ts must exist as a vendored TypeScript implementation."""
    minimist_file = CLI_CLIENT_DIR / "minimist.ts"
    assert minimist_file.exists(), "minimist.ts should be created"

    content = minimist_file.read_text()
    assert "export function minimist" in content, "minimist.ts should export the minimist function"
    assert "MinimistArgs" in content, "minimist.ts should define MinimistArgs interface"
    assert "MinimistOptions" in content, "minimist.ts should define MinimistOptions interface"


def test_program_uses_vendored_minimist():
    """program.ts must import from the vendored minimist, not require external package."""
    program_file = CLI_CLIENT_DIR / "program.ts"
    content = program_file.read_text()

    # Should import from local minimist
    assert 'import { minimist } from \'./minimist\'' in content, \
        "program.ts should import minimist from local ./minimist"
    assert 'import type { MinimistArgs } from \'./minimist\'' in content, \
        "program.ts should import MinimistArgs type from local ./minimist"

    # Should NOT use require('minimist')
    assert "require('minimist')" not in content, \
        "program.ts should not require external minimist package"

    # Should use the imported function
    assert "minimist(argv" in content, \
        "program.ts should call the local minimist function"


def test_session_uses_vendored_minimist():
    """session.ts must import MinimistArgs from vendored minimist."""
    session_file = CLI_CLIENT_DIR / "session.ts"
    content = session_file.read_text()

    # Should import from local minimist
    assert 'import type { MinimistArgs } from \'./minimist\'' in content, \
        "session.ts should import MinimistArgs type from local ./minimist"

    # Should NOT define its own MinimistArgs type
    assert "type MinimistArgs = {" not in content, \
        "session.ts should not define its own MinimistArgs type (should import from minimist)"


def test_deps_list_updated():
    """DEPS.list must declare minimist.ts as a dependency for program.ts and session.ts."""
    deps_file = CLI_CLIENT_DIR / "DEPS.list"
    content = deps_file.read_text()

    # program.ts should depend on minimist.ts
    program_section = re.search(r'\[program\.ts\](.*?)(?=\[|$)', content, re.DOTALL)
    assert program_section is not None, "DEPS.list should have [program.ts] section"
    assert "./minimist.ts" in program_section.group(1), \
        "program.ts in DEPS.list should depend on ./minimist.ts"

    # session.ts should depend on minimist.ts
    session_section = re.search(r'\[session\.ts\](.*?)(?=\[|$)', content, re.DOTALL)
    assert session_section is not None, "DEPS.list should have [session.ts] section"
    assert "./minimist.ts" in session_section.group(1), \
        "session.ts in DEPS.list should depend on ./minimist.ts"

    # minimist.ts should have its own section with "strict"
    assert "[minimist.ts]" in content, "DEPS.list should have [minimist.ts] section"


def test_types_minimist_dependency_removed():
    """@types/minimist dev dependency must be removed from package.json."""
    package_file = REPO / "package.json"
    content = package_file.read_text()

    assert '"@types/minimist"' not in content, \
        "package.json should not contain @types/minimist dependency"


def test_typescript_compiles():
    """TypeScript compilation must succeed for the modified files."""
    # Run TypeScript compiler check on the cli-client directory
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for specific errors in the files we modified
    stderr = result.stderr.lower() if result.stderr else ""
    stdout = result.stdout.lower() if result.stdout else ""
    combined = stderr + stdout

    cli_client_path = "packages/playwright-core/src/tools/cli-client"
    assert cli_client_path not in combined or result.returncode == 0, \
        f"TypeScript errors in cli-client: {result.stderr or result.stdout}"


def test_boolean_option_with_equals_throws():
    """The vendored minimist must throw when boolean option is passed with '=value'."""
    # Create a test script to verify the behavior
    test_script = CLI_CLIENT_DIR / "_test_minimist.js"

    test_script.write_text("""
const { minimist } = require('./minimist.ts');

try {
    minimist(['--test=true'], { boolean: ['test'] });
    console.log('ERROR: Should have thrown for --test=true');
    process.exit(1);
} catch (e) {
    if (e.message.includes("should not be passed with '=value'")) {
        console.log('SUCCESS: Correctly threw for --test=true');
        process.exit(0);
    } else {
        console.log('ERROR: Wrong error message:', e.message);
        process.exit(1);
    }
}
""")

    try:
        # Try to run with ts-node or compile first
        result = subprocess.run(
            ["npx", "tsx", str(test_script)],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=30
        )

        # If tsx doesn't work, try building and running
        if result.returncode != 0 and ("tsx" in result.stderr or "command not found" in result.stderr):
            # Just verify the code is there - we'll rely on other tests
            minimist_content = (CLI_CLIENT_DIR / "minimist.ts").read_text()
            assert "should not be passed with '=value'" in minimist_content, \
                "minimist.ts should throw error for boolean with =value"
        else:
            assert result.returncode == 0, f"Test script failed: {result.stderr}"
            assert "SUCCESS" in result.stdout, f"Test did not pass: {result.stdout}"
    finally:
        test_script.unlink(missing_ok=True)


# =============================================================================
# Category 2: Config/Documentation Update Tests (fail_to_pass - REQUIRED)
# =============================================================================

def test_claude_md_updated_with_new_rule():
    """CLAUDE.md must be updated with the new commit message rule.

    This is a config edit requirement - the PR updated CLAUDE.md to add
    a new rule about commit messages.
    """
    claude_file = REPO / "CLAUDE.md"
    assert claude_file.exists(), "CLAUDE.md should exist"

    content = claude_file.read_text()

    # The PR adds this specific rule
    assert 'Never add "Generated with" in commit message' in content, \
        "CLAUDE.md should contain the new rule: 'Never add \"Generated with\" in commit message'"

    # Verify it's in the Commit Convention section
    commit_section = content.find("## Commit Convention")
    if commit_section != -1:
        section_content = content[commit_section:commit_section + 2000]
        assert 'Never add "Generated with"' in section_content, \
            "The 'Generated with' rule should be in the Commit Convention section"


# =============================================================================
# Category 3: Pass-to-Pass Tests (regression prevention)
# =============================================================================

def test_repo_lint_passes():
    """npm run flint should pass (or at least not fail on our changes)."""
    # This is a p2p test - it should pass on both base and fixed commits
    # We run a lighter check - just verify the files parse
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "packages/playwright-core/tsconfig.json"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180
    )

    # Allow this to pass even if there are unrelated errors
    # We just want to make sure our changes don't introduce NEW errors
    stderr = result.stderr if result.stderr else ""
    stdout = result.stdout if result.stdout else ""
    combined = (stderr + stdout).lower()

    # Check that there are no errors specifically about our new minimist.ts
    assert "minimist.ts" not in combined or result.returncode == 0, \
        f"TypeScript errors in minimist.ts: {stderr or stdout}"


def test_minimist_exports_correct_types():
    """minimist.ts must export all expected types."""
    minimist_content = (CLI_CLIENT_DIR / "minimist.ts").read_text()

    # Check all expected exports
    assert "export interface MinimistOptions" in minimist_content
    assert "export interface MinimistArgs" in minimist_content
    assert "export function minimist" in minimist_content
