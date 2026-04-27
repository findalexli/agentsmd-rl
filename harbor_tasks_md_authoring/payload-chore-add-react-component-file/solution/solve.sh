#!/usr/bin/env bash
set -euo pipefail

cd /workspace/payload

# Idempotency guard
if grep -qF "- **Don't:** Place multiple `ComponentName.tsx` files in a single folder with on" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -71,6 +71,20 @@ Payload is a monorepo structured around Next.js, containing the core CMS platfor
   - Invalid: `payload.logger.error('message', err)` - don't pass error as second argument
   - Use `err` not `error`, use `msg` not `message` in object form
 
+### React Component File Structure
+
+Each React component should have its own named folder:
+
+```
+ComponentName/
+├── index.tsx       # Component implementation
+└── index.scss      # Styles (if applicable)
+```
+
+- **Do:** Create a folder per component with `index.tsx` and `index.scss`
+- **Don't:** Place multiple `ComponentName.tsx` files in a single folder with one shared `.scss` file
+- Re-export from barrel files (`index.ts`) when grouping related components in a parent directory
+
 ### Running Dev Server
 
 - `pnpm run dev` - Start dev server with default config (`test/_community/config.ts`)
PATCH

echo "Gold patch applied."
