"""
Tests for airflow-dag-version-select-filter task.

This task verifies that the DagVersionSelect component correctly filters
version options based on the selected DagRun.
"""
import subprocess
import os
import re

REPO = "/workspace/airflow"
UI_DIR = os.path.join(REPO, "airflow-core/src/airflow/ui")


def _count_tests_passed(stdout: str) -> int:
    """Extract the number of tests that passed from vitest output."""
    m = re.search(r'Tests\s+(\d+)\s+passed', stdout)
    return int(m.group(1)) if m else 0


def test_dagversionselect_vitest():
    """
    Run vitest tests for DagVersionSelect component (fail_to_pass).

    The component must filter versions based on selected DagRun:
    - When no DagRun is selected, show all versions
    - When a DagRun is selected, show only that run's versions
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "src/components/DagVersionSelect.test.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Vitest tests failed:\n{result.stdout}\n{result.stderr}"
    passed = _count_tests_passed(result.stdout)
    assert passed >= 2, (
        f"Expected at least 2 tests to pass (filtered + unfiltered), got {passed}"
    )


def test_typescript_check():
    """
    TypeScript type checking passes for DagVersionSelect (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "tsc", "--noEmit", "-p", "tsconfig.app.json"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stdout}\n{result.stderr}"


def test_component_imports_dag_run_hook():
    """
    Verify the component fetches and uses DagRun data for filtering (fail_to_pass).

    Runs the vitest case that checks filtering when a DagRun is selected.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "-t", "DagRun is selected",
         "src/components/DagVersionSelect.test.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"DagRun filtering test failed — component must fetch DagRun data "
        f"and filter versions when a run is selected:\n{result.stdout}\n{result.stderr}"
    )
    passed = _count_tests_passed(result.stdout)
    assert passed >= 1, (
        f"No tests ran — the filtered DagRun test case must execute:\n{result.stdout}"
    )


def test_component_extracts_runid():
    """
    Verify the component responds to runId in the URL for filtering (fail_to_pass).

    Runs the vitest case that checks all versions render when no DagRun is selected.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "-t", "no DagRun",
         "src/components/DagVersionSelect.test.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"No-runId baseline test failed — component must correctly render "
        f"all versions when no DagRun is selected:\n{result.stdout}\n{result.stderr}"
    )
    passed = _count_tests_passed(result.stdout)
    assert passed >= 1, (
        f"No tests ran — the unfiltered baseline test case must execute:\n{result.stdout}"
    )


def test_component_filters_versions():
    """
    Verify the component's version filtering end-to-end (fail_to_pass).

    Runs the full DagVersionSelect test suite via vitest and verifies at
    least 2 distinct test cases pass — one for the unfiltered case and
    one for the filtered case. This ensures both behaviors are covered.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "src/components/DagVersionSelect.test.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Vitest tests failed:\n{result.stdout}\n{result.stderr}"
    passed = _count_tests_passed(result.stdout)
    assert passed >= 2, (
        f"Expected at least 2 test cases (filtered + unfiltered), found {passed}"
    )


def test_eslint_passes():
    """
    ESLint passes for the component file (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "eslint", "--quiet", "src/components/DagVersionSelect.tsx"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_prettier_check():
    """
    Prettier formatting check passes for the UI (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "prettier", "--check", "."],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_vite_build():
    """
    Vite production build succeeds (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "build"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Vite build failed:\n{result.stdout}\n{result.stderr}"


def test_repo_components_vitest():
    """
    Vitest passes for all component tests (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "src/components/"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Component tests failed:\n{result.stdout}\n{result.stderr}"
