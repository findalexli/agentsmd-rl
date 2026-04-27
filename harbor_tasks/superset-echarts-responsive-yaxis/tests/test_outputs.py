"""Behavioral tests for apache/superset PR #38673 (responsive y-axis for compact timeseries).

The oracle test file (embedded below) is dropped into the plugin's test directory
and executed via jest. Each python test function maps to one oracle assertion.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
FRONTEND = REPO / "superset-frontend"
PLUGIN_TEST_DIR = FRONTEND / "plugins/plugin-chart-echarts/test/Timeseries"
ORACLE_DST = PLUGIN_TEST_DIR / "responsive_axis.oracle.test.ts"

ORACLE_TS = r"""/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import { ChartDataResponseResult, DataRecord } from '@superset-ui/core';
import { EchartsTimeseriesChartProps } from '../../src/types';
import transformProps from '../../src/Timeseries/transformProps';
import { EchartsTimeseriesFormData } from '../../src/Timeseries/types';
import { DEFAULT_FORM_DATA } from '../../src/Timeseries/constants';
import { createEchartsTimeseriesTestChartProps } from '../helpers';
import { createTestData } from './helpers';

function makeQueryData(data: unknown[]): ChartDataResponseResult {
  return {
    annotation_data: null,
    cache_key: null,
    cache_timeout: null,
    cached_dttm: null,
    queried_dttm: null,
    data: data as DataRecord[],
    colnames: [],
    coltypes: [],
    error: null,
    is_cached: false,
    query: '',
    rowcount: data.length,
    sql_rowcount: data.length,
    stacktrace: null,
    status: 'success',
    from_dttm: null,
    to_dttm: null,
    label_map: {},
  } as ChartDataResponseResult;
}

const oracleQueriesData: ChartDataResponseResult[] = [
  makeQueryData(
    createTestData(
      [
        { 'San Francisco': 1, 'New York': 2 },
        { 'San Francisco': 3, 'New York': 4 },
      ],
      { intervalMs: 300000000 },
    ),
  ),
];

function makeProps(config: {
  formData?: Partial<EchartsTimeseriesFormData>;
  width?: number;
  height?: number;
}): EchartsTimeseriesChartProps {
  return createEchartsTimeseriesTestChartProps<
    EchartsTimeseriesFormData,
    EchartsTimeseriesChartProps
  >({
    defaultFormData: DEFAULT_FORM_DATA,
    defaultVizType: 'my_viz',
    defaultQueriesData: oracleQueriesData,
    ...config,
  });
}

test('oracle: legend visible on tall charts when enabled', () => {
  const { legend } = transformProps(
    makeProps({ height: 400, formData: { showLegend: true } }),
  ).echartOptions as any;
  expect(legend.show).toBe(true);
});

test('oracle: legend hidden on small charts even when enabled', () => {
  const { legend } = transformProps(
    makeProps({ height: 80, formData: { showLegend: true } }),
  ).echartOptions as any;
  expect(legend.show).toBe(false);
});

test('oracle: y-axis labels remain visible on small charts', () => {
  const { yAxis } = transformProps(makeProps({ height: 80 }))
    .echartOptions as any;
  expect(yAxis.axisLabel.show).toBe(true);
});

test('oracle: y-axis labels hidden on micro charts', () => {
  const { yAxis } = transformProps(makeProps({ height: 40 }))
    .echartOptions as any;
  expect(yAxis.axisLabel.show).toBe(false);
});

test('oracle: y-axis tick count scales with chart height', () => {
  const shortYAxis = transformProps(makeProps({ height: 200 })).echartOptions
    .yAxis as any;
  const tallYAxis = transformProps(makeProps({ height: 500 })).echartOptions
    .yAxis as any;
  expect(tallYAxis.splitNumber).toBeGreaterThan(shortYAxis.splitNumber);
});

test('oracle: small chart y-axis uses splitNumber=1', () => {
  const { yAxis } = transformProps(makeProps({ height: 80 }))
    .echartOptions as any;
  expect(yAxis.splitNumber).toBe(1);
});

test('oracle: zoomable small chart preserves bottom padding for slider', () => {
  const grid = transformProps(
    makeProps({ height: 80, formData: { zoomable: true } }),
  ).echartOptions.grid as any;
  expect(grid.bottom).toBeGreaterThan(5);
});

test('oracle: boundary 100px uses full axis behavior', () => {
  const { yAxis } = transformProps(makeProps({ height: 100 }))
    .echartOptions as any;
  expect(yAxis.axisLabel.show).toBe(true);
  expect(yAxis.splitNumber).toBeGreaterThanOrEqual(3);
});

