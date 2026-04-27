#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nginx-ui

# Idempotency guard
if grep -qF "AGENTS.md" "AGENTS.md" && grep -qF "- **Backend**: `go generate ./...`, `go build ./...`, run `go test ./... -race -" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+CLAUDE.md
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -23,10 +23,12 @@ This project is a web-based NGINX management interface built with Go backend and
 
 ### Development Guidelines
 - Write concise, maintainable Go code with clear examples
+- Run `gofmt`/`goimports` before committing backend changes
 - Use Gen to streamline database queries and reduce boilerplate
 - Follow Cosy Error Handler best practices for error management
 - Implement standardized CRUD operations using Cosy framework
 - Apply efficient database pagination for large datasets
+- Validate changes with `go test ./... -race -cover` before pushing
 - Keep files modular and well-organized by functionality
 - **All comments and documentation must be in English**
 
@@ -70,10 +72,12 @@ This project is a web-based NGINX management interface built with Go backend and
 
 ### Code Quality
 - **Always use ESLint MCP after generating frontend code** to ensure code quality and consistency
+- Run `pnpm lint`, `pnpm lint:fix`, and `pnpm typecheck` to keep style and typings aligned
 
 ## Development Commands
-- **Frontend**: `pnpm run dev`, `pnpm typecheck`, `pnpm run build`
-- **Backend**: Standard Go commands (`go run`, `go build`, `go test`)
+- **Frontend**: `pnpm run dev`, `pnpm lint`, `pnpm typecheck`, `pnpm run build`
+- **Backend**: `go generate ./...`, `go build ./...`, run `go test ./... -race -cover`; for release artifacts reuse the README command with `-tags=jsoniter -ldflags "$LD_FLAGS ..."`.
+- **Demo stack**: `docker-compose -f docker-compose-demo.yml up` to bootstrap the sample environment
 
 ## Language Requirements
 - **All code comments, documentation, and communication must be in English**
PATCH

echo "Gold patch applied."
