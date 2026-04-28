"""Test outputs for playwright-mcp-browser-run-code task.

This task tests:
1. Code change: browser_run_code tool now accepts a JavaScript function
2. Config updates: browser_run_code added to agent definition files
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/playwright")


def test_run_code_ts_uses_function_format():
    """[f2p] runCode.ts should describe function-based code parameter"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    describe_match = re.search(r'\.describe\s*\(\s*`([^`]+)`', content)
    assert describe_match, "code schema should have a describe() call with template literal"
    description = describe_match.group(1)

    assert re.search(r'\bfunction\b', description, re.IGNORECASE), \
        "Description should mention that the parameter accepts a function"
    assert re.search(r'\bpage\b', description), \
        "Description should mention the page parameter"


def test_run_code_invokes_as_function():
    """[f2p] runCode.ts should invoke the code parameter as a callable with page"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    handle_idx = content.find('handle:')
    assert handle_idx != -1, "runCode.ts must have a handle function"
    handle_section = content[handle_idx:]

    assert 'params.code' in handle_section, "handle should reference params.code"

    snippet_match = re.search(r'snippet\s*=\s*`([\s\S]*?)`', handle_section)
    assert snippet_match, "handle must contain a vm execution snippet"
    snippet_body = snippet_match.group(1)

    assert re.search(r'\(page\)', snippet_body), \
        "VM execution snippet must invoke user code with page as an argument"


def test_run_code_ts_no_direct_injection():
    """[f2p] runCode.ts should not directly inject code into IIFE"""
    run_code_path = REPO / "packages/playwright/src/mcp/browser/tools/runCode.ts"
    content = run_code_path.read_text()

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '${params.code}' in line:
            stripped = line.strip()
            assert not re.match(r'^\$\{params\.code\}\s*;?\s*$', stripped), \
                f"Line {i+1} directly injects params.code as raw statements: {stripped}"


def test_claude_agents_has_browser_run_code():
    """[f2p] .claude/agents/playwright-test-planner.md should include browser_run_code tool"""
    agents_path = REPO / "examples/todomvc/.claude/agents/playwright-test-planner.md"
    content = agents_path.read_text()

    assert "mcp__playwright-test__browser_run_code" in content, \
        "playwright-test-planner.md should include browser_run_code tool"

    press_key_idx = content.find("mcp__playwright-test__browser_press_key")
    run_code_idx = content.find("mcp__playwright-test__browser_run_code")
    select_option_idx = content.find("mcp__playwright-test__browser_select_option")

    assert press_key_idx < run_code_idx < select_option_idx, \
        "browser_run_code should be alphabetically between press_key and select_option"


def test_github_agents_has_browser_run_code():
    """[f2p] .github/agents/playwright-test-planner.agent.md should include browser_run_code tool"""
    agents_path = REPO / "examples/todomvc/.github/agents/playwright-test-planner.agent.md"
    content = agents_path.read_text()

    assert "playwright-test/browser_run_code" in content, \
        ".github/agents/playwright-test-planner.agent.md should include browser_run_code tool"

    lines = content.split('\n')
    press_key_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_press_key" in line)
    run_code_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_run_code" in line)
    select_option_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_select_option" in line)

    assert press_key_line < run_code_line < select_option_line, \
        "browser_run_code should be alphabetically between press_key and select_option"


def test_packages_agents_has_browser_run_code():
    """[f2p] packages/playwright/src/agents/playwright-test-planner.agent.md should include browser_run_code tool"""
    agents_path = REPO / "packages/playwright/src/agents/playwright-test-planner.agent.md"
    content = agents_path.read_text()

    assert "playwright-test/browser_run_code" in content, \
        "packages/agents/playwright-test-planner.agent.md should include browser_run_code tool"

    lines = content.split('\n')
    press_key_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_press_key" in line)
    run_code_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_run_code" in line)
    select_option_line = next(i for i, line in enumerate(lines) if "playwright-test/browser_select_option" in line)

    assert press_key_line < run_code_line < select_option_line, \
        "browser_run_code should be alphabetically between press_key and select_option"


def test_typescript_compiles():
    """[p2p] TypeScript project should build without errors"""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"Build failed (rc={result.returncode}):\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_run_code_test_discovery():
    """[p2p] run-code.spec.ts tests should be discoverable by Playwright"""
    result = subprocess.run(
        ["npx", "playwright", "test", "tests/mcp/run-code.spec.ts", "--list"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Test discovery failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
    assert "browser_run_code" in result.stdout, \
        "Test discovery output should reference browser_run_code tests"
    assert "browser_run_code block" in result.stdout, \
        "Test discovery should include browser_run_code block test"
    assert "browser_run_code no-require" in result.stdout, \
        "Test discovery should include browser_run_code no-require test"
    assert "browser_run_code return value" in result.stdout, \
        "Test discovery should include browser_run_code return value test"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_3():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_verify_clean_tree():
    """pass_to_pass | CI job 'docs & lint' → step 'Verify clean tree'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ -n $(git status -s) ]]; then\n  echo "ERROR: tree is dirty after npm run build:"\n  git diff\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify clean tree' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_pip():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -r utils/doclint/linting-code-snippets/python/requirements.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_mvn():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'mvn package'], cwd=os.path.join(REPO, 'utils/doclint/linting-code-snippets/java'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_node():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/doclint/linting-code-snippets/cli.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")