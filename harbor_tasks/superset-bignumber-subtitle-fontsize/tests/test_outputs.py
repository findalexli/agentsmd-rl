"""Behavioral oracle for apache/superset#39493.

The PR fixes the default font size for the Big Number chart's
subtitle/subheader and adds a fallback chain. We run an authored Jest
test (written into the repo at runtime) that exercises
BigNumberTotal/transformProps.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
FRONTEND = REPO / "superset-frontend"
PLUGIN_TEST_DIR = (
    FRONTEND
    / "plugins"
    / "plugin-chart-echarts"
    / "test"
    / "BigNumber"
)
ORACLE_TEST_NAME = "BigNumberTotal_subtitleFontSize.test.ts"
ORACLE_TEST_DST = PLUGIN_TEST_DIR / ORACLE_TEST_NAME
ORACLE_RELPATH = (
    "plugins/plugin-chart-echarts/test/BigNumber/"
    + ORACLE_TEST_NAME
)

JEST_ENV = {
    **os.environ,
    "NODE_OPTIONS": "--max-old-space-size=4096",
    "TZ": "America/New_York",
    "CI": "true",
}

# The Jest oracle. It exercises BigNumberTotal's transformProps via
# its public TypeScript API (no source inspection / grep) so a fix
# that produces the right behavioural output passes regardless of the
# exact code shape used.
ORACLE_TEST_SOURCE = r"""/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 */
import { DatasourceType, VizType } from '@superset-ui/core';
import { supersetTheme } from '@apache-superset/core/theme';
import transformProps from '../../src/BigNumber/BigNumberTotal/transformProps';
import {
  BigNumberDatum,
  BigNumberTotalChartProps,
  BigNumberTotalFormData,
} from '../../src/BigNumber/types';

const baseFormData = {
  metric: 'value',
  viz_type: VizType.BigNumberTotal,
  yAxisFormat: '.3s',
  datasource: 'test_datasource',
};

const baseRawFormData: BigNumberTotalFormData = {
  datasource: '1__table',
  metric: 'value',
  viz_type: VizType.BigNumberTotal,
  y_axis_format: '.3s',
};

function makeProps(
  data: BigNumberDatum[],
  extraFormData: Partial<BigNumberTotalFormData> = {},
): BigNumberTotalChartProps {
  return {
    width: 200,
    height: 500,
    annotationData: {},
    datasource: {
      id: 0,
      name: '',
      type: DatasourceType.Table,
      columns: [],
      metrics: [],
      columnFormats: {},
      currencyFormats: {},
      verboseMap: {},
    },
    rawDatasource: {},
    rawFormData: baseRawFormData,
    hooks: {},
    initialValues: {},
    formData: {
      ...baseFormData,
      ...extraFormData,
    } as BigNumberTotalFormData,
    queriesData: [
      {
        data,
      },
    ],
    ownState: {},
    filterState: {},
    behaviors: [],
    theme: supersetTheme,
  } as unknown as BigNumberTotalChartProps;
}

