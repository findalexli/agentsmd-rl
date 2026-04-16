# Deprecate Microagent Repository Endpoints

The microagents UI has been removed from OpenHands V1, but the API endpoints for accessing microagent data from repositories are still active and not marked as deprecated.

## Problem

Two API endpoints in `openhands/server/routes/git.py` do not show as deprecated when introspected:

1. `GET /repository/{repository_name:path}/microagents` - Returns a list of microagents from a repository
2. `GET /repository/{repository_name:path}/microagents/content` - Returns content of a specific microagent file

These endpoints should be marked as deprecated in the API documentation to signal to consumers that they will be removed in future versions.

## Task

Mark both endpoints as deprecated so they appear as deprecated when inspecting the FastAPI app or viewing the OpenAPI documentation.

The deprecation notice in each endpoint's docstring should use the Sphinx `.. deprecated::` directive format and include the following text:
- "The microagents UI has already been removed"
- "and is not supported in V1"

## Files to Modify

- `openhands/server/routes/git.py`

## Expected Outcome

When accessing the OpenAPI documentation or introspecting the FastAPI app, both endpoints should show as deprecated.