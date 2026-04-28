#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruby-sdk

# Idempotency guard
if grep -qF ".cursor/rules/release-changelogs.mdc" ".cursor/rules/release-changelogs.mdc" && grep -qF "This is the official Ruby SDK for the Model Context Protocol (MCP), implementing" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/release-changelogs.mdc b/.cursor/rules/release-changelogs.mdc
@@ -1,17 +0,0 @@
----
-description: Updating CHANGELOG.md before cutting a new release of the gem
-globs: CHANGELOG.md
-alwaysApply: false
----
-
-- start by refreshing your knowledge on the Keep a Changelog convention by reading the format spec referenced at the top of CHANGELOG.md
-- stick to Keep a Changelog
-- entries should be terse and in a top-level flat list: do not nest
-- follow this format for entries:
-  - Terse description of the change (#nnn)
-- git tags are used to mark the commit that cut a new release of the gem
-- the gem version is located in [version.rb](mdc:lib/mcp/version.rb)
-- use the git history, especially merge commits from PRs to construct the changelog
-- when necessary, look at the diff of files changed to determine the true nature of the change
-- maintenance PRs that don't concern end users of the gem should not be listed in the changelog
-- when checking PRs, see if there's an upstream remote, and if so, fetch PRs from upstream instead of origin
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,119 @@
+# AGENTS.md
+
+## Project overview
+
+This is the official Ruby SDK for the Model Context Protocol (MCP), implementing both server and client functionality for JSON-RPC 2.0 based communication between LLM applications and context providers.
+
+## Dev environment setup
+
+- Ruby 3.2.0+ required
+- Run `bundle install` to install dependencies
+- Dependencies: `json_rpc_handler` ~> 0.1, `json-schema` >= 4.1
+
+## Build and test commands
+
+- `bundle install` - Install dependencies
+- `rake test` - Run all tests
+- `rake rubocop` - Run linter
+- `rake` - Run tests and linting (default task)
+- `ruby -I lib -I test test/path/to/specific_test.rb` - Run single test file
+- `gem build mcp.gemspec` - Build the gem
+
+## Testing instructions
+
+- Test files are in `test/` directory with `_test.rb` suffix
+- Run full test suite with `rake test`
+- Run individual tests with `ruby -I lib -I test test/path/to/file_test.rb`
+- Tests should pass before submitting PRs
+
+## Code style guidelines
+
+- Follow RuboCop rules (run `rake rubocop`)
+- Use frozen string literals
+- Follow Ruby community conventions
+- Keep dependencies minimal
+
+## Commit message conventions
+
+- Use conventional commit format when possible
+- Include clear, descriptive commit messages
+- Releases are triggered by updating version in `lib/mcp/version.rb` and merging to main
+
+## Release process
+
+- Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format in CHANGELOG.md
+- Update CHANGELOG.md before cutting releases
+- Use git history and PR merge commits to construct changelog entries
+- Format entries as: "Terse description of the change (#nnn)"
+- Keep entries in flat list format (no nesting)
+- Git tags mark commits that cut new releases
+- Exclude maintenance PRs that don't concern end users
+- Check upstream remote for PRs if available
+
+## Architecture overview
+
+### Core Components
+
+**MCP::Server** (`lib/mcp/server.rb`):
+
+- Main server class handling JSON-RPC requests
+- Implements MCP protocol methods: initialize, ping, tools/list, tools/call, prompts/list, prompts/get, resources/list, resources/read
+- Supports custom method registration via `define_custom_method`
+- Handles instrumentation, exception reporting, and notifications
+- Uses JsonRpcHandler for request processing
+
+**MCP::Client** (`lib/mcp/client.rb`):
+
+- Client interface for communicating with MCP servers
+- Transport-agnostic design with pluggable transport layers
+- Supports tool listing and invocation
+
+**Transport Layer**:
+
+- `MCP::Server::Transports::StdioTransport` - Command-line stdio transport
+- `MCP::Server::Transports::StreamableHttpTransport` - HTTP with streaming support
+- `MCP::Client::HTTP` - HTTP client transport (requires faraday gem)
+
+**Protocol Components**:
+
+- `MCP::Tool` - Tool definition with input/output schemas and annotations
+- `MCP::Prompt` - Prompt templates with argument validation
+- `MCP::Resource` - Resource registration and retrieval
+- `MCP::Configuration` - Global configuration with exception reporting and instrumentation
+
+### Key Patterns
+
+**Three Ways to Define Components**:
+
+1. Class inheritance (e.g., `class MyTool < MCP::Tool`)
+2. Define methods (e.g., `MCP::Tool.define(name: "my_tool") { ... }`)
+3. Server registration (e.g., `server.define_tool(name: "my_tool") { ... }`)
+
+**Schema Validation**:
+
+- Tools support input_schema and output_schema for JSON Schema validation
+- Protocol version 2025-03-26+ supports tool annotations (destructive_hint, idempotent_hint, etc.)
+- Validation is configurable via `configuration.validate_tool_call_arguments`
+
+**Context Passing**:
+
+- `server_context` hash passed through tool/prompt calls for request-specific data
+- Methods can accept `server_context:` keyword argument for accessing context
+
+### Dependencies
+
+- `json_rpc_handler` ~> 0.1 - JSON-RPC 2.0 message handling
+- `json-schema` >= 4.1 - Schema validation
+- Ruby 3.2.0+ required
+
+### Integration patterns
+
+- **Rails controllers**: Use `server.handle_json(request.body.read)` for HTTP endpoints
+- **Command-line tools**: Use `StdioTransport.new(server).open` for CLI applications
+- **HTTP services**: Use `StreamableHttpTransport` for web-based servers
+
+### Component definition patterns
+
+1. **Class inheritance**: `class MyTool < MCP::Tool`
+2. **Define methods**: `MCP::Tool.define(name: "my_tool") { ... }`
+3. **Server registration**: `server.define_tool(name: "my_tool") { ... }`
\ No newline at end of file
PATCH

echo "Gold patch applied."
