"""Behavioral tests for apache/superset PR #39136 benchmark task.

The PR fixes a UI bug where the dropdown popup width does not match the
input width after tag collapse in `oneLine` mode of the multi-select
component (`<Select>` in `superset-ui-core`). These tests inject a
benchmark Jest test file and verify that:
  * `f2p` — the new behavior (dropdown style.width tracks the measured
    select width when tags collapse) is implemented correctly at two
    distinct widths (300px and 450px) to prevent hard-coding.
  * `p2p` — the existing 78 tests in `Select.test.tsx` still pass.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
FRONTEND = REPO / "superset-frontend"
SELECT_DIR = (
    FRONTEND
    / "packages"
    / "superset-ui-core"
    / "src"
    / "components"
    / "Select"
)
BENCH_DST = SELECT_DIR / "Select.benchmark.test.tsx"

BENCHMARK_TEST_TSX = r"""/**
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
import {
  render,
  screen,
  userEvent,
  waitFor,
  within,
} from '@superset-ui/core/spec';
import { Select } from '.';

const ARIA_LABEL = 'Test';
const OPTIONS = [
  { label: 'John', value: 1, gender: 'Male' },
  { label: 'Liam', value: 2, gender: 'Male' },
  { label: 'Olivia', value: 3, gender: 'Female' },
];

const defaultProps = {
  allowClear: true,
  ariaLabel: ARIA_LABEL,
  labelInValue: true,
  options: OPTIONS,
  showSearch: true,
};

const getElementByClassName = (className: string) =>
  document.querySelector(className)! as HTMLElement;

const getSelect = () =>
  screen.getByRole('combobox', { name: new RegExp(ARIA_LABEL, 'i') });

const openSelect = () => waitFor(() => userEvent.click(getSelect()));

const escSelect = async () => {
  const select = getSelect();
  await userEvent.clear(select);
  return userEvent.type(select, '{esc}', { delay: 10 });
};

const mockRect = (el: HTMLElement, width: number) =>
  jest.spyOn(el, 'getBoundingClientRect').mockReturnValue({
    width,
    height: 32,
    top: 0,
    left: 0,
    right: width,
    bottom: 32,
    x: 0,
    y: 0,
    toJSON: () => ({}),
  } as DOMRect);

test('dropdown width matches collapsed input width in oneLine mode (300)', async () => {
  render(
    <div style={{ width: '300px' }}>
      <Select
        {...defaultProps}
        value={[OPTIONS[0], OPTIONS[1], OPTIONS[2]]}
        mode="multiple"
        oneLine
      />
    </div>,
  );
  await openSelect();
  await waitFor(() => {
    const withinSelector = within(
      getElementByClassName('.ant-select-selector'),
    );
    expect(
      withinSelector.queryByText(OPTIONS[0].label),
    ).not.toBeInTheDocument();
    expect(withinSelector.getByText('+ 3 ...')).toBeVisible();
  });
  const selectElement = document.querySelector('.ant-select') as HTMLElement;
  expect(selectElement).toBeInTheDocument();
  mockRect(selectElement, 300);
  await escSelect();
  await openSelect();
  const dropdown = document.querySelector(
    '.ant-select-dropdown',
  ) as HTMLElement;
  expect(dropdown).toBeInTheDocument();
  await waitFor(() => {
    expect(parseInt(dropdown.style.width, 10)).toBe(300);
  });
});

test('dropdown width matches collapsed input width in oneLine mode (450)', async () => {
  render(
    <div style={{ width: '450px' }}>
      <Select
        {...defaultProps}
        value={[OPTIONS[0], OPTIONS[1]]}
        mode="multiple"
        oneLine
      />
    </div>,
  );
  await openSelect();
  await waitFor(() => {
    const withinSelector = within(
      getElementByClassName('.ant-select-selector'),
    );
    expect(withinSelector.getByText('+ 2 ...')).toBeVisible();
  });
  const selectElement = document.querySelector('.ant-select') as HTMLElement;
  mockRect(selectElement, 450);
  await escSelect();
  await openSelect();
  const dropdown = document.querySelector(
    '.ant-select-dropdown',
  ) as HTMLElement;
  await waitFor(() => {
    expect(parseInt(dropdown.style.width, 10)).toBe(450);
  });
});
"""


def _install_benchmark_test() -> None:
    """Write the benchmark .test.tsx into the package so jest will find it."""
    SELECT_DIR.mkdir(parents=True, exist_ok=True)
    BENCH_DST.write_text(BENCHMARK_TEST_TSX)


def _run_jest(
    test_path: str, timeout: int, test_name_filter: str | None = None
) -> subprocess.CompletedProcess:
    cmd = [
        "npx",
        "jest",
        "--no-coverage",
        "--colors=false",
    ]
    if test_name_filter:
        cmd.extend(["-t", test_name_filter])
    cmd.append(test_path)
    return subprocess.run(
        cmd,
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_oneLine_dropdown_width_matches_collapsed_input_300():
    """f2p: In oneLine multi-select mode, after tags collapse, the dropdown's
    inline style.width (in px) equals the measured width for a 300px container.
    """
    _install_benchmark_test()
    rel = (
        "packages/superset-ui-core/src/components/Select/"
        "Select.benchmark.test.tsx"
    )
    r = _run_jest(rel, timeout=300, test_name_filter="(300)")
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        "Benchmark jest test (300px) for dropdown width did not pass.\n"
        f"stdout/stderr (last 4000 chars):\n{combined[-4000:]}"
    )
    assert "Tests:       1 skipped, 1 passed, 2 total" in combined or (
        "passed" in combined and "2 total" in combined
    ), f"Expected benchmark (300) test to pass:\n{combined[-2000:]}"


def test_oneLine_dropdown_width_matches_collapsed_input_450():
    """f2p: In oneLine multi-select mode, after tags collapse, the dropdown's
    inline style.width (in px) equals the measured width for a 450px container.
    """
    _install_benchmark_test()
    rel = (
        "packages/superset-ui-core/src/components/Select/"
        "Select.benchmark.test.tsx"
    )
    r = _run_jest(rel, timeout=300, test_name_filter="(450)")
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        "Benchmark jest test (450px) for dropdown width did not pass.\n"
        f"stdout/stderr (last 4000 chars):\n{combined[-4000:]}"
    )
    assert "Tests:       1 skipped, 1 passed, 2 total" in combined or (
        "passed" in combined and "2 total" in combined
    ), f"Expected benchmark (450) test to pass:\n{combined[-2000:]}"


def test_select_existing_suite_still_passes():
    """p2p: the existing 78 tests in Select.test.tsx still pass after the fix."""
    rel = "packages/superset-ui-core/src/components/Select/Select.test.tsx"
    r = _run_jest(rel, timeout=600)
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        "Existing Select.test.tsx suite regressed.\n"
        f"stdout/stderr (last 4000 chars):\n{combined[-4000:]}"
    )


def test_ci_jest_select_suite_via_shell():
    """p2p: CI-style jest run of existing Select.test.tsx suite via bash -lc,
    matching how CI invokes the test runner.
    """
    r = subprocess.run(
        [
            "bash", "-lc",
            "npx jest --no-coverage --colors=false "
            "packages/superset-ui-core/src/components/Select/Select.test.tsx",
        ],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=600,
    )
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        f"CI-style jest run of Select.test.tsx failed (returncode={r.returncode}):\n"
        f"stdout/stderr (last 3000 chars):\n{combined[-3000:]}"
    )
    assert "Tests:" in combined and ("78 passed" in combined or "passed" in combined), (
        f"Expected Select.test.tsx to pass all tests via shell:\n{combined[-2000:]}"
    )
