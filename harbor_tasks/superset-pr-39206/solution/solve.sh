#!/bin/bash
# solve.sh - Apply the fix for superset-mcp-null-fields task
set -euo pipefail

cd /workspace/superset

# Idempotency check - skip if already applied
if grep -q "needs_full_model" superset/daos/base.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# ============================================================================
# Fix 1: Update superset/daos/base.py to handle @property descriptors
# ============================================================================

python3 << 'PYEOF'
import re

with open("superset/daos/base.py", "r") as f:
    content = f.read()

# Add needs_full_model initialization
content = content.replace(
    "column_attrs = []\n        relationship_loads = []",
    "column_attrs = []\n        relationship_loads = []\n        needs_full_model = False"
)

# Replace the comment with an else clause
content = content.replace(
    '''            elif isinstance(prop, RelationshipProperty):
                relationship_loads.append(joinedload(attr))
            # Ignore properties and other non-queryable attributes''',
    '''            elif isinstance(prop, RelationshipProperty):
                relationship_loads.append(joinedload(attr))
            else:
                # Python @property or other descriptor — requires a full
                # model instance (Row objects don't support descriptors)
                needs_full_model = True'''
)

# Update the if condition - keep comment short to avoid E501
content = content.replace(
    "if relationship_loads:\n            # If any relationships are requested",
    "if relationship_loads or needs_full_model:\n            # Need full model for joins or @property"
)

with open("superset/daos/base.py", "w") as f:
    f.write(content)

print("Fixed superset/daos/base.py")
PYEOF

# ============================================================================
# Fix 2: Update superset/mcp_service/dataset/tool/list_datasets.py
# ============================================================================

python3 << 'PYEOF'
with open("superset/mcp_service/dataset/tool/list_datasets.py", "r") as f:
    content = f.read()

# Add database_name and database to DEFAULT_DATASET_COLUMNS
content = content.replace(
    '''DEFAULT_DATASET_COLUMNS = [
    "id",
    "table_name",
    "schema",
    "description",
    "certified_by",
    "certification_details",
    "changed_on",
    "changed_on_humanized",
]''',
    '''DEFAULT_DATASET_COLUMNS = [
    "id",
    "table_name",
    "schema",
    "description",
    "certified_by",
    "certification_details",
    "changed_on",
    "changed_on_humanized",
    "database_name",
    # "database" is included to enable eager loading via joinedload,
    # preventing N+1 lazy-load queries when serializer accesses dataset.database.name
    "database",
]'''
)

with open("superset/mcp_service/dataset/tool/list_datasets.py", "w") as f:
    f.write(content)

print("Fixed superset/mcp_service/dataset/tool/list_datasets.py")
PYEOF

# ============================================================================
# Fix 3: Update superset/mcp_service/sql_lab/schemas.py
# ============================================================================

python3 << 'PYEOF'
with open("superset/mcp_service/sql_lab/schemas.py", "r") as f:
    content = f.read()

# Update imports - split across lines to avoid E501 (line too long)
content = content.replace(
    'from typing import Any',
    'from typing import Any, Dict'
)

content = content.replace(
    'from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator',
    '''from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_serializer,
)'''
)

# Add _SchemaFieldNormalizer class after imports
normalizer_class = '''
class _SchemaFieldNormalizer(BaseModel):
    """Mixin that renames schema_name -> schema in JSON output.

    Ensures the JSON key is "schema" (not "schema_name") for MCP/API consistency.
    """

    @model_serializer(mode="wrap")
    def _normalize_schema_field(
        self, default_serializer: Any
    ) -> Dict[str, Any]:
        data = default_serializer(self)
        if "schema_name" in data:
            data["schema"] = data.pop("schema_name")
        return data


'''

# Insert the normalizer class before ExecuteSqlRequest
content = content.replace(
    '\nclass ExecuteSqlRequest(BaseModel):',
    normalizer_class + 'class ExecuteSqlRequest(BaseModel):'
)

# Add populate_by_name to SaveSqlQueryRequest
content = content.replace(
    '''class SaveSqlQueryRequest(BaseModel):
    """Request schema for saving a SQL query."""

    database_id: int = Field(''',
    '''class SaveSqlQueryRequest(BaseModel):
    """Request schema for saving a SQL query."""

    model_config = ConfigDict(populate_by_name=True)

    database_id: int = Field('''
)

# Change SaveSqlQueryResponse to inherit from _SchemaFieldNormalizer
content = content.replace(
    'class SaveSqlQueryResponse(BaseModel):',
    'class SaveSqlQueryResponse(_SchemaFieldNormalizer):'
)

# Add populate_by_name to SaveSqlQueryResponse and update field
old_response = '''class SaveSqlQueryResponse(_SchemaFieldNormalizer):
    """Response schema for a saved SQL query."""

    id: int = Field(..., description="Saved query ID")
    label: str = Field(..., description="Query name")
    sql: str = Field(..., description="SQL query text")
    database_id: int = Field(..., description="Database ID")
    schema_name: str | None = Field(None, description="Schema name", alias="schema")'''

new_response = '''class SaveSqlQueryResponse(_SchemaFieldNormalizer):
    """Response schema for a saved SQL query."""

    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(..., description="Saved query ID")
    label: str = Field(..., description="Query name")
    sql: str = Field(..., description="SQL query text")
    database_id: int = Field(..., description="Database ID")
    schema_name: str | None = Field(None, description="Schema name", alias="schema")'''

content = content.replace(old_response, new_response)

# Change SqlLabResponse to inherit from _SchemaFieldNormalizer
content = content.replace(
    'class SqlLabResponse(BaseModel):',
    'class SqlLabResponse(_SchemaFieldNormalizer):'
)

with open("superset/mcp_service/sql_lab/schemas.py", "w") as f:
    f.write(content)

print("Fixed superset/mcp_service/sql_lab/schemas.py")
PYEOF

echo "All fixes applied successfully."
