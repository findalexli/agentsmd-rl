#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

# Idempotency guard
if grep -qF "- `packages/ui` - Shared UI components (shadcn/ui + TailwindCSS v4)." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -11,11 +11,10 @@ Bun + Turbo monorepo with:
   - `apps/docs` - Documentation site
   - `apps/blog` - Blog site
 - **Packages**:
-  - `packages/ui` - Shared UI components (shadcn/ui + TailwindCSS v4). 
+  - `packages/ui` - Shared UI components (shadcn/ui + TailwindCSS v4).
     - Add components: `npx shadcn@latest add <component>` (run in `packages/ui/`)
   - `packages/db` - Drizzle ORM database schema
   - `packages/constants` - Shared constants
-  - `packages/models` - Shared data models
   - `packages/scripts` - CLI tooling
   - `packages/typescript-config` - TypeScript configs
 
@@ -236,50 +235,3 @@ The desktop app loads environment variables from the monorepo root `.env` file:
 - `src/lib/electron-router-dom.ts` must NOT import Node.js modules (`node:path`, `dotenv`) as it's shared between main and renderer processes
 - Port configuration flows: `.env` → main process → `electron-router-dom` settings → Vite dev server
 
-### Keyboard Shortcuts System
-
-The desktop app uses a centralized keyboard shortcuts system inspired by Arc Browser.
-
-**File Structure:**
-- `src/renderer/lib/keyboard-shortcuts.ts` - Core shortcuts infrastructure (types, matchers, handlers)
-- `src/renderer/lib/shortcuts.ts` - Arc-style shortcut definitions (workspace, tab, terminal)
-
-**Implemented Shortcuts:**
-
-**Workspace Management:**
-- `Cmd+Option+Left/Right` - Switch between workspaces
-- `Cmd+S` - Toggle sidebar visibility
-- `Cmd+D` - Create split view (horizontal)
-- `Cmd+Shift+D` - Create split view (vertical)
-
-**Tab Management:**
-- `Cmd+Option+Up/Down` - Switch between tabs
-- `Cmd+T` - Create new tab
-- `Cmd+W` - Close tab
-- `Cmd+Shift+T` - Reopen closed tab [TODO - requires history tracking]
-- `Cmd+1-9` - Jump to tab by position
-
-**Terminal:**
-- `Cmd+K` - Clear terminal (scrollback + screen)
-- `Cmd+W` - Close current terminal
-
-**Window:**
-- `Cmd+Shift+W` - Close window (Arc-style: Cmd+W closes content, Cmd+Shift+W closes window)
-
-**Adding New Shortcuts:**
-
-1. Define handlers in the component (e.g., `MainScreen.tsx`)
-2. Create shortcut group using helper functions from `shortcuts.ts`
-3. Use `createShortcutHandler` to convert to event handler
-4. Attach to event listener or terminal custom key handler
-
-**Example:**
-```typescript
-const shortcuts = createWorkspaceShortcuts({
-  switchToPrevWorkspace: () => { /* handler logic */ },
-  // ... other handlers
-});
-
-const handleKeyDown = createShortcutHandler(shortcuts.shortcuts);
-window.addEventListener("keydown", handleKeyDown);
-```
PATCH

echo "Gold patch applied."
