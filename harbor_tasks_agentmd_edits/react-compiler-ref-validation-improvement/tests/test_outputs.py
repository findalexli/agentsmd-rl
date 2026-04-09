"""
Task: react-compiler-ref-validation-improvement
Repo: facebook/react @ c0060cf2a695d719152c939cfc3cced8f7da3e52
PR:   35893

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This PR improves the React Compiler's ref validation to allow functions like
PanResponder.create() to safely capture refs in callbacks, when they have both
Freeze and ImmutableCapture effects on the same operand.
"""

import subprocess
from pathlib import Path
import json

REPO = "/workspace/react"
COMPILER_DIR = "/workspace/react/compiler"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Run TypeScript compiler on the modified validation file
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck",
         "packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts"],
        cwd=COMPILER_DIR,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_panresponder_compiles_without_ref_error():
    """PanResponder.create() with ref in callback should compile without ref access error.

    Before the fix: The compiler would incorrectly report a ref access error when
    passing a callback that accesses refs to PanResponder.create().

    After the fix: The compiler recognizes that PanResponder.create() freezes
    its arguments and uses ImmutableCapture, so it's safe to access refs
    in the callbacks.
    """
    test_code = '''
// @flow
import {PanResponder, Stringify} from 'shared-runtime';

export default component Playground() {
  const onDragEndRef = useRef(() => {});
  useEffect(() => {
    onDragEndRef.current = () => {
      console.log('drag ended');
    };
  });
  const panResponder = useMemo(
    () =>
      PanResponder.create({
        onPanResponderTerminate: () => {
          onDragEndRef.current();
        },
      }),
    []
  );
  return <Stringify responder={panResponder} />;
}
'''
    # Write test file
    test_path = Path(f"{COMPILER_DIR}/test_panresponder.js")
    test_path.write_text(test_code)

    try:
        # Compile with the compiler
        r = subprocess.run(
            ["yarn", "snap", "compile", str(test_path)],
            cwd=COMPILER_DIR,
            capture_output=True,
            timeout=60,
        )
        output = r.stdout.decode() + r.stderr.decode()

        # Should not have ref access error
        assert "ref" not in output.lower() or "error" not in output.lower(), \
            f"PanResponder should not trigger ref error, but got:\n{output}"
    finally:
        test_path.unlink(missing_ok=True)


def test_mutation_function_still_reports_error():
    """Functions that mutate refs should still report errors."""
    test_code = '''
// @validateRefAccessDuringRender:true
import {mutate} from 'shared-runtime';

function Foo(props, ref) {
  mutate(ref.current);
  return <div>{props.bar}</div>;
}
'''
    test_path = Path(f"{COMPILER_DIR}/test_mutate.js")
    test_path.write_text(test_code)

    try:
        r = subprocess.run(
            ["yarn", "snap", "compile", str(test_path)],
            cwd=COMPILER_DIR,
            capture_output=True,
            timeout=60,
        )
        output = r.stdout.decode() + r.stderr.decode()

        # Should report ref access error
        assert "ref" in output.lower() and "error" in output.lower(), \
            f"Mutating function should report ref error, but got:\n{output}"
    finally:
        test_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_existing_ref_validation_tests_pass():
    """Existing ref validation tests should still pass."""
    # Run the specific ref validation test fixture
    r = subprocess.run(
        ["yarn", "snap", "-p", "error.validate-mutate-ref-arg-in-render", "-t"],
        cwd=COMPILER_DIR,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Existing ref validation tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


def test_validation_has_effect_based_logic():
    """The validation must have effect-based ref validation logic (anti-stub)."""
    src_path = Path(f"{COMPILER_DIR}/packages/babel-plugin-react-compiler/src/Validation/ValidateNoRefAccessInRender.ts")
    src = src_path.read_text()

    # Check for the key new logic: effect-based validation with ImmutableCapture handling
    assert "visitedEffects" in src, "Missing visitedEffects tracking"
    assert "ImmutableCapture" in src, "Missing ImmutableCapture handling"
    assert "isFrozen" in src or "Freeze" in src, "Missing Freeze effect checking"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

def test_claude_md_has_linting_section():
    """CLAUDE.md should include linting and formatting sections (compiler/CLAUDE.md:48-55)."""
    claude_md = Path(f"{COMPILER_DIR}/CLAUDE.md").read_text()

    # Check for the linting and formatting sections added in this PR
    assert "## Linting" in claude_md, "Missing Linting section in CLAUDE.md"
    assert "## Formatting" in claude_md, "Missing Formatting section in CLAUDE.md"
    assert "yarn workspace babel-plugin-react-compiler lint" in claude_md, \
        "Missing lint command in CLAUDE.md"
    assert "yarn prettier-all" in claude_md, \
        "Missing prettier command in CLAUDE.md"
