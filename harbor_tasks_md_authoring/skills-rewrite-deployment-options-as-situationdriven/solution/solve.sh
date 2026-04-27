#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "description: \"Guides Qdrant deployment selection. Use when someone asks 'how to " "skills/qdrant-deployment-options/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/qdrant-deployment-options/SKILL.md b/skills/qdrant-deployment-options/SKILL.md
@@ -1,64 +1,53 @@
 ---
 name: qdrant-deployment-options
-description: "Guides Qdrant deployment selection. Use when someone asks 'how to deploy Qdrant', 'Docker vs Cloud', 'local mode', 'embedded Qdrant', 'Qdrant EDGE', 'which deployment option', or 'self-hosted vs cloud'. Also use when choosing between deployment types for a new project."
-allowed-tools:
-  - Read
-  - Grep
-  - Glob
+description: "Guides Qdrant deployment selection. Use when someone asks 'how to deploy Qdrant', 'Docker vs Cloud', 'local mode', 'embedded Qdrant', 'Qdrant EDGE', 'which deployment option', 'self-hosted vs cloud', or 'need lowest latency deployment'. Also use when choosing between deployment types for a new project."
 ---
 
+# Which Qdrant Deployment Do I Need?
 
-# Qdrant Deployment
+Start with what you need: managed ops or full control? Network latency acceptable or not? Production or prototyping? The answer narrows to one of four options.
 
-Qdrant deployment types can be categorized into two broad categories: client-server deployments and embedded deployments.
-Server deployments are suitable for production environments, where accessibility, scalability, and reliability are important.
-This document focuses on several deployment options for Qdrant, including self-hosted, cloud-based, and embedded deployments, and provides guidance on how to choose the right one for your use case.
 
+## Getting Started or Prototyping
 
-## Docker Deployment
+Use when: building a prototype, running tests, CI/CD pipelines, or learning Qdrant.
 
-Docker-based deployment is the default and most common way to deploy Qdrant.
-It provides full features of Qdrant Open Source and requires minimal setup. 
+- Use local mode (Python only): zero-dependency, in-memory or disk-persisted, no server needed [Local mode](https://qdrant.tech/documentation/quickstart/)
+- Local mode data format is NOT compatible with server. Do not use for production or benchmarking.
+- For a real server locally, use Docker [Quick start](https://qdrant.tech/documentation/quickstart/#download-and-run)
 
-Minimal command to run Qdrant in Docker is:
 
-```bash
-docker run -p 6333:6333 qdrant/qdrant
-```
+## Going to Production (Self-Hosted)
 
-For more details on Docker deployment, see [Quick Start -Download and Run](https://qdrant.tech/documentation/quickstart/#download-and-run)
+Use when: you need full control over infrastructure, data residency, or custom configuration.
 
-## Cloud-Based Deployment
+- Docker is the default deployment. Full Qdrant Open Source feature set, minimal setup. [Quick start](https://qdrant.tech/documentation/quickstart/#download-and-run)
+- You own operations: upgrades, backups, scaling, monitoring
+- Must set up distributed mode manually for multi-node clusters [Distributed deployment](https://qdrant.tech/documentation/guides/distributed_deployment/)
+- Consider Hybrid Cloud if you want Qdrant Cloud management on your infrastructure [Hybrid Cloud](https://qdrant.tech/documentation/hybrid-cloud/)
 
-Cloud-based deployment is another version of the client-server deployment, where Qdrant is hosted on a Qdrant Cloud platform.
-On top of the features of the self-hosted deployment, Qdrant Cloud also provides additional features such as zero-downtime updates, resharding, automatic backups, and more. 
 
-For more details on Qdrant Cloud, see [Qdrant Cloud](https://qdrant.tech/documentation/cloud-quickstart/)
+## Going to Production (Zero-Ops)
 
+Use when: you want managed infrastructure with zero-downtime updates, automatic backups, and resharding without operating clusters yourself.
 
-## Local Mode Deployment
+- Qdrant Cloud handles upgrades, scaling, backups, and monitoring [Qdrant Cloud](https://qdrant.tech/documentation/cloud-quickstart/)
+- Supports multi-version upgrades automatically
+- Provides features not available in self-hosted: `/sys_metrics`, managed resharding, pre-configured alerts
 
-One of the features of Qdrant Python Client is the ability to run Qdrant in local mode.
-Local mode is a zero-dependency pure Python implementation of Qdrant API, which is tested for congruence with the server version of Qdrant.
 
-Local mode can either be completely in-memory, or can be configured to use disk storage.
+## Need Lowest Possible Latency
 
-```
-from qdrant_client import QdrantClient
+Use when: network round-trip to a server is unacceptable. Edge devices, in-process search, or latency-critical applications.
 
-client = QdrantClient(":memory:")
-# or
-client = QdrantClient(path="path/to/db")  # Persists changes to disk
-```
+- Qdrant EDGE: in-process bindings to Qdrant shard-level functions, no network overhead [Qdrant EDGE](https://qdrant.tech/documentation/edge/edge-quickstart/)
+- Same data format as server. Can sync with server via shard snapshots.
+- Single-node feature set only. No distributed mode.
 
-Qdrant local mode is suitable for development, testing, CI/CD pipelines.
-Qdrant local mode is not optimized for performance, and is not recommended for production use cases or benchmarking.
-Qdrant local mode data format is not compatible with the server version of Qdrant.
 
-## Qdrant EDGE
-
-Qdrant EDGE is in-process version of Qdrant. It used direct bindings to Qdrant Shard-level function, and can perform same operations as single-node Qdrant deployment, but without the overhead of network communication.
-Qdrant EDGE uses the same data format as the server version of Qdrant, and can be synchronized with the server by using shard snapshots. This allows you to use Qdrant EDGE for latency-sensitive applications, while still benefiting from the scalability and reliability of a server deployment.
-
-More details on Qdrant EDGE can be found in the [Qdrant EDGE docs](https://qdrant.tech/documentation/edge/edge-quickstart/).
+## What NOT to Do
 
+- Use local mode for production or benchmarking (not optimized, incompatible data format)
+- Self-host without monitoring and backup strategy (you will lose data or miss outages)
+- Choose EDGE when you need distributed search (single-node only)
+- Pick Hybrid Cloud unless you have data residency requirements (unnecessary Kubernetes complexity when Qdrant Cloud works)
PATCH

echo "Gold patch applied."
