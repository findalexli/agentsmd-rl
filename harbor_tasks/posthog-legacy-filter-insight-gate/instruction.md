# Gate legacy filter-based insight writes behind a feature flag

## Problem

PostHog's Insights API currently blocks access to legacy insight *endpoints* when the feature flag `"legacy-insight-endpoints-disabled"` is enabled. However, there is no equivalent gate for legacy filter *payloads* sent to modern endpoints.

Users can still create or update insights using the old `filters`-based format (without a `query` key) through POST/PATCH requests to `/api/projects/{team_id}/insights/`. Organizations being migrated away from legacy filters need a way to prevent new legacy-filter insights from being created via these API endpoints.

When a user attempts to create or update an insight with legacy filters, and the feature flag `"legacy-insight-filters-disabled"` is enabled for their organization, the API should reject the request with HTTP 403 Forbidden and the exact error message:

> "Creating or updating insights with legacy filters is not available for this user."

## Requirements

### Feature Flag Integration

Use the feature flag string `"legacy-insight-filters-disabled"` to control access. When checking if this flag is enabled:
- Pass the user's `distinct_id` as a string
- Include `groups` with `"organization"` and `"project"` keys mapped to the team's organization ID and team ID (both as strings)
- Include `group_properties` with nested structures containing the organization and project IDs
- Disable feature flag event tracking by setting `send_feature_flag_events=False`

If the user has no `distinct_id` or it is falsy (None, empty string), the flag check should return `False` (allowing the request).

### Legacy Filter Detection

A request should be treated as using "legacy filters" when ALL of the following are true:
1. The request contains a `"filters"` key with a non-None value
2. The request either lacks a `"query"` key entirely, OR the `"query"` value is `None`, OR the `"query"` value is an empty dict `{}`

Modern query-based requests (those with a non-empty `"query"` value) must continue to work normally, regardless of the feature flag state.

### Implementation Location

The insight API already contains similar feature flag gating logic for endpoints. Look for existing patterns involving `is_legacy_insight_endpoint_blocked` and `posthoganalytics.feature_enabled` to understand how to integrate the new filter-based gating. The validation for insight creation and update happens in the serializer layer.

### Code Quality Requirements

- All new functions must have Python type hints (mypy-strict style) for parameters and return types
- Code must pass ruff lint and format checks
- The validation must properly delegate to parent validation logic for non-blocked requests

## Expected Behavior Summary

| Scenario | Feature Flag State | Expected Result |
|----------|-------------------|-----------------|
| Legacy filters payload (filters present, query empty/absent) | Enabled | HTTP 403 with message "Creating or updating insights with legacy filters is not available for this user." |
| Legacy filters payload | Disabled | Normal processing (HTTP 201/200) |
| Query-based payload | Any | Normal processing (HTTP 201/200) |
| No distinct_id | Any | Normal processing (user bypasses check) |
