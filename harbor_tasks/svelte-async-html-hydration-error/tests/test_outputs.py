"""
Task: svelte-async-html-hydration-error
Repo: svelte @ 54ba176d2c9068f2e6df9249764bb7766ec1b69d
PR:   17999

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/svelte"

FRAGMENT_JS = (
    "packages/svelte/src/compiler/phases/3-transform/"
    "client/visitors/shared/fragment.js"
)


def _compile_component(source, experimental_async=False):
    """Compile a Svelte component and return the generated client JS code."""
    options = {"generate": "client"}
    if experimental_async:
        options["experimental"] = {"async": True}
    script = (
        "import { compile } from "
        "'/workspace/svelte/packages/svelte/src/compiler/index.js';\n"
        f"const result = compile({json.dumps(source)}, {json.dumps(options)});\n"
        "console.log(result.js.code);\n"
    )
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to compile:\n{r.stderr}"
    return r.stdout


def _has_controlled_html(code):
    """Check if any $.html() call in compiled code uses controlled mode.

    When is_controlled=true, the HtmlTag visitor passes `true` as the 3rd arg
    to $.html(). For simple components (no SVG/MathML/ignore), this is the only
    source of `true` in a $.html() call.
    """
    for line in code.split("\n"):
        if "$.html(" in line and ", true" in line:
            return True
    return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified fragment.js loads as an ES module without errors."""
    script = (
        f"await import('/workspace/svelte/{FRAGMENT_JS}');\n"
        "console.log('OK');\n"
    )
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Module load failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_async_html_not_controlled():
    """Async {@html await ...} as sole element child must not be compiled as controlled."""
    source = (
        "<script>\n"
        "function getValue() { return Promise.resolve('<p>hello</p>'); }\n"
        "</script>\n"
        "<div>{@html await getValue()}</div>"
    )
    code = _compile_component(source, experimental_async=True)
    assert "$.html(" in code, "Expected $.html call in compiled output"
    assert not _has_controlled_html(code), (
        "Async {@html} should NOT be compiled as controlled, "
        "but $.html was called with controlled=true"
    )


# [pr_diff] fail_to_pass
def test_async_html_different_parent():
    """Async {@html await ...} in a <section> also must not be controlled."""
    source = (
        "<script>\n"
        "function getContent() { return Promise.resolve('<em>text</em>'); }\n"
        "</script>\n"
        "<section>{@html await getContent()}</section>"
    )
    code = _compile_component(source, experimental_async=True)
    assert "$.html(" in code, "Expected $.html call in compiled output"
    assert not _has_controlled_html(code), (
        "Async {@html} in <section> should NOT be compiled as controlled"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sync_html_still_controlled():
    """Sync {@html ...} as sole element child should still be compiled as controlled."""
    source = (
        "<script>\n"
        "let value = $state('<p>hello</p>');\n"
        "</script>\n"
        "<div>{@html value}</div>"
    )
    code = _compile_component(source)
    assert "$.html(" in code, "Expected $.html call in compiled output"
    assert _has_controlled_html(code), (
        "Sync {@html} as sole child should be compiled as controlled, "
        "but $.html was not called with controlled=true"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repository CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repository typecheck passes (pnpm check)."""
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repository lint passes (pnpm lint after build)."""
    # Build first (lint needs compiled output)
    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    # Run lint
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_compiler_errors_tests():
    """Repository compiler-errors tests pass."""
    r = subprocess.run(
        ["pnpm", "test", "compiler-errors"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Compiler-errors tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_snapshot_tests():
    """Repository snapshot tests pass."""
    r = subprocess.run(
        ["pnpm", "test", "snapshot"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Snapshot tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_hydration_tests():
    """Repository hydration tests pass (relevant to HTML tag handling)."""
    r = subprocess.run(
        ["pnpm", "test", "hydration"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Hydration tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ssr_tests():
    """Repository server-side-rendering tests pass (relevant to async HTML)."""
    r = subprocess.run(
        ["pnpm", "test", "server-side-rendering"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"SSR tests failed:\n{r.stderr[-500:]}"
