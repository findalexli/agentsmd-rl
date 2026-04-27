#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-action

# Idempotency guard
if grep -qF "This is a GitHub Action that enables Claude to interact with GitHub PRs and issu" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,10 +1,11 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code when working with code in this repository.
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
 
 ## Development Tools
 
 - Runtime: Bun 1.2.11
+- TypeScript with strict configuration
 
 ## Common Development Tasks
 
@@ -17,42 +18,119 @@ bun test
 # Formatting
 bun run format          # Format code with prettier
 bun run format:check    # Check code formatting
+
+# Type checking
+bun run typecheck       # Run TypeScript type checker
 ```
 
 ## Architecture Overview
 
-This is a GitHub Action that enables Claude to interact with GitHub PRs and issues. The action:
+This is a GitHub Action that enables Claude to interact with GitHub PRs and issues. The action operates in two main phases:
+
+### Phase 1: Preparation (`src/entrypoints/prepare.ts`)
+
+1. **Authentication Setup**: Establishes GitHub token via OIDC or GitHub App
+2. **Permission Validation**: Verifies actor has write permissions
+3. **Trigger Detection**: Uses mode-specific logic to determine if Claude should respond
+4. **Context Creation**: Prepares GitHub context and initial tracking comment
+
+### Phase 2: Execution (`base-action/`)
+
+The `base-action/` directory contains the core Claude Code execution logic, which serves a dual purpose:
+
+- **Standalone Action**: Published separately as `@anthropic-ai/claude-code-base-action` for direct use
+- **Inner Logic**: Used internally by this GitHub Action after preparation phase completes
+
+Execution steps:
+
+1. **MCP Server Setup**: Installs and configures GitHub MCP server for tool access
+2. **Prompt Generation**: Creates context-rich prompts from GitHub data
+3. **Claude Integration**: Executes via multiple providers (Anthropic API, AWS Bedrock, Google Vertex AI)
+4. **Result Processing**: Updates comments and creates branches/PRs as needed
+
+### Key Architectural Components
+
+#### Mode System (`src/modes/`)
+
+- **Tag Mode** (`tag/`): Responds to `@claude` mentions and issue assignments
+- **Agent Mode** (`agent/`): Automated execution without trigger checking
+- Extensible registry pattern in `modes/registry.ts`
+
+#### GitHub Integration (`src/github/`)
 
-1. **Trigger Detection**: Uses `check-trigger.ts` to determine if Claude should respond based on comment/issue content
-2. **Context Gathering**: Fetches GitHub data (PRs, issues, comments) via `github-data-fetcher.ts` and formats it using `github-data-formatter.ts`
-3. **AI Integration**: Supports multiple Claude providers (Anthropic API, AWS Bedrock, Google Vertex AI)
-4. **Prompt Creation**: Generates context-rich prompts using `create-prompt.ts`
-5. **MCP Server Integration**: Installs and configures GitHub MCP server for extended functionality
+- **Context Parsing** (`context.ts`): Unified GitHub event handling
+- **Data Fetching** (`data/fetcher.ts`): Retrieves PR/issue data via GraphQL/REST
+- **Data Formatting** (`data/formatter.ts`): Converts GitHub data to Claude-readable format
+- **Branch Operations** (`operations/branch.ts`): Handles branch creation and cleanup
+- **Comment Management** (`operations/comments/`): Creates and updates tracking comments
 
-### Key Components
+#### MCP Server Integration (`src/mcp/`)
 
-- **Trigger System**: Responds to `/claude` comments or issue assignments
-- **Authentication**: OIDC-based token exchange for secure GitHub interactions
-- **Cloud Integration**: Supports direct Anthropic API, AWS Bedrock, and Google Vertex AI
-- **GitHub Operations**: Creates branches, posts comments, and manages PRs/issues
+- **GitHub Actions Server** (`github-actions-server.ts`): Workflow and CI access
+- **GitHub Comment Server** (`github-comment-server.ts`): Comment operations
+- **GitHub File Operations** (`github-file-ops-server.ts`): File system access
+- Auto-installation and configuration in `install-mcp-server.ts`
+
+#### Authentication & Security (`src/github/`)
+
+- **Token Management** (`token.ts`): OIDC token exchange and GitHub App authentication
+- **Permission Validation** (`validation/permissions.ts`): Write access verification
+- **Actor Validation** (`validation/actor.ts`): Human vs bot detection
 
 ### Project Structure
 
 ```
 src/
-├── check-trigger.ts        # Determines if Claude should respond
-├── create-prompt.ts        # Generates contextual prompts
-├── github-data-fetcher.ts  # Retrieves GitHub data
-├── github-data-formatter.ts # Formats GitHub data for prompts
-├── install-mcp-server.ts  # Sets up GitHub MCP server
-├── update-comment-with-link.ts # Updates comments with job links
-└── types/
-    └── github.ts          # TypeScript types for GitHub data
+├── entrypoints/           # Action entry points
+│   ├── prepare.ts         # Main preparation logic
+│   ├── update-comment-link.ts  # Post-execution comment updates
+│   └── format-turns.ts    # Claude conversation formatting
+├── github/               # GitHub integration layer
+│   ├── api/              # REST/GraphQL clients
+│   ├── data/             # Data fetching and formatting
+│   ├── operations/       # Branch, comment, git operations
+│   ├── validation/       # Permission and trigger validation
+│   └── utils/            # Image downloading, sanitization
+├── modes/                # Execution modes
+│   ├── tag/              # @claude mention mode
+│   ├── agent/            # Automation mode
+│   └── registry.ts       # Mode selection logic
+├── mcp/                  # MCP server implementations
+├── prepare/              # Preparation orchestration
+└── utils/                # Shared utilities
 ```
 
-## Important Notes
+## Important Implementation Notes
+
+### Authentication Flow
+
+- Uses GitHub OIDC token exchange for secure authentication
+- Supports custom GitHub Apps via `APP_ID` and `APP_PRIVATE_KEY`
+- Falls back to official Claude GitHub App if no custom app provided
+
+### MCP Server Architecture
+
+- Each MCP server has specific GitHub API access patterns
+- Servers are auto-installed in `~/.claude/mcp/github-{type}-server/`
+- Configuration merged with user-provided MCP config via `mcp_config` input
+
+### Mode System Design
+
+- Modes implement `Mode` interface with `shouldTrigger()` and `prepare()` methods
+- Registry validates mode compatibility with GitHub event types
+- Agent mode bypasses all trigger checking for automation scenarios
+
+### Comment Threading
+
+- Single tracking comment updated throughout execution
+- Progress indicated via dynamic checkboxes
+- Links to job runs and created branches/PRs
+- Sticky comment option for consolidated PR comments
+
+## Code Conventions
 
-- Actions are triggered by `@claude` comments or issue assignment unless a different trigger_phrase is specified
-- The action creates branches for issues and pushes to PR branches directly
-- All actions create OIDC tokens for secure authentication
-- Progress is tracked through dynamic comment updates with checkboxes
+- Use Bun-specific TypeScript configuration with `moduleResolution: "bundler"`
+- Strict TypeScript with `noUnusedLocals` and `noUnusedParameters` enabled
+- Prefer explicit error handling with detailed error messages
+- Use discriminated unions for GitHub context types
+- Implement retry logic for GitHub API operations via `utils/retry.ts`
PATCH

echo "Gold patch applied."
