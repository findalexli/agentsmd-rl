"""
Task: svelte-simplify-parser-error-handling
Repo: svelte @ 8966601dcd14582cd46d4fbb7c5cf1b444292255
PR:   18077

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/svelte"
PKG = os.path.join(REPO, "packages/svelte")
PARSE_DIR = os.path.join(PKG, "src/compiler/phases/1-parse")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified JS files parse without syntax errors (via acorn)."""
    files = [
        "src/compiler/phases/1-parse/acorn.js",
        "src/compiler/phases/1-parse/index.js",
        "src/compiler/phases/1-parse/read/context.js",
        "src/compiler/phases/1-parse/read/expression.js",
        "src/compiler/phases/1-parse/read/script.js",
    ]
    for f in files:
        full_path = os.path.join(PKG, f)
        assert os.path.isfile(full_path), f"File not found: {f}"
        r = subprocess.run(
            [
                "node", "-e",
                f"require('acorn').parse(require('fs').readFileSync('{full_path}','utf8'),"
                f"{{sourceType:'module',ecmaVersion:2024}})"
            ],
            cwd=PKG,
            capture_output=True,
            timeout=15,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural refactoring checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_acorn_centralizes_error_handling():
    """acorn.js must import the error module and contain js_parse_error call."""
    src = Path(os.path.join(PARSE_DIR, "acorn.js")).read_text()

    # Must import from the errors module
    assert re.search(
        r"import\b.*from\s+['\"].*errors\.js['\"]", src
    ), "acorn.js does not import from errors module"

    # Must call js_parse_error somewhere in the module
    assert "js_parse_error" in src, "acorn.js does not call js_parse_error"


# [pr_diff] fail_to_pass
def test_parse_expression_at_internal_error_handling():
    """parse_expression_at must have internal try/catch error handling."""
    src = Path(os.path.join(PARSE_DIR, "acorn.js")).read_text()

    # Extract parse_expression_at function body
    # Find the function declaration and get until the next top-level function or end
    match = re.search(
        r"export\s+function\s+parse_expression_at\b.*?\{(.*)",
        src,
        re.DOTALL,
    )
    assert match, "parse_expression_at function not found in acorn.js"

    fn_start = match.start()
    # Find the balanced end of the function by counting braces
    brace_count = 0
    fn_body = ""
    for i, ch in enumerate(src[fn_start:]):
        if ch == "{":
            brace_count += 1
        elif ch == "}":
            brace_count -= 1
            if brace_count == 0:
                fn_body = src[fn_start : fn_start + i + 1]
                break

    assert fn_body, "Could not extract parse_expression_at function body"
    assert "try" in fn_body and "catch" in fn_body, (
        "parse_expression_at does not have try/catch error handling"
    )


# [pr_diff] fail_to_pass
def test_parser_no_acorn_error():
    """Parser class must not have acorn_error method — error handling centralized in acorn.js."""
    src = Path(os.path.join(PARSE_DIR, "index.js")).read_text()

    # The acorn_error method definition should not exist
    assert not re.search(
        r"acorn_error\s*\(", src
    ), "Parser class still has acorn_error method"

    # The regex_position_indicator should also be moved out of index.js
    assert "regex_position_indicator" not in src, (
        "regex_position_indicator should be moved out of index.js"
    )


# [pr_diff] fail_to_pass
def test_context_no_redundant_error_handling():
    """context.js must not have redundant try/catch around parse_expression_at."""
    src = Path(os.path.join(PARSE_DIR, "read/context.js")).read_text()

    # Should not call parser.acorn_error
    assert "parser.acorn_error" not in src, (
        "context.js still calls parser.acorn_error"
    )

    # The read_pattern function should not have a try/catch wrapping parse_expression_at
    # Find read_pattern function
    match = re.search(r"function\s+read_pattern\b", src)
    assert match, "read_pattern function not found in context.js"

    fn_start = match.start()
    brace_count = 0
    fn_body = ""
    for i, ch in enumerate(src[fn_start:]):
        if ch == "{":
            brace_count += 1
        elif ch == "}":
            brace_count -= 1
            if brace_count == 0:
                fn_body = src[fn_start : fn_start + i + 1]
                break

    # The function body should not have try/catch
    assert "} catch" not in fn_body, (
        "read_pattern still wraps parse_expression_at in try/catch"
    )


# [pr_diff] fail_to_pass
def test_script_no_redundant_error_handling():
    """script.js must call acorn.parse directly without try/catch wrapping."""
    src = Path(os.path.join(PARSE_DIR, "read/script.js")).read_text()

    # Should not call parser.acorn_error
    assert "parser.acorn_error" not in src, (
        "script.js still calls parser.acorn_error"
    )

    # Find the read_script function and check it doesn't wrap acorn.parse in try/catch
    match = re.search(r"function\s+read_script\b", src)
    assert match, "read_script function not found in script.js"

    fn_start = match.start()
    brace_count = 0
    fn_body = ""
    for i, ch in enumerate(src[fn_start:]):
        if ch == "{":
            brace_count += 1
        elif ch == "}":
            brace_count -= 1
            if brace_count == 0:
                fn_body = src[fn_start : fn_start + i + 1]
                break

    # Find the acorn.parse call region and check no try/catch around it
    parse_idx = fn_body.find("acorn.parse")
    assert parse_idx != -1, "acorn.parse call not found in read_script"

    # Look at the 200 chars before acorn.parse — should not contain a try {
    preceding = fn_body[max(0, parse_idx - 200) : parse_idx]
    # Count unmatched try blocks: if there's a "try {" without a closing "}" before our call
    try_count = preceding.count("try {") + preceding.count("try{")
    catch_count = preceding.count("catch")
    assert try_count <= catch_count, (
        "acorn.parse in read_script is wrapped in a try block"
    )


# [pr_diff] fail_to_pass
def test_expression_rethrows():
    """expression.js must rethrow errors instead of calling parser.acorn_error."""
    src = Path(os.path.join(PARSE_DIR, "read/expression.js")).read_text()

    # Should NOT call parser.acorn_error
    assert "parser.acorn_error" not in src, (
        "expression.js still calls parser.acorn_error"
    )

    # Should have 'throw err' or 'throw error' in the catch block
    assert re.search(r"\bthrow\s+err\b", src), (
        "expression.js does not rethrow error in catch block"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=os.path.join(REPO, "packages/svelte"),
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_parser_tests():
    """Parser and compiler-errors tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "pnpm", "vitest", "run",
            "packages/svelte/tests/parser-modern",
            "packages/svelte/tests/parser-legacy",
            "packages/svelte/tests/compiler-errors",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Parser tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's lint passes after build (pass_to_pass)."""
    # Build first (required for prettier-plugin-svelte to work)
    r_build = subprocess.run(
        ["pnpm", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r_build.returncode == 0, f"Build failed:\n{r_build.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_syntax_check_acorn():
    """All JS files in the repo parse without syntax errors (pass_to_pass)."""
    # Check that modified files parse correctly with acorn
    files = [
        "packages/svelte/src/compiler/phases/1-parse/acorn.js",
        "packages/svelte/src/compiler/phases/1-parse/index.js",
        "packages/svelte/src/compiler/phases/1-parse/read/context.js",
        "packages/svelte/src/compiler/phases/1-parse/read/expression.js",
        "packages/svelte/src/compiler/phases/1-parse/read/script.js",
    ]
    for f in files:
        full_path = os.path.join(REPO, f)
        assert os.path.isfile(full_path), f"File not found: {f}"
        r = subprocess.run(
            [
                "node", "-e",
                f"require('acorn').parse(require('fs').readFileSync('{full_path}','utf8'),"
                f"{{sourceType:'module',ecmaVersion:2024}})"
            ],
            cwd=os.path.join(REPO, "packages/svelte"),
            capture_output=True,
            timeout=15,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr.decode()}"
