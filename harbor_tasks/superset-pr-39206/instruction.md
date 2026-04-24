# Fix Null Fields in MCP Service Responses

## Problem

The MCP (Model Context Protocol) service has several bugs where fields are returned as `null` when they should have values:

1. **`list_datasets` returns null `database_name`**: When listing datasets through the MCP service, the `database_name` field is always null, even though datasets have associated database names. The root cause is that `DEFAULT_DATASET_COLUMNS` in `superset/mcp_service/dataset/tool/list_datasets.py` doesn't include the columns needed to load the database relationship.

2. **`save_sql_query` silently mishandles the `schema` field**: When saving a SQL query with a schema specified, the response serializes the field as `schema_name` instead of `schema`. Additionally, the request model doesn't accept `schema` as an input alias for `schema_name`.

## Files to Investigate

- `superset/mcp_service/dataset/tool/list_datasets.py` — Dataset listing tool, contains `DEFAULT_DATASET_COLUMNS`
- `superset/mcp_service/sql_lab/schemas.py` — Pydantic schemas for SQL Lab tools (`SaveSqlQueryRequest`, `SaveSqlQueryResponse`, `SqlLabResponse`)
- `superset/daos/base.py` — Base DAO class with the `list()` method

## Required Behavior

### DAO Base (`superset/daos/base.py`)

The `list()` method iterates over requested columns and checks whether each is a `ColumnProperty` or `RelationshipProperty`. However, it silently ignores Python `@property` descriptors, which means properties like `database_name` are never loaded.

The fix should:
- Introduce a boolean flag variable named `needs_full_model` that is set to `True` when a requested column is a Python `@property` or other descriptor (i.e., not a `ColumnProperty` or `RelationshipProperty`)
- Use this flag in the query construction: the condition `if relationship_loads or needs_full_model` should trigger full model loading
- Include a comment referencing `@property` or descriptors in the code

### SQL Lab Schemas (`superset/mcp_service/sql_lab/schemas.py`)

The schema field serialization needs two fixes:

**a) Schema field normalization:**

Create a `_SchemaFieldNormalizer` mixin class that:
- Inherits from Pydantic's `BaseModel`
- Uses a `@model_serializer` decorator (with `mode="wrap"`) to post-process the serialization output
- In the serializer method, renames the `schema_name` key to `schema` in the output dict

Both `SaveSqlQueryResponse` and `SqlLabResponse` should inherit from `_SchemaFieldNormalizer`.

**b) Populate by name:**

Both `SaveSqlQueryRequest` and `SaveSqlQueryResponse` need `populate_by_name=True` in their `model_config` (using Pydantic's `ConfigDict`). This allows the `schema` field alias on `schema_name` to work correctly for both input and output.

### Dataset Listing (`superset/mcp_service/dataset/tool/list_datasets.py`)

Add two entries to the `DEFAULT_DATASET_COLUMNS` list:
- `"database_name"` — the `@property` that returns the database's name
- `"database"` — triggers eager loading via joinedload, preventing N+1 lazy-load queries when the serializer accesses `dataset.database.name`

## Hints

- SQLAlchemy doesn't know about Python `@property` descriptors — they look like regular attributes on the model class but aren't `ColumnProperty` or `RelationshipProperty`
- Pydantic's `alias` parameter on `Field` controls the external (JSON) name, but `populate_by_name=True` is needed for the alias to work bidirectionally
- A `@model_serializer` with `mode="wrap"` lets you post-process the default serialization without replacing it entirely

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
