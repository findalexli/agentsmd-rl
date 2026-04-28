"""
Tests for the LiteLLM access-group-resource resolver helper used by the
team_info / list_team_v2 endpoints.

The fail-to-pass tests target the new `_batch_resolve_access_group_resources`
helper plus the three new fields it populates on the team response objects.
The pass-to-pass tests are a slice of the upstream proxy unit tests.
"""

import inspect
import os
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

REPO = "/workspace/litellm"
sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# fail-to-pass: behavior of _batch_resolve_access_group_resources
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_resolver_empty_list_returns_empty_dict():
    """No IDs -> empty dict, and no DB query is issued."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    fake_find_many = AsyncMock(return_value=[])
    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = fake_find_many

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources([])

    assert result == {}
    assert fake_find_many.await_count == 0


@pytest.mark.asyncio
async def test_batch_resolver_single_group_returns_resources():
    """One ID -> dict keyed by group id with models/mcp_server_ids/agent_ids."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    row = MagicMock()
    row.access_group_id = "ag-1"
    row.access_model_names = ["gpt-4", "claude-3"]
    row.access_mcp_server_ids = ["mcp-a"]
    row.access_agent_ids = ["agent-x", "agent-y"]

    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = AsyncMock(return_value=[row])

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources(["ag-1"])

    assert set(result["ag-1"].keys()) == {"models", "mcp_server_ids", "agent_ids"}
    assert sorted(result["ag-1"]["models"]) == ["claude-3", "gpt-4"]
    assert result["ag-1"]["mcp_server_ids"] == ["mcp-a"]
    assert sorted(result["ag-1"]["agent_ids"]) == ["agent-x", "agent-y"]


@pytest.mark.asyncio
async def test_batch_resolver_multiple_groups_distinct():
    """Two distinct groups -> both surface in the result map."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    r1 = MagicMock()
    r1.access_group_id = "ag-1"
    r1.access_model_names = ["gpt-4"]
    r1.access_mcp_server_ids = ["mcp-a"]
    r1.access_agent_ids = ["agent-x"]

    r2 = MagicMock()
    r2.access_group_id = "ag-2"
    r2.access_model_names = ["gemini-pro"]
    r2.access_mcp_server_ids = ["mcp-b"]
    r2.access_agent_ids = ["agent-y"]

    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = AsyncMock(return_value=[r1, r2])

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources(["ag-1", "ag-2"])

    assert result["ag-1"]["models"] == ["gpt-4"]
    assert result["ag-2"]["models"] == ["gemini-pro"]
    assert result["ag-1"]["mcp_server_ids"] == ["mcp-a"]
    assert result["ag-2"]["mcp_server_ids"] == ["mcp-b"]


@pytest.mark.asyncio
async def test_batch_resolver_omits_missing_groups():
    """A requested ID not present in DB rows is silently absent from result."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    row = MagicMock()
    row.access_group_id = "ag-known"
    row.access_model_names = ["gpt-4"]
    row.access_mcp_server_ids = []
    row.access_agent_ids = []

    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = AsyncMock(return_value=[row])

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources(["ag-known", "ag-missing"])

    assert "ag-known" in result
    assert "ag-missing" not in result


@pytest.mark.asyncio
async def test_batch_resolver_returns_empty_when_prisma_none():
    """If the global prisma_client is None, the resolver short-circuits to {}."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    with patch("litellm.proxy.proxy_server.prisma_client", None):
        result = await _batch_resolve_access_group_resources(["ag-1", "ag-2"])

    assert result == {}


@pytest.mark.asyncio
async def test_batch_resolver_deduplicates_input_ids():
    """Repeated IDs in the input must collapse to a single DB query value."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    row = MagicMock()
    row.access_group_id = "ag-1"
    row.access_model_names = ["gpt-4"]
    row.access_mcp_server_ids = []
    row.access_agent_ids = []

    fake_find_many = AsyncMock(return_value=[row])
    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = fake_find_many

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources(["ag-1", "ag-1", "ag-1"])

    # Single batch call with deduplicated IDs
    assert fake_find_many.await_count == 1
    where = fake_find_many.await_args.kwargs["where"]
    in_ids = where["access_group_id"]["in"]
    assert sorted(in_ids) == ["ag-1"]
    assert "ag-1" in result


@pytest.mark.asyncio
async def test_batch_resolver_handles_null_resource_columns():
    """access_model_names / mcp_server_ids / agent_ids may be None at the DB layer."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    row = MagicMock()
    row.access_group_id = "ag-empty"
    row.access_model_names = None
    row.access_mcp_server_ids = None
    row.access_agent_ids = None

    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = AsyncMock(return_value=[row])

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources(["ag-empty"])

    assert result["ag-empty"]["models"] == []
    assert result["ag-empty"]["mcp_server_ids"] == []
    assert result["ag-empty"]["agent_ids"] == []


@pytest.mark.asyncio
async def test_batch_resolver_uses_single_db_call_for_many_ids():
    """Pulling N groups must use exactly ONE find_many invocation (no N+1)."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    rows = []
    for i in range(5):
        r = MagicMock()
        r.access_group_id = f"ag-{i}"
        r.access_model_names = [f"model-{i}"]
        r.access_mcp_server_ids = []
        r.access_agent_ids = []
        rows.append(r)

    fake_find_many = AsyncMock(return_value=rows)
    fake_prisma = MagicMock()
    fake_prisma.db.litellm_accessgrouptable.find_many = fake_find_many

    with patch("litellm.proxy.proxy_server.prisma_client", fake_prisma):
        result = await _batch_resolve_access_group_resources(
            [f"ag-{i}" for i in range(5)]
        )

    assert fake_find_many.await_count == 1
    assert len(result) == 5
    assert sorted(result["ag-3"]["models"]) == ["model-3"]


