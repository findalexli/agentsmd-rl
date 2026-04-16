"""
Tests for airflow-dagversion-select-filter benchmark task.

This task verifies that the DagVersionSelect component filters version options
based on the selected DagRun. When a DagRun is selected, only that run's
versions should be shown instead of all versions for the DAG.
"""
import os
import subprocess
import tempfile

REPO = "/workspace/airflow"
UI_DIR = os.path.join(REPO, "airflow-core/src/airflow/ui")
COMPONENT_PATH = os.path.join(UI_DIR, "src/components/DagVersionSelect.tsx")

# Test file content from the PR - used to verify behavior
TEST_FILE_CONTENT = '''/*!
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
import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Wrapper } from "src/utils/Wrapper";

import { DagVersionSelect } from "./DagVersionSelect";

const dagVersionV1 = {
  bundle_name: "dags-folder",
  bundle_version: null,
  created_at: "2025-01-01T00:00:00Z",
  dag_id: "test_dag",
  version_number: 1,
};
const dagVersionV2 = {
  bundle_name: "dags-folder",
  bundle_version: null,
  created_at: "2025-01-02T00:00:00Z",
  dag_id: "test_dag",
  version_number: 2,
};
const dagVersionV3 = {
  bundle_name: "dags-folder",
  bundle_version: null,
  created_at: "2025-01-03T00:00:00Z",
  dag_id: "test_dag",
  version_number: 3,
};

const allVersions = [dagVersionV3, dagVersionV2, dagVersionV1];

let mockParams: Record<string, string> = { dagId: "test_dag" };

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");

  return {
    ...actual,
    useParams: () => mockParams,
  };
});

vi.mock("openapi/queries", () => ({
  useDagRunServiceGetDagRun: vi.fn(() => ({
    data: undefined,
    isLoading: false,
  })),
  useDagVersionServiceGetDagVersions: vi.fn(() => ({
    data: { dag_versions: allVersions, total_entries: 3 },
    isLoading: false,
  })),
}));

vi.mock("src/hooks/useSelectedVersion", () => ({
  default: vi.fn(() => undefined),
}));

const { useDagRunServiceGetDagRun } = await import("openapi/queries");

const mockRunData = {
  bundle_version: null,
  conf: null,
  dag_display_name: "test_dag",
  dag_id: "test_dag",
  dag_versions: [dagVersionV1, dagVersionV2],
  end_date: null,
  has_missed_deadline: false,
  logical_date: null,
  note: null,
  partition_key: null,
  queued_at: null,
  run_after: "2025-01-01T00:00:00Z",
  run_id: "run_1",
  run_type: "manual" as const,
  start_date: null,
  state: "success" as const,
  triggered_by: "ui" as const,
  triggering_user_name: null,
};

const getItems = (container: HTMLElement) => container.querySelectorAll(".chakra-select__item");

describe("DagVersionSelect", () => {
  it("shows all versions when no DagRun is selected", () => {
    mockParams = { dagId: "test_dag" };
    const { container } = render(<DagVersionSelect />, { wrapper: Wrapper });

    expect(getItems(container)).toHaveLength(3);
  });

  it("shows only the selected run's versions when a DagRun is selected", () => {
    mockParams = { dagId: "test_dag", runId: "run_1" };
    vi.mocked(useDagRunServiceGetDagRun).mockReturnValue({
      data: mockRunData,
      isLoading: false,
    } as ReturnType<typeof useDagRunServiceGetDagRun>);

    const { container } = render(<DagVersionSelect />, { wrapper: Wrapper });

    expect(getItems(container)).toHaveLength(2);
  });
});
'''


def test_component_imports_dag_run_service():
    """
    Verify that the component imports useDagRunServiceGetDagRun.
    This is required to fetch the selected DagRun's data (fail_to_pass).
    """
    with open(COMPONENT_PATH, "r") as f:
        content = f.read()

    assert "useDagRunServiceGetDagRun" in content, (
        "DagVersionSelect must import useDagRunServiceGetDagRun from openapi/queries "
        "to fetch the selected DagRun's data for filtering versions"
    )


def test_component_extracts_runid_from_params():
    """
    Verify that the component extracts runId from useParams.
    This is required to know which DagRun is selected (fail_to_pass).
    """
    with open(COMPONENT_PATH, "r") as f:
        content = f.read()

    # Check for runId extraction from useParams
    assert "runId" in content, (
        "DagVersionSelect must extract runId from useParams to determine "
        "which DagRun is selected"
    )

    # Verify it's used in the params destructuring
    import re
    params_pattern = r"useParams\s*\(\s*\).*runId"
    # Allow for multiline/spread across lines
    content_no_newlines = content.replace("\n", " ")
    assert re.search(r"const\s*\{[^}]*runId[^}]*\}\s*=\s*useParams", content_no_newlines), (
        "runId must be destructured from useParams call"
    )


def test_component_filters_versions_conditionally():
    """
    Verify that versions are filtered based on DagRun selection.
    When a DagRun is selected, only that run's versions should be shown (fail_to_pass).
    """
    with open(COMPONENT_PATH, "r") as f:
        content = f.read()

    # Check for conditional filtering logic
    assert "runData" in content, (
        "Component must use runData to access the selected DagRun's versions"
    )

    # Check that versions are derived from runData when available
    assert "dag_versions" in content, (
        "Component must access dag_versions from either all versions or runData"
    )

    # Verify conditional logic exists (ternary or if)
    import re
    content_no_newlines = content.replace("\n", " ")
    conditional_pattern = r"runId\s*!==\s*undefined\s*&&\s*runData|runId\s*&&\s*runData"
    assert re.search(conditional_pattern, content_no_newlines), (
        "Component must conditionally filter versions when runId and runData exist"
    )


def test_vitest_dagversionselect_filtering():
    """
    Run the DagVersionSelect vitest tests to verify filtering behavior.
    Tests that the component shows only the selected run's versions when
    a DagRun is selected (fail_to_pass).
    """
    test_file_path = os.path.join(UI_DIR, "src/components/DagVersionSelect.test.tsx")

    # Write the test file if it doesn't exist
    if not os.path.exists(test_file_path):
        with open(test_file_path, "w") as f:
            f.write(TEST_FILE_CONTENT)

    # Run vitest for just this test file
    result = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/components/DagVersionSelect.test.tsx", "--reporter=verbose"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check if tests passed
    assert result.returncode == 0, (
        f"DagVersionSelect vitest tests failed:\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_typescript_compiles():
    """
    Verify that the TypeScript code compiles without errors (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit", "-p", "tsconfig.app.json"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"TypeScript compilation failed:\n{result.stderr[-2000:]}"
    )


def test_eslint_passes():
    """
    Verify that ESLint passes for the component (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "exec", "eslint", "src/components/DagVersionSelect.tsx", "--quiet"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"ESLint failed for DagVersionSelect.tsx:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_prettier_format():
    """
    Verify that Prettier formatting is correct for the component (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "exec", "prettier", "--check", "src/components/DagVersionSelect.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"Prettier check failed for DagVersionSelect.tsx:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_vitest_components():
    """
    Run vitest for the components directory excluding DagVersionSelect test (pass_to_pass).
    Ensures existing component tests continue to pass.
    The DagVersionSelect.test.tsx is excluded as it's created by the f2p test.
    """
    result = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/components", "--exclude", "**/DagVersionSelect.test.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Vitest component tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
    )
