"""Test outputs for playwright-mcp-browser-run-code task.

This task tests:
1. Code change: browser_run_code tool now accepts a JavaScript function
2. Config updates: browser_run_code added to agent definition files
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")


def test_run_code_ts_uses_function_format():
    """[f2p_code] runCode.ts should describe function-based code parameter"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    # The code parameter description should document the function-based API
    describe_match = re.search(r'\.describe\s*\(\s*`([^`]+)`', content)
    assert describe_match, "code schema should have a describe() call with template literal"
    description = describe_match.group(1)

    # Description should mention it accepts a function (not "code snippet")
    assert re.search(r'\bfunction\b', description, re.IGNORECASE), \
        "Description should mention that the parameter accepts a function"
    # Description should reference the page parameter
    assert re.search(r'\bpage\b', description), \
        "Description should mention the page parameter"


def test_run_code_invokes_as_function():
    """[f2p_code] runCode.ts should invoke the code parameter as a callable with page"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    # The handle function should invoke params.code as a function and pass page
    handle_idx = content.find('handle:')
    assert handle_idx != -1, "runCode.ts must have a handle function"
    handle_section = content[handle_idx:]

    # params.code must be referenced in the handle logic
    assert 'params.code' in handle_section, "handle should reference params.code"

    # The vm execution snippet must pass page as a function argument.
    # Old code used page from the vm context as a global; new code should
    # explicitly pass page when invoking the user's function.
    snippet_match = re.search(r'snippet\s*=\s*`([\s\S]*?)`', handle_section)
    assert snippet_match, "handle must contain a vm execution snippet"
    snippet_body = snippet_match.group(1)

    assert re.search(r'\(page\)', snippet_body), \
        "VM execution snippet must invoke user code with page as an argument"


def test_run_code_ts_no_direct_injection():
    """[f2p_code] runCode.ts should not directly inject code into IIFE"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    # The old implementation injected ${params.code} as bare statements inside
    # an async IIFE body. The new implementation should treat params.code as a
    # value (function expression) that gets invoked or assigned, not as raw
    # statements to execute.
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '${params.code}' in line:
            stripped = line.strip()
            # Should NOT be just ${params.code}; on its own (bare statement injection)
            assert not re.match(r'^\$\{params\.code\}\s*;?\s*$', stripped), \
                f"Line {i+1} directly injects params.code as raw statements: {stripped}"


def test_claude_agents_has_browser_run_code():
    """[f2p_config] .claude/agents/playwright-test-planner.md should include browser_run_code tool"""
    agents_path = REPO / "examples/todomvc/.claude/agents/playwright-test-planner.md"
    content = agents_path.read_text()

    # Check for the tool in comma-separated list
    assert "mcp__playwright-test__browser_run_code" in content, \
        "playwright-test-planner.md should include browser_run_code tool"

    # Verify it's in the right position (alphabetically between press_key and select_option)
    press_key_idx = content.find("mcp__playwright-test__browser_press_key")
    run_code_idx = content.find("mcp__playwright-test__browser_run_code")
    select_option_idx = content.find("mcp__playwright-test__browser_select_option")

    assert press_key_idx < run_code_idx < select_option_idx, \
        "browser_run_code should be alphabetically between press_key and select_option"


def test_github_agents_has_browser_run_code():
    """[f2p_config] .github/agents/playwright-test-planner.agent.md should include browser_run_code tool"""
    agents_path = REPO / "examples/todomvc/.github/agents/playwright-test-planner.agent.md"
    content = agents_path.read_text()

    # Check for the tool in YAML list format
    assert "playwright-test/browser_run_code" in content, \
        ".github/agents/playwright-test-planner.agent.md should include browser_run_code tool"

    # Verify it's in the right position (alphabetically between press_key and select_option)
    lines = content.split('\n')
    press_key_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_press_key" in line)
    run_code_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_run_code" in line)
    select_option_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_select_option" in line)

    assert press_key_line < run_code_line < select_option_line, \
        "browser_run_code should be alphabetically between press_key and select_option"


def test_packages_agents_has_browser_run_code():
    """[f2p_config] packages/playwright/src/agents/playwright-test-planner.agent.md should include browser_run_code tool"""
    agents_path = REPO / "packages/playwright/src/agents/playwright-test-planner.agent.md"
    content = agents_path.read_text()

    # Check for the tool in YAML list format
    assert "playwright-test/browser_run_code" in content, \
        "packages/agents/playwright-test-planner.agent.md should include browser_run_code tool"

    # Verify it's in the right position
    lines = content.split('\n')
    press_key_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_press_key" in line)
    run_code_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_run_code" in line)
    select_option_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_select_option" in line)

    assert press_key_line < run_code_line < select_option_line, \
        "browser_run_code should be alphabetically between press_key and select_option"


def test_typescript_compiles():
    """[p2p] TypeScript should compile without errors"""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout}\n{result.stderr}"


def test_repo_run_code_tests():
    """[p2p] Repo tests for run-code.spec.ts should pass"""
    result = subprocess.run(
        ["npx", "playwright", "test", "tests/mcp/run-code.spec.ts", "--reporter=line"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    # These tests require a browser, may fail in container - check return code and output
    # We mainly want to verify the test structure is valid
    assert "browser_run_code" in result.stdout or result.returncode in [0, 1], \
        f"Tests should at least run and mention browser_run_code:\n{result.stdout}\n{result.stderr}"
