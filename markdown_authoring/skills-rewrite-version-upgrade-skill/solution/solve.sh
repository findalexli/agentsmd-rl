#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: \"Guides Qdrant version upgrades without downtime. Use when someone " "skills/qdrant-version-upgrade/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-version-upgrade/SKILL.md b/skills/qdrant-version-upgrade/SKILL.md
@@ -1,23 +1,46 @@
 ---
 name: qdrant-version-upgrade
-description: "Guidance on how to upgrade your Qdrant version without interrupting the availability of your application and ensuring data integrity."
-allowed-tools:
-  - Read
-  - Grep
-  - Glob
+description: "Guides Qdrant version upgrades without downtime. Use when someone asks 'how to upgrade Qdrant', 'is my version compatible', 'rolling upgrade', 'can I skip versions', 'upgrade broke something', or 'SDK version mismatch'. Also use when planning a major or minor version bump."
 ---
 
+# What to Do When Upgrading Qdrant
 
-# Qdrant Version Upgrade
+Compatibility is only guaranteed between consecutive minor versions. You must upgrade sequentially (1.15 to 1.16 to 1.17). Qdrant Cloud automates intermediate steps, self-hosted does not. Storage migration is automatic and irreversible. No downgrades.
 
-Qdrant have the following guarantees about version compatibility:
+- Check upgrade details [Cluster upgrades](https://qdrant.tech/documentation/cloud/cluster-upgrades/)
 
-- Major and minor versions of Qdrant and SDK are expected to match. For example, Qdrant 1.17.x is compatible with SDK 1.17.x.
 
-- Qdrant is tested for backward compatibility between minor versions. For example, Qdrant 1.17.x should be compatible with SDK 1.16.x. Qdrant server 1.16.x is also expected to be compatible with SDK 1.17.x, but only for the subset of features that were available in 1.16.x.
+## Planning an Upgrade
 
-- For migration to next minor version, it is recommended to first upgrade the SDK to the next minor version, and then upgrade the Qdrant server.
+Use when: deciding whether and how to upgrade.
 
-- Storage compatibility is only guaranteed for one minor version. For example, data stored with Qdrant 1.16.x is expected to be compatible with Qdrant 1.17.x. If you need to migrate more than 1 minor version, it is required do the upgrade step by step, one minor version at a time. E.g. to migrate from 1.15.x to 1.17.x, you need to first upgrade to 1.16.x, and then to 1.17.x. Note: Qdrant cloud automates this process, so you can directly upgrade from 1.15.x to 1.17.x without intermediate steps.
+- Major and minor versions of Qdrant and SDK are expected to match (1.17.x server with 1.17.x SDK)
+- Backward compatible one minor version (server 1.17 works with SDK 1.16, but only for 1.16 features) [Qdrant fundamentals](https://qdrant.tech/documentation/faq/qdrant-fundamentals/)
+- Upgrade SDK first, then server. Not the other way around.
+- Take a backup before upgrading to allow rollback
+- Check release notes for breaking changes [Release notes](https://github.com/qdrant/qdrant/releases)
 
-- Qdrant cluster with replication factor of 2 and above can be upgraded without downtime, by performing a rolling upgrade. This means that you can upgrade one node at a time, while the other nodes continue to serve requests. This allows you to maintain availability of your application during the upgrade process. More about replication factor: https://qdrant.tech/documentation/guides/distributed_deployment/#replication-factor
+## Zero-Downtime Upgrade (Rolling)
+
+Use when: production must stay available during upgrade.
+
+- Requires multi-node cluster with `replication_factor: 2` or higher [Replication](https://qdrant.tech/documentation/guides/distributed_deployment/#replication-factor)
+- Single-node clusters or `replication_factor: 1` require brief downtime
+- Upgrade one node at a time while others continue serving
+
+## Skipping Versions
+
+Use when: need to jump more than one minor version.
+
+- Self-hosted: must upgrade one minor version at a time (1.15 to 1.16 to 1.17). No skipping.
+- Qdrant Cloud: handles multi-version jumps automatically with intermediate updates
+
+
+## What NOT to Do
+
+- Skip minor versions on self-hosted (storage format incompatibility)
+- Let SDK drift more than one minor version from cluster (compatibility not guaranteed)
+- Upgrade server before SDK (upgrade SDK first, then server)
+- Upgrade all nodes simultaneously in a cluster (defeats rolling upgrade, causes downtime)
+- Downgrade after upgrading (storage migration is irreversible)
+- Upgrade without a backup (no rollback path if something breaks)
PATCH

echo "Gold patch applied."
