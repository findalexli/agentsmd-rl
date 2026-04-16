"""
Tests for superset-mcp-null-fields task.

These tests verify that:
1. DAO list() method handles Python @property columns correctly
2. Schema serializers properly rename schema_name -> schema
3. Default dataset columns include database_name for eager loading

Note: We read and parse files directly to avoid importing the full superset
package which has many heavy dependencies (alembic, flask, etc.).
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/superset")


def get_file_content(path: str) -> str:
    """Read file content from the repository."""
    full_path = REPO / path
    if not full_path.exists():
        raise FileNotFoundError(f"File not found: {full_path}")
    return full_path.read_text()


def parse_python_file(path: str) -> ast.Module:
    """Parse Python file into AST."""
    content = get_file_content(path)
    return ast.parse(content)


# ============================================================================
# Tests for sql_lab/schemas.py
# ============================================================================

def test_schema_field_normalizer_exists():
    """
    Test that _SchemaFieldNormalizer mixin class exists in sql_lab schemas.
    (fail_to_pass)
    """
    tree = parse_python_file("superset/mcp_service/sql_lab/schemas.py")

    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "_SchemaFieldNormalizer" in class_names, \
        f"Expected '_SchemaFieldNormalizer' class, found classes: {class_names}"


def test_schema_field_normalizer_has_serializer():
    """
    Test that _SchemaFieldNormalizer has a model_serializer method.
    (fail_to_pass)
    """
    content = get_file_content("superset/mcp_service/sql_lab/schemas.py")

    # Check for model_serializer decorator usage within _SchemaFieldNormalizer
    assert "@model_serializer" in content, \
        "Expected @model_serializer decorator in schemas.py"

    # Check for the normalize function
    assert "_normalize_schema_field" in content or "schema_name" in content and "schema" in content, \
        "Expected schema normalization logic in schemas.py"


def test_save_sql_query_response_inherits_normalizer():
    """
    Test that SaveSqlQueryResponse inherits from _SchemaFieldNormalizer.
    (fail_to_pass)
    """
    tree = parse_python_file("superset/mcp_service/sql_lab/schemas.py")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SaveSqlQueryResponse":
            # Check base classes
            base_names = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)

            assert "_SchemaFieldNormalizer" in base_names, \
                f"SaveSqlQueryResponse should inherit from _SchemaFieldNormalizer, but bases are: {base_names}"
            return

    raise AssertionError("SaveSqlQueryResponse class not found")


def test_sql_lab_response_inherits_normalizer():
    """
    Test that SqlLabResponse inherits from _SchemaFieldNormalizer.
    (fail_to_pass)
    """
    tree = parse_python_file("superset/mcp_service/sql_lab/schemas.py")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SqlLabResponse":
            # Check base classes
            base_names = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)

            assert "_SchemaFieldNormalizer" in base_names, \
                f"SqlLabResponse should inherit from _SchemaFieldNormalizer, but bases are: {base_names}"
            return

    raise AssertionError("SqlLabResponse class not found")


def test_save_sql_query_request_has_populate_by_name():
    """
    Test that SaveSqlQueryRequest has populate_by_name=True in model_config.
    (fail_to_pass)
    """
    content = get_file_content("superset/mcp_service/sql_lab/schemas.py")

    # Find the SaveSqlQueryRequest class and check for populate_by_name
    # Look for the pattern: class SaveSqlQueryRequest ... model_config = ConfigDict(populate_by_name=True)

    # Split by class definitions
    class_pattern = r"class SaveSqlQueryRequest\b[^:]*:.*?(?=\nclass |\Z)"
    match = re.search(class_pattern, content, re.DOTALL)

    assert match is not None, "SaveSqlQueryRequest class not found"
    class_content = match.group(0)

    assert "populate_by_name" in class_content and "True" in class_content, \
        f"SaveSqlQueryRequest should have populate_by_name=True in model_config"


def test_save_sql_query_response_has_populate_by_name():
    """
    Test that SaveSqlQueryResponse has populate_by_name=True in model_config.
    (fail_to_pass)
    """
    content = get_file_content("superset/mcp_service/sql_lab/schemas.py")

    class_pattern = r"class SaveSqlQueryResponse\b[^:]*:.*?(?=\nclass |\Z)"
    match = re.search(class_pattern, content, re.DOTALL)

    assert match is not None, "SaveSqlQueryResponse class not found"
    class_content = match.group(0)

    assert "populate_by_name" in class_content and "True" in class_content, \
        f"SaveSqlQueryResponse should have populate_by_name=True in model_config"


# ============================================================================
# Tests for list_datasets.py
# ============================================================================

def test_default_dataset_columns_includes_database():
    """
    Test that DEFAULT_DATASET_COLUMNS includes 'database' for eager loading.
    (fail_to_pass)
    """
    content = get_file_content("superset/mcp_service/dataset/tool/list_datasets.py")

    # Find DEFAULT_DATASET_COLUMNS definition
    pattern = r"DEFAULT_DATASET_COLUMNS\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, "DEFAULT_DATASET_COLUMNS not found"
    columns_str = match.group(1)

    # Check for "database" in the list
    assert '"database"' in columns_str or "'database'" in columns_str, \
        f"Expected 'database' in DEFAULT_DATASET_COLUMNS for eager loading"


def test_default_dataset_columns_includes_database_name():
    """
    Test that DEFAULT_DATASET_COLUMNS includes 'database_name'.
    (fail_to_pass)
    """
    content = get_file_content("superset/mcp_service/dataset/tool/list_datasets.py")

    pattern = r"DEFAULT_DATASET_COLUMNS\s*=\s*\[(.*?)\]"
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, "DEFAULT_DATASET_COLUMNS not found"
    columns_str = match.group(1)

    assert '"database_name"' in columns_str or "'database_name'" in columns_str, \
        f"Expected 'database_name' in DEFAULT_DATASET_COLUMNS"


# ============================================================================
# Tests for daos/base.py
# ============================================================================

def test_dao_handles_property_descriptors():
    """
    Test that the DAO list() method handles Python @property descriptors.
    (fail_to_pass)
    """
    content = get_file_content("superset/daos/base.py")

    # Check for needs_full_model logic
    assert "needs_full_model" in content, \
        "Expected 'needs_full_model' variable in DAO base.py to handle @property descriptors"


def test_dao_checks_for_property_or_descriptor():
    """
    Test that the DAO list() method checks for @property or other descriptors.
    (fail_to_pass)
    """
    content = get_file_content("superset/daos/base.py")

    # The fix adds an else clause that sets needs_full_model = True
    # when the attribute is neither ColumnProperty nor RelationshipProperty
    # Look for comment about @property or descriptor
    assert "@property" in content.lower() or "descriptor" in content.lower(), \
        "Expected comment about @property or descriptors in DAO base.py"


def test_dao_uses_needs_full_model_in_query():
    """
    Test that needs_full_model is used in the query construction.
    (fail_to_pass)
    """
    content = get_file_content("superset/daos/base.py")

    # Check that needs_full_model is used in an if condition
    assert "if relationship_loads or needs_full_model" in content or \
           "needs_full_model or relationship_loads" in content, \
        "Expected 'if relationship_loads or needs_full_model' in query construction"


# ============================================================================
# Pass-to-pass tests - static file checks
# ============================================================================

def test_schemas_file_exists():
    """
    Test that SQL Lab schemas file exists (pass_to_pass).
    """
    path = REPO / "superset/mcp_service/sql_lab/schemas.py"
    assert path.exists(), f"File not found: {path}"


def test_list_datasets_file_exists():
    """
    Test that list_datasets file exists (pass_to_pass).
    """
    path = REPO / "superset/mcp_service/dataset/tool/list_datasets.py"
    assert path.exists(), f"File not found: {path}"


def test_dao_base_file_exists():
    """
    Test that DAO base file exists (pass_to_pass).
    """
    path = REPO / "superset/daos/base.py"
    assert path.exists(), f"File not found: {path}"


def test_schemas_file_is_valid_python():
    """
    Test that schemas.py is valid Python syntax (pass_to_pass).
    """
    try:
        parse_python_file("superset/mcp_service/sql_lab/schemas.py")
    except SyntaxError as e:
        raise AssertionError(f"schemas.py has invalid Python syntax: {e}")


def test_list_datasets_file_is_valid_python():
    """
    Test that list_datasets.py is valid Python syntax (pass_to_pass).
    """
    try:
        parse_python_file("superset/mcp_service/dataset/tool/list_datasets.py")
    except SyntaxError as e:
        raise AssertionError(f"list_datasets.py has invalid Python syntax: {e}")


# ============================================================================
# Pass-to-pass tests - actual CI commands (repo_tests)
# ============================================================================

def test_ruff_lint_modified_files():
    """
    Run ruff linter on the files modified by this PR (pass_to_pass).
    Uses the project's ruff configuration from pyproject.toml.
    """
    # First ensure ruff is installed
    install_result = subprocess.run(
        ["pip", "install", "ruff"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if install_result.returncode != 0:
        raise AssertionError(f"Failed to install ruff: {install_result.stderr}")

    # Run ruff check on the modified files
    result = subprocess.run(
        [
            "ruff", "check",
            "superset/daos/base.py",
            "superset/mcp_service/sql_lab/schemas.py",
            "superset/mcp_service/dataset/tool/list_datasets.py",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr}"


def test_python_syntax_modified_files():
    """
    Validate Python syntax on modified files using py_compile (pass_to_pass).
    """
    result = subprocess.run(
        [
            "python", "-m", "py_compile",
            "superset/daos/base.py",
            "superset/mcp_service/sql_lab/schemas.py",
            "superset/mcp_service/dataset/tool/list_datasets.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Python syntax validation failed:\n{result.stderr}"


def test_ruff_lint_mcp_service():
    """
    Run ruff linter on the entire mcp_service directory (pass_to_pass).
    Ensures no lint errors are introduced in the MCP service code.
    """
    # Ensure ruff is installed
    subprocess.run(["pip", "install", "ruff"], capture_output=True, timeout=120)

    result = subprocess.run(
        ["ruff", "check", "superset/mcp_service/"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff lint on mcp_service failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_lint_daos():
    """
    Run ruff linter on the entire daos directory (pass_to_pass).
    Ensures no lint errors are introduced in DAO code.
    """
    # Ensure ruff is installed
    subprocess.run(["pip", "install", "ruff"], capture_output=True, timeout=120)

    result = subprocess.run(
        ["ruff", "check", "superset/daos/"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff lint on daos failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
