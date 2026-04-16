#!/bin/bash
set -e

cd /workspace/dagster

# Check python_packages.md first (per CLAUDE.md conventions)
if [ -f ".claude/python_packages.md" ]; then
    echo "Verified python_packages.md exists"
fi

# Check if already applied (idempotency check)
if grep -q "Dlt keeps some local state that interferes with next runs" python_modules/libraries/dagster-dlt/dagster_dlt/resource.py; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Install uv if not present (using uv for package management per CLAUDE.md)
if ! command -v uv &> /dev/null; then
    pip install uv -q
fi

# Install ruff using uv (needed for make ruff)
uv pip install --system ruff==0.15.0 -q

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py b/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
index 123456..789abc 100644
--- a/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
+++ b/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
@@ -282,6 +282,18 @@ def _run(
                 ]
             )

+        # Dlt keeps some local state that interferes with next runs.
+        # This is annoying when an asset fails and running a different one on the same pipeline
+        # would just pick up the failing job and fail again.
+        # When restore_from_destination is enabled (default), we can safely drop all local state
+        # because it will be restored from the destination.
+        # When restore_from_destination is disabled, we only drop pending packages to avoid
+        # wiping incremental loading cursors that can't be recovered from the destination.
+        if dlt_pipeline.config.restore_from_destination:
+            dlt_pipeline.drop()
+        else:
+            dlt_pipeline.drop_pending_packages()
+
         load_info = dlt_pipeline.run(dlt_source, **kwargs)

         load_info.raise_on_failed_jobs()
PATCH

echo "Gold patch applied successfully"

# Run make ruff after code changes (mandatory per CLAUDE.md)
echo "Running make ruff to format and lint code..."
make ruff || echo "Note: make ruff may modify files for formatting"
