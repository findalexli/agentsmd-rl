"""Tests for the DagVersionSelect component fix.

This verifies that the DagVersionSelect component correctly filters
version options based on the selected DagRun.
"""

import subprocess
import sys

REPO = "/workspace/airflow/airflow-core/src/airflow/ui"


def test_typescript_compiles():
    """Verify TypeScript compiles without errors after the fix."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"TypeScript compilation failed:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )


def test_unit_tests_pass():
    """Run the vitest tests for DagVersionSelect component."""
    result = subprocess.run(
        ["npx", "vitest", "run", "src/components/DagVersionSelect.test.tsx", "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    output = result.stdout.decode() + result.stderr.decode()
    assert result.returncode == 0, f"Tests failed:\n{output}"
    # Verify both specific tests ran and passed
    assert "shows all versions when no DagRun is selected" in output, "Missing test for no run selected"
    assert "shows only the selected run's versions when a DagRun is selected" in output, "Missing test for run selected"
    assert "2 passed" in output or "✓" in output, "Expected 2 tests to pass"


def test_component_uses_runid_from_params():
    """Verify the component extracts runId from useParams."""
    with open(f"{REPO}/src/components/DagVersionSelect.tsx") as f:
        content = f.read()

    # Check that runId is extracted from useParams
    assert "const { dagId = \"\", runId } = useParams()" in content, (
        "Component must extract runId from useParams"
    )


def test_component_fetches_dagrun_data():
    """Verify the component fetches DagRun data when runId is present."""
    with open(f"{REPO}/src/components/DagVersionSelect.tsx") as f:
        content = f.read()

    # Check that useDagRunServiceGetDagRun is imported and called
    assert "useDagRunServiceGetDagRun" in content, "Component must use useDagRunServiceGetDagRun hook"
    assert 'enabled: Boolean(runId)' in content, "Query must be conditionally enabled based on runId"


def test_component_filters_versions_based_on_run():
    """Verify the component filters versions when a run is selected."""
    with open(f"{REPO}/src/components/DagVersionSelect.tsx") as f:
        content = f.read()

    # Check for the filtering logic
    assert "runData.dag_versions" in content, "Component must use runData.dag_versions for filtering"
    assert "runId !== undefined && runData" in content, "Component must check if run is selected"


def test_version_options_use_filtered_versions():
    """Verify versionOptions uses the filtered versions array."""
    with open(f"{REPO}/src/components/DagVersionSelect.tsx") as f:
        content = f.read()

    # The versionOptions should be created from filtered 'versions' not 'allVersions'
    assert "items: versions.map" in content, "versionOptions must use filtered versions array"


def test_disabled_state_uses_filtered_versions():
    """Verify disabled state checks the filtered versions array length."""
    with open(f"{REPO}/src/components/DagVersionSelect.tsx") as f:
        content = f.read()

    assert "disabled={isLoading || versions.length === 0}" in content, (
        "Disabled state must check filtered versions length"
    )


def test_selected_version_uses_filtered_versions():
    """Verify selectedVersion lookup uses the filtered versions array."""
    with open(f"{REPO}/src/components/DagVersionSelect.tsx") as f:
        content = f.read()

    assert "const selectedVersion = versions.find" in content, (
        "selectedVersion must be found in filtered versions array"
    )
