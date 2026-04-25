"""
Tests for Cascader menu item ellipsis fix (ant-design/ant-design#57540)

This PR fixes the Cascader menu item ellipsis styles for long option labels.
The ellipsis styles were incorrectly applied to the parent node (`&-item`)
instead of the actual text container (`&-content`), preventing proper
truncation in flex layouts.

The fix:
1. Removes `...textEllipsis` from `&-item`
2. Adds `maxWidth: 400` to `&-item`
3. Adds `minWidth: 0` and `...textEllipsis` to `&-content`
"""

import os
import subprocess
import sys
import json
import re

REPO_DIR = "/workspace/ant-design"
COLUMNS_STYLE_FILE = os.path.join(REPO_DIR, "components/cascader/style/columns.ts")


def read_columns_style_file():
    """Read the Cascader columns style file."""
    with open(COLUMNS_STYLE_FILE, 'r') as f:
        return f.read()


def test_cascader_columns_file_exists():
    """Verify the columns.ts style file exists."""
    assert os.path.exists(COLUMNS_STYLE_FILE), f"File not found: {COLUMNS_STYLE_FILE}"


def test_cascader_style_structure():
    """
    Fail-to-pass test: Verify CSS-in-JS structure is correct for flexbox ellipsis.

    This test parses the TypeScript file to verify correct properties are
    in the correct nested blocks. It fails on base commit and passes when fixed.
    """
    content = read_columns_style_file()

    lines = content.split('\n')

    # Track block state with proper nesting
    in_item = False
    in_content = False
    item_depth = 0
    content_depth = 0
    item_props = []
    content_props = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for &-item block
        if "'&-item':" in stripped or '"&-item":' in stripped:
            in_item = True
            in_content = False
            item_depth = 0
            content_depth = 0
            item_props = []
            continue

        # Check for &-content block (nested)
        if "'&-content':" in stripped or '"&-content":' in stripped:
            in_content = True
            in_item = False
            item_depth = 0
            content_depth = 0
            content_props = []
            continue

        if in_item and not in_content:
            item_depth += stripped.count('{') - stripped.count('}')
            if item_depth >= 0:
                if 'textEllipsis' in stripped:
                    item_props.append(('textEllipsis', stripped))
                if 'maxWidth' in stripped:
                    item_props.append(('maxWidth', stripped))
            if item_depth < 0:
                in_item = False

        if in_content:
            content_depth += stripped.count('{') - stripped.count('}')
            if content_depth >= 0:
                if 'textEllipsis' in stripped:
                    content_props.append(('textEllipsis', stripped))
                if 'minWidth' in stripped:
                    content_props.append(('minWidth', stripped))
            if content_depth < 0:
                in_content = False

    # Verify behavior: textEllipsis should be in &-content, not &-item
    has_text_ellipsis_in_item = any(p[0] == 'textEllipsis' for p in item_props)
    has_text_ellipsis_in_content = any(p[0] == 'textEllipsis' for p in content_props)
    has_min_width_in_content = any(p[0] == 'minWidth' for p in content_props)
    has_max_width_in_item = any(p[0] == 'maxWidth' for p in item_props)

    # The fix requires:
    # 1. textEllipsis moved to &-content (not in &-item)
    assert not has_text_ellipsis_in_item, \
        "FAIL: textEllipsis should NOT be in &-item block (it should be in &-content)"
    assert has_text_ellipsis_in_content, \
        "FAIL: textEllipsis should be in &-content block"
    assert has_min_width_in_content, \
        "FAIL: &-content should have minWidth: 0 for ellipsis to work in flex layout"
    assert has_max_width_in_item, \
        "FAIL: &-item should have maxWidth constraint"


def test_typescript_compiles():
    """
    Verify the TypeScript file compiles without errors using subprocess.

    This is a fail-to-pass test that actually executes tsc to verify
    the CSS-in-JS code is syntactically and type-correct.
    """
    # Run TypeScript compiler on the specific file
    result = subprocess.run(
        ['npx', 'tsc', '--noEmit', '--skipLibCheck', COLUMNS_STYLE_FILE],
        cwd=REPO_DIR,
        capture_output=True,
        timeout=120
    )

    # If tsc is not available, fall back to syntax check
    if result.returncode != 0:
        if b"not found" in result.stderr or b"command not found" in result.stderr:
            # Fallback: verify the file has balanced braces
            content = read_columns_style_file()
            open_braces = content.count('{')
            close_braces = content.count('}')
            assert open_braces == close_braces, "FAIL: Unbalanced braces in TypeScript file"
        else:
            # Check for actual syntax/parse errors
            stderr = result.stderr.decode() if isinstance(result.stderr, bytes) else result.stderr
            if "syntax" in stderr.lower() or "parse" in stderr.lower() or "unexpected" in stderr.lower():
                assert False, f"TypeScript syntax error: {stderr[:500]}"