test('oracle: boundary 99px triggers small chart behavior', () => {
  const { yAxis, legend } = transformProps(
    makeProps({ height: 99, formData: { showLegend: true } }),
  ).echartOptions as any;
  expect(yAxis.splitNumber).toBe(1);
  expect(legend.show).toBe(false);
});

test('oracle: boundary 60px shows labels but uses compact axis', () => {
  const { yAxis } = transformProps(makeProps({ height: 60 }))
    .echartOptions as any;
  expect(yAxis.axisLabel.show).toBe(true);
  expect(yAxis.splitNumber).toBe(1);
});

test('oracle: boundary 59px triggers micro chart behavior', () => {
  const { yAxis } = transformProps(makeProps({ height: 59 }))
    .echartOptions as any;
  expect(yAxis.axisLabel.show).toBe(false);
});

test('oracle: tall chart still produces a valid yAxis (baseline sanity)', () => {
  const result = transformProps(makeProps({ height: 600 }));
  expect(result.echartOptions).toBeDefined();
  const yAxis = (result.echartOptions as any).yAxis;
  expect(yAxis).toBeDefined();
  expect(yAxis.axisLabel).toBeDefined();
});
"""

_RESULTS: dict[str, str] | None = None


def _ensure_oracle_installed() -> None:
    if not ORACLE_DST.exists() or ORACLE_DST.read_text() != ORACLE_TS:
        ORACLE_DST.write_text(ORACLE_TS)


def _run_jest() -> dict[str, str]:
    global _RESULTS
    if _RESULTS is not None:
        return _RESULTS

    _ensure_oracle_installed()

    rel_test = "plugins/plugin-chart-echarts/test/Timeseries/responsive_axis.oracle.test.ts"
    out_path = Path("/tmp/oracle_jest_out.json")
    if out_path.exists():
        out_path.unlink()

    env = os.environ.copy()
    env["CI"] = "1"
    proc = subprocess.run(
        [
            "npx", "jest",
            rel_test,
            "--json",
            f"--outputFile={out_path}",
        ],
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )

    if not out_path.exists():
        raise RuntimeError(
            f"jest did not produce {out_path}. exit={proc.returncode}\n"
            f"STDOUT:\n{proc.stdout[-3000:]}\nSTDERR:\n{proc.stderr[-3000:]}"
        )

    data = json.loads(out_path.read_text())
    by_title: dict[str, str] = {}
    for ts in data.get("testResults", []):
        for assertion in ts.get("assertionResults", []):
            by_title[assertion["title"]] = assertion["status"]

    _RESULTS = by_title
    return _RESULTS


def _check(title: str) -> None:
    results = _run_jest()
    assert title in results, (
        f"oracle test {title!r} not found. Got: {sorted(results.keys())}"
    )
    status = results[title]
    assert status == "passed", f"oracle test {title!r} status={status}"


# --- f2p: behavioral oracles for responsive y-axis ---

def test_legend_visible_on_tall_charts():
    _check("oracle: legend visible on tall charts when enabled")


def test_legend_hidden_on_small_charts():
    _check("oracle: legend hidden on small charts even when enabled")


def test_yaxis_labels_visible_on_small_charts():
    _check("oracle: y-axis labels remain visible on small charts")


def test_yaxis_labels_hidden_on_micro_charts():
    _check("oracle: y-axis labels hidden on micro charts")


def test_yaxis_tick_count_scales_with_height():
    _check("oracle: y-axis tick count scales with chart height")


def test_small_chart_uses_splitnumber_one():
    _check("oracle: small chart y-axis uses splitNumber=1")


def test_zoomable_small_chart_preserves_bottom_padding():
    _check("oracle: zoomable small chart preserves bottom padding for slider")


def test_boundary_100px_full_axis():
    _check("oracle: boundary 100px uses full axis behavior")


def test_boundary_99px_small_chart():
    _check("oracle: boundary 99px triggers small chart behavior")


def test_boundary_60px_compact_axis_with_labels():
    _check("oracle: boundary 60px shows labels but uses compact axis")


def test_boundary_59px_micro_chart():
    _check("oracle: boundary 59px triggers micro chart behavior")


# --- p2p: pre-existing transformProps tests must still pass ---

def test_existing_transformprops_baseline():
    """Sanity oracle test that always passes on a working build."""
    _check("oracle: tall chart still produces a valid yAxis (baseline sanity)")


def test_repo_existing_transformprops_suite_passes():
    """The repository's own transformProps.test.ts (non-oracle) must still pass."""
    rel = "plugins/plugin-chart-echarts/test/Timeseries/transformProps.test.ts"
    proc = subprocess.run(
        ["npx", "jest", rel, "--ci"],
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"existing transformProps.test.ts suite failed (exit={proc.returncode}).\n"
        f"STDERR tail:\n{proc.stderr[-1500:]}"
    )
