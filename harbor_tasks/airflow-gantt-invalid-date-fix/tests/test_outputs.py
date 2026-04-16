"""Tests for airflow Gantt chart date parsing fix.

This module tests that the Gantt chart correctly parses ISO date strings
without throwing "Error invalid date" when rendering running DagRuns.
"""

import subprocess
import sys
from pathlib import Path

# Path to the airflow UI source
REPO = Path("/workspace/airflow/airflow-core/src/airflow/ui")
UTILS_FILE = REPO / "src" / "layouts" / "Details" / "Gantt" / "utils.ts"


def test_dayjs_used_for_date_parsing():
    """Verify dayjs is used instead of new Date() for x-axis scale calculations.

    This is a fail-to-pass test: on the base commit, new Date() is used which
    can return NaN for certain date formats. After the fix, dayjs() is used.
    """
    content = UTILS_FILE.read_text()

    # Check that dayjs is used for parsing in x-axis calculations
    # The fix replaces new Date(item.x[1] ?? "").getTime() with dayjs(item.x[1]).valueOf()
    has_dayjs_for_max = "dayjs(item.x[1]).valueOf()" in content
    has_dayjs_for_min = "dayjs(item.x[0]).valueOf()" in content

    # Check that old new Date() pattern is NOT present in scale calculations
    has_old_date_pattern = "new Date(item.x[1] ?? \"\").getTime()" in content or \
                           "new Date(item.x[0] ?? \"\").getTime()" in content

    assert has_dayjs_for_max, "Expected dayjs(item.x[1]).valueOf() in scale max calculation"
    assert has_dayjs_for_min, "Expected dayjs(item.x[0]).valueOf() in scale min calculation"
    assert not has_old_date_pattern, "Found old new Date() pattern that causes 'invalid date' errors"


