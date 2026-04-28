"""
Task: posthog-featcloudagent-added-sandboxenvironmentid-ext-caller
Repo: PostHog/posthog @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
PR:   53163

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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
# Behavioral tests use subprocess to actually execute code and verify behavior
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_create_and_run_accepts_sandbox_env_id():
    """create_and_run must accept sandbox_environment_id keyword argument defaulting to None."""
    code = """
import inspect
import sys
sys.path.insert(0, '.')

try:
    from products.tasks.backend.models import Task
except ImportError as e:
    # If Django imports fail, fall back to AST-based signature check
    import ast

    src = open("products/tasks/backend/models.py").read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_and_run":
            kwonly = [a.arg for a in node.args.kwonlyargs]
            if "sandbox_environment_id" not in kwonly:
                print(f"FAIL: sandbox_environment_id not in kwonlyargs: {kwonly}", file=sys.stderr)
                sys.exit(1)

            idx = kwonly.index("sandbox_environment_id")
            default = node.args.kw_defaults[idx]
            if not (isinstance(default, ast.Constant) and default.value is None):
                print(f"FAIL: sandbox_environment_id must default to None, got {type(default)}", file=sys.stderr)
                sys.exit(1)

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
    sys.exit(0)

sig = inspect.signature(Task.create_and_run)

# Check if sandbox_environment_id is a kwonly parameter
params = sig.parameters
if 'sandbox_environment_id' not in params:
    print(f"FAIL: sandbox_environment_id not found in parameters: {list(params.keys())}", file=sys.stderr)
    sys.exit(1)

param = params['sandbox_environment_id']
# Check it has a default value of None
if param.default is not None:
    print(f"FAIL: sandbox_environment_id default must be None, got {param.default}", file=sys.stderr)
    sys.exit(1)

# Check type annotation includes str and None
ann = param.annotation
if ann == inspect.Parameter.empty:
    print("FAIL: sandbox_environment_id must have type annotation", file=sys.stderr)
    sys.exit(1)
ann_str = str(ann)
if 'str' not in ann_str or 'None' not in ann_str:
    print(f"FAIL: sandbox_environment_id annotation must be str | None, got {ann}", file=sys.stderr)
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
    assert result.returncode == 0, f"Signature check failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_invalid_sandbox_env_id_raises_valueerror():
    """create_and_run validates sandbox_environment_id and raises ValueError if the ID is not found."""
    code = """
import sys
sys.path.insert(0, '.')

try:
    from unittest.mock import MagicMock, patch
    from products.tasks.backend.models import Task

    # Mock GitHub integration check to pass
    with patch.object(Task, '_get_github_installation_id', return_value=MagicMock()):
        # Mock SandboxEnvironment.objects.filter to return None (no environment found)
        with patch('products.tasks.backend.models.SandboxEnvironment') as MockSandboxEnv:
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value.first.return_value = None
            MockSandboxEnv.objects.filter.return_value = mock_queryset

            # Mock Task.objects.create to avoid database
            with patch.object(Task.objects, 'create', return_value=MagicMock(id=1)) as mock_create:
                # Mock task.create_run
                mock_task = MagicMock()
                mock_task.id = 1
                mock_create.return_value = mock_task

                try:
                    Task.create_and_run(
                        team=MagicMock(id=1),
                        title="Test",
                        description="Test desc",
                        origin_product=Task.OriginProduct.CLOUD_AGENT,
                        user_id=1,
                        repository="test/repo",
                        sandbox_environment_id="nonexistent-id",
                    )
                    print("FAIL: Expected ValueError was not raised", file=sys.stderr)
                    sys.exit(1)
                except ValueError as e:
                    err_msg = str(e)
                    # Verify the error message contains the invalid ID
                    if "nonexistent-id" not in err_msg:
                        print(f"FAIL: ValueError message should contain the invalid ID, got: {err_msg}", file=sys.stderr)
                        sys.exit(1)
                    print("OK")
                    sys.exit(0)
                except Exception as e:
                    print(f"FAIL: Unexpected exception: {type(e).__name__}: {e}", file=sys.stderr)
                    sys.exit(1)
except ImportError as e:
    # If Django not available, fall back to source-based check
    import ast

    src = open("products/tasks/backend/models.py").read()
    tree = ast.parse(src)

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
    if "SandboxEnvironment" not in func_src or ".objects" not in func_src:
        print("FAIL: Must use SandboxEnvironment.objects for lookup", file=sys.stderr)
        sys.exit(1)

    # Check for ValueError with message containing the sandbox_environment_id
    if "ValueError" not in func_src:
        print("FAIL: Must raise ValueError for invalid sandbox_environment_id", file=sys.stderr)
        sys.exit(1)

    # Check that the ID is referenced in the validation
    if "sandbox_environment_id" not in func_src:
        print("FAIL: Must reference sandbox_environment_id in validation", file=sys.stderr)
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
    assert result.returncode == 0, f"Behavioral test failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_sandbox_env_id_stored_in_extra_state():
    """Valid sandbox_environment_id is stored as string in extra_state dict for downstream consumption."""
    code = """
