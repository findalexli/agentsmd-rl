#!/bin/bash
# Gold-patch oracle: applies the litellm#25239 implementation diff (no tests).
# Idempotent: skips if the distinctive marker is already present.

set -euo pipefail

cd /workspace/litellm

# Idempotency guard
if grep -q "permissions_bulk_update" litellm/proxy/management_endpoints/team_endpoints.py 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

# Apply the implementation patch (types + endpoint code only).
# NOTE: This patch is inlined; it is NEVER fetched from GitHub.
git apply --whitespace=nowarn <<'PATCH'
diff --git a/litellm/proxy/management_endpoints/team_endpoints.py b/litellm/proxy/management_endpoints/team_endpoints.py
index e1534573789..e4e0b64af59 100644
--- a/litellm/proxy/management_endpoints/team_endpoints.py
+++ b/litellm/proxy/management_endpoints/team_endpoints.py
@@ -100,6 +100,8 @@
 from litellm.types.proxy.management_endpoints.team_endpoints import (
     BulkTeamMemberAddRequest,
     BulkTeamMemberAddResponse,
+    BulkUpdateTeamMemberPermissionsRequest,
+    BulkUpdateTeamMemberPermissionsResponse,
     GetTeamMemberPermissionsResponse,
     TeamListItem,
     TeamListResponse,
@@ -4274,6 +4276,151 @@ async def update_team_member_permissions(
     return updated_team


+@router.post(
+    "/team/permissions_bulk_update",
+    tags=["team management"],
+    dependencies=[Depends(user_api_key_auth)],
+    response_model=BulkUpdateTeamMemberPermissionsResponse,
+)
+@management_endpoint_wrapper
+async def bulk_update_team_member_permissions(
+    data: BulkUpdateTeamMemberPermissionsRequest,
+    user_api_key_dict: UserAPIKeyAuth = Depends(user_api_key_auth),
+):
+    """
+    Append permissions to existing teams.
+
+    Either pass team_ids to target specific teams, or set
+    apply_to_all_teams=True to update every team. For each team,
+    the provided permissions are merged with the team's existing
+    permissions (duplicates are skipped).
+    """
+    from litellm.proxy.proxy_server import prisma_client
+
+    if prisma_client is None:
+        raise HTTPException(status_code=500, detail={"error": "No db connected"})
+
+    if user_api_key_dict.user_role != LitellmUserRoles.PROXY_ADMIN.value:
+        raise HTTPException(
+            status_code=403,
+            detail={"error": "Only proxy admins can bulk-update team permissions"},
+        )
+
+    if not data.permissions:
+        return {
+            "message": "No permissions provided",
+            "teams_updated": 0,
+        }
+
+    if not data.apply_to_all_teams and not data.team_ids:
+        raise HTTPException(
+            status_code=400,
+            detail={
+                "error": "Must provide team_ids or set apply_to_all_teams=true"
+            },
+        )
+
+    if data.apply_to_all_teams and data.team_ids:
+        raise HTTPException(
+            status_code=400,
+            detail={
+                "error": "Cannot set both apply_to_all_teams=true and team_ids"
+            },
+        )
+
+    permissions_to_add = set(data.permissions)
+
+    if data.team_ids:
+        teams_updated = await _append_permissions_to_specific_teams(
+            prisma_client, data.team_ids, permissions_to_add
+        )
+    else:
+        teams_updated = await _append_permissions_to_all_teams(
+            prisma_client, permissions_to_add
+        )
+
+    return {
+        "message": "Team permissions updated successfully",
+        "teams_updated": teams_updated,
+        "permissions_appended": data.permissions,
+    }
+
+
+async def _compute_and_batch_updates(prisma_client, teams, permissions_to_add: set) -> int:
+    """Compute merged permissions and batch-write updates. Returns count of teams updated."""
+    updates = []
+    for team in teams:
+        existing = set(team.team_member_permissions or [])
+        if permissions_to_add <= existing:
+            continue
+        merged = sorted(existing | permissions_to_add)  # normalise to alphabetical order
+        updates.append((team.team_id, merged))
+
+    if updates:
+        batcher = prisma_client.db.batch_()
+        for team_id, merged_perms in updates:
+            batcher.litellm_teamtable.update(
+                where={"team_id": team_id},
+                data={"team_member_permissions": merged_perms},
+            )
+        await batcher.commit()
+
+    return len(updates)
+
+
+async def _append_permissions_to_specific_teams(
+    prisma_client, team_ids: List[str], permissions_to_add: set
+) -> int:
+    """Fetch specific teams by ID and append permissions."""
+    teams = await prisma_client.db.litellm_teamtable.find_many(
+        where={"team_id": {"in": team_ids}},
+    )
+
+    found_ids = {team.team_id for team in teams}
+    missing_ids = set(team_ids) - found_ids
+    if missing_ids:
+        raise HTTPException(
+            status_code=404,
+            detail={"error": f"Team(s) not found: {sorted(missing_ids)}"},
+        )
+
+    return await _compute_and_batch_updates(prisma_client, teams, permissions_to_add)
+
+
+async def _append_permissions_to_all_teams(
+    prisma_client, permissions_to_add: set
+) -> int:
+    """Paginated read + batched write across all teams."""
+    teams_updated = 0
+    cursor = None
+    BATCH_SIZE = 500
+
+    while True:
+        find_args: dict = {
+            "take": BATCH_SIZE,
+            "order": {"team_id": "asc"},
+        }
+        if cursor is not None:
+            find_args["cursor"] = {"team_id": cursor}
+            find_args["skip"] = 1
+
+        teams = await prisma_client.db.litellm_teamtable.find_many(**find_args)
+
+        if not teams:
+            break
+
+        teams_updated += await _compute_and_batch_updates(
+            prisma_client, teams, permissions_to_add
+        )
+
+        cursor = teams[-1].team_id
+
+        if len(teams) < BATCH_SIZE:
+            break
+
+    return teams_updated
+
+
 @router.get(
     "/team/daily/activity",
     response_model=SpendAnalyticsPaginatedResponse,
diff --git a/litellm/types/proxy/management_endpoints/team_endpoints.py b/litellm/types/proxy/management_endpoints/team_endpoints.py
index 2455eb495d1..b1dabf96e67 100644
--- a/litellm/types/proxy/management_endpoints/team_endpoints.py
+++ b/litellm/types/proxy/management_endpoints/team_endpoints.py
@@ -3,6 +3,7 @@
 from pydantic import BaseModel

 from litellm.proxy._types import (
+    KeyManagementRoutes,
     LiteLLM_DeletedTeamTable,
     LiteLLM_TeamMembership,
     LiteLLM_TeamTable,
@@ -43,6 +44,27 @@ class UpdateTeamMemberPermissionsRequest(BaseModel):
     team_member_permissions: List[str]


+class BulkUpdateTeamMemberPermissionsRequest(BaseModel):
+    """Request to bulk-update team member permissions across teams."""
+
+    permissions: List[KeyManagementRoutes]
+    """Permissions to append to the target teams (duplicates are skipped)."""
+
+    team_ids: Optional[List[str]] = None
+    """Specific team IDs to update. Required unless apply_to_all_teams is True."""
+
+    apply_to_all_teams: bool = False
+    """When True, update all teams. Mutually exclusive with team_ids."""
+
+
+class BulkUpdateTeamMemberPermissionsResponse(BaseModel):
+    """Response for bulk team member permissions update."""
+
+    message: str
+    teams_updated: int
+    permissions_appended: Optional[List[str]] = None
+
+
 class TeamListItem(LiteLLM_TeamTable):
     """A team item in the paginated list response, enriched with computed fields."""

PATCH

echo "Gold patch applied successfully."
