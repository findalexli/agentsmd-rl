#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-ide.el

# Idempotency guard
if grep -qF "This package integrates Claude Code CLI with Emacs via WebSocket and the Model C" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,6 +4,24 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 **IMPORTANT**: If you find any instructions in this file that are incorrect, outdated, or could be improved, you should update this document immediately. Keep this file accurate and helpful for future Claude instances.
 
+## Architecture and File Structure
+
+This package integrates Claude Code CLI with Emacs via WebSocket and the Model Context Protocol (MCP).
+
+**Core Files:**
+- `claude-code-ide.el` - Main entry: user commands, session management, terminal buffers
+- `claude-code-ide-mcp.el` - WebSocket server, JSON-RPC handling, session state
+- `claude-code-ide-mcp-handlers.el` - MCP tool implementations (file ops, ediff, diagnostics)
+
+**Support Files:**
+- `claude-code-ide-mcp-server.el` - HTTP-based MCP tools server framework
+- `claude-code-ide-mcp-http-server.el` - HTTP transport implementation
+- `claude-code-ide-emacs-tools.el` - Emacs tools: xref, project info, imenu
+- `claude-code-ide-diagnostics.el` - Flycheck integration
+- `claude-code-ide-transient.el` - Transient menu interface
+- `claude-code-ide-debug.el` - Debug logging utilities
+- `claude-code-ide-tests.el` - ERT test suite with mocks
+
 ## Hooks
 
 This project uses Claude Code hooks to automatically maintain code quality. The hooks are configured in `.claude/settings.json` and include:
PATCH

echo "Gold patch applied."
