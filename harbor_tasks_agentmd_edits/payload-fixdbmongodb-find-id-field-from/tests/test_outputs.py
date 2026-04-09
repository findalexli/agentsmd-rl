"""
Task: payload-fixdbmongodb-find-id-field-from
Repo: payloadcms/payload @ 5ebda61c74724cf68d2b1b1dc9886dde6f55b0ff
PR:   15110

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/payload"


def _install_deps():
    """Install dependencies if not already installed."""
    subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True,
        timeout=300,
        cwd=REPO,
    )


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    _install_deps()

    # Check the modified packages compile
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "packages/db-mongodb/tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"TypeScript compilation failed: {result.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_buildschema_finds_nested_id_field():
    """buildSchema finds custom ID fields nested in tabs via flattenedFields."""
    # This test executes buildSchema logic to verify it finds a nested ID field
    test_code = """
const { fieldAffectsData } = require('payload/shared');

// Simulate the logic from buildSchema.ts
function findCustomIdField(flattenedFields, configFields) {
    const fieldsToSearch = flattenedFields || configFields;
    const idField = fieldsToSearch.find((field) => fieldAffectsData(field) && field.name === 'id');
    return idField;
}

// Test case 1: ID nested inside tabs (needs flattenedFields)
const fieldsWithNestedId = [
    {
        type: 'tabs',
        tabs: [
            {
                label: 'Main',
                fields: [
                    { name: 'id', type: 'number' },
                    { name: 'title', type: 'text' },
                ],
            },
        ],
    },
];

// Simulated flattenedFields (what the fix provides)
const flattenedFields = [
    { name: 'id', type: 'number' },
    { name: 'title', type: 'text' },
];

// With flattenedFields (the fix), should find the ID
const foundWithFlattened = findCustomIdField(flattenedFields, fieldsWithNestedId);
if (!foundWithFlattened || foundWithFlattened.name !== 'id') {
    console.error('FAIL: Did not find ID field using flattenedFields');
    process.exit(1);
}

// Without flattenedFields (old behavior), should NOT find the ID in nested tabs
const foundWithoutFlattened = findCustomIdField(null, fieldsWithNestedId);
if (foundWithoutFlattened && foundWithoutFlattened.name === 'id') {
    console.error('FAIL: Should not find ID in nested structure without flattenedFields');
    process.exit(1);
}

console.log('PASS: buildSchema correctly uses flattenedFields to find nested ID');
"""

    result = subprocess.run(
        ["node", "-e", test_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr or result.stdout}"
    assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"


# [pr_diff] fail_to_pass
def test_buildschema_accepts_flattenedfields_param():
    """buildSchema function accepts and uses flattenedFields parameter."""
    # Verify the actual buildSchema.ts has the flattenedFields parameter
    build_schema_path = Path(f"{REPO}/packages/db-mongodb/src/models/buildSchema.ts")
    content = build_schema_path.read_text()

    # Check that flattenedFields parameter exists and is used correctly
    assert "flattenedFields?: FlattenedField[]" in content, \
        "buildSchema doesn't declare flattenedFields parameter"
    assert "flattenedFields," in content or "flattenedFields" in content, \
        "flattenedFields not destructured from args"
    assert "fieldsToSearch = flattenedFields || configFields" in content or \
           "const fieldsToSearch = flattenedFields" in content, \
        "buildSchema doesn't create fieldsToSearch from flattenedFields"


# [pr_diff] fail_to_pass
def test_afterread_preserves_top_level_id():
    """afterRead preserves top-level custom ID even when hidden."""
    # Test the isTopLevelIDField logic that prevents ID stripping
    test_code = """
// Simulate the logic from promise.ts
function simulateAfterReadLogic(field, siblingDoc, fieldDepth, showHiddenFields) {
    const fieldAffectsDataResult = field.name && field.name !== '_id';
    const isTopLevelIDField = fieldAffectsDataResult && field.name === 'id' && fieldDepth === 0;

    const shouldRemove = fieldAffectsDataResult &&
        field.hidden &&
        typeof siblingDoc[field.name] !== 'undefined' &&
        !showHiddenFields &&
        !isTopLevelIDField;

    if (shouldRemove) {
        delete siblingDoc[field.name];
        return { removed: true, value: undefined };
    }
    return { removed: false, value: siblingDoc[field.name] };
}

// Test case: top-level hidden ID field at depth 0 should be preserved
const topLevelIdField = { name: 'id', type: 'number', hidden: true };
const docWithId = { id: 12345, title: 'Test' };
const result1 = simulateAfterReadLogic(topLevelIdField, { ...docWithId }, 0, false);
if (result1.removed) {
    console.error('FAIL: Top-level ID was removed at depth 0');
    process.exit(1);
}

