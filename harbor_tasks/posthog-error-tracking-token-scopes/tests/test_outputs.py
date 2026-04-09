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
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{REPO}/{TARGET}').read())"],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in {TARGET}:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_read_actions_includes_values():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_read_actions")
    assert actions is not None, (
        "scope_object_read_actions is not defined on ErrorTrackingIssueViewSet — "
        "custom read actions like 'values' won't be scoped for API tokens"
    )
    assert "values" in actions, (
        f"'values' not in scope_object_read_actions: {actions}. "
        "The values endpoint will reject Personal API keys with error_tracking:read scope."
    )


def test_write_actions_includes_custom_actions():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_write_actions")
    assert actions is not None, (
        "scope_object_write_actions is not defined on ErrorTrackingIssueViewSet — "
        "custom write actions won't be scoped for API tokens"
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
            f"Standard DRF action '{std}' missing from scope_object_read_actions: {actions}. "
            "Setting this attribute overrides defaults, so standard actions must be included."
        )


def test_standard_write_actions_preserved():
    actions = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object_write_actions")
    assert actions is not None, "scope_object_write_actions not defined"
    for std in ["create", "update", "partial_update"]:
        assert std in actions, (
            f"Standard DRF action '{std}' missing from scope_object_write_actions: {actions}. "
            "Setting this attribute overrides defaults, so standard actions must be included."
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_scope_object_still_error_tracking():
    val = _get_class_attr("ErrorTrackingIssueViewSet", "scope_object")
    assert val == "error_tracking", (
        f"scope_object should be 'error_tracking', got: {val!r}"
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
