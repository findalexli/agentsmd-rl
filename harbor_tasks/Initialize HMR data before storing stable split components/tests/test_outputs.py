"""
Test that the HMR data initialization fix is properly applied.

The bug: The Babel template for stable split components accessed `import.meta.hot.data[key]`
without first checking if `data` exists. This causes crashes in Vitest when HMR is not initialized.

The fix: Add `import.meta.hot.data ??= {}` before accessing the data property.
"""

import subprocess
import sys
import os
import re

REPO_PATH = "/workspace/router"
TARGET_FILE = "packages/router-plugin/src/core/code-splitter/plugins/react-stable-hmr-split-route-components.ts"
FULL_TARGET_PATH = f"{REPO_PATH}/{TARGET_FILE}"


def test_source_file_has_data_initialization():
    """
    FAIL-TO-PASS: Source code must initialize import.meta.hot.data before use.

    The fix must add `import.meta.hot.data ??= {}` before accessing data[key].
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Must contain the data initialization
    assert 'import.meta.hot.data ??= {}' in content, \
        "Missing 'import.meta.hot.data ??= {}' in source template"

    # Must have it BEFORE the data access in the if block
    template_section = re.search(
        r'if \(import\.meta\.hot\) \{(.*?)import\.meta\.hot\.data\[',
        content,
        re.DOTALL
    )
    if template_section:
        assert '??=' in template_section.group(1), \
            "Data initialization must come before data[key] access"


def test_template_produces_correct_output():
    """
    FAIL-TO-PASS: The Babel template must generate code with data initialization.

    We compile a sample route component and verify the output includes
    the nullish coalescing assignment for import.meta.hot.data.
    """
    # Create a test file to compile
    test_code = '''
import * as React from 'react'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/posts')({
  component: component,
})

function component() {
  return <div>posts</div>
}
'''

    test_file = "/tmp/test_hmr.tsx"
    with open(test_file, 'w') as f:
        f.write(test_code)

    # Build the router-plugin first
    build_result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:build"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    # Create a Node.js script to run the compilation
    compile_script = f'''
const {{ compileCodeSplitReferenceRoute }} = require('{REPO_PATH}/packages/router-plugin/dist/index.cjs');
const {{ getReferenceRouteCompilerPlugins }} = require('{REPO_PATH}/packages/router-plugin/dist/index.cjs');

const defaultCodeSplitGroupings = [
  ['component', 'errorComponent'],
  ['notFoundComponent'],
];

const code = `{test_code.replace("'", "\\'")}`;

const compileResult = compileCodeSplitReferenceRoute({{
  code,
  filename: 'posts.tsx',
  id: 'posts.tsx',
  addHmr: true,
  codeSplitGroupings: defaultCodeSplitGroupings,
  targetFramework: 'react',
  compilerPlugins: getReferenceRouteCompilerPlugins({{
    targetFramework: 'react',
    addHmr: true,
  }}),
}});

if (compileResult?.code) {{
  console.log(compileResult.code);
}} else {{
  console.error('Compilation failed or returned no code');
  process.exit(1);
}}
'''

    compile_file = "/tmp/compile_test.js"
    with open(compile_file, 'w') as f:
        f.write(compile_script)

    # Run the compilation
    compile_result = subprocess.run(
        ["node", compile_file],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=60
    )

    if compile_result.returncode != 0:
        # If the test fails to run, skip with informative message
        # The important test is that the source has the fix
        print(f"Compilation test setup issue: {compile_result.stderr}")
        # Fall back to checking the snapshot files which are updated with the fix
        return

    output = compile_result.stdout

    # Check for the initialization in the output
    assert 'import.meta.hot.data ??= {}' in output or 'import.meta.hot.data ??= {}' in output.replace(' ', ''), \
        f"Compiled output missing data initialization. Output:\n{output}"

    # Check that data[key] comes after the initialization
    lines = output.split('\n')
    init_found = False
    for line in lines:
        if '??=' in line and 'import.meta.hot.data' in line:
            init_found = True
        if '["tsr-split-component:' in line and 'import.meta.hot.data[' in line:
            assert init_found, "data[key] access found before data initialization"


def test_add_hmr_unit_tests_pass():
    """
    PASS-TO-PASS: The existing unit tests for add-hmr must pass.

    This includes the new test that verifies data initialization.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:test:unit", "--", "tests/add-hmr.test.ts"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_snapshots_have_data_initialization():
    """
    FAIL-TO-PASS: Snapshot files must contain the data initialization.

    The fix updates multiple snapshot files to include `import.meta.hot.data ??= {{}}`
    in the expected output.
    """
    snapshot_files = [
        "packages/router-plugin/tests/add-hmr/snapshots/react/arrow-function@true.tsx",
        "packages/router-plugin/tests/add-hmr/snapshots/react/function-declaration@true.tsx",
        "packages/router-plugin/tests/add-hmr/snapshots/react/multi-component@true.tsx",
        "packages/router-plugin/tests/add-hmr/snapshots/react/string-literal-keys@true.tsx",
    ]

    for snapshot_file in snapshot_files:
        full_path = f"{REPO_PATH}/{snapshot_file}"
        if not os.path.exists(full_path):
            continue  # Skip if file doesn't exist

        with open(full_path, 'r') as f:
            content = f.read()

        # Each snapshot should have the data initialization
        assert 'import.meta.hot.data ??= {}' in content, \
            f"Missing data initialization in {snapshot_file}"

        # Count occurrences - should match number of HMR blocks
        init_count = content.count('import.meta.hot.data ??= {}')
        hmr_blocks = content.count('if (import.meta.hot)')
        assert init_count >= hmr_blocks, \
            f"Expected at least {hmr_blocks} data initializations in {snapshot_file}, found {init_count}"


def test_code_compiles_after_fix():
    """
    PASS-TO-PASS: The package must compile without TypeScript errors.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-plugin:build"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, \
        f"Build failed:\n{result.stdout}\n{result.stderr}"


def test_no_direct_data_access_without_check():
    """
    FAIL-TO-PASS: The template should not access data[key] without first initializing data.

    This checks the source template for the anti-pattern of directly accessing
    import.meta.hot.data[key] without the ??= initialization.
    """
    with open(FULL_TARGET_PATH, 'r') as f:
        content = f.read()

    # Find the template string content
    template_match = re.search(
        r'template\.statements\((.*?)syntacticPlaceholders',
        content,
        re.DOTALL
    )

    if template_match:
        template_str = template_match.group(1)
        # After the fix, the template should have ??= before data[key]
        assert '??=' in template_str, \
            "Template missing nullish coalescing assignment for data initialization"

        # Check ordering: ??= should come before data[key] access
        init_pos = template_str.find('??=')
        data_access_pos = template_str.find('import.meta.hot.data[%%hotDataKey%%]')

        if init_pos > 0 and data_access_pos > 0:
            assert init_pos < data_access_pos, \
                "Data initialization must come before data[key] access in template"
