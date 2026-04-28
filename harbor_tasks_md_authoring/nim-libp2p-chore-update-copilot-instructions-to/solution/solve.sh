#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nim-libp2p

# Idempotency guard
if grep -qF "| `daily_ci_report.yml` | Daily CI failure reporting: opens/updates GitHub issue" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -157,7 +157,7 @@ The test runner (`libp2p.nimble`) always compiles with:
 
 ## Key Dependencies
 
-- **chronos** (`>= 4.0.4`) — Async I/O framework (core dependency, used everywhere)
+- **chronos** (`>= 4.2.2`) — Async I/O framework (core dependency, used everywhere)
 - **chronicles** (`>= 0.11.0`) — Structured logging
 - **stew** (`>= 0.4.2`) — Utility library
 - **results** — Result/Option types for error handling
@@ -392,13 +392,16 @@ The test runner (`libp2p.nimble`) always compiles with:
 - `dcutr/` — Direct Connection Upgrade Through Relay (hole punching)
 - `relay/` — Circuit Relay v1/v2
 
+### Identify (`protocols/`)
+- `identify.nim` — Identify and Identify Push protocols (peer metadata exchange)
+
 ### Performance (`protocols/perf/`)
 - `core.nim`, `client.nim`, `server.nim` — libp2p perf protocol for measuring throughput between peers
 
 ### Discovery (`protocols/`)
 - `kademlia.nim` + `kademlia/` — Kademlia DHT
-- `kad_disco.nim` + `kademlia_discovery/` — Kademlia-based peer discovery
-- `rendezvous.nim` — Rendezvous server protocol
+- `rendezvous.nim` + `rendezvous/` — Rendezvous server protocol
+- `service_discovery.nim` + `service_discovery/` — Service discovery (random find, routing table manager)
 
 ### Privacy (`protocols/mix/`)
 - Sphinx mix network for privacy-preserving message routing
@@ -470,6 +473,7 @@ nimble examples      # Build and run C examples
 |----------|-------------|
 | `ci.yml` | Main CI: Linux (amd64/i386), macOS (arm64), Windows; Nim v2.0.16 & v2.2.6 |
 | `daily_amd64.yml` / `daily_i386.yml` | Extended daily tests |
+| `daily_ci_report.yml` | Daily CI failure reporting: opens/updates GitHub issues for failed daily CI runs |
 | `daily_common.yml` | Shared steps/config reused by daily workflows |
 | `daily_nimbus.yml` | Nimbus-specific test matrix |
 | `daily_tests_no_flags.yml` | Tests without experimental flags |
PATCH

echo "Gold patch applied."
