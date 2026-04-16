"""
Tests for superset-mcp-chart-type-schema task.

These tests verify that the get_chart_type_schema MCP tool is properly implemented.
Uses AST-based structural checks since the full Superset environment isn't available.
"""

import ast
import os
import re
import pytest

REPO = "/workspace/superset"
MODULE_PATH = os.path.join(
    REPO,
    "superset/mcp_service/chart/tool/get_chart_type_schema.py"
)


def get_module_content():
    """Read the module file content if it exists."""
    if not os.path.isfile(MODULE_PATH):
        return None
    with open(MODULE_PATH, "r") as f:
        return f.read()


def parse_module_ast():
    """Parse the module AST if file exists and is valid Python."""
    content = get_module_content()
    if content is None:
        return None
    try:
        return ast.parse(content)
    except SyntaxError:
        return None


class TestGetChartTypeSchemaModuleExists:
    """Test that the get_chart_type_schema module exists (fail_to_pass)."""

    def test_module_file_exists(self):
        """The get_chart_type_schema.py module file must exist."""
        assert os.path.isfile(MODULE_PATH), (
            f"Module file not found at {MODULE_PATH}. "
            "The get_chart_type_schema tool must be implemented."
        )


class TestGetChartTypeSchemaExported:
    """Test that get_chart_type_schema is exported from the tools module (fail_to_pass)."""

    def test_function_in_init_exports(self):
        """The function must be exported in chart/tool/__init__.py."""
        init_path = os.path.join(
            REPO,
            "superset/mcp_service/chart/tool/__init__.py"
        )
        with open(init_path, "r") as f:
            content = f.read()

        # Check that it's imported
        assert "get_chart_type_schema" in content, (
            "get_chart_type_schema must be imported in "
            "superset/mcp_service/chart/tool/__init__.py"
        )

        # Check it's in __all__
        assert '"get_chart_type_schema"' in content or "'get_chart_type_schema'" in content, (
            "get_chart_type_schema must be added to __all__ in "
            "superset/mcp_service/chart/tool/__init__.py"
        )


class TestGetChartTypeSchemaRegisteredInApp:
    """Test that get_chart_type_schema is registered in app.py (fail_to_pass)."""

    def test_imported_in_app(self):
        """The tool must be imported in mcp_service/app.py for MCP registration."""
        app_path = os.path.join(REPO, "superset/mcp_service/app.py")
        with open(app_path, "r") as f:
            content = f.read()

        assert "get_chart_type_schema" in content, (
            "get_chart_type_schema must be imported in superset/mcp_service/app.py "
            "for automatic MCP tool registration"
        )


class TestImplFunctionDefined:
    """Test that _get_chart_type_schema_impl function is defined (fail_to_pass)."""

    def test_impl_function_exists_in_ast(self):
        """The _get_chart_type_schema_impl function must be defined."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        tree = parse_module_ast()
        if tree is None:
            pytest.fail("Module has syntax errors")

        # Find function definitions
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        assert "_get_chart_type_schema_impl" in func_names, (
            "_get_chart_type_schema_impl function must be defined"
        )


class TestValidChartTypesConstant:
    """Test that VALID_CHART_TYPES constant is defined (fail_to_pass)."""

    def test_valid_chart_types_defined(self):
        """VALID_CHART_TYPES constant must be defined."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        assert "VALID_CHART_TYPES" in content, (
            "VALID_CHART_TYPES constant must be defined"
        )

    def test_seven_chart_types_in_adapters(self):
        """_CHART_TYPE_ADAPTERS must define all 7 chart types."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check for all 7 chart types in _CHART_TYPE_ADAPTERS
        expected_types = ["xy", "table", "pie", "pivot_table", "mixed_timeseries", "handlebars", "big_number"]
        for chart_type in expected_types:
            pattern = rf'["\']({chart_type})["\']'
            assert re.search(pattern, content), (
                f"Chart type '{chart_type}' must be defined in _CHART_TYPE_ADAPTERS"
            )


class TestXYChartTypeAdapter:
    """Test XY chart type adapter is defined (fail_to_pass)."""

    def test_xy_type_adapter_uses_xychartconfig(self):
        """XY chart type adapter must use XYChartConfig."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check that XYChartConfig is imported
        assert "XYChartConfig" in content, (
            "XYChartConfig must be imported"
        )

        # Check that xy type uses XYChartConfig
        assert re.search(r'["\']xy["\']\s*:\s*TypeAdapter\(XYChartConfig\)', content), (
            "xy chart type must use TypeAdapter(XYChartConfig)"
        )


