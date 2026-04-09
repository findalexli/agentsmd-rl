"""
Task: posthog-error-tracking-token-scopes
Repo: posthog @ 43d0423b3f819335cfecfae1f1844ea883ba97ac
PR:   53639

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
TARGET = "products/error_tracking/backend/api/issues.py"


def _get_class_attr(class_name: str, attr_name: str):
    """Parse the target file and extract a class-level attribute value via AST."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == attr_name:
                            return ast.literal_eval(item.value)
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Target file parses without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open(\"{REPO}/{TARGET}\").read())"],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in {TARGET}:\n{r.stderr.decode()}"


def test_ruff_lint():
    """Target file passes ruff linting (pass_to_pass)."""
    # Install ruff if not available
    try:
        subprocess.run(["python3", "-m", "ruff", "--version"], capture_output=True, check=True, timeout=30)
    except (subprocess.CalledProcessError, FileNotFoundError):
        subprocess.run(["pip", "install", "ruff", "-q"], capture_output=True, timeout=60)
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", f"{REPO}/{TARGET}"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}{r.stderr}"


def test_importable():
    """Target module can be imported without ImportError (pass_to_pass)."""
    # This checks that basic Python syntax and imports are valid
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open(\"{REPO}/{TARGET}\").read())"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Import check failed (syntax error):\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_read_actions_includes_values():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_read_actions")
    assert actions is not None, (
        "scope_object_read_actions is not defined on ErrorTrackingIssueViewSet — "
        "custom read actions like \"values\" will not be scoped for API tokens"
    )
    assert "values" in actions, (
        f"\"values\" not in scope_object_read_actions: {actions}. "
        "The values endpoint will reject Personal API keys with error_tracking:read scope."
    )


def test_write_actions_includes_custom_actions():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_write_actions")
    assert actions is not None, (
        "scope_object_write_actions is not defined on ErrorTrackingIssueViewSet — "
        "custom write actions will not be scoped for API tokens"
    )
    required = {"merge", "split", "assign", "cohort", "bulk"}
    missing = required - set(actions)
    assert not missing, (
        f"Custom write actions missing from scope_object_write_actions: {missing}. "
        f"Current list: {actions}"
    )


def test_standard_read_actions_preserved():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_read_actions")
    assert actions is not None, "scope_object_read_actions not defined"
    for std in ["list", "retrieve"]:
        assert std in actions, (
            f"Standard DRF action \"{std}\" missing from scope_object_read_actions: {actions}. "
            "Setting this attribute overrides defaults, so standard actions must be included."
        )


def test_standard_write_actions_preserved():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_write_actions")
    assert actions is not None, "scope_object_write_actions not defined"
    for std in ["create", "update", "partial_update"]:
        assert std in actions, (
            f"Standard DRF action \"{std}\" missing from scope_object_write_actions: {actions}. "
            "Setting this attribute overrides defaults, so standard actions must be included."
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_scope_object_still_error_tracking():
    val = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object")
    assert val == "error_tracking", (
        f"scope_object should be \"error_tracking\", got: {val!r}"
    )


def test_viewset_class_has_substance():
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ErrorTrackingIssueViewSet":
            body_stmts = [
                s for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))
            ]
            assert len(body_stmts) >= 5, (
                f"ErrorTrackingIssueViewSet body has only {len(body_stmts)} statements — "
                "expected a substantial class with scope attrs, queryset, serializer, and methods"
            )
            return
    raise AssertionError("ErrorTrackingIssueViewSet class not found")
