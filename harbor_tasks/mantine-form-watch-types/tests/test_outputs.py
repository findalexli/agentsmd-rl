"""Tests for mantine-form-watch-types task.

This task verifies that the form.watch callback has correct TypeScript types
for previousValue and value fields, using FormPathValue and LooseKeys types.
"""

import subprocess
import sys
import os

REPO = "/workspace/mantine"
FORM_PACKAGE = f"{REPO}/packages/@mantine/form"


def test_form_watch_types_import_present():
    """Verify that FormPathValue and LooseKeys types are imported in use-form.ts.

    This is a fail-to-pass test: without the fix, the import is missing.
    """
    use_form_path = f"{FORM_PACKAGE}/src/use-form.ts"
    with open(use_form_path, "r") as f:
        content = f.read()

    # Check that the import for FormPathValue and LooseKeys is present
    assert "import type { FormPathValue, LooseKeys } from './paths.types';" in content, \
        "Missing import for FormPathValue and LooseKeys types"


def test_form_watch_callback_has_type_assertions():
    """Verify that form.watch callback values have proper type assertions.

    This is a fail-to-pass test: without the fix, the type assertions are missing.
    """
    use_form_path = f"{FORM_PACKAGE}/src/use-form.ts"
    with open(use_form_path, "r") as f:
        content = f.read()

    # Check that previousValue has FormPathValue type assertion
    assert "previousValue: getPath(path, previousValues) as FormPathValue<" in content, \
        "Missing FormPathValue type assertion for previousValue"

    # Check that value has FormPathValue type assertion
    assert "value: getPath(path, $values.refValues.current) as FormPathValue<" in content, \
        "Missing FormPathValue type assertion for value"

    # Check that both use LooseKeys<Values> as the second type parameter
    assert "LooseKeys<Values>" in content, \
        "Missing LooseKeys<Values> type parameter in assertions"


def test_eslint_passes():
    """Verify ESLint passes on the modified use-form.ts file.

    This is a pass-to-pass test: per CLAUDE.md, always run eslint on changed files.
    """
    result = subprocess.run(
        ["npx", "eslint", "packages/@mantine/form/src/use-form.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_form_package_tests():
    """Run the existing Jest tests for @mantine/form package.

    This is a pass-to-pass test: existing tests should continue to pass.
    """
    result = subprocess.run(
        ["npx", "jest", "@mantine/form", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Jest tests failed:\n{result.stdout}\n{result.stderr}"


def test_form_watch_tests():
    """Run Jest tests specifically for form.watch functionality.

    This is a pass_to_pass test: the watch functionality tests should pass
    before and after the fix. Verifies that the form.watch callbacks work
    correctly with previousValue and value fields.
    """
    result = subprocess.run(
        ["npx", "jest", "packages/@mantine/form/src/tests/use-form/watch.test.tsx", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Watch tests failed:\n{result.stdout}\n{result.stderr}"


def test_form_paths_tests():
    """Run Jest tests for the paths module where FormPathValue and LooseKeys types are defined.

    This is a pass_to_pass test: the paths module tests should pass
    before and after the fix. Verifies the core type utilities work correctly.
    """
    result = subprocess.run(
        ["npx", "jest", "packages/@mantine/form/src/paths/", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Paths tests failed:\n{result.stdout}\n{result.stderr}"


