#!/usr/bin/env python3
"""
Tests for playwright-cli-vendor-minimist task.

This task tests:
1. Code behavior: Vendored minimist module works correctly (parsing CLI args)
2. Config update: CLAUDE.md updated with new commit convention
3. TypeScript: Modified files compile without errors
"""

import subprocess
import json
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
CLI_CLIENT_DIR = REPO / "packages" / "playwright-core" / "src" / "tools" / "cli-client"

def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript script using Node.js with experimental strip types."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


def test_typescript_compiles():
    """TypeScript files should compile without errors."""
    # Check that the minimist.ts file exists and TypeScript can parse it
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "packages/playwright-core/src/tools/cli-client/minimist.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=60
    )
    # Note: tsc might fail on other files, we just care about our minimist.ts
    # The important thing is that the new file doesn't have syntax errors
    if r.returncode != 0 and "minimist.ts" in r.stderr:
        raise AssertionError(f"TypeScript error in minimist.ts: {r.stderr}")


def test_minimist_file_exists():
    """FAIL-TO-PASS: minimist.ts file should exist after the fix."""
    minimist_file = CLI_CLIENT_DIR / "minimist.ts"
    if not minimist_file.exists():
        raise AssertionError("minimist.ts file does not exist - vendoring not complete")


def test_minimist_parses_boolean_args():
    """FAIL-TO-PASS: minimist should parse boolean arguments correctly."""
    result = _run_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'

