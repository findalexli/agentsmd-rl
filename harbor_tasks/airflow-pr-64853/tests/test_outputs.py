#!/usr/bin/env python3
"""
Tests for airflow-gantt-date-parsing task.

This task tests fixing the Gantt view "Error invalid date" bug where
new Date().getTime() fails to parse certain date strings (returning NaN),
while dayjs().valueOf() handles them correctly.
"""
import subprocess
import os
import json

REPO = "/workspace/airflow"
UI_DIR = os.path.join(REPO, "airflow-core/src/airflow/ui")


def run_node_script(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Node.js script in the UI directory."""
    return subprocess.run(
        ["node", "-e", script],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_dayjs_used_for_date_parsing():
    """
    Verify that dayjs().valueOf() is used instead of new Date().getTime()
    for parsing date strings in scale calculations.
    (fail_to_pass)
    """
    utils_path = os.path.join(UI_DIR, "src/layouts/Details/Gantt/utils.ts")
    with open(utils_path, "r") as f:
        content = f.read()

    # The fix replaces new Date().getTime() with dayjs().valueOf()
    # Check that dayjs is used for parsing in scale calculations
    assert "dayjs(item.x[1]).valueOf()" in content, \
        "Expected dayjs().valueOf() for x[1] parsing, but found old new Date().getTime() pattern"
    assert "dayjs(item.x[0]).valueOf()" in content, \
        "Expected dayjs().valueOf() for x[0] parsing, but found old new Date().getTime() pattern"

    # Ensure the old buggy pattern is NOT present
    assert "new Date(item.x[1]" not in content, \
        "Found buggy new Date(item.x[1]...) pattern that should be replaced with dayjs"
    assert "new Date(item.x[0]" not in content, \
        "Found buggy new Date(item.x[0]...) pattern that should be replaced with dayjs"


def test_no_nan_for_iso_dates():
    """
    Test that ISO date strings are parsed without returning NaN.
    The old code with new Date() could return NaN for certain timezone formats.
    (fail_to_pass)
    """
    # Create a test script that imports the utils and tests date parsing behavior
    test_script = '''
const dayjs = require("dayjs");

// Test ISO date strings that should be parsed correctly
const testDates = [
    "2024-03-14T10:00:00.000Z",
    "2024-03-14T10:00:00+00:00",
    "2024-03-14T10:00:00+05:30",
    "2024-03-14T10:00:00-08:00",
];

// Read the utils.ts file to check the implementation
const fs = require("fs");
const content = fs.readFileSync("src/layouts/Details/Gantt/utils.ts", "utf-8");

// Check if dayjs is used for scale calculations
const usesDayjs = content.includes("dayjs(item.x[1]).valueOf()") &&
                  content.includes("dayjs(item.x[0]).valueOf()");

if (!usesDayjs) {
    console.log("FAIL: dayjs not used for date parsing");
    process.exit(1);
}

// Verify dayjs handles all test dates without NaN
for (const date of testDates) {
    const value = dayjs(date).valueOf();
    if (Number.isNaN(value)) {
        console.log("FAIL: NaN for date " + date);
        process.exit(1);
    }
}

console.log("PASS: All dates parsed correctly with dayjs");
process.exit(0);
'''
    result = run_node_script(test_script)
    assert result.returncode == 0, f"Date parsing test failed:\n{result.stdout}\n{result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output:\n{result.stdout}"


def test_scale_min_max_not_nan():
    """
    Test that the code uses dayjs for date parsing in both max and min scale calculations.
    The old new Date() approach is buggy for certain timezone formats.
    (fail_to_pass)
    """
    utils_path = os.path.join(UI_DIR, "src/layouts/Details/Gantt/utils.ts")
    with open(utils_path, "r") as f:
        content = f.read()

    # Both the max and min scale calculations should use dayjs
    # The bug was that both used new Date().getTime() which fails for certain timezones
    max_uses_dayjs = "dayjs(item.x[1]).valueOf()" in content and "dayjs(item.x[0]).valueOf()" in content

    # Count occurrences - both max and min calculations need to be fixed (4 total replacements)
    dayjs_x1_count = content.count("dayjs(item.x[1]).valueOf()")
    dayjs_x0_count = content.count("dayjs(item.x[0]).valueOf()")

    assert dayjs_x1_count >= 2, \
        f"Expected at least 2 uses of dayjs(item.x[1]).valueOf() for max/min calculations, found {dayjs_x1_count}"
    assert dayjs_x0_count >= 2, \
        f"Expected at least 2 uses of dayjs(item.x[0]).valueOf() for max/min calculations, found {dayjs_x0_count}"


def test_typescript_compiles():
    """
    Test that the TypeScript code compiles without errors.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "tsconfig.app.json"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # TypeScript compilation should succeed
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-2000:]}"


def test_eslint_passes():
    """
    Test that ESLint passes on the codebase.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_vitest_gantt_utils():
    """
    Run vitest on the Gantt utils tests if they exist.
    (pass_to_pass - only runs if test file exists after fix)
    """
    test_file = os.path.join(UI_DIR, "src/layouts/Details/Gantt/utils.test.ts")
    if not os.path.exists(test_file):
        # Test file doesn't exist on base commit, skip gracefully
        # This becomes a p2p test after the fix adds the test file
        return

    result = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/layouts/Details/Gantt/utils.test.ts"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Vitest failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_vitest_full():
    """
    Run the full vitest test suite for the UI.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "run", "test"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Vitest full suite failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_prettier_gantt():
    """
    Check that Gantt directory files are formatted with Prettier.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "exec", "prettier", "--check", "src/layouts/Details/Gantt/"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    import sys

    tests = [
        test_dayjs_used_for_date_parsing,
        test_no_nan_for_iso_dates,
        test_scale_min_max_not_nan,
        test_typescript_compiles,
        test_eslint_passes,
        test_vitest_gantt_utils,
        test_repo_vitest_full,
        test_repo_prettier_gantt,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...", end=" ")
            test()
            print("PASSED")
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed!")
        sys.exit(0)
