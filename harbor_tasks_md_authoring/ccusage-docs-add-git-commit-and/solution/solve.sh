#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ccusage

# Idempotency guard
if grep -qF "PR titles should follow the same format as commit messages. When a PR contains m" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -173,6 +173,73 @@ This is a CLI tool that analyzes Claude Code usage data from local JSONL files s
   - **Byethrow MCP**: Access @praha/byethrow documentation and examples for functional error handling
   - **TypeScript MCP (lsmcp)**: Search for TypeScript functions, types, and symbols across the codebase
 
+## Git Commit and PR Conventions
+
+**Commit Message Format:**
+
+Follow the Conventional Commits specification with package/area prefixes:
+
+```
+<type>(<scope>): <subject>
+```
+
+**Scope Naming Rules:**
+
+- **Apps**: Use the app directory name
+  - `feat(ccusage):` - Changes to apps/ccusage
+  - `fix(mcp):` - Fixes in apps/mcp
+  - `feat(codex):` - Features for apps/codex (if exists)
+
+- **Packages**: Use the package directory name
+  - `feat(terminal):` - Changes to packages/terminal
+  - `fix(ui):` - Fixes in packages/ui
+  - `refactor(core):` - Refactoring packages/core
+
+- **Documentation**: Use `docs` scope
+  - `docs:` or `docs(guide):` - Documentation updates
+  - `docs(api):` - API documentation changes
+
+- **Root-level changes**: No scope (preferred) or use `root`
+  - `chore:` - Root config updates
+  - `ci:` - CI/CD changes
+  - `feat:` - Root-level features
+  - `docs:` - Root documentation updates
+  - `build:` or `build(root):` - Root build system changes
+
+**Type Prefixes:**
+
+- `feat:` - New feature
+- `fix:` - Bug fix
+- `docs:` - Documentation only changes
+- `style:` - Code style changes (formatting, missing semi-colons, etc)
+- `refactor:` - Code change that neither fixes a bug nor adds a feature
+- `perf:` - Performance improvements
+- `test:` - Adding missing tests or correcting existing tests
+- `chore:` - Changes to the build process or auxiliary tools
+- `ci:` - CI/CD configuration changes
+- `revert:` - Reverting a previous commit
+
+**Examples:**
+
+```
+feat(ccusage): add support for Claude 4.1 models
+fix(mcp): resolve connection timeout issues
+docs(guide): update installation instructions
+refactor(ccusage): extract cost calculation to separate module
+test(mcp): add integration tests for HTTP transport
+chore: update dependencies
+```
+
+**PR Title Convention:**
+
+PR titles should follow the same format as commit messages. When a PR contains multiple commits, the title should describe the main change:
+
+```
+feat(ccusage): implement session-based usage reports
+fix(mcp): handle edge cases in data aggregation
+docs: comprehensive API documentation update
+```
+
 ## Code Style Notes
 
 - Uses ESLint for linting and formatting with tab indentation and double quotes
PATCH

echo "Gold patch applied."
