#!/bin/bash
set -e

cd /workspace/superset

# Apply the gold patch
cat << 'PATCH' | git apply -
diff --git a/superset/migrations/shared/utils.py b/superset/migrations/shared/utils.py
index dbcfa2f9f5ba..f91f3d1a45e7 100644
--- a/superset/migrations/shared/utils.py
+++ b/superset/migrations/shared/utils.py
@@ -199,6 +199,18 @@ def has_table(table_name: str) -> bool:
     return table_exists


+def get_foreign_key_names(table_name: str) -> set[str]:
+    """
+    Get the set of foreign key constraint names for a table.
+
+    :param table_name: The table name
+    :returns: A set of foreign key constraint names
+    """
+    connection = op.get_bind()
+    inspector = Inspector.from_engine(connection)
+    return {fk["name"] for fk in inspector.get_foreign_keys(table_name)}
+
+
 def drop_fks_for_table(
     table_name: str, foreign_key_names: list[str] | None = None
 ) -> None:
@@ -211,13 +223,12 @@ def drop_fks_for_table(
     If None is provided, all will be dropped.
     """
     connection = op.get_bind()
-    inspector = Inspector.from_engine(connection)

     if isinstance(connection.dialect, SQLiteDialect):
         return  # sqlite doesn't like constraints

     if has_table(table_name):
-        existing_fks = {fk["name"] for fk in inspector.get_foreign_keys(table_name)}
+        existing_fks = get_foreign_key_names(table_name)

         # What to delete based on whether the list was passed
         if foreign_key_names is not None:
@@ -523,6 +534,18 @@ def create_fks_for_table(
         )
         return

+    if foreign_key_name in get_foreign_key_names(table_name):
+        logger.info(
+            "Foreign key %s%s%s already exists on table %s%s%s. Skipping...",
+            GREEN,
+            foreign_key_name,
+            RESET,
+            GREEN,
+            table_name,
+            RESET,
+        )
+        return
+
     if isinstance(connection.dialect, SQLiteDialect):
         # SQLite requires batch mode since ALTER TABLE is limited
         with op.batch_alter_table(table_name) as batch_op:
PATCH

# Verify the patch was applied
grep -q "def get_foreign_key_names" superset/migrations/shared/utils.py && echo "Patch applied successfully"
