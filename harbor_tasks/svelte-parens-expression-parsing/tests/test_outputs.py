"""
Task: svelte-parens-expression-parsing
Repo: svelte @ 0395ef0df7ff12c4b633b650c5f2db512d382836
PR:   18075

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/svelte"


def _parse_template(template):
    """Parse a Svelte template via the compiler and return the AST as a dict."""
    script = (
        "import { parse } from "
        "'/workspace/svelte/packages/svelte/src/compiler/index.js';\n"
        f"const ast = parse({json.dumps(template)}, {{ modern: true }});\n"
        "console.log(JSON.stringify(ast));\n"
    )
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Failed to parse template {template!r}:\n{r.stderr}"
    )
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified compiler JS files can be loaded as ES modules."""
    files = [
        "packages/svelte/src/compiler/phases/1-parse/acorn.js",
        "packages/svelte/src/compiler/phases/1-parse/read/expression.js",
        "packages/svelte/src/compiler/phases/1-parse/read/context.js",
        "packages/svelte/src/compiler/phases/1-parse/state/tag.js",
    ]
    imports = "; ".join(
        f"await import('/workspace/svelte/{f}')" for f in files
    )
    script = f"{imports}; console.log('OK');"
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Module load failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parens_before_block_comment():
    """Template expression {(/**/ 42)} must parse — paren before block comment."""
    ast = _parse_template("{(/**/ 42)}")
    nodes = ast["fragment"]["nodes"]
    assert len(nodes) == 1, f"Expected 1 node, got {len(nodes)}"
    tag = nodes[0]
    assert tag["type"] == "ExpressionTag", f"Expected ExpressionTag, got {tag['type']}"
    expr = tag["expression"]
    assert expr["type"] == "Literal", f"Expected Literal, got {expr['type']}"
    assert expr["value"] == 42, f"Expected value 42, got {expr['value']}"


# [pr_diff] fail_to_pass
def test_parens_before_named_comment():
    """Template expression {(/* comment */ \"hello\")} must parse correctly."""
    ast = _parse_template('{(/* comment */ "hello")}')
    expr = ast["fragment"]["nodes"][0]["expression"]
    assert expr["type"] == "Literal", f"Expected Literal, got {expr['type']}"
    assert expr["value"] == "hello", f"Expected 'hello', got {expr['value']}"


# [pr_diff] fail_to_pass
def test_parens_identifier_after_comment():
    """Template expression {(/**/ x)} must parse to an Identifier node."""
    ast = _parse_template("{(/**/ x)}")
    expr = ast["fragment"]["nodes"][0]["expression"]
    assert expr["type"] == "Identifier", f"Expected Identifier, got {expr['type']}"
    assert expr["name"] == "x", f"Expected name 'x', got {expr.get('name')}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and fixed
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's lint (eslint + prettier) passes after build (pass_to_pass)."""
    # Build first (required for prettier-plugin-svelte)
    r1 = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r1.returncode == 0, f"Build failed:\n{r1.stderr[-500:]}"

    r2 = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r2.returncode == 0, f"Lint failed:\n{r2.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tests():
    """Repo's test suite passes, excluding browser tests (pass_to_pass)."""
    # Exclude browser tests that require Playwright/Chromium
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--exclude", "**/tests/runtime-browser/**"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_simple_expressions_parse():
    """Basic template expressions without problematic parens still parse."""
    cases = [
        ("{42}", "Literal", {"value": 42}),
        ("{(42)}", "Literal", {"value": 42}),
        ('{"hello"}', "Literal", {"value": "hello"}),
        ("{true}", "Literal", {"value": True}),
    ]
    for template, expected_type, expected_props in cases:
        ast = _parse_template(template)
        expr = ast["fragment"]["nodes"][0]["expression"]
        assert expr["type"] == expected_type, (
            f"Template {template}: expected {expected_type}, got {expr['type']}"
        )
        for key, val in expected_props.items():
            assert expr[key] == val, (
                f"Template {template}: expected {key}={val}, got {expr[key]}"
            )
