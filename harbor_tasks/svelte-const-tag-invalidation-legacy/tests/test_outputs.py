"""
Task: svelte-const-tag-invalidation-legacy
Repo: svelte @ ff3495dc05bbdd81a225ba43446d82171b4413e3
PR:   18041

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/svelte"
TARGET = "packages/svelte/src/compiler/phases/2-analyze/visitors/shared/function.js"
SAMPLES = f"{REPO}/packages/svelte/tests/runtime-legacy/samples"


def _run_vitest_sample(sample_name, timeout=120):
    """Run a single Svelte runtime-legacy test sample via vitest."""
    r = subprocess.run(
        ["npx", "vitest", "run",
         "packages/svelte/tests/runtime-legacy/test.ts",
         "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        timeout=timeout,
        env={
            **dict(__import__("os").environ),
            "FILTER": sample_name,
        },
    )
    return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified function.js must parse without errors."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/{TARGET}"],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in function.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_const_tag_arrow_invalidation():
    """@const depending on another @const via arrow function IIFE must update reactively."""
    sample_dir = Path(SAMPLES) / "const-tag-cross-ref-arrow"
    sample_dir.mkdir(exist_ok=True)

    (sample_dir / "main.svelte").write_text(
        '<svelte:options runes={false} />\n'
        '\n'
        '<script>\n'
        "\tlet message = 'hello';\n"
        '</script>\n'
        '\n'
        '<input bind:value={message} />\n'
        '\n'
        '{#if true}\n'
        '\t{@const m1 = message}\n'
        '\t{@const m2 = (() => m1)()}\n'
        '\n'
        '\t<p>{m1}</p>\n'
        '\t<p>{m2}</p>\n'
        '{/if}\n'
    )

    (sample_dir / "_config.js").write_text(
        "import { flushSync } from 'svelte';\n"
        "import { test } from '../../test';\n"
        '\n'
        'export default test({\n'
        '\thtml: `\n'
        '\t\t<input>\n'
        '\t\t<p>hello</p>\n'
        '\t\t<p>hello</p>\n'
        '\t`,\n'
        '\n'
        '\tssrHtml: `\n'
        '\t\t<input value="hello">\n'
        '\t\t<p>hello</p>\n'
        '\t\t<p>hello</p>\n'
        '\t`,\n'
        '\n'
        '\tasync test({ assert, target }) {\n'
        "\t\tconst [input] = target.querySelectorAll('input');\n"
        '\n'
        '\t\tflushSync(() => {\n'
        "\t\t\tinput.value = 'goodbye';\n"
        "\t\t\tinput.dispatchEvent(new InputEvent('input', { bubbles: true }));\n"
        '\t\t});\n'
        '\n'
        '\t\tassert.htmlEqual(\n'
        '\t\t\ttarget.innerHTML,\n'
        '\t\t\t`\n'
        '\t\t\t\t<input>\n'
        '\t\t\t\t<p>goodbye</p>\n'
        '\t\t\t\t<p>goodbye</p>\n'
        '\t\t\t`\n'
        '\t\t);\n'
        '\t}\n'
        '});\n'
    )

    r = _run_vitest_sample("const-tag-cross-ref-arrow")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"@const arrow invalidation test failed:\n{out[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_const_tag_uppercase_invalidation():
    """@const chain with string transform via arrow IIFE must update reactively."""
    sample_dir = Path(SAMPLES) / "const-tag-cross-ref-transform"
    sample_dir.mkdir(exist_ok=True)

    (sample_dir / "main.svelte").write_text(
        '<svelte:options runes={false} />\n'
        '\n'
        '<script>\n'
        "\tlet word = 'abc';\n"
        '</script>\n'
        '\n'
        '<input bind:value={word} />\n'
        '\n'
        '{#if true}\n'
        '\t{@const w = word}\n'
        '\t{@const upper = (() => w.toUpperCase())()}\n'
        '\n'
        '\t<p>{w}</p>\n'
        '\t<p>{upper}</p>\n'
        '{/if}\n'
    )

    (sample_dir / "_config.js").write_text(
        "import { flushSync } from 'svelte';\n"
        "import { test } from '../../test';\n"
        '\n'
        'export default test({\n'
        '\thtml: `\n'
        '\t\t<input>\n'
        '\t\t<p>abc</p>\n'
        '\t\t<p>ABC</p>\n'
        '\t`,\n'
        '\n'
        '\tssrHtml: `\n'
        '\t\t<input value="abc">\n'
        '\t\t<p>abc</p>\n'
        '\t\t<p>ABC</p>\n'
        '\t`,\n'
        '\n'
        '\tasync test({ assert, target }) {\n'
        "\t\tconst [input] = target.querySelectorAll('input');\n"
        '\n'
        '\t\tflushSync(() => {\n'
        "\t\t\tinput.value = 'xyz';\n"
        "\t\t\tinput.dispatchEvent(new InputEvent('input', { bubbles: true }));\n"
        '\t\t});\n'
        '\n'
        '\t\tassert.htmlEqual(\n'
        '\t\t\ttarget.innerHTML,\n'
        '\t\t\t`\n'
        '\t\t\t\t<input>\n'
        '\t\t\t\t<p>xyz</p>\n'
        '\t\t\t\t<p>XYZ</p>\n'
        '\t\t\t`\n'
        '\t\t);\n'
        '\t}\n'
        '});\n'
    )

    r = _run_vitest_sample("const-tag-cross-ref-transform")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"@const transform invalidation test failed:\n{out[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_const_tag_tests():
    """Existing const-tag-dependencies upstream test still passes."""
    r = _run_vitest_sample("const-tag-dependencies")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing const-tag-dependencies test failed:\n{out[-2000:]}"
    )


# [static] pass_to_pass
def test_not_stub():
    """visit_function in function.js has real scope-comparison logic."""
    src = Path(f"{REPO}/{TARGET}").read_text()

    # Must export visit_function
    assert "export function visit_function" in src, "visit_function not exported"

    # Must iterate scope references and add to expression.references
    assert "expression.references.add" in src, "Missing expression.references.add"

    # Must have a conditional comparing binding scope to current scope
    assert "binding" in src and "scope" in src, "Missing binding/scope logic"

    # Must call context.next with updated state
    assert "context.next" in src, "Missing context.next call"

    # Must have at least 5 non-empty lines in the function body (not a stub)
    lines = [l.strip() for l in src.splitlines() if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 8, f"Function body too short ({len(lines)} lines), likely a stub"
