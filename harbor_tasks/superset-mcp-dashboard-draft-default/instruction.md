# Task: Fix MCP Dashboard Default State

## Problem

When dashboards are created through the MCP (Model Context Protocol) service, they are automatically published by default. This is inconsistent with the manual dashboard creation flow in Superset, where newly created dashboards start in draft state.

## What Needs to Change

In the MCP service dashboard schemas, the `GenerateDashboardRequest` class has a `published` field that currently defaults to `True`. This should be changed to default to `False` so that dashboards created via MCP start as drafts, matching the behavior of manual dashboard creation.

## Where to Look

- Look in the MCP service directory: `superset/mcp_service/dashboard/`
- The relevant file is `schemas.py`
- Find the `GenerateDashboardRequest` class and its `published` field

## Expected Behavior

After the fix:
- When `GenerateDashboardRequest` is instantiated without specifying `published`, the dashboard should be created in draft state (unpublished)
- Users can still explicitly set `published=True` if they want to create a published dashboard
- This aligns with how the Superset UI handles new dashboard creation

## Testing

The fix should result in:
1. The `published` field defaulting to `False` instead of `True`
2. The field description remaining accurate (it describes whether to publish the dashboard)
3. No other changes to the schema structure
