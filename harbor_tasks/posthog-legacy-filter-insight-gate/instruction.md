# Gate legacy filter-based insight writes behind a feature flag

## Problem

PostHog's Insights API currently blocks access to legacy insight *endpoints* when the feature flag `"legacy-insight-endpoints-disabled"` is enabled. However, there is no equivalent gate for legacy filter *payloads* sent to the modern endpoints.

Users can still create or update insights using the old `filters`-based format (without a `query` key) through the standard POST/PATCH endpoints at `/api/projects/{team_id}/insights/`. This means organizations being migrated away from legacy filters have no way to prevent new legacy-filter insights from being created via the API.

## Expected Behavior

When the feature flag `"legacy-insight-filters-disabled"` is enabled for a user's organization/project:
- POST/PATCH requests to `/api/projects/{team_id}/insights/` that contain legacy `filters` (with no `query` or an empty `query`) must be rejected with HTTP 403 Forbidden
- The error message must be exactly: `"Creating or updating insights with legacy filters is not available for this user."`
- Requests that use the modern `query`-based format must continue to work normally (HTTP 201/200), unaffected by the flag

## Required Implementation in `posthog/api/insight.py`

### 1. Feature Flag Constant

Define a module-level constant named `LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG` with the exact string value `"legacy-insight-filters-disabled"`.

### 2. Blocking Function

Create a function named `is_legacy_insight_filters_blocked(user: Any, team: Team) -> bool` that:
- Returns `False` immediately if the user has no `distinct_id` attribute or if `distinct_id` is falsy (None, empty string)
- Calls `posthoganalytics.feature_enabled()` with these exact parameters when the user has a valid `distinct_id`:
  - First argument: the flag string `"legacy-insight-filters-disabled"`
  - Second argument: user's `distinct_id` converted to string via `str(distinct_id)`
  - `groups` keyword argument: `{"organization": str(team.organization_id), "project": str(team.id)}`
  - `group_properties` keyword argument: `{"organization": {"id": str(team.organization_id)}, "project": {"id": str(team.id)}}`
  - `send_feature_flag_events=False`
- Returns the boolean result returned by `feature_enabled()`
- Uses Python type hints for both parameters and return type

### 3. Serializer Validation

In the `InsightSerializer` class, implement a `validate` method that:
- Accepts `attrs: dict[str, Any]` and returns `dict[str, Any]`
- Detects legacy filter payloads by checking:
  - `"filters"` key exists in `attrs` AND has a non-None value
  - `"query"` key is either absent from `attrs`, or has value `None`, or has value `{}`
- When both conditions indicate legacy filters are being used AND `is_legacy_insight_filters_blocked(self.context["request"].user, self.context["get_team"]())` returns `True`:
  - Raise `PermissionDenied` with the exact message: `"Creating or updating insights with legacy filters is not available for this user."`
- For all non-blocked requests, delegate to `super().validate(attrs)` and return its result

## Reference

- `posthog/api/insight.py` — Contains `InsightSerializer` class and the existing `is_legacy_insight_endpoint_blocked` pattern to mirror
