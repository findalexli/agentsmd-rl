"""
Task: playwright-mcp-expression-evaluate-fix
Repo: playwright @ cec7b21afa00c0f48e46859c683680a2c6e9e029
PR:   39979

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This tests the MCP browser_evaluate tool's ability to properly distinguish
between expressions (like `[1,2,3].map(x => x*2)`) and actual functions.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_expressions_with_arrow_not_wrapped():
    """
    Expressions containing '=>' should NOT be wrapped in () => ().

    The bug: `[1,2,3].map(x => x*2)` was incorrectly detected as a function
    because it contains '=>', and got wrapped as `() => ([1,2,3].map(x => x*2))`
    which executes the map but ignores the result.

    Fixed behavior: The code should properly detect actual function syntax
    (() =>, x =>, async () =>, function) vs expressions that happen to contain '=>'.
    """
    src_path = Path(f"{REPO}/packages/playwright-core/src/tools/backend/evaluate.ts")
    src = src_path.read_text()

    # Check that the fix is present - we look for the new implementation pattern
    # The fix uses proper function detection instead of simple includes('=>')

    # The old buggy code: if (!params.function.includes('=>'))
    # The new code should NOT have this simple check
    if "!params.function.includes('=>')" in src:
        assert False, "Bug still present: using simple includes('=>') check"

    # The fix uses a more sophisticated approach with evalResult.isFunction
    assert "evalResult.isFunction" in src, "Fix not applied: missing evalResult.isFunction check"

    # The fix properly detects functions and only wraps non-functions
    assert "codeExpression = evalResult.isFunction ? expression" in src, \
        "Fix not applied: missing conditional codeExpression logic"


def test_proper_function_detection():
    """
    Verify the new implementation properly handles various function syntaxes.

    The fix should correctly identify:
    - Arrow functions: () => ..., x => ..., async () => ...
    - Regular functions: function foo() { ... }
    - Expressions that happen to contain '=>': [1,2,3].map(x => x*2)
    """
    src_path = Path(f"{REPO}/packages/playwright-core/src/tools/backend/evaluate.ts")
    src = src_path.read_text()

    # Check for the new implementation that evaluates and checks typeof
    assert "typeof value === 'function'" in src, \
        "Fix not applied: missing typeof function check"

    # The implementation should use eval to check the actual value type
    assert "const value = eval" in src, \
        "Fix not applied: missing eval-based value detection"

    # The code should return both result and isFunction flag
    assert "return { result, isFunction }" in src, \
        "Fix not applied: missing result + isFunction return"


def test_nullish_coalescing_for_undefined():
    """
    Verify the nullish coalescing operator is used for undefined results.

    The PR also changed: JSON.stringify(result, null, 2) || 'undefined'
    to: JSON.stringify(evalResult.result, null, 2) ?? 'undefined'

    This properly handles the case where the result is 0, false, or ''.
    """
    src_path = Path(f"{REPO}/packages/playwright-core/src/tools/backend/evaluate.ts")
    src = src_path.read_text()

    # Check for nullish coalescing operator usage
    assert "?? 'undefined'" in src or '?? "undefined"' in src, \
        "Fix not applied: missing nullish coalescing (??) for undefined fallback"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    src_path = Path(f"{REPO}/packages/playwright-core/src/tools/backend/evaluate.ts")
    src = src_path.read_text()

    # The handle function should have substantial implementation
    handle_start = src.find("handle: async (tab, params, response)")
    assert handle_start > 0, "handle function not found"

    # Extract the function body (up to the closing of the handle object)
    func_section = src[handle_start:handle_start + 3000]

    # Check for meaningful statements (not just pass/return)
    # The fixed version has:
    # - const expression = params.function
    # - if (params.ref) ...
    # - await tab.waitForCompletion...
    # - let evalResult...
    # - if (locator?.locator) ... else ...
    # - const codeExpression = evalResult.isFunction ? ...
    # - response.addCode...
    # - await response.addResult...

    assert "const expression = params.function" in func_section, \
        "Function missing: const expression = params.function"
    assert "await tab.waitForCompletion" in func_section, \
        "Function missing: await tab.waitForCompletion"
    assert "response.addResult" in func_section, \
        "Function missing: response.addResult call"

    # Count the number of assignment statements to ensure substantial logic
    assignments = func_section.count("const ") + func_section.count("let ")
    assert assignments >= 5, f"Function appears to be a stub (only {assignments} assignments)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify CI/CD checks pass on base commit
# ---------------------------------------------------------------------------

def test_repo_tsc():
    """Repo's TypeScript compilation passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_check_deps():
    """Repo's dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Dependency check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_lint_packages():
    """Repo's package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Package lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_lint_tests():
    """Repo's test linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Test lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_test_types():
    """Repo's type tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-types"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Type tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_eslint_backend():
    """Repo's eslint check passes on modified backend directory (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0", "packages/playwright-core/src/tools/backend/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
