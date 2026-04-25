#!/bin/bash
set -e

cd /workspace/airflow

# Check if patch already applied (idempotency check)
if grep -q 'with disable_sqlite_fkeys(op):' airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py && \
   grep -A2 'with disable_sqlite_fkeys(op):' airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py | grep -q 'op.execute("UPDATE log SET event'; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py b/airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py
index 49fb4bcc3f7ac..5af4f7be74d62 100644
--- a/airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py
+++ b/airflow-core/src/airflow/migrations/versions/0097_3_2_0_enforce_log_event_and_dag_is_stale_not_null.py
@@ -40,13 +40,10 @@

 def upgrade():
     """Bring existing deployments in line with 0010 and 0067."""
-    # Ensure `log.event` can safely transition to NOT NULL.
-    op.execute("UPDATE log SET event = '' WHERE event IS NULL")
-
-    # Make sure DAG rows that survived the old 0067 path are not NULL.
-    op.execute("UPDATE dag SET is_stale = false WHERE is_stale IS NULL")
-
     with disable_sqlite_fkeys(op):
+        op.execute("UPDATE log SET event = '' WHERE event IS NULL")
+        op.execute("UPDATE dag SET is_stale = false WHERE is_stale IS NULL")
+
         with op.batch_alter_table("log") as batch_op:
             batch_op.alter_column("event", existing_type=sa.String(60), nullable=False)

PATCH

echo "Patch applied successfully"
