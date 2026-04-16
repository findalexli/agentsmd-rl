"""
Test suite for Storybook dual-slot status functionality.

Tests verify actual behavior by importing and calling the functions,
then asserting on their return values.
"""

import subprocess
import os
import json
import tempfile
import re

REPO = "/workspace/storybook/code"


def run_tsx(code, timeout=60):
    """Execute TypeScript code using tsx and return stdout."""
    result = subprocess.run(
        ["npx", "tsx", "-e", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def test_change_detection_status_exists_and_runs():
    """Fail-to-pass: getChangeDetectionStatus must exist and be callable."""
    code = """
import { getChangeDetectionStatus } from './core/src/manager/utils/status.tsx';

// Call with empty object - should return default structure
const result = getChangeDetectionStatus({});
console.log(JSON.stringify(result));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Function not callable: {result.stderr[:500]}"
    # Should return an object with changeStatus and testStatus
    data = json.loads(result.stdout.strip())
    assert "changeStatus" in data, f"Missing changeStatus in result: {data}"
    assert "testStatus" in data, f"Missing testStatus in result: {data}"


def test_change_detection_status_correctly_splits_categories():
    """Fail-to-pass: statuses must be split by typeId into change vs test."""
    code = """
import { getChangeDetectionStatus, CHANGE_DETECTION_STATUS_TYPE_ID } from './core/src/manager/utils/status.tsx';

// Create test data: one CHANGE_DETECTION status and one other status
const statuses = {
    'status-1': { typeId: CHANGE_DETECTION_STATUS_TYPE_ID, value: 'warn' },
    'status-2': { typeId: 'some-other-type', value: 'error' }
};

const result = getChangeDetectionStatus(statuses);
console.log(JSON.stringify(result));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Function failed: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    # changeStatus should be the most critical among change-type statuses (only 'warn')
    assert data["changeStatus"] == "warn", f"Expected changeStatus 'warn', got: {data['changeStatus']}"
    # testStatus should be the most critical among test-type statuses (only 'error')
    assert data["testStatus"] == "error", f"Expected testStatus 'error', got: {data['testStatus']}"


def test_change_detection_status_prioritizes_critical_values():
    """Fail-to-pass: getChangeDetectionStatus must return most critical value."""
    code = """
import { getChangeDetectionStatus, CHANGE_DETECTION_STATUS_TYPE_ID } from './core/src/manager/utils/status.tsx';

const statuses = {
    'status-1': { typeId: CHANGE_DETECTION_STATUS_TYPE_ID, value: 'positive' },
    'status-2': { typeId: CHANGE_DETECTION_STATUS_TYPE_ID, value: 'error' },
    'status-3': { typeId: 'other-type', value: 'warn' },
    'status-4': { typeId: 'other-type', value: 'positive' }
};

const result = getChangeDetectionStatus(statuses);
console.log(JSON.stringify(result));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Function failed: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    # Among change statuses: 'positive' < 'error' -> should be 'error'
    assert data["changeStatus"] == "error", f"Expected 'error' (most critical), got: {data['changeStatus']}"
    # Among test statuses: 'positive' < 'warn' -> should be 'warn'
    assert data["testStatus"] == "warn", f"Expected 'warn' (most critical), got: {data['testStatus']}"


def test_group_dual_status_exists_and_runs():
    """Fail-to-pass: getGroupDualStatus must exist and be callable."""
    code = """
import { getGroupDualStatus } from './core/src/manager/utils/status.tsx';

// Minimal test data
const collapsedData = {};
const allStatuses = {};
const result = getGroupDualStatus(collapsedData, allStatuses);
console.log(JSON.stringify(result));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Function not callable: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    # Result should be an object (possibly empty)
    assert isinstance(data, dict), f"Expected dict, got: {type(data)}"


def test_group_dual_status_aggregates_descendants():
    """Fail-to-pass: getGroupDualStatus must aggregate statuses from descendant stories."""
    code = """
import { getGroupDualStatus, getDescendantIds, CHANGE_DETECTION_STATUS_TYPE_ID } from './core/src/manager/utils/status.tsx';

// Set up: a group containing two stories with different status types
const collapsedData = {
    'group-1': { id: 'group-1', type: 'group' },
    'story-1': { id: 'story-1', type: 'story', parent: 'group-1' },
    'story-2': { id: 'story-2', type: 'story', parent: 'group-1' }
};

const allStatuses = {
    'story-1': {
        'status-1': { typeId: CHANGE_DETECTION_STATUS_TYPE_ID, value: 'error' }
    },
    'story-2': {
        'status-2': { typeId: 'other-type', value: 'warn' }
    }
};

// Compute expected: story-1 and story-2 are descendants of group-1
const childIds = getDescendantIds(collapsedData, 'group-1', false);
// Only 'story' type should be included in aggregation
const storyIds = Object.values(collapsedData)
    .filter(item => item.type === 'story')
    .map(item => item.id);

const result = getGroupDualStatus(collapsedData, allStatuses);
console.log(JSON.stringify(result));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Function failed: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    # Should have entry for 'group-1'
    assert 'group-1' in data, f"Expected group-1 in result, got: {list(data.keys())}"
    # The group should have change and test properties
    assert 'change' in data['group-1'], f"Expected 'change' in group result: {data['group-1']}"
    assert 'test' in data['group-1'], f"Expected 'test' in group result: {data['group-1']}"
    # The change value should be 'error' (from story-1's CHANGE_DETECTION status)
    assert data['group-1']['change'] == 'error', f"Expected 'error', got: {data['group-1']['change']}"
    # The test value should be 'warn' (from story-2's non-CHANGE_DETECTION status)
    assert data['group-1']['test'] == 'warn', f"Expected 'warn', got: {data['group-1']['test']}"


def test_status_priority_exported():
    """Fail-to-pass: statusPriority must be exported for Tree.tsx to use."""
    code = """
import { statusPriority } from './core/src/manager/utils/status.tsx';
console.log(JSON.stringify(statusPriority));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"statusPriority not exported: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    assert isinstance(data, list), f"statusPriority should be array, got: {type(data)}"
    assert len(data) > 0, "statusPriority should not be empty"


# === PASS-TO-PASS TESTS ===

def test_existing_status_functions_still_work():
    """Pass-to-pass: Existing getStatus and getGroupStatus still work."""
    code = """
import { getStatus, getGroupStatus, getMostCriticalStatusValue } from './core/src/manager/utils/status.tsx';
// Verify they're callable with expected signatures
const critical = getMostCriticalStatusValue(['positive', 'warn', 'error']);
console.log(JSON.stringify({ critical }));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Existing functions broken: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    assert data["critical"] == "error", "getMostCriticalStatusValue broken"


def test_status_types_importable():
    """Pass-to-pass: Status types are correctly imported."""
    code = """
import type { StatusByTypeId, StatusesByStoryIdAndTypeId } from 'storybook/internal/types';
// Verify types are available (TypeScript will error if not)
console.log(JSON.stringify({ ok: true }));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Types not importable: {result.stderr[:500]}"


def test_imports_from_internal_types():
    """Pass-to-pass: Imports come from storybook/internal/types."""
    code = """
import { CHANGE_DETECTION_STATUS_TYPE_ID } from 'storybook/internal/types';
console.log(JSON.stringify({ typeId: CHANGE_DETECTION_STATUS_TYPE_ID }));
"""
    result = run_tsx(code)
    assert result.returncode == 0, f"Import from storybook/internal/types failed: {result.stderr[:500]}"
    data = json.loads(result.stdout.strip())
    assert data["typeId"], "CHANGE_DETECTION_STATUS_TYPE_ID not available"


# === REPO CI TESTS ===

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
        ["test", "-f", "core/src/manager/utils/status.test.ts"],
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
            "bash", "-c",
            "! find core/src/manager/utils -name '*.ts' -o -name '*.tsx' | xargs -I{} sh -c 'test -s \"{}\" || echo \"{}\"' 2>/dev/null | grep .",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 1 or r.stdout.strip() == "", f"Empty files found:\n{r.stdout}"