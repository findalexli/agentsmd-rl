"""
Task: react-compiler-improved-ref-validation-for
Repo: facebook/react @ c0060cf2a695d719152c939cfc3cced8f7da3e52
PR:   35893

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
COMPILER = f"{REPO}/compiler"
VALIDATION_FILE = (
    f"{COMPILER}/packages/babel-plugin-react-compiler/src/Validation/"
    "ValidateNoRefAccessInRender.ts"
)
TYPE_PROVIDER_FILE = (
    f"{COMPILER}/packages/snap/src/sprout/shared-runtime-type-provider.ts"
)
SHARED_RUNTIME_FILE = (
    f"{COMPILER}/packages/snap/src/sprout/shared-runtime.ts"
)
CLAUDE_MD = f"{COMPILER}/CLAUDE.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without errors."""
    for fpath in [VALIDATION_FILE, TYPE_PROVIDER_FILE, SHARED_RUNTIME_FILE]:
        p = Path(fpath)
        assert p.exists(), f"File not found: {fpath}"
        content = p.read_text()
        # Basic: file is non-empty and has no obvious syntax issues
        assert len(content) > 100, f"File suspiciously small: {fpath}"
        # Check balanced braces as a rough syntax check
        assert content.count("{") == content.count("}"), (
            f"Unbalanced braces in {fpath}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_panresponder_fixture_compiles():
    """PanResponder fixture should compile without ref-access error.

    The compiler should recognize that PanResponder.create freezes its
    input, so passing a ref-accessing callback is safe (not called during
    render). On the base commit, this would error with 'ref access in render'.
    """
    fixture = Path(
        f"{COMPILER}/packages/babel-plugin-react-compiler/src/__tests__/"
        "fixtures/compiler/panresponder-ref-in-callback.js"
    )
    assert fixture.exists(), (
        "panresponder-ref-in-callback.js fixture must exist"
    )
    content = fixture.read_text()
    assert "PanResponder" in content, "Fixture must use PanResponder"
    assert "useRef" in content or "Ref" in content, (
        "Fixture must involve refs"
    )

    # Run the fixture through the compiler — it should NOT produce an error
    r = subprocess.run(
        ["yarn", "snap", "-p", "panresponder-ref-in-callback"],
        cwd=COMPILER,
        capture_output=True,
        timeout=120,
    )
    # Check the expect.md was generated and does NOT contain "Error:"
    expect_md = fixture.with_suffix(".expect.md")
    assert expect_md.exists(), "Expected output file must be generated"
    expect_content = expect_md.read_text()
    assert "InvalidReact" not in expect_content, (
        "Fixture should not produce InvalidReact error"
    )
    assert "Cannot access ref" not in expect_content, (
        "Fixture should not produce ref-access error"
    )


# [pr_diff] fail_to_pass
def test_panresponder_type_provider():
    """PanResponder must be registered in the shared-runtime type provider.

    The type provider must define PanResponder.create with Freeze aliasing
    effect so the compiler knows this function freezes its arguments.
    """
    content = Path(TYPE_PROVIDER_FILE).read_text()
    assert "PanResponder" in content, (
        "Type provider must define PanResponder"
    )
    assert "create" in content, (
        "PanResponder must have a 'create' method defined"
    )
    # Verify the aliasing signature includes Freeze effect
    assert "Freeze" in content, "PanResponder.create must have Freeze effect"
    assert "ImmutableCapture" in content, (
        "PanResponder.create must have ImmutableCapture effect"
    )


# [pr_diff] fail_to_pass
def test_panresponder_shared_runtime():
    """PanResponder must be exported from shared-runtime for test fixtures."""
    content = Path(SHARED_RUNTIME_FILE).read_text()
    assert "PanResponder" in content, (
        "shared-runtime.ts must export PanResponder"
    )
    assert "create" in content, (
        "PanResponder must have a create method"
    )


# [pr_diff] fail_to_pass
def test_validation_uses_effects():
    """ValidateNoRefAccessInRender must use instruction effects for non-hook
    function calls instead of the old blanket operand iteration.

    The key behavioral change: when hookKind is null and instr.effects is
    available, iterate over effects to determine per-place validation rather
    than treating all operands uniformly.
    """
    content = Path(VALIDATION_FILE).read_text()
    # The fix introduces an effects-based branch: hookKind == null && instr.effects != null
    assert "instr.effects" in content, (
        "Validation must check instr.effects for non-hook calls"
    )
    # The fix uses visitedEffects to deduplicate
    assert "visitedEffects" in content or "visited" in content.lower(), (
        "Validation must track visited effects to avoid duplicate errors"
    )
    # ImmutableCapture + Freeze check is the key PanResponder logic
    assert "ImmutableCapture" in content, (
        "Validation must handle ImmutableCapture effect kind"
    )


# [pr_diff] fail_to_pass
def test_mutate_ref_still_errors():
    """Mutating a ref arg in render must still produce a compiler error.

    The updated fixture uses mutate() from shared-runtime instead of
    console.log() to ensure that functions with mutation effects on ref
    args are still caught.
    """
    fixture = Path(
        f"{COMPILER}/packages/babel-plugin-react-compiler/src/__tests__/"
        "fixtures/compiler/error.validate-mutate-ref-arg-in-render.js"
    )
    assert fixture.exists(), "Mutate-ref fixture must exist"
    content = fixture.read_text()
    assert "mutate" in content, (
        "Fixture must use mutate() instead of console.log()"
    )

    expect_md = fixture.with_suffix(".expect.md")
    assert expect_md.exists(), "Expected output file must exist"
    expect_content = expect_md.read_text()
    # This fixture SHOULD produce an error
    assert "Error" in expect_content or "error" in expect_content, (
        "Mutating a ref arg in render must still error"
    )
    assert "ref" in expect_content.lower(), (
        "Error should mention ref access"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_snap_tests_pass():
    """A focused subset of snap fixture tests still passes."""
    r = subprocess.run(
        ["yarn", "snap", "-p", "error.validate-mutate-ref-arg-in-render"],
        cwd=COMPILER,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Snap test failed:\n{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — compiler/CLAUDE.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    The CLAUDE.md should include a Linting section with the command to lint
    the compiler source code.
    """
    content = Path(CLAUDE_MD).read_text()
    assert "lint" in content.lower(), (
        "CLAUDE.md should mention linting"
    )
    # Must include the actual lint command
    assert "babel-plugin-react-compiler" in content and "lint" in content, (
        "CLAUDE.md should document the compiler lint command referencing "
        "babel-plugin-react-compiler"
    )


# [config_edit] fail_to_pass

    The CLAUDE.md should include a Formatting section with the command to
    format code (prettier).
    """
    content = Path(CLAUDE_MD).read_text()
    # Check for formatting/prettier documentation
    assert "prettier" in content.lower() or "format" in content.lower(), (
        "CLAUDE.md should mention formatting or prettier"
    )
    # Must include an actionable command
    assert "prettier" in content.lower(), (
        "CLAUDE.md should document the prettier command"
    )
