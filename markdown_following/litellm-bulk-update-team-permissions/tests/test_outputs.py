"""
Tests for `POST /team/permissions_bulk_update`:
new endpoint, request/response Pydantic models, paginated
read + batched write, validation, admin-only access.

These mirror the contract tested by the upstream PR. We mock prisma_client
end-to-end — no real DB needed.
"""
from __future__ import annotations

import os
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

REPO = "/workspace/litellm"
sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_team(team_id, permissions):
    t = MagicMock()
    t.team_id = team_id
    t.team_member_permissions = permissions
    return t


def _admin_key_dict():
    from litellm.proxy._types import LitellmUserRoles, UserAPIKeyAuth

    return UserAPIKeyAuth(
        user_role=LitellmUserRoles.PROXY_ADMIN.value,
        api_key="sk-1234",
    )


def _non_admin_key_dict():
    from litellm.proxy._types import LitellmUserRoles, UserAPIKeyAuth

    return UserAPIKeyAuth(
        user_role=LitellmUserRoles.INTERNAL_USER.value,
        api_key="sk-user",
    )


def _mock_prisma(monkeypatch, find_many_return, raise_on_find=False):
    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    if raise_on_find:
        mock_prisma.db.litellm_teamtable.find_many = AsyncMock(side_effect=Exception("should not be called"))
    elif isinstance(find_many_return, list) and find_many_return and isinstance(find_many_return[0], list):
        # multiple pages
        mock_prisma.db.litellm_teamtable.find_many = AsyncMock(side_effect=find_many_return)
    else:
        mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=find_many_return)
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)
    return mock_prisma, mock_batcher


# ---------------------------------------------------------------------------
# Schema / import tests
# ---------------------------------------------------------------------------


def test_request_model_has_required_fields():
    """BulkUpdateTeamMemberPermissionsRequest exists with permissions, team_ids, apply_to_all_teams."""
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    fields = BulkUpdateTeamMemberPermissionsRequest.model_fields
    assert "permissions" in fields
    assert "team_ids" in fields
    assert "apply_to_all_teams" in fields
    # default for apply_to_all_teams is False
    inst = BulkUpdateTeamMemberPermissionsRequest(permissions=["/team/daily/activity"])
    assert inst.apply_to_all_teams is False
    assert inst.team_ids is None


def test_response_model_has_required_fields():
    """BulkUpdateTeamMemberPermissionsResponse exists with message, teams_updated."""
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsResponse,
    )

    fields = BulkUpdateTeamMemberPermissionsResponse.model_fields
    assert "message" in fields
    assert "teams_updated" in fields


def test_endpoint_function_importable():
    """bulk_update_team_member_permissions is exported from team_endpoints."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )

    assert callable(bulk_update_team_member_permissions)


def test_invalid_permission_rejected_by_pydantic():
    """Permissions are typed against KeyManagementRoutes — random strings are rejected."""
    from pydantic import ValidationError

    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    with pytest.raises(ValidationError):
        BulkUpdateTeamMemberPermissionsRequest(permissions=["/not/a/real/permission"])


# ---------------------------------------------------------------------------
# apply_to_all_teams behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_all_teams_appends_preserving_existing(monkeypatch):
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_a = _make_team("team-a", ["/key/generate"])
    team_b = _make_team("team-b", ["/key/delete", "/key/update"])
    _, batcher = _mock_prisma(monkeypatch, [team_a, team_b])

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 2
    calls = batcher.litellm_teamtable.update.call_args_list
    assert len(calls) == 2
    a_call = [c for c in calls if c.kwargs["where"]["team_id"] == "team-a"][0]
    a_perms = a_call.kwargs["data"]["team_member_permissions"]
    assert "/key/generate" in a_perms
    assert "/team/daily/activity" in a_perms
    b_call = [c for c in calls if c.kwargs["where"]["team_id"] == "team-b"][0]
    b_perms = b_call.kwargs["data"]["team_member_permissions"]
    assert "/key/delete" in b_perms
    assert "/key/update" in b_perms
    assert "/team/daily/activity" in b_perms


@pytest.mark.asyncio
async def test_all_teams_skips_teams_already_having_permission(monkeypatch):
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_has = _make_team("team-has", ["/team/daily/activity", "/key/update"])
    team_missing = _make_team("team-missing", ["/key/generate"])
    _, batcher = _mock_prisma(monkeypatch, [team_has, team_missing])

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 1
    calls = batcher.litellm_teamtable.update.call_args_list
    assert len(calls) == 1
    assert calls[0].kwargs["where"]["team_id"] == "team-missing"


@pytest.mark.asyncio
async def test_pagination_processes_multiple_pages(monkeypatch):
    """Cursor-based pagination — the second page picks up after the last team_id of the first."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    page1 = [_make_team(f"team-{i:04d}", []) for i in range(500)]
    page2 = [_make_team(f"team-{i:04d}", []) for i in range(500, 502)]
    prisma, batcher = _mock_prisma(monkeypatch, [page1, page2])

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 502
    find_calls = prisma.db.litellm_teamtable.find_many.call_args_list
    assert len(find_calls) == 2
    # second find_many uses cursor pointing at the last id of page 1
    second_kwargs = find_calls[1].kwargs
    assert "cursor" in second_kwargs
    assert second_kwargs["cursor"] == {"team_id": "team-0499"}


