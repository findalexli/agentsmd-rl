"""
Task: react-exhaustive-deps-flow-type-assertion
Repo: facebook/react @ 22a20e1f2f557b99115d82b639ff5a32b6453cb6
PR:   35691

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: React is a Node.js/TypeScript project. Behavioral tests use
subprocess.run() to invoke yarn/jest. Structural tests read source files
directly — AST-only because the ESLint rule runs under Node, not Python.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
PLUGIN_DIR = f"{REPO}/packages/eslint-plugin-react-hooks"
SOURCE_FILE = Path(f"{PLUGIN_DIR}/src/rules/ExhaustiveDeps.ts")
TEST_FILE = Path(
    f"{PLUGIN_DIR}/__tests__/ESLintRuleExhaustiveDeps-test.js"
)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — TypeScript compilation
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_typescript_compiles():
    """ExhaustiveDeps.ts must pass TypeScript compilation with no errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "src/rules/ExhaustiveDeps.ts"],
        cwd=PLUGIN_DIR,
        capture_output=True,
        timeout=60,
    )
    out = r.stdout.decode() + r.stderr.decode()
    errors = [l for l in out.splitlines() if "error TS" in l]
    assert not errors, (
        "TypeScript errors in ExhaustiveDeps.ts:\n" + "\n".join(errors)
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_generic_type_annotation_check_added():
    """ExhaustiveDeps.ts must skip deps whose parent node is GenericTypeAnnotation.

    Bug: Flow type aliases used in type assertions (e.g. `value as Type<Alias>`)
    are incorrectly flagged as missing hook dependencies.
    Fix: when dependencyNode.parent?.type === 'GenericTypeAnnotation', skip it.

    Fails on base commit (check absent), passes after fix.
    # AST-only because: the ESLint rule is TypeScript/Node — can't import into Python
    """
    src = SOURCE_FILE.read_text()
    assert "GenericTypeAnnotation" in src, (
        "GenericTypeAnnotation check missing from ExhaustiveDeps.ts — "
        "Flow type aliases in type assertions will be incorrectly flagged as deps"
    )
    # Confirm the check is near the TypeParameter handling (not an unrelated occurrence)
    idx = src.index("GenericTypeAnnotation")
    surrounding = src[max(0, idx - 300) : idx + 100]
    assert "TypeParameter" in surrounding or "parent" in surrounding, (
        "GenericTypeAnnotation occurrence not near the TypeParameter/dependency check"
    )


# [pr_diff] fail_to_pass
def test_flow_type_assertion_test_case_added():
    """A new valid test case covering Flow type aliases in type assertions must exist.

    The PR adds a testsFlow.valid case where ColumnKey/Item are Flow types used in
    `as TextColumn<ColumnKey, Item>` — they must NOT be flagged as missing deps.

    Fails on base commit (case absent), passes after fix.
    # AST-only because: test file is JavaScript running under Jest/Node
    """
    content = TEST_FILE.read_text()
    # The new test case introduces TextColumn as a Flow generic type assertion
    assert "TextColumn" in content, (
        "New Flow type assertion test case (using TextColumn<ColumnKey, Item>) "
        "not found in ESLintRuleExhaustiveDeps-test.js"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_exhaustive_deps_suite_passes():
    """Full ESLintRuleExhaustiveDeps jest test suite must pass with no failures."""
    r = subprocess.run(
        ["yarn", "test", "ESLintRuleExhaustiveDeps", "--no-watchman"],
        cwd=PLUGIN_DIR,
        capture_output=True,
        timeout=300,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"ESLint ExhaustiveDeps test suite failed:\n{output[-4000:]}"
    )


# [static] pass_to_pass
def test_not_stub():
    """ExhaustiveDeps.ts must retain TypeParameter handling and be non-trivial."""
    src = SOURCE_FILE.read_text()
    # Original TypeParameter ignore check must still be present
    assert "TypeParameter" in src, (
        "TypeParameter check removed from ExhaustiveDeps.ts"
    )
    # continue statement must be present (skipping type params)
    assert src.count("continue") >= 1, (
        "continue statement(s) removed from ExhaustiveDeps.ts"
    )
    # File must be substantial (not gutted)
    code_lines = [l for l in src.splitlines() if l.strip()]
    assert len(code_lines) > 100, (
        f"ExhaustiveDeps.ts is suspiciously short ({len(code_lines)} lines)"
    )
