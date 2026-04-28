"""
Task: playwright-choremcp-change-browserruncode-argument-to
Repo: playwright @ 703996071cb3a7ec642b30a2b428c369c3ebb7c7
PR:   38517

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _npm_install():
    """Install npm dependencies if needed."""
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    return r.returncode == 0


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_runcode_function_invocation():
    """browser_run_code must invoke user code as a function with page argument."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const vm = require('vm');

const src = fs.readFileSync(
    '/workspace/playwright/packages/playwright/src/mcp/browser/tools/runCode.ts',
    'utf8'
);

// Source must contain function invocation pattern
if (!src.includes('const result = await (${params.code})(page);')) {
    console.error('FAIL: missing function invocation pattern');
    process.exit(1);
}

// Simulate the execution with a mock page object
const userCode = 'async (page) => { return page.url(); }';
const mockPage = { url: () => 'https://test.example.com' };

let resolvedValue = null;
const __end__ = {
    resolve: (v) => { resolvedValue = v; },
    reject: (e) => { throw e; }
};

const context = { page: mockPage, __end__ };
vm.createContext(context);

const snippet = `(async () => {
    try {
        const result = await (${userCode})(page);
        __end__.resolve(JSON.stringify(result));
    } catch (e) {
        __end__.reject(e);
    }
})()`;

vm.runInContext(snippet, context).then(() => {
    const parsed = JSON.parse(resolvedValue);
    if (parsed === 'https://test.example.com') {
        console.log('PASS');
    } else {
        console.error('FAIL: expected https://test.example.com, got ' + parsed);
        process.exit(1);
    }
}).catch(e => {
    console.error('FAIL: ' + e.message);
    process.exit(1);
});
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, (
        f"Function invocation test failed:\n{result.stdout}\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_runcode_schema_describes_function():
    """Schema description must say 'function', not 'snippet'."""
    src = Path(f"{REPO}/packages/playwright/src/mcp/browser/tools/runCode.ts").read_text()
    assert "A JavaScript function containing Playwright code to execute" in src, \
        "Schema description should describe a function, not a snippet"
    assert "async (page) =>" in src, \
        "Schema example should show async (page) => arrow function syntax"


# [pr_diff] fail_to_pass
def test_runcode_addcode_wraps_invocation():
    """response.addCode must show function invocation format."""
    src = Path(f"{REPO}/packages/playwright/src/mcp/browser/tools/runCode.ts").read_text()
    # Check that addCode wraps code with await and function invocation
    assert 'addCode(`await (' in src, \
        "addCode should wrap code as function invocation"
    assert "addCode(params.code)" not in src, \
        "addCode should not just echo raw params.code"


# [pr_diff] fail_to_pass
def test_runcode_no_iife_wrapper():
    """Old IIFE code wrapper pattern must be replaced."""
    src = Path(f"{REPO}/packages/playwright/src/mcp/browser/tools/runCode.ts").read_text()
    # Old pattern had a bare ${params.code}; statement inside an IIFE
    assert "${params.code};" not in src, \
        "Should not have bare ${params.code}; — must use (${params.code})(page)"


# ---------------------------------------------------------------------------
# Config update tests — agent definition files must list browser_run_code
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_agent_has_browser_run_code():
    """Claude agent planner must list browser_run_code in tools."""
    content = Path(
        f"{REPO}/examples/todomvc/.claude/agents/playwright-test-planner.md"
    ).read_text()
    assert "browser_run_code" in content, \
        "playwright-test-planner.md should include browser_run_code in tools list"


# [pr_diff] fail_to_pass
def test_packages_agent_has_browser_run_code():
    """Packages agent planner must list browser_run_code in tools."""
    content = Path(
        f"{REPO}/packages/playwright/src/agents/playwright-test-planner.agent.md"
    ).read_text()
    assert "browser_run_code" in content, \
        "playwright-test-planner.agent.md should include browser_run_code in tools"


# [pr_diff] fail_to_pass
def test_github_agent_has_browser_run_code():
    """GitHub agent planner must list browser_run_code in tools."""
    content = Path(
        f"{REPO}/examples/todomvc/.github/agents/playwright-test-planner.agent.md"
    ).read_text()
    assert "browser_run_code" in content, \
        "playwright-test-planner.agent.md should include browser_run_code in tools"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural sanity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_runcode_uses_vm_context():
    """runCode.ts must still use vm.createContext and vm.runInContext."""
    src = Path(f"{REPO}/packages/playwright/src/mcp/browser/tools/runCode.ts").read_text()
    assert "vm.createContext" in src, "Should use vm.createContext"
    assert "vm.runInContext" in src, "Should use vm.runInContext"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build():
    """Repository build passes (pass_to_pass)."""
    # Install dependencies first
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repository workspace consistency check passes (pass_to_pass)."""
    # Install dependencies first
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """Repository dependency check passes (pass_to_pass)."""
    # Install dependencies and build first
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_test_types():
    """Repository type tests pass (pass_to_pass)."""
    # Install dependencies and build first
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "test-types"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Test types failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repository ESLint check passes on MCP browser code (pass_to_pass)."""
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright/src/mcp/browser/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_tests():
    """Repository test linting passes (pass_to_pass)."""
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint tests failed:\n{r.stderr[-500:]}"