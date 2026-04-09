# Fix missing token scope mappings for error tracking issue actions

## Problem

The error tracking issue endpoints have several custom actions — `merge`, `split`, `assign`, `cohort`, `bulk`, and `values` — that work fine with session-authenticated web flows. However, when accessing these same endpoints using a Personal API key or OAuth token with the appropriate `error_tracking:read` or `error_tracking:write` scopes, the server returns:

```
This action does not support Personal API Key access
```

For example, calling `GET /api/environments/{team_id}/error_tracking/issues/values?key=name&value=Type` with a `Bearer` token that has `error_tracking:read` scope fails with a 403 even though the user should have read access.

Similarly, `POST /api/environments/{team_id}/error_tracking/issues/{id}/merge` with an `error_tracking:write` scoped token also returns 403.

## Expected Behavior

Personal API keys and OAuth tokens with the correct error tracking scopes should be able to access all error tracking issue endpoints, including custom actions — not just the standard CRUD operations.

## Files to Look At

- `products/error_tracking/backend/api/issues.py` — The `ErrorTrackingIssueViewSet` that handles all error tracking issue API endpoints. The custom actions are defined here but token scope mappings are incomplete.
- `posthog/api/routing.py` — Contains `TeamAndOrgViewSetMixin` which provides the scope-checking infrastructure that ViewSets hook into.
