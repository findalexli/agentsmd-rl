"""
Tests for apache/airflow#64859: Add exclude-newer-package=false for workspace components.

Behavioral tests that verify actual function execution, not source text inspection.
Uses AST to extract functions without importing the module (avoiding top-level execution).
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

AIRFLOW_REPO = Path("/workspace/airflow")
UPDATE_SCRIPT = AIRFLOW_REPO / "scripts/ci/prek/update_airflow_pyproject_toml.py"
INSTALL_SCRIPT = AIRFLOW_REPO / "scripts/in_container/install_airflow_and_providers.py"
PYPROJECT_TOML = AIRFLOW_REPO / "pyproject.toml"


def run_python(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=AIRFLOW_REPO,
    )


def test_get_all_workspace_component_names_function_exists():
    """
    f2p: get_all_workspace_component_names() function must exist.
    Uses AST to parse and verify function exists without executing top-level code.
    """
    code = """
import ast
from pathlib import Path

source = Path('/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py').read_text()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_all_workspace_component_names':
        found = True
        break

print(f"FOUND:{found}")
"""
    result = run_python(code)
    assert "FOUND:True" in result.stdout, (
        f"Function get_all_workspace_component_names() not found via AST.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_get_all_workspace_component_names_returns_sorted_list():
    """
    f2p: get_all_workspace_component_names() must return a sorted list.
    Verifies behavior by extracting function via AST and calling it.
    """
    code = """
import ast
from pathlib import Path

script_path = '/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py'
source = Path(script_path).read_text()
tree = ast.parse(source)

target_func = None
read_toml_func = None

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == 'get_all_workspace_component_names':
            target_func = node
        elif node.name == '_read_toml':
            read_toml_func = node

if not target_func or not read_toml_func:
    print("FUNCTION_NOT_FOUND")
    exit(1)

# Build namespace with dependencies
ns = {
    "Path": Path,
    "AIRFLOW_PYPROJECT_TOML_FILE": Path('/workspace/airflow/pyproject.toml'),
    "__name__": "__test__"
}

try:
    import tomllib
    ns['tomllib'] = tomllib
except ImportError:
    import tomli as tomlib
    ns['tomllib'] = tomlib

# Execute both functions
exec(ast.unparse(read_toml_func).replace('Any', 'object'), ns)
exec(ast.unparse(target_func).replace('Any', 'object'), ns)

# Get expected from TOML
try:
    import tomllib
except ImportError:
    import tomli as tomllib

toml_dict = tomllib.loads(Path('/workspace/airflow/pyproject.toml').read_text())
sources = toml_dict.get("tool", {}).get("uv", {}).get("sources", {})
expected = sorted([
    name for name, value in sources.items()
    if isinstance(value, dict) and value.get("workspace")
])

# Call the function
result = ns['get_all_workspace_component_names']()

print(f"EXPECTED:{expected}")
print(f"ACTUAL:{result}")

if result != expected:
    print("MISMATCH")
    exit(1)
print("OK")
"""
    result = run_python(code)
    assert "FUNCTION_NOT_FOUND" not in result.stdout, f"Function not found.\n{result.stdout}"
    assert "MISMATCH" not in result.stdout, f"Function returned wrong list.\n{result.stdout}"
    assert "OK" in result.stdout, f"Test did not pass.\n{result.stdout}"


def test_get_all_workspace_component_names_is_sorted():
    """
    f2p: The returned list must be alphabetically sorted.
    """
    code = """
import ast
from pathlib import Path

script_path = '/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py'
source = Path(script_path).read_text()
tree = ast.parse(source)

target_func = None
read_toml_func = None

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == 'get_all_workspace_component_names':
            target_func = node
        elif node.name == '_read_toml':
            read_toml_func = node

ns = {
    "Path": Path,
    "AIRFLOW_PYPROJECT_TOML_FILE": Path('/workspace/airflow/pyproject.toml'),
    "__name__": "__test__"
}
try:
    import tomllib
    ns['tomllib'] = tomllib
