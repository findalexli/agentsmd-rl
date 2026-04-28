#!/usr/bin/env bash
set -euo pipefail

cd /workspace/couchers

# Idempotency guard
if grep -qF ".cursorrules" ".cursorrules" && grep -qF "- For dates and times on the web frontend, never use `Date.toLocaleDateString()`" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -1,89 +0,0 @@
-# Couchers Project Rules
-
-This is a monorepo containing:
-- `/app/web` - Next.js web frontend
-- `/app/mobile` - React Native Expo mobile app
-- `/app/backend` - Python backend
-
----
-
-## Web Frontend (`/app/web`)
-
-### Package Manager
-This project uses **yarn** as the package manager. Always use `yarn` commands instead of `npm`:
-- Use `yarn install` instead of `npm install`
-- Use `yarn add` instead of `npm install`
-- Use `yarn test` instead of `npm test`
-- Use `yarn start` instead of `npm start`
-
-### Linting
-- Run linting `yarn lint` to see issues and `yarn lint:fix` to fix them
-
-### Testing
-Run tests with: `yarn test`
-
-#### Testing Best Practices
-- **Use fixture data when available**: Import test data from `test/fixtures/` (e.g., `hostRequest.json`, `messages.json`, `groupChat.json`) instead of creating mock data inline
-- **Query elements by label**: Prefer `getByLabelText()` for form inputs as it tests accessibility
-  - When there's ambiguity (e.g., both a label and aria-label), use the `selector` option: `getByLabelText(label, { selector: "textarea" })`
-- **Text matching with embedded elements**: When text is split by child elements (e.g., links inside text), use function matchers:
-  ```typescript
-  screen.getByText((content, element) => {
-    return element?.textContent === "Full text including embedded link text";
-  })
-  ```
-- **Type safety**: Explicitly type mock mutations (e.g., `UseMutationResult<...>`) without using `any`
-- **Async queries**: Use `await screen.findByText()` when waiting for elements after loading states, instead of `getByText()` after `waitForElementToBeRemoved()`
-
-### Development
-To run the app locally in development, use `yarn start` (not Docker)
-
-### File Imports
-- Use our import aliases, e.g. "components/" instead of "../../../components/" and "routes" instead of "../../../routes"
-- Import multiple MUI icons together: `import { Favorite, Star, Public } from "@mui/icons-material"` instead of separate imports
-
-### Code Style
-- Do not use the `any` type in TypeScript - it's considered bad practice
-- Remove extra unnecessary style declarations, including anything that's already a default of MUI or the theme
-- Use theme-defined colors instead of ad-hoc gray backgrounds
-- Use default Material-UI hover styles instead of custom dark grey on hover
-- Prefer modern 2025 design patterns for UI components
-- Use StyledLink.tsx component or import from next/link for links to preserve routing, NOT MUI Link
-- Always put types at the top of the file below the imports
-- Add Tanstack queryKeys to app/web/features/queryKeys.ts if they are used more than one place.
-- Use slotProps rather than InputLabelProps for MUI. InputLabelProps is deprecated now.
-
-### Internationalization (i18n)
-- **Never hardcode English text** - always use the `t()` function or `<Trans>` component for user-facing text
-- Store all English text strings in the appropriate locale files (`features/*/locales/en.json`)
-- When adding strings to an `en.json` file, refer to `/docs/localization.md` for string key and text guidance
-- Use `<Trans>` component for text with embedded components (like links)
-- When using `<Trans>`, make sure components in the translation JSON match the components prop exactly
-
-### Dark Mode
-- **Always use CSS variables for theme colors** to ensure dark mode compatibility:
-  - Use `"var(--mui-palette-primary-main)"` instead of `theme.palette.primary.main` in styled components
-  - Use `"var(--mui-palette-text-primary)"` for text colors
-  - Use `"var(--mui-palette-background-paper)"` for backgrounds
-  - Use `"var(--mui-palette-background-default)"` for page backgrounds
-  - Use `"var(--mui-palette-divider)"` for borders/dividers
-  - Use `"var(--mui-palette-grey-XXX)"` for grey shades (e.g., grey-50, grey-200, grey-300)
-  - Use `"var(--mui-palette-action-hover)"` for hover states
-- **Exception**: Use `theme.palette.*` values when you need to pass colors to functions like `alpha()` that require actual color values, not CSS variables
-- **For styled components**: Add `({ theme })` parameter only when you need `theme.spacing()`, `theme.breakpoints`, or functions like `alpha()`
-- Test all components in both light and dark mode to ensure proper color contrast and visibility
-
----
-
-## Mobile App (`/app/mobile`)
-
-- Uses npm (not yarn) for package management
-- See `/app/mobile/README.md` for setup instructions
-
----
-
-## Backend (`/app/backend`)
-
-- Run tests with `make test file=<test_name>` in the backend folder
-- See `/app/backend/readme.md` for more details
-- Always add a downgrade to migrations when possible and relevant.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -10,9 +10,9 @@ This is a monorepo for Couchers.org, a non-profit couch surfing platform. Users
 
 ## Repository Structure
 
-- `/app/backend` - Python backend (gRPC, SQLAlchemy, PostgreSQL/PostGIS)
+- `/app/backend` - Python backend (gRPC, SQLAlchemy, PostgreSQL/PostGIS). See `/app/backend/readme.md` for more details
 - `/app/web` - Next.js web frontend
-- `/app/mobile` - React Native Expo mobile app
+- `/app/mobile` - React Native Expo mobile app (uses `npm`, not `yarn`). See `/app/mobile/README.md` for setup instructions
 - `/app/proto` - Protocol buffer definitions shared across services
 - `/docs` - Documentation
 
