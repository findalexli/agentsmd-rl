"""
Task: posthog-featcloudagent-added-sandboxenvironmentid-ext-caller
Repo: PostHog/posthog @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
PR:   53163

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified Python file must parse without errors."""
    import py_compile

    py_compile.compile(
        f"{REPO}/products/tasks/backend/models.py", doraise=True
    )


# [repo_tests] pass_to_pass
# Repo ruff lint on modified file must pass (static analysis)
def test_repo_ruff_check():
    """Ruff lint check passes on modified file (pass_to_pass)."""
    import pytest

    # First, check if ruff is available, install if not
    r = subprocess.run(
        ["python3", "-c", "import ruff"],
        capture_output=True, text=True, cwd=REPO,
    )
    if r.returncode != 0:
        # Install ruff
        r = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True, text=True, cwd=REPO, timeout=60,
        )
        if r.returncode != 0:
            pytest.skip("Could not install ruff")

    r = subprocess.run(
        ["ruff", "check", "products/tasks/backend/models.py", "--output-format=concise"],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
# Repo Python syntax check for all modified-related files
def test_repo_python_syntax():
    """All Python files in products/tasks/backend parse without syntax errors (pass_to_pass)."""
    import py_compile

    backend_dir = Path(f"{REPO}/products/tasks/backend")
    py_files = list(backend_dir.rglob("*.py"))

    errors = []
    for py_file in py_files:
        try:
            py_compile.compile(str(py_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{py_file}: {e}")

    assert not errors, f"Syntax errors found:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# All tests MUST use subprocess.run() to execute code per requirements
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_create_and_run_accepts_sandbox_env_id():
    """create_and_run must accept sandbox_environment_id keyword argument."""
    code = """
import ast
import sys
src = open("products/tasks/backend/models.py").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        kwonly = [a.arg for a in node.args.kwonlyargs]
        if "sandbox_environment_id" not in kwonly:
            print(f"FAIL: sandbox_environment_id not in {kwonly}", file=sys.stderr)
            sys.exit(1)
        # Verify default is None
        for i, arg in enumerate(node.args.kwonlyargs):
            if arg.arg == "sandbox_environment_id":
                d = node.args.kw_defaults[i]
                if d is None or not (isinstance(d, ast.Constant) and d.value is None):
                    print("FAIL: sandbox_environment_id must default to None", file=sys.stderr)
                    sys.exit(1)
        print("OK")
        sys.exit(0)
print("FAIL: create_and_run not found", file=sys.stderr)
sys.exit(1)
"""
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert result.returncode == 0, f"Signature check failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_invalid_sandbox_env_id_raises_valueerror():
    """create_and_run must validate sandbox_environment_id and raise ValueError if invalid."""
    code = """
import sys
src = open("products/tasks/backend/models.py").read()

# Check for the lookup pattern
if "SandboxEnvironment.objects.filter" not in src:
    print("FAIL: Must look up SandboxEnvironment via objects.filter", file=sys.stderr)
    sys.exit(1)

# Check for ValueError with descriptive message  
if "Invalid sandbox_environment_id" not in src:
    print("FAIL: Must raise ValueError with descriptive message", file=sys.stderr)
    sys.exit(1)

# Check variable assignment
if "sandbox_env" not in src:
    print("FAIL: Must assign lookup result to sandbox_env variable", file=sys.stderr)
    sys.exit(1)

print("OK")
"""
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert result.returncode == 0, f"Validation check failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_sandbox_env_id_stored_in_extra_state():
    """sandbox_environment_id must be stored in extra_state dict when a valid env is provided."""
    code = """
import sys
src = open("products/tasks/backend/models.py").read()

# Check for storing in extra_state
if '"sandbox_environment_id"' not in src and "'sandbox_environment_id'" not in src:
    print("FAIL: Must store sandbox_environment_id in extra_state dict", file=sys.stderr)
    sys.exit(1)

# Check for str() conversion
if "str(sandbox_env.id)" not in src:
    print("FAIL: Must store the string representation of sandbox_env.id", file=sys.stderr)
    sys.exit(1)

print("OK")
"""
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert result.returncode == 0, f"Extra state check failed:\n{result.stderr}"
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# Agent config compliance (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — AGENTS.md:87 @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
def test_team_filter_in_sandbox_lookup():
    """SandboxEnvironment lookup must filter by team (AGENTS.md: always filter querysets by team_id)."""
    code = """
import sys
src = open("products/tasks/backend/models.py").read()

# Check for filter usage
if "SandboxEnvironment.objects.filter" not in src:
    print("FAIL: Must use SandboxEnvironment.objects.filter for lookup", file=sys.stderr)
    sys.exit(1)

# Verify team filter is present
if "team=team" not in src:
    print("FAIL: SandboxEnvironment filter must include team=team per AGENTS.md rule", file=sys.stderr)
    sys.exit(1)

print("OK")
"""
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert result.returncode == 0, f"Team filter check failed:\n{result.stderr}"
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# Config/documentation update checks (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_docs_parameter_table_includes_sandbox_env_id():
    """Handbook must document sandbox_environment_id in the Parameters section."""
    doc = Path(f"{REPO}/docs/published/handbook/engineering/ai/sandboxed-agents.md").read_text()
    params_idx = doc.find("### Parameters")
    assert params_idx != -1, "Parameters section not found in handbook"
    params_section = doc[params_idx:]
    assert "sandbox_environment_id" in params_section, (
        "Parameters table must include sandbox_environment_id entry"
    )
    assert "SandboxEnvironment" in params_section, (
        "sandbox_environment_id description must reference SandboxEnvironment"
    )


# [pr_diff] fail_to_pass
def test_docs_include_usage_example():
    """Handbook must include code example showing how to create SandboxEnvironment and pass its ID."""
    doc = Path(f"{REPO}/docs/published/handbook/engineering/ai/sandboxed-agents.md").read_text()
    assert "SandboxEnvironment.objects.create" in doc, (
        "Handbook must show SandboxEnvironment.objects.create in usage example"
    )
    assert "network_access_level" in doc, (
        "Usage example must demonstrate network_access_level configuration"
    )
    assert "allowed_domains" in doc, (
        "Usage example must mention allowed_domains"
    )
    assert "sandbox_environment_id=str(env.id)" in doc, (
        "Usage example must show passing sandbox_environment_id to create_and_run"
    )


# ---------------------------------------------------------------------------
# Anti-stub (pass_to_pass)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """create_and_run has real sandbox_environment_id validation logic, not just a parameter."""
    src = Path(f"{REPO}/products/tasks/backend/models.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
            body_src = ast.get_source_segment(src, node)
            # Must have at least 3 distinct references to sandbox_env logic
            refs = body_src.count("sandbox_env") + body_src.count("sandbox_environment_id")
            assert refs >= 5, (
                f"create_and_run body has only {refs} refs to sandbox logic — likely a stub"
            )
            return
    raise AssertionError("create_and_run method not found")


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (repo_tests)
# These tests ensure existing CI checks pass on both base commit and after fix
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
# Ruff format check - verifies code formatting follows repo standards
def test_repo_ruff_format():
    """Ruff format check passes on products/tasks/backend directory (pass_to_pass)."""
    import pytest

    # Check if ruff is available, install if not
    r = subprocess.run(
        ["python3", "-c", "import ruff"],
        capture_output=True, text=True, cwd=REPO,
    )
    if r.returncode != 0:
        r = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True, text=True, cwd=REPO, timeout=120,
        )
        if r.returncode != 0:
            pytest.skip("Could not install ruff")

    # Run ruff format check on modified file and related files
    r = subprocess.run(
        ["ruff", "format", "--check", "products/tasks/backend/models.py", "products/tasks/backend/constants.py"],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
# Import check for modified module
def test_repo_imports():
    """Modified module can be imported without errors (pass_to_pass)."""
    import pytest

    r = subprocess.run(
        ["python3", "-c", "import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'common'); from products.tasks.backend import models; print('OK')"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    # Note: This may fail due to Django setup issues, but we check if the syntax is valid
    # If it fails with ImportError/ModuleNotFoundError for Django deps, that is expected
    # If it fails with SyntaxError, that is a real problem
    if r.returncode != 0:
        # Only fail on syntax errors, not dependency issues
        if "SyntaxError" in r.stderr or "IndentationError" in r.stderr:
            assert False, f"Syntax error in module:\n{r.stderr}"
        # Otherwise, dependency issues are expected in this limited environment
        pytest.skip("Module has dependency requirements (expected in container environment)")


# [repo_tests] pass_to_pass
# AST validation for Python file
def test_repo_ast_valid():
    """Modified Python file has valid AST structure (pass_to_pass)."""
    src = Path(f"{REPO}/products/tasks/backend/models.py").read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        assert False, f"Invalid AST: {e}"


# [repo_tests] pass_to_pass
# Check that the file does not contain obvious errors
def test_repo_no_obvious_errors():
    """Modified file does not contain obvious syntax patterns that indicate errors (pass_to_pass)."""
    src = Path(f"{REPO}/products/tasks/backend/models.py").read_text()

    # Check for common error patterns
    error_patterns = [
        "FIXME",
        "TODO: fix",
        "XXX",
        "raise NotImplementedError",
    ]

    for pattern in error_patterns:
        # Allow these in comments but not in actual code
        lines = src.split("\n")
        for i, line in enumerate(lines, 1):
            if pattern in line and not line.strip().startswith("#"):
                # In actual code (not comment)
                if pattern == "raise NotImplementedError":
                    assert False, f"Line {i} contains NotImplementedError - feature not implemented"

    # Check for balanced parentheses and quotes (basic)
    # This is a simple heuristic - real syntax check is done by py_compile
    assert src.count("(") >= src.count(")"), "Unbalanced parentheses (more closing)"
    assert src.count(")") >= src.count("("), "Unbalanced parentheses (more opening)"


# [repo_tests] pass_to_pass
# Verify that constants used by the modified code exist and are importable
def test_repo_constants_importable():
    """DEFAULT_TRUSTED_DOMAINS constant is importable from constants module (pass_to_pass)."""
    import pytest

    r = subprocess.run(
        ["python3", "-c", "from products.tasks.backend.constants import DEFAULT_TRUSTED_DOMAINS; print('OK')"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    if r.returncode != 0:
        # Skip if Django not available, but fail on syntax errors
        if "SyntaxError" in r.stderr or "IndentationError" in r.stderr:
            assert False, f"Syntax error in constants module:\n{r.stderr}"
        pytest.skip("Django dependencies not available (expected in container environment)")
    assert "OK" in r.stdout, "Failed to import DEFAULT_TRUSTED_DOMAINS"
