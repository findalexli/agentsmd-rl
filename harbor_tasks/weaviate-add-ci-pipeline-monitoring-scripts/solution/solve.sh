#!/usr/bin/env bash
set -euo pipefail

cd /workspace/weaviate

# Idempotent: skip if already applied
if grep -q 'CI / Pipeline Monitoring' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/.claude/scripts/monitor_docker.sh b/.claude/scripts/monitor_docker.sh
new file mode 100755
index 00000000000..1d2bc5dcc54
--- /dev/null
+++ b/.claude/scripts/monitor_docker.sh
@@ -0,0 +1,41 @@
+#!/bin/bash
+
+set -euo pipefail
+
+RUN_ID=${1:-}
+if [ -z "$RUN_ID" ]; then
+  echo "Usage: $0 <run_id>"
+  exit 1
+fi
+
+echo "Monitoring generate-docker-report for run $RUN_ID..."
+
+while true; do
+  RESULT=$(gh run view "$RUN_ID" --repo weaviate/weaviate --json jobs \
+    --jq '.jobs[] | select(.name | test("generate-docker-report|docker report")) | {status: .status, conclusion: .conclusion}' 2>&1)
+
+  STATUS=$(echo "$RESULT" | jq -r '.status' 2>/dev/null || echo "unknown")
+  CONCLUSION=$(echo "$RESULT" | jq -r '.conclusion' 2>/dev/null || echo "unknown")
+
+  echo "[$(date '+%H:%M:%S')] status=$STATUS conclusion=$CONCLUSION"
+
+  if [ "$STATUS" = "completed" ]; then
+    if [ "$CONCLUSION" = "success" ]; then
+      echo "Docker image is ready!"
+      JOB_ID=$(gh run view "$RUN_ID" --repo weaviate/weaviate --json jobs \
+        --jq '.jobs[] | select(.name | test("generate-docker-report|docker report")) | .databaseId')
+      echo "Docker image tags:"
+      gh api repos/weaviate/weaviate/actions/jobs/"$JOB_ID"/logs 2>&1 \
+        | sed 's/\x1b\[[0-9;]*m//g' \
+        | grep -oE 'semitechnologies/weaviate:[a-zA-Z0-9.:_-]+' \
+        | sort -u \
+        | while read -r tag; do echo "  $tag"; done
+      exit 0
+    else
+      echo "generate-docker-report ended with: $CONCLUSION"
+      exit 1
+    fi
+  fi
+
+  sleep 30
+done
diff --git a/.claude/scripts/monitor_pr.sh b/.claude/scripts/monitor_pr.sh
new file mode 100755
index 00000000000..823c947d1dc
--- /dev/null
+++ b/.claude/scripts/monitor_pr.sh
@@ -0,0 +1,34 @@
+#!/bin/bash
+# Monitor CI checks for a PR until all checks complete.
+# Usage: PR=<number> .claude/scripts/monitor_pr.sh
+# Exits with code 0 if all pass, 1 if any fail.
+PR=${PR:-}
+if [ -z "$PR" ]; then
+  echo "Usage: PR=<number> $0"
+  exit 1
+fi
+
+while true; do
+  OUTPUT=$(gh pr checks $PR --repo weaviate/weaviate 2>&1)
+  PASS=$(echo "$OUTPUT" | grep -c $'\tpass\t')
+  FAIL=$(echo "$OUTPUT" | grep -c $'\tfail\t')
+  PENDING=$(echo "$OUTPUT" | grep -c $'\tpending\t')
+  FAILED_CHECKS=$(echo "$OUTPUT" | grep $'\tfail\t' | awk -F'\t' '{print $1}')
+
+  echo "[$(date '+%H:%M:%S')] PASS: $PASS | FAIL: $FAIL | PENDING: $PENDING"
+
+  if [ "$PENDING" -eq 0 ]; then
+    echo ""
+    echo "=== ALL CHECKS COMPLETE ==="
+    echo "PASSED: $PASS | FAILED: $FAIL"
+    if [ -n "$FAILED_CHECKS" ]; then
+      echo ""
+      echo "Failed checks:"
+      echo "$FAILED_CHECKS" | while read line; do echo "  - $line"; done
+      exit 1
+    fi
+    exit 0
+  fi
+
+  sleep 60
+done
diff --git a/.gitignore b/.gitignore
index 7ea079c72f1..e87cf7a5cee 100644
--- a/.gitignore
+++ b/.gitignore
@@ -136,3 +136,4 @@ test/modules/backup-filesystem/bucketPath
 # Claude
 .claude/*
 !.claude/settings.json
+!.claude/scripts/
diff --git a/CLAUDE.md b/CLAUDE.md
index b292c55aa5a..543e99aab9d 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -122,3 +122,32 @@ We use logrus as logger. Always populate errors using `.Error(err)` and do NOT u
 ### API Code Generation
 REST API is generated from OpenAPI specs via go-swagger (`openapi-specs/`). You can regenerate by running `./tools/gen-code-from-swagger.sh`.
 gRPC is generated from protobuf definitions in `grpc/proto/` using `buf`.
+
+## CI / Pipeline Monitoring
+
+All monitoring scripts live in `.claude/scripts/` and are committed to the repo. Always run them as background tasks (use `run_in_background=true` in the Bash tool) so you get notified on completion without blocking the conversation.
+
+### Monitor PR checks
+Polls all CI checks for a PR until they complete. Exits with code 1 if any checks fail:
+```bash
+PR=1234 .claude/scripts/monitor_pr.sh
+```
+
+### Monitor Docker image build
+Use this when waiting for a PR's docker image to be produced. First get the run ID from the PR's docker checks, then pass it to the script:
+```bash
+# Get the run ID
+gh pr checks <PR> --repo weaviate/weaviate 2>&1 | grep -i "docker"
+# Monitor the build
+.claude/scripts/monitor_docker.sh <run_id>
+```
+The script also prints the docker image tags on success. Tags are fetched via `gh api` (works even if the overall run is still in progress).
+
+### Inspect failed checks / rerun
+```bash
+# Get job ID from: gh pr checks <PR> --repo weaviate/weaviate
+gh api repos/weaviate/weaviate/actions/jobs/<job_id>/logs 2>&1 | grep "FAIL:" | head -20
+
+# Re-run only failed jobs:
+gh run rerun <run_id> --failed --repo weaviate/weaviate
+```

PATCH

echo "Patch applied successfully."
