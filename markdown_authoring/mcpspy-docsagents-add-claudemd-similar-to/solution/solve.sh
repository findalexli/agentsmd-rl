#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcpspy

# Idempotency guard
if grep -qF "\u2502   \u2514\u2500\u2500 output/          # Output formatting (console, and file output)" ".cursorrules" && grep -qF "MCPSpy is a CLI utility that uses eBPF to monitor MCP (Model Context Protocol) c" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -18,8 +18,10 @@ mcpspy/
 ├── cmd/mcpspy/          # CLI entry point
 ├── pkg/
 │   ├── ebpf/            # eBPF loading and management
+│   ├── event/           # Event definitions and handling
+|   |── http/            # HTTP transport parsing and analysis
 │   ├── mcp/             # MCP protocol parsing and analysis
-│   └── output/          # CLI output formatting
+│   └── output/          # Output formatting (console, and file output)
 ├── bpf/                 # eBPF C programs
 ├── tests/               # Test files
 ├── deploy/docker/  # Docker configuration
@@ -32,7 +34,7 @@ mcpspy/
 - Messages have jsonrpc: "2.0" field
 - Three message types: Request, Response, Notification
 - Track method names like "tools/call", "resources/read", etc.
-- Focus on stdio transport.
+- Focus on both stdio and HTTP transport (streamable HTTP).
 
 ## Performance Guidelines
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,88 @@
+# MCPSpy Project Rules
+
+## Project Overview
+
+MCPSpy is a CLI utility that uses eBPF to monitor MCP (Model Context Protocol) communication by tracking stdio operations and analyzing JSON-RPC 2.0 messages.
+
+## Technology Stack
+
+- Go 1.24+ for the main application
+- C for eBPF programs
+- cilium/ebpf for loading eBPF programs
+- Docker for containerization
+
+## Project Structure
+
+```
+mcpspy/
+├── cmd/mcpspy/          # CLI entry point
+├── pkg/
+│   ├── ebpf/            # eBPF loading and management
+│   ├── event/           # Event definitions and handling
+|   |── http/            # HTTP transport parsing and analysis
+│   ├── mcp/             # MCP protocol parsing and analysis
+│   └── output/          # Output formatting (console, and file output)
+├── bpf/                 # eBPF C programs
+├── tests/               # Test files
+├── deploy/docker/  # Docker configuration
+└── .github/workflows/   # CI/CD workflows
+```
+
+## MCP Protocol Context
+
+- MCP uses JSON-RPC 2.0 format
+- Messages have jsonrpc: "2.0" field
+- Three message types: Request, Response, Notification
+- Track method names like "tools/call", "resources/read", etc.
+- Focus on both stdio and HTTP transport (streamable HTTP).
+
+## Performance Guidelines
+
+- Use efficient data structures
+- Minimize data copying between kernel and userspace
+- Filter early in eBPF to reduce overhead
+
+## Building
+
+```bash
+make build
+```
+
+## Running
+
+```bash
+sudo ./mcpspy
+
+# It is must be stopped by sending SIGINT (Ctrl+C) or SIGTERM.
+```
+
+## Testing
+
+Running all tests (unit tests, and end-to-end tests for both stdio and https transports):
+
+```bash
+make test
+```
+
+Running unit tests:
+
+```bash
+make test-unit
+```
+
+Running end-to-end tests (including mcpspy, and verifying the output):
+
+```bash
+make test-e2e-stdio
+make test-e2e-https
+
+# Or
+make test-e2e
+```
+
+Running solely the mcp e2e tests (without mcpspy):
+
+```bash
+make test-e2e-mcp-stdio
+make test-e2e-mcp-https
+```
PATCH

echo "Gold patch applied."
