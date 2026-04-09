"""Tests for dagster-dbt type annotation fix.

This tests that the return types are correctly set to DbtEventIterator[DbtDagsterEventType]
instead of the generic Iterator or the long union type.
"""

import ast
import inspect
import sys
from pathlib import Path

# Paths to the modified files
REPO = Path("/workspace/dagster")
COMPONENT_FILE = REPO / "python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py"
ITERATOR_FILE = REPO / "python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py"


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
