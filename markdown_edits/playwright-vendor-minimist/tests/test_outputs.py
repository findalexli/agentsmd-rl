"""
Test suite for playwright-vendor-minimist task.

Tests cover:
1. minimist.ts functionality (vendored module works correctly)
2. CLAUDE.md config update (new commit message rule added)
3. DEPS.list update (minimist.ts listed as dependency)
4. package.json update (@types/minimist removed)
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
CLI_CLIENT = REPO / "packages/playwright-core/src/tools/cli-client"


def _run_node_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run TypeScript code with Node.js."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO)
        )
    finally:
        script_path.unlink(missing_ok=True)


def test_minimist_file_exists():
    """minimist.ts must exist at the expected path."""
    minimist_path = CLI_CLIENT / "minimist.ts"
    assert minimist_path.exists(), f"minimist.ts not found at {minimist_path}"


def test_minimist_parses_boolean_flags():
    """minimist must correctly parse boolean flags."""
    result = _run_node_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'
const args = minimist(['--help', '--version'], { boolean: ['help', 'version'] })
console.log(JSON.stringify({
    help: args.help,
    version: args.version,
    _: args._
}))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["help"] is True, f"help should be true, got: {data['help']}"
    assert data["version"] is True, f"version should be true, got: {data['version']}"
    assert data["_"] == [], f"positional args should be empty, got: {data['_']}"


def test_minimist_parses_string_values():
    """minimist must correctly parse string arguments."""
    result = _run_node_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'
const args = minimist(['--name', 'test', '--config', 'file.json'], { string: ['name', 'config'] })
console.log(JSON.stringify({
    name: args.name,
    config: args.config,
    _: args._
}))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["name"] == "test", f"name should be 'test', got: {data['name']}"
    assert data["config"] == "file.json", f"config should be 'file.json', got: {data['config']}"


def test_minimist_throws_on_boolean_equals():
    """minimist must throw error when boolean flag is passed with =value."""
    result = _run_node_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'
try {
    minimist(['--bool=true'], { boolean: ['bool'] })
    console.log('ERROR: should have thrown')
} catch (e) {
    console.log('OK: threw expected error')
}
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert "OK: threw expected error" in result.stdout, f"minimist should throw on boolean=val, got: {result.stdout}"


def test_minimist_parses_positional_args():
    """minimist must correctly parse positional arguments."""
    result = _run_node_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'
const args = minimist(['open', 'file.txt', '--browser', 'chromium'], { string: ['browser'] })
console.log(JSON.stringify({
    browser: args.browser,
    _: args._
}))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["_"][0] == "open", f"first positional should be 'open', got: {data['_'][0]}"
    assert data["_"][1] == "file.txt", f"second positional should be 'file.txt', got: {data['_'][1]}"
    assert data["browser"] == "chromium", f"browser should be 'chromium', got: {data['browser']}"


def test_minimist_parses_negated_flags():
    """minimist must correctly parse --no-* boolean flags."""
    result = _run_node_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'
const args = minimist(['--no-headless', '--headed'], { boolean: ['headless', 'headed'] })
console.log(JSON.stringify({
    headless: args.headless,
    headed: args.headed
}))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["headless"] is False, f"headless should be false, got: {data['headless']}"
    assert data["headed"] is True, f"headed should be true, got: {data['headed']}"


def test_minimist_parses_shorthand_flags():
    """minimist must correctly parse shorthand flags like -abc."""
    result = _run_node_ts("""
import { minimist } from './packages/playwright-core/src/tools/cli-client/minimist.ts'
const args = minimist(['-abc'], { boolean: ['a', 'b', 'c'] })
console.log(JSON.stringify({
    a: args.a,
    b: args.b,
    c: args.c
}))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["a"] is True, f"a should be true"
    assert data["b"] is True, f"b should be true"
    assert data["c"] is True, f"c should be true"


def test_program_imports_minimist():
    """program.ts must import from the vendored minimist module."""
    program_path = CLI_CLIENT / "program.ts"
    content = program_path.read_text()
    assert "from './minimist'" in content, "program.ts must import from './minimist'"
    assert "require('minimist')" not in content, "program.ts must not use require('minimist')"


def test_session_imports_minimist_type():
    """session.ts must import MinimistArgs type from vendored minimist."""
    session_path = CLI_CLIENT / "session.ts"
    content = session_path.read_text()
    assert "from './minimist'" in content, "session.ts must import from './minimist'"


def test_claude_md_has_generated_with_rule():
    """CLAUDE.md must include the new 'Never add Generated with' rule."""
    claude_path = REPO / "CLAUDE.md"
    content = claude_path.read_text()
    assert "Never add \"Generated with\" in commit message." in content, \
        "CLAUDE.md must include 'Never add \"Generated with\" in commit message.' rule"


def test_deps_list_includes_minimist():
    """DEPS.list must include minimist.ts as a dependency."""
    deps_path = CLI_CLIENT / "DEPS.list"
    content = deps_path.read_text()
    assert "[minimist.ts]" in content, "DEPS.list must declare [minimist.ts] section"
    assert "./minimist.ts" in content, "DEPS.list must reference ./minimist.ts"


def test_package_json_no_minimist_types():
    """package.json must not have @types/minimist dev dependency."""
    package_path = REPO / "package.json"
    content = package_path.read_text()
    assert '"@types/minimist"' not in content, "package.json must not have @types/minimist dependency"


def test_minimist_exports_correct_types():
    """minimist.ts must export minimist function and MinimistArgs type."""
    minimist_path = CLI_CLIENT / "minimist.ts"
    content = minimist_path.read_text()
    assert "export function minimist" in content, "minimist.ts must export minimist function"
    assert "export interface MinimistArgs" in content, "minimist.ts must export MinimistArgs interface"
    assert "export interface MinimistOptions" in content, "minimist.ts must export MinimistOptions interface"


def test_program_type_safety():
    """program.ts must use proper type assertions for args.session and args.all."""
    program_path = CLI_CLIENT / "program.ts"
    content = program_path.read_text()
    # After fix, args.session should be cast with `as string`
    assert "args.session as string" in content, "program.ts must cast args.session to string"
    # After fix, args.all should be converted to boolean with !!
    assert "!!args.all" in content, "program.ts must convert args.all to boolean with !!"


def test_session_type_safety():
    """session.ts must use proper type assertions for cliArgs.session."""
    session_path = CLI_CLIENT / "session.ts"
    content = session_path.read_text()
    # After fix, cliArgs.session should be cast with `as string`
    assert "cliArgs.session as string" in content, "session.ts must cast cliArgs.session to string"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
