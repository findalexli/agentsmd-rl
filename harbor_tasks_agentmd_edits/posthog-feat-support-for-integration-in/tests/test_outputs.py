"""
Task: posthog-feat-support-for-integration-in
Repo: PostHog/posthog @ 6fe1d5dafe2218c2e35121466285017ecadaed60
PR:   51915

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import py_compile
from pathlib import Path

REPO = "/workspace/posthog"

BIGQUERY_MODULE = (
    Path(REPO) / "products" / "batch_exports" / "backend" / "api" / "destination_tests" / "bigquery.py"
)
HTTP_MODULE = Path(REPO) / "posthog" / "batch_exports" / "http.py"
README_PATH = (
    Path(REPO) / "products" / "batch_exports" / "backend" / "tests" / "temporal" / "README.md"
)


def _parse_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text())


def _get_classes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {node.name: node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def _get_functions(tree: ast.Module) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for path in [BIGQUERY_MODULE, HTTP_MODULE]:
        py_compile.compile(str(path), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_get_client_helper_function():
    """bigquery.py must have a get_client() helper that accepts project_id, integration, and service_account_info."""
    tree = _parse_module(BIGQUERY_MODULE)
    funcs = _get_functions(tree)
    assert "get_client" in funcs, "get_client function must exist in bigquery.py"

    func = funcs["get_client"]
    param_names = [arg.arg for arg in func.args.args]
    assert "project_id" in param_names, "get_client must accept project_id parameter"
    assert "integration" in param_names, "get_client must accept integration parameter"
    assert "service_account_info" in param_names, "get_client must accept service_account_info parameter"


# [pr_diff] fail_to_pass
def test_impersonate_service_account_step():
    """bigquery.py must define BigQueryImpersonateServiceAccountTestStep with _run_step."""
    tree = _parse_module(BIGQUERY_MODULE)
    classes = _get_classes(tree)
    cls_name = "BigQueryImpersonateServiceAccountTestStep"
    assert cls_name in classes, f"{cls_name} must exist in bigquery.py"

    cls = classes[cls_name]
    method_names = {
        node.name
        for node in ast.walk(cls)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_run_step" in method_names, f"{cls_name} must implement _run_step"
    assert "_is_configured" in method_names, f"{cls_name} must implement _is_configured"

    # Must accept integration parameter in __init__
    init = next((n for n in ast.walk(cls) if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
    assert init is not None, f"{cls_name} must have __init__"
    init_params = [a.arg for a in init.args.args]
    assert "integration" in init_params, f"{cls_name}.__init__ must accept integration"


# [pr_diff] fail_to_pass
def test_verify_ownership_step():
    """bigquery.py must define BigQueryVerifyServiceAccountOwnershipTestStep."""
    tree = _parse_module(BIGQUERY_MODULE)
    classes = _get_classes(tree)
    cls_name = "BigQueryVerifyServiceAccountOwnershipTestStep"
    assert cls_name in classes, f"{cls_name} must exist in bigquery.py"

    cls = classes[cls_name]
    method_names = {
        node.name
        for node in ast.walk(cls)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_run_step" in method_names, f"{cls_name} must implement _run_step"

    # Must accept organization_id parameter
    init = next((n for n in ast.walk(cls) if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
    assert init is not None
    init_params = [a.arg for a in init.args.args]
    assert "organization_id" in init_params, f"{cls_name}.__init__ must accept organization_id"
    assert "integration" in init_params, f"{cls_name}.__init__ must accept integration"


# [pr_diff] fail_to_pass
def test_http_passes_integration_object():
    """http.py must pass the integration object in test_configuration dict."""
    content = HTTP_MODULE.read_text()
    # The fix adds "integration": integration to the test_configuration dict
    # Check both run_test_step_new and run_test_step methods
    assert '"integration": integration' in content or "'integration': integration" in content, (
        "http.py must include integration in test_configuration dict"
    )


# [pr_diff] fail_to_pass
def test_existing_steps_accept_integration():
    """BigQueryProjectTestStep, BigQueryDatasetTestStep, BigQueryTableTestStep must accept integration."""
    tree = _parse_module(BIGQUERY_MODULE)
    classes = _get_classes(tree)

    for cls_name in ["BigQueryProjectTestStep", "BigQueryDatasetTestStep", "BigQueryTableTestStep"]:
        assert cls_name in classes, f"{cls_name} must exist"
        cls = classes[cls_name]
        init = next(
            (n for n in ast.walk(cls) if isinstance(n, ast.FunctionDef) and n.name == "__init__"),
            None,
        )
        assert init is not None, f"{cls_name} must have __init__"
        params = [a.arg for a in init.args.args]
        assert "integration" in params, f"{cls_name}.__init__ must accept integration parameter"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README must document new auth mechanisms
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_impersonate_step_not_stub():
    """BigQueryImpersonateServiceAccountTestStep._run_step must have real logic."""
    tree = _parse_module(BIGQUERY_MODULE)
    classes = _get_classes(tree)
    cls = classes["BigQueryImpersonateServiceAccountTestStep"]

    run_step = next(
        (n for n in ast.walk(cls) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "_run_step"),
        None,
    )
    assert run_step is not None
    # Must have meaningful body (not just pass/raise NotImplementedError)
    stmts = [s for s in run_step.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(stmts) >= 3, (
        f"_run_step has only {len(stmts)} non-trivial statements — appears to be a stub"
    )
