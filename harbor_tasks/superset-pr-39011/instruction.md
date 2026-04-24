# MCP Dashboard Creation Defaults to Published State

## Problem

When creating dashboards through the MCP (Model Context Protocol) service, dashboards are immediately published upon creation. This is inconsistent with the manual dashboard creation flow, where newly created dashboards start in an unpublished state and must be explicitly published.

## Expected Behavior

MCP-created dashboards should behave consistently with manually created ones — they should not be published immediately upon creation. The option to publish immediately should still be available for users who want it.

## Context

The MCP service's dashboard functionality is located in the `superset/mcp_service/dashboard/` directory. Investigate how the dashboard generation request is defined and what assumptions it makes about the initial publication state.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
