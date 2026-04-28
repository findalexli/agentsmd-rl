#!/usr/bin/env bash
set -euo pipefail

cd /workspace/minder

# Idempotency guard
if grep -qF "**Note**: Run `make bootstrap` once after cloning the repository. You may need t" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -70,15 +70,43 @@ Minder consists of:
 
 ### Prerequisites
 
+**Required tools:**
 - Go 1.24+
 - Docker & Docker Compose
-- PostgreSQL (via Docker)
+- OpenSSL (for key generation)
+
+**Build tools (installed via `make bootstrap`):**
 - ko (for container builds)
 - buf (Protocol Buffer compilation)
 - sqlc (SQL code generation)
 - golangci-lint (linting)
 - gotestfmt (test output formatting)
-- Keycloak (via Docker for local auth)
+- protoc plugins (grpc-gateway, protoc-gen-go, etc.)
+- mockgen (mock generation)
+- yq (YAML processing)
+- fga (OpenFGA CLI)
+- helm-docs (Helm documentation)
+
+**Runtime services (via Docker):**
+- PostgreSQL (database)
+- Keycloak (authentication)
+- NATS (message queue)
+
+### Initial Setup
+
+Before building or running Minder, install all build dependencies and initialize configuration:
+
+```bash
+# Install build tools and initialize configuration
+make bootstrap
+```
+
+This command will:
+- Install all Go-based build tools (sqlc, protoc plugins, mockgen, etc.)
+- Create `config.yaml` and `server-config.yaml` from example templates (if they don't exist)
+- Generate encryption keys in `.ssh/` directory for token signing
+
+**Note**: Run `make bootstrap` once after cloning the repository. You may need to run it again if build tool versions change.
 
 ### Building
 
@@ -380,6 +408,7 @@ if errors.Is(err, sql.ErrNoRows) {
 
 ```bash
 make help           # Show all available targets
+make bootstrap      # Install build tools and initialize configuration (run once)
 make build          # Build CLI and server binaries
 make gen            # Run all code generators
 make test           # Run all tests with verbose output
PATCH

echo "Gold patch applied."
