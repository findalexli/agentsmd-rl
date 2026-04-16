#!/bin/bash
# Gold solution for apache/superset PR #39207
# Adds template_processor to adhoc_column_to_sqla call in get_sqla_query filter processing

set -e

cd /workspace/superset

# Idempotency check - skip if patch already applied
# Check for the specific multi-line pattern added by the fix
if grep -A2 "adhoc_column_to_sqla(" superset/models/helpers.py | grep -q "force_type_check=True,$"; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/superset/models/helpers.py b/superset/models/helpers.py
index c6e2b693b96d..71958d8cf837 100644
--- a/superset/models/helpers.py
+++ b/superset/models/helpers.py
@@ -3012,7 +3012,11 @@ def get_sqla_query(  # pylint: disable=too-many-arguments,too-many-locals,too-ma
                 col_obj = dttm_col
             elif is_adhoc_column(flt_col):
                 try:
-                    sqla_col = self.adhoc_column_to_sqla(flt_col, force_type_check=True)
+                    sqla_col = self.adhoc_column_to_sqla(
+                        flt_col,
+                        force_type_check=True,
+                        template_processor=template_processor,
+                    )
                     applied_adhoc_filters_columns.append(flt_col)
                 except ColumnNotFoundException:
                     rejected_adhoc_filters_columns.append(flt_col)
PATCH

echo "Patch applied successfully."