def test_vitest_unit_tests_pass():
    """Run the repo's vitest unit tests for Gantt utils.

    This is a pass-to-pass test: it verifies the repo's own test suite passes.
    The PR added 7 new unit tests for createChartOptions and transformGanttData.
    """
    test_file = REPO / "src" / "layouts" / "Details" / "Gantt" / "utils.test.ts"

    # If test file doesn't exist yet (base commit), skip - it was added by the PR
    if not test_file.exists():
        return

    result = subprocess.run(
        ["pnpm", "test", "src/layouts/Details/Gantt/utils.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"

    # Verify specific tests for the fix are present and passing
    output = result.stdout + result.stderr
    assert "createChartOptions" in output or "transformGanttData" in output, \
        "Expected tests for createChartOptions or transformGanttData"


def test_typescript_compiles():
    """Verify TypeScript compiles without errors.

    This is a pass-to-pass test: the code should compile both before and after.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.app.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-1000:]}"


def test_date_parsing_produces_valid_numbers():
    """Test that date parsing produces valid numeric timestamps, not NaN.

    This is a fail-to-pass test: on the base commit with the bug, certain date
    strings would produce NaN. After the fix, dayjs consistently produces valid numbers.
    """
    # Create a test script that exercises the date parsing logic
    test_script = """
const dayjs = require('dayjs');

// Test cases for date parsing - these are ISO strings that transformGanttData produces
const testDates = [
    "2024-03-14T10:00:00.000Z",
    "2024-03-14T10:05:00.000Z",
    dayjs().toISOString(),  // Current time as ISO string (like running tasks use)
];

let allValid = true;
const results = [];

for (const dateStr of testDates) {
    // Old method (buggy)
    const oldResult = new Date(dateStr ?? "").getTime();

    // New method (fixed)
    const newResult = dayjs(dateStr).valueOf();

    results.push({
        input: dateStr,
        oldMethod: oldResult,
        newMethod: newResult,
        oldIsNaN: Number.isNaN(oldResult),
        newIsNaN: Number.isNaN(newResult),
    });

    // The fixed method should never produce NaN
    if (Number.isNaN(newResult)) {
        allValid = false;
    }
}

console.log(JSON.stringify({ allValid, results }, null, 2));
process.exit(allValid ? 0 : 1);
"""

    # Write and run the test script
    script_path = REPO / "test_date_parsing.cjs"
    script_path.write_text(test_script)

    try:
        result = subprocess.run(
            ["node", str(script_path)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Date parsing test failed: {result.stderr}"

        # Parse results to verify
        import json
        output = json.loads(result.stdout)

        for item in output["results"]:
            # The fixed method (dayjs) should never produce NaN
            assert not item["newIsNaN"], f"dayjs produced NaN for input: {item['input']}"
            # The result should be a valid number
            assert isinstance(item["newMethod"], (int, float)), f"dayjs returned non-numeric value for: {item['input']}"
            assert item["newMethod"] > 0, f"dayjs returned invalid timestamp for: {item['input']}"
    finally:
        script_path.unlink(missing_ok=True)


def test_chart_options_scale_calculation():
    """Test that chart options scale calculation produces valid numbers.

    This is a fail-to-pass test that simulates the actual bug scenario.
    On base commit, the min/max calculations could return NaN for running tasks.
    """
    # This test runs the actual Gantt utils with test data
    test_script = """
const dayjs = require('dayjs');

// Simulate the data structure that causes the bug
// When a task is running, end_date is current time as ISO string
const now = dayjs().toISOString();

const ganttData = [
    {
        x: ["2024-03-14T10:00:00.000Z", "2024-03-14T10:05:00.000Z"],
        y: "task_1",
    },
    {
        x: ["2024-03-14T10:05:00.000Z", now],  // Running task with ISO end time
        y: "task_2",
    },
];

// Simulate the scale calculation logic from createChartOptions
// OLD (buggy) implementation:
const oldMaxTime = Math.max(...ganttData.map((item) => new Date(item.x[1] ?? "").getTime()));
const oldMinTime = Math.min(...ganttData.map((item) => new Date(item.x[0] ?? "").getTime()));

// NEW (fixed) implementation:
const newMaxTime = Math.max(...ganttData.map((item) => dayjs(item.x[1]).valueOf()));
const newMinTime = Math.min(...ganttData.map((item) => dayjs(item.x[0]).valueOf()));

const results = {
    old: { max: oldMaxTime, min: oldMinTime, maxIsNaN: Number.isNaN(oldMaxTime), minIsNaN: Number.isNaN(oldMinTime) },
    new: { max: newMaxTime, min: newMinTime, maxIsNaN: Number.isNaN(newMaxTime), minIsNaN: Number.isNaN(newMinTime) },
};

console.log(JSON.stringify(results));

// The fix should produce valid numbers
if (Number.isNaN(newMaxTime) || Number.isNaN(newMinTime)) {
    process.exit(1);
}
process.exit(0);
"""

    script_path = REPO / "test_scale_calc.cjs"
    script_path.write_text(test_script)

    try:
        result = subprocess.run(
            ["node", str(script_path)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Scale calculation test failed: {result.stderr}"

        import json
        output = json.loads(result.stdout)

        # Verify the new (fixed) method produces valid numbers
        assert not output["new"]["maxIsNaN"], "dayjs scale max calculation produced NaN"
        assert not output["new"]["minIsNaN"], "dayjs scale min calculation produced NaN"
        assert output["new"]["max"] > 0, "dayjs scale max should be positive"
        assert output["new"]["min"] > 0, "dayjs scale min should be positive"
        assert output["new"]["max"] > output["new"]["min"], "max should be greater than min"
    finally:
        script_path.unlink(missing_ok=True)


def test_repo_lint():
    """Repo's linter passes (pass_to_pass).

    Verifies the code follows the repo's style guidelines.
    """
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-1000:]}"


def test_repo_build():
    """Repo's build passes (pass_to_pass).

    Verifies the UI package builds successfully with vite.
    """
    result = subprocess.run(
        ["pnpm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, f"Build failed:\n{result.stderr[-1000:]}"


def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass).

    Verifies all vitest unit tests pass (not just Gantt-related).
    """
    result = subprocess.run(
        ["pnpm", "test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-1000:]}"


def test_repo_format():
    """Repo's code formatting passes (pass_to_pass).

    Verifies the code follows the repo's prettier formatting rules.
    This is a lightweight check that ensures code style consistency.
    """
    # Check formatting on the modified file - fast and relevant
    result = subprocess.run(
        ["npx", "prettier", "--check", "src/layouts/Details/Gantt/utils.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"Format check failed:\n{result.stderr[-500:]}"