// Test boolean parsing
const args = minimist(['--verbose', '--no-debug'], { boolean: ['verbose', 'debug'] })
const result = {
    verbose: args.verbose,
    debug: args.debug,
    _: args._
}
console.log(JSON.stringify(result))
""")
    if result.returncode != 0:
        raise AssertionError(f"Script failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    assert data["verbose"] == True, f"Expected verbose=true, got {data['verbose']}"
    assert data["debug"] == False, f"Expected debug=false, got {data['debug']}"


def test_minimist_parses_string_args():
    """FAIL-TO-PASS: minimist should parse string arguments correctly."""
    result = _run_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'

// Test string parsing
const args = minimist(['--name', 'test', '--port', '8080'], { string: ['name', 'port'] })
const result = {
    name: args.name,
    port: args.port,
    _: args._
}
console.log(JSON.stringify(result))
""")
    if result.returncode != 0:
        raise AssertionError(f"Script failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    assert data["name"] == "test", f"Expected name='test', got {data['name']}"
    assert data["port"] == "8080", f"Expected port='8080', got {data['port']}"


def test_minimist_throws_on_boolean_with_value():
    """FAIL-TO-PASS: minimist should throw error when boolean is passed with =value."""
    result = _run_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'

try {
    minimist(['--verbose=true'], { boolean: ['verbose'] })
    console.log('ERROR: Should have thrown')
} catch (e: any) {
    console.log(JSON.stringify({ error: e.message }))
}
""")
    if result.returncode != 0:
        raise AssertionError(f"Script failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    assert "error" in data, "Expected error to be thrown for boolean with =value"
    assert "should not be passed with" in data["error"], f"Expected specific error message, got: {data['error']}"


def test_minimist_handles_positional_args():
    """FAIL-TO-PASS: minimist should handle positional arguments."""
    result = _run_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'

const args = minimist(['list', '--verbose', 'myarg1', 'myarg2'], { boolean: ['verbose'] })
const result = {
    verbose: args.verbose,
    positional: args._
}
console.log(JSON.stringify(result))
""")
    if result.returncode != 0:
        raise AssertionError(f"Script failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    assert data["verbose"] == True, f"Expected verbose=true, got {data['verbose']}"
    assert "list" in data["positional"], f"Expected 'list' in positional args, got {data['positional']}"


def test_minimist_handles_double_dash():
    """FAIL-TO-PASS: minimist should handle -- separator for non-option args."""
    result = _run_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'

const args = minimist(['--verbose', '--', '--not-an-option', 'another'], { boolean: ['verbose'] })
const result = {
    verbose: args.verbose,
    positional: args._
}
console.log(JSON.stringify(result))
""")
    if result.returncode != 0:
        raise AssertionError(f"Script failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    assert data["verbose"] == True, f"Expected verbose=true, got {data['verbose']}"
    assert "--not-an-option" in data["positional"], f"Expected '--not-an-option' in positional args, got {data['positional']}"


def test_minimist_handles_short_flags():
    """FAIL-TO-PASS: minimist should handle short flag arguments."""
    result = _run_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'

const args = minimist(['-v', '-p', '8080'], { boolean: ['verbose'], string: ['port'] })
const result = {
    v: args.v,
    p: args.p,
    _: args._
}
console.log(JSON.stringify(result))
""")
    if result.returncode != 0:
        raise AssertionError(f"Script failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    # Short flags that aren't explicitly declared become their short form
    assert data["v"] == True, f"Expected v=true, got {data['v']}"


def test_program_ts_imports_minimist():
    """FAIL-TO-PASS: program.ts should import from local minimist module."""
    program_file = CLI_CLIENT_DIR / "program.ts"
    content = program_file.read_text()

    # Should import from local minimist, not external package
    assert "from './minimist'" in content, "program.ts should import minimist from local path"
    assert "require('minimist')" not in content, "program.ts should not require external minimist package"


def test_session_ts_imports_minimist():
    """FAIL-TO-PASS: session.ts should import MinimistArgs type from local minimist."""
    session_file = CLI_CLIENT_DIR / "session.ts"
    content = session_file.read_text()

    assert "from './minimist'" in content, "session.ts should import from local minimist path"


def test_deps_list_includes_minimist():
    """FAIL-TO-PASS: DEPS.list should include minimist.ts dependencies."""
    deps_file = CLI_CLIENT_DIR / "DEPS.list"
    content = deps_file.read_text()

    assert "[minimist.ts]" in content, "DEPS.list should have section for minimist.ts"
    assert './minimist.ts' in content, "DEPS.list should reference minimist.ts in program.ts and session.ts sections"


def test_claude_md_has_commit_convention():
    """FAIL-TO-PASS: CLAUDE.md should include new commit convention about 'Generated with'."""
    claude_file = REPO / "CLAUDE.md"
    content = claude_file.read_text()

    # The PR adds this line to the commit conventions section
    assert 'Never add "Generated with" in commit message' in content, \
        "CLAUDE.md should include 'Never add \"Generated with\" in commit message' convention"


def test_claude_md_has_co_authored_by_rule():
    """PASS-TO-PASS: CLAUDE.md should still have the existing Co-Authored-By rule."""
    claude_file = REPO / "CLAUDE.md"
    content = claude_file.read_text()

    assert "Never add Co-Authored-By agents in commit message" in content, \
        "CLAUDE.md should include existing Co-Authored-By rule"


def test_minimist_has_proper_types():
    """PASS-TO-PASS: minimist.ts should export proper TypeScript interfaces."""
    minimist_file = CLI_CLIENT_DIR / "minimist.ts"
    content = minimist_file.read_text()

    assert "export interface MinimistOptions" in content, "Should export MinimistOptions interface"
    assert "export interface MinimistArgs" in content, "Should export MinimistArgs interface"
    assert "export function minimist" in content, "Should export minimist function"


def test_minimist_has_license_header():
    """PASS-TO-PASS: minimist.ts should have proper MIT license header."""
    minimist_file = CLI_CLIENT_DIR / "minimist.ts"
    content = minimist_file.read_text()

    assert "MIT License" in content, "minimist.ts should include MIT license header"
    assert "James Halliday and contributors" in content, "Should attribute original author"
    assert "Modifications copyright (c) Microsoft Corporation" in content, "Should note Microsoft modifications"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
