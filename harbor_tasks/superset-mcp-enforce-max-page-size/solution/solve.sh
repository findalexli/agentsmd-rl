#!/bin/bash
set -e

cd /workspace/superset

# Check if already patched (idempotency check)
if grep -q "MAX_PAGE_SIZE = 100" superset/mcp_service/constants.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

echo "Applying constants.py changes..."
python3 << 'PYEOF'
with open('superset/mcp_service/constants.py', 'r') as f:
    content = f.read()

pagination_constants = '''# Pagination defaults
DEFAULT_PAGE_SIZE = 10  # Default number of items per page
MAX_PAGE_SIZE = 100  # Maximum allowed page_size to prevent oversized responses
'''

if 'MAX_PAGE_SIZE' not in content:
    content = content.replace(
        '"""Constants for the MCP service."""\n\n#',
        '"""Constants for the MCP service."""\n\n' + pagination_constants + '#'
    )

with open('superset/mcp_service/constants.py', 'w') as f:
    f.write(content)
print("constants.py updated")
PYEOF

echo "Applying chart/schemas.py changes..."
python3 << 'PYEOF'
import re

with open('superset/mcp_service/chart/schemas.py', 'r') as f:
    content = f.read()

import_line = 'from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE'
if import_line not in content:
    content = content.replace(
        'from superset.mcp_service.common.error_schemas import ChartGenerationError\n',
        'from superset.mcp_service.common.error_schemas import ChartGenerationError\n' + import_line + '\n'
    )

# More flexible pattern matching for page_size field
old_patterns = [
    r'page_size:\s*Annotated\[\s*PositiveInt,\s*Field\(default=10,\s*description="Number of items per page"\)\s*\]',
    r'page_size:\s*Annotated\[\s*PositiveInt,\s*Field\(default=10,\s*description="Number of items per page"\)\]',
]

new_field = '''page_size: Annotated[
        int,
        Field(
            default=DEFAULT_PAGE_SIZE,
            gt=0,
            le=MAX_PAGE_SIZE,
            description=f"Number of items per page (max {MAX_PAGE_SIZE})",
        ),
    ]'''

for pattern in old_patterns:
    if re.search(pattern, content):
        content = re.sub(pattern, new_field, content)
        break

with open('superset/mcp_service/chart/schemas.py', 'w') as f:
    f.write(content)
print("chart/schemas.py updated")
PYEOF

echo "Applying dashboard/schemas.py changes..."
python3 << 'PYEOF'
import re

with open('superset/mcp_service/dashboard/schemas.py', 'r') as f:
    content = f.read()

import_line = 'from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE'
if import_line not in content:
    content = content.replace(
        'from superset.mcp_service.common.cache_schemas import MetadataCacheControl\n',
        'from superset.mcp_service.common.cache_schemas import MetadataCacheControl\n' + import_line + '\n'
    )

old_patterns = [
    r'page_size:\s*Annotated\[\s*PositiveInt,\s*Field\(default=10,\s*description="Number of items per page"\)\s*\]',
    r'page_size:\s*Annotated\[\s*PositiveInt,\s*Field\(default=10,\s*description="Number of items per page"\)\]',
]

new_field = '''page_size: Annotated[
        int,
        Field(
            default=DEFAULT_PAGE_SIZE,
            gt=0,
            le=MAX_PAGE_SIZE,
            description=f"Number of items per page (max {MAX_PAGE_SIZE})",
        ),
    ]'''

for pattern in old_patterns:
    if re.search(pattern, content):
        content = re.sub(pattern, new_field, content)
        break

with open('superset/mcp_service/dashboard/schemas.py', 'w') as f:
    f.write(content)
print("dashboard/schemas.py updated")
PYEOF

echo "Applying dataset/schemas.py changes..."
python3 << 'PYEOF'
import re

with open('superset/mcp_service/dataset/schemas.py', 'r') as f:
    content = f.read()

# Add import after the cache_schemas import line
import_line = 'from superset.mcp_service.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE'
if import_line not in content:
    # The import comes after MetadataCacheControl import in dataset/schemas.py
    content = content.replace(
        'from superset.mcp_service.common.cache_schemas import MetadataCacheControl\nfrom superset.mcp_service.system.schemas import',
        'from superset.mcp_service.common.cache_schemas import MetadataCacheControl\n' + import_line + '\nfrom superset.mcp_service.system.schemas import'
    )

old_patterns = [
    r'page_size:\s*Annotated\[\s*PositiveInt,\s*Field\(default=10,\s*description="Number of items per page"\)\s*\]',
    r'page_size:\s*Annotated\[\s*PositiveInt,\s*Field\(default=10,\s*description="Number of items per page"\)\]',
]

new_field = '''page_size: Annotated[
        int,
        Field(
            default=DEFAULT_PAGE_SIZE,
            gt=0,
            le=MAX_PAGE_SIZE,
            description=f"Number of items per page (max {MAX_PAGE_SIZE})",
        ),
    ]'''

for pattern in old_patterns:
    if re.search(pattern, content):
        content = re.sub(pattern, new_field, content)
        break

with open('superset/mcp_service/dataset/schemas.py', 'w') as f:
    f.write(content)
print("dataset/schemas.py updated")
PYEOF

