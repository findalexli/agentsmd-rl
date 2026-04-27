"""
Behavioral and integration tests for the litellm bulk-update team-permissions endpoint.

f2p tests (11): exercise the new endpoint via mocked Prisma. They all import
symbols (BulkUpdateTeamMemberPermissionsRequest, bulk_update_team_member_permissions)
that do not exist at the base commit, so they MUST fail before the agent's fix
and pass after.

p2p tests: subprocess-driven repo regression checks (existing pre-PR tests + black).
"""

import os
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

REPO = "/workspace/litellm"

# Make litellm importable
if REPO not in sys.path:
    sys.path.insert(0, REPO)


# --------------------------------------------------------------------------
# Helpers used by the f2p tests
# --------------------------------------------------------------------------

def _make_team(team_id, permissions):
    team = MagicMock()
    team.team_id = team_id
    team.team_member_permissions = permissions
    return team


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


# --------------------------------------------------------------------------
# f2p: behavior of bulk_update_team_member_permissions
# --------------------------------------------------------------------------


async def test_all_teams_appends_preserving_existing(monkeypatch):
    """apply_to_all_teams: permissions are merged, not overwritten."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_a = _make_team("team-a", ["/key/generate"])
    team_b = _make_team("team-b", ["/key/delete", "/key/update"])

    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=[team_a, team_b])
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 2
    calls = mock_batcher.litellm_teamtable.update.call_args_list
    assert len(calls) == 2

    team_a_call = [c for c in calls if c.kwargs["where"]["team_id"] == "team-a"][0]
    assert "/key/generate" in team_a_call.kwargs["data"]["team_member_permissions"]
    assert "/team/daily/activity" in team_a_call.kwargs["data"]["team_member_permissions"]

    team_b_call = [c for c in calls if c.kwargs["where"]["team_id"] == "team-b"][0]
    assert "/key/delete" in team_b_call.kwargs["data"]["team_member_permissions"]
    assert "/key/update" in team_b_call.kwargs["data"]["team_member_permissions"]


async def test_all_teams_skips_teams_that_already_have_permission(monkeypatch):
    """apply_to_all_teams: teams that already have the permission are skipped."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_has = _make_team("team-has", ["/team/daily/activity", "/key/update"])
    team_missing = _make_team("team-missing", ["/key/generate"])

    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=[team_has, team_missing])
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 1
    calls = mock_batcher.litellm_teamtable.update.call_args_list
    assert len(calls) == 1
    assert calls[0].kwargs["where"]["team_id"] == "team-missing"


async def test_all_teams_pagination(monkeypatch):
    """apply_to_all_teams: cursor-based pagination processes multiple pages of 500."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    page1 = [_make_team(f"team-{i}", []) for i in range(500)]
    page2 = [_make_team(f"team-{i}", []) for i in range(500, 502)]

    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(side_effect=[page1, page2])
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 502
    find_calls = mock_prisma.db.litellm_teamtable.find_many.call_args_list
    assert len(find_calls) == 2
    assert find_calls[1].kwargs["cursor"] == {"team_id": "team-499"}
    assert mock_batcher.commit.call_count == 2


async def test_team_ids_updates_only_specified_teams(monkeypatch):
    """team_ids: only the specified teams are fetched and updated."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_a = _make_team("team-a", ["/key/generate"])
    team_b = _make_team("team-b", ["/key/delete"])

    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=[team_a, team_b])
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], team_ids=["team-a", "team-b"]
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 2
    find_call = mock_prisma.db.litellm_teamtable.find_many.call_args
    assert find_call.kwargs["where"] == {"team_id": {"in": ["team-a", "team-b"]}}


