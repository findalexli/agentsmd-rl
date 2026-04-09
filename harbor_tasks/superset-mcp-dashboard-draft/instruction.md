# Fix MCP Dashboard Draft State Default

## Problem

When the MCP (Model Context Protocol) service creates a dashboard, the dashboard is being published by default. This is inconsistent with the manual dashboard creation flow, where newly created dashboards start in draft state.

The issue is in the dashboard generation schema: dashboards created through MCP should start as drafts (unpublished) unless explicitly requested otherwise.

## Affected Code

The relevant code is in:
- `superset/mcp_service/dashboard/schemas.py` - Specifically the `GenerateDashboardRequest` Pydantic model

Look at the `published` field definition in this model. The current behavior causes dashboards to be published immediately upon creation, which may expose incomplete work to users.

## Expected Behavior

1. When a dashboard is created via MCP without specifying the `published` parameter, it should default to draft state (unpublished)
2. When `published=True` is explicitly provided in the request, the dashboard should still be published
3. When `published=False` is explicitly provided, the dashboard should be created as a draft

## Task

Modify the `GenerateDashboardRequest` schema so that dashboards created through MCP default to draft state instead of being published by default.

## Context

- The MCP service is located in `superset/mcp_service/`
- The schema file uses Pydantic for validation
- Unit tests for the MCP dashboard generation exist and may need their assertions updated to reflect the new expected behavior

## Hints

- Look at the `published` field in `GenerateDashboardRequest` - this controls whether the dashboard is published on creation
- The `Field()` default parameter determines the behavior when the parameter is not provided
- Consider checking the unit tests in `tests/unit_tests/mcp_service/dashboard/tool/test_dashboard_generation.py` for context on how this is tested
