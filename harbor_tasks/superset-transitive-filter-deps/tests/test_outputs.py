"""Behavioral oracle for apache/superset#39504.

The fail-to-pass tests run jest tests (written out at runtime under the
superset-frontend `spec/` directory) that exercise the public hook
`useFilterDependencies` against multi-level filter dependency chains. The
buggy base implementation only walks the direct `cascadeParentIds` of a
filter and so omits transitive ancestors from the merged `extra_form_data`.
The corrected implementation walks the full transitive ancestor chain in
topological order.

The pass-to-pass tests guard against regressions and verify edge cases
(cycle protection, scalar override precedence) that pass on both base and
gold.
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


def _run_jest(
    test_path_pattern: str,
    test_name_pattern: str | None = None,
    timeout: int = 600,
) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    env["CI"] = "1"
    env["TZ"] = "America/New_York"
    cmd = [
        "npx",
        "jest",
        "--no-coverage",
        "--colors=false",
        "--runInBand",
        "--testPathPatterns",
        test_path_pattern,
    ]
    if test_name_pattern:
        cmd.extend(["--testNamePattern", test_name_pattern])
    return subprocess.run(
        cmd,
        cwd=str(FRONTEND),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass tests
# ---------------------------------------------------------------------------


def test_transitive_chain_linear_merge():
    """f2p: A->B->C->D linear chain must merge all ancestors into D.

    The buggy implementation walks only direct cascadeParentIds, so D only
    sees C's filter data. The fix must walk the full transitive chain so D
    receives extra_form_data from A, B, and C on the first Apply.
    """
    _install_oracle()
    r = _run_jest(
        "__oracle_transitive_chain",
        "linear A->B->C->D chain",
        timeout=600,
    )
    assert r.returncode == 0, (
        "Oracle jest test (linear chain) failed.\n"
        f"--- stdout (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_transitive_chain_diamond_merge():
    """f2p: Diamond ancestor graph must deduplicate shared ancestors.

    When D has parents B and C that both depend on A, A's data must appear
    exactly once in D's merged extra_form_data, not twice. The buggy
    implementation would miss A entirely if it only walks direct parents.
    """
    _install_oracle()
    r = _run_jest(
        "__oracle_transitive_chain",
        "diamond ancestor",
        timeout=600,
    )
    assert r.returncode == 0, (
        "Oracle jest test (diamond merge) failed.\n"
        f"--- stdout (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass tests
# ---------------------------------------------------------------------------


def test_scalar_override_precedence():
    """p2p: Closest ancestor's scalar values must win over distant ancestors.

    For chain A->B->C where both A and B set time_range, C must receive B's
    time_range. This holds on both base (direct parent walk yields B) and
    gold (topological walk visits A then B, B overwrites A).
    """
    _install_oracle()
    r = _run_jest(
        "__oracle_transitive_chain",
        "closest ancestor wins",
        timeout=600,
    )
    assert r.returncode == 0, (
        "Oracle jest test (scalar override) failed.\n"
        f"--- stdout (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_cycle_protection():
    """p2p: Cyclic filter configs must not cause infinite loops.

    A cycle A<->B must produce a finite ancestor set without looping forever.
    Both base (single-hop walk) and gold (visited-guarded DFS) satisfy this.
    """
    _install_oracle()
    r = _run_jest(
        "__oracle_transitive_chain",
        "cyclic config",
        timeout=600,
    )
    assert r.returncode == 0, (
        "Oracle jest test (cycle protection) failed.\n"
        f"--- stdout (tail) ---\n{r.stdout[-3000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_filtercontrols_existing_jest_suite_passes():
    """p2p: The existing FilterControls jest suite must still pass.

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