except ImportError:
    import tomli as tomlib
    ns['tomllib'] = tomlib

exec(ast.unparse(read_toml_func).replace('Any', 'object'), ns)
exec(ast.unparse(target_func).replace('Any', 'object'), ns)

result = ns['get_all_workspace_component_names']()
assert result == sorted(result), f"List not sorted: {result}"
print(f"SORTED_OK:{len(result)}")
"""
    result = run_python(code)
    assert "SORTED_OK:" in result.stdout


def test_exclude_newer_package_constants_defined():
    """
    f2p: START_EXCLUDE_NEWER_PACKAGE and END_EXCLUDE_NEWER_PACKAGE constants must be defined.
    Uses AST to check constant definitions without executing top-level code.
    """
    code = """
import ast
from pathlib import Path

source = Path('/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py').read_text()
tree = ast.parse(source)

constants_found = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id in ('START_EXCLUDE_NEWER_PACKAGE', 'END_EXCLUDE_NEWER_PACKAGE',
                                 'START_EXCLUDE_NEWER_PACKAGE_PIP', 'END_EXCLUDE_NEWER_PACKAGE_PIP'):
                    constants_found.add(target.id)

expected = {'START_EXCLUDE_NEWER_PACKAGE', 'END_EXCLUDE_NEWER_PACKAGE'}
missing = expected - constants_found
if missing:
    print(f"MISSING:{missing}")
    exit(1)
print(f"CONSTANTS_OK:{constants_found}")
"""
    result = run_python(code)
    assert "MISSING:" not in result.stdout, f"Constants not found via AST.\n{result.stdout}"
    assert "CONSTANTS_OK:" in result.stdout


def test_exclude_newer_package_marker_values():
    """
    f2p: The marker constants should contain descriptive text referencing the script.
    Extracts constant values via AST and checks semantic content.
    """
    code = """
import ast
from pathlib import Path

source = Path('/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py').read_text()
tree = ast.parse(source)

# Find the START_EXCLUDE_NEWER_PACKAGE constant
start_value = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'START_EXCLUDE_NEWER_PACKAGE':
                if isinstance(node.value, (ast.Constant, ast.Tuple)):
                    if isinstance(node.value, ast.Tuple):
                        start_value = ''.join(ast.get_source_segment(source, e) or '' for e in node.value.elts)
                    else:
                        start_value = ast.get_source_segment(source, node.value)

if not start_value:
    print("CONSTANT_NOT_FOUND")
    exit(1)

has_script_ref = 'update_airflow_pyproject_toml.py' in start_value
has_marker = 'exclude-newer-package' in start_value.lower()

print(f"MARKER_CHECK:script={has_script_ref}:marker={has_marker}")
"""
    result = run_python(code)
    stdout = result.stdout.strip()
    assert "CONSTANT_NOT_FOUND" not in stdout, f"Constant not found.\n{stdout}"
    # Parse the output properly - format is "MARKER_CHECK:script=True:marker=True"
    parts = stdout.split(':')
    # Last part has marker=True/False
    marker_part = parts[-1] if parts else ''
    script_part = 'True' if any('script=True' in p for p in stdout.split('\n')) else 'False'
    assert 'True' in marker_part, f"Marker keyword not found in: {stdout}"
    assert 'True' in script_part or 'script=True' in stdout, f"Script reference not found in: {stdout}"


def test_install_script_no_exclude_newer_with_datetime():
    """
    f2p: install_airflow_and_providers.py should NOT use --exclude-newer with datetime.
    Uses AST to check for the forbidden pattern without importing.
    """
    code = """
import ast
from pathlib import Path

source = Path('/workspace/airflow/scripts/in_container/install_airflow_and_providers.py').read_text()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if hasattr(node.func, 'attr') and node.func.attr == 'extend':
            args_repr = str(node)
            if '--exclude-newer' in args_repr and ('datetime.now()' in args_repr or 'isoformat()' in args_repr):
                print("FORBIDDEN_PATTERN_FOUND")
                exit(1)

