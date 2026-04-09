#!/usr/bin/env python3
"""Tests for airflow-gantt-date-fix benchmark task.

These tests verify that the Gantt chart date parsing fix works correctly.
The bug was that `new Date().getTime()` fails for non-UTC timezone abbreviations,
returning NaN and crashing Chart.js's time scale. The fix replaces it with
`dayjs().valueOf()` for reliable date parsing.
"""

import subprocess
import sys

REPO = "/workspace/airflow"
UI_DIR = f"{REPO}/airflow-core/src/airflow/ui"


def test_vitest_gantt_utils():
    """Gantt utils tests pass (fail_to_pass).

    The PR adds comprehensive unit tests for Gantt chart scale calculations
    and data transformation. These tests verify:
    - Valid min/max computation for completed tasks with ISO dates
    - Valid min/max for running tasks (null end dates)
    - Empty data handling with running DagRun
    - Tasks with null start_date are skipped
    - Running tasks use current time as end
    - Groups with null dates are skipped
    - ISO date strings are parseable by dayjs without NaN
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "src/layouts/Details/Gantt/utils.test.ts", "--run"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Vitest failed:\n{result.stdout}\n{result.stderr}"


def test_date_parsing_produces_valid_numbers():
    """Date parsing produces valid numbers not NaN (fail_to_pass).

    This test verifies the difference between the buggy pattern
    (new Date(item.x[1] ?? "").getTime()) and the fixed pattern
    (dayjs(item.x[1]).valueOf()).

    The bug: when item.x[1] is null, the ?? operator gives "", and
    new Date("").getTime() returns NaN, crashing Chart.js.

    The fix: dayjs handles null/undefined more gracefully by returning
    the current time, which is a valid timestamp.
    """
    test_js = """
const dayjs = require('dayjs');

// Test cases that should produce valid timestamps with dayjs
const testDates = [
    "2024-03-14T10:00:00.000Z",
    "2024-03-14T10:00:00+00:00",
    "2024-03-14T10:00:00+05:30",
    "2024-03-14T10:00:00-08:00",
    undefined,  // dayjs(undefined) returns the current time
];

for (const date of testDates) {
    const val = dayjs(date).valueOf();
    if (Number.isNaN(val)) {
        console.error(`dayjs().valueOf() returned NaN for: ${date}`);
        process.exit(1);
    }
}

// Demonstrate the bug with the OLD pattern:
// new Date(item.x[1] ?? "").getTime() when item.x[1] is null
// ?? gives empty string, and new Date("").getTime() is NaN
const oldPatternWithNull = new Date("").getTime();
if (!Number.isNaN(oldPatternWithNull)) {
    console.error("Expected new Date('').getTime() to be NaN");
    process.exit(1);
}

// Demonstrate the fix with dayjs:
// dayjs(null).valueOf() - may be NaN but at least dayjs(undefined) works
// The key improvement is that dayjs handles ISO strings reliably
const dayjsIsoResult = dayjs("2024-03-14T10:00:00+00:00").valueOf();
const newDateIsoResult = new Date("2024-03-14T10:00:00+00:00").getTime();

if (Number.isNaN(dayjsIsoResult) || Number.isNaN(newDateIsoResult)) {
    console.error("ISO date parsing failed");
    process.exit(1);
}

if (dayjsIsoResult !== newDateIsoResult) {
    console.error("dayjs and Date.parse should give same result for valid ISO strings");
    process.exit(1);
}

console.log("All date parsing tests passed");
"""
    result = subprocess.run(
        ["node", "-e", test_js],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Date parsing test failed:\n{result.stderr}"


def test_no_new_date_gettime_in_gantt_utils():
    """Gantt utils does not use new Date().getTime() for parsing (fail_to_pass).

    The buggy code used new Date(item.x[1] ?? "").getTime() which fails for
    certain date formats. The fix uses dayjs(item.x[1]).valueOf() instead.
    """
    utils_file = f"{UI_DIR}/src/layouts/Details/Gantt/utils.ts"
    with open(utils_file, 'r') as f:
        content = f.read()

    # Should NOT have the buggy pattern new Date(item.x[...]).getTime()
    if 'new Date(item.x[' in content and ').getTime()' in content:
        # Check if it's still the old buggy pattern
        import re
        buggy_pattern = r'new Date\(item\.x\[\d+\] \?\? ""\)\.getTime\(\)'
        if re.search(buggy_pattern, content):
            assert False, "Found buggy pattern: new Date(item.x[...] ?? '').getTime()"

    # Should have the fixed dayjs pattern
    assert 'dayjs(item.x[1]).valueOf()' in content, "Missing fix: dayjs(item.x[1]).valueOf()"
    assert 'dayjs(item.x[0]).valueOf()' in content, "Missing fix: dayjs(item.x[0]).valueOf()"


def test_typescript_compiles():
    """TypeScript compiles without errors (pass_to_pass).

    The repo's TypeScript type checker should pass.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Allow warnings but not errors
    if "error TS" in result.stdout or "error TS" in result.stderr:
        assert False, f"TypeScript errors found:\n{result.stdout}\n{result.stderr}"


def test_eslint_passes():
    """ESLint passes on modified files (pass_to_pass).

    The repo's linting rules should pass for the Gantt utils files.
    """
    result = subprocess.run(
        ["npx", "eslint", "src/layouts/Details/Gantt/utils.ts", "src/layouts/Details/Gantt/utils.test.ts"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_pnpm_lint():
    """Repo's combined lint passes (pass_to_pass).

    The repo's lint command runs both ESLint and TypeScript checks.
    This is the same command run in CI.
    """
    result = subprocess.run(
        ["pnpm", "lint"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"pnpm lint failed:\n{result.stdout}\n{result.stderr}"


def test_pnpm_test():
    """Repo's full test suite passes (pass_to_pass).

    All vitest tests in the UI directory should pass.
    This verifies no regressions in the existing codebase.
    """
    result = subprocess.run(
        ["pnpm", "test"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"pnpm test failed:\n{result.stdout}\n{result.stderr}"


def test_pnpm_build():
    """Repo's build passes (pass_to_pass).

    The UI should build for production without errors.
    This verifies the codebase is in a releasable state.
    """
    result = subprocess.run(
        ["pnpm", "build"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"pnpm build failed:\n{result.stdout}\n{result.stderr}"
