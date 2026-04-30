#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruby-sdk

# Idempotency guard
if grep -qF "3. **Server registration**: `server.define_tool(name: \"my_tool\") { ... }`" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -8,7 +8,7 @@ This is the official Ruby SDK for the Model Context Protocol (MCP), implementing
 
 - Ruby 3.2.0+ required
 - Run `bundle install` to install dependencies
-- Dependencies: `json_rpc_handler` ~> 0.1, `json-schema` >= 4.1
+- Dependencies: `json-schema` >= 4.1 - Schema validation
 
 ## Build and test commands
 
@@ -100,12 +100,6 @@ This is the official Ruby SDK for the Model Context Protocol (MCP), implementing
 - `server_context` hash passed through tool/prompt calls for request-specific data
 - Methods can accept `server_context:` keyword argument for accessing context
 
-### Dependencies
-
-- `json_rpc_handler` ~> 0.1 - JSON-RPC 2.0 message handling
-- `json-schema` >= 4.1 - Schema validation
-- Ruby 3.2.0+ required
-
 ### Integration patterns
 
 - **Rails controllers**: Use `server.handle_json(request.body.read)` for HTTP endpoints
@@ -116,4 +110,4 @@ This is the official Ruby SDK for the Model Context Protocol (MCP), implementing
 
 1. **Class inheritance**: `class MyTool < MCP::Tool`
 2. **Define methods**: `MCP::Tool.define(name: "my_tool") { ... }`
-3. **Server registration**: `server.define_tool(name: "my_tool") { ... }`
\ No newline at end of file
+3. **Server registration**: `server.define_tool(name: "my_tool") { ... }`
PATCH

echo "Gold patch applied."
