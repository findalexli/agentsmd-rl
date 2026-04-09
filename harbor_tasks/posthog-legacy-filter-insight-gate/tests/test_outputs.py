"""
Task: posthog-legacy-filter-insight-gate
Repo: posthog @ 011a93306e5dfe5e26464fba7c61680076df62c8
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

# [agent_config] fail_to_pass — AGENTS.md:92 @ 011a93306e5dfe5e26464fba7c61680076df62c8
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
