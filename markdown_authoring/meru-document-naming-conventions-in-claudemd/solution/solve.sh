#!/usr/bin/env bash
set -euo pipefail

cd /workspace/meru

# Idempotency guard
if grep -qF "- Name files by the domain/topic they cover, not by the single function they cur" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -17,6 +17,7 @@ This installs dependencies and runs postinstall scripts (including the lefthook
   - `startMinutes`/`endMinutes` not `s`/`e`
   - `aStart`/`aEnd`/`bStart`/`bEnd` not `aS`/`aE`/`bS`/`bE`
   - `event` not `e`, `error` not `err`, `index` not `i` (unless in a for loop counter)
+- Avoid generic/contextless names even when they're full words — pick a name that carries the domain. `raw`, `data`, `parsed`, `record`, `result`, `value`, `item`, `obj`, `tmp` are all red flags on their own. Prefer `gtkDecorationLayout` over `layout`, `savedLanguages` over `languages`, `accountConfigs` over `configs`. This lets a reader understand a line without tracing back to where the value came from.
 
 ## Code Formatting
 
@@ -57,6 +58,14 @@ This installs dependencies and runs postinstall scripts (including the lefthook
   };
   ```
 
+- Name boolean-returning functions with the bare predicate prefix — `is`, `has`, `can`, `should`, `did`, `will` — matching Node.js, Lodash, React, and typescript-eslint's `naming-convention` rule (e.g. `isWithinNotificationTimes`, `isMailtoUrl`, `hasOverlap`). Don't prefix with `get` to dodge a variable-name collision. Avoid the collision one of these ways instead:
+  - Inline single-use calls — `if (!isWithinNotificationTimes()) { ... }` needs no local.
+  - If a local is needed, name it for its purpose rather than mirroring the function — e.g. `const shouldSuppressNotification = !isWithinNotificationTimes();`.
+
+## File Naming
+
+- Name files by the domain/topic they cover, not by the single function they currently contain. Prefer generic, higher-level names (`lib/linux.ts`, `lib/fs.ts`) over function-specific ones (`lib/linux-window-controls.ts`, `lib/file-exists.ts`) so related helpers can accrete into the same file over time instead of each living in its own tiny file. Only split when a file grows large enough that the current topic is clearly two topics.
+
 ## Dependencies
 
 - Always install packages as dev dependencies with `bun add -d <package>`. Rolldown/Vite bundle everything at build time, and Electron builder re-bundles anything in `dependencies` into the shipped app, so normal deps would ship duplicated. The only exception is packages with native modules that Electron needs to load at runtime — those must go in `dependencies` so electron-builder can package them correctly. Never edit `package.json` or `bun.lock` manually to add or bump dependencies.
PATCH

echo "Gold patch applied."
