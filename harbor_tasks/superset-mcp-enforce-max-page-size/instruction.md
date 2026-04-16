# Enforce MAX_PAGE_SIZE on MCP List Tools

The MCP (Model Context Protocol) service in Apache Superset allows LLM clients to list resources like charts, dashboards, and datasets. Currently, there's no upper limit on the `page_size` parameter in list requests, which means clients can request excessively large pages (e.g., 10000 items). These oversized responses can overwhelm LLM context windows and cause service issues.

## Problem

When a client sends a request with a very large `page_size`, the server attempts to return that many items, potentially causing:
- Memory pressure on the server
- Response payloads too large for LLM context windows
- Poor user experience due to slow response times

## Files Involved

The relevant files are in `superset/mcp_service/`:
- `constants.py` - Define service-wide constants
- `chart/schemas.py` - Pydantic schemas for chart list requests
- `dashboard/schemas.py` - Pydantic schemas for dashboard list requests
- `dataset/schemas.py` - Pydantic schemas for dataset list requests
- `mcp_core.py` - Core classes including the list tool runner
- `__main__.py` - Entry point for the MCP service

## Expected Behavior

1. **Constants defined**: Two pagination constants should be defined in `constants.py`:
   - A maximum page size constant with value 100
   - A default page size constant with value 10

2. **Schema validation**: All three list request schemas (chart, dashboard, dataset) should:
   - Import the pagination constants from `constants.py`
   - Apply a `le` (less-than-or-equal) constraint on the `page_size` field using the maximum constant
   - Apply `gt=0` (greater-than-zero) constraint to ensure positive page sizes
   - Use the default constant as the field's default value

3. **Defense-in-depth**: The list tool runner should enforce an additional runtime check that caps `page_size` at the maximum even if schema validation is somehow bypassed

4. **Middleware**: The service entry point should include standard middleware (response size guard, logging, error handler, content stripper)

## Testing

The fix should be validated by tests that:
- Verify the pagination constants are properly defined with correct values
- Confirm oversized page sizes are rejected with validation errors
- Confirm valid page sizes are accepted
- Verify runtime page size capping exists in the list tool runner
- Check that middleware is properly configured
