#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already applied
if grep -q "pg_advisory_lock(3617572382373537863)" enterprise/migrations/env.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/enterprise/migrations/env.py b/enterprise/migrations/env.py
index e3915fbf65ba..23daa3a28d27 100644
--- a/enterprise/migrations/env.py
+++ b/enterprise/migrations/env.py
@@ -8,7 +8,7 @@

 from alembic import context  # noqa: E402
 from google.cloud.sql.connector import Connector  # noqa: E402
-from sqlalchemy import create_engine  # noqa: E402
+from sqlalchemy import create_engine, text  # noqa: E402
 from storage.base import Base  # noqa: E402

 target_metadata = Base.metadata
@@ -109,6 +109,10 @@ def run_migrations_online() -> None:
             version_table_schema=target_metadata.schema,
         )

+        # Lock number must be unique — md5 hash of 'openhands_enterprise_migrations'
+        # Lock is released when the connection context manager exits
+        connection.execute(text('SELECT pg_advisory_lock(3617572382373537863)'))
+
         with context.begin_transaction():
             context.run_migrations()
PATCH

echo "Patch applied successfully"
