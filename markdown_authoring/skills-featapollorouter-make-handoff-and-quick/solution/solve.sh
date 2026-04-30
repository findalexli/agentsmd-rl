#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "- Local supergraph path: use `graphql-schema` + `apollo-server` to define/run su" "skills/apollo-router/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/apollo-router/SKILL.md b/skills/apollo-router/SKILL.md
@@ -12,7 +12,7 @@ license: MIT
 compatibility: Linux/macOS/Windows. Requires a composed supergraph schema from Rover or GraphOS.
 metadata:
   author: apollographql
-  version: "2.0.0"
+  version: "2.2.1"
 allowed-tools: Bash(router:*) Bash(./router:*) Bash(rover:*) Bash(curl:*) Bash(docker:*) Read Write Edit Glob Grep
 ---
 
@@ -169,50 +169,25 @@ After answering any Apollo Router request (config generation, edits, validation,
 
 If prerequisites are already present, do not add extra handoff text.
 
-If prerequisites are missing or unknown, end with a concise **Next steps** handoff (1-3 lines max):
+If prerequisites are missing or unknown, end with a concise **Next steps** handoff (1-3 lines max) that is skill-first and command-free:
 
-1. Compose or fetch a supergraph (`rover supergraph compose` or `rover supergraph fetch`).
-2. Run Router with both supergraph and config (`router --supergraph ... --config router.yaml`).
-3. If subgraphs are missing, suggest using related skills (`apollo-server`, `graphql-schema`, `rover`, `graphql-operations`) to scaffold and test.
+1. Suggest the `rover` skill to compose or fetch the supergraph schema.
+2. Suggest continuing with `apollo-router` once the supergraph is ready to validate and run with the generated config.
+3. If subgraphs are missing, suggest `apollo-server`, `graphql-schema`, and `graphql-operations` skills to scaffold and test.
 
-## Quick Start (for reference)
+Do not include raw shell commands in this handoff unless the user explicitly asks for commands.
 
-### Install
+## Quick Start (skill-first)
 
-```bash
-# macOS/Linux
-curl -sSL https://router.apollo.dev/download/nix/latest | sh
-sudo mv router /usr/local/bin/
-router --version
+1. Use this `apollo-router` skill to generate or refine `router.yaml` for your environment.
+2. Choose a runtime path:
+   - GraphOS-managed path: provide `APOLLO_KEY` and `APOLLO_GRAPH_REF` (no local supergraph composition required).
+   - Local supergraph path: use `graphql-schema` + `apollo-server` to define/run subgraphs, then use `graphql-operations` for smoke tests, then use the `rover` skill to compose or fetch `supergraph.graphql`.
+3. Use this `apollo-router` skill to validate readiness (`validation/checklist.md`) and walk through runtime startup inputs.
 
-# Docker
-docker pull ghcr.io/apollographql/router:latest
-```
-
-### Get a Supergraph Schema
-
-```bash
-# Compose from local files
-rover supergraph compose --config supergraph.yaml > supergraph.graphql
-
-# Or fetch from GraphOS
-rover supergraph fetch my-graph@production > supergraph.graphql
-```
-
-### Run the Router
-
-```bash
-# With local schema
-router --supergraph supergraph.graphql
-
-# With configuration file
-router --supergraph supergraph.graphql --config router.yaml
-
-# Development mode (relaxed security, better errors)
-router --dev --supergraph supergraph.graphql
-```
+Default endpoint remains `http://localhost:4000` when using standard Router listen defaults.
 
-Default endpoint: `http://localhost:4000`
+If the user asks for executable shell commands, provide them on request. Otherwise keep Quick Start guidance skill-oriented.
 
 ## Running Modes
 
@@ -280,5 +255,8 @@ Options:
 - MUST run `router config validate <file>` when Router CLI is available
 - MUST report when CLI validation could not run (for example, Router binary missing)
 - MUST append a brief conditional handoff when runtime prerequisites are missing or unknown
+- MUST make this handoff skill-first and avoid raw shell commands unless the user explicitly requests commands
+- MUST keep Quick Start guidance skill-first and command-free unless the user explicitly requests commands
+- MUST state that Rover is required only for the local supergraph path; GraphOS-managed runtime does not require local Rover composition
 - USE `max_depth: 50` as the default starting point, not 15 (too aggressive) or 100 (too permissive)
 - RECOMMEND `warn_only: true` for initial limits rollout to observe real traffic before enforcing
PATCH

echo "Gold patch applied."
