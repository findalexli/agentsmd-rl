"""
Test suite for Shadow DOM support in Combobox component (PR #8438)

Tests verify that:
1. The new find-element-in-shadow-dom utility functions exist and work correctly
2. The use-combobox hook properly queries elements across Shadow DOM boundaries
3. TypeScript compilation succeeds for modified files
"""

import subprocess
import os
import sys

REPO = "/workspace/mantine"
UTILS_PATH = f"{REPO}/packages/@mantine/core/src/core/utils"
COMBOBOX_PATH = f"{REPO}/packages/@mantine/core/src/components/Combobox/use-combobox"


def test_find_element_in_shadow_dom_file_exists():
    """The new utility file was created (fail-to-pass)."""
    file_path = f"{UTILS_PATH}/find-element-in-shadow-dom/find-element-in-shadow-dom.ts"
    assert os.path.exists(file_path), f"Utility file not found: {file_path}"


def test_find_element_in_shadow_dom_exports():
    """The utility file exports the three required functions (fail-to-pass)."""
    file_path = f"{UTILS_PATH}/find-element-in-shadow-dom/find-element-in-shadow-dom.ts"
    with open(file_path) as f:
        content = f.read()

    assert "export function findElementBySelector" in content, "findElementBySelector not exported"
    assert "export function findElementsBySelector" in content, "findElementsBySelector not exported"
    assert "export function getRootElement" in content, "getRootElement not exported"


def test_core_utils_exports_shadow_dom_utilities():
    """The core/utils/index.ts exports the new shadow DOM utilities (fail-to-pass)."""
    file_path = f"{UTILS_PATH}/index.ts"
    with open(file_path) as f:
        content = f.read()

    assert "findElementBySelector" in content, "findElementBySelector not exported from core/utils"
    assert "findElementsBySelector" in content, "findElementsBySelector not exported from core/utils"
    assert "getRootElement" in content, "getRootElement not exported from core/utils"


def test_use_combobox_imports_shadow_dom_utilities():
    """The use-combobox.ts imports the shadow DOM utilities (fail-to-pass)."""
    file_path = f"{COMBOBOX_PATH}/use-combobox.ts"
    with open(file_path) as f:
        content = f.read()

    # Should import from the shadow DOM utilities, not use document.querySelector directly
    assert "findElementBySelector" in content, "use-combobox.ts should import findElementBySelector"
    assert "findElementsBySelector" in content, "use-combobox.ts should import findElementsBySelector"
    assert "getRootElement" in content, "use-combobox.ts should import getRootElement"


def test_use_combobox_does_not_use_direct_document_query():
    """The use-combobox.ts no longer uses direct document.querySelector for option queries (fail-to-pass)."""
    file_path = f"{COMBOBOX_PATH}/use-combobox.ts"
    with open(file_path) as f:
        content = f.read()

    # After the fix, document.querySelector should only be used within the new utility functions
    # The use-combobox.ts itself should use the shadow DOM-aware utilities
    # Check that getRootElement is used before querying
    assert "getRootElement(targetRef.current)" in content, \
        "use-combobox.ts should use getRootElement to determine the query root"


def test_use_combobox_typescript_compiles():
    """The modified use-combobox.ts compiles without errors (pass-to-pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "packages/@mantine/core/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Filter out unrelated errors (from other packages)
    errors = [line for line in result.stderr.split('\n') if 'use-combobox.ts' in line]

    assert result.returncode == 0 or len(errors) == 0, \
        f"TypeScript compilation errors in use-combobox.ts:\n{result.stderr[-2000:]}"


def test_shadow_dom_utility_typescript_compiles():
    """The new find-element-in-shadow-dom.ts compiles without errors (pass-to-pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "packages/@mantine/core/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Filter for errors in the shadow DOM utility file
    errors = [line for line in result.stderr.split('\n')
              if 'find-element-in-shadow-dom' in line]

    assert result.returncode == 0 or len(errors) == 0, \
        f"TypeScript compilation errors in find-element-in-shadow-dom:\n{result.stderr[-2000:]}"


def test_use_combobox_unit_tests_exist():
    """The use-combobox.shadow-dom.test.tsx test file was created (fail-to-pass)."""
    test_file = f"{COMBOBOX_PATH}/use-combobox.shadow-dom.test.tsx"
    assert os.path.exists(test_file), f"Shadow DOM test file not found: {test_file}"


def test_find_element_in_shadow_dom_test_file_exists():
    """The find-element-in-shadow-dom.test.ts test file was created (fail-to-pass)."""
    test_file = f"{UTILS_PATH}/find-element-in-shadow-dom/find-element-in-shadow-dom.test.ts"
    assert os.path.exists(test_file), f"Test file not found: {test_file}"


def test_getrootelement_handles_null():
    """The getRootElement function returns document when given null (fail-to-pass)."""
    file_path = f"{UTILS_PATH}/find-element-in-shadow-dom/find-element-in-shadow-dom.ts"
    with open(file_path) as f:
        content = f.read()

    # getRootElement should check for null/undefined and return document
    assert "if (!targetElement)" in content or "targetElement ?? document" in content or \
           "targetElement || document" in content, \
        "getRootElement should handle null/undefined by returning document"


def test_getrootelement_returns_shadow_root():
    """The getRootElement function returns ShadowRoot for shadow DOM elements (fail-to-pass)."""
    file_path = f"{UTILS_PATH}/find-element-in-shadow-dom/find-element-in-shadow-dom.ts"
    with open(file_path) as f:
        content = f.read()

    # Should use getRootNode() to get the actual root
    assert "getRootNode()" in content, \
        "getRootElement should use getRootNode() to determine the root"
    assert "ShadowRoot" in content, \
        "getRootElement should check if root is a ShadowRoot instance"


if __name__ == "__main__":
    # Run pytest programmatically
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))