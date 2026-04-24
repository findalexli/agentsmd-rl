# Fix API token access for error tracking issue endpoints

## Problem

When accessing error tracking issue endpoints with a Personal API key or OAuth token that has the appropriate `error_tracking:read` or `error_tracking:write` scopes, the server returns:

```
This action does not support Personal API Key access
```

The following endpoints are affected:

**Read endpoints that should work with `error_tracking:read` scope:**
- `GET /api/environments/{team_id}/error_tracking/issues` (list issues)
- `GET /api/environments/{team_id}/error_tracking/issues/{id}` (retrieve issue)
- `GET /api/environments/{team_id}/error_tracking/issues/values` (get distinct values for a property)

**Write endpoints that should work with `error_tracking:write` scope:**
- `POST /api/environments/{team_id}/error_tracking/issues` (create issue)
- `PUT /api/environments/{team_id}/error_tracking/issues/{id}` (update issue)
- `PATCH /api/environments/{team_id}/error_tracking/issues/{id}` (partial update)
- `DELETE /api/environments/{team_id}/error_tracking/issues/{id}` (destroy)
- `POST /api/environments/{team_id}/error_tracking/issues/{id}/merge` (merge issues)
- `POST /api/environments/{team_id}/error_tracking/issues/{id}/split` (split issue)
- `POST /api/environments/{team_id}/error_tracking/issues/{id}/assign` (assign issue)
- `POST /api/environments/{team_id}/error_tracking/issues/{id}/cohort` (create cohort from issue)
- `POST /api/environments/{team_id}/error_tracking/issues/bulk` (bulk update issues)

These endpoints work correctly with session-based authentication (web UI), but return 403 when using Bearer tokens with the appropriate scopes.

## Expected Behavior

Personal API keys and OAuth tokens with the `error_tracking:read` scope should be able to access all read endpoints. Tokens with the `error_tracking:write` scope should be able to access all write endpoints.

When investigating this issue:
1. Find the ViewSet handling error tracking issue endpoints
2. Examine how it inherits scope-checking behavior from its parent classes
3. Identify why custom actions (like `merge`, `split`, `assign`, `cohort`, `bulk`, `values`) and standard DRF actions (`patch`, `destroy`) are not being validated against the proper scopes

The scope object for error tracking endpoints is `"error_tracking"`, and the available scopes are `error_tracking:read` and `error_tracking:write`.

## Required Scope Mappings

After the fix, the following actions must be accessible with their respective scopes:

**Read scope (`error_tracking:read`) must allow:**
- `list` - for listing issues
- `retrieve` - for retrieving a single issue  
- `values` - for getting distinct values for a property

**Write scope (`error_tracking:write`) must allow:**
- `create` - for creating issues
- `update` - for full updates
- `partial_update` - for PATCH updates
- `patch` - the DRF patch action
- `destroy` - for DELETE requests
- `merge` - for merging issues
- `split` - for splitting an issue
- `assign` - for assigning an issue
- `cohort` - for creating a cohort from an issue
- `bulk` - for bulk updates

Note that setting scope mappings overrides any defaults, so all actions requiring access must be explicitly included.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
