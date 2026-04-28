#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wp-calypso

# Idempotency guard
if grep -qF "- **Image Studio** (`packages/image-studio`) \u2014 AI-powered image editing and gene" "AGENTS.md" && grep -qF "- Dialog buttons on mobile: `.dialog__action-buttons` flips to `flex-direction: " "client/AGENTS.md" && grep -qF "# Image Studio" "packages/image-studio/AGENTS.md" && grep -qF "packages/image-studio/CLAUDE.md" "packages/image-studio/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -22,7 +22,7 @@
 
 ## Packages
 
-- **Image Studio** (`packages/image-studio`) — AI-powered image editing and generation. See `packages/image-studio/AGENTS.md` for architecture, conventions, and manual browser testing steps.
+- **Image Studio** (`packages/image-studio`) — AI-powered image editing and generation
 
 ## Development
 
diff --git a/client/AGENTS.md b/client/AGENTS.md
@@ -1,34 +1,60 @@
 # Calypso Client
 
-React + TypeScript application clients for WordPress.com. For repo-level context, see root `AGENTS.md`.
+React + TypeScript application clients for WordPress.com.
 
-## Project Knowledge
+## Architecture
 
-Two coexisting architectures: Classic (`client/me/`, `client/my-sites/`) uses Redux +
-page.js routing. Dashboard (`client/dashboard/`) uses TanStack Query + TanStack Router.
+Two coexisting architectures:
+
+- Classic Calypso (`client/me/`, `client/my-sites/`) uses Redux + page.js routing.
+- Dashboard (`client/dashboard/`) uses TanStack Query + TanStack Router.
 
 ## Commands
 
 ```bash
-yarn eslint <file>                    # Lint JS/TS/TSX
-yarn eslint --fix <file>              # Lint + fix
-yarn stylelint <file>                 # Lint CSS/SCSS
-yarn prettier --write <file>          # Format
-yarn typecheck-client                 # Type-check (slow)
-yarn test-client <test-file>          # Run specific test
+yarn eslint <file>                          # Lint JS/TS/TSX
+yarn eslint --fix <file>                    # Lint + fix
+yarn stylelint <file>                       # Lint CSS/SCSS
+yarn prettier --write <file>                # Format
+yarn typecheck-client                       # Type-check (slow)
+yarn test-client <file>                     # Run specific test
 yarn test-client --findRelatedTests <file>  # Find + run related tests
 ```
 
 ## Conventions
 
-- Use `import clsx from 'clsx'` — not `classnames`.
-- One empty line between `import './style.scss'` and other imports.
-- Avoid BEM shortcuts (`&--`, `&__`) in SCSS.
+### File structure
+
+- Use kebab-case for directories (e.g., `components/auth-wizard`).
+
+### Imports
+
+- Use `import clsx from 'clsx'`, not `classnames`.
+- Add one empty line between `import './style.scss'` and other imports.
+
+### Types
+
+- Use strict TypeScript. No `any` unless justified.
+- Prefer simple, concrete types over complex generics.
+
+### UI
+
+- Prefer `@wordpress/components` primitives (Button, Modal, Card, etc.).
+- Avoid `__experimental*` components unless already used in the codebase.
+- Prefer `VStack`, `HStack` over `Flex` components.
+- Minimize custom CSS; rely on the design system first.
+
+### CSS/SCSS
+
 - Use CSS logical properties (`margin-inline-start`, not `margin-left`).
-- Prefer `@wordpress/components` over custom UI primitives (Button, Modal, Card, etc.). Avoid `__experimental*` components unless existing usage in codebase.
-- No `any` unless justified — strict TypeScript throughout.
-- kebab-case for directories (e.g., `components/auth-wizard`).
-- `userEvent` over `fireEvent` in tests. `toBeVisible` over `toBeInTheDocument`.
-- Dialog buttons on mobile: `.dialog__action-buttons` flips to
-  `flex-direction: column-reverse` below `$break-mobile`. Flex labels inside
-  buttons need `width: 100%` for `justify-content: center` to work.
+- Do not use BEM shortcuts (`&--`, `&__`) in SCSS.
+- Dialog buttons on mobile: `.dialog__action-buttons` flips to `flex-direction: column-reverse` below `$break-mobile`. Flex labels inside buttons need `width: 100%` for `justify-content: center` to work.
+
+### Internationalization
+
+- Use `@wordpress/i18n` for translations.
+
+### Testing
+
+- Prefer `userEvent` over `fireEvent` in tests.
+- Prefer `toBeVisible()` over `toBeInTheDocument()`.
diff --git a/packages/image-studio/AGENTS.md b/packages/image-studio/AGENTS.md
@@ -1,4 +1,4 @@
-# Image Studio - AGENTS.md
+# Image Studio
 
 ## Package Overview
 
diff --git a/packages/image-studio/CLAUDE.md b/packages/image-studio/CLAUDE.md
@@ -1,3 +1 @@
-# Image Studio - CLAUDE.md
-
 @AGENTS.md
PATCH

echo "Gold patch applied."
