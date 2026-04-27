"""
Pytest harness for the litellm 'guardrails on projects UI' task (PR #25100).

The oracle Vitest test source is embedded as a Python string literal so the
/tests/ directory contains only the standard files (test.sh,
test_outputs.py). At session start we write it to the project's tests/
directory so vitest picks it up via its include glob and so the relative
`./test-utils` import resolves.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/litellm")
UI = REPO / "ui" / "litellm-dashboard"
ORACLE_DEST = UI / "tests" / "__oracle_guardrails.test.tsx"
RESULTS_JSON = Path("/tmp/vitest-oracle.json")

# The oracle vitest test source. Each `it("ORACLE_F2P_N ...")` maps 1:1 to a
# pytest function below.
ORACLE_TSX = r"""/**
 * Oracle test file for litellm PR #25100. Generated from test_outputs.py.
 */
import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import { Form } from "antd";

import { renderWithProviders, screen, waitFor } from "./test-utils";
import {
  ProjectBaseForm,
  ProjectFormValues,
} from "@/components/Projects/ProjectModals/ProjectBaseForm";
import { buildProjectApiParams } from "@/components/Projects/ProjectModals/projectFormUtils";

const mockUseTeams = vi.fn();
vi.mock("@/app/(dashboard)/hooks/teams/useTeams", () => ({
  useTeams: () => mockUseTeams(),
}));

vi.mock("@/components/organisms/create_key_button", () => ({
  fetchTeamModels: vi.fn().mockResolvedValue([]),
}));

vi.mock("@/components/key_team_helpers/fetch_available_models_team_key", () => ({
  getModelDisplayName: (model: string) => model,
}));

vi.mock("@/components/networking", () => ({
  getGuardrailsList: vi.fn().mockResolvedValue({ guardrails: [] }),
}));

const baseValues: ProjectFormValues = {
  project_alias: "Project X",
  team_id: "team-1",
  models: [],
  isBlocked: false,
};

describe("ORACLE: buildProjectApiParams handles guardrails", () => {
  it("ORACLE_F2P_1 should include guardrails as a top-level field when provided", () => {
    const result = buildProjectApiParams({
      ...baseValues,
      guardrails: ["pii-check", "content-filter"],
    }) as Record<string, unknown>;
    expect(result.guardrails).toEqual(["pii-check", "content-filter"]);
  });

  it("ORACLE_F2P_2 should omit guardrails when the array is empty", () => {
    const result = buildProjectApiParams({
      ...baseValues,
      guardrails: [],
    }) as Record<string, unknown>;
    expect(result).not.toHaveProperty("guardrails");
  });

  it("ORACLE_F2P_3 should omit guardrails when not provided at all", () => {
    const result = buildProjectApiParams({
      ...baseValues,
    }) as Record<string, unknown>;
    expect(result).not.toHaveProperty("guardrails");
  });

  it("ORACLE_F2P_4 should preserve a single-entry guardrails array", () => {
    const result = buildProjectApiParams({
      ...baseValues,
      guardrails: ["only-one"],
    }) as Record<string, unknown>;
    expect(result.guardrails).toEqual(["only-one"]);
  });

  it("ORACLE_F2P_5 should keep guardrails as a top-level field, NOT inside metadata", () => {
    const result = buildProjectApiParams({
      ...baseValues,
      guardrails: ["g-a"],
    }) as Record<string, unknown>;
    expect(result.guardrails).toEqual(["g-a"]);
    if ("metadata" in result && result.metadata !== undefined) {
      expect((result.metadata as Record<string, unknown>).guardrails).toBeUndefined();
    }
  });
});

function FormWrapper() {
  const [form] = Form.useForm<ProjectFormValues>();
  return <ProjectBaseForm form={form} />;
}

