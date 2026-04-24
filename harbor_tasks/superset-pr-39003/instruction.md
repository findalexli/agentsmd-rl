# Fix execute_sql Error Message Missing Limit Parameter Suggestion

When the `execute_sql` MCP tool returns a response that exceeds the token limit, the error message provides suggestions to reduce the response size. However, the suggestions are incomplete:

1. The error message suggests adding a SQL `LIMIT` clause, but does **not** mention the tool's own `limit` parameter which can cap rows returned
2. Even when a `limit` parameter is already specified, the message doesn't adapt its suggestions appropriately

## Current Behavior

When `execute_sql` returns too much data, users see a generic SQL LIMIT suggestion but no mention of the tool's `limit` parameter option.

## Expected Behavior

The error message should:
1. Suggest using the `limit` parameter (e.g., `limit=100`) to cap rows returned
2. Only suggest adding the `limit` parameter if one isn't already specified
3. Keep the SQL LIMIT clause suggestion for direct SQL modification

## Files to Investigate

- `superset/mcp_service/utils/token_utils.py` - Contains `generate_size_reduction_suggestions` and `_get_tool_specific_suggestions` functions that generate error messages

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
