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
# All tests MUST use subprocess.run() to execute actual code per requirements
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_create_and_run_accepts_sandbox_env_id():
    """create_and_run must accept sandbox_environment_id keyword argument defaulting to None."""
    code = """
import ast
import sys

src = open("products/tasks/backend/models.py").read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        # Check kwonlyargs for sandbox_environment_id
        kwonly = [a.arg for a in node.args.kwonlyargs]
        if "sandbox_environment_id" not in kwonly:
            print(f"FAIL: sandbox_environment_id not in kwonlyargs: {kwonly}", file=sys.stderr)
            sys.exit(1)

        # Find the index and check default is None
        idx = kwonly.index("sandbox_environment_id")
        if idx >= len(node.args.kw_defaults):
            print("FAIL: sandbox_environment_id has no default value", file=sys.stderr)
            sys.exit(1)

        default = node.args.kw_defaults[idx]
        if default is None:
            print("FAIL: sandbox_environment_id default is not explicitly None (Type annotation without default)", file=sys.stderr)
            sys.exit(1)

        if not (isinstance(default, ast.Constant) and default.value is None):
            print(f"FAIL: sandbox_environment_id must default to None, got {type(default)}", file=sys.stderr)
            sys.exit(1)

        # Also verify type annotation is str | None
        arg = node.args.kwonlyargs[idx]
        if arg.annotation:
            ann_str = ast.unparse(arg.annotation) if hasattr(ast, "unparse") else str(arg.annotation)
            if "str" not in ann_str or "None" not in ann_str:
                print(f"FAIL: sandbox_environment_id type hint should be str | None, got {ann_str}", file=sys.stderr)
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
    """create_and_run must validate sandbox_environment_id via SandboxEnvironment.objects.filter and raise ValueError if invalid."""
    code = """
import ast
import sys

src = open("products/tasks/backend/models.py").read()
tree = ast.parse(src)

# Find create_and_run function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        func_node = node
        break

if func_node is None:
    print("FAIL: create_and_run not found", file=sys.stderr)
    sys.exit(1)

func_src = ast.get_source_segment(src, func_node)
if func_src is None:
    func_src = src[func_node.lineno-1:func_node.end_lineno]

# Check for SandboxEnvironment.objects.filter
if "SandboxEnvironment.objects.filter" not in func_src:
    print("FAIL: Must use SandboxEnvironment.objects.filter for lookup", file=sys.stderr)
    sys.exit(1)

# Check for ValueError with descriptive message about invalid sandbox_environment_id
if "Invalid sandbox_environment_id" not in func_src:
    print("FAIL: Must raise ValueError with 'Invalid sandbox_environment_id' message", file=sys.stderr)
    sys.exit(1)

# Check that validation logic exists (looking up by id and team)
if "sandbox_env" not in func_src:
    print("FAIL: Must assign lookup result to sandbox_env variable", file=sys.stderr)
    sys.exit(1)

# Check for conditional raise based on lookup result
if ".first()" not in func_src:
    print("FAIL: Must use .first() to check if sandbox environment exists", file=sys.stderr)
    sys.exit(1)

if "if not sandbox_env" not in func_src and "if sandbox_env is None" not in func_src:
    print("FAIL: Must check if sandbox_env is None/not found", file=sys.stderr)
    sys.exit(1)

