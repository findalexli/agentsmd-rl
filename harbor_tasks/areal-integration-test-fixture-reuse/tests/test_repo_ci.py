"""
Pass-to-pass tests for repo CI/CD checks via AST analysis.

These verify static code quality matching the repo's pre-commit/CI standards.
These tests do NOT require pytest/ruff/clang-format to be installed —
they use AST analysis like the existing test_outputs.py tests.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"

CTRL_FILE = f"{REPO}/tests/experimental/inference_service/test_controller_integration.py"
PROXY_FILE = f"{REPO}/tests/experimental/inference_service/test_data_proxy_integration.py"
GW_FILE = f"{REPO}/tests/experimental/inference_service/test_gateway_integration.py"

ALL_FILES = [CTRL_FILE, PROXY_FILE, GW_FILE]


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess; return CompletedProcess."""
    script = Path("/tmp/_eval_check.py")
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Repo CI/CD checks via AST analysis
# ---------------------------------------------------------------------------


def test_repo_test_classes_follow_naming():
    """All test classes must follow Test* naming convention (pass_to_pass).

    Matches ruff/pre-commit check: test classes should be named Test*.
    """
    r = _run_py(f'''
import ast
from pathlib import Path

ALL_FILES = {ALL_FILES!r}

for fpath in ALL_FILES:
    tree = ast.parse(Path(fpath).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it's a test class (contains test methods)
            has_test_methods = any(
                isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name.startswith("test_")
                for n in ast.walk(node)
            )
            if has_test_methods:
                assert node.name.startswith("Test"), (
                    f"{{fpath}}: Test class {{node.name}} should start with 'Test'"
                )
print("PASS")
''')
    assert r.returncode == 0, f"Test class naming check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_no_bare_excepts():
    """No bare 'except:' clauses in test files (pass_to_pass).

    Matches ruff E722: do not use bare except.
    """
    r = _run_py(f'''
import ast
from pathlib import Path

ALL_FILES = {ALL_FILES!r}

for fpath in ALL_FILES:
    tree = ast.parse(Path(fpath).read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    raise AssertionError(
                        f"{{fpath}}: Bare 'except:' found at line {{handler.lineno}}, "
                        f"use 'except Exception:' instead"
                    )
print("PASS")
''')
    assert r.returncode == 0, f"Bare except check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_yaml_files_valid():
    """All YAML files in the repo must be valid (pass_to_pass).

    Matches pre-commit check-yaml hook.
    """
    r = _run_py(f'''
import yaml
from pathlib import Path

REPO = "{REPO}"

repo_yaml_files = [
    f"{{REPO}}/.pre-commit-config.yaml",
]

# Find all YAML files in examples directory
examples_yaml = list(Path(f"{{REPO}}/examples").rglob("*.yaml")) + list(Path(f"{{REPO}}/examples").rglob("*.yml"))

for fpath in repo_yaml_files + [str(p) for p in examples_yaml]:
    path = Path(fpath)
    if path.exists():
        try:
            yaml.safe_load(path.read_text())
        except yaml.YAMLError as e:
            raise AssertionError(f"{{fpath}}: Invalid YAML - {{e}}")
print("PASS")
''')
    assert r.returncode == 0, f"YAML validity check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_pyproject_toml_valid():
    """pyproject.toml must be valid TOML (pass_to_pass).

    Basic syntax check for the repo's main config file.
    """
    r = _run_py(f'''
import tomllib
from pathlib import Path

REPO = "{REPO}"
pyproject_path = Path(f"{{REPO}}/pyproject.toml")
if pyproject_path.exists():
    try:
        tomllib.loads(pyproject_path.read_text())
    except Exception as e:
        raise AssertionError(f"pyproject.toml: Invalid TOML - {{e}}")
print("PASS")
''')
    assert r.returncode == 0, f"pyproject.toml validity check failed: {r.stderr}"
    assert "PASS" in r.stdout
