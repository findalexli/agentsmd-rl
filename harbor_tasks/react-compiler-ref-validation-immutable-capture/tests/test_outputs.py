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
        ["yarn", "workspace", "babel-plugin-react-compiler", "typecheck"],
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
def test_effects_path_for_non_hook_calls():
    """Non-hook calls with known effects must use the effects-based validation path.

    The fix adds a new else-if branch that activates when hookKind is null and
    instr.effects is populated (i.e., the callee has known aliasing effects).
    On the base commit this branch does not exist, causing all operands to be
    validated uniformly with validateNoRefPassedToFunction.
    """
    # AST-only because: TypeScript source, modifying a live compiler pass
    src = Path(VALIDATION_FILE).read_text()

    # The new branch guards on hookKind == null and non-null effects
    assert "hookKind == null && instr.effects != null" in src, (
        "Missing effects-based validation branch: "
        "'else if (hookKind == null && instr.effects != null)'"
    )

    # The branch must iterate over effects, not operands
    assert "for (const effect of instr.effects)" in src, (
        "Missing iteration over instr.effects in the new branch"
    )


# [pr_diff] fail_to_pass
def test_immutable_capture_freeze_distinction():
    """ImmutableCapture operands that also have a Freeze effect must be treated as safe.

    ImmutableCapture can come from two sources:
      1. A known signature that explicitly freezes the operand (safe — Freeze + ImmutableCapture)
      2. Downgraded defaults when the operand is already frozen (unsafe — ImmutableCapture only)

    The fix distinguishes these by checking whether the same operand also has a Freeze
    effect on the same instruction. On the base commit this check does not exist.
    """
    # AST-only because: TypeScript source, modifying a live compiler pass
    src = Path(VALIDATION_FILE).read_text()

    # ImmutableCapture case must be handled in the switch
    assert "case 'ImmutableCapture'" in src, (
        "Missing 'ImmutableCapture' case in effect kind switch"
    )

    # Must check for a co-existing Freeze effect on the same place
    assert "isFrozen" in src, (
        "Missing 'isFrozen' variable — fix must check for Freeze + ImmutableCapture combination"
    )
    assert "e.kind === 'Freeze'" in src, (
        "Missing Freeze check inside ImmutableCapture handling"
    )
    assert "effect.from.identifier.id" in src, (
        "Missing identifier.id comparison for Freeze/ImmutableCapture same-operand check"
    )


# [pr_diff] fail_to_pass
def test_visited_effects_deduplication():
    """Each (place, validation-kind) pair must only be validated once per instruction.

    The fix introduces a visitedEffects Set to avoid emitting duplicate diagnostics
    when multiple effects reference the same operand. On the base commit this does
    not exist.
    """
    # AST-only because: TypeScript source, modifying a live compiler pass
    src = Path(VALIDATION_FILE).read_text()

    assert "visitedEffects" in src, (
        "Missing 'visitedEffects' deduplication set in effects-based validation branch"
    )
    assert "new Set()" in src or "new Set<string>()" in src, (
        "visitedEffects must be initialized as a Set"
    )
    assert "visitedEffects.has(" in src, (
        "Missing visitedEffects.has() guard to skip duplicate validations"
    )
    assert "visitedEffects.add(" in src, (
        "Missing visitedEffects.add() to record processed (place, validation) pairs"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_mutate_ref_fixture_still_errors():
    """Passing a ref value to a mutating function during render must still produce an error.

    The fix must not suppress errors for functions with Mutate effects on a ref operand.
    The existing error.validate-mutate-ref-arg-in-render fixture exercises this case.
    """
    r = subprocess.run(
        ["yarn", "snap", "-p", "error.validate-mutate-ref-arg-in-render"],
        cwd=COMPILER,
        capture_output=True,
        timeout=120,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Regression: error.validate-mutate-ref-arg-in-render fixture failed:\n{output}"
    )


# [static] pass_to_pass
def test_effect_kind_switch_covers_mutation_cases():
    """The effect kind switch must still route Mutate/Capture effects to ref-passed validation.

    A correct fix must preserve the behavior for mutation effects — they must still
    produce 'ref-passed' validation (i.e., refs must not be passed to mutating functions).
    """
    # AST-only because: TypeScript source, modifying a live compiler pass
    src = Path(VALIDATION_FILE).read_text()

    # Mutate effects → ref-passed
    assert "case 'Mutate'" in src, (
        "Missing 'Mutate' case in effect kind switch — mutation effects must still error"
    )
    # Freeze effects → direct-ref (allow)
    assert "case 'Freeze'" in src, (
        "Missing 'Freeze' case in effect kind switch"
    )
    # Capture effects → ref-passed
    assert "case 'Capture'" in src, (
        "Missing 'Capture' case in effect kind switch"
    )
    # Both validation kinds must be dispatched
    assert "validateNoDirectRefValueAccess" in src, (
        "Missing validateNoDirectRefValueAccess call in effects branch"
    )
    assert "validateNoRefPassedToFunction" in src, (
        "Missing validateNoRefPassedToFunction call in effects branch"
    )
