#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcp-use

# Idempotency guard
if grep -qF "**mcp-use** is a full-stack MCP (Model Context Protocol) framework providing cli" "CLAUDE.md" && grep -qF "**IMPORTANT:** Read the root `/CLAUDE.md` first for critical workflow requiremen" "libraries/python/CLAUDE.md" && grep -qF "The TypeScript library is a **pnpm workspace monorepo** containing multiple pack" "libraries/typescript/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,144 @@
+# CLAUDE.md
+
+This is the root configuration for Claude Code in the mcp-use monorepo.
+
+## Project Overview
+
+**mcp-use** is a full-stack MCP (Model Context Protocol) framework providing clients, agents, and servers in both Python and TypeScript. This is a widely-used open-source library.
+
+## Repository Structure
+
+```
+mcp-use/
+├── libraries/
+│   ├── python/      → Python library (PyPI: mcp-use)
+│   └── typescript/  → TypeScript monorepo (npm: mcp-use, @mcp-use/*)
+├── docs/            → Documentation
+└── .github/         → CI/CD workflows
+```
+
+See language-specific CLAUDE.md files in `libraries/python/` and `libraries/typescript/` for detailed guidance.
+
+---
+
+## CRITICAL: Workflow for Non-Trivial Tasks
+
+**YOU MUST follow this workflow for any task beyond simple fixes:**
+
+### 1. Plan Before Implementing
+
+Before writing any code for a non-trivial task:
+- Use plan mode to reason through the approach
+- Identify files that need changes
+- Consider edge cases and potential issues
+- Get explicit user approval before proceeding
+
+### 2. Context Management
+
+When exploring the codebase:
+- Read only files directly relevant to the task
+- Avoid loading entire directories or large numbers of files
+- Use targeted grep/glob searches first
+- Summarize findings rather than dumping file contents
+
+### 3. Breaking Changes & Backward Compatibility
+
+**This is a library used by many people. Breaking changes have real impact.**
+
+Before implementing ANY change that modifies public APIs:
+- Explicitly identify if it's a breaking change
+- Present options to the user in plan mode:
+  - Option A: Breaking change (cleaner, but requires user migration)
+  - Option B: Backward compatible (may add complexity)
+- **DO NOT** automatically add backward compatibility shims, re-exports, or deprecation wrappers
+- Let the user decide - often breaking changes are acceptable and preferred over code duplication
+
+### 4. Implementation Requirements
+
+After plan approval:
+- Write clean, minimal code that solves the problem
+- **Tests are MANDATORY** for new functions/methods/classes
+- Tests must verify actual behavior, not just mock everything
+- Avoid over-engineering - solve the current problem, not hypothetical future ones
+
+### 5. Post-Implementation Checklist
+
+After implementation is complete:
+1. Run the test suite and verify tests pass
+2. Check if documentation needs updates (`docs/`, README files, docstrings)
+3. Check if examples need updates (`examples/` directories)
+4. Prepare a PR description following `.github/pull_request_template.md`
+
+---
+
+## Testing Standards
+
+**Tests are not optional. Fake tests are worse than no tests.**
+
+- Unit tests: Test actual logic, not mocked implementations
+- Integration tests: Test real component interactions
+- If you're mocking everything, you're testing nothing
+- Cover happy paths AND edge cases
+
+---
+
+## PR Description Format
+
+After completing work, provide a PR description following this format:
+
+```markdown
+## Changes
+[Concise description of what changed]
+
+## Implementation Details
+1. [Specific changes made]
+2. [Architectural decisions]
+3. [Dependencies added/modified]
+
+## Example Usage (Before)
+[If applicable]
+
+## Example Usage (After)
+[Show the new usage]
+
+## Documentation Updates
+- [List updated docs]
+
+## Testing
+- [Tests added/modified]
+- [How you verified the changes]
+
+## Backwards Compatibility
+[Is this breaking? What do users need to do?]
+
+## Related Issues
+Closes #[issue_number]
+```
+
+---
+
+## Language-Specific Commands
+
+### Python (`libraries/python/`)
+```bash
+ruff check --fix && ruff format    # Lint and format
+pytest tests/unit                   # Run unit tests
+```
+
+### TypeScript (`libraries/typescript/`)
+```bash
+pnpm build                          # Build all packages
+pnpm test                           # Run tests
+pnpm changeset                      # Create changeset for PR
+```
+
+---
+
+## What NOT to Do
+
+- Don't implement features without explicit approval
+- Don't add backward compatibility code without asking first
+- Don't create tests that only test mocks
+- Don't skip documentation updates
+- Don't make sweeping refactors alongside feature work
+- Don't guess at requirements - ask for clarification
diff --git a/libraries/python/CLAUDE.md b/libraries/python/CLAUDE.md
@@ -1,6 +1,10 @@
-# CLAUDE.md
+# CLAUDE.md - Python Library
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+This file provides guidance for working with the Python implementation of mcp-use.
+
+**IMPORTANT:** Read the root `/CLAUDE.md` first for critical workflow requirements around planning, breaking changes, and testing standards.
+
+---
 
 ## Project Overview
 
