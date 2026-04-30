#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cursorless

# Idempotency guard
if grep -qF "- For versatile actions like `drink`, `pour`, `drop`, `float`, and `puff`, expla" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,5 +1,49 @@
 # AGENTS.md
 
+## Documentation Structure
+
+- Main documentation is in `/packages/cursorless-org-docs/src/docs/user/README.md`
+- Spoken forms are defined in `/cursorless-talon/src/spoken_forms.json`
+- Contributing documentation is in `/packages/cursorless-org-docs/src/docs/contributing/`
+
+## Project Organization
+
+- Main extension code is in `/packages/cursorless-vscode/`
+- Engine code is in `/packages/cursorless-engine/`
+- Tests are in `data/fixtures/recorded/`
+- Language-specific parsing is defined in the `queries/*.scm` files
+
+## Build and Test
+
+- Always run lint and typecheck when making changes:
+  - `pnpm run lint`
+  - `pnpm run typecheck`
+- Tests can be run with:
+  - `pnpm test`
+
+## Documentation Conventions
+
+When documenting actions or modifiers:
+
+- Include a brief description of what the item does
+- Include the format/syntax
+- Include at least one example
+- For versatile actions like `drink`, `pour`, `drop`, `float`, and `puff`, explain their behavior with different scope types
+- Always document special behaviors with different scope types
+
+## Implementation Notes
+
+- Many actions (`drop`, `float`, `puff`) work with both line and non-line targets
+- Always check test fixtures in `/data/fixtures/recorded/` to understand behavior
+- Implementation for many actions is in `/packages/cursorless-engine/src/actions/`
+
 ## Scope test format
 
 When writing or updating `.scope` files please follow the guidelines in [scope-test-format.md](./packages/cursorless-org-docs/src/docs/contributing/scope-test-format.md)
+
+## Pull Request Guidelines
+
+- Any feedback should be addressed in code or replied to
+- Tests should be included for new functionality
+- Documentation should be updated to reflect changes
+- Make sure changes are consistent with the project architecture
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,47 +0,0 @@
-# Claude Helpers for Cursorless
-
-This file contains helpful hints for Claude when working with the Cursorless codebase.
-
-## Documentation Structure
-
-- Main documentation is in `/packages/cursorless-org-docs/src/docs/user/README.md`
-- Spoken forms are defined in `/cursorless-talon/src/spoken_forms.json`
-- Contributing documentation is in `/packages/cursorless-org-docs/src/docs/contributing/`
-
-## Project Organization
-
-- Main extension code is in `/packages/cursorless-vscode/`
-- Engine code is in `/packages/cursorless-engine/`
-- Tests are in `data/fixtures/recorded/`
-- Language-specific parsing is defined in the `queries/*.scm` files
-
-## Build and Test
-
-- Always run lint and typecheck when making changes:
-  - `pnpm run lint`
-  - `pnpm run typecheck`
-- Tests can be run with:
-  - `pnpm test`
-
-## Documentation Conventions
-
-When documenting actions or modifiers:
-
-- Include a brief description of what the item does
-- Include the format/syntax
-- Include at least one example
-- For versatile actions like `drink`, `pour`, `drop`, `float`, and `puff`, explain their behavior with different scope types
-- Always document special behaviors with different scope types
-
-## Implementation Notes
-
-- Many actions (`drop`, `float`, `puff`) work with both line and non-line targets
-- Always check test fixtures in `/data/fixtures/recorded/` to understand behavior
-- Implementation for many actions is in `/packages/cursorless-engine/src/actions/`
-
-## Pull Request Guidelines
-
-- Any feedback should be addressed in code or replied to
-- Tests should be included for new functionality
-- Documentation should be updated to reflect changes
-- Make sure changes are consistent with the project architecture
PATCH

echo "Gold patch applied."