async def test_team_ids_skips_teams_that_already_have_permission(monkeypatch):
    """team_ids: teams that already have the permission are skipped."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_has = _make_team("team-has", ["/team/daily/activity"])
    team_missing = _make_team("team-missing", [])

    mock_batcher = MagicMock()
    mock_batcher.commit = AsyncMock(return_value=None)

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=[team_has, team_missing])
    mock_prisma.db.batch_ = MagicMock(return_value=mock_batcher)
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], team_ids=["team-has", "team-missing"]
    )
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 1
    calls = mock_batcher.litellm_teamtable.update.call_args_list
    assert calls[0].kwargs["where"]["team_id"] == "team-missing"


async def test_team_ids_returns_404_for_missing_teams(monkeypatch):
    """If any provided team_ids don't exist, return 404."""
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    team_a = _make_team("team-a", ["/key/generate"])

    mock_prisma = MagicMock()
    mock_prisma.db.litellm_teamtable.find_many = AsyncMock(return_value=[team_a])
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], team_ids=["team-a", "team-b"]
    )

    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_admin_key_dict()
        )

    assert exc_info.value.status_code == 404
    assert "team-b" in str(exc_info.value.detail)


async def test_rejects_when_no_team_ids_and_no_apply_all(monkeypatch):
    """Must provide team_ids or set apply_to_all_teams=True."""
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    mock_prisma = MagicMock()
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(permissions=["/team/daily/activity"])

    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_admin_key_dict()
        )
    assert exc_info.value.status_code == 400


async def test_rejects_when_both_team_ids_and_apply_all(monkeypatch):
    """Cannot set both team_ids and apply_to_all_teams=True."""
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    mock_prisma = MagicMock()
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

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


async def test_empty_permissions_list_is_noop(monkeypatch):
    """Passing an empty permissions list returns immediately with 0 updated."""
    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    mock_prisma = MagicMock()
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(permissions=[])
    result = await bulk_update_team_member_permissions(
        data=data, user_api_key_dict=_admin_key_dict()
    )

    assert result["teams_updated"] == 0
    mock_prisma.db.litellm_teamtable.find_many.assert_not_called()


async def test_non_admin_gets_403(monkeypatch):
    """Non-admin users are rejected with 403."""
    from fastapi import HTTPException

    from litellm.proxy.management_endpoints.team_endpoints import (
        bulk_update_team_member_permissions,
    )
    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    mock_prisma = MagicMock()
    monkeypatch.setattr("litellm.proxy.proxy_server.prisma_client", mock_prisma)

    data = BulkUpdateTeamMemberPermissionsRequest(
        permissions=["/team/daily/activity"], apply_to_all_teams=True
    )

    with pytest.raises(HTTPException) as exc_info:
        await bulk_update_team_member_permissions(
            data=data, user_api_key_dict=_non_admin_key_dict()
        )
    assert exc_info.value.status_code == 403


def test_invalid_permission_rejected_by_pydantic():
    """Invalid permission strings are rejected at the type level by Pydantic."""
    from pydantic import ValidationError

    from litellm.types.proxy.management_endpoints.team_endpoints import (
        BulkUpdateTeamMemberPermissionsRequest,
    )

    with pytest.raises(ValidationError):
        BulkUpdateTeamMemberPermissionsRequest(permissions=["/not/a/real/permission"])


# --------------------------------------------------------------------------
# p2p: existing repo tests must still pass after the agent's edits
# --------------------------------------------------------------------------


def test_p2p_existing_team_default_params_safe_overrides():
    """Existing pre-PR tests in test_team_default_params.py must still pass.

    Guards against the agent breaking adjacent code (regressions to
    LITELLM_SETTINGS_SAFE_DB_OVERRIDES, default-team-params plumbing, etc.).
    """
    r = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/test_litellm/proxy/management_endpoints/test_team_default_params.py::TestSafeDbOverrides",
            "-x", "--tb=short", "--no-header", "-q",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Existing pre-PR tests failed:\n"
        f"STDOUT:\n{r.stdout[-2500:]}\n\nSTDERR:\n{r.stderr[-500:]}"
    )


def test_p2p_module_imports_cleanly():
    """The modified modules must still import without error."""
    r = subprocess.run(
        [
            sys.executable, "-c",
            "import litellm.proxy.management_endpoints.team_endpoints as m; "
            "import litellm.types.proxy.management_endpoints.team_endpoints as t; "
            "assert hasattr(m, 'router'); "
            "assert hasattr(t, 'UpdateTeamMemberPermissionsRequest');"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Module import failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