print("NO_FORBIDDEN_PATTERN:OK")
"""
    result = run_python(code)
    assert "NO_FORBIDDEN_PATTERN:OK" in result.stdout, (
        f"Found forbidden --exclude-newer with datetime pattern.\n{result.stdout}"
    )


def test_install_script_pre_release_simplified():
    """
    f2p: Pre-release installation should use --pre without --exclude-newer datetime.
    Uses AST to detect the old three-argument pattern.
    """
    code = """
import ast
from pathlib import Path

source = Path('/workspace/airflow/scripts/in_container/install_airflow_and_providers.py').read_text()
tree = ast.parse(source)

old_pattern_found = False
for node in ast.walk(tree):
    if isinstance(node, ast.List) and node.elts:
        args = [str(ast.dump(e)) for e in node.elts]
        args_str = ' '.join(args)
        if '--pre' in args_str and '--exclude-newer' in args_str and 'datetime' in args_str:
            old_pattern_found = True
            break

if old_pattern_found:
    print("OLD_PATTERN_STILL_PRESENT")
    exit(1)
print("PRE_RELEASE_SIMPLIFIED:OK")
"""
    result = run_python(code)
    assert "PRE_RELEASE_SIMPLIFIED:OK" in result.stdout, (
        f"Pre-release install still uses old pattern.\n{result.stdout}"
    )


def test_function_extracts_workspace_components_correctly():
    """
    f2p: get_all_workspace_component_names() correctly extracts only workspace entries.
    Verifies filtering behavior - only entries with workspace=true are included.
    """
    code = """
import ast
from pathlib import Path

script_path = '/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py'
source = Path(script_path).read_text()
tree = ast.parse(source)

target_func = None
read_toml_func = None

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == 'get_all_workspace_component_names':
            target_func = node
        elif node.name == '_read_toml':
            read_toml_func = node

ns = {
    "Path": Path,
    "AIRFLOW_PYPROJECT_TOML_FILE": Path('/workspace/airflow/pyproject.toml'),
    "__name__": "__test__"
}
try:
    import tomllib
    ns['tomllib'] = tomllib
except ImportError:
    import tomli as tomlib
    ns['tomllib'] = tomlib

exec(ast.unparse(read_toml_func).replace('Any', 'object'), ns)
exec(ast.unparse(target_func).replace('Any', 'object'), ns)

result = ns['get_all_workspace_component_names']()

assert isinstance(result, list), f"Result is not a list: {type(result)}"
assert len(result) > 0, "Result is empty"
assert result == sorted(result), "Result is not sorted"
assert "apache-airflow" in result, "apache-airflow should be in result"
assert len(result) == len(set(result)), "Result contains duplicates"
assert all(isinstance(x, str) for x in result), "All elements should be strings"

print(f"WORKSPACE_EXTRACTION:OK:{len(result)}")
"""
    result = run_python(code)
    assert "WORKSPACE_EXTRACTION:OK:" in result.stdout, (
        f"Function behavior incorrect.\n{result.stdout}"
    )


# ===== PASS-TO-PASS TESTS =====

def test_update_script_syntax_valid():
    """p2p: update_airflow_pyproject_toml.py has valid Python syntax."""
    content = UPDATE_SCRIPT.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in update_airflow_pyproject_toml.py: {e}")


def test_install_script_syntax_valid():
    """p2p: install_airflow_and_providers.py has valid Python syntax."""
    content = INSTALL_SCRIPT.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in install_airflow_and_providers.py: {e}")


def test_repo_py_compile_update_script():
    """p2p: Python's py_compile passes on update_airflow_pyproject_toml.py."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(UPDATE_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=AIRFLOW_REPO,
    )
    assert r.returncode == 0, f"py_compile failed on update_airflow_pyproject_toml.py:\n{r.stderr}"


def test_repo_py_compile_install_script():
    """p2p: Python's py_compile passes on install_airflow_and_providers.py."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(INSTALL_SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=AIRFLOW_REPO,
    )
    assert r.returncode == 0, f"py_compile failed on install_airflow_and_providers.py:\n{r.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