class TestPieChartTypeAdapter:
    """Test Pie chart type adapter is defined (fail_to_pass)."""

    def test_pie_type_adapter_uses_piechartconfig(self):
        """Pie chart type adapter must use PieChartConfig."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check that PieChartConfig is imported
        assert "PieChartConfig" in content, (
            "PieChartConfig must be imported"
        )

        # Check that pie type uses PieChartConfig
        assert re.search(r'["\']pie["\']\s*:\s*TypeAdapter\(PieChartConfig\)', content), (
            "pie chart type must use TypeAdapter(PieChartConfig)"
        )


class TestInvalidTypeHandling:
    """Test error handling for invalid chart types (fail_to_pass)."""

    def test_impl_returns_error_for_invalid_type(self):
        """Implementation must return error dict for invalid chart types."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check that the implementation handles None adapter case
        assert "adapter is None" in content or "adapter is None:" in content or 'if adapter is None' in content, (
            "Implementation must check for None adapter (invalid chart type)"
        )

        # Check that it returns error with valid_chart_types
        assert '"error"' in content or "'error'" in content, (
            "Implementation must return 'error' key for invalid types"
        )

        assert '"valid_chart_types"' in content or "'valid_chart_types'" in content, (
            "Error response must include 'valid_chart_types' key"
        )


class TestIncludeExamplesParameter:
    """Test include_examples parameter (fail_to_pass)."""

    def test_include_examples_parameter_defined(self):
        """include_examples parameter must be defined on impl function."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        tree = parse_module_ast()
        if tree is None:
            pytest.fail("Module has syntax errors")

        # Find the _get_chart_type_schema_impl function
        impl_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_get_chart_type_schema_impl":
                impl_func = node
                break

        assert impl_func is not None, "_get_chart_type_schema_impl must be defined"

        # Check for include_examples parameter
        arg_names = [arg.arg for arg in impl_func.args.args]
        assert "include_examples" in arg_names, (
            "include_examples parameter must be defined"
        )

    def test_include_examples_controls_examples_in_response(self):
        """include_examples must control whether examples are included."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check that examples are conditionally added based on include_examples
        assert "if include_examples" in content, (
            "Examples must be conditionally added based on include_examples"
        )


class TestChartExamplesDefined:
    """Test that chart examples are defined (fail_to_pass)."""

    def test_chart_examples_dict_defined(self):
        """_CHART_EXAMPLES dict must be defined with examples for each type."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        assert "_CHART_EXAMPLES" in content, (
            "_CHART_EXAMPLES dict must be defined"
        )

    def test_examples_have_chart_type_field(self):
        """Examples must have chart_type field matching the type."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check for chart_type field in example dicts
        # Look for patterns like "chart_type": "xy" or 'chart_type': 'pie'
        expected_types = ["xy", "table", "pie", "pivot_table", "mixed_timeseries", "handlebars", "big_number"]
        for chart_type in expected_types:
            pattern = rf'"chart_type":\s*"{chart_type}"'
            assert re.search(pattern, content), (
                f"Example for '{chart_type}' must have 'chart_type': '{chart_type}'"
            )


class TestApacheLicenseHeader:
    """Test that the module has Apache license header (fail_to_pass)."""

    def test_module_has_license_header(self):
        """The get_chart_type_schema.py module must have Apache license header."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check for Apache license header
        assert "Licensed to the Apache Software Foundation" in content, (
            "Module must have Apache Software Foundation license header"
        )
        assert "Apache License, Version 2.0" in content, (
            "Module must reference Apache License, Version 2.0"
        )


class TestTypeAdaptersUsed:
    """Test that Pydantic TypeAdapters are used (fail_to_pass)."""

    def test_chart_type_adapters_defined(self):
        """_CHART_TYPE_ADAPTERS dict must be defined with TypeAdapters."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        assert "_CHART_TYPE_ADAPTERS" in content, (
            "Module must define _CHART_TYPE_ADAPTERS dict"
        )
        assert "TypeAdapter" in content, (
            "Module must use pydantic TypeAdapter"
        )
        assert "from pydantic import TypeAdapter" in content, (
            "Module must import TypeAdapter from pydantic"
        )


class TestToolDecoratorUsed:
    """Test that @tool decorator is used (fail_to_pass)."""

    def test_tool_decorator_applied(self):
        """The get_chart_type_schema function must use @tool decorator."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check for @tool decorator
        assert "@tool" in content, (
            "get_chart_type_schema must use @tool decorator"
        )

    def test_tool_decorator_imported(self):
        """tool decorator must be imported from superset_core."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check for import from superset_core.mcp.decorators
        assert "from superset_core" in content, (
            "tool decorator must be imported from superset_core"
        )


class TestPublicFunctionDefined:
    """Test that get_chart_type_schema public function is defined (fail_to_pass)."""

    def test_public_function_exists(self):
        """get_chart_type_schema public function must be defined."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        tree = parse_module_ast()
        if tree is None:
            pytest.fail("Module has syntax errors")

        # Find function definitions
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]

        assert "get_chart_type_schema" in func_names, (
            "get_chart_type_schema public function must be defined"
        )

    def test_public_function_has_docstring(self):
        """get_chart_type_schema must have a docstring."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        tree = parse_module_ast()
        if tree is None:
            pytest.fail("Module has syntax errors")

        # Find the get_chart_type_schema function
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_chart_type_schema":
                docstring = ast.get_docstring(node)
                assert docstring is not None and len(docstring) > 20, (
                    "get_chart_type_schema must have a meaningful docstring"
                )
                return

        pytest.fail("get_chart_type_schema function not found")


class TestSchemaGeneration:
    """Test that schema is properly generated (fail_to_pass)."""

    def test_json_schema_method_called(self):
        """Implementation must call json_schema() on adapter."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        assert "json_schema()" in content or ".json_schema(" in content, (
            "Implementation must call json_schema() to generate schema"
        )

    def test_schema_included_in_result(self):
        """Result dict must include 'schema' key."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        # Check that schema is included in result
        assert '"schema"' in content or "'schema'" in content, (
            "Result must include 'schema' key"
        )


class TestToolAnnotations:
    """Test that ToolAnnotations are used for metadata (fail_to_pass)."""

    def test_tool_annotations_used(self):
        """Tool must use ToolAnnotations for LLM-friendly metadata."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        assert "ToolAnnotations" in content, (
            "Tool must use ToolAnnotations for metadata"
        )

    def test_readonly_hint_set(self):
        """Tool must set readOnlyHint=True since it's a read operation."""
        content = get_module_content()
        if content is None:
            pytest.fail("get_chart_type_schema module does not exist")

        assert "readOnlyHint" in content and "True" in content, (
            "Tool must set readOnlyHint=True"
        )


# =============================================================================
# Pass-to-Pass Tests: Repo CI commands that must pass before and after the fix
# =============================================================================
import subprocess


class TestRepoRuffLint:
    """Test that ruff linting passes on mcp_service code (pass_to_pass)."""

    def test_ruff_check_mcp_service_chart_tool(self):
        """Ruff linter passes on mcp_service/chart/tool directory."""
        # Install ruff if not available and run check
        install_result = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        result = subprocess.run(
            ["ruff", "check", "superset/mcp_service/chart/tool/"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Ruff lint failed on mcp_service/chart/tool:\n{result.stdout}\n{result.stderr[-500:]}"
        )

    def test_ruff_check_mcp_service_app(self):
        """Ruff linter passes on mcp_service/app.py."""
        result = subprocess.run(
            ["ruff", "check", "superset/mcp_service/app.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Ruff lint failed on app.py:\n{result.stdout}\n{result.stderr[-500:]}"
        )


class TestRepoRuffFormat:
    """Test that ruff formatting passes on mcp_service code (pass_to_pass)."""

    def test_ruff_format_check_mcp_service_chart_tool(self):
        """Ruff formatting check passes on mcp_service/chart/tool directory."""
        result = subprocess.run(
            ["ruff", "format", "--check", "superset/mcp_service/chart/tool/"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Ruff format check failed on mcp_service/chart/tool:\n{result.stdout}\n{result.stderr[-500:]}"
        )


class TestRepoPythonSyntax:
    """Test Python syntax validity on modified files (pass_to_pass)."""

    def test_python_syntax_chart_tool_init(self):
        """Python syntax is valid in chart/tool/__init__.py."""
        result = subprocess.run(
            ["python", "-m", "py_compile", "superset/mcp_service/chart/tool/__init__.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Python syntax error in __init__.py:\n{result.stderr[-500:]}"
        )

    def test_python_syntax_mcp_app(self):
        """Python syntax is valid in mcp_service/app.py."""
        result = subprocess.run(
            ["python", "-m", "py_compile", "superset/mcp_service/app.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Python syntax error in app.py:\n{result.stderr[-500:]}"
        )
