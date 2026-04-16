#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already patched (idempotency check)
if grep -q "pg_advisory_lock(3617572382373537863)" enterprise/migrations/env.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Use Python to apply the patch reliably
python3 << 'EOF'
import re

# Read the file
with open('enterprise/migrations/env.py', 'r') as f:
    content = f.read()

# Fix 1: Add 'text' to the sqlalchemy import
content = content.replace(
    'from sqlalchemy import create_engine  # noqa: E402',
    'from sqlalchemy import create_engine, text  # noqa: E402'
)

# Fix 2: Add advisory lock before migrations
old_pattern = '''        with context.begin_transaction():
            context.run_migrations()'''

new_code = '''        # Lock number must be unique — md5 hash of 'openhands_enterprise_migrations'
        # Lock is released when the connection context manager exits
        connection.execute(text('SELECT pg_advisory_lock(3617572382373537863)'))

        with context.begin_transaction():
            context.run_migrations()'''

content = content.replace(old_pattern, new_code)

# Write the file
with open('enterprise/migrations/env.py', 'w') as f:
    f.write(content)

print("Patch applied successfully")
EOF
