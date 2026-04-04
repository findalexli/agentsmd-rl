"""
Task: react-compiler-ref-validation-immutable-capture
Repo: facebook/react @ c0060cf2a695d719152c939cfc3cced8f7da3e52
PR:   35893

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
COMPILER = "/workspace/react/compiler"
VALIDATION_FILE = (
    "/workspace/react/compiler/packages/babel-plugin-react-compiler"
    "/src/Validation/ValidateNoRefAccessInRender.ts"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typecheck():
    """ValidateNoRefAccessInRender.ts must typecheck without errors."""
    # AST-only because: TypeScript source cannot be executed directly in Python
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p",
         "packages/babel-plugin-react-compiler"],
        cwd=COMPILER,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_panresponder_no_false_positive():
    """Refs passed to PanResponder.create (ImmutableCapture+Freeze) must not
    produce false positive ref-access errors.

    On the base commit, the compiler uniformly applies validateNoRefPassedToFunction
    to all operands, producing a false positive. The fix uses per-effect validation
    so that ImmutableCapture operands with a co-existing Freeze are handled safely.

    The fixture file and PanResponder type definition are pre-installed in the
    Dockerfile as test infrastructure.
    """
    # Generate the fixture output (suppress Node 22 punycode deprecation warning)
    env = {**__import__("os").environ, "NODE_OPTIONS": "--no-deprecation"}
    r = subprocess.run(
        ["yarn", "snap", "-p", "panresponder-ref-in-callback", "-u"],
        cwd=COMPILER,
        capture_output=True,
        timeout=120,
        env=env,
    )
    combined = r.stdout.decode() + r.stderr.decode()

    # Read the generated expect.md
    expect_path = Path(COMPILER) / (
        "packages/babel-plugin-react-compiler/src/__tests__"
        "/fixtures/compiler/panresponder-ref-in-callback.expect.md"
    )
    assert expect_path.exists(), (
        f"Fixture expect.md was not generated. Snap output:\n{combined}"
    )
    content = expect_path.read_text()

    # The fixture must compile WITHOUT ref-access errors
    assert "InvalidReact" not in content, (
        f"False positive: ref in PanResponder.create callback should not error.\n"
        f"Got InvalidReact in output:\n{content[:500]}"
    )
    assert "Cannot access ref" not in content, (
        f"False positive ref-access error in panresponder fixture:\n{content[:500]}"
    )
    # Must have compiled code (not just an error block)
    assert "## Code" in content, (
        f"Fixture did not produce compiled output:\n{content[:500]}"
    )


# [pr_diff] fail_to_pass
def test_effects_branch_for_non_hook_calls():
    """Non-hook calls with known effects must use per-effect validation.

    The fix adds a new else-if branch for (hookKind == null && instr.effects != null)
    that iterates over effects to determine per-operand validation. On the base commit
    this branch does not exist and all operands are validated uniformly.
    """
    # AST-only because: TypeScript source, cannot be imported/executed in Python
    src = Path(VALIDATION_FILE).read_text()

    # The new branch must guard on hookKind being null and effects being present
    assert "hookKind == null" in src and "instr.effects" in src, (
        "Missing effects-based validation branch for non-hook calls with known effects"
    )
    # Must iterate over individual effects (not operands)
    assert "for (const effect of instr.effects)" in src or \
           "for (const effect of instr.effects!)" in src, (
        "Missing iteration over instr.effects in effects-based branch"
    )


# [pr_diff] fail_to_pass
def test_immutable_capture_freeze_distinction():
    """ImmutableCapture with co-existing Freeze must be treated differently
    from ImmutableCapture alone.

    ImmutableCapture can come from:
      1. Known signature with Freeze (safe — e.g. PanResponder.create)
      2. Downgraded defaults without Freeze (unsafe — unknown function)

    The fix must check for a co-existing Freeze effect on the same operand.
    """
    # AST-only because: TypeScript source, cannot be imported/executed in Python
    src = Path(VALIDATION_FILE).read_text()

    # Must handle ImmutableCapture as a distinct case
    assert "'ImmutableCapture'" in src, (
        "Missing 'ImmutableCapture' case in effect kind handling"
    )
    # Must check for Freeze on the same operand to distinguish safe vs unsafe
    assert "Freeze" in src and "identifier.id" in src, (
        "Missing Freeze co-existence check for ImmutableCapture operands"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_mutate_ref_fixture_still_errors():
    """Mutating a ref arg during render must still produce a validation error.

    The fix must not suppress errors for functions with Mutate effects on refs.
    The existing error.validate-mutate-ref-arg-in-render fixture exercises this.
    We regenerate the output (with -u) and verify it contains the expected error,
    rather than relying on exact snap comparison which is fragile to Node version.
    """
    env = {**__import__("os").environ, "NODE_OPTIONS": "--no-deprecation"}
    r = subprocess.run(
        ["yarn", "snap", "-p", "error.validate-mutate-ref-arg-in-render", "-u"],
        cwd=COMPILER,
        capture_output=True,
        timeout=120,
        env=env,
    )
    expect_path = Path(COMPILER) / (
        "packages/babel-plugin-react-compiler/src/__tests__"
        "/fixtures/compiler/error.validate-mutate-ref-arg-in-render.expect.md"
    )
    assert expect_path.exists(), "Fixture expect.md not found"
    content = expect_path.read_text()

    # Must contain a ref-access error (not silently pass)
    assert "## Error" in content, (
        f"Regression: mutate-ref fixture should produce an error block:\n{content[:500]}"
    )
    assert "Cannot access ref" in content or "ref" in content.lower(), (
        f"Regression: mutate-ref fixture should report ref-access error:\n{content[:500]}"
    )
    # Must NOT have compiled code (it should be an error-only fixture)
    assert "## Code" not in content, (
        f"Regression: mutate-ref fixture should NOT compile successfully:\n{content[:500]}"
    )


# [static] pass_to_pass
def test_validation_functions_present():
    """Both ref validation functions must be present and called in the
    validation pass. This is an anti-stub check — the fix must not remove
    or break existing validation dispatchers."""
    # AST-only because: TypeScript source, cannot be imported/executed in Python
    src = Path(VALIDATION_FILE).read_text()

    # Both validation dispatchers must be present and called
    assert "validateNoDirectRefValueAccess" in src, (
        "Missing validateNoDirectRefValueAccess call"
    )
    assert "validateNoRefPassedToFunction" in src, (
        "Missing validateNoRefPassedToFunction call"
    )
    assert "validateNoRefValueAccess" in src, (
        "Missing validateNoRefValueAccess call"
    )
