"""Tests for OpenHands PR #13625: Replace loading spinner with static icon."""

import os
import re
import subprocess

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"

# File paths
TASK_ITEM_V1 = f"{FRONTEND}/src/components/v1/chat/task-tracking/task-item.tsx"
TASK_ITEM_FEATURES = f"{FRONTEND}/src/components/features/chat/task-tracking/task-item.tsx"
NEW_ICON = f"{FRONTEND}/src/icons/u-check-circle-half.svg"


def test_new_icon_file_exists():
    """Fail-to-pass: New SVG icon file must exist."""
    assert os.path.exists(NEW_ICON), f"New icon file not found: {NEW_ICON}"
    with open(NEW_ICON, 'r') as f:
        content = f.read()
    assert '<svg' in content, "Icon file should contain SVG markup"
    assert 'check-circle-half' in content.lower() or '<path' in content, "Icon should have SVG paths"


def test_v1_component_imports_correct_icon():
    """Fail-to-pass: V1 component imports CheckCircleHalfIcon instead of LoadingIcon."""
    with open(TASK_ITEM_V1, 'r') as f:
        content = f.read()

    # Should import CheckCircleHalfIcon
    assert 'CheckCircleHalfIcon' in content, "V1 component should import CheckCircleHalfIcon"
    # Should NOT import LoadingIcon
    assert 'LoadingIcon' not in content, "V1 component should not import LoadingIcon"


def test_features_component_imports_correct_icon():
    """Fail-to-pass: Features component imports CheckCircleHalfIcon instead of LoadingIcon."""
    with open(TASK_ITEM_FEATURES, 'r') as f:
        content = f.read()

    # Should import CheckCircleHalfIcon
    assert 'CheckCircleHalfIcon' in content, "Features component should import CheckCircleHalfIcon"
    # Should NOT import LoadingIcon
    assert 'LoadingIcon' not in content, "Features component should not import LoadingIcon"


def test_v1_in_progress_no_animation():
    """Fail-to-pass: V1 component should not use animate-spin for in_progress state."""
    with open(TASK_ITEM_V1, 'r') as f:
        content = f.read()

    # Find the in_progress case
    pattern = r'case "in_progress":\s*return\s*<([^>]+)'
    match = re.search(pattern, content)
    assert match, "Should find in_progress case in V1 component"

    in_progress_element = match.group(1)
    # Should use CheckCircleHalfIcon
    assert 'CheckCircleHalfIcon' in in_progress_element, "in_progress should use CheckCircleHalfIcon"
    # Should NOT have animate-spin
    assert 'animate-spin' not in in_progress_element, "in_progress should NOT have animate-spin class"


def test_features_in_progress_no_animation():
    """Fail-to-pass: Features component should not use animate-spin for in_progress state."""
    with open(TASK_ITEM_FEATURES, 'r') as f:
        content = f.read()

    # Find the in_progress case
    pattern = r'case "in_progress":\s*return\s*<([^>]+)>'
    match = re.search(pattern, content)
    assert match, "Should find in_progress case in Features component"

    in_progress_element = match.group(1)
    # Should use CheckCircleHalfIcon
    assert 'CheckCircleHalfIcon' in in_progress_element, "in_progress should use CheckCircleHalfIcon"
    # Should NOT have animate-spin
    assert 'animate-spin' not in in_progress_element, "in_progress should NOT have animate-spin class"


def test_v1_icon_usage_consistency():
    """Fail-to-pass: V1 component uses correct icons for all states."""
    with open(TASK_ITEM_V1, 'r') as f:
        content = f.read()

    # Check each state uses the correct icon
    assert 'case "todo":' in content, "Should have todo case"
    assert 'case "in_progress":' in content, "Should have in_progress case"
    assert 'case "done":' in content, "Should have done case"

    # Verify CircleIcon for todo
    todo_match = re.search(r'case "todo":\s*return\s*<([^>]+)>', content)
    if todo_match:
        assert 'CircleIcon' in todo_match.group(1), "todo should use CircleIcon"

    # Verify CheckCircleIcon for done
    done_match = re.search(r'case "done":\s*return\s*<([^>]+)>', content)
    if done_match:
        assert 'CheckCircleIcon' in done_match.group(1), "done should use CheckCircleIcon"


def test_features_icon_usage_consistency():
    """Fail-to-pass: Features component uses correct icons for all states."""
    with open(TASK_ITEM_FEATURES, 'r') as f:
        content = f.read()

    # Check each state uses the correct icon
    assert 'case "todo":' in content, "Should have todo case"
    assert 'case "in_progress":' in content, "Should have in_progress case"
    assert 'case "done":' in content, "Should have done case"

    # Verify CircleIcon for todo
    todo_match = re.search(r'case "todo":\s*return\s*<([^>]+)>', content)
    if todo_match:
        assert 'CircleIcon' in todo_match.group(1), "todo should use CircleIcon"

    # Verify CheckCircleIcon for done
    done_match = re.search(r'case "done":\s*return\s*<([^>]+)>', content)
    if done_match:
        assert 'CheckCircleIcon' in done_match.group(1), "done should use CheckCircleIcon"


def test_repo_frontend_build():
    """Pass-to-pass: Frontend should build successfully."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Frontend build failed:\n{result.stderr[-1000:]}"


def test_repo_frontend_lint():
    """Pass-to-pass: Frontend lint should pass."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Allow some warnings but not errors
    assert result.returncode == 0, f"Frontend lint failed:\n{result.stderr[-500:]}"


def test_repo_typecheck():
    """Pass-to-pass: TypeScript typecheck should pass."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-500:]}"


def test_repo_translation_completeness():
    """Pass-to-pass: Translation completeness check should pass."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Translation completeness check failed:\n{result.stderr[-500:]}"
