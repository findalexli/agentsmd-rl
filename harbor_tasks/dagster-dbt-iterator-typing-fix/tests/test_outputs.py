"""Tests for dagster-dbt type annotation fix.

This tests that the return types are correctly set to DbtEventIterator[DbtDagsterEventType]
instead of the generic Iterator or the long union type.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path

import pytest

# Paths to the modified files
REPO = Path("/workspace/dagster")
COMPONENT_FILE = REPO / "python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py"
ITERATOR_FILE = REPO / "python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py"

DBT_PROJECT_DIR = REPO / "python_modules/libraries/dagster-dbt"


# =============================================================================
# PASS_TO_PASS TESTS - Repo CI commands (origin: repo_tests)
# These verify the repo's CI checks pass on both base commit and after the fix
# =============================================================================


def test_ruff_check_component():
    """Ruff linter check on component.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", str(COMPONENT_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff check failed on component.py:\n{r.stdout}\n{r.stderr}"


def test_ruff_check_iterator():
    """Ruff linter check on dbt_event_iterator.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "check", str(ITERATOR_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff check failed on dbt_event_iterator.py:\n{r.stdout}\n{r.stderr}"


def test_component_py_compile():
    """Python syntax check on component.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(COMPONENT_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"py_compile failed on component.py:\n{r.stderr}"


def test_iterator_py_compile():
    """Python syntax check on dbt_event_iterator.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", str(ITERATOR_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"py_compile failed on dbt_event_iterator.py:\n{r.stderr}"


# =============================================================================
# PASS_TO_PASS TESTS - Static checks (origin: static)
# These verify static properties of the code
# =============================================================================


def test_dagster_dbt_package_structure():
    """Verify dagster-dbt package has expected structure (pass_to_pass)."""
    assert COMPONENT_FILE.exists(), f"component.py should exist at {COMPONENT_FILE}"
    assert ITERATOR_FILE.exists(), f"dbt_event_iterator.py should exist at {ITERATOR_FILE}"

    # Verify key directories exist
    core_dir = REPO / "python_modules/libraries/dagster-dbt/dagster_dbt/core"
    components_dir = REPO / "python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project"
    assert core_dir.exists(), "dagster_dbt/core directory should exist"
    assert components_dir.exists(), "dagster_dbt/components/dbt_project directory should exist"


def test_pyproject_toml_exists():
    """Verify dagster-dbt has valid pyproject.toml (pass_to_pass)."""
    pyproject = DBT_PROJECT_DIR / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml should exist"

    # Verify it's valid TOML by checking it has expected sections
    content = pyproject.read_text()
    assert "[project]" in content, "pyproject.toml should have [project] section"
    assert 'name = "dagster-dbt"' in content, "pyproject.toml should have correct package name"


def test_component_ast_valid():
    """Verify component.py is valid Python AST (pass_to_pass)."""
    source = COMPONENT_FILE.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise AssertionError(f"component.py has syntax error: {e}")

    # Verify it has DbtProjectComponent class
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "DbtProjectComponent" in classes, "component.py should have DbtProjectComponent class"


def test_iterator_ast_valid():
    """Verify dbt_event_iterator.py is valid Python AST (pass_to_pass)."""
    source = ITERATOR_FILE.read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise AssertionError(f"dbt_event_iterator.py has syntax error: {e}")

    # Verify it has DbtEventIterator class
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "DbtEventIterator" in classes, "dbt_event_iterator.py should have DbtEventIterator class"


def test_dbt_event_iterator_has_event_type_alias():
    """Verify DbtDagsterEventType TypeAlias is defined (pass_to_pass)."""
    source = ITERATOR_FILE.read_text()

    # Check for TypeAlias definition
    assert "DbtDagsterEventType: TypeAlias" in source, (
        "DbtDagsterEventType should be defined as TypeAlias in dbt_event_iterator.py"
    )


# =============================================================================
# FAIL_TO_PASS TESTS - These verify the specific fix
# =============================================================================


def get_function_return_type(file_path: Path, function_name: str, class_name: str = None) -> str:
    """Extract the return type annotation from a function."""
    source = file_path.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if class_name:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == function_name:
                        if item.returns:
                            return ast.unparse(item.returns)
        else:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                if node.returns:
                    return ast.unparse(node.returns)
    return None


def test_component_iterator_return_type():
    """Test that _get_dbt_event_iterator returns DbtEventIterator[DbtDagsterEventType]."""
    return_type = get_function_return_type(
        COMPONENT_FILE,
        "_get_dbt_event_iterator",
        "DbtProjectComponent"
    )

    assert return_type is not None, "Could not find _get_dbt_event_iterator method"
    assert "DbtEventIterator" in return_type, (
        f"Return type should be DbtEventIterator, got: {return_type}"
    )
    assert "DbtDagsterEventType" in return_type, (
        f"Return type should be parameterized with DbtDagsterEventType, got: {return_type}"
    )
    assert "Iterator" not in return_type or "DbtEventIterator" in return_type, (
        f"Return type should not be generic Iterator, got: {return_type}"
    )


def test_iterator_fetch_row_counts_return_type():
    """Test that fetch_row_counts returns DbtEventIterator[DbtDagsterEventType]."""
    return_type = get_function_return_type(
        ITERATOR_FILE,
        "fetch_row_counts",
        "DbtEventIterator"
    )

    assert return_type is not None, "Could not find fetch_row_counts method"
    assert "DbtEventIterator" in return_type, (
        f"Return type should be DbtEventIterator, got: {return_type}"
    )
    assert "DbtDagsterEventType" in return_type, (
        f"Return type should be parameterized with DbtDagsterEventType, got: {return_type}"
    )
    # Ensure it's not the old long union type
    assert "AssetCheckResult | AssetObservation" not in return_type, (
        f"Return type should use DbtDagsterEventType alias, not the full union, got: {return_type}"
    )


def test_iterator_fetch_column_metadata_return_type():
    """Test that fetch_column_metadata returns DbtEventIterator[DbtDagsterEventType]."""
    return_type = get_function_return_type(
        ITERATOR_FILE,
        "fetch_column_metadata",
        "DbtEventIterator"
    )

    assert return_type is not None, "Could not find fetch_column_metadata method"
    assert "DbtEventIterator" in return_type, (
        f"Return type should be DbtEventIterator, got: {return_type}"
    )
    assert "DbtDagsterEventType" in return_type, (
        f"Return type should be parameterized with DbtDagsterEventType, got: {return_type}"
    )
    assert "AssetCheckResult | AssetObservation" not in return_type, (
        f"Return type should use DbtDagsterEventType alias, not the full union, got: {return_type}"
    )


def test_iterator_with_insights_return_type():
    """Test that with_insights returns DbtEventIterator[DbtDagsterEventType]."""
    return_type = get_function_return_type(
        ITERATOR_FILE,
        "with_insights",
        "DbtEventIterator"
    )

    assert return_type is not None, "Could not find with_insights method"
    assert "DbtEventIterator" in return_type, (
        f"Return type should be DbtEventIterator, got: {return_type}"
    )
    assert "DbtDagsterEventType" in return_type, (
        f"Return type should be parameterized with DbtDagsterEventType, got: {return_type}"
    )
    assert "AssetCheckResult | AssetObservation" not in return_type, (
        f"Return type should use DbtDagsterEventType alias, not the full union, got: {return_type}"
    )


def test_component_imports_event_types():
    """Test that component.py imports DbtDagsterEventType and DbtEventIterator."""
    source = COMPONENT_FILE.read_text()
    tree = ast.parse(source)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "dbt_event_iterator" in module:
                for alias in node.names:
                    imports.append(alias.name)

    assert "DbtEventIterator" in imports, (
        f"component.py should import DbtEventIterator from dbt_event_iterator, found imports: {imports}"
    )
    assert "DbtDagsterEventType" in imports, (
        f"component.py should import DbtDagsterEventType from dbt_event_iterator, found imports: {imports}"
    )


def test_imports_are_callable():
    """Test that the imports actually work at runtime."""
    # Skip if dagster is not installed (type annotation fix doesn't require full dagster)
    try:
        import dagster
    except ImportError:
        pytest.skip("dagster package not installed - skipping runtime import test")

    sys.path.insert(0, str(REPO / "python_modules/libraries/dagster-dbt"))

    try:
        from dagster_dbt.core.dbt_event_iterator import DbtDagsterEventType, DbtEventIterator

        # Verify these are actual types
        assert DbtEventIterator is not None
        assert DbtDagsterEventType is not None

        # Check that DbtEventIterator has the expected methods
        assert hasattr(DbtEventIterator, 'fetch_row_counts')
        assert hasattr(DbtEventIterator, 'fetch_column_metadata')
        assert hasattr(DbtEventIterator, 'with_insights')
    finally:
        sys.path.pop(0)


def test_dbt_dagster_event_type_is_type_alias():
    """Test that DbtDagsterEventType is properly defined as a TypeAlias."""
    source = ITERATOR_FILE.read_text()

    # Check that DbtDagsterEventType is defined
    assert "DbtDagsterEventType: TypeAlias =" in source, (
        "DbtDagsterEventType should be defined as a TypeAlias"
    )

    # Check the union includes all expected types
    assert "Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation" in source, (
        "DbtDagsterEventType should include all expected event types in the correct order"
    )