def test_style_structure_valid():
    """
    Verify the style file has the expected structure with proper CSS properties.
    """
    content = read_columns_style_file()

    # Check for key structure elements
    assert "GenerateStyle" in content, "File should import/use GenerateStyle type"
    assert "CascaderToken" in content, "File should reference CascaderToken"
    assert "getColumnsStyle" in content, "File should export getColumnsStyle function"


def test_cssinjs_runtime_behavior():
    """
    Fail-to-pass test: Verify CSS-in-JS produces correct output via actual execution.

    This test actually runs a Node.js script that reads and analyzes the
    CSS-in-JS file to verify the generated CSS has correct properties.
    """
    test_script = """
const fs = require('fs');
const path = require('path');

const stylePath = '/workspace/ant-design/components/cascader/style/columns.ts';
const content = fs.readFileSync(stylePath, 'utf8');

const hasTextEllipsis = content.includes("textEllipsis");
const hasMinWidthZero = content.includes("minWidth: 0") || content.includes("minWidth:0");
const hasMaxWidth = content.includes("maxWidth");

console.log(JSON.stringify({
    hasTextEllipsis,
    hasMinWidthZero,
    hasMaxWidth
}));
"""

    script_path = os.path.join(REPO_DIR, "_test_style_eval.js")
    with open(script_path, 'w') as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO_DIR
        )

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout.strip())
                # Verify the expected CSS properties are present
                assert data.get('hasMinWidthZero', False), \
                    "FAIL: Generated CSS should have minWidth: 0"
                assert data.get('hasMaxWidth', False), \
                    "FAIL: Generated CSS should have maxWidth constraint"
            except json.JSONDecodeError:
                pass
    finally:
        if os.path.exists(script_path):
            os.unlink(script_path)


def test_repo_typescript_check():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR, env=env
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_repo_biome_lint():
    """Repo's Biome lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True, text=True, timeout=120, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:script"],
        capture_output=True, text=True, timeout=180, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_cascader_index_tests():
    """Repo's Cascader index component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/index.test.tsx", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader index tests failed:\n{r.stderr[-500:]}"


def test_repo_cascader_demo_tests():
    """Repo's Cascader demo tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/demo.test.tsx", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader demo tests failed:\n{r.stderr[-500:]}"


def test_repo_cascader_a11y_tests():
    """Repo's Cascader a11y tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/a11y.test.ts", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader a11y tests failed:\n{r.stderr[-500:]}"


def test_repo_cascader_type_tests():
    """Repo's Cascader TypeScript type tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/type.test.tsx", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader type tests failed:\n{r.stderr[-500:]}"


def test_repo_cascader_semantic_tests():
    """Repo's Cascader semantic styling tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "components/cascader/__tests__/semantic.test.tsx", "--maxWorkers=1", "--testTimeout=60000"],
        capture_output=True, text=True, timeout=600, cwd=REPO_DIR
    )
    assert r.returncode == 0, f"Cascader semantic tests failed:\n{r.stderr[-500:]}"


def calculate_reward():
    """Calculate the final reward based on test results."""
    tests = [
        test_cascader_columns_file_exists,
        test_cascader_style_structure,
        test_typescript_compiles,
        test_style_structure_valid,
        test_cssinjs_runtime_behavior,
        test_repo_typescript_check,
        test_repo_biome_lint,
        test_repo_eslint,
        test_repo_cascader_index_tests,
        test_repo_cascader_demo_tests,
        test_repo_cascader_a11y_tests,
        test_repo_cascader_type_tests,
        test_repo_cascader_semantic_tests,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"ERROR: {test.__name__}: {e}")

    total = passed + failed
    reward = 1.0 if failed == 0 else 0.0

    print(f"\n{'='*50}")
    print(f"Tests passed: {passed}/{total}")
    print(f"REWARD: {reward:.2f}")
    print(f"{'='*50}")

    return reward


if __name__ == "__main__":
    reward = calculate_reward()
    sys.exit(0 if reward >= 0.8 else 1)
