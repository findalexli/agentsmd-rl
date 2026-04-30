#!/usr/bin/env bash
set -euo pipefail

cd /workspace/docker-agent

# Idempotency guard
if grep -qF "- **Agent properties**: name, model, description, instruction, sub_agents, tools" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -9,19 +9,22 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 - `task build` - Build the application binary 
 - `task test` - Run Go tests
 - `task lint` - Run golangci-lint
+- `task format` - Format code
 - `task link` - Create symlink to ~/bin for easy access
 
 ### Docker Operations
 
 - `task build-image` - Build Docker image
+- `task push-image` - Build and push Docker image
 - `task build-local` - Build binaries for local platform using Docker
 - `task cross` - Build cross-platform binaries using Docker
 
 ### Running cagent
 
-- `./bin/cagent run <config.yaml>` - Run agent with configuration
+- `./bin/cagent run <config.yaml>` - Run agent with configuration (uses TUI by default)
+- `./bin/cagent run <config.yaml> --tui=false` - Run in CLI mode
 - `./bin/cagent run <config.yaml> -a <agent_name>` - Run specific agent
-- `./bin/cagent init` - Initialize new project
+- `./bin/cagent exec <config.yaml>` - Execute agent without TUI
 
 ### Single Test Execution
 
@@ -35,14 +38,6 @@ cagent is a multi-agent AI system with hierarchical agent structure and pluggabl
 
 ### Core Components
 
-#### ServiceCore Layer (`pkg/servicecore/`)
-
-- **Multi-tenant architecture**: Client-isolated operations ensuring security between different users
-- **Transport-agnostic design**: Core business logic independent of MCP/HTTP transport specifics
-- **Agent resolution**: File-based and Docker store-based agent discovery with explicit reference formatting
-- **Session management**: Per-client session lifecycle with proper resource cleanup
-- **Security-first design**: All operations require client ID scoping, preventing cross-client data access
-
 #### Agent System (`pkg/agent/`)
 
 - **Agent struct**: Core abstraction with name, description, instruction, toolsets, models, and sub-agents
@@ -56,27 +51,21 @@ cagent is a multi-agent AI system with hierarchical agent structure and pluggabl
 - **Tool execution**: Handles tool calls and coordinates between agents and external tools
 - **Session management**: Maintains conversation state and message history
 - **Task delegation**: Routes tasks between agents using transfer_task tool
+- **Remote runtime support**: Can connect to remote runtime servers
 
 #### Configuration System (`pkg/config/`)
 
 - **YAML-based configuration**: Declarative agent, model, and tool definitions
-- **Agent properties**: name, model, description, instruction, sub_agents, toolsets, think, todo, memory, add_date, add_environment_info
-- **Model providers**: openai, anthropic, dmr with configurable parameters
-- **Tool configuration**: MCP tools (local stdio and remote), builtin tools (filesystem, shell)
+- **Agent properties**: name, model, description, instruction, sub_agents, toolsets, add_date, add_environment_info, code_mode_tools, max_iterations, num_history_items
+- **Model providers**: openai, anthropic, gemini, dmr with configurable parameters
+- **Tool configuration**: MCP tools (local stdio and remote), builtin tools (filesystem, shell, think, todo, memory, etc.)
 
 #### Command Layer (`cmd/root/`)
 
-- **Multiple interfaces**: CLI (`run.go`), TUI (`tui.go`), API (`api.go`)
-- **Interactive commands**: `/exit`, `/reset`, `/eval` during sessions
+- **Multiple interfaces**: CLI (`run.go`), TUI (default for `run` command), API (`api.go`)
+- **Interactive commands**: `/exit`, `/reset`, `/eval`, `/usage`, `/compact` during sessions
 - **Debug support**: `--debug` flag for detailed logging
-- **MCP server mode**: SSE-based transport for external MCP clients like Claude Code
-
-#### MCP Server (`pkg/mcpserver/`)
-
-- **Protocol compliance**: Full MCP specification implementation with SSE transport
-- **Tool handlers**: Agent listing, invocation, session management, and Docker image operations
-- **Client isolation**: Per-client contexts preventing cross-client interference
-- **Structured responses**: Explicit agent_ref formatting for file vs store-based agents
+- **Gateway mode**: SSE-based transport for external MCP clients like Claude Code
 
 ### Tool System (`pkg/tools/`)
 
