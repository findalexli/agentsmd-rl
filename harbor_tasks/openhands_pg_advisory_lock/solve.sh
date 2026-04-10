#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already applied
if grep -q "pg_advisory_lock(3617572382373537863)" enterprise/migrations/env.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Use Python to properly edit the file
python3 << 'EOF'
import re

with open("enterprise/migrations/env.py", "r") as f:
    content = f.read()

# 1. Add 'text' to the sqlalchemy import
content = content.replace(
    "from sqlalchemy import create_engine  # noqa: E402",
    "from sqlalchemy import create_engine, text  # noqa: E402"
)

# 2. Add the advisory lock call before begin_transaction in run_migrations_online
# Find the pattern in run_migrations_online function
old_pattern = """    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
        )

        with context.begin_transaction():"""

new_pattern = """    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
        )

        # Lock number must be unique — md5 hash of 'openhands_enterprise_migrations'
        # Lock is released when the connection context manager exits
        connection.execute(text('SELECT pg_advisory_lock(3617572382373537863)'))

        with context.begin_transaction():"""

content = content.replace(old_pattern, new_pattern)

with open("enterprise/migrations/env.py", "w") as f:
    f.write(content)

print("Patch applied successfully")
EOF
