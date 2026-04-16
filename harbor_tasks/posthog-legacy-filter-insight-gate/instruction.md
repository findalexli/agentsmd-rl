# Gate legacy filter-based insight writes behind a feature flag

## Problem

PostHog's Insights API currently allows users to create or update insights using the old `filters`-based format (without a `query` key) through POST/PATCH requests to `/api/projects/{team_id}/insights/`. Organizations being migrated away from legacy filters need a way to prevent new legacy-filter insights from being created via these API endpoints.

When a user attempts to create or update an insight with legacy filters, and the feature flag is enabled for their organization, the API should reject the request with HTTP 403 Forbidden and the exact error message:

> "Creating or updating insights with legacy filters is not available for this user."

## Requirements

### Feature Flag Integration

The implementation must use a module-level constant named `LEGACY_INSIGHT_FILTERS_BLOCKED_FLAG` with the value `"legacy-insight-filters-disabled"`.

Create a top-level function in `posthog/api/insight.py` named `is_legacy_insight_filters_blocked(user, team)` that:
- Returns `False` when the user has no `distinct_id` attribute, or when `distinct_id` is `None`, or when `distinct_id` is an empty string
- When the user has a valid `distinct_id`, calls `posthoganalytics.feature_enabled()` with:
  - The flag name passed as the first positional argument
  - The user's `distinct_id` passed as the second positional argument (converted to string)
  - `groups` keyword argument containing `"organization"` and `"project"` keys mapped to the team's organization ID and team ID (both as strings)
  - `group_properties` keyword argument containing nested structures with the organization and project IDs
  - `send_feature_flag_events=False` to disable feature flag event tracking
- Returns whatever `posthoganalytics.feature_enabled()` returns (True when the flag is enabled for the user, False otherwise)

The function must use Python type hints (mypy-strict style) for parameters and return types.

### Legacy Filter Detection

A request should be treated as using "legacy filters" when ALL of the following are true:
1. The request contains a `"filters"` key with a non-None value
2. The request either lacks a `"query"` key entirely, OR the `"query"` value is `None`, OR the `"query"` value is an empty dict `{}`

Modern query-based requests (those with a non-empty `"query"` value) must continue to work normally, regardless of the feature flag state.

### Serializer Validation

The `InsightSerializer` class in `posthog/api/insight.py` must implement a `validate(attrs)` method that:
1. Detects when the incoming `attrs` represent a legacy filter payload (using the criteria above)
2. Calls `is_legacy_insight_filters_blocked()` with the request user and team
3. When the flag is enabled and the payload uses legacy filters, raises `PermissionDenied` with the exact message: "Creating or updating insights with legacy filters is not available for this user."
4. For non-blocked requests, delegates to the parent validation by calling `super().validate(attrs)`

### Code Quality Requirements

- All new functions must have Python type hints (mypy-strict style) for parameters and return types
- Code must pass ruff lint and format checks

## Expected Behavior Summary

| Scenario | Feature Flag State | Expected Result |
|----------|-------------------|-----------------|
| Legacy filters payload (filters present, query empty/absent) | Enabled | HTTP 403 with message "Creating or updating insights with legacy filters is not available for this user." |
| Legacy filters payload | Disabled | Normal processing (HTTP 201/200) |
| Query-based payload | Any | Normal processing (HTTP 201/200) |
| No distinct_id | Any | Normal processing (user bypasses check) |
