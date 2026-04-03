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

import re
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
def test_flow_type_assertion_behavioral():
    """ESLint rule must not flag Flow type aliases in type assertions as deps.

    Runs the full ESLintRuleExhaustiveDeps test suite which includes the
    Flow type assertion test case. The test case defines local type aliases
    (ColumnKey, Item) used in `as TextColumn<ColumnKey, Item>` and expects
    no missing-dependency warnings.

    Fails on base commit (test case absent or rule incorrectly flags types).
    # AST-only because: ESLint rule is TypeScript/Node — behavioral via jest
    """
    # Write a targeted jest test that exercises the rule with our specific case
    targeted_test = Path(f"{PLUGIN_DIR}/__tests__/_flow_type_assertion_test.js")
    targeted_test.write_text("""\
const {RuleTester} = require('eslint');
const ReactHooksESLintRule = require('../src/rules/ExhaustiveDeps');

function normalizeIndent(strings, ...values) {
  const result = strings.reduce((acc, str, i) => acc + str + (values[i] || ''), '');
  const lines = result.split('\\n');
  const nonEmptyLines = lines.filter(l => l.trim().length > 0);
  if (nonEmptyLines.length === 0) return result;
  const minIndent = Math.min(...nonEmptyLines.map(l => l.match(/^\\s*/)[0].length));
  return lines.map(l => l.slice(minIndent)).join('\\n').trim() + '\\n';
}

const ruleTester = new RuleTester({
  languageOptions: {
    ecmaVersion: 2024,
    sourceType: 'module',
  },
});

// Test: Flow type aliases in type assertions should NOT be flagged
ruleTester.run('react-hooks/exhaustive-deps', ReactHooksESLintRule, {
  valid: [
    {
      code: normalizeIndent`
        function MyComponent() {
          type ColumnKey = 'id' | 'name';
          type Item = {id: string, name: string};

          const columns = useMemo(
            () => [
              {
                type: 'text',
                key: 'id',
              } as TextColumn<ColumnKey, Item>,
            ],
            [],
          );
        }
      `,
    },
  ],
  invalid: [],
});

console.log('FLOW_TYPE_ASSERTION_TEST_PASSED');
""")
    try:
        r = subprocess.run(
            ["npx", "jest", "--no-watchman", "--no-cache",
             "__tests__/_flow_type_assertion_test.js"],
            cwd=PLUGIN_DIR,
            capture_output=True,
            timeout=120,
        )
        output = r.stdout.decode() + r.stderr.decode()
        assert r.returncode == 0, (
            f"Flow type assertion test failed — rule incorrectly flags "
            f"type aliases in type assertions:\n{output[-3000:]}"
        )
    finally:
        targeted_test.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_flow_type_assertion_test_case_in_suite():
    """A new valid test case covering Flow type aliases in type assertions must exist.

    The fix adds a testsFlow.valid case where ColumnKey/Item are Flow types used in
    `as TextColumn<ColumnKey, Item>` — they must NOT be flagged as missing deps.

    Fails on base commit (case absent), passes after fix.
    # AST-only because: test file is JavaScript running under Jest/Node
    """
    content = TEST_FILE.read_text()
    # Check for the actual test pattern, not just a keyword
    assert "as TextColumn<ColumnKey, Item>" in content or \
           "as TextColumn<ColumnKey," in content, (
        "New Flow type assertion test case (using TextColumn<ColumnKey, Item>) "
        "not found in ESLintRuleExhaustiveDeps-test.js"
    )
    # Verify it's in the valid section of testsFlow (not just a comment)
    flow_valid_idx = content.find("const testsFlow")
    assert flow_valid_idx != -1, "testsFlow section not found in test file"
    text_col_idx = content.find("TextColumn", flow_valid_idx)
    assert text_col_idx != -1, "TextColumn not in testsFlow section"
    # Verify ColumnKey type declaration is part of the test
    assert "type ColumnKey" in content[flow_valid_idx:], (
        "ColumnKey type declaration missing from Flow type assertion test case"
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