@@ -176,19 +180,31 @@ export MCP_USE_DEBUG=2
 
 ## Testing Strategy
 
+**Tests are MANDATORY for new functionality. See root CLAUDE.md for standards.**
+
 ### Unit Tests (`tests/unit/`)
 
 - Test individual components in isolation
-- Mock external dependencies
+- Mock only external dependencies (network, file I/O), NOT internal logic
 - Focus on business logic and edge cases
+- **DO NOT** create tests that only verify mocks were called
 
 ### Integration Tests (`tests/integration/`)
 
-- Test component interactions
-- Include real MCP server integrations
-- Organized by transport type (stdio, sse, websocket, etc.)
+- Test component interactions with real MCP servers
+- Organized by category:
+  - `client/transports/` - stdio, sse, streamable_http
+  - `client/primitives/` - tools, resources, prompts
+  - `agent/` - Full agent workflows (require API keys)
 - Custom test servers in `tests/integration/servers_for_testing/`
 
+### Test Requirements
+
+- Every new public method/function needs tests
+- Test both success cases AND error handling
+- Integration tests preferred over heavily mocked unit tests
+- If you mock everything, you're testing nothing
+
 ### Test Configuration
 
 - Uses pytest with asyncio mode
@@ -226,3 +242,13 @@ export MCP_USE_DEBUG=2
 1. Create test server in `tests/integration/servers_for_testing/`
 2. Add integration test in appropriate transport directory
 3. Use custom servers for controlled testing scenarios
