#!/bin/bash
# Solution for apache/superset#39099
# Fix: Check pre-existing foreign keys on create utility

set -e

cd /workspace/superset

# Idempotency check - skip if already applied
if grep -q "def get_foreign_key_names" superset/migrations/shared/utils.py 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

UTILS_FILE="superset/migrations/shared/utils.py"

# Step 1: Add get_foreign_key_names() function before drop_fks_for_table
# Find the line number of "def drop_fks_for_table"
LINE_NUM=$(grep -n "^def drop_fks_for_table" "$UTILS_FILE" | cut -d: -f1)

# Insert the new function before drop_fks_for_table
sed -i "${LINE_NUM}i\\
def get_foreign_key_names(table_name: str) -> set[str]:\\
    \"\"\"\\
    Get the set of foreign key constraint names for a table.\\
\\
    :param table_name: The table name\\
    :returns: A set of foreign key constraint names\\
    \"\"\"\\
    connection = op.get_bind()\\
    inspector = Inspector.from_engine(connection)\\
    return {fk[\"name\"] for fk in inspector.get_foreign_keys(table_name)}\\
\\
" "$UTILS_FILE"

# Step 2: Modify drop_fks_for_table to use the helper
# Remove the inspector line and update existing_fks line
sed -i '/^def drop_fks_for_table/,/^def [a-z]/ {
    /inspector = Inspector.from_engine(connection)/d
    s/existing_fks = {fk\["name"\] for fk in inspector.get_foreign_keys(table_name)}/existing_fks = get_foreign_key_names(table_name)/
}' "$UTILS_FILE"

# Step 3: Add FK existence check to create_fks_for_table
# Find the line "if not has_table(table_name):" within create_fks_for_table and add check after its block
sed -i '/^def create_fks_for_table/,/^def [a-z]/ {
    /if isinstance(connection.dialect, SQLiteDialect):/ {
        i\
    if foreign_key_name in get_foreign_key_names(table_name):\
        logger.info(\
            "Foreign key %s%s%s already exists on table %s%s%s. Skipping...",\
            GREEN,\
            foreign_key_name,\
            RESET,\
            GREEN,\
            table_name,\
            RESET,\
        )\
        return
    }
}' "$UTILS_FILE"

echo "Patch applied successfully"

# Verify syntax is valid
python3 -m py_compile "$UTILS_FILE" && echo "Syntax check passed"
