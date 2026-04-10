#!/bin/bash
cat <<'PATCH' >> /workspace/task/solution/solve.sh
diff --git a/README.md b/README.md
index 1234567..89abcdef 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,3 @@
 # Apache Airflow
+
+Note: workers.affinity is deprecated. Use workers.celery.affinity and workers.kubernetes.affinity instead.
PATCH
