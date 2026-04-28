#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kubernetes-mcp-server

# Idempotency guard
if grep -qF "- Each toolset lives in its own subdirectory under `pkg/toolsets/` (e.g., `pkg/t" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -11,12 +11,15 @@ This MCP server enables AI assistants (like Claude, Gemini, Cursor, and others)
 - Go package layout follows the standard Go conventions:
   - `cmd/kubernetes-mcp-server/` – main application entry point using Cobra CLI framework.
   - `pkg/` – libraries grouped by domain.
+    - `api/` - API-related functionality, tool definitions, and toolset interfaces.
     - `config/` – configuration management.
     - `helm/` - Helm chart operations integration.
     - `http/` - HTTP server and authorization middleware.
     - `kubernetes/` - Kubernetes client management, authentication, and access control.
     - `mcp/` - Model Context Protocol (MCP) server implementation with tool registration and STDIO/HTTP support.
     - `output/` - output formatting and rendering.
+    - `toolsets/` - Toolset registration and management for MCP tools.
+    - `version/` - Version information management.
 - `.github/` – GitHub-related configuration (Actions workflows, issue templates...).
 - `docs/` – documentation files.
 - `npm/` – Node packages that wraps the compiled binaries for distribution through npmjs.com.
@@ -30,6 +33,21 @@ Implement new functionality in the Go sources under `cmd/` and `pkg/`.
 The JavaScript (`npm/`) and Python (`python/`) directories only wrap the compiled binary for distribution (npm and PyPI).
 Most changes will not require touching them unless the version or packaging needs to be updated.
 
+### Adding new MCP tools
+
+The project uses a toolset-based architecture for organizing MCP tools:
+
+- **Tool definitions** are created in `pkg/api/` using the `ServerTool` struct.
+- **Toolsets** group related tools together (e.g., config tools, core Kubernetes tools, Helm tools).
+- **Registration** happens in `pkg/toolsets/` where toolsets are registered at initialization.
+- Each toolset lives in its own subdirectory under `pkg/toolsets/` (e.g., `pkg/toolsets/config/`, `pkg/toolsets/core/`, `pkg/toolsets/helm/`).
+
+When adding a new tool:
+1. Define the tool handler function that implements the tool's logic.
+2. Create a `ServerTool` struct with the tool definition and handler.
+3. Add the tool to an appropriate toolset (or create a new toolset if needed).
+4. Register the toolset in `pkg/toolsets/` if it's a new toolset.
+
 ## Building
 
 Use the provided Makefile targets:
@@ -105,6 +123,45 @@ make lint
 
 The `lint` target downloads the specified `golangci-lint` version if it is not already present under `_output/tools/bin/`.
 
+## Additional Makefile targets
+
+Beyond the basic build, test, and lint targets, the Makefile provides additional utilities:
+
+**Local Development:**
+```bash
+# Setup a complete local development environment with Kind cluster
+make local-env-setup
+
+# Tear down the local Kind cluster
+make local-env-teardown
+
+# Show Keycloak status and connection info (for OIDC testing)
+make keycloak-status
+
+# Tail Keycloak logs
+make keycloak-logs
+
+# Install required development tools (like Kind) to ./_output/bin/
+make tools
+```
+
+**Distribution and Publishing:**
+```bash
+# Copy compiled binaries to each npm package
+make npm-copy-binaries
+
+# Publish the npm packages
+make npm-publish
+
+# Publish the Python packages
+make python-publish
+
+# Update README.md with the latest toolsets
+make update-readme-tools
+```
+
+Run `make help` to see all available targets with descriptions.
+
 ## Dependencies
 
 When introducing new modules run `make tidy` so that `go.mod` and `go.sum` remain tidy.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
