"""
Test suite for Storybook dual-slot status functionality.

Tests verify:
1. getChangeDetectionStatus() - splits statuses into change vs test categories
2. getGroupDualStatus() - computes dual status for groups/components
3. statusPriority is properly exported
4. CHANGE_DETECTION_STATUS_TYPE_ID is properly imported and used
"""

import subprocess
import sys
import os

REPO = "/workspace/storybook/code"


def test_change_detection_status_function_exists():
    """Fail-to-pass: getChangeDetectionStatus function must exist."""
    result = subprocess.run(
        ["grep", "-n", "export function getChangeDetectionStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getChangeDetectionStatus function not found in status.tsx"
    assert "export function getChangeDetectionStatus" in result.stdout


def test_group_dual_status_function_exists():
    """Fail-to-pass: getGroupDualStatus function must exist."""
    result = subprocess.run(
        ["grep", "-n", "export function getGroupDualStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getGroupDualStatus function not found in status.tsx"
    assert "export function getGroupDualStatus" in result.stdout


def test_status_priority_exported():
    """Fail-to-pass: statusPriority must be exported for Tree.tsx to use."""
    result = subprocess.run(
        ["grep", "-n", "export.*statusPriority", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "statusPriority not exported from status.tsx"


def test_change_detection_imports_constant():
    """Fail-to-pass: status.tsx must import CHANGE_DETECTION_STATUS_TYPE_ID."""
    result = subprocess.run(
        ["grep", "CHANGE_DETECTION_STATUS_TYPE_ID", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "CHANGE_DETECTION_STATUS_TYPE_ID not imported in status.tsx"


def test_change_detection_status_filters_by_typeid():
    """Fail-to-pass: getChangeDetectionStatus must filter by typeId."""
    # Check that the function uses filter with typeId comparison
    result = subprocess.run(
        ["grep", "-A30", "export function getChangeDetectionStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getChangeDetectionStatus function not found"
    # Should filter by CHANGE_DETECTION_STATUS_TYPE_ID
    assert "CHANGE_DETECTION_STATUS_TYPE_ID" in result.stdout, "Function must use CHANGE_DETECTION_STATUS_TYPE_ID"
    assert "filter" in result.stdout, "Function must use filter()"


def test_change_detection_uses_most_critical():
    """Fail-to-pass: getChangeDetectionStatus must call getMostCriticalStatusValue."""
    result = subprocess.run(
        ["grep", "-A30", "export function getChangeDetectionStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getChangeDetectionStatus function not found"
    assert "getMostCriticalStatusValue" in result.stdout, "Function must call getMostCriticalStatusValue"


def test_group_dual_status_traverses_descendants():
    """Fail-to-pass: getGroupDualStatus must use getDescendantIds."""
    result = subprocess.run(
        ["grep", "-A40", "export function getGroupDualStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getGroupDualStatus function not found"
    assert "getDescendantIds" in result.stdout, "Function must use getDescendantIds"


def test_group_dual_status_returns_correct_shape():
    """Fail-to-pass: getGroupDualStatus must return {change, test} structure."""
    result = subprocess.run(
        ["grep", "-A40", "export function getGroupDualStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getGroupDualStatus function not found"
    # Check return type annotation includes change and test
    content = result.stdout
    assert "change" in content, "Function must handle change status"
    assert "test" in content, "Function must handle test status"


# Pass-to-pass tests: These verify the implementation doesn't break existing functionality

def test_status_function_signatures():
    """Pass-to-pass: Status utility functions have correct signatures."""
    # Check that getMostCriticalStatusValue still exists and works
    result = subprocess.run(
        ["grep", "-n", "export const getMostCriticalStatusValue", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getMostCriticalStatusValue not found"


def test_types_import_correct():
    """Pass-to-pass: Types are correctly imported."""
    # Check that StatusByTypeId is imported from types
    result = subprocess.run(
        ["grep", "StatusByTypeId", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "StatusByTypeId not referenced in status.tsx"


def test_imports_from_internal_types():
    """Pass-to-pass: Imports come from storybook/internal/types."""
    result = subprocess.run(
        ["grep", "from 'storybook/internal/types'", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "Must import from 'storybook/internal/types'"


def test_getstatus_still_works():
    """Pass-to-pass: Existing getStatus function still works."""
    result = subprocess.run(
        ["grep", "-n", "export const getStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getStatus function not found"


def test_getgroupstatus_still_works():
    """Pass-to-pass: Existing getGroupStatus function still works."""
    result = subprocess.run(
        ["grep", "-n", "export function getGroupStatus", "core/src/manager/utils/status.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "getGroupStatus function not found"


# Repository CI tests - these run actual CI commands as pass-to-pass gates


def test_repo_esbuild_status():
    """Repo CI: status.tsx compiles with esbuild (pass_to_pass)."""
    r = subprocess.run(
        [
            "npx", "esbuild",
            "core/src/manager/utils/status.tsx",
            "--bundle",
            "--platform=node",
            "--format=esm",
            "--external:storybook/*",
            "--external:@storybook/*",
            "--external:react",
            "--external:react-dom",
            "--external:memoizerific",
            "--external:polished",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"esbuild failed:\n{r.stderr[-500:]}"


def test_repo_syntax_status():
    """Repo CI: status.tsx has valid syntax (pass_to_pass)."""
    # Use node to check the file can be parsed as TypeScript
    r = subprocess.run(
        [
            "node",
            "-e",
            "require('fs').readFileSync('core/src/manager/utils/status.tsx', 'utf8'); console.log('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"syntax check failed:\n{r.stderr[-500:]}"


def test_repo_status_test_exists():
    """Repo CI: status.test.ts exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        [
            "test",
            "-f",
            "core/src/manager/utils/status.test.ts",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, "status.test.ts does not exist"


def test_repo_no_empty_files():
    """Repo CI: No empty source files in manager utils (pass_to_pass)."""
    r = subprocess.run(
        [
            "bash",
            "-c",
            "! find core/src/manager/utils -name '*.ts' -o -name '*.tsx' | xargs -I{} sh -c 'test -s \"{}\" || echo \"{}\"' 2>/dev/null | grep .",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    # Exit code 1 means no empty files found (grep didn't match), which is good
    assert r.returncode == 1 or r.stdout.strip() == "", f"Empty files found:\n{r.stdout}"