import sys
sys.path.insert(0, '.')

try:
    from unittest.mock import MagicMock, patch
    from products.tasks.backend.models import Task

    # Mock GitHub integration check to pass
    with patch.object(Task, '_get_github_installation_id', return_value=MagicMock()):
        # Mock SandboxEnvironment.objects.filter to return a valid environment
        with patch('products.tasks.backend.models.SandboxEnvironment') as MockSandboxEnv:
            mock_env = MagicMock()
            mock_env.id = 12345  # Use a numeric ID like real Django models
            mock_queryset = MagicMock()
            mock_queryset.filter.return_value.first.return_value = mock_env
            MockSandboxEnv.objects.filter.return_value = mock_queryset

            captured_extra_state = {}

            # Mock Task.objects.create
            def capture_create(**kwargs):
                captured_extra_state.update(kwargs.get('extra_state', {}))
                mock_task = MagicMock()
                mock_task.id = 1
                return mock_task

            with patch.object(Task.objects, 'create', side_effect=capture_create) as mock_create:
                # Mock task.create_run
                with patch.object(Task, 'create_run', return_value=MagicMock()):
                    Task.create_and_run(
                        team=MagicMock(id=1),
                        title="Test",
                        description="Test desc",
                        origin_product=Task.OriginProduct.CLOUD_AGENT,
                        user_id=1,
                        repository="test/repo",
                        sandbox_environment_id="env-123",
                    )

            # Verify sandbox_environment_id was stored in extra_state
            if 'sandbox_environment_id' not in captured_extra_state:
                print(f"FAIL: sandbox_environment_id not found in extra_state. Keys: {list(captured_extra_state.keys())}", file=sys.stderr)
                sys.exit(1)

            stored_id = captured_extra_state['sandbox_environment_id']
            # The stored value should be a STRING representation of the environment's ID
            if not isinstance(stored_id, str):
                print(f"FAIL: sandbox_environment_id should be stored as string, got {type(stored_id).__name__}: {stored_id}", file=sys.stderr)
                sys.exit(1)

            # Verify it matches the string representation of the mock env's ID
            expected = str(mock_env.id)
            if stored_id != expected:
                print(f"FAIL: sandbox_environment_id should be str(env.id)={expected}, got {stored_id}", file=sys.stderr)
                sys.exit(1)

            print("OK")
            sys.exit(0)
