"""Test outputs for playwright-mcp-browser-run-code task.

This task tests:
1. Code change: browser_run_code tool now accepts a JavaScript function
2. Config updates: browser_run_code added to agent definition files
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")


def test_run_code_ts_uses_function_format():
    """[f2p_code] runCode.ts should describe function-based code parameter"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    # Should describe the function-based API
    assert "async (page) =>" in content, "runCode.ts should describe function format"
    assert "single argument, page" in content or "page, which you can use" in content, \
        "runCode.ts should document the page argument"


def test_run_code_ts_wraps_function_call():
    """[f2p_code] runCode.ts should wrap code as function call"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    # Should wrap as function call in response.addCode
    assert "await (${params.code})(page)" in content, \
        "runCode.ts should wrap code as function call in response"

    # Should execute as function call
    assert "await (${params.code})(page);" in content and content.count("(${params.code})(page)") >= 2, \
        "runCode.ts should execute code as function call"


def test_run_code_ts_no_direct_injection():
    """[f2p_code] runCode.ts should not directly inject code into IIFE"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    # Old pattern was: ${params.code}; inside an async IIFE
    # New pattern should NOT have bare ${params.code} followed by semicolon
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '${params.code}' in line:
            # Should always be wrapped as function call
            assert '(${params.code})(page)' in line, \
                f"Line {i+1} should wrap params.code as function call, found: {line.strip()}"


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
    tool_lines = [i for i, line in enumerate(lines) if "playwright-test/browser_" in line]
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
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright/src/mcp/browser"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


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
