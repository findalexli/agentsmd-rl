#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'is_legacy_insight_filters_blocked' posthog/api/insight.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/posthog/api/insight.py b/posthog/api/insight.py
index 05f2d22dbcf4..fb3a2b10408a 100644
--- a/posthog/api/insight.py
+++ b/posthog/api/insight.py
@@ -121,6 +121,7 @@
 logger = structlog.get_logger(__name__)

 LEGACY_INSIGHT_ENDPOINTS_BLOCKED_FLAG = "legacy-insight-endpoints-disabled"
+LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG = "legacy-insight-filters-disabled"


 EXPORT_QUERY_CACHE_MISS = Counter(
@@ -203,6 +204,26 @@ def is_legacy_insight_endpoint_blocked(user: Any, team: Team) -> bool:
     )


+def is_legacy_insight_filters_blocked(user: Any, team: Team) -> bool:
+    distinct_id = getattr(user, "distinct_id", None)
+    if not distinct_id:
+        return False
+
+    return posthoganalytics.feature_enabled(
+        LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG,
+        str(distinct_id),
+        groups={
+            "organization": str(team.organization_id),
+            "project": str(team.id),
+        },
+        group_properties={
+            "organization": {"id": str(team.organization_id)},
+            "project": {"id": str(team.id)},
+        },
+        send_feature_flag_events=False,
+    )
+
+
 def capture_legacy_api_call(request: request.Request, team: Team) -> None:
     if is_legacy_insight_endpoint_blocked(request.user, team):
         raise PermissionDenied("Legacy insight endpoints are not available for this user.")
@@ -464,6 +485,15 @@ class Meta:
             "is_cached",
         )

+    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
+        query = attrs.get("query") if "query" in attrs else None
+        using_legacy_filters = "filters" in attrs and attrs.get("filters") is not None and query in (None, {})
+        if using_legacy_filters and is_legacy_insight_filters_blocked(
+            self.context["request"].user, self.context["get_team"]()
+        ):
+            raise PermissionDenied("Creating or updating insights with legacy filters is not available for this user.")
+        return super().validate(attrs)
+
     @monitor(feature=Feature.INSIGHT, endpoint="insight", method="POST")
     def create(self, validated_data: dict, *args: Any, **kwargs: Any) -> Insight:
         request = self.context["request"]
diff --git a/posthog/api/test/test_insight.py b/posthog/api/test/test_insight.py
index 7377558759cb..bcaa0d169808 100644
--- a/posthog/api/test/test_insight.py
+++ b/posthog/api/test/test_insight.py
@@ -97,6 +97,39 @@ def test_legacy_insight_endpoints_blocked_with_feature_flag(self, _name: str, pa
         ]
         self.assertEqual(len(legacy_calls), 1)

+    def test_creating_legacy_filter_insight_blocked_with_feature_flag(self) -> None:
+        with patch("posthog.api.insight.posthoganalytics.feature_enabled", return_value=True) as mock_feature_enabled:
+            response = self.client.post(
+                f"/api/projects/{self.team.id}/insights/",
+                {"name": "Legacy filter insight", "filters": {"insight": "TRENDS", "events": [{"id": "$pageview"}]}},
+            )
+
+        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
+        self.assertEqual(
+            response.json()["detail"],
+            "Creating or updating insights with legacy filters is not available for this user.",
+        )
+        legacy_filter_calls = [
+            c for c in mock_feature_enabled.call_args_list if c[0][0] == "legacy-insight-filters-disabled"
+        ]
+        self.assertEqual(len(legacy_filter_calls), 1)
+
+    def test_creating_query_insight_not_blocked_by_legacy_filter_flag(self) -> None:
+        with patch("posthog.api.insight.posthoganalytics.feature_enabled", return_value=True) as mock_feature_enabled:
+            response = self.client.post(
+                f"/api/projects/{self.team.id}/insights/",
+                {
+                    "name": "Query insight",
+                    "query": InsightVizNode(source=TrendsQuery(series=[EventsNode(event="$pageview")])).model_dump(),
+                },
+            )
+
+        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
+        legacy_filter_calls = [
+            c for c in mock_feature_enabled.call_args_list if c[0][0] == "legacy-insight-filters-disabled"
+        ]
+        self.assertEqual(len(legacy_filter_calls), 0)
+
     def test_get_insight_items(self) -> None:
         filter_dict = {
             "events": [{"id": "$pageview"}],

PATCH

echo "Patch applied successfully."