describe("ORACLE: ProjectBaseForm has a Guardrails field", () => {
  beforeEach(() => {
    mockUseTeams.mockReturnValue({ data: [], isLoading: false });
  });

  it("ORACLE_F2P_6 should show a Guardrails field in the Advanced Settings section", async () => {
    const user = userEvent.setup();
    renderWithProviders(<FormWrapper />);
    await user.click(screen.getByText("Advanced Settings"));
    await waitFor(() => {
      expect(screen.getByText("Guardrails")).toBeInTheDocument();
    });
  });
});
"""


@pytest.fixture(scope="session")
def vitest_results() -> dict:
    """Materialize the oracle test, run vitest once, return parsed JSON."""
    assert UI.exists(), f"missing UI dir at {UI}"

    ORACLE_DEST.parent.mkdir(parents=True, exist_ok=True)
    ORACLE_DEST.write_text(ORACLE_TSX)

    if RESULTS_JSON.exists():
        RESULTS_JSON.unlink()

    try:
        proc = subprocess.run(
            [
                "npx",
                "vitest",
                "run",
                "tests/__oracle_guardrails.test.tsx",
                "--reporter=json",
                f"--outputFile={RESULTS_JSON}",
            ],
            cwd=str(UI),
            capture_output=True,
            text=True,
            timeout=600,
        )
    finally:
        if ORACLE_DEST.exists():
            ORACLE_DEST.unlink()

    if not RESULTS_JSON.exists():
        raise AssertionError(
            "vitest produced no results JSON.\n"
            f"stdout:\n{proc.stdout[-2000:]}\n"
            f"stderr:\n{proc.stderr[-2000:]}"
        )

    with open(RESULTS_JSON) as f:
        return json.load(f)


def _assert_oracle_test_passed(results: dict, name_substring: str) -> None:
    matched = []
    for suite in results.get("testResults", []):
        for assertion in suite.get("assertionResults", []):
            full_name = assertion.get("fullName") or assertion.get("title", "")
            if name_substring in full_name:
                matched.append((full_name, assertion.get("status")))
    assert matched, (
        f"could not find any vitest test matching '{name_substring}'.\n"
        f"available tests: "
        + ", ".join(
            (a.get('fullName') or a.get('title', ''))
            for s in results.get('testResults', [])
            for a in s.get('assertionResults', [])
        )
    )
    failed = [name for name, status in matched if status != "passed"]
    assert not failed, f"vitest test(s) failed: {failed}"


# ---- f2p tests: behavior introduced by PR #25100 ----

def test_build_passes_guardrails_with_values(vitest_results):
    """buildProjectApiParams must include guardrails as a top-level array."""
    _assert_oracle_test_passed(vitest_results, "ORACLE_F2P_1")


def test_build_omits_empty_guardrails(vitest_results):
    """buildProjectApiParams must omit guardrails entirely when given []."""
    _assert_oracle_test_passed(vitest_results, "ORACLE_F2P_2")


def test_build_omits_undefined_guardrails(vitest_results):
    """buildProjectApiParams must omit guardrails when not provided."""
    _assert_oracle_test_passed(vitest_results, "ORACLE_F2P_3")


def test_build_preserves_single_guardrail(vitest_results):
    """buildProjectApiParams must work with a single-entry guardrails array."""
    _assert_oracle_test_passed(vitest_results, "ORACLE_F2P_4")


def test_build_keeps_guardrails_top_level_not_nested(vitest_results):
    """guardrails must be top-level, not nested in metadata."""
    _assert_oracle_test_passed(vitest_results, "ORACLE_F2P_5")


def test_form_renders_guardrails_field(vitest_results):
    """ProjectBaseForm must render a 'Guardrails' label inside Advanced Settings."""
    _assert_oracle_test_passed(vitest_results, "ORACLE_F2P_6")


# ---- p2p tests: existing behavior must keep working ----

def test_p2p_repo_form_utils_existing_tests():
    r = subprocess.run(
        [
            "npx",
            "vitest",
            "run",
            "src/components/Projects/ProjectModals/projectFormUtils.test.ts",
        ],
        cwd=str(UI),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"projectFormUtils.test.ts failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
    )


def test_p2p_repo_baseform_existing_tests():
    r = subprocess.run(
        [
            "npx",
            "vitest",
            "run",
            "src/components/Projects/ProjectModals/ProjectBaseForm.test.tsx",
        ],
        cwd=str(UI),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"ProjectBaseForm.test.tsx failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
    )


def test_p2p_repo_global_setup_tests():
    r = subprocess.run(
        [
            "npx",
            "vitest",
            "run",
            "src/components/Projects/ProjectModals/",
        ],
        cwd=str(UI),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"ProjectModals/ test dir failed:\n"
        f"stdout:\n{r.stdout[-2000:]}\n"
        f"stderr:\n{r.stderr[-2000:]}"
    )
