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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_npm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_npm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run ci:release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_sqlite_python_integration_tests_sqlite():
    """pass_to_pass | CI job 'test-sqlite' → step 'Python integration tests (SQLite)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (SQLite)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_mysql_generate_database_diagnostics_for_docs():
    """pass_to_pass | CI job 'test-mysql' → step 'Generate database diagnostics for docs'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Generate database diagnostics for docs' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_hive_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-hive' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "pip install -e .[hive] && ./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_postgres_presto_python_unit_tests_postgresql():
    """pass_to_pass | CI job 'test-postgres-presto' → step 'Python unit tests (PostgreSQL)'"""
    r = subprocess.run(
        ["bash", "-lc", "./scripts/python_tests.sh -m 'chart_data_flow or sql_json_flow'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python unit tests (PostgreSQL)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_check_for_uncommitted_changes():
    """pass_to_pass | CI job 'check-python-deps' → step 'Check for uncommitted changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Full diff (for logging/debugging):"\ngit diff\n\necho "Filtered diff (excluding comments and whitespace):"\nfiltered_diff=$(git diff -U0 | grep \'^[-+]\' | grep -vE \'^[-+]{3}\' | grep -vE \'^[-+][[:space:]]*#\' | grep -vE \'^[-+][[:space:]]*$\' || true)\necho "$filtered_diff"\n\nif [[ -n "$filtered_diff" ]]; then\n  echo\n  echo "ERROR: The pinned dependencies are not up-to-date."\n  echo "Please run \'./scripts/uv-pip-compile.sh\' and commit the changes."\n  echo "More info: https://github.com/apache/superset/tree/master/requirements"\n  exit 1\nelse\n  echo "Pinned dependencies are up-to-date."\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for uncommitted changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_superset_extensions_cli_p_run_pytest_with_coverage():
    """pass_to_pass | CI job 'test-superset-extensions-cli-package' → step 'Run pytest with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest --cov=superset_extensions_cli --cov-report=xml --cov-report=term-missing --cov-report=html -v --tb=short'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pytest with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")