@pytest.mark.asyncio
async def test_batch_resolver_is_async_coroutine():
    """The helper must be an async function (called with `await`)."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        _batch_resolve_access_group_resources,
    )

    assert inspect.iscoroutinefunction(_batch_resolve_access_group_resources)


# ---------------------------------------------------------------------------
# fail-to-pass: response models gain the three access-group fields
# ---------------------------------------------------------------------------


def test_team_info_response_object_has_access_group_fields():
    """TeamInfoResponseObjectTeamTable exposes access_group_{models,mcp_server_ids,agent_ids}."""
    from litellm.proxy._types import TeamInfoResponseObjectTeamTable

    fields = TeamInfoResponseObjectTeamTable.model_fields
    assert "access_group_models" in fields
    assert "access_group_mcp_server_ids" in fields
    assert "access_group_agent_ids" in fields


def test_team_list_item_has_access_group_fields():
    """TeamListItem (paginated list response) exposes the same three fields."""
    from litellm.types.proxy.management_endpoints.team_endpoints import TeamListItem

    fields = TeamListItem.model_fields
    assert "access_group_models" in fields
    assert "access_group_mcp_server_ids" in fields
    assert "access_group_agent_ids" in fields


def test_access_group_fields_default_to_none():
    """The new fields are optional and default to None when not provided."""
    from litellm.types.proxy.management_endpoints.team_endpoints import TeamListItem

    item = TeamListItem(team_id="t1")
    assert item.access_group_models is None
    assert item.access_group_mcp_server_ids is None
    assert item.access_group_agent_ids is None


# ---------------------------------------------------------------------------
# pass-to-pass: pre-existing tests in the proxy team_endpoints unit suite
# ---------------------------------------------------------------------------


def _run_upstream_tests(node_ids):
    """Run a subset of upstream unit tests via subprocess and return its CompletedProcess."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--no-header",
        "-p",
        "no:cacheprovider",
        *node_ids,
    ]
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )


_TEAM_ENDPOINTS_TEST = (
    "tests/test_litellm/proxy/management_endpoints/test_team_endpoints.py"
)


def test_p2p_validate_team_org_change():
    """Upstream `validate_team_org_change` tests must continue to pass."""
    r = _run_upstream_tests(
        [
            f"{_TEAM_ENDPOINTS_TEST}::test_validate_team_org_change_same_org_id",
            f"{_TEAM_ENDPOINTS_TEST}::test_validate_team_org_change_members_in_org",
            f"{_TEAM_ENDPOINTS_TEST}::test_validate_team_org_change_member_not_in_org",
        ]
    )
    assert r.returncode == 0, (
        f"Upstream pass-to-pass tests failed:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-1000:]}"
    )


def test_p2p_team_member_helpers():
    """Upstream team_member helper tests must continue to pass."""
    r = _run_upstream_tests(
        [
            f"{_TEAM_ENDPOINTS_TEST}::test_team_member_add_duplication_check_raises_proxy_exception",
            f"{_TEAM_ENDPOINTS_TEST}::test_team_member_add_duplication_check_allows_new_member",
            f"{_TEAM_ENDPOINTS_TEST}::test_clean_team_member_fields",
            f"{_TEAM_ENDPOINTS_TEST}::test_clean_team_member_fields_with_missing_fields",
        ]
    )
    assert r.returncode == 0, (
        f"Upstream pass-to-pass tests failed:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-1000:]}"
    )


def test_p2p_team_models_helpers():
    """Upstream team-models helper tests must continue to pass."""
    r = _run_upstream_tests(
        [
            f"{_TEAM_ENDPOINTS_TEST}::test_add_new_models_to_team",
            f"{_TEAM_ENDPOINTS_TEST}::test_add_new_models_to_team_with_existing_models",
        ]
    )
    assert r.returncode == 0, (
        f"Upstream pass-to-pass tests failed:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_generate_prisma_client():
    """pass_to_pass | CI job 'test' → step 'Generate Prisma client'"""
    r = subprocess.run(
        ["bash", "-lc", 'poetry run pip install nodejs-wheel-binaries==24.13.1\npoetry run prisma generate --schema litellm/proxy/schema.prisma'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Generate Prisma client' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests_matrix_test_group_name():
    """pass_to_pass | CI job 'test' → step 'Run tests - ${{ matrix.test-group.name }}'"""
    r = subprocess.run(
        ["bash", "-lc", 'poetry run pytest ${{ matrix.test-group.path }} \\\n  --tb=short -vv \\\n  --maxfail=10 \\\n  -n ${{ matrix.test-group.workers }} \\\n  --reruns ${{ matrix.test-group.reruns }} \\\n  --reruns-delay 1 \\\n  --dist=loadscope \\\n  --durations=20 \\\n  --cov=litellm \\\n  --cov-report=xml:coverage-${{ matrix.test-group.name }}.xml \\\n  --cov-config=pyproject.toml'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Run tests - ${{ matrix.test-group.name }}' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")