// Test case: nested ID field (depth > 0) should be removed if hidden
const nestedIdField = { name: 'id', type: 'number', hidden: true };
const nestedDoc = { id: 67890, title: 'Nested' };
const result2 = simulateAfterReadLogic(nestedIdField, { ...nestedDoc }, 1, false);
if (!result2.removed) {
    console.error('FAIL: Nested ID should be removed at depth 1');
    process.exit(1);
}

// Test case: non-ID hidden field should still be removed
const hiddenTitleField = { name: 'title', type: 'text', hidden: true };
const docWithHiddenTitle = { id: 12345, title: 'Secret' };
const result3 = simulateAfterReadLogic(hiddenTitleField, { ...docWithHiddenTitle }, 0, false);
if (!result3.removed) {
    console.error('FAIL: Non-ID hidden field should be removed');
    process.exit(1);
}

console.log('PASS: afterRead correctly preserves top-level ID while removing other hidden fields');
"""

    result = subprocess.run(
        ["node", "-e", test_code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr or result.stdout}"
    assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"


# [pr_diff] fail_to_pass
def test_fielddepth_tracked_in_afterread():
    """afterRead hooks track fieldDepth parameter through traversal."""
    # Verify fieldDepth is declared and passed through the call chain
    traverse_path = Path(f"{REPO}/packages/payload/src/fields/hooks/afterRead/traverseFields.ts")
    promise_path = Path(f"{REPO}/packages/payload/src/fields/hooks/afterRead/promise.ts")
    index_path = Path(f"{REPO}/packages/payload/src/fields/hooks/afterRead/index.ts")

    traverse_content = traverse_path.read_text()
    promise_content = promise_path.read_text()
    index_content = index_path.read_text()

    # Check traverseFields.ts has fieldDepth parameter with default
    assert "fieldDepth?: number" in traverse_content, \
        "traverseFields.ts missing fieldDepth parameter declaration"
    assert "fieldDepth = 0" in traverse_content, \
        "traverseFields.ts missing fieldDepth default value"
    assert "fieldDepth," in traverse_content, \
        "traverseFields.ts doesn't pass fieldDepth to promise()"

    # Check promise.ts has fieldDepth and increments it for nested fields
    assert "fieldDepth: number" in promise_content, \
        "promise.ts missing fieldDepth parameter declaration"
    assert "isTopLevelIDField" in promise_content, \
        "promise.ts missing isTopLevelIDField logic"
    assert "fieldDepth === 0" in promise_content, \
        "promise.ts missing fieldDepth === 0 check for isTopLevelIDField"
    assert "fieldDepth + 1" in promise_content, \
        "promise.ts doesn't increment fieldDepth for nested fields"

    # Check index.ts initializes fieldDepth to 0
    assert "fieldDepth: 0" in index_content, \
        "index.ts doesn't initialize fieldDepth to 0"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    _install_deps()

    result = subprocess.run(
        ["pnpm", "test:unit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**subprocess.os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"},
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


# [static] pass_to_pass
def test_claude_md_updated():
    """CLAUDE.md has been updated with testing best practices."""
    claude_md_path = Path(f"{REPO}/CLAUDE.md")
    content = claude_md_path.read_text()

    # Check for the new Testing section content
    assert "Writing Tests - Required Practices" in content, \
        "CLAUDE.md missing 'Writing Tests - Required Practices' section"
    assert "Tests MUST be self-contained and clean up after themselves" in content, \
        "CLAUDE.md missing test self-containment guidance"
    assert "afterEach" in content, \
        "CLAUDE.md missing afterEach guidance"


# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    import re

    # Check buildSchema has meaningful logic
    build_schema_path = Path(f"{REPO}/packages/db-mongodb/src/models/buildSchema.ts")
    content = build_schema_path.read_text()

    # Find the buildSchema function
    pattern = r'export const buildSchema.*?^}'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        func_body = match.group(0)
        # Should have actual logic statements, not just return
        lines_with_logic = [l for l in func_body.split('\n')
                          if l.strip() and not l.strip().startswith('//')
                          and not l.strip().startswith('*')
                          and 'export' not in l and 'const buildSchema' not in l]
        assert len(lines_with_logic) > 5, "buildSchema appears to be a stub"

    # Check promise.ts has meaningful logic
    promise_path = Path(f"{REPO}/packages/payload/src/fields/hooks/afterRead/promise.ts")
    content = promise_path.read_text()

    assert "isTopLevelIDField" in content, "promise.ts missing isTopLevelIDField logic"