+
+## Post-Implementation Checklist
+
+After completing any feature or fix:
+
+1. **Tests pass**: `pytest tests/unit` (and integration if applicable)
+2. **Linting passes**: `ruff check && ruff format --check`
+3. **Documentation updated**: Check `docs/`, README, docstrings
+4. **Examples updated**: Check `examples/` directory if API changed
+5. **PR description ready**: Follow `.github/pull_request_template.md`
diff --git a/libraries/typescript/CLAUDE.md b/libraries/typescript/CLAUDE.md
@@ -0,0 +1,172 @@
+# CLAUDE.md - TypeScript Library
+
+This file provides guidance for working with the TypeScript implementation of mcp-use.
+
+## Overview
+
+The TypeScript library is a **pnpm workspace monorepo** containing multiple packages for MCP clients, agents, servers, and tooling.
+
+## Package Structure
+
+```
+libraries/typescript/
+├── packages/
+│   ├── mcp-use/           → Core framework (npm: mcp-use)
+│   ├── cli/               → Build tools (npm: @mcp-use/cli)
+│   ├── inspector/         → Web debugger (npm: @mcp-use/inspector)
+│   └── create-mcp-use-app/→ Scaffolding CLI
+├── package.json           → Root workspace config
+└── pnpm-workspace.yaml    → Workspace definition
+```
+
+## Development Commands
+
+```bash
+# Install all dependencies
+pnpm install
+
+# Build all packages (respects dependency order)
+pnpm build
+
+# Build specific package
+pnpm --filter mcp-use build
+pnpm --filter @mcp-use/cli build
+
+# Run all tests
+pnpm test
+
+# Run tests for specific package
+pnpm --filter mcp-use test
+pnpm --filter mcp-use test:unit
+pnpm --filter mcp-use test:integration:agent  # Requires OPENAI_API_KEY
+
+# Linting and formatting
+pnpm lint
+pnpm lint:fix
+pnpm format
+pnpm format:check
+```
+
+## Changesets (Required for PRs)
+
+**All changes require a changeset.** This is enforced in CI.
+
+```bash
+pnpm changeset
+```
+
+Select affected packages, choose semver bump (patch/minor/major), write summary.
+
+## Architecture
+
+### Core Package (`packages/mcp-use/`)
+
+**MCPClient** (`src/client/`)
+- Manages MCP server connections
+- Handles configuration from files or objects
+- Supports multiple concurrent server sessions
+
+**MCPAgent** (`src/agent/`)
+- High-level AI agent using LangChain
+- Integrates LLMs with MCP tools
+- Supports streaming and conversation memory
+
+**MCPServer** (`src/server/`)
+- Framework for building MCP servers
+- Declarative tool/resource/prompt definitions
+- Built-in inspector integration
+
+### Key Patterns
+
+- **TypeScript Strict Mode**: All code uses strict typing
+- **Async/Await**: All I/O is asynchronous
+- **Zod Validation**: Schema validation for tool inputs
+- **Workspace Dependencies**: Use `workspace:*` for internal deps
+
+## Code Style
+
+- ESLint + Prettier (auto-run via Husky pre-commit)
+- Explicit types required (avoid `any`)
+- Use interfaces for object shapes
+- Prefer `const` over `let`
+- Async/await over raw promises
+
+## Testing Guidelines
+
+### Test Location
+- Unit tests: `packages/*/src/**/*.test.ts`
+- Integration tests: `packages/*/tests/`
+
+### Test Requirements
+- Test real behavior, not mocked implementations
+- Cover error cases and edge conditions
+- Integration tests should use actual MCP servers where possible
+- Mock only external dependencies (network, file system) when necessary
+
+### Running Tests
+```bash
+# All tests
+pnpm test
+
+# Unit tests only
+pnpm --filter mcp-use test:unit
+
+# Watch mode during development
+pnpm --filter mcp-use test:watch
+```
+
+## Common Tasks
+
+### Adding a New Tool to MCPServer
+
+1. Define tool in server setup with Zod schema
+2. Implement handler function
+3. Add unit tests for the handler
+4. Add integration test with real server
+5. Update documentation if public API
+
+### Adding Client Features
+
+1. Modify relevant class in `packages/mcp-use/src/client/`
+2. Update TypeScript interfaces as needed
+3. Add tests covering new functionality
+4. Run full test suite before PR
+
+### Working with Multiple Packages
+
+When changes span packages:
+```bash
+# Build in correct order
+pnpm build
+
+# Test affected packages
+pnpm --filter mcp-use test
+pnpm --filter @mcp-use/cli test
+```
+
+## Pre-commit Hooks
+
+Husky + lint-staged runs automatically on commit:
+- Prettier formatting
+- ESLint checks
+
+If hooks fail, fix issues before committing.
+
+## Post-Implementation Checklist
+
+After completing any feature or fix:
+
+1. **Build succeeds**: `pnpm build`
+2. **Tests pass**: `pnpm test`
+3. **Linting passes**: `pnpm lint && pnpm format:check`
+4. **Changeset created**: `pnpm changeset`
+5. **Documentation updated**: Check README files, JSDoc comments
+6. **Examples updated**: Check `examples/` if API changed
+7. **PR description ready**: Follow `.github/pull_request_template.md`
+
+## Important Notes
+
+- Node.js 20+ required (22 recommended)
+- pnpm 10+ required
+- Always run `pnpm build` after pulling changes
+- Changeset required for all PRs to main
PATCH

echo "Gold patch applied."
