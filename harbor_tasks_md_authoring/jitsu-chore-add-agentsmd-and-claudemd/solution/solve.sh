#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jitsu

# Idempotency guard
if grep -qF "- `connectors/` \u2014 warehouse connectors (ClickHouse, BigQuery, Redshift, Snowflak" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,90 @@
+# Jitsu — Agent Guidelines
+
+## Project Overview
+
+Jitsu is an open-source data pipeline platform (self-hosted Segment alternative). It
+collects events from websites/apps and routes them to data warehouses and other
+destinations.
+
+## Repository Structure
+
+This is a monorepo with two main technology stacks:
+
+### Go (`/bulker`)
+
+Data ingestion engine for streaming events to warehouses.
+
+- `bulkerapp/` — main Bulker service
+- `ingest/` — HTTP ingest endpoint
+- `sync-controller/` — connector sync orchestration
+- `bulkerlib/` — core ingestion library
+- `connectors/` — warehouse connectors (ClickHouse, BigQuery, Redshift, Snowflake, S3,
+  GCS, etc.)
+
+### Node.js / TypeScript
+
+**Services (`/services`)**
+- `rotor/` — event routing, transformation, and function execution
+
+**Web apps (`/webapps`)**
+- `console/` — admin UI (Next.js)
+- `ee-api/` — enterprise edition API (Next.js)
+
+**Libraries (`/libs`)**
+- `jitsu-js/` — browser JS SDK (`@jitsu/js`)
+- `jitsu-react/` — React bindings (`@jitsu/jitsu-react`)
+- `functions/` — functions runtime (`@jitsu/functions-lib`)
+- `juava/` — shared utilities
+
+**CLI (`/cli`)**
+- `jitsu-cli/` — developer CLI (`jitsu-cli` on npm)
+
+**Types (`/types`)**
+- `protocols/` — shared TypeScript protocols (`@jitsu/protocols`)
+
+## Tooling
+
+- **Node.js:** pnpm ≥10 (workspace manager), Turbo (build orchestration), Node.js ≥22
+- **Go:** Go 1.26 with Go workspaces (`go.work` at repo root)
+- **Frontend:** Next.js, React 18, TypeScript, Tailwind CSS
+- **Testing:** Jest (unit), Playwright (E2E), Go's built-in `testing`
+- **CI:** GitHub Actions (`.github/workflows/`)
+
+## Common Commands
+
+```bash
+# Install JS dependencies
+pnpm install
+
+# Build all JS packages
+pnpm build:turbo
+
+# Type-check
+pnpm typecheck:turbo
+
+# Run unit tests
+pnpm test
+
+# Lint / format
+pnpm lint
+pnpm format
+
+# Start all dev services (hot-reload)
+pnpm dev
+
+# Start only the console
+pnpm console:dev
+```
+
+For Go (run inside `/bulker`):
+
+```bash
+go build ./...
+go test ./...
+```
+
+## Git Workflow
+
+When you need to create branches, make commits, or open pull requests, read
+[CONTRIBUTING.md](CONTRIBUTING.md) first. No need to read it for code exploration —
+only when interacting with git.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
