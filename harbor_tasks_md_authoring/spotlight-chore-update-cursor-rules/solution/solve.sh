#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spotlight

# Idempotency guard
if grep -qF ".cursor/rules/.cursor/rules/routing.mdc" ".cursor/rules/.cursor/rules/routing.mdc" && grep -qF ".cursor/rules/general-guidelines.mdc" ".cursor/rules/general-guidelines.mdc" && grep -qF "- `spotlight run <command>` - Most common usage. Wraps your application, auto-de" "packages/spotlight/.cursor/rules/overview.mdc" && grep -qF "dragBar.style.cssText = 'position:fixed;top:0;left:0;right:0;height:40px;-webkit" "packages/spotlight/src/electron/.cursor/rules/electron.mdc" && grep -qF "The Spotlight server (sidecar) is a Node.js HTTP server built with Hono that rec" "packages/spotlight/src/server/.cursor/rules/server.mdc" && grep -qF "| `spotlight` / `spotlight server` | Starts the sidecar server (default) | `serv" "packages/spotlight/src/server/cli/.cursor/rules/cli.mdc" && grep -qF "The MCP server enables AI coding assistants to access Spotlight telemetry data v" "packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc" && grep -qF "**Important**: Do NOT manage navigation state in local component state. Extract " "packages/spotlight/src/ui/.cursor/rules/ui.mdc" && grep -qF "- **Components**: Astro (`.astro`) for static content, React (`.tsx`) for intera" "packages/website/.cursor/rules/website.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/.cursor/rules/routing.mdc b/.cursor/rules/.cursor/rules/routing.mdc
@@ -1,15 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: false
----
-## Routing
-Use React Router v6 (with MemoryRouter) for all routing logic.
-
-Details:
-	•	Use <Routes> and <Route> to define all navigable views.
-	•	Use <Link> or useNavigate for navigation — do not manually manage routing state like selectedTrace or similar in local component state.
-	•	When possible, extract state from the URL using useParams or useSearchParams instead of passing props or using global state.
-	•	Treat the URL as the source of truth for navigation-related state (e.g. selected items, tabs, filters, etc).
-
-Examples of routing: [TraceItem.tsx](mdc:packages/overlay/src/integrations/sentry/components/traces/TraceItem.tsx) [index.tsx](mdc:packages/overlay/src/integrations/sentry/components/traces/TraceDetails/index.tsx) 
diff --git a/.cursor/rules/general-guidelines.mdc b/.cursor/rules/general-guidelines.mdc
@@ -1,412 +0,0 @@
----
-description: 
-globs: 
-alwaysApply: false
----
-# Spotlight Development Guidelines
-
-Based on analysis of the actual codebase structure and patterns.
-
-## Repository Layout
-
-### Monorepo Structure
-
-```shell
-packages/
-├── overlay/         # React-based UI component
-├── sidecar/         # Node.js proxy server
-├── spotlight/       # Main package (combines overlay + sidecar)
-├── astro/           # Astro integration
-├── electron/        # Electron integration
-├── website/         # Documentation site
-└── tsconfig/        # Shared TypeScript configuration
-
-.changeset/          # Changeset configuration
-```
-
-### Package Dependencies
-
-- `spotlight` depends on `overlay` and `sidecar` using `workspace:*`
-- All packages extend shared TypeScript config from `@spotlightjs/tsconfig`
-- Each package has its own build configuration and scripts
-
-## Overlay Package Patterns
-
-### Directory Structure
-
-```shell
-src/
-├── components/      # React components (flat structure)
-├── integrations/    # Plugin system with subdirectories per integration
-├── lib/             # Utilities and hooks (flat files)
-├── ui/              # Reusable UI components
-├── assets/          # SVG icons and resources
-├── App.tsx          # Main application component
-├── index.tsx        # Entry point and initialization
-├── types.ts         # Type definitions
-└── constants.ts     # Application constants
-```
-
-### React Component Patterns
-
-#### File Naming & Structure
-
-- Components use PascalCase: `Trigger.tsx`, `Debugger.tsx`
-- Utility files use camelCase: `classNames.ts`, `useKeyPress.ts`
-- Single component per file with default export
-
-#### Component Definition Pattern
-
-```typescript
-export default function ComponentName({
-  prop1,
-  prop2 = defaultValue,
-}: {
-  prop1: boolean;
-  prop2?: string;
-}) {
-  // State declarations first
-  const [state, setState] = useState(defaultValue);
-
-  // Effects second
-  useEffect(() => {
-    // effect logic
-  }, [dependencies]);
-
-  // Event handlers third
-  const handleEvent = useCallback(() => {
-    // handler logic
-  }, [dependencies]);
-
-  // Return JSX
-  return (
-    <div>
-      {/* JSX content */}
-    </div>
-  );
-}
-```
-
-#### Styling Patterns
-
-- Uses Tailwind CSS with custom utilities
-- Custom `cn()` utility function for conditional classes:
-
-  ```typescript
-  className={cn(
-    'base-classes',
-    condition ? 'conditional-classes' : '',
-    variable === 'value' ? 'variant-classes' : 'default-classes'
-  )}
-  ```
-
-- Anchor positioning via utility functions that return Tailwind classes
-- No CSS modules or styled-components
-
-#### Component Props
-
-- Inline type definitions in component signature
-- Uses `ComponentPropsWithoutRef<'element'>` for extending native props
-- Omits specific props when extending: `Omit<BaseProps, 'excluded'>`
-
-### Integration System
-
-#### Integration Interface
-
-```typescript
-type Integration<T = any> = {
-  name: string;
-  forwardedContentType?: string[];
-  tabs?: TabsCreationFunction<T>;
-  setup?: (
-    context: SpotlightContext
-  ) => void | Promise<void> | TeardownFunction;
-  processEvent?: (
-    eventContext: RawEventContext
-  ) => ProcessedEventContainer<T> | undefined;
-  reset?: () => void;
-};
-```
-
-#### Integration Organization
-
-```shell
-integrations/
-├── integration.ts       # Base interfaces and utilities
-├── sentry/             # Full integration example
-│   ├── index.ts        # Main integration implementation
-│   ├── types.ts        # Integration-specific types
-│   ├── constants.ts    # Integration constants
-│   ├── components/     # React components for this integration
-│   ├── tabs/           # Tab components
-│   ├── store/          # State management (Zustand)
-│   └── utils/          # Utility functions
-└── console/            # Simpler integration example
-```
-
-### Utility Patterns
-
-#### Custom Hooks
-
-- File naming: `useHookName.ts`
-- Document parameters with JSDoc
-- Return cleanup functions from useEffect as `undefined`:
-
-  ```typescript
-  return () => cleanup() as undefined;
-  ```
-
-#### Utility Functions
-
-- Single responsibility per file
-- Default exports for main utility
-- Simple function signatures without over-abstraction
-
-### State Management
-
-- Local state with React hooks for component state
-- Zustand for complex/shared state (see `sentry/store/`)
-- Event-driven architecture using custom event target
-- No Redux or Context for global state
-
-## Sidecar Package Patterns
-
-### Directory Structure
-
-```shell
-src/
-├── main.ts              # Main server logic
-├── constants.ts         # Port and endpoint constants
-├── logger.ts            # Logging utilities
-├── messageBuffer.ts     # Event buffering system
-├── contextlines.ts      # Source code context handling
-```
-
-### Server Architecture
-
-- Single main file with all HTTP handlers
-- Route-based handler mapping using RegExp patterns
-- CORS middleware wrapper pattern
-- Functional composition for middleware
-
-#### Handler Pattern
-
-```typescript
-const handlerName = (
-  req: IncomingMessage,
-  res: ServerResponse,
-  pathname?: string,
-  searchParams?: URLSearchParams
-) => {
-  // Handler logic
-};
-
-const ROUTES: [RegExp, RequestHandler][] = [
-  [/^\/endpoint$/, enableCORS(handlerName)],
-  // more routes...
-];
-```
-
-#### Middleware Pattern
-
-```typescript
-const middlewareName = (handler: RequestHandler): RequestHandler =>
-  withTracing(
-    (req, res, pathname, searchParams) => {
-      // Middleware logic before
-      const result = handler(req, res, pathname, searchParams);
-      // Middleware logic after
-      return result;
-    },
-    { name: "middlewareName", op: "sidecar.operation" }
-  );
-```
-
-### Error Handling
-
-- No try/catch blocks in route handlers
-- Error responses via dedicated error functions
-- Logging via custom logger with levels
-
-## Spotlight Package Patterns
-
-### Directory Structure
-
-```
-src/
-├── overlay.ts           # Re-export overlay
-├── sidecar.ts           # Re-export sidecar
-└── index.html           # Standalone HTML page
-```
-
-### Plugin Pattern
-
-```typescript
-export default function pluginName(options: PluginOptions = {}): PluginOption {
-  return {
-    name: "plugin-name",
-    apply: "serve",
-    transform(code, id) {
-      // Transform logic
-    },
-    configureServer(server) {
-      // Server configuration
-    },
-  };
-}
-```
-
-## TypeScript Patterns
-
-### Type Organization
-
-- Shared types in `types.ts` at package level
-- Integration-specific types in integration subdirectories
-- Use `type` for object shapes, `interface` for extensible contracts
-
-### Type Definitions
-
-```typescript
-// Configuration objects use type
-export type ConfigOptions = {
-  prop1: boolean;
-  prop2?: string;
-};
-
-// React component props use inline types
-export default function Component({ prop }: { prop: string }) {
-  // component logic
-}
-
-// Complex generic types
-export type ProcessedEventContainer<T> = {
-  event: T;
-};
-```
-
-### Import/Export Patterns
-
-- Default exports for main functionality
-- Named exports for utilities and secondary functionality
-- Re-exports in main index files for public API
-- Tilde (`~/`) path alias for src root in overlay package
-
-## Build & Development Patterns
-
-### Build System
-
-- **Turbo** for build orchestration and task caching across the monorepo
-- **Vite** for individual package bundling
-- **TypeScript** for type checking and declaration generation
-
-### Development Tools
-
-- **Linting & Formatting**: Biome for fast linting and formatting
-- **Testing**: Vitest for unit tests, custom E2E testing setup
-- **Type Checking**: Strict TypeScript with composite projects
-- **Version Management**: Changesets for semantic versioning
-
-## Coding Standards
-
-### Biome Configuration
-
-- **Linting**: Comprehensive rule set with TypeScript support
-- **Formatting**: Matches previous Prettier settings
-- **Import Organization**: Automatic import sorting and type-only imports
-- **CSS Class Sorting**: Tailwind class sorting for consistency
-
-### Code Style
-
-- **Line Length**: 120 characters
-- **Quotes**: Single quotes for strings, double quotes in JSON
-- **Trailing Commas**: Always use trailing commas
-- **Arrow Functions**: Parentheses as needed (asNeeded)
-- **Import Organization**: Automatic sorting via Biome
-
-### Common Commands
-
-```shell
-# Development
-pnpm dev              # Start overlay and sidecar development
-pnpm dev:website      # Start website development
-
-# Building
-pnpm build            # Build all packages
-turbo build           # Direct turbo build command
-turbo build --filter=@spotlightjs/overlay  # Build specific package
-
-# Testing
-pnpm -r test             # Run package tests
-pnpm -r test:e2e         # Run end-to-end tests
-
-# Code Quality
-pnpm lint             # Check code with Biome
-pnpm lint:fix         # Fix auto-fixable issues
-pnpm format           # Format code with Biome
-pnpm clean            # Clean all dist folders
-```
-
-### Package Scripts
-
-```json
-{
-  "dev": "vite build --watch",
-  "build": "vite build && tsc",
-  "test": "vitest"
-}
-```
-
-### Turbo Configuration
-
-- **Task Dependencies**: Build tasks depend on dependencies being built first (`^build`)
-- **Caching**: Aggressive caching for build, test, and lint tasks
-- **Development**: No caching for `dev` tasks (persistent/long-running)
-- **Inputs**: File patterns that affect task outputs for cache invalidation
-- **Outputs**: Generated files that should be cached
-
-### Build Outputs
-
-- Dual ESM/CJS builds using Vite
-- TypeScript declarations via `tsc`
-- `exports` field for multiple entry points
-- Dist folder with organized outputs
-
-### Configuration Files
-
-- `biome.json` for linting and formatting
-- `turbo.json` for build orchestration and caching
-- Shared TypeScript config extended from `@spotlightjs/tsconfig`
-- Individual Vite configs per package
-- Tailwind config in overlay package only
-
-## Testing Patterns
-
-### Test Organization
-
-- Vitest for unit tests
-- Test files alongside source: `file.spec.ts`
-- E2E tests in separate package with framework demos
-
-### Test Structure
-
-- Integration tests over unit tests
-- Mock external dependencies
-- Test actual user scenarios in demo applications
-
-## Documentation Patterns
-
-### Code Documentation
-
-- JSDoc for public APIs
-- Inline comments for complex business logic
-- Parameter documentation in custom hooks
-
-### Package Documentation
-
-- Each package has README with setup instructions
-- Changelog files maintained via changesets
-- Migration guides for breaking changes
-
----
-
-_These guidelines reflect the actual patterns used in the Spotlight codebase as of the current version._
diff --git a/packages/spotlight/.cursor/rules/overview.mdc b/packages/spotlight/.cursor/rules/overview.mdc
@@ -0,0 +1,147 @@
+---
+description: Overview of the Spotlight package - the main package containing UI, server, and Electron app
+globs:
+alwaysApply: true
+---
+
+# Spotlight Package Overview
+
+The `@spotlightjs/spotlight` package is a unified package containing the UI, server (sidecar), CLI, and Electron desktop application.
+
+## The `spotlight` CLI
+
+Spotlight provides a CLI tool called `spotlight` that users run from the terminal. It's the main way developers interact with Spotlight.
+
+### Available Commands
+
+```bash
+# Run your app with Spotlight (wraps your process, sets env vars)
+spotlight run # detects package.json and docker compose
+spotlight run npm run dev
+spotlight run docker compose up
+
+# Start the sidecar server only (listens on port 8969)
+spotlight
+spotlight server
+spotlight --port 3000
+
+# Tail/stream events to terminal
+spotlight tail                    # All events
+spotlight tail errors             # Only errors
+spotlight tail traces logs        # Multiple types
+spotlight tail --format json      # Different output format
+
+# Start MCP server for AI assistants (Cursor, Claude, etc.)
+spotlight mcp
+
+# Show help
+spotlight help
+spotlight --help
+```
+
+### Key Points
+
+- `spotlight run <command>` - Most common usage. Wraps your application, auto-detects Docker Compose or package.json scripts, sets `SENTRY_SPOTLIGHT` env var
+- `spotlight` (no args) - Starts the sidecar server with UI on http://localhost:8969
+- `spotlight tail` - Streams events to terminal, useful for debugging without UI
+- `spotlight mcp` - Starts MCP server for AI coding assistants
+
+### CLI Implementation
+
+- Entry point: `src/run.ts` → `src/server/cli.ts`
+- Commands: `src/server/cli/` directory (run.ts, tail.ts, mcp.ts, server.ts, help.ts)
+- Binary defined in `package.json`: `"bin": { "spotlight": "./dist/run.js" }`
+
+## Electron Desktop App
+
+Spotlight is also available as a standalone desktop app (see `electron/.cursor/rules`).
+
+- **Main process**: `src/electron/main/index.ts` - Window, tray, menus, runs sidecar
+- **Renderer**: `src/electron-index.tsx` - Entry point for UI in Electron
+- **Build config**: `vite.electron.config.ts`
+- **Packaging**: `electron-builder.cjs`
+
+The desktop app:
+- Runs the sidecar server internally (no need for `spotlight run`)
+- Shows a system tray icon (macOS/Windows)
+- Supports auto-updates
+- Uses `IS_ELECTRON` constant for UI adaptations (see `ui/.cursor/rules`)
+
+```bash
+pnpm dev:electron    # Run Electron in development
+pnpm build:electron  # Build Electron app
+pnpm build:mac       # Package for macOS
+```
+
+## Package Structure
+
+```
+src/
+├── ui/              # React-based UI (see ui/.cursor/rules)
+├── server/          # Node.js server/sidecar (see server/.cursor/rules)
+│   ├── cli/        # CLI commands (see cli/.cursor/rules)
+│   └── mcp/        # MCP server (see mcp/.cursor/rules)
+├── electron/        # Electron main process (see electron/.cursor/rules)
+├── shared/          # Shared constants between UI and server
+├── index.tsx        # UI entry point (web)
+├── electron-index.tsx  # UI entry point (Electron)
+├── run.ts           # CLI entry point
+└── instrument.ts    # Sentry instrumentation
+```
+
+## Build System
+
+Multiple Vite configurations for different targets:
+
+- `vite.ui.config.ts` - UI bundle (web)
+- `vite.node.config.ts` - Server/CLI bundle
+- `vite.electron.config.ts` - Electron app (sets `__IS_ELECTRON__`)
+- `vite.dev.config.ts` - Development server
+
+## Development Commands
+
+```bash
+# From repository root
+pnpm dev            # UI + server concurrently
+pnpm dev:ui         # UI only (Vite dev server)
+pnpm dev:server     # Server only (Node with --watch)
+pnpm dev:electron   # Electron app with HMR
+
+# Testing
+pnpm test           # Run unit tests (Vitest)
+pnpm test:dev       # Run tests in watch mode
+pnpm test:e2e       # Run all E2E tests
+pnpm test:e2e:cli   # CLI E2E tests
+pnpm test:e2e:ui    # UI E2E tests (Playwright)
+```
+
+## Key Dependencies
+
+- **UI**: React, React Router, Zustand, Tailwind CSS, Shiki
+- **Server**: Hono, @hono/node-server, @sentry/node
+- **MCP**: @modelcontextprotocol/sdk, Zod
+- **Electron**: electron, electron-builder, electron-updater, electron-store
+
+## Testing
+
+- **Unit tests**: Vitest with happy-dom for UI components
+- **E2E tests**: Playwright for UI and CLI testing
+- **Config files**: `vitest.config.ts`, `vitest.cli.config.ts`, `playwright.config.ts`
+
+## Exports
+
+The package exports:
+
+```typescript
+// Main server API
+import { setupSpotlight } from '@spotlightjs/spotlight';
+
+// SDK utilities
+import { pushToSpotlightBuffer } from '@spotlightjs/spotlight/sdk';
+```
+
+## Environment Variables
+
+- `SENTRY_SPOTLIGHT` - URL to Spotlight sidecar (auto-set by `spotlight run`)
+- `SPOTLIGHT_DEBUG` - Enable debug logging
+- `SPOTLIGHT_CAPTURE` - Capture incoming envelopes to files
diff --git a/packages/spotlight/src/electron/.cursor/rules/electron.mdc b/packages/spotlight/src/electron/.cursor/rules/electron.mdc
@@ -0,0 +1,233 @@
+---
+description: Electron desktop app development guidelines
+globs:
+alwaysApply: true
+---
+
+# Electron App Guidelines
+
+The Spotlight desktop app packages the UI and server into a standalone Electron application.
+
+## Architecture
+
+```
+Electron App
+├── Main Process (Node.js)
+│   ├── electron/main/index.ts   # Window, tray, menus, auto-update
+│   ├── Runs sidecar server      # setupSpotlight() on port 8969
+│   └── IPC handlers
+│
+└── Renderer Process (Chromium)
+    ├── electron-index.tsx       # Entry point, Sentry init
+    └── UI (React app)           # Same as web UI, with IS_ELECTRON=true
+```
+
+## Main Process (`electron/main/index.ts`)
+
+The main process handles:
+
+### Window Management
+```typescript
+const win = new BrowserWindow({
+  titleBarStyle: 'hidden',           // Custom title bar
+  trafficLightPosition: { x: 16, y: 16 },  // macOS traffic lights
+  webPreferences: {
+    nodeIntegration: true,
+    sandbox: false,
+  },
+});
+
+// Load UI
+if (process.env.VITE_DEV_SERVER_URL) {
+  win.loadURL(process.env.VITE_DEV_SERVER_URL);  // Dev
+} else {
+  win.loadFile(path.join(__dirname, '../renderer/index.html'));  // Prod
+}
+```
+
+### Sidecar Server
+The main process runs the sidecar server internally:
+```typescript
+import { setupSpotlight } from '../../server/main';
+
+await setupSpotlight({
+  port: DEFAULT_PORT,  // 8969
+  incomingPayload: storeIncomingPayload,
+  isStandalone: true,
+});
+```
+
+### System Tray
+- Tray icon with context menu
+- Click to show/hide window
+- "Start at Login" option
+- Linux: No tray (quit on window close)
+
+### Auto-Update
+```typescript
+import { autoUpdater } from 'electron-updater';
+
+autoUpdater.checkForUpdates();
+autoUpdater.on('update-downloaded', () => {
+  // Prompt user to restart
+});
+```
+
+### Menus
+- Application menu (File, Edit, View, Window, Settings, Help)
+- Settings: "Send Error Reports", "Send Payload to Sentry", "Start at Login"
+
+### Persistent Settings
+```typescript
+import Store from 'electron-store';
+const store = new Store();
+
+store.get('sentry-enabled');
+store.set('sentry-enabled', true);
+```
+
+### Drag Bar Injection
+The main process injects a drag bar element after the page loads:
+```typescript
+win.webContents.executeJavaScript(`
+  const dragBar = document.createElement('div');
+  dragBar.id = 'electron-top-drag-bar';
+  dragBar.style.cssText = 'position:fixed;top:0;left:0;right:0;height:40px;-webkit-app-region:drag;z-index:99999;';
+  document.body.appendChild(dragBar);
+`);
+```
+
+## Renderer Process (`electron-index.tsx`)
+
+Entry point for the UI in Electron:
+
+```typescript
+import { init as ElectronSentryInit } from '@sentry/electron/renderer';
+import { init as ReactSentryInit } from '@sentry/react';
+import { _init } from './index';
+
+// Electron-specific Sentry initialization
+ElectronSentryInit({
+  dsn: '...',
+  integrations: getIntegrations(true),
+}, ReactSentryInit);
+
+// Initialize the React app
+_init();
+```
+
+## UI Adaptations for Electron
+
+### `IS_ELECTRON` Constant
+
+Build-time constant set by `vite.electron.config.ts`:
+
+```typescript
+// vite.electron.config.ts
+define: {
+  __IS_ELECTRON__: true,
+}
+
+// lib/isElectron.ts
+export const IS_ELECTRON = typeof __IS_ELECTRON__ !== 'undefined' && __IS_ELECTRON__;
+```
+
+### Conditional Rendering
+
+Use `IS_ELECTRON` to adapt UI for the desktop app:
+
+```tsx
+import { IS_ELECTRON } from '@spotlight/ui/lib/isElectron';
+
+// Add padding for the 40px drag bar
+<div className={cn('flex-1', IS_ELECTRON && 'pt-10')}>
+
+// Sidebar header margin
+<header className={cn('p-4', IS_ELECTRON && 'mt-10')}>
+```
+
+### Router
+
+Electron uses `HashRouter` instead of `BrowserRouter` because it loads from `file://` protocol:
+
+```tsx
+// lib/Router.tsx
+if (IS_ELECTRON) {
+  return <HashRouter>{children}</HashRouter>;
+}
+return <BrowserRouter>{children}</BrowserRouter>;
+```
+
+## Build & Packaging
+
+### Vite Config (`vite.electron.config.ts`)
+
+```typescript
+import electron from 'vite-plugin-electron/simple';
+
+export default defineConfig({
+  plugins: [
+    electron({
+      main: {
+        entry: 'src/electron/main/index.ts',
+        vite: {
+          build: { outDir: 'dist-electron/main' },
+        },
+      },
+    }),
+  ],
+  define: {
+    __IS_ELECTRON__: true,
+  },
+  build: {
+    outDir: 'dist-electron/renderer',
+  },
+});
+```
+
+### Electron Builder (`electron-builder.cjs`)
+
+Packages the app for distribution:
+- macOS: `.dmg`, code signing, notarization
+- Windows: `.exe` installer
+- Linux: `.AppImage`
+
+### Resources
+
+```
+resources/
+├── icons/
+│   ├── mac/icon.icns
+│   ├── win/icon.ico
+│   └── png/              # Various sizes
+└── tray/
+    ├── logoTemplate.png  # macOS tray (template image)
+    └── logoTemplate.ico  # Windows tray
+```
+
+## Development
+
+```bash
+pnpm dev:electron    # Start Electron in dev mode with HMR
+```
+
+In dev mode:
+- Main process rebuilds on change
+- Renderer uses Vite dev server (`VITE_DEV_SERVER_URL`)
+- Auto-update uses `dev-app-update.yml`
+
+## Platform Differences
+
+| Feature | macOS | Windows | Linux |
+|---------|-------|---------|-------|
+| Tray icon | Yes | Yes | No (quit on close) |
+| Title bar | Hidden + traffic lights | Default | Default |
+| Auto-update | DMG | NSIS | AppImage |
+| Start at login | Yes | Yes | Depends on DE |
+
+## Sentry Integration
+
+- Main process: `@sentry/electron/main`
+- Renderer process: `@sentry/electron/renderer` + `@sentry/react`
+- User consent dialogs for error reporting
+- Optionally attach incoming payloads for debugging
diff --git a/packages/spotlight/src/server/.cursor/rules/server.mdc b/packages/spotlight/src/server/.cursor/rules/server.mdc
@@ -0,0 +1,215 @@
+---
+description: Server/sidecar development guidelines using Hono framework
+globs:
+alwaysApply: true
+---
+
+# Server Development Guidelines
+
+The Spotlight server (sidecar) is a Node.js HTTP server built with Hono that receives, stores, and streams telemetry data.
+
+## Framework
+
+Uses **Hono** with `@hono/node-server` for the HTTP server.
+
+## Project Structure
+
+```
+server/
+├── main.ts           # Server setup, startServer(), setupSpotlight()
+├── cli.ts            # CLI entry point and argument parsing
+├── cli/              # CLI command handlers (see cli/.cursor/rules)
+├── mcp/              # MCP server (see mcp/.cursor/rules)
+├── routes/           # HTTP route handlers
+│   ├── index.ts      # Route composition
+│   ├── stream/       # SSE streaming endpoints
+│   ├── health.ts     # Health check
+│   ├── clear.ts      # Buffer clear endpoint
+│   └── contextlines/ # Source context resolution
+├── parser/           # Envelope parsing logic
+├── formatters/       # Output formatters (human, json, logfmt, md)
+├── handlers/         # Request handlers
+├── utils/            # Utility functions
+├── types/            # TypeScript type definitions
+├── constants.ts      # Server constants
+├── logger.ts         # Logging utilities
+├── messageBuffer.ts  # Event storage buffer
+└── sdk.ts            # SDK utilities for external integrations
+```
+
+## Route Patterns
+
+Routes are modular Hono routers composed in `routes/index.ts`:
+
+```typescript
+import { Hono } from 'hono';
+import type { HonoEnv } from '../types/env';
+
+const router = new Hono<HonoEnv>()
+  .get('/path', ctx => {
+    return ctx.json({ status: 'ok' });
+  })
+  .post('/path', async ctx => {
+    const body = await ctx.req.json();
+    // Process...
+    return ctx.body(null, 200);
+  });
+
+export default router;
+```
+
+### Composing Routes
+
+```typescript
+// routes/index.ts
+import { Hono } from 'hono';
+import streamRouter from './stream/index';
+import healthRouter from './health';
+
+const router = new Hono();
+router.route('/stream', streamRouter);
+router.route('/health', healthRouter);
+
+export default router;
+```
+
+## Middleware
+
+### CORS
+
+```typescript
+import { cors } from 'hono/cors';
+
+app.use(cors({
+  origin: async origin => isAllowedOrigin(origin) ? origin : null,
+}));
+```
+
+### Custom Middleware
+
+```typescript
+app.use(async (ctx, next) => {
+  ctx.header('X-Custom-Header', 'value');
+  ctx.set('customKey', value); // Set context variable
+  await next();
+});
+```
+
+## Server-Sent Events (SSE)
+
+Streaming implemented in `routes/stream/streaming.ts`:
+
+```typescript
+import { streamSSE } from './streaming';
+
+router.get('/stream', ctx => {
+  return streamSSE(ctx, async stream => {
+    const sub = buffer.subscribe(container => {
+      stream.writeSSE({
+        id: container.id,
+        event: contentType,
+        data: JSON.stringify(data),
+      });
+    });
+
+    stream.onAbort(() => buffer.unsubscribe(sub));
+  });
+});
+```
+
+## Message Buffer
+
+`MessageBuffer` in `messageBuffer.ts` stores incoming envelopes:
+
+```typescript
+import { getBuffer } from './utils/index';
+
+const buffer = getBuffer();
+
+// Add data
+buffer.put(container);
+
+// Subscribe to new data
+const sub = buffer.subscribe(callback);
+buffer.unsubscribe(sub);
+
+// Read data with filters
+const envelopes = buffer.read({ timeWindow: 60 });
+const envelopes = buffer.read({ filename: 'auth.ts' });
+```
+
+## Envelope Parsing
+
+Parse incoming Sentry envelopes in `parser/`:
+
+```typescript
+import { processEnvelope } from './parser/index';
+
+const parsed = processEnvelope({
+  contentType: container.getContentType(),
+  data: container.getData(),
+});
+
+const [envelopeHeader, items] = parsed.envelope;
+```
+
+## Formatters
+
+Multiple output formats in `formatters/`:
+
+- `human/` - Human-readable terminal output
+- `json/` - JSON format
+- `logfmt/` - Logfmt format
+- `md/` - Markdown format (for MCP/AI)
+
+```typescript
+import { applyFormatter, humanFormatters } from './formatters/index';
+
+const output = applyFormatter(humanFormatters, type, payload, envelopeHeader);
+```
+
+## Tracing
+
+Use Sentry spans for request tracing:
+
+```typescript
+import { startSpan } from '@sentry/node';
+
+await startSpan({
+  name: `HTTP ${method} ${path}`,
+  op: 'sidecar.http.get',
+  attributes: { /* ... */ },
+}, async span => {
+  // Handle request
+  span.setAttribute('http.response.status_code', status);
+});
+```
+
+## Type Definitions
+
+```typescript
+// types/env.ts - Hono environment
+export type HonoEnv = {
+  Variables: {
+    basePath?: string;
+    incomingPayload?: (data: string) => void;
+  };
+};
+
+// types/cli.ts - CLI handler options
+export type CLIHandlerOptions = {
+  port: number;
+  cmdArgs: string[];
+  format: FormatterType;
+  // ...
+};
+```
+
+## Constants
+
+```typescript
+// constants.ts
+export const DEFAULT_PORT = 8969;
+export const SERVER_IDENTIFIER = 'spotlight-sidecar';
+export const SENTRY_CONTENT_TYPE = 'application/x-sentry-envelope';
+```
diff --git a/packages/spotlight/src/server/cli/.cursor/rules/cli.mdc b/packages/spotlight/src/server/cli/.cursor/rules/cli.mdc
@@ -0,0 +1,171 @@
+---
+description: CLI command development guidelines for Spotlight
+globs:
+alwaysApply: true
+---
+
+# CLI Development Guidelines
+
+This directory contains the implementation of the `spotlight` CLI commands.
+
+## Commands
+
+| Command | Description | Handler |
+|---------|-------------|---------|
+| `spotlight run <cmd>` | Wraps and runs an application with Spotlight | `run.ts` |
+| `spotlight` / `spotlight server` | Starts the sidecar server (default) | `server.ts` |
+| `spotlight tail [types]` | Streams events to terminal | `tail.ts` |
+| `spotlight mcp` | Starts MCP server for AI assistants | `mcp.ts` |
+| `spotlight help` | Shows help message | `help.ts` |
+
+Entry point is `../cli.ts` which handles argument parsing and routes via `CLI_CMD_MAP`.
+
+## CLI Handler Pattern
+
+Each command exports a default async function:
+
+```typescript
+import type { CLIHandlerOptions } from '../types/cli';
+
+export default async function commandName({
+  port,
+  cmdArgs,
+  basePath,
+  filesToServe,
+  format,
+  allowedOrigins,
+}: CLIHandlerOptions) {
+  // Command implementation
+}
+```
+
+### CLIHandlerOptions
+
+```typescript
+type CLIHandlerOptions = {
+  port: number;
+  cmdArgs: string[];         // Additional arguments after command
+  basePath?: string;         // Path for static files
+  filesToServe?: Record<string, Buffer>;
+  format: FormatterType;     // human | json | logfmt | md
+  allowedOrigins: string[];  // CORS origins
+};
+```
+
+## Argument Parsing
+
+Uses `parseArgs` from `node:util` in `../cli.ts`:
+
+```typescript
+import { parseArgs } from 'node:util';
+
+const { values, positionals } = parseArgs({
+  args: process.argv.slice(2),
+  options: {
+    port: { type: 'string', short: 'p' },
+    debug: { type: 'boolean', short: 'd', default: false },
+    format: { type: 'string', short: 'f', default: 'human' },
+    'allowed-origin': { type: 'string', short: 'A', multiple: true },
+    help: { type: 'boolean', short: 'h' },
+  },
+  allowPositionals: true,
+});
+```
+
+## Command Details
+
+### `spotlight run` (run.ts)
+
+Wraps and runs application processes with Spotlight environment:
+
+- Auto-detects Docker Compose (`docker-compose.yml`) or package.json scripts
+- Sets `SENTRY_SPOTLIGHT` environment variable for the child process
+- Captures stdout/stderr and sends as logs to Spotlight
+- Uses `host.docker.internal` for Docker containers to reach host
+
+```typescript
+const runCmd = spawn(cmdArgs[0], cmdArgs.slice(1), {
+  env: {
+    ...process.env,
+    SENTRY_SPOTLIGHT: spotlightUrl,
+    NEXT_PUBLIC_SENTRY_SPOTLIGHT: spotlightUrl,
+  },
+  stdio: ['inherit', 'pipe', 'pipe'],
+});
+```
+
+### `spotlight tail` (tail.ts)
+
+Streams events to terminal:
+
+```typescript
+// Supported event types
+const NAME_TO_TYPE_MAPPING = {
+  traces: ['transaction', 'span'],
+  logs: ['log'],
+  errors: ['event'],
+  attachments: ['attachment'],
+};
+
+// Magic words for all types
+const EVERYTHING_MAGIC_WORDS = ['everything', 'all', '*'];
+```
+
+### `spotlight mcp` (mcp.ts)
+
+Starts MCP server in stdio mode for AI assistants:
+
+```typescript
+import { createMCPInstance } from '../mcp/mcp';
+import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
+
+const mcpInstance = createMCPInstance();
+const transport = new StdioServerTransport();
+await mcpInstance.connect(transport);
+```
+
+## Output Formatters
+
+Support multiple output formats via `../formatters/`:
+
+- `human` - Human-readable colored output (default)
+- `json` - JSON format
+- `logfmt` - Logfmt format
+- `md` - Markdown format
+
+```bash
+spotlight tail --format json
+spotlight tail -f logfmt
+```
+
+## Logging
+
+Use the logger from `../logger.ts`:
+
+```typescript
+import { logger, enableDebugLogging } from '../logger';
+
+logger.info('Message');
+logger.error('Error message');
+logger.debug('Debug info'); // Only when --debug flag
+```
+
+## Metrics
+
+Track CLI usage with Sentry metrics:
+
+```typescript
+import { metrics } from '@sentry/node';
+
+metrics.count('cli.invocation', 1, {
+  attributes: { command: 'run', format: 'human' },
+});
+```
+
+## Testing
+
+CLI E2E tests in `tests/e2e/cli/`:
+
+```bash
+pnpm test:e2e:cli  # Run CLI E2E tests
+```
diff --git a/packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc b/packages/spotlight/src/server/mcp/.cursor/rules/mcp.mdc
@@ -0,0 +1,208 @@
+---
+description: MCP (Model Context Protocol) server development guidelines
+globs:
+alwaysApply: true
+---
+
+# MCP Server Guidelines
+
+The MCP server enables AI coding assistants to access Spotlight telemetry data via the Model Context Protocol.
+
+## Overview
+
+- **SDK**: `@modelcontextprotocol/sdk` for MCP server implementation
+- **Transport**: stdio (standard input/output) for communication with AI clients
+- **Validation**: Zod v3 for input schema validation
+- **Output**: Markdown-formatted text for AI consumption
+
+## Files
+
+```
+mcp/
+├── mcp.ts         # createMCPInstance() - tool registration
+└── constants.ts   # Response constants (NO_ERRORS_CONTENT, etc.)
+```
+
+## Creating the MCP Instance
+
+```typescript
+import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
+import { wrapMcpServerWithSentry } from '@sentry/node';
+
+export function createMCPInstance() {
+  const mcp = wrapMcpServerWithSentry(
+    new McpServer({
+      name: 'spotlight-mcp',
+      version: String(process.env.npm_package_version),
+    }),
+  );
+
+  // Register tools...
+
+  return mcp;
+}
+```
+
+## Tool Registration Pattern
+
+```typescript
+import { z } from 'zod/v3';
+import type { TextContent } from '@modelcontextprotocol/sdk/types.js';
+
+mcp.registerTool(
+  'tool_name',
+  {
+    title: 'Human-Readable Title',
+    description: `**Purpose:** Brief description of what the tool does.
+
+**When to use:**
+- Condition 1
+- Condition 2
+
+**Example calls:**
+\`\`\`json
+tool_name({ param: "value" })
+\`\`\`
+
+**Parameter hints:**
+• param: Description of parameter`,
+    inputSchema: {
+      param: z.string().describe('Parameter description'),
+      optionalParam: z.number().optional().describe('Optional parameter'),
+    },
+  },
+  async args => {
+    // Tool implementation
+    const data = getBuffer().read(args.filters);
+    
+    if (data.length === 0) {
+      return NO_DATA_CONTENT; // Return appropriate empty response
+    }
+
+    const content: TextContent[] = [];
+    
+    for (const item of data) {
+      content.push({
+        type: 'text',
+        text: formatItem(item), // Format for AI consumption
+      });
+    }
+
+    return { content };
+  },
+);
+```
+
+## Input Schema with Zod
+
+Use Zod v3 (`zod/v3`) for input validation:
+
+```typescript
+import { z } from 'zod/v3';
+
+const inputSchema = {
+  filters: z.union([
+    z.object({
+      timeWindow: z.number().describe('Seconds to look back'),
+    }),
+    z.object({
+      filename: z.string().describe('Filename to filter by'),
+    }),
+    z.object({
+      limit: z.number().describe('Max results'),
+      offset: z.number().default(0).describe('Skip N results'),
+    }).optional(),
+  ]),
+};
+```
+
+## Accessing Telemetry Data
+
+Use the message buffer to read stored envelopes:
+
+```typescript
+import { getBuffer } from '../utils/index';
+
+// Read with time window filter
+const envelopes = getBuffer().read({ timeWindow: 60 }); // Last 60 seconds
+
+// Read with filename filter
+const envelopes = getBuffer().read({ filename: 'auth.tsx' });
+
+// Read all
+const envelopes = getBuffer().read({ all: true });
+```
+
+## Formatters for AI Output
+
+Use markdown formatters from `formatters/md/` for AI-friendly output:
+
+```typescript
+import { formatErrorEnvelope } from '../formatters/md/errors';
+import { formatLogEnvelope } from '../formatters/md/logs';
+import { formatTraceSummary, buildSpanTree, renderSpanTree } from '../formatters/md/traces';
+
+// Format errors
+const errorText = await formatErrorEnvelope(envelope);
+
+// Format logs
+const logText = await formatLogEnvelope(envelope);
+
+// Format traces
+const traceSummary = formatTraceSummary(trace);
+const spanTree = buildSpanTree(trace);
+const treeLines = renderSpanTree(spanTree);
+```
+
+## Error Handling
+
+Always capture exceptions with context:
+
+```typescript
+import { captureException } from '@sentry/node';
+
+try {
+  // Process data
+} catch (err) {
+  captureException(err, { 
+    extra: { context: 'Error formatting envelope in MCP' } 
+  });
+}
+```
+
+## Response Constants
+
+Define in `constants.ts`:
+
+```typescript
+export const NO_ERRORS_CONTENT = {
+  content: [{
+    type: 'text',
+    text: 'No errors found in the specified time period.',
+  }],
+};
+
+export const NO_LOGS_CONTENT = {
+  content: [{
+    type: 'text',
+    text: 'No logs found in the specified time period.',
+  }],
+};
+```
+
+## Available Tools
+
+Current tools in `mcp.ts`:
+
+1. **search_errors** - Search for runtime errors and exceptions
+2. **search_logs** - Search application logs
+3. **search_traces** - List performance traces
+4. **get_traces** - Get detailed span tree for a trace
+
+## Testing
+
+Test MCP tools by running:
+
+```bash
+spotlight mcp  # Starts MCP server in stdio mode
+```
diff --git a/packages/spotlight/src/ui/.cursor/rules/ui.mdc b/packages/spotlight/src/ui/.cursor/rules/ui.mdc
@@ -0,0 +1,272 @@
+---
+description: UI development guidelines for the Spotlight React application
+globs:
+alwaysApply: true
+---
+
+# UI Development Guidelines
+
+The Spotlight UI is a React application for visualizing telemetry data (errors, traces, logs).
+
+## Server Connection (SSE)
+
+The UI connects to the sidecar server via **Server-Sent Events (SSE)**.
+
+### Connection Flow
+
+```
+sidecar.ts (connectToSidecar)
+    ↓
+EventSource → GET /stream?base64=1&client=spotlight-ui
+    ↓
+Listens for content-type events (application/x-sentry-envelope)
+    ↓
+telemetry/index.tsx (listener callback)
+    ↓
+useSentryStore.getState().pushEnvelope(envelope)
+    ↓
+Store processes → events, traces, logs, profiles
+```
+
+### Key Files
+
+- `sidecar.ts` - `connectToSidecar()` establishes SSE connection
+- `telemetry/index.tsx` - `Telemetry` component manages connection lifecycle
+- `store/slices/envelopesSlice.ts` - `pushEnvelope()` processes incoming data
+
+### Connection Code
+
+```tsx
+// sidecar.ts
+export function connectToSidecar(
+  sidecarUrl: string,
+  contentTypeListeners: Record<string, (event: string) => void>,
+  setOnline: (online: boolean) => void,
+) {
+  const source = new EventSource(`${sidecarUrl}/stream?base64=1`);
+  
+  for (const [contentType, listener] of Object.entries(contentTypeListeners)) {
+    source.addEventListener(contentType, (event) => listener(event.data));
+  }
+  
+  source.addEventListener('open', () => setOnline(true));
+  source.addEventListener('error', () => setOnline(false));
+  
+  return () => { /* cleanup */ };
+}
+```
+
+### Usage in Telemetry Component
+
+```tsx
+// telemetry/index.tsx
+export function Telemetry({ sidecarUrl }: { sidecarUrl: string }) {
+  const [isOnline, setOnline] = useState(false);
+
+  const listener = useCallback((event: string) => {
+    const envelope = JSON.parse(event);
+    useSentryStore.getState().pushEnvelope(envelope);
+  }, []);
+
+  useEffect(
+    () => connectToSidecar(sidecarUrl, { [SENTRY_CONTENT_TYPE]: listener }, setOnline),
+    [sidecarUrl, listener],
+  );
+
+  return <TelemetryView isOnline={isOnline} />;
+}
+```
+
+## Routing
+
+Use **React Router v6** for all navigation. The URL is the source of truth for navigation state.
+
+### Router Setup
+
+`lib/Router.tsx` provides the appropriate router based on environment:
+- `BrowserRouter` for standalone web
+- `HashRouter` for Electron (file:// protocol)
+
+### Navigation Patterns
+
+```tsx
+import { Link, useParams, useSearchParams, useNavigate } from 'react-router-dom';
+
+// Get state from URL
+const { traceId, spanId } = useParams();
+const [searchParams] = useSearchParams();
+
+// Programmatic navigation
+const navigate = useNavigate();
+navigate('/telemetry/traces');
+
+// Link component
+<Link to={`/telemetry/traces/${trace.trace_id}/context`}>View Trace</Link>
+```
+
+### Route Structure
+
+```
+/telemetry/
+├── traces/
+│   └── :traceId/
+│       └── context
+├── errors/
+│   └── :eventId
+├── logs/
+│   └── :logId
+└── insights/
+```
+
+**Important**: Do NOT manage navigation state in local component state. Extract it from URL parameters.
+
+## State Management
+
+Use **Zustand** with the slice pattern for global state.
+
+### Store Structure
+
+```
+store/
+├── store.ts          # Combined store (creates all slices)
+├── types.ts          # Type definitions
+├── slices/
+│   ├── envelopesSlice.ts  # pushEnvelope(), raw envelope storage
+│   ├── eventsSlice.ts     # pushEvent(), error events
+│   ├── tracesSlice.ts     # Trace data
+│   ├── logsSlice.ts       # Log data
+│   ├── profilesSlice.ts   # Profile data
+│   ├── sdksSlice.ts       # SDK info
+│   ├── settingsSlice.ts   # UI settings
+│   ├── subscriptionsSlice.ts  # Event subscriptions
+│   └── sharedSlice.ts     # Shared helpers (getEventById, resetData, etc.)
+└── utils/            # Processing utilities
+    ├── traceProcessor.ts
+    ├── logProcessor.ts
+    └── profileProcessor.ts
+```
+
+### Data Flow
+
+1. `pushEnvelope(envelope)` - Entry point for all incoming data
+2. Extracts items from envelope, identifies SDK
+3. Calls `pushEvent()` for each supported item type
+4. `pushEvent()` routes to appropriate processor:
+   - Error events → store in eventsById
+   - Trace events → `processTransactionEvent()` → tracesById
+   - Log events → `processLogItems()` → logsById
+   - Profile events → `processProfileEvent()` → profilesByTraceId
+
+### Usage Pattern
+
+```tsx
+import useSentryStore from '../store';
+
+function Component() {
+  // Select specific state
+  const traces = useSentryStore(state => state.getTraces());
+  const events = useSentryStore(state => state.getEvents());
+  
+  // Get actions
+  const resetData = useSentryStore(state => state.resetData);
+  
+  // Direct store access (outside React)
+  useSentryStore.getState().pushEnvelope(envelope);
+}
+```
+
+## Styling
+
+Use **Tailwind CSS** with the `cn()` utility for conditional classes.
+
+```tsx
+import { cn } from '@spotlight/ui/lib/cn';
+
+<div className={cn(
+  'base-classes px-4 py-2',
+  isSelected && 'bg-primary-800',
+  variant === 'error' ? 'text-red-400' : 'text-green-400'
+)}>
+```
+
+## Component Organization
+
+```
+ui/
+├── sidecar.ts       # connectToSidecar() - SSE connection
+├── ui/              # Reusable primitives (badge, button, table, tooltip)
+├── lib/             # Utilities and hooks
+├── telemetry/
+│   ├── index.tsx    # Telemetry component (connection setup)
+│   ├── components/  # Feature components
+│   │   ├── shared/  # Shared components (DateTime, JsonViewer, etc.)
+│   │   ├── traces/  # Trace-specific components
+│   │   ├── events/  # Error event components
+│   │   └── log/     # Log components
+│   ├── tabs/        # Tab views (TracesTab, ErrorsTab, LogsTab, InsightsTab)
+│   ├── store/       # Zustand store
+│   └── hooks/       # Custom hooks
+└── assets/          # SVG icons
+```
+
+## Path Aliases
+
+- `@spotlight/ui/` maps to `src/ui/`
+- `@spotlight/shared/` maps to `src/shared/`
+
+```tsx
+import { cn } from '@spotlight/ui/lib/cn';
+import { SENTRY_CONTENT_TYPE } from '@spotlight/shared/constants';
+```
+
+## Electron Awareness
+
+Use `IS_ELECTRON` for conditional rendering:
+
+```tsx
+import { IS_ELECTRON } from '@spotlight/ui/lib/isElectron';
+
+<div className={cn('flex-1', IS_ELECTRON && 'pt-10')}>
+```
+
+## Component Patterns
+
+### Function Components with Inline Props
+
+```tsx
+export default function TraceItem({ trace, className }: { 
+  trace: Trace; 
+  className?: string;
+}) {
+  const { traceId } = useParams();
+  const isSelected = traceId === trace.trace_id;
+  
+  return (
+    <Link to={`/telemetry/traces/${trace.trace_id}`}>
+      {/* ... */}
+    </Link>
+  );
+}
+```
+
+### Custom Hooks
+
+```tsx
+// hooks/useDebounce.ts
+export function useDebounce<T>(value: T, delay: number): T {
+  const [debouncedValue, setDebouncedValue] = useState(value);
+  
+  useEffect(() => {
+    const timer = setTimeout(() => setDebouncedValue(value), delay);
+    return () => clearTimeout(timer);
+  }, [value, delay]);
+  
+  return debouncedValue;
+}
+```
+
+## Testing
+
+- Use `@testing-library/react` for component tests
+- Test files: `*.test.tsx` or `*.spec.tsx`
+- Run with `pnpm test` or `pnpm test:dev` for watch mode
diff --git a/packages/website/.cursor/rules/website.mdc b/packages/website/.cursor/rules/website.mdc
@@ -0,0 +1,95 @@
+---
+description: Rules for the Spotlight documentation website
+globs:
+alwaysApply: true
+---
+
+# Website Package Guidelines
+
+This is the Spotlight documentation website built with Astro and Starlight.
+
+## Tech Stack
+
+- **Framework**: Astro 5 with Starlight documentation theme
+- **Styling**: Tailwind CSS v4 via `@tailwindcss/vite`
+- **Components**: Astro (`.astro`) for static content, React (`.tsx`) for interactive elements
+- **Content**: MDX files with frontmatter
+
+## Project Structure
+
+```
+src/
+├── components/          # Reusable components
+│   ├── docs/           # Documentation-specific components
+│   └── homepage/       # Landing page components
+├── content/
+│   ├── config.ts       # Content collection config
+│   └── docs/           # MDX documentation pages
+├── lib/                # Utility functions
+├── pages/              # Astro pages (index.astro)
+├── tailwind.css        # Tailwind entry point
+└── theme.css           # Custom theme styles
+public/                 # Static assets
+```
+
+## Documentation Pages
+
+MDX files in `src/content/docs/` require frontmatter:
+
+```mdx
+---
+title: Page Title
+description: Brief description for SEO
+sidebar:
+  order: 0  # Optional: controls sidebar position
+---
+
+Content here...
+```
+
+## Component Patterns
+
+### Astro Components (`.astro`)
+Use for static content, layouts, and server-rendered pages:
+
+```astro
+---
+import Layout from '../components/Layout.astro';
+const { title } = Astro.props;
+---
+
+<Layout title={title}>
+  <slot />
+</Layout>
+```
+
+### React Components (`.tsx`)
+Use for interactive elements that need client-side state:
+
+```tsx
+export default function InteractiveComponent({ prop }: { prop: string }) {
+  const [state, setState] = useState(false);
+  return <button onClick={() => setState(!state)}>{prop}</button>;
+}
+```
+
+## Configuration
+
+- `astro.config.mjs` - Astro configuration, Starlight sidebar, integrations
+- `tailwind.config.mjs` - Tailwind theme customization
+- `tsconfig.json` - TypeScript configuration
+
+## Starlight Features
+
+- Sidebar defined in `astro.config.mjs` under `starlight.sidebar`
+- Custom components override defaults via `starlight.components`
+- Use `@astrojs/starlight/components` for built-in components (Tabs, TabItem, etc.)
+
+## Commands
+
+```bash
+pnpm dev:website    # Start dev server (from root)
+pnpm dev            # Start dev server (from this directory)
+pnpm build          # Build for production
+pnpm preview        # Preview production build
+```
PATCH

echo "Gold patch applied."
