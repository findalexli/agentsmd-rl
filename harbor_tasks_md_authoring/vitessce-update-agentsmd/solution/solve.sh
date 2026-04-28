#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitessce

# Idempotency guard
if grep -qF "- Test files are co-located with source, named `*.test.js`, `*.test.ts`, `*.test" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -13,7 +13,7 @@ This repository is organized as a monorepo that contains NPM packages, websites
 ## Naming Conventions
 
 - **Directories**: lowercase with dashes (`view-types/feature-list/`)
-- **Components**: PascalCase (`DashboardMenu.tsx`)
+- **Components**: PascalCase (`FeatureList.tsx`)
 - **Variables and Props**: descriptive with auxiliary verbs (`isLoading`, `hasError`, `canSubmit`). no negation in names (i.e., prefer `enableFeature: false` rather than `disableFeature: true`)
 
 
@@ -37,41 +37,64 @@ This project uses **pnpm workspaces**. Packages live under `packages/`. Key pack
 - `packages/globals` - Defines getters and setters for global state such as debugMode and logLevel (`getDebugMode`, `getLogLevel`, `atLeastLogLevel`).
 - `packages/main/all` — Meta-package that defines the base set of plugins and the top-level `<Vitessce/>` React component.
 
+The repository contains web apps for under `sites/`:
+- `sites/demo/` - Development website to test demo/example Vitessce configurations.
+- `sites/docs/` - Documentation website built with Docusaurus.
 
-## Common Commands
+
+
+## Development Workflow: Essential Commands
 
 All commands are run from the repository root unless otherwise noted.
 
 ```bash
-pnpm install          # Install dependencies
-pnpm run build        # Build all packages
-pnpm run start-demo   # Run the development server
-pnpm run clean-start  # Clean node_modules and start the development server
-pnpm run lint         # Lint
-pnpm run lint-fix     # Fix a subset of linting errors
-pnpm run test         # Run unit tests
+# Setup (requires PNPM v9.5+, NodeJS v18.6.0)
+pnpm install && pnpm run build && pnpm run start-demo
+
+# Testing
+./scripts/test.sh          # Full test suite (lint + unit + e2e)
+pnpm run test              # Unit tests only
+pnpm run lint-fix          # Fix linting issues
+
+# Changesets (never edit CHANGELOG.md directly)
+pnpm changeset             # Add changeset for changes
+
+# Clean node_modules and start the development server
+pnpm run clean-start
+
+# Create new view type
+pnpm run create-view line-plot
 ```
 
-For more details, see `README.md`.
+### Build System
+
+- TypeScript compilation: `tsc --build` (root) builds all packages via project references
+- Exceptions use custom Vite/Rollup configs: `@vitessce/icons`, `@vitessce/workers`, `@vitessce/dev`
+- Output: `dist-tsc/` (dev), `dist/` (production bundles)
+
+
+For more details, see `README.md` and `dev-docs/monorepo-and-bundling.md`.
+
 
 ## Testing
 
-- **Framework**: [Vitest](https://vitest.dev/)
-- **Test files**: Co-located with source, named `*.test.js`, `*.test.ts`, `*.test.jsx`, or `*.test.tsx` (use `.jsx`/`.tsx` for files containing JSX).
-- **Fixture files**: Large mock data is factored into co-located `*.test.fixtures.js` files.
+- Uses the Vitest framework.
+- Test files are co-located with source, named `*.test.js`, `*.test.ts`, `*.test.jsx`, or `*.test.tsx` (use `.jsx`/`.tsx` for files containing JSX).
 - Import `{ describe, it, expect }` from `vitest`.
-- No mocking frameworks are typically used — tests use real functions with simple inline mock data.
+- Toy data fixtures are factored into co-located `*.test.fixtures.js` files.
 
 
 ## Code Style & Conventions
 
 - **Language**: TypeScript (`.ts`, `.tsx`) is preferred for new code; legacy code may be `.js`/`.jsx`, with or without JSDoc comments for types.
 - **React**: Functional components with hooks. No class components in new code. Prefer `useMemo` over useState/useEffect.
-- **Imports**: Use named exports. Avoid default exports in new code.
+- **Exports**: Use named exports. Avoid default exports in new code.
+- **Imports**: Avoid non-standard imports (CSS, JSON) - use JS files instead
 - **Formatting**: Follow the existing ESLint rules. No separate Prettier config—ESLint handles style.
 - **NO CSS ALLOWED**: Use JSS-based `makeStyles` from `@vitessce/styles` (see [Styling snippet](#styling-jss-via-makestyles) below).
 - **Material UI**: MUI components and icons are re-exported from `@vitessce/styles`. Reuse MUI components when possible.
 - **Colors**: Prefer `[r, g, b]` color representations, and only convert to strings at the "last second".
+- **Dependency version consistency**: External dependencies via PNPM catalogs for version consistency
 
 ## Plugin Architecture
 
@@ -86,12 +109,20 @@ The type interface for plugins is defined in `packages/plugins/src/index.ts`.
 
 ### View Type Two-Component Pattern
 
-Every view type follows a **Subscriber + Presentational** split:
+Every view follows a **two-component pattern**:
 
-| Layer | Name Pattern | Responsibility |
-|---|---|---|
-| **Subscriber** (container) | `FooSubscriber` | Wires up coordination state, data loaders, loading status, and errors. This is the component registered as a plugin. |
-| **Presentational** (view) | `Foo` | Pure rendering. Receives only plain props. No knowledge of coordination or loaders. |
+1. **Subscriber component** (`*Subscriber.js`) - handles coordination and data loading
+2. **Child component** - pure rendering logic
+
+```jsx
+<FeatureListSubscriber>
+  {" "}
+  {/* Handles useCoordination, data hooks */}
+  <TitleInfo>
+    <FeatureList /> {/* Pure component with props */}
+  </TitleInfo>
+</FeatureListSubscriber>
+```
 
 Subscriber components follow this structure (see [full example](#subscriber-component-example) below):
 1. Destructure props (`coordinationScopes`, `theme`, `title`, `removeGridComponent`, etc.)
@@ -119,12 +150,14 @@ Many configuration examples can be found in `examples/configs`.
 
 ## Coordination Model
 
-Views communicate through a **coordination space**:
+Vitessce uses a **coordination model** for state management between components. Views communicate through a **coordination space**:
 
 - A **coordination type** is a named parameter (e.g., `obsSetSelection`).
 - A **coordination scope** is a named instance of a coordination type with a value.
 - Views subscribe to scopes; when one view updates a scope's value, all other views on the same scope react.
 
+Internally, this is implemented using Zustand.
+
 ### Key Constants (from `@vitessce/constants-internal`)
 
 - **`CoordinationType`** — Object in `@vitessce/constants-internal` mapping `UPPER_SNAKE_CASE` keys to `camelCase` string values (e.g., `CoordinationType.OBS_SET_SELECTION` → `'obsSetSelection'`).
@@ -151,6 +184,9 @@ Data source and data loader classes are defined in sub-packages in `packages/fil
 These are instantiated by the `createLoaders` function which is defined in `packages/vit-s/src/vitessce-grid-utils.js`.
 The `createLoaders` function is executed by the `<VitS/>` component which is defined in `packages/vit-s/src/VitS.js`.
 
+React hooks for data loading (using React-Query) are defined in `packages/vit-s/src/data-hooks.js`
+
+
 ### DataSource / DataLoader Architecture
 
 File type plugins follow a two-layer pattern:
@@ -278,37 +314,32 @@ Minimal complete Subscriber (`packages/view-types/status/src/StatusSubscriber.js
 ```js
 import React from 'react';
 import {
-  TitleInfo, useCoordination, useWarning,
+  TitleInfo,
+  useCoordination,
   useCoordinationScopes,
 } from '@vitessce/vit-s';
 import { ViewType, COMPONENT_COORDINATION_TYPES, ViewHelpMapping } from '@vitessce/constants-internal';
-import Status from './Status.js';
+import { HeatmapPlot } from './HeatmapPlot.js';
 
-export function StatusSubscriber(props) {
+export function HeatmapPlotSubscriber(props) {
   const {
     coordinationScopes: coordinationScopesRaw,
     closeButtonVisible,
     removeGridComponent,
     theme,
-    title = 'Status',
-    helpText = ViewHelpMapping.STATUS,
+    title = 'Heatmap',
+    helpText = ViewHelpMapping.HEATMAP,
   } = props;
 
   const coordinationScopes = useCoordinationScopes(coordinationScopesRaw);
 
   const [{
-    obsHighlight: cellHighlight,
-    featureHighlight: geneHighlight,
-    moleculeHighlight,
-  }] = useCoordination(COMPONENT_COORDINATION_TYPES[ViewType.STATUS], coordinationScopes);
-
-
-  const infos = [
-    ...(cellHighlight ? [`Hovered cell ${cellHighlight}`] : []),
-    ...(geneHighlight ? [`Hovered gene ${geneHighlight}`] : []),
-    ...(moleculeHighlight ? [`Hovered gene ${moleculeHighlight}`] : []),
-  ];
-  const info = infos.join('; ');
+    obsHighlight,
+    featureHighlight,
+  }, {
+    setObsHighlight,
+    setFeatureHighlight,
+  }] = useCoordination(COMPONENT_COORDINATION_TYPES[ViewType.HEATMAP], coordinationScopes);
 
   return (
     <TitleInfo
@@ -320,7 +351,12 @@ export function StatusSubscriber(props) {
       isReady
       helpText={helpText}
     >
-      <Status info={info} />
+      <HeatmapPlot
+        obsHighlight={obsHighlight}
+        setObsHighlight={setObsHighlight}
+        featureHighlight={featureHighlight}
+        setFeatureHighlight={setFeatureHighlight}
+      />
     </TitleInfo>
   );
 }
@@ -350,7 +386,7 @@ const urls = useUrls([embeddingUrls, obsSetsUrls]);
 const errors = [embeddingError, obsSetsError];
 ```
 
-### `TitleInfo` wrapper
+### `TitleInfo` wrapper component
 
 `TitleInfo` is the standard shell for every view type (title bar, spinner, error indicator, download button, settings popover, help tooltip):
 
@@ -439,3 +475,26 @@ export const myConfig = {
   ],
 };
 ```
+
+### VitessceConfig API
+
+- Programmatic config creation via `packages/config/src/VitessceConfig.js`
+- JSON schema validation in `packages/json-schema/`
+
+### Schema Versioning
+
+- Increment schema version for new coordination types
+- Provide upgrade functions for backward compatibility
+
+## Common Pitfalls
+
+- Never edit `CHANGELOG.md` directly - use changesets
+- Check `COMPONENT_COORDINATION_TYPES` when adding coordination dependencies
+
+## Examples to Study
+
+- `packages/view-types/feature-list/` - Simple subscriber/child pattern
+- `packages/file-types/csv/` - Simple data loading
+- `packages/file-types/zarr/` - Complex data loading
+- `packages/config/src/VitessceConfig.js` - Configuration API
+- `scripts/create-view.mjs` - Code generation patterns
\ No newline at end of file
PATCH

echo "Gold patch applied."
