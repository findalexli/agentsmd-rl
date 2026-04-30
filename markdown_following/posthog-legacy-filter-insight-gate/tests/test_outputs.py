"""
Task: posthog-legacy-filter-insight-gate
Repo: posthog @ 011a93306e5dfe6e26464fba7c61680076df62c8
PR:   53653

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/posthog"
INSIGHT_PY = Path(f"{REPO}/posthog/api/insight.py")


def _extract_function_source(source: str, func_name: str) -> str | None:
    """Extract a top-level function's source from a Python file."""
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return ast.get_source_segment(source, node)
    return None


def _extract_method_source(source: str, class_name: str, method_name: str) -> str | None:
    """Extract a method's source from a class in a Python file."""
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return ast.get_source_segment(source, item)
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """posthog/api/insight.py must parse without errors."""
    src = INSIGHT_PY.read_text()
    ast.parse(src)


# [repo_tests] pass_to_pass — Repo CI/CD checks
def test_repo_syntax_insight_py():
    """Repo: posthog/api/insight.py passes Python syntax check (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/posthog/api/insight.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed for insight.py:\n{r.stderr}"


def test_repo_syntax_test_insight_py():
    """Repo: posthog/api/test/test_insight.py passes Python syntax check (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/posthog/api/test/test_insight.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed for test_insight.py:\n{r.stderr}"


def test_repo_ast_parse_insight_files():
    """Repo: All insight-related Python files parse as valid AST (pass_to_pass)."""
    files = [
        f"{REPO}/posthog/api/insight.py",
        f"{REPO}/posthog/api/test/test_insight.py",
    ]
    for f in files:
        src = Path(f).read_text()
        ast.parse(src)  # raises SyntaxError if invalid


def test_repo_dependency_analysis():
    """Repo: Python dependency analysis tests pass (pass_to_pass).

    Runs bin/test/test_find_python_dependencies.py which validates the import
    graph analysis tooling used by CI to detect dependency changes.
    """
    # Install required dependencies first
    r = subprocess.run(
        ["pip", "install", "grimp", "parameterized", "pytest", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run the dependency analysis tests
    r = subprocess.run(
        ["python", "-m", "pytest", "bin/test/test_find_python_dependencies.py",
         "--override-ini=addopts=", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Dependency analysis tests failed:\n{r.stderr}\n{r.stdout}"


def test_repo_insight_py_compiles():
    """Repo: posthog/api/insight.py compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/posthog/api/insight.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"insight.py failed to compile:\n{r.stderr}"


def test_repo_ruff_check_insight_py():
    """Repo: posthog/api/insight.py passes ruff lint check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/posthog/api/insight.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed for insight.py:\n{r.stderr}"


def test_repo_ruff_format_check_insight_py():
    """Repo: posthog/api/insight.py passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/posthog/api/insight.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed for insight.py:\n{r.stderr}"


def test_repo_ruff_check_test_insight_py():
    """Repo: posthog/api/test/test_insight.py passes ruff lint check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/posthog/api/test/test_insight.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed for test_insight.py:\n{r.stderr}"


def test_repo_ruff_format_check_test_insight_py():
    """Repo: posthog/api/test/test_insight.py passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", f"{REPO}/posthog/api/test/test_insight.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed for test_insight.py:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_legacy_filters_flag_constant():
    """LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG must be defined with correct value."""
    src = INSIGHT_PY.read_text()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG":
                    assert isinstance(node.value, ast.Constant), "Flag must be a string constant"
                    assert node.value.value == "legacy-insight-filters-disabled", (
                        f"Expected 'legacy-insight-filters-disabled', got {node.value.value!r}"
                    )
                    return
    raise AssertionError("LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG constant not found at module level")


# [pr_diff] fail_to_pass
def test_filters_blocked_returns_false_without_distinct_id():
    """is_legacy_insight_filters_blocked returns False when user has no distinct_id."""
    src = INSIGHT_PY.read_text()
    func_src = _extract_function_source(src, "is_legacy_insight_filters_blocked")
    assert func_src is not None, "Function is_legacy_insight_filters_blocked not found"

    mock_analytics = MagicMock()
    ns = {
        "posthoganalytics": mock_analytics,
        "LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG": "legacy-insight-filters-disabled",
        "getattr": getattr,
        "str": str,
        "Any": type("Any", (), {}),
        "Team": type("Team", (), {}),
    }
    exec(func_src, ns)

    # User without distinct_id attribute
    user_no_attr = object()
    team = MagicMock(organization_id="org-001", id=7)
    result = ns["is_legacy_insight_filters_blocked"](user_no_attr, team)
    assert result is False, f"Expected False for user without distinct_id, got {result!r}"
    mock_analytics.feature_enabled.assert_not_called()

    # User with distinct_id=None
    user_none_id = MagicMock(distinct_id=None)
    mock_analytics.reset_mock()
    result = ns["is_legacy_insight_filters_blocked"](user_none_id, team)
    assert result is False, f"Expected False for user with distinct_id=None, got {result!r}"
    mock_analytics.feature_enabled.assert_not_called()

    # User with distinct_id="" (empty string is falsy)
    user_empty_id = MagicMock(distinct_id="")
    mock_analytics.reset_mock()
    result = ns["is_legacy_insight_filters_blocked"](user_empty_id, team)
    assert result is False, f"Expected False for user with empty distinct_id, got {result!r}"
    mock_analytics.feature_enabled.assert_not_called()


# [pr_diff] fail_to_pass
def test_filters_blocked_delegates_to_feature_flag():
    """is_legacy_insight_filters_blocked calls posthoganalytics.feature_enabled with correct args."""
    src = INSIGHT_PY.read_text()
    func_src = _extract_function_source(src, "is_legacy_insight_filters_blocked")
    assert func_src is not None, "Function is_legacy_insight_filters_blocked not found"

    mock_analytics = MagicMock()
    mock_analytics.feature_enabled.return_value = True
    ns = {
        "posthoganalytics": mock_analytics,
        "LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG": "legacy-insight-filters-disabled",
        "getattr": getattr,
        "str": str,
        "Any": type("Any", (), {}),
        "Team": type("Team", (), {}),
    }
    exec(func_src, ns)

    user = MagicMock(distinct_id="user-xyz-42")
    team = MagicMock(organization_id="org-789", id=55)

    result = ns["is_legacy_insight_filters_blocked"](user, team)
    assert result is True, f"Expected True when feature_enabled returns True, got {result!r}"

    mock_analytics.feature_enabled.assert_called_once()
    call_kwargs = mock_analytics.feature_enabled.call_args
    # First positional arg: flag name
    assert call_kwargs[0][0] == "legacy-insight-filters-disabled", (
        f"Wrong flag name: {call_kwargs[0][0]!r}"
    )
    # Second positional arg: distinct_id as string
    assert call_kwargs[0][1] == "user-xyz-42", f"Wrong distinct_id: {call_kwargs[0][1]!r}"
    # groups must include organization and project
    groups = call_kwargs[1].get("groups", call_kwargs.kwargs.get("groups", {}))
    assert "organization" in groups, "groups must include 'organization'"
    assert "project" in groups, "groups must include 'project'"
    # send_feature_flag_events must be False
    send_events = call_kwargs[1].get(
        "send_feature_flag_events",
        call_kwargs.kwargs.get("send_feature_flag_events", None),
    )
    assert send_events is False, f"send_feature_flag_events must be False, got {send_events!r}"


# [pr_diff] fail_to_pass
def test_filters_blocked_returns_feature_flag_result():
    """is_legacy_insight_filters_blocked returns whatever feature_enabled returns."""
    src = INSIGHT_PY.read_text()
    func_src = _extract_function_source(src, "is_legacy_insight_filters_blocked")
    assert func_src is not None, "Function is_legacy_insight_filters_blocked not found"

    user = MagicMock(distinct_id="user-test-99")
    team = MagicMock(organization_id="org-a", id=1)

    for expected_value in (True, False):
        mock_analytics = MagicMock()
        mock_analytics.feature_enabled.return_value = expected_value
        ns = {
            "posthoganalytics": mock_analytics,
            "LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG": "legacy-insight-filters-disabled",
            "getattr": getattr,
            "str": str,
            "Any": type("Any", (), {}),
            "Team": type("Team", (), {}),
        }
        exec(func_src, ns)
        result = ns["is_legacy_insight_filters_blocked"](user, team)
        assert result is expected_value, (
            f"Expected {expected_value} when feature_enabled returns {expected_value}, got {result!r}"
        )


# [pr_diff] fail_to_pass
def test_serializer_validate_blocks_legacy_filters():
    """InsightSerializer.validate must block legacy filter payloads when gate is active."""
    src = INSIGHT_PY.read_text()
    method_src = _extract_method_source(src, "InsightSerializer", "validate")
    assert method_src is not None, "InsightSerializer.validate method not found"

    # The validate method must:
    # 1. Check for "filters" in the attrs
    # 2. Call the legacy filters blocking function
    # 3. Raise PermissionDenied when blocked
    assert "PermissionDenied" in method_src, (
        "validate must raise PermissionDenied for blocked legacy filter writes"
    )
    assert "filters" in method_src, "validate must check for legacy filters in attrs"

    # Must reference a blocking function related to legacy filters
    lower_src = method_src.lower()
    assert "legacy" in lower_src and "filter" in lower_src and "block" in lower_src, (
        "validate must call the legacy insight filters blocking function"
    )


# [pr_diff] fail_to_pass
def test_serializer_validate_allows_query_insights():
    """InsightSerializer.validate must not block query-based insight writes."""
    src = INSIGHT_PY.read_text()
    method_src = _extract_method_source(src, "InsightSerializer", "validate")
    assert method_src is not None, "InsightSerializer.validate method not found"

    # The method must distinguish between legacy filters and query-based insights.
    # It should check that "query" is absent/empty before treating as legacy.
    assert "query" in method_src, (
        "validate must check for 'query' key to distinguish from legacy filters"
    )

    # Must call super().validate to preserve the rest of the validation chain
    assert "super()" in method_src, (
        "validate must call super().validate() to preserve the DRF validation chain"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """is_legacy_insight_filters_blocked must have real logic, not just pass/return."""
    src = INSIGHT_PY.read_text()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "is_legacy_insight_filters_blocked":
            # Function must have at least 3 statements (guard + return with call)
            stmts = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(stmts) >= 2, (
                f"Function body is too short ({len(stmts)} statements) — looks like a stub"
            )
            return
    raise AssertionError("is_legacy_insight_filters_blocked function not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:92 @ 011a93306e5dfe6e26464fba7c61680076df62c8
def test_new_function_has_type_hints():
    """New function must use type hints (AGENTS.md: 'Python: Use type hints (mypy-strict style)')."""
    src = INSIGHT_PY.read_text()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "is_legacy_insight_filters_blocked":
            # Check return type annotation
            assert node.returns is not None, (
                "is_legacy_insight_filters_blocked must have a return type annotation"
            )
            # Check parameter annotations (skip 'self' if present)
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                assert arg.annotation is not None, (
                    f"Parameter '{arg.arg}' must have a type annotation"
                )
            return
    raise AssertionError("is_legacy_insight_filters_blocked function not found")



def test_repo_ruff_check_posthog_api():
    """Repo: posthog/api/ directory passes ruff lint check (pass_to_pass).

    Validates that all Python files in the posthog/api/ directory,
    including insight.py and related modules, conform to the project's
    linting standards as defined in pyproject.toml.
    """
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/posthog/api/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed for posthog/api/: {r.stderr}"

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_test_creating_legacy_filter_insight_blocked_with():
    """fail_to_pass | PR added test 'test_creating_legacy_filter_insight_blocked_with_feature_flag' in test_insight.py"""
    test_path = Path(f"{REPO}/posthog/api/test/test_insight.py")
    src = test_path.read_text()
    tree = ast.parse(src)

    found_test = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "legacy_filter" in node.name and "blocked" in node.name:
            found_test = node
            break
    assert found_test is not None, (
        "Test method for blocked legacy filter insight not found in test_insight.py"
    )
    test_src = ast.get_source_segment(src, found_test)
    assert "Creating or updating insights with legacy filters is not available for this user." in test_src, (
        "Test must assert on the exact error message for blocked legacy filter writes"
    )
    assert "403" in test_src or "403_FORBIDDEN" in test_src, (
        "Test must assert HTTP 403 Forbidden for blocked legacy filter writes"
    )


def test_pr_added_test_creating_query_insight_not_blocked_by_legac():
    """fail_to_pass | PR added test 'test_creating_query_insight_not_blocked_by_legacy_filter_flag' in test_insight.py"""
    test_path = Path(f"{REPO}/posthog/api/test/test_insight.py")
    src = test_path.read_text()
    tree = ast.parse(src)

    found_test = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "query" in node.name and "legacy" in node.name:
            found_test = node
            break
    assert found_test is not None, (
        "Test method for query insight not blocked by legacy filter flag not found in test_insight.py"
    )
    test_src = ast.get_source_segment(src, found_test)
    assert "201" in test_src or "201_CREATED" in test_src, (
        "Test must assert HTTP 201 Created for query-based insight writes"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_and_validate_ui_apps_check_generated_ui_apps_are_up_to_date():
    """pass_to_pass | CI job 'Build and validate UI Apps' → step 'Check generated UI apps are up to date'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run generate:ui-apps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated UI apps are up to date' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_and_validate_ui_apps_build_ui_apps():
    """pass_to_pass | CI job 'Build and validate UI Apps' → step 'Build UI Apps'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build:ui-apps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build UI Apps' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_and_validate_ui_apps_validate_build_output():
    """pass_to_pass | CI job 'Build and validate UI Apps' → step 'Validate build output'"""
    r = subprocess.run(
        ["bash", "-lc", '# Each app should produce main.js and styles.css\n# Use find to recurse into wrapper dirs like generated/\nmissing=0\nfor app_dir in $(find services/mcp/public/ui-apps -mindepth 1 -type d ! -name generated | sort); do\n  app=$(basename "$app_dir")\n  if [ ! -f "$app_dir/main.js" ]; then\n    echo "::error::Missing main.js for $app"\n    missing=1\n  fi\n  if [ ! -f "$app_dir/styles.css" ]; then\n    echo "::error::Missing styles.css for $app"\n    missing=1\n  fi\ndone\nif [ "$missing" -eq 1 ]; then\n  exit 1\nfi\necho "All UI Apps built successfully."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Validate build output' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_jest_test_test_with_jest():
    """pass_to_pass | CI job 'Jest test' → step 'Test with Jest'"""
    r = subprocess.run(
        ["bash", "-lc", 'bin/turbo run test --filter=@posthog/frontend -- --maxWorkers=2'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test with Jest' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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

def test_ci_build___test_type_check():
    """pass_to_pass | CI job 'Build & Test' → step 'Type check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build___test_run_tests():
    """pass_to_pass | CI job 'Build & Test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")