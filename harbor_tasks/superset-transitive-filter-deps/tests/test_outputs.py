"""Behavioral oracle for apache/superset#39504.

The fail-to-pass test runs a small jest test (written out at runtime under
the superset-frontend `spec/` directory) that exercises the public hook
`useFilterDependencies` against a multi-level filter dependency chain. The
buggy base implementation only walks the direct `cascadeParentIds` of a
filter and so omits transitive ancestors from the merged
`extra_form_data`. The corrected implementation walks the full transitive
ancestor chain in topological order.

The pass-to-pass test runs the upstream test that already lived in this
area of the codebase (`FilterControls.test.tsx`) to guard against
regressions in adjacent behavior.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
FRONTEND = REPO / "superset-frontend"
ORACLE_DST = FRONTEND / "spec" / "__oracle_transitive_chain.test.ts"

ORACLE_TS_SOURCE = r"""/**
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
import { renderHook } from '@testing-library/react-hooks';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import { createElement } from 'react';
import type { ReactNode } from 'react';
import type { DataMaskStateWithId } from '@superset-ui/core';
import { useFilterDependencies } from 'src/dashboard/components/nativeFilters/FilterBar/FilterControls/state';

type CascadeMap = Record<string, { cascadeParentIds?: string[] }>;

const mockStore = configureStore([]);

const buildWrapper = (filters: CascadeMap) => {
  const store = mockStore({ nativeFilters: { filters } });
  return ({ children }: { children: ReactNode }) =>
    createElement(Provider, { store }, children);
};

test('linear A->B->C->D chain merges all ancestor filters into D on first apply', () => {
  const wrapper = buildWrapper({
    A: { cascadeParentIds: [] },
    B: { cascadeParentIds: ['A'] },
    C: { cascadeParentIds: ['B'] },
    D: { cascadeParentIds: ['C'] },
  });
  const dataMaskSelected: DataMaskStateWithId = {
    A: {
      id: 'A',
      extraFormData: { filters: [{ col: 'country', op: 'IN', val: ['US'] }] },
    },
    B: {
      id: 'B',
      extraFormData: { filters: [{ col: 'region', op: 'IN', val: ['West'] }] },
    },
    C: {
      id: 'C',
      extraFormData: { filters: [{ col: 'state', op: 'IN', val: ['CA'] }] },
    },
  };
  const { result } = renderHook(
    () => useFilterDependencies('D', dataMaskSelected),
    { wrapper },
  );
  const cols = (result.current.filters ?? []).map((f: any) => f.col);
  expect(cols).toEqual(expect.arrayContaining(['country', 'region', 'state']));
  expect(result.current.filters ?? []).toHaveLength(3);
});

test('diamond ancestor graph deduplicates the shared root', () => {
  const wrapper = buildWrapper({
    A: { cascadeParentIds: [] },
    B: { cascadeParentIds: ['A'] },
    C: { cascadeParentIds: ['A'] },
    D: { cascadeParentIds: ['B', 'C'] },
  });
  const dataMaskSelected: DataMaskStateWithId = {
    A: {
      id: 'A',
      extraFormData: { filters: [{ col: 'country', op: 'IN', val: ['US'] }] },
    },
    B: {
      id: 'B',
      extraFormData: { filters: [{ col: 'region', op: 'IN', val: ['West'] }] },
    },
    C: {
      id: 'C',
      extraFormData: { filters: [{ col: 'state', op: 'IN', val: ['CA'] }] },
    },
  };
  const { result } = renderHook(
    () => useFilterDependencies('D', dataMaskSelected),
    { wrapper },
  );
  const cols = (result.current.filters ?? []).map((f: any) => f.col);
  expect(cols).toEqual(expect.arrayContaining(['country', 'region', 'state']));
  expect(cols.filter((c: string) => c === 'country')).toHaveLength(1);
  expect(result.current.filters ?? []).toHaveLength(3);
});

test('closest ancestor wins for scalar fields like time_range', () => {
  const wrapper = buildWrapper({
    A: { cascadeParentIds: [] },
    B: { cascadeParentIds: ['A'] },
    C: { cascadeParentIds: ['B'] },
  });
  const dataMaskSelected: DataMaskStateWithId = {
    A: {
      id: 'A',
      extraFormData: { time_range: 'Last year' },
    },
    B: {
      id: 'B',
      extraFormData: { time_range: 'Last month' },
    },
  };
  const { result } = renderHook(
    () => useFilterDependencies('C', dataMaskSelected),
    { wrapper },
  );
  expect(result.current.time_range).toBe('Last month');
});

test('cyclic config does not loop forever and produces a finite ancestor set', () => {
  const wrapper = buildWrapper({
    A: { cascadeParentIds: ['B'] },
    B: { cascadeParentIds: ['A'] },
  });
  const dataMaskSelected: DataMaskStateWithId = {
    B: {
      id: 'B',
      extraFormData: { filters: [{ col: 'k', op: 'IN', val: ['v'] }] },
    },
  };
  const { result } = renderHook(
    () => useFilterDependencies('A', dataMaskSelected),
    { wrapper },
  );
  expect(typeof result.current).toBe('object');
});
"""


def _install_oracle() -> None:
    """Write the oracle jest test into the jest-tracked tree."""
    ORACLE_DST.parent.mkdir(parents=True, exist_ok=True)
    ORACLE_DST.write_text(ORACLE_TS_SOURCE)


def _run_jest(test_path_pattern: str, timeout: int = 600) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    env["CI"] = "1"
    env["TZ"] = "America/New_York"
    return subprocess.run(
        [
            "npx",
            "jest",
            "--no-coverage",
            "--colors=false",
            "--runInBand",
            "--testPathPatterns",
            test_path_pattern,
        ],
        cwd=str(FRONTEND),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_full_transitive_chain_oracle():
    """Fail-to-pass: oracle jest tests for full ancestor chain merging."""
    _install_oracle()
    r = _run_jest("__oracle_transitive_chain", timeout=600)
    assert r.returncode == 0, (
        "Oracle jest tests failed.\n"
        f"--- stdout (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_filtercontrols_existing_jest_suite_passes():
    """Pass-to-pass: the existing FilterControls jest suite must still pass.

    This is a real upstream test in the same area of the codebase, present
    on the base commit. Guards against regressions in unrelated
    FilterControls behavior.
    """
    r = _run_jest(
        "FilterControls/FilterControls\\.test\\.",
        timeout=900,
    )
    assert r.returncode == 0, (
        "Upstream FilterControls.test.tsx failed (regression).\n"
        f"--- stdout (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )
