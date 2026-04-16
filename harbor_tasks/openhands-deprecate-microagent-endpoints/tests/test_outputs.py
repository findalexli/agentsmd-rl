"""Tests for OpenHands microagent endpoints deprecation.

This module tests that the microagent repository endpoints are properly
marked as deprecated in the FastAPI routes by verifying OpenAPI schema behavior.
"""

import sys
import os
from pathlib import Path
import subprocess
import json
import re

# Add the openhands directory to path
REPO = Path("/workspace/openhands")
sys.path.insert(0, str(REPO))

GIT_ROUTES_FILE = REPO / "openhands" / "server" / "routes" / "git.py"


def _get_openapi_schema_with_deprecation_check():
    """Create a minimal FastAPI app with the git router and get its OpenAPI schema.

    Returns a dict with 'deprecated' boolean for each microagents endpoint path.
    """
    # We need to run this in a subprocess because the module has complex dependencies
    # that can't be imported directly in the test environment
    script = '''
import sys
from pathlib import Path
import json

# Set up minimal environment
sys.path.insert(0, str(Path(__file__).parent.parent))

# Create a minimal FastAPI app that includes the git router
from fastapi import FastAPI

# Import the router - this may fail if dependencies aren't fully installed
try:
    from openhands.server.routes.git import app as git_router

    app = FastAPI()
    app.include_router(git_router)

    # Get the OpenAPI schema
    schema = app.openapi()

    # Check the microagents endpoints
    paths = schema.get("paths", {})
    result = {}

    for path, methods in paths.items():
        if "microagents" in path and isinstance(methods, dict):
            for method, details in methods.items():
                if method in ("get", "post", "put", "delete", "patch"):
                    result[f"{method.upper()} {path}"] = details.get("deprecated", False)

    print("OPENAPI_RESULT:" + json.dumps(result))

except Exception as e:
    print(f"ERROR:{type(e).__name__}:{str(e)}", file=sys.stderr)
    sys.exit(1)
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=60
    )

    if result.returncode != 0:
        # Fallback: try to at least check the AST for deprecated=True
        return _check_deprecated_via_ast()

    output = result.stdout.strip()
    if output.startswith("OPENAPI_RESULT:"):
        data = json.loads(output[len("OPENAPI_RESULT:"):])
        return data
    elif output.startswith("ERROR:"):
        # Import failed, fall back to AST check
        return _check_deprecated_via_ast()

    return {}


def _check_deprecated_via_ast():
    """Fallback: Check if deprecated=True appears in decorators via AST.

    Returns a dict mapping route path+method to deprecated status.
    """
    import ast

    content = GIT_ROUTES_FILE.read_text()
    tree = ast.parse(content)

    result = {}

    class RouteVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            self._check_function(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node):
            self._check_function(node)
            self.generic_visit(node)

        def _check_function(self, node):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'get':
                        # Check path argument
                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                            path = decorator.args[0].value
                            if 'microagents' in path:
                                # Check for deprecated=True
                                for kw in decorator.keywords:
                                    if kw.arg == 'deprecated':
                                        if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                            result[f'GET {path}'] = True
                                        elif isinstance(kw.value, ast.NameConstant) and kw.value.value is True:
                                            result[f'GET {path}'] = True

    RouteVisitor().visit(tree)
    return result


def test_microagents_endpoint_deprecated_flag():
    """Test that GET /repository/{repository_name}/microagents has deprecated=True via OpenAPI schema."""
    schema_info = _get_openapi_schema_with_deprecation_check()

    # Check for the microagents list endpoint
    list_endpoint_found = False
    list_endpoint_deprecated = False

    for path_method, is_deprecated in schema_info.items():
        if '/microagents' in path_method and 'content' not in path_method and 'GET' in path_method:
            list_endpoint_found = True
            list_endpoint_deprecated = is_deprecated
            break

    if not list_endpoint_found:
        # Fallback check via AST if OpenAPI schema couldn't be generated
        import ast
        content = GIT_ROUTES_FILE.read_text()
        tree = ast.parse(content)

        class DeprecatedChecker(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                self._check_function(node)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self._check_function(node)
                self.generic_visit(node)

            def _check_function(self, node):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'get':
                            if decorator.args and isinstance(decorator.args[0], ast.Constant) and 'microagents' in decorator.args[0].value and 'content' not in decorator.args[0].value:
                                for kw in decorator.keywords:
                                    if kw.arg == 'deprecated' and kw.value.value is True:
                                        raise ast.NodeVisitor()
                self.generic_visit(node)

        try:
            DeprecatedChecker().visit(tree)
        except:
            pass
        else:
            assert False, "Could not verify deprecation status via OpenAPI schema or AST"

    assert list_endpoint_found, "Microagents list endpoint not found in OpenAPI schema"
    assert list_endpoint_deprecated, "Microagents list endpoint should have deprecated=True in OpenAPI schema"


def test_microagents_content_endpoint_deprecated_flag():
    """Test that GET /repository/{repository_name}/microagents/content has deprecated=True via OpenAPI schema."""
    schema_info = _get_openapi_schema_with_deprecation_check()

    # Check for the microagents content endpoint
    content_endpoint_found = False
    content_endpoint_deprecated = False

    for path_method, is_deprecated in schema_info.items():
        if '/microagents/content' in path_method and 'GET' in path_method:
            content_endpoint_found = True
            content_endpoint_deprecated = is_deprecated
            break

    if not content_endpoint_found:
        # Fallback check via AST if OpenAPI schema couldn't be generated
        import ast
        content = GIT_ROUTES_FILE.read_text()
        tree = ast.parse(content)

        class DeprecatedChecker(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                self._check_function(node)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self._check_function(node)
                self.generic_visit(node)

            def _check_function(self, node):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'get':
                            if decorator.args and isinstance(decorator.args[0], ast.Constant) and 'microagents/content' in decorator.args[0].value:
                                for kw in decorator.keywords:
                                    if kw.arg == 'deprecated' and kw.value.value is True:
                                        raise ast.NodeVisitor()
                self.generic_visit(node)

        try:
            DeprecatedChecker().visit(tree)
        except:
            pass
        else:
            assert False, "Could not verify deprecation status via OpenAPI schema or AST"

    assert content_endpoint_found, "Microagents content endpoint not found in OpenAPI schema"
    assert content_endpoint_deprecated, "Microagents content endpoint should have deprecated=True in OpenAPI schema"


def test_microagents_endpoint_has_deprecation_notice():
    """Test that microagents endpoint docstring contains some deprecation notice (behavioral check).

    This checks that a deprecation notice exists without requiring specific gold text,
    since alternative correct fixes might phrase the notice differently.
    """
    import ast

    content = GIT_ROUTES_FILE.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'get_repository_microagents':
            docstring = ast.get_docstring(node) or ""

            # Check for presence of deprecation-related content
            # Without being specific about exact wording (to allow alternative phrasings)
            has_deprecation_notice = (
                "deprecated" in docstring.lower() or
                "deprecation" in docstring.lower() or
                "microagents ui" in docstring.lower() or
                "not supported" in docstring.lower()
            )

            assert has_deprecation_notice, (
                "Microagents endpoint docstring should contain a deprecation notice. "
                "Found docstring: " + docstring[:200]
            )
            return

    assert False, "get_repository_microagents function not found"


def test_microagents_content_endpoint_has_deprecation_notice():
    """Test that microagents content endpoint docstring contains some deprecation notice.

    This checks that a deprecation notice exists without requiring specific gold text,
    since alternative correct fixes might phrase the notice differently.
    """
    import ast

    content = GIT_ROUTES_FILE.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'get_repository_microagent_content':
            docstring = ast.get_docstring(node) or ""

            # Check for presence of deprecation-related content
            has_deprecation_notice = (
                "deprecated" in docstring.lower() or
                "deprecation" in docstring.lower() or
                "microagents ui" in docstring.lower() or
                "not supported" in docstring.lower()
            )

            assert has_deprecation_notice, (
                "Microagents content endpoint docstring should contain a deprecation notice. "
                "Found docstring: " + docstring[:200]
            )
            return

    assert False, "get_repository_microagent_content function not found"


def test_file_syntax_valid():
    """Test that the modified file has valid Python syntax."""
    content = GIT_ROUTES_FILE.read_text()

    # Parse to check syntax
    try:
        import ast
        ast.parse(content)
    except SyntaxError as e:
        raise AssertionError(f"Invalid Python syntax: {e}")


def test_functions_exist():
    """Test that both endpoint functions exist in the file."""
    content = GIT_ROUTES_FILE.read_text()

    for func_name in ['get_repository_microagents', 'get_repository_microagent_content']:
        pattern = rf'(?:async\s+)?def\s+{func_name}\s*\('
        assert re.search(pattern, content), f"{func_name} function should exist in the file"


# =============================================================================
# Pass-to-Pass Tests: Repo CI Commands
# =============================================================================
# These tests run actual CI commands from the repository's CI pipeline to ensure
# the codebase passes quality checks on the base commit (existing functionality).


def test_repo_ruff_lint():
    """Repo's ruff linter passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    if r.returncode != 0:
        # pip install failure is not a test failure - continue
        pass

    r = subprocess.run(
        ["ruff", "check", "--config", "dev_config/python/ruff.toml", "openhands/server/routes/git.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr}\n{r.stdout}"


def test_repo_py_compile():
    """Modified file has valid Python syntax via py_compile (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "openhands/server/routes/git.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"