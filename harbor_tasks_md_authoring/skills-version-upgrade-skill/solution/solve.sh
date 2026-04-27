#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "- Storage compatibility is only guaranteed for one minor version. For example, d" "skills/qdrant-version-upgrade/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-version-upgrade/SKILL.md b/skills/qdrant-version-upgrade/SKILL.md
@@ -10,5 +10,14 @@ allowed-tools:
 
 # Qdrant Version Upgrade
 
-<!-- ToDo -->
+Qdrant have the following guarantees about version compatibility:
 
+- Major and minor versions of Qdrant and SDK are expected to match. For example, Qdrant 1.17.x is compatible with SDK 1.17.x.
+
+- Qdrant is tested for backward compatibility between minor versions. For example, Qdrant 1.17.x should be compatible with SDK 1.16.x. Qdrant server 1.16.x is also expected to be compatible with SDK 1.17.x, but only for the subset of features that were available in 1.16.x.
+
+- For migration to next minor version, it is recommended to first upgrade the SDK to the next minor version, and then upgrade the Qdrant server.
+
+- Storage compatibility is only guaranteed for one minor version. For example, data stored with Qdrant 1.16.x is expected to be compatible with Qdrant 1.17.x. If you need to migrate more than 1 minor version, it is required do the upgrade step by step, one minor version at a time. E.g. to migrate from 1.15.x to 1.17.x, you need to first upgrade to 1.16.x, and then to 1.17.x. Note: Qdrant cloud automates this process, so you can directly upgrade from 1.15.x to 1.17.x without intermediate steps.
+
+- Qdrant cluster with replication factor of 2 and above can be upgraded without downtime, by performing a rolling upgrade. This means that you can upgrade one node at a time, while the other nodes continue to serve requests. This allows you to maintain availability of your application during the upgrade process. More about replication factor: https://qdrant.tech/documentation/guides/distributed_deployment/#replication-factor
PATCH

echo "Gold patch applied."
