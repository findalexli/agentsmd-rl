"""
Tests for excalidraw crop cursor drift fix (PR #10727).

This verifies that:
1. The drag offset calculation uses natural image dimensions instead of zoom scaling
2. The vectorScale import is removed and getUncroppedWidthAndHeight is added
3. TypeScript compilation passes
"""

import subprocess
import re

REPO = "/workspace/excalidraw"
APP_TSX = f"{REPO}/packages/excalidraw/components/App.tsx"


def test_vectorScale_import_removed():
    """vectorScale import should be removed from imports (f2p)."""
    with open(APP_TSX, 'r') as f:
        content = f.read()

    # Check that vectorScale is no longer imported
    import_section = content.split('from "@excalidraw/element"')[0]
    assert 'vectorScale' not in import_section, \
        "vectorScale should be removed from imports"


def test_getUncroppedWidthAndHeight_import_added():
    """getUncroppedWidthAndHeight import should be added (f2p)."""
    with open(APP_TSX, 'r') as f:
        content = f.read()

    # Check that getUncroppedWidthAndHeight is imported from @excalidraw/element
    assert 'getUncroppedWidthAndHeight' in content, \
        "getUncroppedWidthAndHeight should be imported"

    # Verify it's in the right import block
    element_imports = re.search(
        r'import\s*\{[^}]*\}\s*from\s*"@excalidraw/element"',
        content,
        re.DOTALL
    )
    assert element_imports is not None, \
        "Should have imports from @excalidraw/element"
    assert 'getUncroppedWidthAndHeight' in element_imports.group(0), \
        "getUncroppedWidthAndHeight should be in @excalidraw/element imports"


def test_natural_width_scaling_used():
    """Drag offset should use naturalWidth/uncroppedSize.width ratio (f2p)."""
    with open(APP_TSX, 'r') as f:
        content = f.read()

    # Find the cropping section and verify new scaling logic
    assert 'image.naturalWidth / uncroppedSize.width' in content, \
        "Should use naturalWidth / uncroppedSize.width for x scaling"
    assert 'image.naturalHeight / uncroppedSize.height' in content, \
        "Should use naturalHeight / uncroppedSize.height for y scaling"


def test_uncropped_size_variable_created():
    """uncroppedSize variable should be created using getUncroppedWidthAndHeight (f2p)."""
    with open(APP_TSX, 'r') as f:
        content = f.read()

    # Check that getUncroppedWidthAndHeight is called
    assert 'getUncroppedWidthAndHeight(croppingElement)' in content, \
        "Should call getUncroppedWidthAndHeight with croppingElement"


def test_zoom_scaling_removed():
    """Old zoom-based scaling (Math.max(this.state.zoom.value, 2)) should be removed (f2p)."""
    with open(APP_TSX, 'r') as f:
        content = f.read()

    # Check that the old zoom-based scaling is removed
    # Look for the pattern that was in vectorScale(..., Math.max(this.state.zoom.value, 2))
    assert 'Math.max(this.state.zoom.value, 2)' not in content, \
        "Old zoom-based scaling Math.max(this.state.zoom.value, 2) should be removed"


def test_vector_function_used_directly():
    """vector() should be called directly instead of vectorScale() (f2p)."""
    with open(APP_TSX, 'r') as f:
        content = f.read()

    # In the fix, vector is called directly and then scaled manually
    # We should NOT find vectorScale being called anymore
    assert 'vectorScale' not in content, \
        "vectorScale function should not be used anywhere"


def test_typescript_compilation():
    """TypeScript compilation should pass (p2p)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_linting_passes():
    """ESLint should pass on the modified file (p2p)."""
    result = subprocess.run(
        ["yarn", "eslint", "--max-warnings=0", "packages/excalidraw/components/App.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Some warnings are OK, but no errors
    assert result.returncode == 0 or "error" not in result.stdout.lower(), \
        f"ESLint found errors:\n{result.stdout[-500:]}"


def test_crop_element_tests():
    """Crop element unit tests should pass (p2p)."""
    result = subprocess.run(
        ["yarn", "vitest", "run", "packages/element/tests/cropElement.test.tsx", "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"Crop element tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_image_tests():
    """Image insertion tests should pass (p2p)."""
    result = subprocess.run(
        ["yarn", "vitest", "run", "packages/excalidraw/tests/image.test.tsx", "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"Image tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_element_package_tests():
    """All element package tests should pass (p2p)."""
    result = subprocess.run(
        ["yarn", "vitest", "run", "packages/element/tests/", "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"Element package tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"