echo "Applying mcp_core.py changes..."
python3 << 'PYEOF'
with open('superset/mcp_service/mcp_core.py', 'r') as f:
    content = f.read()

# Find the ModelListCore.run_tool method and add clamping
# The method signature varies, so let's look for the common pattern

old_pattern1 = '''    def run_tool(
        self,
        filters: Any | None = None,
        search: str | None = None,
        select_columns: Any | None = None,
        order_column: str | None = None,
        order_direction: Literal["asc", "desc"] | None = "asc",
        page: int = 0,
        page_size: int = 10,
    ) -> L:
        # Parse filters using generic utility (accepts JSON string or object)'''

new_pattern1 = '''    def run_tool(
        self,
        filters: Any | None = None,
        search: str | None = None,
        select_columns: Any | None = None,
        order_column: str | None = None,
        order_direction: Literal["asc", "desc"] | None = "asc",
        page: int = 0,
        page_size: int = 10,
    ) -> L:
        from superset.mcp_service.constants import MAX_PAGE_SIZE

        # Clamp page_size to MAX_PAGE_SIZE as defense-in-depth
        page_size = min(page_size, MAX_PAGE_SIZE)

        # Parse filters using generic utility (accepts JSON string or object)'''

if "min(page_size, MAX_PAGE_SIZE)" not in content:
    if old_pattern1 in content:
        content = content.replace(old_pattern1, new_pattern1)
        print("Updated mcp_core.py (pattern 1)")
    else:
        print("WARNING: Could not find expected pattern in mcp_core.py")

with open('superset/mcp_service/mcp_core.py', 'w') as f:
    f.write(content)
print("mcp_core.py updated")
PYEOF

echo "Applying __main__.py changes..."
python3 << 'PYEOF'
with open('superset/mcp_service/__main__.py', 'r') as f:
    content = f.read()

middleware_func = '''\n\ndef _add_default_middlewares() -> None:
    """Add the standard middleware stack to the MCP instance.

    This ensures all entry points (stdio, streamable-http, etc.) get
    the same protection middlewares that the Flask CLI and server.py add.
    Order is innermost → outermost (last-added wraps everything).
    """
    from superset.mcp_service.middleware import (
        create_response_size_guard_middleware,
        GlobalErrorHandlerMiddleware,
        LoggingMiddleware,
        StructuredContentStripperMiddleware,
    )

    # Response size guard (innermost among these)
    if size_guard := create_response_size_guard_middleware():
        mcp.add_middleware(size_guard)
        limit = size_guard.token_limit
        sys.stderr.write(f"[MCP] Response size guard enabled (token_limit={limit})\\n")

    # Logging
    mcp.add_middleware(LoggingMiddleware())

    # Global error handler
    mcp.add_middleware(GlobalErrorHandlerMiddleware())

    # Structured content stripper (must be outermost)
    mcp.add_middleware(StructuredContentStripperMiddleware())

'''

if '_add_default_middlewares' not in content:
    content = content.replace(
        'from superset.mcp_service.app import init_fastmcp_server, mcp\n\n\ndef main',
        'from superset.mcp_service.app import init_fastmcp_server, mcp' + middleware_func + '\ndef main'
    )

    content = content.replace(
        'init_fastmcp_server()\n\n        # Log captured output',
        'init_fastmcp_server()\n            _add_default_middlewares()\n\n        # Log captured output'
    )

    content = content.replace(
        'init_fastmcp_server()\n\n        # Run with specified transport',
        'init_fastmcp_server()\n        _add_default_middlewares()\n\n        # Run with specified transport'
    )

with open('superset/mcp_service/__main__.py', 'w') as f:
    f.write(content)

print("__main__.py updated")
PYEOF

echo "Verifying changes..."
grep -q "MAX_PAGE_SIZE = 100" superset/mcp_service/constants.py && echo "✓ constants.py updated" || echo "✗ constants.py NOT updated"
grep -q "from superset.mcp_service.constants import" superset/mcp_service/chart/schemas.py && echo "✓ chart/schemas.py imports" || echo "✗ chart/schemas.py imports missing"
grep -q "le=MAX_PAGE_SIZE" superset/mcp_service/chart/schemas.py && echo "✓ chart/schemas.py le=MAX_PAGE_SIZE" || echo "✗ chart/schemas.py le=MAX_PAGE_SIZE missing"
grep -q "le=MAX_PAGE_SIZE" superset/mcp_service/dashboard/schemas.py && echo "✓ dashboard/schemas.py le=MAX_PAGE_SIZE" || echo "✗ dashboard/schemas.py le=MAX_PAGE_SIZE missing"
grep -q "le=MAX_PAGE_SIZE" superset/mcp_service/dataset/schemas.py && echo "✓ dataset/schemas.py le=MAX_PAGE_SIZE" || echo "✗ dataset/schemas.py le=MAX_PAGE_SIZE missing"
grep -q "min(page_size, MAX_PAGE_SIZE)" superset/mcp_service/mcp_core.py && echo "✓ mcp_core.py clamping" || echo "✗ mcp_core.py clamping missing"
grep -q "_add_default_middlewares" superset/mcp_service/__main__.py && echo "✓ __main__.py middleware" || echo "✗ __main__.py middleware missing"

echo "Patch applied!"
