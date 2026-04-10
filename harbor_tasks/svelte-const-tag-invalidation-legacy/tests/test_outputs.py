"""
Task: svelte-const-tag-invalidation-legacy
Repo: svelte @ ff3495dc05bbdd81a225ba43446d82171b4413e3
PR:   18041

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import os
import tempfile
import shutil

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


def _create_and_run_test(sample_name, main_svelte_content, config_js_content, timeout=120):
    """Create test samples in the repo samples dir and run the test."""
    # Create sample in the actual samples directory where vitest looks
    sample_dir = Path(SAMPLES) / sample_name
    sample_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Write the test files
        (sample_dir / "main.svelte").write_text(main_svelte_content)
        (sample_dir / "_config.js").write_text(config_js_content)

        # Run vitest with filter
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
    finally:
        # Cleanup: remove the test sample we created
        shutil.rmtree(sample_dir, ignore_errors=True)


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
    # Copy existing const-tag sample and modify to test cross-const dependency
    sample_dir = Path(SAMPLES) / "const-tag-cross-ref-arrow"

    main_content = '''<svelte:options runes={false} />

<script>
	let message = 'hello';
</script>

<input bind:value={message} />

{#if true}
	{@const m1 = message}
	{@const m2 = (() => m1)()}

	<p>{m1}</p>
	<p>{m2}</p>
{/if}
'''

    config_content = '''import { flushSync } from 'svelte';
import { test } from '../../test';

export default test({
	html: `
		<input>
		<p>hello</p>
		<p>hello</p>
	`,

	ssrHtml: `
		<input value="hello">
		<p>hello</p>
		<p>hello</p>
	`,

	async test({ assert, target }) {
		const [input] = target.querySelectorAll('input');

		flushSync(() => {
			input.value = 'goodbye';
			input.dispatchEvent(new InputEvent('input', { bubbles: true }));
		});

		assert.htmlEqual(
			target.innerHTML,
			`
				<input>
				<p>goodbye</p>
				<p>goodbye</p>
			`
		);
	}
});
'''

    r = _create_and_run_test("const-tag-cross-ref-arrow", main_content, config_content)
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"@const arrow invalidation test failed:\n{out[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_const_tag_uppercase_invalidation():
    """@const chain with string transform via arrow IIFE must update reactively."""
    main_content = '''<svelte:options runes={false} />

<script>
	let word = 'abc';
</script>

<input bind:value={word} />

{#if true}
	{@const w = word}
	{@const upper = (() => w.toUpperCase())()}

	<p>{w}</p>
	<p>{upper}</p>
{/if}
'''

    config_content = '''import { flushSync } from 'svelte';
import { test } from '../../test';

export default test({
	html: `
		<input>
		<p>abc</p>
		<p>ABC</p>
	`,

	ssrHtml: `
		<input value="abc">
		<p>abc</p>
		<p>ABC</p>
	`,

	async test({ assert, target }) {
		const [input] = target.querySelectorAll('input');

		flushSync(() => {
			input.value = 'xyz';
			input.dispatchEvent(new InputEvent('input', { bubbles: true }));
		});

		assert.htmlEqual(
			target.innerHTML,
			`
				<input>
				<p>xyz</p>
				<p>XYZ</p>
			`
		);
	}
});
'''

    r = _create_and_run_test("const-tag-cross-ref-transform", main_content, config_content)
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


# [repo_tests] pass_to_pass
def test_const_tag_shadow():
    """Existing const-tag-shadow upstream test still passes (scope handling)."""
    r = _run_vitest_sample("const-tag-shadow")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing const-tag-shadow test failed:\n{out[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_const_tag_each_arrow():
    """Existing const-tag-each-arrow upstream test still passes (arrow functions in @const)."""
    r = _run_vitest_sample("const-tag-each-arrow")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing const-tag-each-arrow test failed:\n{out[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_const_tag_invalidate():
    """Existing const-tag-invalidate upstream test still passes (reactivity)."""
    r = _run_vitest_sample("const-tag-invalidate")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing const-tag-invalidate test failed:\n{out[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_const_tag_hoisting():
    """Existing const-tag-hoisting upstream test still passes."""
    r = _run_vitest_sample("const-tag-hoisting")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing const-tag-hoisting test failed:\n{out[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_const_tag_if_else():
    """Existing const-tag-if-else upstream test still passes (control flow)."""
    r = _run_vitest_sample("const-tag-if-else")
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing const-tag-if-else test failed:\n{out[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_compiler_errors():
    """Repo's compiler-errors test suite passes (CI gate)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "packages/svelte/tests/compiler-errors/test.ts",
         "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Compiler errors test suite failed:\n{out[-2000:]}"


# [repo_tests] pass_to_pass
def test_validator():
    """Repo's validator test suite passes (CI gate)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "packages/svelte/tests/validator/test.ts",
         "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Validator test suite failed:\n{out[-2000:]}"


# [repo_tests] pass_to_pass
def test_eslint_function_js():
    """ESLint passes on the modified function.js file."""
    r = subprocess.run(
        ["pnpm", "exec", "eslint", f"{REPO}/{TARGET}"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"ESLint failed on function.js:\n{out[-1000:]}"


# [repo_tests] pass_to_pass
def test_syntax_check_node():
    """Modified function.js passes Node.js syntax check."""
    r = subprocess.run(
        ["node", "--check", f"{REPO}/{TARGET}"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Node.js syntax check failed:\n{r.stderr.decode()[-500:]}"


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
