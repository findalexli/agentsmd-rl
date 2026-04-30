#!/usr/bin/env bash
set -euo pipefail

cd /workspace/litellm

# Idempotency: bail out if the patch has already been applied.
if grep -q "_batch_resolve_access_group_resources" litellm/proxy/management_endpoints/team_endpoints.py 2>/dev/null; then
    echo "Gold patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/litellm/proxy/_types.py b/litellm/proxy/_types.py
index 8faf36df4c6..6b581957e91 100644
--- a/litellm/proxy/_types.py
+++ b/litellm/proxy/_types.py
@@ -3805,6 +3805,10 @@ class OrganizationMemberUpdateResponse(MemberUpdateResponse):

 class TeamInfoResponseObjectTeamTable(LiteLLM_TeamTable):
     team_member_budget_table: Optional[LiteLLM_BudgetTable] = None
+    # Resources inherited from access groups (separate from direct assignments)
+    access_group_models: Optional[List[str]] = None
+    access_group_mcp_server_ids: Optional[List[str]] = None
+    access_group_agent_ids: Optional[List[str]] = None


 class TeamInfoResponseObject(TypedDict):
diff --git a/litellm/proxy/management_endpoints/team_endpoints.py b/litellm/proxy/management_endpoints/team_endpoints.py
index 3643373be65..ae89f09bb44 100644
--- a/litellm/proxy/management_endpoints/team_endpoints.py
+++ b/litellm/proxy/management_endpoints/team_endpoints.py
@@ -3042,6 +3042,19 @@ async def team_info(
                 team_info_response_object=_team_info,
             )

+        # Resolve resources inherited from access groups
+        if _team_info.access_group_ids:
+            ag_lookup = await _batch_resolve_access_group_resources(_team_info.access_group_ids)
+            models, mcp_ids, agent_ids = set(), set(), set()
+            for ag_id in _team_info.access_group_ids:
+                if ag_id in ag_lookup:
+                    models.update(ag_lookup[ag_id]["models"])
+                    mcp_ids.update(ag_lookup[ag_id]["mcp_server_ids"])
+                    agent_ids.update(ag_lookup[ag_id]["agent_ids"])
+            _team_info.access_group_models = list(models)
+            _team_info.access_group_mcp_server_ids = list(mcp_ids)
+            _team_info.access_group_agent_ids = list(agent_ids)
+
         response_object = TeamInfoResponseObject(
             team_id=team_id,
             team_info=_team_info,
@@ -3332,6 +3345,36 @@ async def _build_team_list_where_conditions(
     return where_conditions


+async def _batch_resolve_access_group_resources(
+    all_access_group_ids: List[str],
+) -> Dict[str, Dict[str, List[str]]]:
+    """
+    Batch-fetch access groups in a single DB query and return a per-group
+    resource map.
+
+    Returns {ag_id: {"models": [...], "mcp_server_ids": [...], "agent_ids": [...]}}.
+    Missing/invalid groups are silently omitted.
+    """
+    from litellm.proxy.proxy_server import prisma_client as _prisma_client
+
+    if not all_access_group_ids or _prisma_client is None:
+        return {}
+
+    unique_ids = list(set(all_access_group_ids))
+    rows = await _prisma_client.db.litellm_accessgrouptable.find_many(
+        where={"access_group_id": {"in": unique_ids}},
+    )
+
+    result: Dict[str, Dict[str, List[str]]] = {}
+    for row in rows:
+        result[row.access_group_id] = {
+            "models": list(row.access_model_names or []),
+            "mcp_server_ids": list(row.access_mcp_server_ids or []),
+            "agent_ids": list(row.access_agent_ids or []),
+        }
+    return result
+
+
 def _convert_teams_to_response_models(
     teams: list,
     use_deleted_table: bool,
@@ -3558,6 +3601,30 @@ async def list_team_v2(
     # Convert Prisma models to response models with members_count
     team_list = _convert_teams_to_response_models(teams, use_deleted_table)

+    # Resolve resources inherited from access groups (single batch query)
+    if not use_deleted_table:
+        team_items_with_ag = [
+            t for t in team_list
+            if isinstance(t, TeamListItem) and t.access_group_ids
+        ]
+        if team_items_with_ag:
+            all_ag_ids = [
+                ag_id
+                for t in team_items_with_ag
+                for ag_id in (t.access_group_ids or [])
+            ]
+            ag_lookup = await _batch_resolve_access_group_resources(all_ag_ids)
+            for team_item in team_items_with_ag:
+                models, mcp_ids, agent_ids = set(), set(), set()
+                for ag_id in (team_item.access_group_ids or []):
+                    if ag_id in ag_lookup:
+                        models.update(ag_lookup[ag_id]["models"])
+                        mcp_ids.update(ag_lookup[ag_id]["mcp_server_ids"])
+                        agent_ids.update(ag_lookup[ag_id]["agent_ids"])
+                team_item.access_group_models = list(models)
+                team_item.access_group_mcp_server_ids = list(mcp_ids)
+                team_item.access_group_agent_ids = list(agent_ids)
+
     return {
         "teams": team_list,
         "total": total_count,
diff --git a/litellm/types/proxy/management_endpoints/team_endpoints.py b/litellm/types/proxy/management_endpoints/team_endpoints.py
index 5055a65783f..2455eb495d1 100644
--- a/litellm/types/proxy/management_endpoints/team_endpoints.py
+++ b/litellm/types/proxy/management_endpoints/team_endpoints.py
@@ -47,6 +47,10 @@ class TeamListItem(LiteLLM_TeamTable):
     """A team item in the paginated list response, enriched with computed fields."""

     members_count: int = 0
+    # Resources inherited from access groups (separate from direct assignments)
+    access_group_models: Optional[List[str]] = None
+    access_group_mcp_server_ids: Optional[List[str]] = None
+    access_group_agent_ids: Optional[List[str]] = None


 class TeamListResponse(BaseModel):
PATCH

echo "Gold patch applied."
