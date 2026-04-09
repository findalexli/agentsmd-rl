#!/bin/bash
set -e

cd /workspace/ClickHouse
TARGET_FILE="src/Interpreters/InterpreterDropQuery.cpp"

# Check if patch is already applied (idempotency)
if grep -q "Don't ignore DROP for refreshable materialized views" "$TARGET_FILE"; then
    echo "Patch already applied"
    exit 0
fi

# Apply the patch using Python
python3 << 'PYTHON_SCRIPT'
import re

with open("src/Interpreters/InterpreterDropQuery.cpp", "r") as f:
    content = f.read()

# Check if already patched
if "Don't ignore DROP for refreshable materialized views" in content:
    print("Patch already applied")
    exit(0)

# Find and replace the specific pattern
# The original code:
#         bool secondary_query = getContext()->getClientInfo().query_kind == ClientInfo::QueryKind::SECONDARY_QUERY;
#         if (!secondary_query && settings[Setting::ignore_drop_queries_probability] != 0 && ast_drop_query.kind == ASTDropQuery::Kind::Drop

old_lines = """        bool secondary_query = getContext()->getClientInfo().query_kind == ClientInfo::QueryKind::SECONDARY_QUERY;
        if (!secondary_query && settings[Setting::ignore_drop_queries_probability] != 0 && ast_drop_query.kind == ASTDropQuery::Kind::Drop"""

new_lines = """        bool secondary_query = getContext()->getClientInfo().query_kind == ClientInfo::QueryKind::SECONDARY_QUERY;

        /// Don't ignore DROP for refreshable materialized views: TRUNCATE doesn't stop
        /// the periodic refresh task, so the orphaned view would keep refreshing indefinitely,
        /// consuming background pool threads and potentially overwhelming the server.
        auto * materialized_view = dynamic_cast<StorageMaterializedView *>(table.get());
        bool is_refreshable_view = materialized_view && materialized_view->isRefreshable();

        if (!secondary_query && !is_refreshable_view
            && settings[Setting::ignore_drop_queries_probability] != 0 && ast_drop_query.kind == ASTDropQuery::Kind::Drop"""

if old_lines not in content:
    print("ERROR: Could not find the exact pattern to replace")
    print("Searching for partial match...")
    if "bool secondary_query = getContext()->getClientInfo().query_kind" in content:
        print("Found secondary_query line")
    if "settings[Setting::ignore_drop_queries_probability]" in content:
        print("Found ignore_drop_queries_probability")
    exit(1)

new_content = content.replace(old_lines, new_lines)

with open("src/Interpreters/InterpreterDropQuery.cpp", "w") as f:
    f.write(new_content)

print("Patch applied successfully")
PYTHON_SCRIPT

echo "Patch applied successfully"
