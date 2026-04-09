# Gate legacy filter-based insight writes behind a feature flag

## Problem

PostHog's Insights API currently has a gating mechanism (`is_legacy_insight_endpoint_blocked`) that blocks access to legacy insight *endpoints* when a feature flag is enabled.
However, there is no equivalent gate for legacy filter *payloads*.
Users can still create or update insights using the old `filters`-based format (without a `query` key) through the standard create/update endpoints, even when the organization should be blocked from legacy filter usage.

This means organizations being migrated away from legacy filters have no way to prevent new legacy-filter insights from being created via the API.

## Expected Behavior

When a new feature flag (`legacy-insight-filters-disabled`) is enabled for a user's organization/project:
- POST/PATCH requests to the insights API that contain legacy `filters` (with no `query`) should be rejected with a 403 Forbidden response.
- Requests that use the modern `query`-based format should continue to work normally, unaffected by the flag.

The gating logic should mirror the existing `is_legacy_insight_endpoint_blocked` pattern: check `posthoganalytics.feature_enabled` with org and project group targeting, and integrate into the serializer validation flow.

## Files to Look At

- `posthog/api/insight.py` — The Insight API serializer and viewset. Contains the existing `is_legacy_insight_endpoint_blocked` function and `InsightSerializer` class. The new gate should follow the same pattern.
