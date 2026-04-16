"""Tests for excalidraw bound arrow elements fix.

This test validates that:
1. distributeElements calls updateBoundElements after mutating elements
2. textWysiwyg calls updateBoundElements after updating container height
"""

import subprocess
import os
import re

REPO = "/workspace/excalidraw"


def test_typescript_compiles():
    """Repo TypeScript should compile without errors."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript type check failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_distribute_imports_update_bound_elements():
    """distribute.ts should import updateBoundElements from binding module."""
    dist_file = os.path.join(REPO, "packages/element/src/distribute.ts")
    with open(dist_file, "r") as f:
        content = f.read()

    # Check for the import
    assert "updateBoundElements" in content, \
        "distribute.ts should import updateBoundElements"
    assert 'from "./binding"' in content, \
        "distribute.ts should import from ./binding"


def test_distribute_imports_scene_type():
    """distribute.ts should import Scene type."""
    dist_file = os.path.join(REPO, "packages/element/src/distribute.ts")
    with open(dist_file, "r") as f:
        content = f.read()

    assert 'import type { Scene }' in content, \
        "distribute.ts should import Scene type"


def test_distribute_elements_accepts_scene_param():
    """distributeElements function should accept scene parameter."""
    dist_file = os.path.join(REPO, "packages/element/src/distribute.ts")
    with open(dist_file, "r") as f:
        content = f.read()

    # Check function signature includes scene parameter
    pattern = r"export const distributeElements\s*=\s*\([^)]*scene:\s*Scene"
    assert re.search(pattern, content), \
        "distributeElements should accept scene: Scene parameter"


def test_distribute_uses_mutate_element():
    """distributeElements should use scene.mutateElement instead of newElementWith."""
    dist_file = os.path.join(REPO, "packages/element/src/distribute.ts")
    with open(dist_file, "r") as f:
        content = f.read()

    # Should use scene.mutateElement
    assert "scene.mutateElement" in content, \
        "distributeElements should use scene.mutateElement"
    # Should NOT use newElementWith (which was the old implementation)
    assert "newElementWith" not in content, \
        "distributeElements should NOT use newElementWith (use scene.mutateElement instead)"


def test_distribute_calls_update_bound_elements():
    """distributeElements should call updateBoundElements after mutation."""
    dist_file = os.path.join(REPO, "packages/element/src/distribute.ts")
    with open(dist_file, "r") as f:
        content = f.read()

    # Check for updateBoundElements call with simultaneouslyUpdated option
    assert "updateBoundElements(element, scene" in content, \
        "distributeElements should call updateBoundElements(element, scene, ...)"
    assert "simultaneouslyUpdated: group" in content, \
        "updateBoundElements should be called with simultaneouslyUpdated: group"


def test_distribute_calls_update_bound_elements_twice():
    """distributeElements should call updateBoundElements in both code paths."""
    dist_file = os.path.join(REPO, "packages/element/src/distribute.ts")
    with open(dist_file, "r") as f:
        content = f.read()

    # Count occurrences - should be at least 2 (for both the negative step and normal distribution paths)
    count = content.count("updateBoundElements(element, scene")
    assert count >= 2, \
        f"distributeElements should call updateBoundElements at least twice (found {count})"


def test_action_distribute_passes_scene():
    """actionDistribute.tsx should pass app.scene to distributeElements."""
    action_file = os.path.join(REPO, "packages/excalidraw/actions/actionDistribute.tsx")
    with open(action_file, "r") as f:
        content = f.read()

    # Check that app.scene is passed as the last argument
    assert "app.scene," in content or "app.scene\n" in content, \
        "actionDistribute.tsx should pass app.scene to distributeElements"


def test_wysiwyg_imports_update_bound_elements():
    """textWysiwyg.tsx should import updateBoundElements."""
    wysiwyg_file = os.path.join(REPO, "packages/excalidraw/wysiwyg/textWysiwyg.tsx")
    with open(wysiwyg_file, "r") as f:
        content = f.read()

    # Check for the import
    assert "updateBoundElements" in content, \
        "textWysiwyg.tsx should import updateBoundElements"


def test_wysiwyg_calls_update_bound_elements_on_overflow():
    """textWysiwyg should call updateBoundElements when text overflows container."""
    wysiwyg_file = os.path.join(REPO, "packages/excalidraw/wysiwyg/textWysiwyg.tsx")
    with open(wysiwyg_file, "r") as f:
        content = f.read()

    # Count occurrences of updateBoundElements calls
    count = content.count("updateBoundElements(container, app.scene)")
    assert count >= 2, \
        f"textWysiwyg should call updateBoundElements at least twice (found {count})"


def test_wysiwyg_calls_after_mutate_element():
    """updateBoundElements in textWysiwyg should be called after mutateElement."""
    wysiwyg_file = os.path.join(REPO, "packages/excalidraw/wysiwyg/textWysiwyg.tsx")
    with open(wysiwyg_file, "r") as f:
        content = f.read()

    # Look for pattern: app.scene.mutateElement(container, { height: ... });
    # followed by updateBoundElements(container, app.scene);
    pattern = r"app\.scene\.mutateElement\(container,\s*\{\s*height:\s*targetContainerHeight\s*\}\);\s*updateBoundElements\(container,\s*app\.scene\)"
    matches = re.findall(pattern, content, re.DOTALL)
    assert len(matches) >= 2, \
        f"updateBoundElements should be called after mutateElement in both overflow scenarios (found {len(matches)} matches)"


# =============================================================================
# PASS-TO-PASS TESTS: Repository CI commands that should pass at base commit
# These validate the fix doesn't break existing functionality
# =============================================================================


def test_repo_typecheck():
    """Repository TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repository ESLint linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_format():
    """Repository Prettier formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_distribute_tests():
    """Repository distribute tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/distribute.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Distribute tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_binding_tests():
    """Repository binding tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/binding.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Binding tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_wysiwyg_tests():
    """Repository textWysiwyg tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/wysiwyg/textWysiwyg.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"textWysiwyg tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