@pytest.mark.asyncio
async def test_uses_batch_writer_not_individual_updates(monkeypatch):
    """Per agent config rule: multiple writes to the same table must go through batch_().

    A correct implementation must use prisma_client.db.batch_() rather than
    calling .update() directly on the model in a loop.
    """
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    teams = [_make_team(f"team-{i}", []) for i in range(3)]

    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=teams)
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 3
    # batch_() is called and commit is invoked exactly once for that batch
    assert mock_prisma.db.batch_.call_count >= 1
    assert mock_batcher.commit.await_count >= 1
    # update_many on the table directly must NOT be used (different semantics)
    # and per-team .update() outside of the batcher must NOT be used
    assert mock_prisma.db.litellm_teamtable.update.call_count == 0


# ---------------------------------------------------------------------------
# team_ids behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_team_ids_uses_in_filter(monkeypatch):
    """find_many is called with `where={"team_id": {"in": [...]}}` (no N+1)."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_a = _make_team("team-a", ["/key/generate"])
    team_b = _make_team("team-b", ["/key/delete"])
    prisma, _ = _mock_prisma(monkeypatch, [team_a, team_b])

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], team_ids=["team-a", "team-b"]
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 2
    find_call = prisma.db.litellm_teamtable.find_many.call_args
    assert find_call.kwargs["where"] == {"team_id": {"in": ["team-a", "team-b"]}}
    # find_many is called exactly once when team_ids is provided (no per-team loop)
    assert prisma.db.litellm_teamtable.find_many.call_count == 1


@pytest.mark.asyncio
async def test_team_ids_returns_404_for_missing(monkeypatch):
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_a = _make_team("team-a", ["/key/generate"])
    _mock_prisma(monkeypatch, [team_a])

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], team_ids=["team-a", "team-missing"]
    )

    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_admin_key_dict()
        )

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_400_when_neither_team_ids_nor_apply_all(monkeypatch):
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", MagicMock())

    data = BulkUpdateTeamMemberPermissionsRequest(permissions=["/team/daily/activity"])
    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_admin_key_dict()
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_400_when_both_team_ids_and_apply_all(monkeypatch):
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", MagicMock())

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"],
        team_ids=["team-a"],
        apply_to_all_teams=True,
    )
    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_admin_key_dict()
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_empty_permissions_is_noop(monkeypatch):
    """Empty permissions list → 0 teams updated, no DB read."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=[])
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(permissions=[])
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )
    assert result["teams_updated"] == 0
    mock_prisma.db.litellm_teamtable.find_many.assert_not_called()


@pytest.mark.asyncio
async def test_non_admin_gets_403(monkeypatch):
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", MagicMock())

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_non_admin_key_dict()
        )
    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# pass-to-pass: existing test file in the repo still imports/runs.
# ---------------------------------------------------------------------------


def test_existing_team_default_params_tests_pass():
    """The existing test file's pre-PR baseline still passes after edits.

    Guards against accidental breakage of unrelated team endpoint logic.
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_litellm/proxy/management_endpoints/test_team_default_params.py::TestSafeDbOverrides",
        "-x",
        "-q",
        "--no-header",
        "--tb=short",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"Existing tests failed (stdout):\n{r.stdout[-2000:]}\n"
        f"(stderr):\n{r.stderr[-2000:]}"
    )


def test_ruff_check_doesnt_regress_changed_files():
    """Ruff error count on the changed files must not increase vs. base.

    The base commit already has a couple of unused-import warnings in these
    files; we just guard that the agent's diff doesn't introduce new ones.
    """
    cmd = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        "--exit-zero",
        "--statistics",
        "litellm/proxy/management_endpoints/team_endpoints.py",
        "litellm/types/proxy/management_endpoints/team_endpoints.py",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"ruff invocation failed:\n{r.stdout}\n{r.stderr}"
    # Count of total errors reported on the line that says "Found N errors"
    # is harder; instead, count by parsing each statistic line "<N> <code> ..."
    total = 0
    for line in r.stdout.splitlines():
        parts = line.strip().split()
        if parts and parts[0].isdigit():
            total += int(parts[0])
    # Base commit has exactly 2 ruff errors in these files (F401 unused imports).
    assert total <= 2, (
        f"Ruff regressed: {total} errors > baseline of 2.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_test_install_helm_unit_test_plugin():
    """pass_to_pass | CI job 'unit-test' → step 'Install Helm Unit Test Plugin'"""
    r = subprocess.run(
        ["bash", "-lc", 'helm plugin install https://github.com/helm-unittest/helm-unittest --version v0.4.4'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Install Helm Unit Test Plugin' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_test_verify_helm_unit_test_plugin_integrity():
    """pass_to_pass | CI job 'unit-test' → step 'Verify Helm Unit Test Plugin integrity'"""
    r = subprocess.run(
        ["bash", "-lc", 'EXPECTED_SHA="e251ba198448629678ff2168e1a469249d998155"\nPLUGIN_DIR="$(helm env HELM_PLUGINS)/helm-unittest"\nACTUAL_SHA="$(git -C "$PLUGIN_DIR" rev-parse HEAD)"\nif [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then\n  echo "::error::Helm unittest plugin checksum mismatch! Expected $EXPECTED_SHA but got $ACTUAL_SHA"\n  exit 1\nfi\necho "Helm unittest plugin integrity verified: $ACTUAL_SHA"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Helm Unit Test Plugin integrity' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_test_run_unit_tests():
    """pass_to_pass | CI job 'unit-test' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", "helm unittest -f 'tests/*.yaml' deploy/charts/litellm-helm"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")