@@ -88,21 +77,26 @@ cagent is a multi-agent AI system with hierarchical agent structure and pluggabl
 - **transfer_task**: Agent-to-agent task delegation
 - **filesystem**: File operations
 - **shell**: Command execution
+- **script**: Custom shell scripts
+- **fetch**: HTTP requests
 
 #### MCP Integration
 
 - **Local MCP servers**: stdio-based tools via command execution
 - **Remote MCP servers**: SSE/streamable transport for remote tools
+- **Docker-based MCP**: Reference MCP servers from Docker images (e.g., `docker:github-official`)
 - **Tool filtering**: Optional tool whitelisting per agent
 
 ### Key Patterns
 
 #### Agent Configuration
 
 ```yaml
+version: "2"
+
 agents:
   root:
-    model: model_ref
+    model: model_ref  # Can be inline like "openai/gpt-4o" or reference defined models
     description: purpose
     instruction: detailed_behavior
     sub_agents: [list]
@@ -111,8 +105,14 @@ agents:
       - type: think
       - type: todo
       - type: memory
-        path: { path: string }
+        path: ./path/to/db
       - ...
+
+models:
+  model_ref:
+    provider: anthropic
+    model: claude-sonnet-4-0
+    max_tokens: 64000
 ```
 
 #### Task Delegation Flow
@@ -140,7 +140,7 @@ agents:
 ### Configuration Validation
 
 - All agent references must exist in config
-- Model references must be defined
+- Model references can be inline (e.g., `openai/gpt-4o`) or defined in models section
 - Tool configurations validated at startup
 
 ### Adding New Features
@@ -150,30 +150,10 @@ agents:
 - Add configuration support if needed
 - Consider both CLI and TUI interface impacts, along with API server impacts
 
-### Key Patterns
-
-#### Agent Reference Formatting
-
-- **File agents**: Use relative path from agents directory (e.g., `agent.yaml`)
-- **Store agents**: Use full Docker image reference with tag (e.g., `user/agent:latest`)
-- **Explicit agent_ref field**: MCP responses include unambiguous agent reference for tool calls
-
-#### MCP vs HTTP API
-
-- **MCP Server**: Designed for multi-tenant with client isolation, secure by design, recommended for external integrations
-- **HTTP API**: Legacy single-tenant mode, no client isolation, used for backward compatibility
-- **ServiceCore abstraction**: Shared business logic between both transport layers
-
-#### Current Multi-Tenant Limitation
-
-- **ServiceCore layer**: Fully supports multi-tenant operation with client isolation
-- **MCP implementation**: Client ID extraction from MCP context is not yet implemented
-- **Current behavior**: All MCP clients use `DEFAULT_CLIENT_ID` ("\_\_global"), making them effectively share sessions
-- **Impact**: Multiple MCP clients can see and interact with each other's agent sessions
-- **Recommendation**: Use single MCP client per cagent instance until full multi-tenant support is implemented
-
 ## Model Provider Configuration Examples
 
+Models can be referenced inline (e.g., `openai/gpt-4o`) or defined explicitly:
+
 ### OpenAI
 
 ```yaml
@@ -205,6 +185,15 @@ models:
     temperature: 0.5
 ```
 
+### DMR
+
+```yaml
+models:
+  dmr:
+    provider: dmr
+    model: ai/llama3.2
+```
+
 ## Tool Configuration Examples
 
 ### Local MCP Server (stdio)
@@ -216,7 +205,7 @@ toolsets:
     args: ["-m", "mcp_server"]
     tools: ["specific_tool"] # optional filtering
     env:
-      - "API_KEY=value"
+      API_KEY: "value"
 ```
 
 ### Remote MCP Server (SSE)
@@ -231,6 +220,16 @@ toolsets:
         Authorization: "Bearer token"
 ```
 
