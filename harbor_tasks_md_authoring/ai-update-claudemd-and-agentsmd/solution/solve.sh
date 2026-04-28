#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai

# Idempotency guard
if grep -qF "Each core component has bridges in `src/<component>/src/Bridge/` that provide in" "AGENTS.md" && grep -qF "Each core component has bridges in `src/<component>/src/Bridge/` that provide in" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -12,6 +12,10 @@ Symfony AI monorepo with independent packages for AI integration in PHP applicat
 - **Platform** (`src/platform/`): Unified AI platform interface (OpenAI, Anthropic, Azure, Gemini, VertexAI)
 - **Agent** (`src/agent/`): AI agent framework for user interaction and task execution
 - **Store** (`src/store/`): Data storage abstraction with vector database support
+- **Mate** (`src/mate/`): AI-powered coding assistant for PHP development
+
+### Bridges
+Each core component has bridges in `src/<component>/src/Bridge/` that provide integrations with specific third-party services. Bridges are separate Composer packages with their own dependencies and can be installed independently.
 
 ### Integration Bundles
 - **AI Bundle** (`src/ai-bundle/`): Symfony integration for Platform, Store, and Agent
@@ -89,7 +93,19 @@ cd demo && symfony server:start
 ## Development Workflow
 
 1. Each `src/` component is independently versioned
-2. Use `@dev` versions for internal dependencies during development
-3. Run PHP-CS-Fixer after code changes
-4. Test component-specific changes in isolation
-5. Use monorepo structure for shared development workflow
\ No newline at end of file
+2. Run PHP-CS-Fixer after code changes
+3. Test component-specific changes in isolation
+4. Use monorepo structure for shared development workflow
+
+## Version Documentation
+
+### UPGRADE.md
+- Document breaking changes in the root `UPGRADE.md` file
+- Format: Use version headers like `UPGRADE FROM 0.X to 0.Y` with sections per component
+- Include code examples showing before/after changes with diff syntax
+
+### CHANGELOG.md
+- Each component has its own `CHANGELOG.md` in its root directory
+- Add entries for new features, and deprecations under the appropriate version heading
+- Format entries as bullet points starting with "Add", "Fix", "Deprecate", etc.
+
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -12,6 +12,10 @@ This is the Symfony AI monorepo containing multiple components and bundles that
 - **Platform** (`src/platform/`): Unified interface to AI platforms (OpenAI, Anthropic, Azure, Gemini, VertexAI, etc.)
 - **Agent** (`src/agent/`): Framework for building AI agents that interact with users and perform tasks
 - **Store** (`src/store/`): Data storage abstraction with indexing and retrieval for vector databases
+- **Mate** (`src/mate/`): AI-powered coding assistant for PHP development
+
+### Bridges
+Each core component has bridges in `src/<component>/src/Bridge/` that provide integrations with specific third-party services. Bridges are separate Composer packages with their own dependencies and can be installed independently.
 
 ### Integration Bundles
 - **AI Bundle** (`src/ai-bundle/`): Symfony integration for Platform, Store, and Agent components
@@ -105,7 +109,6 @@ Each component uses:
 ## Development Notes
 
 - Each component in `src/` is a separate Composer package with its own dependencies
-- Use `@dev` versions for internal component dependencies during development
 - Components follow Symfony coding standards and use `@Symfony` PHP CS Fixer rules
 - The monorepo structure allows independent versioning while maintaining shared development workflow
 - Do not use void return type for testcase methods
@@ -118,3 +121,16 @@ Each component uses:
 - Define array shapes for parameters and return types
 - Use project specific exceptions instead of global exception classes like \RuntimeException, \InvalidArgumentException etc.
 - NEVER mention Claude as co-author in commits
+
+## Version Documentation
+
+### UPGRADE.md
+- Document breaking changes in the root `UPGRADE.md` file
+- Format: Use version headers like `UPGRADE FROM 0.X to 0.Y` with sections per component
+- Include code examples showing before/after changes with diff syntax
+
+### CHANGELOG.md
+- Each component has its own `CHANGELOG.md` in its root directory
+- Add entries for new features, and deprecations under the appropriate version heading
+- Format entries as bullet points starting with "Add", "Fix", "Deprecate", etc.
+
PATCH

echo "Gold patch applied."