except ImportError as e:
    # If Django not available, fall back to source-based check
    import ast

    src = open("products/tasks/backend/models.py").read()
    tree = ast.parse(src)

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
    assert result.returncode == 0, f"Behavioral test failed:\n{result.stderr}"
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# Agent config compliance (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — AGENTS.md:87 @ a65a8fd19c2bed0c06c111f1d65b0deb87f31313
def test_team_filter_in_sandbox_lookup():
    """SandboxEnvironment lookup must filter by team (AGENTS.md: always filter querysets by team_id)."""
    # This test verifies the team filtering requirement from AGENTS.md without
    # being coupled to the gold implementation's variable names or exact patterns.
    # We check that the lookup logic exists and includes team filtering.
    code = """
import ast
import sys
import re

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

# Verify SandboxEnvironment lookup is performed when sandbox_environment_id is provided
if "SandboxEnvironment" not in func_src or ".objects" not in func_src:
    print("FAIL: Must use SandboxEnvironment.objects for lookup", file=sys.stderr)
    sys.exit(1)

# Find all filter() calls in the function
filter_calls = re.findall(r'\\.filter\\([^)]+\\)', func_src)
if not filter_calls:
    print("FAIL: Must use .filter() for SandboxEnvironment lookup", file=sys.stderr)
    sys.exit(1)

# Check if any filter call includes team filtering
has_team_filter = any('team' in call for call in filter_calls)
if not has_team_filter:
    print("FAIL: SandboxEnvironment filter must include team filtering per AGENTS.md security rule", file=sys.stderr)
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
    # Check for str(...) wrapping of env.id (the str() may be in different forms)
    if not __import__('re').search(r'sandbox_environment_id\s*=\s*str\(', doc):
        assert False, "Usage example must show str() conversion of env.id for sandbox_environment_id"
    print("OK")


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
            # Must have at least references to sandbox_environment_id in the body
            # (checking for substantive logic, not just adding a parameter)
            refs = body_src.count("sandbox_environment_id")
            assert refs >= 3, (
                f"create_and_run body has only {refs} refs to sandbox_environment_id — likely a stub"
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
    # Run ruff format check on modified file and related files
    r = subprocess.run(
        ["ruff", "format", "--check", "products/tasks/backend/models.py", "products/tasks/backend/constants.py"],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


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


# === CI-scoped test (scoped to products/tasks/backend, uses pytest test runner) ===
def test_ci_pytest_tasks_backend_syntax():
    """pass_to_pass | CI: pytest verifies products/tasks/backend Python files parse without errors"""
    import os as _os

    test_code = '''import ast, pathlib
def test_tasks_backend_python_files_parse():
    """All Python files in products/tasks/backend parse without syntax errors."""
    backend_dir = pathlib.Path("products/tasks/backend")
    errors = []
    for py_file in backend_dir.rglob("*.py"):
        try:
            ast.parse(py_file.read_text())
        except SyntaxError as e:
            errors.append(f"{py_file}: {e}")
    assert not errors, "\\\\n".join(errors)
'''
    tmp = "/tmp/test_scoped_ci_tasks.py"
    with open(tmp, "w") as f:
        f.write(test_code)
    try:
        r = subprocess.run(
            ["bash", "-lc", f"python -m pytest {tmp} -v"],
            capture_output=True, text=True, cwd=REPO, timeout=60,
        )
        assert r.returncode == 0, f"Pytest scoped test failed:\\n{r.stdout}\\n{r.stderr}"
    finally:
        _os.unlink(tmp)

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_hog_tests_check_if_antlr_definitions_are_up_to_dat():
    """pass_to_pass | CI job 'Hog tests' → step 'Check if ANTLR definitions are up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'antlr | grep "Version" && npm run grammar:build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check if ANTLR definitions are up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_check_if_stl_bytecode_is_up_to_date():
    """pass_to_pass | CI job 'Hog tests' → step 'Check if STL bytecode is up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m common.hogvm.stl.compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check if STL bytecode is up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_run_hogvm_python_tests():
    """pass_to_pass | CI job 'Hog tests' → step 'Run HogVM Python tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest common/hogvm'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run HogVM Python tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_run_hogvm_typescript_tests():
    """pass_to_pass | CI job 'Hog tests' → step 'Run HogVM TypeScript tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/hogvm install --frozen-lockfile && pnpm --filter=@posthog/hogvm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run HogVM TypeScript tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_hog_tests_run_hog_tests():
    """pass_to_pass | CI job 'Hog tests' → step 'Run Hog tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/hogvm install --frozen-lockfile && pnpm --filter=@posthog/hogvm compile:stl && ./test.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Hog tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'go test -v ./...'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_build_package():
    """pass_to_pass | CI job 'Build Package' → step 'Build package'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build package' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_type_check():
    """pass_to_pass | CI job 'Build Package' → step 'Type check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_check_mcp_schema_is_up_to_date():
    """pass_to_pass | CI job 'Build Package' → step 'Check MCP schema is up to date'"""
    r = subprocess.run(
        ["bash", "-lc", './bin/hogli build:schema-mcp\nif ! git diff --exit-code services/mcp/schema/tool-inputs.json; then\n  echo ""\n  echo "::error::MCP tool-inputs.json is out of date. Run \'hogli build:schema-mcp\' and commit the result."\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check MCP schema is up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_check_generated_ui_apps_are_up_to_date():
    """pass_to_pass | CI job 'Build Package' → step 'Check generated UI apps are up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run generate:ui-apps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated UI apps are up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_package_lint_tool_names():
    """pass_to_pass | CI job 'Build Package' → step 'Lint tool names'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint-tool-names'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint tool names' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_run_unit_tests():
    """pass_to_pass | CI job 'Unit Tests' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/mcp run test -u'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")