+### Docker-based MCP Server
+
+```yaml
+toolsets:
+  - type: mcp
+    ref: docker:github-official
+    instruction: |
+      Use these tools to help with GitHub tasks.
+```
+
 ### Memory Tool with Custom Path
 
 ```yaml
@@ -239,75 +238,104 @@ toolsets:
     path: "./agent_memory.db"
 ```
 
+### Shell Tool
+
+```yaml
+toolsets:
+  - type: shell
+```
+
+### Filesystem Tool
+
+```yaml
+toolsets:
+  - type: filesystem
+```
+
 ## Common Development Patterns
 
 ### Agent Hierarchy Example
 
 ```yaml
+version: "2"
+
 agents:
   root:
-    model: claude
+    model: anthropic/claude-sonnet-4-0
     description: "Main coordinator"
     sub_agents: ["researcher", "writer"]
     toolsets:
       - type: transfer_task
       - type: think
 
   researcher:
-    model: gpt4
+    model: openai/gpt-4o
     description: "Research specialist"
     toolsets:
       - type: mcp
-        command: "web_search_tool"
+        ref: docker:search-tools
 
   writer:
-    model: claude
+    model: anthropic/claude-sonnet-4-0
     description: "Writing specialist"
     toolsets:
       - type: filesystem
       - type: memory
+        path: ./writer_memory.db
 ```
 
 ### Session Commands During CLI Usage
 
 - `/exit` - End the session
 - `/reset` - Clear session history
-- `/eval <expression>` - Evaluate expression (debug mode)
+- `/usage` - Show token usage statistics
+- `/compact` - Generate summary and compact session history
+- `/eval` - Save evaluation data
 
 ## File Locations and Patterns
 
 ### Key Package Structure
 
-- `pkg/servicecore/` - Multi-tenant business logic layer
 - `pkg/agent/` - Core agent abstraction and management
 - `pkg/runtime/` - Event-driven execution engine
 - `pkg/tools/` - Built-in and MCP tool implementations
 - `pkg/model/provider/` - AI provider implementations
 - `pkg/session/` - Conversation state management
 - `pkg/config/` - YAML configuration parsing and validation
-- `pkg/mcpserver/` - MCP protocol server implementation
+- `pkg/gateway/` - MCP gateway/server implementation
+- `pkg/tui/` - Terminal User Interface components
+- `pkg/api/` - API server implementation
 
 ### Configuration File Locations
 
-- `examples/config/` - Sample agent configurations
+- `examples/` - Sample agent configurations
 - Root directory - Main project configurations (`Taskfile.yml`, `go.mod`)
 
 ### Environment Variables
 
 - `OPENAI_API_KEY` - OpenAI authentication
 - `ANTHROPIC_API_KEY` - Anthropic authentication
 - `GOOGLE_API_KEY` - Google/Gemini authentication
-- `MCP_SSE_ENDPOINT` - Override MCP test endpoint
+- `TELEMETRY_ENABLED` - Control telemetry (set to false to disable)
+- `CAGENT_HIDE_TELEMETRY_BANNER` - Hide telemetry banner message
+- `CAGENT_HIDE_FEEDBACK_LINK` - Hide feedback link
 
 ## Debugging and Troubleshooting
 
 ### Debug Mode
 
 - Add `--debug` flag to any command for detailed logging
+- Logs written to `~/.cagent/cagent.debug.log` by default
+- Use `--log-file <path>` to specify custom log location
 - Example: `./bin/cagent run config.yaml --debug`
 
+### OpenTelemetry Tracing
+
+- Add `--otel` flag to enable OpenTelemetry tracing
+- Example: `./bin/cagent run config.yaml --otel`
+
 ### Common Issues
 
 - **Agent not found**: Check agent name matches config file agent definitions
 - **Tool startup failures**: Verify MCP tool commands and dependencies are available
-- **Multi-tenant sessions**: Remember all MCP clients currently share sessions
+- **Model not found**: Ensure model is defined in config or use inline format (provider/model)
PATCH

echo "Gold patch applied."
