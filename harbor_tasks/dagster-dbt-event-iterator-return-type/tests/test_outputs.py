"""Tests for dagster-dbt event iterator return type fix."""

import os
import subprocess
from pathlib import Path

# Repo paths
REPO = Path("/workspace/dagster")
COMPONENT_PY = REPO / "python_modules" / "libraries" / "dagster-dbt" / "dagster_dbt" / "components" / "dbt_project" / "component.py"
ITERATOR_PY = REPO / "python_modules" / "libraries" / "dagster-dbt" / "dagster_dbt" / "core" / "dbt_event_iterator.py"


def test_component_imports_iterator_types():
    """F2P: component.py must import DbtEventIterator and DbtDagsterEventType."""
    content = COMPONENT_PY.read_text()

    # Check that the import line exists
    assert "from dagster_dbt.core.dbt_event_iterator import DbtDagsterEventType, DbtEventIterator" in content, \
        "component.py must import DbtEventIterator and DbtDagsterEventType"


def test_component_method_return_type():
    """F2P: _get_dbt_event_iterator must return DbtEventIterator[DbtDagsterEventType]."""
    content = COMPONENT_PY.read_text()

    # Find the method and check its return type
    assert "def _get_dbt_event_iterator(" in content, "Method _get_dbt_event_iterator must exist"

    # Check return type annotation
    assert ") -> DbtEventIterator[DbtDagsterEventType]:" in content, \
        "Method must have return type DbtEventIterator[DbtDagsterEventType]"

    # Make sure it's NOT the old generic Iterator
    lines = content.split("\n")
    in_method = False
    method_lines = []
    for line in lines:
        if "def _get_dbt_event_iterator(" in line:
            in_method = True
        if in_method:
            method_lines.append(line)
            if line.strip().endswith(":") and "def _get_dbt_event_iterator" not in line:
                break

    method_sig = "\n".join(method_lines)
    assert "-> Iterator:" not in method_sig, \
        "Method must NOT have generic Iterator return type (should be DbtEventIterator[DbtDagsterEventType])"


def test_iterator_methods_use_type_alias():
    """F2P: Iterator methods must use DbtDagsterEventType type alias consistently."""
    content = ITERATOR_PY.read_text()

    # Check that the type alias is used (check for the pattern with proper indentation)
    assert ') -> "DbtEventIterator[DbtDagsterEventType]":' in content, \
        "Methods must return DbtEventIterator[DbtDagsterEventType]"

    # Count occurrences - should be at least 3 (fetch_row_counts, fetch_column_metadata, with_insights)
    type_alias_count = content.count('"DbtEventIterator[DbtDagsterEventType]"')
    assert type_alias_count >= 3, \
        f"Expected at least 3 uses of DbtDagsterEventType type alias, found {type_alias_count}"

    # Verify specific methods use the type alias in their return annotations
    # Check fetch_row_counts, fetch_column_metadata, and with_insights specifically
    import re

    # Find the method definitions and check their return types
    method_pattern = r'def (fetch_row_counts|fetch_column_metadata|with_insights)\([^)]*\)\s*->\s*"([^"]+)"'
    matches = re.findall(method_pattern, content)

    for method_name, return_type in matches:
        assert "DbtDagsterEventType" in return_type, \
            f"Method {method_name} should return DbtEventIterator[DbtDagsterEventType], got {return_type}"


def test_type_alias_exists():
    """F2P: DbtDagsterEventType type alias must exist."""
    content = ITERATOR_PY.read_text()

    assert "DbtDagsterEventType: TypeAlias =" in content, \
        "DbtDagsterEventType type alias must be defined"

    assert "Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation" in content, \
        "Type alias must include all event types"


def test_grep_style_type_check():
    """P2P: Verify consistent use of type alias via grep."""
    # Use grep to verify the pattern in both files
    r1 = subprocess.run(
        ["grep", r"DbtEventIterator\[DbtDagsterEventType\]", str(COMPONENT_PY)],
        capture_output=True,
        text=True
    )
    assert r1.returncode == 0, "component.py should contain DbtEventIterator[DbtDagsterEventType]"

    # Count occurrences in iterator file
    r2 = subprocess.run(
        ["grep", "-c", r"DbtEventIterator\[DbtDagsterEventType\]", str(ITERATOR_PY)],
        capture_output=True,
        text=True
    )
    assert r2.returncode == 0, "Should find type alias in iterator file"
    count = int(r2.stdout.strip())
    assert count >= 3, f"Expected at least 3 uses, found {count}"


def test_repo_ruff_check():
    """Repo CI: dagster-dbt passes ruff linting (pass_to_pass)."""
    # Install exact ruff version required by repo
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", "python_modules/libraries/dagster-dbt/dagster_dbt"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr}\n{r.stdout}"


def test_repo_ruff_format():
    """Repo CI: dagster-dbt passes ruff format check (pass_to_pass)."""
    # Install exact ruff version required by repo
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", "python_modules/libraries/dagster-dbt/dagster_dbt"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


def test_repo_python_syntax():
    """Repo CI: dagster-dbt Python files have valid syntax (pass_to_pass)."""
    # Test component.py syntax
    r1 = subprocess.run(
        ["python", "-m", "py_compile", str(COMPONENT_PY)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r1.returncode == 0, f"component.py syntax error: {r1.stderr}"

    # Test dbt_event_iterator.py syntax
    r2 = subprocess.run(
        ["python", "-m", "py_compile", str(ITERATOR_PY)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r2.returncode == 0, f"dbt_event_iterator.py syntax error: {r2.stderr}"


def test_repo_module_browsable():
    """Repo CI: dagster-dbt modules can be parsed by pyclbr (pass_to_pass)."""
    # Use pyclbr to verify the module is structurally parseable
    r = subprocess.run(
        [
            "python",
            "-c",
            "import pyclbr; "
            "m = pyclbr.readmodule_ex('dagster_dbt.core.dbt_event_iterator', "
            "['python_modules/libraries/dagster-dbt']); "
            "assert 'DbtEventIterator' in m, 'DbtEventIterator class not found'; "
            "print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Module browse failed: {r.stderr}"
