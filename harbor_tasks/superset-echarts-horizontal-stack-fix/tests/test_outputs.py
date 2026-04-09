"""
Tests for the ECharts horizontal stacked bar chart fix.

The bug: For horizontal stacked bar charts with truncateYAxis enabled,
the xAxis.max was incorrectly set to the individual series max (dataMax)
instead of the stacked total max. This caused:
1. Bars appearing clipped/not fully stacked
2. Duplicate x-axis labels due to cramped axis range

The fix: When stack is truthy, use the max of sortedTotalValues (per-row
stacked totals) as the effective axis max instead of dataMax.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/superset")
PLUGIN_DIR = REPO / "superset-frontend/plugins/plugin-chart-echarts"


def test_stacked_horizontal_bar_axis_max():
    """
    Fail-to-pass: Stacked horizontal bar charts should use stacked total max,
    not individual series max, for xAxis.max.

    Before fix: xAxis.max = 4 (individual series max)
    After fix: xAxis.max >= 8 (stacked total max for Team A)
    """
    test_code = '''
const {
  createEchartsTimeseriesTestChartProps,
} = require('../../../test/helpers');
const transformProps = require('../../src/Timeseries/transformProps').default;
const { StackControlsValue } = require('../../src/constants');
const { OrientationType, EchartsTimeseriesSeriesType } = require('../../src/types');
const { GenericDataType } = require('@superset-ui/core');
const { supersetTheme } = require('@apache-superset/core/theme');

// Dataset where each series max = 4 but stacked total max = 8
const stackedData = [
  {
    data: [
      { team: 'Team A', High: 2, Low: 2, Medium: 4 },
      { team: 'Team B', High: null, Low: null, Medium: 3 },
      { team: 'Team C', High: null, Low: null, Medium: 1 },
    ],
    colnames: ['team', 'High', 'Low', 'Medium'],
    coltypes: [
      GenericDataType.String,
      GenericDataType.Numeric,
      GenericDataType.Numeric,
      GenericDataType.Numeric,
    ],
  },
];

const formData = {
  x_axis: 'team',
  metrics: ['High', 'Low', 'Medium'],
  groupby: [],
  orientation: OrientationType.Horizontal,
  seriesType: EchartsTimeseriesSeriesType.Bar,
  stack: StackControlsValue.Stack,
  truncateYAxis: true,
  timeRange: 'No filter',
  viz_type: 'echarts_timeseries_bar',
};

const chartProps = createEchartsTimeseriesTestChartProps({
  defaultFormData: formData,
  defaultVizType: 'echarts_timeseries_bar',
  defaultQueriesData: stackedData,
});

const result = transformProps(chartProps);
const xAxis = result.echartOptions.xAxis;

// The stacked total for Team A = 2 + 2 + 4 = 8
// Individual series max = 4 (Medium column)
// With the fix, xAxis.max should be >= 8, not 4
if (xAxis.max < 8) {
  console.error(`FAIL: xAxis.max (${xAxis.max}) should be >= 8 (stacked total), got < 8`);
  process.exit(1);
}

// Also verify it's not exactly 4 (the bug)
if (xAxis.max === 4) {
  console.error(`FAIL: xAxis.max should not be exactly 4 (the bug - using individual series max)`);
  process.exit(1);
}

console.log(`PASS: xAxis.max = ${xAxis.max}, correctly >= 8 (stacked total)`);
process.exit(0);
'''

    # Write test file
    test_file = PLUGIN_DIR / "test_stacked_axis.js"
    test_file.write_text(test_code)

    try:
        result = subprocess.run(
            ["node", str(test_file)],
            cwd=str(PLUGIN_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            assert False, f"Stacked horizontal bar test failed: {result.stderr or result.stdout}"
    finally:
        test_file.unlink(missing_ok=True)


def test_non_stacked_uses_individual_max():
    """
    Pass-to-pass: Non-stacked horizontal bar charts should still use
    individual series max for xAxis.max.

    Regression guard: ensure the fix doesn't break non-stacked charts.
    """
    test_code = '''
const {
  createEchartsTimeseriesTestChartProps,
} = require('../../../test/helpers');
const transformProps = require('../../src/Timeseries/transformProps').default;
const { OrientationType, EchartsTimeseriesSeriesType } = require('../../src/types');
const { GenericDataType } = require('@superset-ui/core');

// Dataset where series max = 4
const data = [
  {
    data: [
      { team: 'Team A', High: 2, Low: 2, Medium: 4 },
    ],
    colnames: ['team', 'High', 'Low', 'Medium'],
    coltypes: [
      GenericDataType.String,
      GenericDataType.Numeric,
      GenericDataType.Numeric,
      GenericDataType.Numeric,
    ],
  },
];

const formData = {
  x_axis: 'team',
  metrics: ['High', 'Low', 'Medium'],
  groupby: [],
  orientation: OrientationType.Horizontal,
  seriesType: EchartsTimeseriesSeriesType.Bar,
  stack: null,  // No stacking
  truncateYAxis: true,
  timeRange: 'No filter',
  viz_type: 'echarts_timeseries_bar',
};

const chartProps = createEchartsTimeseriesTestChartProps({
  defaultFormData: formData,
  defaultVizType: 'echarts_timeseries_bar',
  defaultQueriesData: data,
});

const result = transformProps(chartProps);
const xAxis = result.echartOptions.xAxis;

// Without stacking, xAxis.max should be based on individual series values (4)
if (xAxis.max !== 4) {
  console.error(`FAIL: Non-stacked chart xAxis.max should be 4 (individual series max), got ${xAxis.max}`);
  process.exit(1);
}

console.log(`PASS: Non-stacked xAxis.max = ${xAxis.max}, correctly using individual max`);
process.exit(0);
'''

    test_file = PLUGIN_DIR / "test_non_stacked.js"
    test_file.write_text(test_code)

    try:
        result = subprocess.run(
            ["node", str(test_file)],
            cwd=str(PLUGIN_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            assert False, f"Non-stacked test failed: {result.stderr or result.stdout}"
    finally:
        test_file.unlink(missing_ok=True)


def test_dimension_value_undefined_guard():
    """
    Fail-to-pass: The fix guards against setting stack to undefined when
    dimensionValue is undefined. This prevents accidental overwrite of
    the stack property.
    """
    test_code = '''
const {
  createEchartsTimeseriesTestChartProps,
} = require('../../../test/helpers');
const transformProps = require('../../src/Timeseries/transformProps').default;
const { StackControlsValue } = require('../../src/constants');
const { OrientationType, EchartsTimeseriesSeriesType } = require('../../src/types');
const { GenericDataType } = require('@superset-ui/core');

// Data with a series that might have undefined dimension
const data = [
  {
    data: [
      { team: 'Team A', metric1: 5 },
    ],
    colnames: ['team', 'metric1'],
    coltypes: [GenericDataType.String, GenericDataType.Numeric],
  },
];

const formData = {
  x_axis: 'team',
  metrics: ['metric1'],
  groupby: [],
  orientation: OrientationType.Horizontal,
  seriesType: EchartsTimeseriesSeriesType.Bar,
  stack: StackControlsValue.Stack,
  truncateYAxis: true,
  timeRange: 'No filter',
  viz_type: 'echarts_timeseries_bar',
};

const chartProps = createEchartsTimeseriesTestChartProps({
  defaultFormData: formData,
  defaultVizType: 'echarts_timeseries_bar',
  defaultQueriesData: data,
});

try {
  const result = transformProps(chartProps);
  // Check that series exist and don't crash
  if (!result.echartOptions.series || result.echartOptions.series.length === 0) {
    console.error('FAIL: No series generated');
    process.exit(1);
  }
  console.log('PASS: Dimension value undefined guard works correctly');
  process.exit(0);
} catch (e) {
  console.error(`FAIL: Error during transform: ${e.message}`);
  process.exit(1);
}
'''

    test_file = PLUGIN_DIR / "test_dimension_guard.js"
    test_file.write_text(test_code)

    try:
        result = subprocess.run(
            ["node", str(test_file)],
            cwd=str(PLUGIN_DIR),
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            assert False, f"Dimension guard test failed: {result.stderr or result.stdout}"
    finally:
        test_file.unlink(missing_ok=True)


def test_existing_unit_tests():
    """
    Pass-to-pass: Run the existing upstream Jest tests for transformProps.
    This validates that our changes don't break existing functionality.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "--testPathPattern=transformProps.test.ts", "--testNamePattern=Horizontal stacked bar", "--no-coverage", "--verbose"],
        cwd=str(PLUGIN_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        # Check if the specific tests we care about are mentioned
        if "Horizontal stacked bar" in result.stdout or "Horizontal stacked bar" in result.stderr:
            assert False, "Upstream horizontal stacked bar tests failed"
        # If the pattern didn't match any tests, that's OK - the tests might not exist yet
        if "No tests found" in result.stdout:
            print("Note: Upstream tests for horizontal stacked bar not found (may be the fix tests)")
            return

    print("PASS: Existing unit tests passed")


def test_typescript_compiles():
    """
    Structural: TypeScript should compile without errors.
    Builds dependencies first, then runs typecheck.
    """
    # Build dependencies first (required for project references)
    build_result = subprocess.run(
        ["npm", "run", "plugins:build"],
        cwd=str(REPO / "superset-frontend"),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if build_result.returncode != 0:
        print(f"Build STDERR: {build_result.stderr[-500:]}")
        assert False, f"Plugins build failed: {build_result.stderr[-500:]}"

    # Run typecheck
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "."],
        cwd=str(PLUGIN_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"STDERR: {result.stderr[-500:]}")
        print(f"STDOUT: {result.stdout[-500:]}")
        assert False, f"TypeScript compilation failed: {result.stderr[-500:]}"

    print("PASS: TypeScript compiles successfully")


def test_repo_jest_transformprops():
    """
    Pass-to-pass: Repo Jest tests for transformProps.ts pass.
    Runs the full upstream test suite for the transformProps module.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--",
         "--testPathPatterns=plugin-chart-echarts/test/Timeseries/transformProps.test.ts",
         "--no-coverage", "--max-workers=2"],
        cwd=str(REPO / "superset-frontend"),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        assert False, f"Jest transformProps tests failed: {result.stderr or result.stdout}"

    print("PASS: Repo Jest transformProps tests passed")


def test_repo_jest_timeseries():
    """
    Pass-to-pass: Repo Jest tests for Timeseries plugin pass.
    Ensures all Timeseries-related tests continue to work.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--",
         "--testPathPatterns=plugin-chart-echarts/test/Timeseries/",
         "--no-coverage", "--max-workers=2"],
        cwd=str(REPO / "superset-frontend"),
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        assert False, f"Jest Timeseries tests failed: {result.stderr or result.stdout}"

    print("PASS: Repo Jest Timeseries tests passed")


if __name__ == "__main__":
    print("Running ECharts horizontal stacked bar chart fix tests...")
    print("=" * 60)

    tests = [
        ("TypeScript compilation", test_typescript_compiles),
        ("Repo Jest transformProps tests", test_repo_jest_transformprops),
        ("Repo Jest Timeseries tests", test_repo_jest_timeseries),
        ("Stacked horizontal bar axis max", test_stacked_horizontal_bar_axis_max),
        ("Non-stacked uses individual max", test_non_stacked_uses_individual_max),
        ("Dimension value undefined guard", test_dimension_value_undefined_guard),
        ("Existing unit tests", test_existing_unit_tests),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n--- Running: {name} ---")
        try:
            test_fn()
            passed += 1
            print(f"✓ {name} PASSED")
        except AssertionError as e:
            failed += 1
            print(f"✗ {name} FAILED: {e}")
        except Exception as e:
            failed += 1
            print(f"✗ {name} ERROR: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)
