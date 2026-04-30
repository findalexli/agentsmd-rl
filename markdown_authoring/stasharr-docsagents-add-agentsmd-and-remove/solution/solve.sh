#!/usr/bin/env bash
set -euo pipefail

cd /workspace/stasharr

# Idempotency guard
if grep -qF "This document is a quick, practical guide for agentic coding assistants working " "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,143 @@
+# AGENTS.md
+
+This document is a quick, practical guide for agentic coding assistants working in this repository. It summarizes how the project is structured, where to make changes, how to validate them, and how to ship them safely with the repo’s conventions and tooling.
+
+## Project Snapshot
+
+- Type: Browser userscript that augments StashDB and integrates with Whisparr v3+
+- Framework: SolidJS + TypeScript
+- Build: Webpack (webpack-userscript)
+- Styles: SCSS + Bootstrap
+- Quality: ESLint + Prettier + Husky + commitlint (Conventional Commits)
+- Package manager: npm
+
+Key value props:
+
+- One‑click scene actions and bulk actions
+- Progress modal for bulk feedback (noisy toasts avoided in bulk flows)
+- Service layer separation for StashDB/Whisparr calls
+
+## Common Commands
+
+- Install deps: `npm ci`
+- Dev server (proxy userscript): `npm run dev`
+- Build production userscript: `npm run build`
+- Lint + autofix: `npm run lint`
+- Conventional commit helper: `npm run cm`
+
+Husky + commitlint enforce Conventional Commits and body line length in commit messages.
+
+## Codebase Map (where to change what)
+
+- UI entry (bulk actions): `src/components/BulkActionDropdown.tsx`
+
+  - Owns the Stasharr Actions dropdown and confirmation modals
+  - Starts/updates bulk progress via FeedbackService
+  - Uses StashDBService for titles and SceneService for work
+
+- Progress UI: `src/components/ProgressModal.tsx`
+
+  - Renders overall progress, item statuses, skipped info, and empty-state infoMessage
+
+- Feedback + operations state: `src/service/FeedbackService.ts`
+
+  - Global state source for ProgressModal
+  - Methods returned by `startBulkOperation`: `updateItem`, `addItems`, `removeItem`, `updateItemName(s)`, `setSkippedInfo`, `setInfo`, `complete`
+  - Button state helpers: `startButtonOperation`, `completeButtonOperation`
+
+- Scene domain logic: `src/service/SceneService.ts`
+
+  - Lookup/add/search flows
+  - Bulk orchestration helpers (`lookupAndAddAll`, `triggerWhisparrSearchAll`, `addAllMissingScenes`)
+  - Accepts `{ suppressToasts?: boolean }` where appropriate to keep bulk UX clean
+
+- Comparison logic: `src/service/SceneComparisonService.ts`
+
+  - Cross-checks StashDB vs. Whisparr and computes missing scenes
+  - Supports `suppressToasts` in bulk flows
+
+- StashDB GraphQL: `src/service/StashDBService.ts`
+
+  - `getSceneById(id)` via GraphQL `findScene`
+  - `getSceneTitlesByIds(ids)` resolves titles by ID (no text “OR” search)
+  - All queries support `suppressToasts`
+
+- Whisparr REST: `src/service/WhisparrService.ts`
+  - `getAllScenes`, `command`, profiles, etc. (`suppressToasts` supported in bulk)
+
+## Patterns and Conventions
+
+Coding
+
+- Keep changes minimal and targeted; prefer surgical edits over large refactors
+- Follow existing style and component organization
+- Avoid introducing new global state—extend FeedbackService if you need bulk UI changes
+- Prefer in-place updates (e.g., update item names by ID) instead of remove+add cycles
+
+UX rules of thumb
+
+- Bulk operations use the Progress Modal for all detailed feedback
+- Use `setSkippedInfo(count, "already in Whisparr")` to summarize skips
+- For “nothing to do” cases, start a bulk op with no items and set `setInfo("No scenes available …")` then `complete()`; do not add dummy “success” items
+- Titles shown in progress should be Scene Titles (via StashDB by ID), not hashes
+
+Toasts
+
+- Bulk flows: avoid toasts; rely on the modal and per‑item messages
+- Non-bulk flows: toasts are fine for quick feedback
+
+Commits & PRs
+
+- Conventional commits required; keep body lines ≤ 100 chars
+- Group commits by logical change:
+  - `feat(stashdb): add getSceneById …`
+  - `feat(actions,ui): … modal feedback …`
+  - `fix(ui): … empty-state …`
+  - `chore(lint): … ts-expect-error …`
+- Use GitHub CLI for PRs: `gh pr create --base main --head <branch> --title "feat(...): ..."`
+
+## Typical Agent Flows
+
+Add/improve a bulk action
+
+1. Update `BulkActionDropdown.tsx` to collect scene IDs and open a bulk operation
+2. If you need more progress data, add methods/fields in `FeedbackService`
+3. Use `StashDBService.getSceneById` or `getSceneTitlesByIds` to show titles
+4. Call into `SceneService` for the behavior (lookup/add/search)
+5. Ensure skipped info and empty-state are handled; keep toasts suppressed
+
+Display/UX change for bulk progress
+
+1. Adjust `ProgressModal.tsx` (e.g., sections guarded by item count)
+2. Pass any new props from `SceneList.tsx` reading FeedbackService state
+3. Extend `FeedbackService` to expose new state/methods
+
+Service/API work
+
+1. Implement in `StashDBService` or `WhisparrService`
+2. Return typed data; catch and log errors; use `suppressToasts` where caller is bulk
+3. Thread options through upstream services that call you
+
+## Validation Checklist
+
+- `npm run lint` passes (eslint + prettier)
+- No stray `@ts-ignore` (use `@ts-expect-error` with rationale when needed)
+- Commit messages follow Conventional Commits and commitlint constraints
+- Bulk UI:
+  - Progress shows titles, per-item statuses
+  - Skipped info says “already in Whisparr”
+  - Empty-state shows info, not “1/1 succeeded”
+
+## Dev Setup (for local manual testing)
+
+1. `npm run dev` (webpack dev server)
+2. Install `http://localhost:8080/stasharr.dev.proxy.user.js` in Tampermonkey/Violentmonkey
+3. Reload StashDB; iteratively test bulk actions and UI
+
+## Notes for Sandboxed Agents
+
+- Use fast file/text search: `rg`
+- Read files in ≤ 250‑line chunks to avoid truncation
+- Edit files via `apply_patch` only
+- Prefer not to install new tools unless necessary
+- Pushing branches / making PRs is supported via `gh` CLI when credentials exist
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,112 +0,0 @@
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-Stasharr is a userscript that integrates StashDB with Whisparr (v3+) and Stash applications. It allows users to add scenes from StashDB directly to Whisparr and provides monitoring capabilities for studios and performers.
-
-## Tech Stack
-
-- **Framework**: SolidJS with TypeScript
-- **Build Tool**: Webpack with webpack-userscript plugin
-- **Styling**: SCSS with Bootstrap integration
-- **Code Quality**: ESLint, Prettier, Husky for git hooks
-- **Package Manager**: npm
-- **Target**: Browser userscript (Tampermonkey/Violentmonkey)
-
-## Development Commands
-
-```bash
-# Install dependencies
-npm ci
-
-# Start development server with hot reload
-npm run dev
-
-# Build production userscript
-npm run build
-
-# Lint and fix code
-npm run lint
-
-# Commit with conventional commits
-npm run cm
-```
-
-## Architecture Overview
-
-### Entry Point
-
-- `src/index.tsx`: Main entry point that initializes all controllers
-- Controllers are instantiated with a shared `Config` instance
-
-### Core Architecture Patterns
-
-**Controller Pattern**: Each page type has a dedicated controller:
-
-- `NavbarController`: Handles navigation elements
-- `PerformerController`: Manages performer pages
-- `StudioController`: Handles studio pages
-- `ScenesListController`: Manages scene listing pages
-- `CardController`: Handles scene cards
-- `DetailsController`: Manages scene detail pages
-
-**Observer Pattern**: Uses `MutationObserverFactory` to watch for DOM changes and react accordingly via `MutationHandler` implementations.
-
-**Service Layer**: API interactions are handled by service classes:
-
-- `WhisparrService`: Whisparr API integration
-- `StashSceneService`: Stash GraphQL API
-- `ServiceBase`: Base class with common HTTP request functionality
-
-### Key Components Structure
-
-```
-src/
-├── controller/          # Page-specific controllers using MutationObserver pattern
-├── components/          # SolidJS React components for UI elements
-├── service/            # API service layer for Whisparr/Stash integration
-├── mutation-handlers/  # DOM mutation event handlers
-├── builder/           # Payload builders for API requests
-├── models/            # Configuration and data models with Zod validation
-├── contexts/          # SolidJS contexts for state management
-├── enums/            # TypeScript enums for constants
-├── types/            # TypeScript type definitions
-├── styles/           # SCSS stylesheets with Bootstrap integration
-└── util/             # Utility functions
-```
-
-### Configuration System
-
-- `Config` class manages user settings with persistence via `GM_setValue`/`GM_getValue`
-- Zod validation schemas in `ConfigValidation.ts` ensure type safety
-- Settings include Whisparr/Stash API credentials, quality profiles, root folders
-
-### Build Process
-
-- Webpack bundles TypeScript/SolidJS into a single userscript file
-- Development mode creates proxy script for hot reloading
-- Production mode minifies and optimizes the output
-- `metadata.js` defines userscript headers and permissions
-
-### Userscript Integration
-
-- Uses Greasemonkey/Tampermonkey APIs (`GM_*` functions)
-- Targets `stashdb.org` domain exclusively
-- Requires permissions for cross-origin requests to user's Whisparr/Stash instances
-
-## Development Setup
-
-1. Enable Tampermonkey access to local file URIs
-2. Run `npm run dev` to start webpack dev server on port 8080
-3. Install the proxy script from `http://localhost:8080/stasharr.dev.proxy.user.js`
-4. Changes auto-recompile; reload userscript in browser to see updates
-
-## Testing
-
-No specific test framework is configured. Manual testing is done by:
-
-1. Installing the development userscript
-2. Navigating to StashDB and testing functionality
-3. Verifying integration with Whisparr/Stash instances
PATCH

echo "Gold patch applied."