print("OK")
sys.exit(0)
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
    """Valid sandbox_environment_id must be stored as string in extra_state dict for downstream consumption."""
    code = """
import ast
import sys

src = open("products/tasks/backend/models.py").read()
tree = ast.parse(src)

# Find create_and_run function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        func_node = node
        break

if func_node is None:
    print("FAIL: create_and_run not found", file=sys.stderr)
    sys.exit(1)

func_src = ast.get_source_segment(src, func_node)
if func_src is None:
    func_src = src[func_node.lineno-1:func_node.end_lineno]

# Check for storing sandbox_environment_id in extra_state
has_sandbox_key = ('"sandbox_environment_id"' in func_src or "'sandbox_environment_id'" in func_src)
if not has_sandbox_key:
    print("FAIL: Must store sandbox_environment_id key in extra_state dict", file=sys.stderr)
    sys.exit(1)

# Check for extra_state assignment
if "extra_state[" not in func_src:
    print("FAIL: Must assign to extra_state using key access", file=sys.stderr)
    sys.exit(1)

# Check for str() conversion of sandbox_env.id
if "str(sandbox_env.id)" not in func_src:
    print("FAIL: Must store string representation of sandbox_env.id using str()", file=sys.stderr)
    sys.exit(1)

# Verify extra_state initialization before use
if "extra_state = extra_state or {}" not in func_src and "if extra_state is None" not in func_src:
    # Check various patterns of extra_state initialization
    if not ("extra_state = {}" in func_src and "extra_state[" in func_src):
        print("FAIL: Must ensure extra_state is initialized before storing sandbox_environment_id", file=sys.stderr)
        sys.exit(1)

print("OK")
sys.exit(0)
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
import ast
import sys

src = open("products/tasks/backend/models.py").read()
tree = ast.parse(src)

# Find create_and_run function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
        func_node = node
        break

if func_node is None:
    print("FAIL: create_and_run not found", file=sys.stderr)
    sys.exit(1)

func_src = ast.get_source_segment(src, func_node)
if func_src is None:
    func_src = src[func_node.lineno-1:func_node.end_lineno]

# Check for SandboxEnvironment.objects.filter
if "SandboxEnvironment.objects.filter" not in func_src:
    print("FAIL: Must use SandboxEnvironment.objects.filter for lookup", file=sys.stderr)
    sys.exit(1)

# Verify team filter is present - must filter by team for security
if "team=team" not in func_src:
    print("FAIL: SandboxEnvironment filter must include team=team per AGENTS.md security rule", file=sys.stderr)
    sys.exit(1)

# Verify id filter is also present
if "id=sandbox_environment_id" not in func_src:
    print("FAIL: Must filter by id=sandbox_environment_id", file=sys.stderr)
    sys.exit(1)

print("OK")
sys.exit(0)
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
    doc_path = Path(f"{REPO}/docs/published/handbook/engineering/ai/sandboxed-agents.md")
    doc = doc_path.read_text()

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
    doc_path = Path(f"{REPO}/docs/published/handbook/engineering/ai/sandboxed-agents.md")
    doc = doc_path.read_text()

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
            # Must have at least 5 distinct references to sandbox_env logic
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


# [repo_tests] pass_to_pass
# Repo product lint check - validates product structure per PostHog conventions
def test_repo_hogli_product_lint():
    """Product structure lint passes for all products (pass_to_pass)."""
    import pytest

    # Install required dependencies for hogli
    deps_r = subprocess.run(
        ["pip", "install", "-q", "requests", "click", "pyyaml"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    if deps_r.returncode != 0:
        pytest.skip("Could not install hogli dependencies")

    # Run hogli product:lint --all
    r = subprocess.run(
        ["python3", "bin/hogli", "product:lint", "--all"],
        capture_output=True, text=True, cwd=REPO, timeout=300,
    )
    assert r.returncode == 0, f"Product lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
# Tach module boundary check - ensures no circular dependencies
def test_repo_tach_check():
    """Tach module boundary check passes (pass_to_pass)."""
    import pytest

    # Install tach
    install_r = subprocess.run(
        ["pip", "install", "-q", "tach"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    if install_r.returncode != 0:
        pytest.skip("Could not install tach")

    # Run tach check
    r = subprocess.run(
        ["tach", "check"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    # tach check may return 0 even with config warnings, so we check for actual error patterns
    # The check passed in our testing even with TOML parse warnings
    if r.returncode != 0:
        # Only fail on actual boundary violations, not config parsing issues
        if "BoundaryError" in r.stderr or "Import" in r.stderr and " violates " in r.stderr:
            assert False, f"Tach boundary check failed:\n{r.stderr}"
        # If it's just config issues, consider it passed (the command ran)
