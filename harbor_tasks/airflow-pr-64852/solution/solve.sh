#!/bin/bash
# Gold solution for airflow-optional-theme-tokens
set -euo pipefail

cd /workspace/airflow

# Idempotency check - skip if already applied
if grep -q "tokens: dict\[Literal\[\"colors\"\], ThemeColors\] | None = None" airflow-core/src/airflow/api_fastapi/common/types.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# ============================================
# Fix 1: Update types.py - remove model_serializer from ThemeColors, make tokens optional
# ============================================

TYPES_FILE="airflow-core/src/airflow/api_fastapi/common/types.py"

# Remove the unused "Any" import since we're removing the model_serializer that used it
sed -i 's/from typing import Annotated, Any, Literal/from typing import Annotated, Literal/' "$TYPES_FILE"

# Remove the model_serializer method from ThemeColors (lines with @model_serializer and the serialize_model method)
# This is the 4-line block after the check_at_least_one_color validator
python3 << 'PYEOF'
import re

filepath = "airflow-core/src/airflow/api_fastapi/common/types.py"
with open(filepath, 'r') as f:
    content = f.read()

# Remove the model_serializer decorator and method from ThemeColors
# Pattern: the @model_serializer(mode="wrap") decorator and the def serialize_model method
pattern = r'''    @model_serializer\(mode="wrap"\)\n    def serialize_model\(self, handler: Any\) -> dict:\n        return \{k: v for k, v in handler\(self\)\.items\(\) if v is not None\}\n'''
content = re.sub(pattern, '', content)

# Make tokens field optional in Theme class
content = content.replace(
    'tokens: dict[Literal["colors"], ThemeColors]',
    'tokens: dict[Literal["colors"], ThemeColors] | None = None'
)

with open(filepath, 'w') as f:
    f.write(content)

print("types.py updated successfully")
PYEOF

# ============================================
# Fix 2: Update config.py - add field_serializer for theme
# ============================================

CONFIG_FILE="airflow-core/src/airflow/api_fastapi/core_api/datamodels/ui/config.py"

python3 << 'PYEOF'
filepath = "airflow-core/src/airflow/api_fastapi/core_api/datamodels/ui/config.py"
with open(filepath, 'r') as f:
    content = f.read()

# Add ConfigDict and field_serializer imports from pydantic
old_import = "from airflow.api_fastapi.common.types import Theme, UIAlert"
new_import = """from pydantic import ConfigDict, field_serializer

from airflow.api_fastapi.common.types import Theme, UIAlert"""
content = content.replace(old_import, new_import)

# Add model_config to ConfigResponse class
old_class = '''class ConfigResponse(BaseModel):
    """configuration serializer."""

    fallback_page_limit: int'''
new_class = '''class ConfigResponse(BaseModel):
    """configuration serializer."""

    model_config = ConfigDict(json_schema_mode_override="validation")

    fallback_page_limit: int'''
content = content.replace(old_class, new_class)

# Add field_serializer for theme at the end of the class
old_end = '''    theme: Theme | None
    multi_team: bool'''
new_end = '''    theme: Theme | None
    multi_team: bool

    @field_serializer("theme")
    def serialize_theme(self, theme: Theme | None) -> dict | None:
        if theme is None:
            return None
        return theme.model_dump(exclude_none=True)'''
content = content.replace(old_end, new_end)

with open(filepath, 'w') as f:
    f.write(content)

print("config.py updated successfully")
PYEOF

echo "Patch applied successfully"
