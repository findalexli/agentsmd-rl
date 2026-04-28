# MCP Database Tools Issues

## Background

The Superset MCP (Model Context Protocol) service provides database query tools alongside chart and dashboard tools. Users can filter databases by columns such as `database_name`, `expose_in_sqllab`, `allow_file_upload`, `created_by_fk`, and `changed_by_fk`. The app instructions mention `list_databases` and include a `My databases` section with `created_by_fk` filtering examples.

## Issues

### 1. Timestamps are timezone-naive

`DatabaseError.create()` produces naive timestamps lacking timezone information. Additionally, `_humanize_timestamp()` raises a TypeError when passed a timezone-aware datetime because the subtraction `datetime.now() - dt` mixes aware and naive operands. The expected behavior is that timestamps carry UTC timezone info, and the humanize function produces strings like "2 hours ago" for both naive and timezone-aware datetime inputs.

### 2. Test helper missing type annotations

The `create_mock_database()` function in the database tool test file defines parameters without Python type annotations. Parameters such as `database_id` and `database_name` should use standard Python 3.10+ annotation syntax.

### 3. Docstring omits database model type

A docstring in `mcp_core.py` that enumerates supported model types lists chart, dataset, and dashboard but does not include `database`, even though database querying is a supported operation.

## Code Style Requirements

All Python code must pass `ruff` linting without errors. Run `ruff check` on changed files before submitting.

## Reference

For the timezone handling patterns, look at how other MCP modules handle datetime serialization. The chart and dashboard schemas demonstrate the expected Python 3.10+ style for type annotations.