@@ -59,21 +59,45 @@ make mypy
 
 ### Web (TypeScript/React)
 - Uses `nvm` for node version management
-- Uses `yarn` (not npm)
-- Import aliases: use `components/` not `../../../components/`
-- No `any` types
-- Use StyledLink or next/link for routing
-- Type definitions should always go at the top of the file below the imports.
+- Uses `yarn` (not npm) - run dev server with `yarn start` (not Docker)
+- Run linting with `yarn lint` and auto-fix with `yarn lint:fix`
+- Run tests with `yarn test`
+- Run linting AND formatting with `yarn format`
+- Import aliases: use `components/` not `../../../components/`, `routes` not `../../../routes`
+- Import multiple MUI icons together: `import { Favorite, Star, Public } from "@mui/icons-material"` instead of separate imports
+- No `any` types - explicitly type mock mutations (e.g., `UseMutationResult<...>`)
+- Use StyledLink or next/link for routing - NOT MUI `Link`
+- Type definitions should always go at the top of the file below the imports
 - **IMPORTANT**: When using Material-UI components (Button, Chip, MenuItem, etc.) with the `href` prop for internal navigation, ALWAYS use `component={Link}` instead of `component="a"` to preserve locale prefixes. Import Link from `next/link`
+- Remove extra unnecessary style declarations - don't repeat anything that's already a default of MUI or the theme
+- Use theme-defined colors instead of ad-hoc gray backgrounds; use default MUI hover styles instead of custom dark-grey-on-hover
+- Prefer modern 2025 design patterns for UI components
+- Add Tanstack `queryKeys` to `app/web/features/queryKeys.ts` if they are used in more than one place
+- Use `slotProps` rather than `InputLabelProps` for MUI (`InputLabelProps` is deprecated)
+
+### Web Dark Mode
+- **Always use CSS variables for theme colors** to ensure dark mode compatibility:
+  - `var(--mui-palette-primary-main)` instead of `theme.palette.primary.main` in styled components
+  - `var(--mui-palette-text-primary)` for text colors
+  - `var(--mui-palette-background-paper)` / `var(--mui-palette-background-default)` for backgrounds
+  - `var(--mui-palette-divider)` for borders/dividers
+  - `var(--mui-palette-grey-XXX)` for grey shades (e.g., grey-50, grey-200, grey-300)
+  - `var(--mui-palette-action-hover)` for hover states
+- **Exception**: Use `theme.palette.*` values when passing colors to functions like `alpha()` that require actual color values, not CSS variables
+- For styled components, only add `({ theme })` parameter when you need `theme.spacing()`, `theme.breakpoints`, or functions like `alpha()`
+- Test all components in both light and dark mode to ensure proper color contrast and visibility
 
 ### Proto Files
 - Located in `/app/proto`
 - Run `make protos` from backend after changes
 - Internal job payloads in `/app/backend/proto/internal/jobs.proto`
 
 ### Localization
-- Do not hard-code English text strings, store them in the appropriate locale files (`features/*/locales/en.json`)
+- Never hardcode English text - always use the `t()` function or `<Trans>` component for user-facing text
+- Store all English strings in the appropriate locale files (`features/*/locales/en.json`)
 - When adding strings to an `en.json` file, refer to `/docs/localization.md` for string key and text guidance
+- Use the `<Trans>` component for text with embedded components (like links). Make sure components in the translation JSON match the `components` prop exactly
+- For dates and times on the web frontend, never use `Date.toLocaleDateString()` or `Intl.DateTimeFormat` directly - use the helpers in `app/web/utils/date.ts` (`localizeDateTime`, `localizeDateTimeRange`, `localizeYearMonth`, `timeAgo`). Pass the user's current language via `useTranslation()`'s `i18n.language`, not the browser locale
 
 ## Testing
 
@@ -85,9 +109,15 @@ make mypy
 - Background jobs don't run automatically in tests - use `process_job()` to manually execute queued jobs
 
 ### Web Tests
-- Use fixture data from `test/fixtures/` when available
-- Query by label (`getByLabelText`) for accessibility
-- Use `findByText` for async elements
+- Use fixture data from `test/fixtures/` (e.g., `hostRequest.json`, `messages.json`, `groupChat.json`) when available, instead of creating mock data inline
+- Query elements by label (`getByLabelText`) for accessibility. When there's ambiguity (e.g., both a label and aria-label), use the `selector` option: `getByLabelText(label, { selector: "textarea" })`
+- For text split by child elements (e.g., links inside text), use a function matcher:
+  ```typescript
+  screen.getByText((content, element) => {
+    return element?.textContent === "Full text including embedded link text";
+  })
+  ```
+- Use `await screen.findByText()` when waiting for elements after loading states, instead of `getByText()` after `waitForElementToBeRemoved()`
 - Tests should assert correct behavior (TDD-style), not mirror bugs. Fix the code if needed, and follow existing test patterns in the repo.
 
 ### Mobile Tests (React Native)
@@ -118,6 +148,7 @@ uv run --project .claude/tools ci-job-log <job-id> --full
 - PostgreSQL with PostGIS extension
 - Migrations in `/app/backend/src/couchers/migrations/versions/`
 - Migrations use ordinal numbering (`0001_`, `0002_`, ...) and must be linear (no branches). New migrations automatically get the next ordinal as their revision ID via `env.py`
+- Always add a `downgrade()` to migrations when possible and relevant
 - Models in `/app/backend/src/couchers/models/`
 
 ## Pull Requests
PATCH

echo "Gold patch applied."
