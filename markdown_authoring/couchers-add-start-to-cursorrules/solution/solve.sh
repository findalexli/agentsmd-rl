#!/usr/bin/env bash
set -euo pipefail

cd /workspace/couchers

# Idempotency guard
if grep -qF "- Each subproject has its own `.cursorrules` file with specific tooling and styl" ".cursorrules" && grep -qF "- Remove extra unnecessary style declarations, including anything that's already" "app/web/.cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -0,0 +1,12 @@
+# Couchers Project Rules
+
+This is a monorepo containing:
+- `/app/web` - Next.js web frontend (see `/app/web/.cursorrules` for web-specific rules)
+- `/app/mobile` - React Native Expo mobile app
+- `/app/native` - Deprecated please ignore
+- `/app/backend` - Python backend
+
+## General Conventions
+- Each subproject has its own `.cursorrules` file with specific tooling and style guidelines
+- Check the relevant folder's `.cursorrules` for language/framework-specific rules
+
diff --git a/app/web/.cursorrules b/app/web/.cursorrules
@@ -0,0 +1,27 @@
+# Web Frontend Rules
+
+## Package Manager
+This project uses **yarn** as the package manager. Always use `yarn` commands instead of `npm`:
+- Use `yarn install` instead of `npm install`
+- Use `yarn add` instead of `npm install`
+- Use `yarn test` instead of `npm test`
+- Use `yarn start` instead of `npm start`
+- etc.
+
+## Linting
+- Run linting `yarn lint` to see issues and `yarn lint:fix` to fix them
+
+## Testing
+Run tests with: `yarn test`
+
+## Development
+To run the app locally in development, use `yarn start` (not Docker)
+
+## Code Style
+- Do not use the `any` type in TypeScript - it's considered bad practice
+- Remove extra unnecessary style declarations, including anything that's already a default of MUI or the theme
+- Use theme-defined colors instead of ad-hoc gray backgrounds
+- Use default Material-UI hover styles instead of custom dark grey on hover
+- Prefer modern 2025 design patterns for UI components
+- Use StyledLink.tsx component or import from next/link for links to preserve routing, NOT MUI Link
+
PATCH

echo "Gold patch applied."