describe('BigNumberTotal transformProps subtitle font size', () => {
  test('default subtitle font size is 0.125 when nothing is configured', () => {
    const transformed = transformProps(
      makeProps([{ value: 42 }]),
    );
    expect(transformed.subtitleFontSize).toBeCloseTo(0.125);
    expect(transformed.subtitleFontSize).not.toBe(1);
  });

  test('default subtitle font size is 0.125 when subtitle is set without font size', () => {
    const transformed = transformProps(
      makeProps([{ value: 42 }], {
        subtitle: 'A subtitle',
      } as Partial<BigNumberTotalFormData>),
    );
    expect(transformed.subtitleFontSize).toBeCloseTo(0.125);
    expect(transformed.subtitleFontSize).not.toBe(1);
  });

  test('default subtitle font size is 0.125 when subheader is set without font size', () => {
    const transformed = transformProps(
      makeProps([{ value: 42 }], {
        subheader: 'A subheader',
      } as Partial<BigNumberTotalFormData>),
    );
    expect(transformed.subtitleFontSize).toBeCloseTo(0.125);
    expect(transformed.subtitleFontSize).not.toBe(1);
  });

  test('falls back to subtitleFontSize when subheader is set but only subtitleFontSize is provided', () => {
    const transformed = transformProps(
      makeProps([{ value: 42 }], {
        subheader: 'Legacy subheader',
        subtitleFontSize: 0.4,
      } as Partial<BigNumberTotalFormData>),
    );
    expect(transformed.subtitleFontSize).toBeCloseTo(0.4);
  });

  test('respects an explicit subheaderFontSize when subtitle is empty', () => {
    const transformed = transformProps(
      makeProps([{ value: 42 }], {
        subheader: 'Legacy subheader',
        subheaderFontSize: 0.2,
      } as Partial<BigNumberTotalFormData>),
    );
    expect(transformed.subtitleFontSize).toBeCloseTo(0.2);
  });

  test('respects an explicit subtitleFontSize when subtitle is non-empty', () => {
    const transformed = transformProps(
      makeProps([{ value: 42 }], {
        subtitle: 'A subtitle',
        subtitleFontSize: 0.5,
      } as Partial<BigNumberTotalFormData>),
    );
    expect(transformed.subtitleFontSize).toBeCloseTo(0.5);
  });
});
"""


def _install_oracle_test():
    PLUGIN_TEST_DIR.mkdir(parents=True, exist_ok=True)
    ORACLE_TEST_DST.write_text(ORACLE_TEST_SOURCE, encoding="utf-8")


_ORACLE_INSTALLED = False


def _ensure_oracle():
    global _ORACLE_INSTALLED
    if not _ORACLE_INSTALLED:
        _install_oracle_test()
        _ORACLE_INSTALLED = True


def _run_jest(test_relpath: str, name_filter: str | None = None, timeout: int = 600):
    cmd = [
        "npx",
        "jest",
        "--max-workers=2",
        "--colors=false",
        "--json",
        test_relpath,
    ]
    if name_filter is not None:
        cmd.extend(["-t", name_filter])
    return subprocess.run(
        cmd,
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=JEST_ENV,
    )


def _parse_jest_json(proc):
    raw = proc.stdout + "\n" + proc.stderr
    text = proc.stdout.strip()
    last_brace = text.rfind("{")
    while last_brace >= 0:
        candidate = text[last_brace:]
        try:
            return json.loads(candidate), raw
        except json.JSONDecodeError:
            last_brace = text.rfind("{", 0, last_brace)
    return None, raw


def _assert_jest_test_passed(proc, full_test_name: str):
    data, raw = _parse_jest_json(proc)
    assert data is not None, f"Could not parse jest JSON output:\n{raw[-3000:]}"
    matched = []
    for suite in data.get("testResults", []):
        for assertion in suite.get("assertionResults", []):
            title = assertion.get("fullName") or assertion.get("title") or ""
            if full_test_name in title:
                matched.append((title, assertion.get("status")))
    assert matched, (
        f"Jest test named '{full_test_name}' was not found.\n"
        f"Output tail:\n{raw[-1500:]}"
    )
    for title, status in matched:
        assert status == "passed", (
            f"Jest test '{title}' status={status}\nOutput tail:\n{raw[-1500:]}"
        )


# ---- Fail-to-pass tests ------------------------------------------------


def test_default_font_size_when_unconfigured():
    """Default subtitle font size must be PROPORTION.SUBHEADER (0.125), not 1."""
    _ensure_oracle()
    proc = _run_jest(
        ORACLE_RELPATH,
        name_filter="default subtitle font size is 0.125 when nothing is configured",
    )
    _assert_jest_test_passed(
        proc,
        "default subtitle font size is 0.125 when nothing is configured",
    )


def test_default_font_size_with_subtitle_only():
    """When subtitle is set but no font size, default to PROPORTION.SUBHEADER."""
    _ensure_oracle()
    proc = _run_jest(
        ORACLE_RELPATH,
        name_filter="default subtitle font size is 0.125 when subtitle is set without font size",
    )
    _assert_jest_test_passed(
        proc,
        "default subtitle font size is 0.125 when subtitle is set without font size",
    )


def test_default_font_size_with_subheader_only():
    """When subheader is set but no font size, default to PROPORTION.SUBHEADER."""
    _ensure_oracle()
    proc = _run_jest(
        ORACLE_RELPATH,
        name_filter="default subtitle font size is 0.125 when subheader is set without font size",
    )
    _assert_jest_test_passed(
        proc,
        "default subtitle font size is 0.125 when subheader is set without font size",
    )


def test_fallback_chain_subheader_field_uses_subtitle_size():
    """When only the legacy subheader text field is populated and only
    subtitleFontSize is supplied, the resolved font size must come from
    subtitleFontSize. This is the defining behaviour of the new
    fallback chain introduced by the fix."""
    _ensure_oracle()
    proc = _run_jest(
        ORACLE_RELPATH,
        name_filter="falls back to subtitleFontSize when subheader is set but only subtitleFontSize is provided",
    )
    _assert_jest_test_passed(
        proc,
        "falls back to subtitleFontSize when subheader is set but only subtitleFontSize is provided",
    )


# ---- Pass-to-pass tests ------------------------------------------------


def test_explicit_subheader_font_size_respected():
    """An explicit subheaderFontSize must still be respected."""
    _ensure_oracle()
    proc = _run_jest(
        ORACLE_RELPATH,
        name_filter="respects an explicit subheaderFontSize when subtitle is empty",
    )
    _assert_jest_test_passed(
        proc,
        "respects an explicit subheaderFontSize when subtitle is empty",
    )


def test_explicit_subtitle_font_size_respected():
    """An explicit subtitleFontSize must still be respected."""
    _ensure_oracle()
    proc = _run_jest(
        ORACLE_RELPATH,
        name_filter="respects an explicit subtitleFontSize when subtitle is non-empty",
    )
    _assert_jest_test_passed(
        proc,
        "respects an explicit subtitleFontSize when subtitle is non-empty",
    )


def test_existing_bignumber_with_trendline_transformprops():
    """The pre-existing BigNumberWithTrendline transformProps test
    suite must keep passing — guards against unrelated regressions."""
    proc = _run_jest(
        "plugins/plugin-chart-echarts/test/BigNumber/transformProps.test.ts",
        timeout=600,
    )
    assert proc.returncode == 0, (
        "Pre-existing transformProps test failed:\n"
        f"stdout tail:\n{proc.stdout[-1500:]}\n"
        f"stderr tail:\n{proc.stderr[-1500:]}"
    )
