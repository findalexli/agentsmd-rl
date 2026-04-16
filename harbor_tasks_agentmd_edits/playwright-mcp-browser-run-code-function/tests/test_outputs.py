"""
Tests for the browser_run_code MCP tool change.

This PR changes the browser_run_code tool to accept a JavaScript function
instead of raw Playwright code snippets. The function receives the page
object as an argument.

OLD format: code: 'await page.getByRole("button").click()'
NEW format: code: 'async (page) => { await page.getByRole("button").click(); }'

Additionally, the PR updates agent config files to include the new
browser_run_code tool in the tools list.
"""

import subprocess
import sys
from pathlib import Path
import os

REPO = Path(os.environ.get("REPO", "/workspace/playwright"))

def _check_file_contains(file_path: Path, patterns: list, should_contain: bool = True) -> tuple:
    """Check if file contains all patterns. Returns (success, message)."""
    if not file_path.exists():
        return False, f"File not found: {file_path}"

    content = file_path.read_text()
    missing = []

    for pattern in patterns:
        if should_contain and pattern not in content:
            missing.append(f"Missing required: {pattern}")
        elif not should_contain and pattern in content:
            missing.append(f"Should not contain: {pattern}")

    if missing:
        return False, "; ".join(missing)
    return True, "OK"


def test_runCode_uses_function_wrapper():
    """
    [code] fail_to_pass
    The runCode.ts tool must wrap code parameter as a function call.
    """
    runCode_path = REPO / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "runCode.ts"

    success, msg = _check_file_contains(runCode_path, [
        "await (${params.code})(page)",
        "async (page) =>",
    ])

    assert success, msg


def test_runCode_updated_description():
    """
    [code] fail_to_pass
    The codeSchema description must document the function-based approach.
    """
    runCode_path = REPO / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "runCode.ts"

    success, msg = _check_file_contains(runCode_path, [
        "invoked with a single argument, page",
        "async (page) =>",
    ])

    assert success, msg


def test_runCode_no_raw_code_injection():
    """
    [code] fail_to_pass
    The old raw code injection pattern should be removed.
    """
    runCode_path = REPO / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "runCode.ts"

    content = runCode_path.read_text()

    # Should NOT have the old pattern of injecting raw code
    old_pattern = "${params.code};"
    assert old_pattern not in content, f"Should not use raw code injection pattern: {old_pattern}"


def test_agent_config_claude_includes_tool():
    """
    [config] fail_to_pass
    The .claude/agents/playwright-test-planner.md must include browser_run_code tool.
    """
    config_path = REPO / "examples" / "todomvc" / ".claude" / "agents" / "playwright-test-planner.md"

    success, msg = _check_file_contains(config_path, [
        "mcp__playwright-test__browser_run_code",
    ])

    assert success, msg


def test_agent_config_github_includes_tool():
    """
    [config] fail_to_pass
    The .github/agents/playwright-test-planner.agent.md must include browser_run_code tool.
    """
    config_path = REPO / "examples" / "todomvc" / ".github" / "agents" / "playwright-test-planner.agent.md"

    success, msg = _check_file_contains(config_path, [
        "playwright-test/browser_run_code",
    ])

    assert success, msg


def test_agent_config_packages_includes_tool():
    """
    [config] fail_to_pass
    The packages/playwright/src/agents/playwright-test-planner.agent.md must include browser_run_code tool.
    """
    config_path = REPO / "packages" / "playwright" / "src" / "agents" / "playwright-test-planner.agent.md"

    success, msg = _check_file_contains(config_path, [
        "playwright-test/browser_run_code",
    ])

    assert success, msg


def test_specs_updated_to_function_format():
    """
    [tests] fail_to_pass
    The test file must use the new function-based code format.
    """
    spec_path = REPO / "tests" / "mcp" / "run-code.spec.ts"

    success, msg = _check_file_contains(spec_path, [
        "async (page) => await page.getByRole",
        "async (page) => { await page.getByRole",
    ])

    assert success, msg


def test_syntax_check():
    """
    [syntax] pass_to_pass
    Modified TypeScript files must have valid syntax.
    """
    runCode_path = REPO / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "runCode.ts"

    # Use TypeScript compiler to check syntax
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", str(runCode_path)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    # If tsc is not available, try node to parse as JavaScript module (loose check)
    if result.returncode != 0 and "Cannot find module" in result.stderr:
        # TypeScript not fully set up, check basic file structure
        content = runCode_path.read_text()
        assert "export default" in content, "File should have export"
        assert "import " in content, "File should have imports"
        return

    assert result.returncode == 0, f"TypeScript syntax error: {result.stderr}"


def test_file_structure_preserved():
    """
    [structure] pass_to_pass
    The runCode.ts file structure must remain valid with proper exports.
    """
    runCode_path = REPO / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "runCode.ts"

    content = runCode_path.read_text()

    # Check essential structure
    assert "import vm from 'vm';" in content, "Should import vm module"
    assert "import { z } from 'playwright-core/lib/mcpBundle';" in content, "Should import zod"
    assert "const codeSchema = z.object" in content, "Should define codeSchema"
    assert "const runCode = defineTabTool" in content, "Should define runCode tool"
    assert "export default [" in content, "Should export default array"
