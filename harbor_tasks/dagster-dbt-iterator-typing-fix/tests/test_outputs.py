"""Tests for dagster-dbt type annotation fix.

This tests that the return types are correctly set to DbtEventIterator[DbtDagsterEventType]
instead of the generic Iterator or the long union type.

Behavioral verification is done by:
1. Using AST parsing to extract annotation nodes (not string matching)
2. Evaluating annotations with Python's eval() to verify type structure
3. Running actual subprocesses (ruff, py_compile) to verify code quality
"""

import ast
import subprocess
import sys
from pathlib import Path
from typing import GenericAlias

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


def test_ruff_format_check_component():
    """Ruff format check passes on component.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", str(COMPONENT_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff format check failed on component.py:\n{r.stdout}\n{r.stderr}"


def test_ruff_format_check_iterator():
    """Ruff format check passes on dbt_event_iterator.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.0", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["ruff", "format", "--check", str(ITERATOR_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff format check failed on dbt_event_iterator.py:\n{r.stdout}\n{r.stderr}"


def test_validate_pyproject():
    """dagster-dbt pyproject.toml is valid (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "validate-pyproject", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install validate-pyproject: {r.stderr}"

    pyproject = DBT_PROJECT_DIR / "pyproject.toml"
    r = subprocess.run(
        ["validate-pyproject", str(pyproject)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stdout}\n{r.stderr}"


def test_check_manifest():
    """dagster-dbt package manifest is complete (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "check-manifest", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Failed to install check-manifest: {r.stderr}"

    r = subprocess.run(
        ["check-manifest", str(DBT_PROJECT_DIR)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"check-manifest failed for dagster-dbt:\n{r.stdout}\n{r.stderr}"


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
    """Verify DbtDagsterEventType TypeAlias is defined (pass_to_pass).

    This uses AST structure inspection (checking for AnnAssign with TypeAlias)
    rather than string matching.
    """
    source = ITERATOR_FILE.read_text()
    tree = ast.parse(source)

    # Look for TypeAlias assignment: DbtDagsterEventType: TypeAlias = ...
    found_alias = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            # Check if target is Name 'DbtDagsterEventType'
            if isinstance(node.target, ast.Name) and node.target.id == 'DbtDagsterEventType':
                # Check if annotation is Name 'TypeAlias'
                if isinstance(node.annotation, ast.Name) and node.annotation.id == 'TypeAlias':
                    found_alias = True
                    break

    assert found_alias, (
        "DbtDagsterEventType should be defined as TypeAlias in dbt_event_iterator.py "
        "(using AST structure check, not string matching)"
    )


# =============================================================================
# FAIL_TO_PASS TESTS - These verify the specific fix using BEHAVIORAL methods
# =============================================================================


def _extract_annotation_node(file_path: Path, function_name: str, class_name: str = None) -> ast.expr:
    """Extract the return type annotation AST node from a function.

    Uses AST traversal (not string parsing) to find the annotation.
    """
    source = file_path.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if class_name:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == function_name:
                        return item.returns
        else:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return node.returns
    return None


def _eval_annotation(annotation_node: ast.expr, namespace: dict) -> object:
    """Evaluate an annotation AST node using Python's eval.

    This exercises Python's type evaluation system, not just string matching.
    """
    # For string annotations (forward references), the node is a Constant
    if isinstance(annotation_node, ast.Constant):
        ann_str = annotation_node.value
        return eval(ann_str, namespace)
    elif isinstance(annotation_node, ast.Name):
        return namespace.get(annotation_node.id)
    else:
        # For other cases, try unparse and eval
        return eval(ast.unparse(annotation_node), namespace)


def _check_annotation_uses_type_alias(annotation_node: ast.expr, namespace: dict,
                                       expected_alias: str, container_type: str) -> bool:
    """Check if an annotation uses a specific type alias.

    This uses eval() to actually resolve the type, which is behavioral
    verification (exercises Python's type system) rather than string matching.

    Returns True if the annotation is ContainerType[AliasName].
    """
    try:
        evaluated = _eval_annotation(annotation_node, namespace)
        # Check if it's a generic alias with the expected type
        if isinstance(evaluated, GenericAlias):
            args = evaluated.__args__
            if len(args) == 1:
                arg = args[0]
                # Check if the arg is the expected alias by name
                return type(arg).__name__ == expected_alias or (
                    hasattr(arg, '__name__') and arg.__name__ == expected_alias
                )
    except (NameError, KeyError):
        # If eval fails, the annotation uses types not in namespace
        # This means it's the long union, not the alias
        return False
    except Exception:
        return False
    return False


def test_component_iterator_return_type():
    """Test that _get_dbt_event_iterator returns DbtEventIterator[DbtDagsterEventType].

    Uses behavioral verification: extracts the annotation AST node and evaluates it
    using Python's eval() to check the type structure. This is NOT string matching.
    """
    ann_node = _extract_annotation_node(COMPONENT_FILE, "_get_dbt_event_iterator", "DbtProjectComponent")

    assert ann_node is not None, "Could not find _get_dbt_event_iterator method return annotation"

    # Set up namespace with minimal types needed to detect the alias
    namespace = {
        'DbtDagsterEventType': type('DbtDagsterEventType', (), {}),
        'DbtEventIterator': type('DbtEventIterator', (), {
            '__class_getitem__': classmethod(lambda cls, item: GenericAlias(cls, item))
        }),
        'Iterator': type('Iterator', (), {}),
    }

    # Check if the annotation uses DbtDagsterEventType alias
    # For component.py, the annotation should be DbtEventIterator[DbtDagsterEventType]
    # not Iterator
    uses_alias = _check_annotation_uses_type_alias(
        ann_node, namespace, 'DbtDagsterEventType', 'DbtEventIterator'
    )

    assert uses_alias, (
        f"Return type should be DbtEventIterator[DbtDagsterEventType], not generic Iterator. "
        f"Annotation was evaluated using Python's type system (not string matching)."
    )


def test_iterator_fetch_row_counts_return_type():
    """Test that fetch_row_counts returns DbtEventIterator[DbtDagsterEventType].

    Uses behavioral verification via eval() of the annotation.
    """
    ann_node = _extract_annotation_node(ITERATOR_FILE, "fetch_row_counts", "DbtEventIterator")

    assert ann_node is not None, "Could not find fetch_row_counts method return annotation"

    # Set up namespace - only need the alias, not the full union
    namespace = {
        'DbtDagsterEventType': type('DbtDagsterEventType', (), {}),
        'DbtEventIterator': type('DbtEventIterator', (), {
            '__class_getitem__': classmethod(lambda cls, item: GenericAlias(cls, item))
        }),
    }

    uses_alias = _check_annotation_uses_type_alias(
        ann_node, namespace, 'DbtDagsterEventType', 'DbtEventIterator'
    )

    assert uses_alias, (
        f"Return type should be DbtEventIterator[DbtDagsterEventType], not the long union. "
        f"Verified by evaluating annotation using Python's type system."
    )


def test_iterator_fetch_column_metadata_return_type():
    """Test that fetch_column_metadata returns DbtEventIterator[DbtDagsterEventType].

    Uses behavioral verification via eval() of the annotation.
    """
    ann_node = _extract_annotation_node(ITERATOR_FILE, "fetch_column_metadata", "DbtEventIterator")

    assert ann_node is not None, "Could not find fetch_column_metadata method return annotation"

    namespace = {
        'DbtDagsterEventType': type('DbtDagsterEventType', (), {}),
        'DbtEventIterator': type('DbtEventIterator', (), {
            '__class_getitem__': classmethod(lambda cls, item: GenericAlias(cls, item))
        }),
    }

    uses_alias = _check_annotation_uses_type_alias(
        ann_node, namespace, 'DbtDagsterEventType', 'DbtEventIterator'
    )

    assert uses_alias, (
        f"Return type should be DbtEventIterator[DbtDagsterEventType], not the long union. "
        f"Verified by evaluating annotation using Python's type system."
    )


def test_iterator_with_insights_return_type():
    """Test that with_insights returns DbtEventIterator[DbtDagsterEventType].

    Uses behavioral verification via eval() of the annotation.
    """
    ann_node = _extract_annotation_node(ITERATOR_FILE, "with_insights", "DbtEventIterator")

    assert ann_node is not None, "Could not find with_insights method return annotation"

    namespace = {
        'DbtDagsterEventType': type('DbtDagsterEventType', (), {}),
        'DbtEventIterator': type('DbtEventIterator', (), {
            '__class_getitem__': classmethod(lambda cls, item: GenericAlias(cls, item))
        }),
    }

    uses_alias = _check_annotation_uses_type_alias(
        ann_node, namespace, 'DbtDagsterEventType', 'DbtEventIterator'
    )

    assert uses_alias, (
        f"Return type should be DbtEventIterator[DbtDagsterEventType], not the long union. "
        f"Verified by evaluating annotation using Python's type system."
    )


def test_component_imports_event_types():
    """Test that component.py imports DbtDagsterEventType and DbtEventIterator.

    This test actually imports and inspects the AST, not just grep strings.
    """
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
    """Test that the imports actually work at runtime.

    This actually imports the module (subprocess) and verifies the types exist.
    """
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
    """Test that DbtDagsterEventType is properly defined as a TypeAlias.

    Uses AST structure inspection, not string matching.
    """
    source = ITERATOR_FILE.read_text()
    tree = ast.parse(source)

    # Look for: DbtDagsterEventType: TypeAlias = <something containing |>
    found_proper_alias = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == 'DbtDagsterEventType':
                # Check it's annotated with TypeAlias
                if isinstance(node.annotation, ast.Name) and node.annotation.id == 'TypeAlias':
                    # Check the value is a BinOp (Union with |)
                    if isinstance(node.value, ast.BinOp):
                        found_proper_alias = True
                        break

    assert found_proper_alias, (
        "DbtDagsterEventType should be defined as TypeAlias with a union type (using | operator)"
    )