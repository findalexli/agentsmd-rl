#!/bin/bash
set -e

cd /workspace/superset

# Fix 1: DatabaseError.create - add timezone.utc at top-level only (not inside method)
sed -i 's/from datetime import datetime/from datetime import datetime, timezone/' superset/mcp_service/database/schemas.py
sed -i 's/datetime.now())/datetime.now(timezone.utc))/' superset/mcp_service/database/schemas.py

# Fix 2: _humanize_timestamp - handle timezone-aware datetimes
# Use a Python script for this more complex replacement
python3 << 'PYEOF'
import re

with open('superset/mcp_service/database/schemas.py', 'r') as f:
    content = f.read()

# Replace the _humanize_timestamp function
old_code = 'def _humanize_timestamp(dt: datetime | None) -> str | None:\n    """Convert a datetime to a humanized string like \'2 hours ago\'."""\n    if dt is None:\n        return None\n    return humanize.naturaltime(datetime.now() - dt)'

new_code = 'def _humanize_timestamp(dt: datetime | None) -> str | None:\n    """Convert a datetime to a humanized string like \'2 hours ago\'."""\n    if dt is None:\n        return None\n    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()\n    return humanize.naturaltime(now - dt)'

content = content.replace(old_code, new_code)

# Fix: Remove the redundant timezone import inside create() method if it exists
# (since we already added it at top-level)
content = re.sub(
    r'(    def create\(cls, error: str, error_type: str\) -> "DatabaseError":)'
    r'(\n        """Create a standardized DatabaseError with timestamp.""")'
    r'(\n        from datetime import datetime, timezone\n)',
    r'\1\2\n        from datetime import datetime\n',
    content
)

# Also fix the line length issue - break the long line
content = content.replace(
    'return cls(error=error, error_type=error_type, timestamp=datetime.now(timezone.utc))',
    'return cls(\n            error=error,\n            error_type=error_type,\n            timestamp=datetime.now(timezone.utc),\n        )'
)

with open('superset/mcp_service/database/schemas.py', 'w') as f:
    f.write(content)

print("_humanize_timestamp fixed")
print("DatabaseError.create timezone handling fixed")
PYEOF

# Fix 3: mcp_core.py docstring - add database to model_type description
sed -i 's/(chart, dataset, dashboard)/(chart, dataset, dashboard, database)/' superset/mcp_service/mcp_core.py

# Fix 4: test file - add type annotations to create_mock_database
# Fix the parameter type hints
sed -i 's/database_id=1,/database_id: int = 1,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/database_name="examples",/database_name: str = "examples",/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/backend="postgresql",/backend: str = "postgresql",/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/expose_in_sqllab=True,/expose_in_sqllab: bool = True,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/allow_ctas=False,/allow_ctas: bool = False,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/allow_cvas=False,/allow_cvas: bool = False,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/allow_dml=False,/allow_dml: bool = False,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/allow_file_upload=False,/allow_file_upload: bool = False,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py
sed -i 's/allow_run_async=False,/allow_run_async: bool = False,/' tests/unit_tests/mcp_service/database/tool/test_database_tools.py

# Fix the return type annotation - use Python to properly handle the replacement
python3 << 'PYEOF'
import re

with open('tests/unit_tests/mcp_service/database/tool/test_database_tools.py', 'r') as f:
    content = f.read()

# Fix the create_mock_database function signature
# Replace the closing ): with proper return type annotation
old_sig = '''def create_mock_database(
    database_id: int = 1,
    database_name: str = "examples",
    backend: str = "postgresql",
    expose_in_sqllab: bool = True,
    allow_ctas: bool = False,
    allow_cvas: bool = False,
    allow_dml: bool = False,
    allow_file_upload: bool = False,
    allow_run_async: bool = False,
):'''

new_sig = '''def create_mock_database(
    database_id: int = 1,
    database_name: str = "examples",
    backend: str = "postgresql",
    expose_in_sqllab: bool = True,
    allow_ctas: bool = False,
    allow_cvas: bool = False,
    allow_dml: bool = False,
    allow_file_upload: bool = False,
    allow_run_async: bool = False,
) -> MagicMock:'''

content = content.replace(old_sig, new_sig)

# Also remove any erroneous -> MagicMock: that was added to test functions
# by the old buggy sed command
content = re.sub(
    r'(@pytest\.mark\.asyncio\nasync def test_get_database_info_not_found\(mock_find, mcp_server\)): -> MagicMock:',
    r'\1:',
    content
)

with open('tests/unit_tests/mcp_service/database/tool/test_database_tools.py', 'w') as f:
    f.write(content)

print("Type annotations fixed")
PYEOF

echo "All fixes applied successfully!"
