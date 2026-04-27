#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tokentracker

# Idempotency guard
if grep -qF "**macOS App (`TokenTrackerBar/`)** \u2014 Native Swift 5.9 menu bar + widget app. Emb" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -26,17 +26,17 @@ Token Tracker is a local-first AI token usage tracker. It collects token counts
 AI CLI Tools → hooks/notify.cjs trigger sync → rollout.js parses logs → queue.jsonl → local API → dashboard
 ```
 
-### Four Layers
+### Three Layers (this repo) + Cloud Backend (separate repo)
 
 **CLI (`src/`)** — Node.js CommonJS. Entry: `bin/tracker.js` → `src/cli.js` dispatches commands. Default command (no args) runs `serve` which auto-runs `init` on first use, then launches local HTTP server on port 7680.
 
 **Dashboard (`dashboard/`)** — React 18 + Vite 7 + TypeScript + TailwindCSS. Built to `dashboard/dist/` and served by the CLI's `serve` command. In local mode (`localhost`), skips auth and reads data from local API endpoints. Deployed to Vercel at token.rynn.me for cloud mode.
 
-**macOS App (`TokenTrackerBar/`)** — Native Swift 5.9 menu bar app. Embeds a complete Node.js + tokentracker runtime (`EmbeddedServer/`). Hosts the React dashboard via WKWebView and provides native UI panels (usage summary, heatmap, model breakdown, usage limits, Clawd companion). Built with XcodeGen.
+**macOS App (`TokenTrackerBar/`)** — Native Swift 5.9 menu bar + widget app. Embeds a complete Node.js + tokentracker runtime (`EmbeddedServer/`, universal arm64+x64). Hosts the React dashboard via WKWebView and provides native UI panels (usage summary, heatmap, model breakdown, usage limits, Clawd companion). Ships a `TokenTrackerWidget` WidgetKit target. Built with XcodeGen.
 
-**Backend (`insforge/`)** — InsForge Edge Functions for the cloud service. Handles cloud authentication, leaderboard, and data sync. Not needed for local-only usage.
+**Cloud backend** — InsForge Edge Functions live in a separate repo and are documented in `BACKEND_API.md`. Handles cloud authentication, leaderboard, and data sync. Not needed for local-only usage.
 
-### Supported AI Tools (8 providers)
+### Supported AI Tools (9 providers)
 
 | Tool | Hook Method | Parser |
 |------|------------|--------|
@@ -48,6 +48,7 @@ AI CLI Tools → hooks/notify.cjs trigger sync → rollout.js parses logs → qu
 | OpenClaw | Session plugin (modern) | Rollout JSONL |
 | Every Code | TOML notify array (same as Codex) | Rollout JSONL |
 | Kiro | SQLite + JSONL hybrid | Rollout JSONL |
+| Hermes Agent | SQLite sessions table (`~/.hermes/state.db`) | `parseHermesIncremental` |
 
 ### CLI Commands
 
@@ -64,41 +65,65 @@ AI CLI Tools → hooks/notify.cjs trigger sync → rollout.js parses logs → qu
 
 ### Key Source Files — CLI
 
-- `src/lib/rollout.js` (2907 lines) — Core parser. Handles all 8 log formats. Aggregates into 30-minute UTC buckets. Contains per-provider normalizers.
-- `src/lib/local-api.js` (951 lines) — Local API handler. Serves 11 endpoints under `/functions/tokentracker-*` and `/api/auth/*`.
-- `src/lib/usage-limits.js` (1092 lines) — Rate limit detection via API/CLI introspection for Claude, Codex, Cursor, Gemini, Kiro, Antigravity.
-- `src/commands/init.js` (907 lines) — First-time setup. Installs notify.cjs, copies runtime to `~/.tokentracker/app/`, configures hooks for all providers.
-- `src/commands/sync.js` (816 lines) — Parses all sources, queues hourly buckets, uploads in batches (max 5 batches × 200 records).
+- `src/lib/rollout.js` (3020 lines) — Core parser. Handles all 9 log formats. Aggregates into 30-minute UTC buckets. Contains per-provider normalizers + `parseHermesIncremental` for SQLite-backed Hermes sessions.
+- `src/lib/local-api.js` (961 lines) — Local API handler. Serves 11 endpoints under `/functions/tokentracker-*` and `/api/auth/*`.
+- `src/lib/usage-limits.js` (1151 lines) — Rate limit detection via API/CLI introspection for Claude, Codex, Cursor, Gemini, Kiro, Antigravity.
+- `src/commands/init.js` (912 lines) — First-time setup. Installs notify.cjs, copies runtime to `~/.tokentracker/app/`, configures hooks for all providers.
+- `src/commands/sync.js` (840 lines) — Parses all sources (including Hermes SQLite), queues hourly buckets, uploads in batches (max 5 batches × 200 records).
 - `src/commands/serve.js` — HTTP server. Port conflict resolution, CORS, SPA fallback.
 - `src/lib/cursor-config.js` — Extracts Cursor auth from local SQLite, fetches usage CSV.
 - `src/lib/codex-config.js` — Parse/update Codex & Every Code config.toml notify arrays.
+- `src/lib/opencode-config.js` / `src/lib/opencode-usage-audit.js` — OpenCode plugin install + SQLite audit.
+- `src/lib/openclaw-session-plugin.js` / `src/lib/openclaw-hook.js` — OpenClaw session plugin + legacy hook.
 - `src/lib/subscriptions.js` — Detect Claude Pro, ChatGPT plans via keychain/API.
+- `src/lib/project-usage-purge.js` — Purge/trim project-attribution state.
+- `src/lib/upload-throttle.js` — Per-device upload rate limiting.
+- `src/lib/tracker-paths.js` — Canonical paths under `~/.tokentracker/`.
 
 ### Key Source Files — Dashboard
 
-- `dashboard/src/App.jsx` — Router + auth gate. Localhost → dashboard directly; cloud → requires auth.
+- `dashboard/src/App.jsx` — Router + auth gate. Localhost → dashboard directly; cloud → requires auth. Lazy-loads all pages; `/ip-check`, `/leaderboard/:handle`, and the native-auth callback bypass the sidebar shell.
 - `dashboard/src/pages/DashboardPage.jsx` — Main dashboard (lazy-loaded). Period selector, usage panels, charts.
 - `dashboard/src/pages/LeaderboardPage.jsx` — Global token usage rankings with sortable columns.
+- `dashboard/src/pages/LeaderboardProfilePage.jsx` — Public user profile (standalone chrome; excluded from `AppLayout`).
 - `dashboard/src/pages/LandingPage.jsx` — Marketing/onboarding page.
+- `dashboard/src/pages/LimitsPage.jsx` — Dedicated usage-limits view (wrapped by `AppLayout`).
+- `dashboard/src/pages/SettingsPage.jsx` — User settings + progressive disclosure for account actions.
+- `dashboard/src/pages/WidgetsPage.jsx` — Widget gallery (macOS desktop widget previews).
+- `dashboard/src/pages/IpCheckPage.jsx` — Standalone Claude IP check tool with dark mode support.
+- `dashboard/src/pages/LoginPage.jsx` — Cloud-mode sign-in page.
+- `dashboard/src/pages/NativeAuthCallbackPage.jsx` — OAuth callback for the macOS WKWebView bridge.
+- `dashboard/src/ui/openai/components/Shell.jsx` / `Sidebar.jsx` — `AppLayout` sidebar shell used by most pages.
 - `dashboard/src/ui/matrix-a/views/DashboardView.jsx` — Main layout orchestrator.
 - `dashboard/src/ui/matrix-a/components/UsageLimitsPanel.jsx` — Rate limits display per AI tool.
 - `dashboard/src/ui/matrix-a/components/TrendChart.jsx` — Line/bar chart with Motion animations.
 - `dashboard/src/ui/matrix-a/components/ActivityHeatmap.jsx` — GitHub-style contribution calendar.
+- `dashboard/src/ui/share/ShareModal.tsx` + `variants/BroadsheetCard.jsx` + `variants/AnnualReportCard.jsx` — Shareable screenshot cards (Broadsheet + Neon annual-report variant with glassmorphism). `capture-share-card.ts` → html-to-image, `native-save.ts` dispatches to Swift via `NativeBridge`.
 - `dashboard/src/hooks/use-usage-data.ts` — Primary data fetching hook.
 - `dashboard/src/lib/api.ts` — HTTP client for local & cloud APIs.
-- `dashboard/src/lib/copy.ts` — i18n system reading from `content/copy.csv` (456 strings).
+- `dashboard/src/lib/copy.ts` — i18n system reading from `content/copy.csv` (~550 strings).
+- `dashboard/src/lib/native-bridge.js` — JS half of the Swift ↔ WebView bridge (`getSettings`, `setSetting`, `action`).
 - `dashboard/src/contexts/InsforgeAuthContext.jsx` — Cloud OAuth via InsForge SDK.
+- `dashboard/src/contexts/LoginModalContext.jsx` — Global sign-in modal controller.
 
 ### Key Source Files — macOS App
 
 - `TokenTrackerBar/TokenTrackerBarApp.swift` — Entry point. NSApplicationDelegateAdaptor manages StatusBarController, DashboardViewModel, ServerManager.
 - `TokenTrackerBar/Services/ServerManager.swift` — Embedded/system Node.js server lifecycle with health check polling.
 - `TokenTrackerBar/Services/StatusBarController.swift` — Menu bar popover UI + status icon animation.
 - `TokenTrackerBar/Services/DashboardWindowController.swift` — WKWebView hosting React dashboard.
+- `TokenTrackerBar/Services/NativeBridge.swift` — WKScriptMessageHandler bridging dashboard settings/actions to Swift.
+- `TokenTrackerBar/Services/APIClient.swift` — HTTP client against the embedded local server.
+- `TokenTrackerBar/Services/MenuBarAnimator.swift` — Status icon idle/activity animation.
+- `TokenTrackerBar/Services/LaunchAtLoginManager.swift` — `SMAppService.mainApp` wrapper with `@Published` state.
+- `TokenTrackerBar/Services/UpdateChecker.swift` — Polls npm registry for CLI updates.
+- `TokenTrackerBar/Services/WidgetSnapshotWriter.swift` — Writes App Group snapshots for the desktop widget.
 - `TokenTrackerBar/ViewModels/DashboardViewModel.swift` — All dashboard state. Auto-refresh every 5 minutes.
 - `TokenTrackerBar/Views/ClawdCompanionView.swift` — Animated pixel art companion with 9 states (DrawCtx + static draw methods).
 - `TokenTrackerBar/Views/UsageLimitsView.swift` — Native usage limits display.
+- `TokenTrackerBar/Views/UsageTrendChart.swift` / `TopModelsView.swift` / `SummaryCardsView.swift` / `ActivityHeatmapView.swift` — Native panel components. Charts module is hidden on macOS < 13 (the popover auto-shrinks).
 - `TokenTrackerBar/Models/LimitsSettingsStore.swift` — UserDefaults persistence for limit preferences.
+- `TokenTrackerBar/TokenTrackerWidget/` — Desktop widget target (WidgetKit) reading shared snapshots via App Group.
 
 ### Local API Endpoints
 
@@ -127,8 +152,8 @@ Query params: `from`, `to` (YYYY-MM-DD), `tz` (timezone), `tz_offset_minutes`, `
 ```json
 {
   "hour_start": "2026-04-05T14:00:00Z",
-  "source": "codex|claude|gemini|opencode|cursor|openclaw|kiro",
-  "model": "gpt-5.4|claude-opus-4-6|gemini-2.5-pro|...",
+  "source": "codex|claude|gemini|opencode|cursor|openclaw|kiro|every-code|hermes",
+  "model": "gpt-5.4|claude-opus-4-6|gemini-2.5-pro|hermes-agent|...",
   "input_tokens": 1000,
   "output_tokens": 500,
   "cached_input_tokens": 100,
@@ -152,36 +177,40 @@ Query params: `from`, `to` (YYYY-MM-DD), `tz` (timezone), `tz_offset_minutes`, `
 ### Dashboard Features
 
 - **Token usage tracking** — totals, cost estimation, breakdown by time/model/provider/project
-- **Usage limits** — rate limit tracking for Claude, Codex, Cursor, Gemini, Kiro, Antigravity
-- **Leaderboard** — global token usage rankings with user profiles
+- **Usage limits** — rate limit tracking for Claude, Codex, Cursor, Gemini, Kiro, Antigravity (dedicated `/limits` page)
+- **Leaderboard** — global token usage rankings with per-user profile pages (`/leaderboard/:handle`)
 - **Activity heatmap** — GitHub-style contribution calendar
 - **Trend charts** — line/bar charts with period selector (day/week/month/total/custom)
 - **Cost analysis** — modal with per-model pricing breakdown (70+ models)
 - **Cloud sync** — one-click sync local usage to cloud via InsForge
-- **Data sharing** — screenshot captures + public share links
+- **Share cards** — screenshot-ready Broadsheet + Neon annual-report variants via html-to-image; `native-save` bridge for macOS WKWebView copy/save
+- **Claude IP Check** — standalone `/ip-check` utility page (no auth, no sidebar)
+- **Widgets gallery** — `/widgets` preview of macOS desktop widgets
 - **Dark/light theme** — persisted to localStorage
 - **Clawd companion** — animated pixel art mascot with 9 animation states
-- **Copy system** — CSV-based i18n with 456 strings, validated by `validate:copy`
+- **Copy system** — CSV-based i18n (~550 strings in `dashboard/src/content/copy.csv`), validated by `validate:copy`
 
 ### macOS App Architecture
 
-- Swift 5.9, macOS 12.0+, XcodeGen project generation
+- Swift 5.9, macOS 12.0+ (Monterey supported), XcodeGen project generation
 - Menu bar app (LSUIElement: true), single-click → popover, double-click → full dashboard window
 - Embedded Node.js server (universal arm64+x64 binary) — self-contained, no external Node dependency
-- WKWebView hosts React dashboard with script messaging for OAuth
-- Native panels: summary cards, heatmap, model breakdown, usage limits, Clawd companion
+- WKWebView hosts React dashboard with script messaging for OAuth + settings bridge
+- Native panels: summary cards, heatmap, model breakdown, usage limits, Clawd companion (Charts panel hidden on macOS < 13)
+- WidgetKit target (`TokenTrackerWidget`) reads snapshots from App Group storage for desktop widgets
 - Auto-refresh every 5 minutes, server health check with exponential backoff
 - URL scheme: `tokentracker://` for OAuth callbacks
 
 ## Conventions
 
-- Package name: `tokentracker-cli` (npm), bin command: `tokentracker`
+- Package name: `tokentracker-cli` (npm), bin command: `tokentracker` (also `tracker`, `tokentracker-cli`, `tokentracker-tracker`)
+- Node engine: `>=20`
 - CommonJS throughout `src/` (no ESM)
-- Dashboard uses TypeScript + ESM
+- Dashboard uses TypeScript 5.9 (strict) + ESM
 - Environment variable prefix: `TOKENTRACKER_` (e.g., `TOKENTRACKER_DEBUG`, `TOKENTRACKER_DEVICE_TOKEN`)
 - Dashboard env prefix: `VITE_` (e.g., `VITE_INSFORGE_BASE_URL`, `VITE_TOKENTRACKER_MOCK`)
-- All user-facing text in `dashboard/src/content/copy.csv`
-- Platform: macOS-first
+- All user-facing text in `dashboard/src/content/copy.csv` — never hardcode strings; `validate:ui-hardcode` will catch regressions
+- Platform: macOS-first, but the CLI + dashboard work on Linux
 - UTC timestamps, half-hour bucket aggregation
 - Privacy: token counts only, never prompts or conversation content
 - Git commit messages in English, conventional commits style (feat/fix/refactor/chore/ci/docs/test)
@@ -289,14 +318,16 @@ One-line English summary, e.g. `Fix token stats inflation caused by duplicate qu
 
 ## Test Suite
 
-96 test files using Node.js built-in test runner (`node --test`). Key areas:
+~95 test files using Node.js built-in test runner (`node --test test/*.test.js`). Key areas:
 
-- **Rollout parser** — `test/rollout-parser.test.js` (comprehensive, covers all 8 providers)
+- **Rollout parser** — `test/rollout-parser.test.js` (comprehensive, covers all 9 providers including Hermes)
 - **CLI commands** — init, sync, status, doctor, diagnostics, uninstall
 - **Integrations** — codex-config, cursor-config, openclaw, opencode
-- **Dashboard** — layout, identity, link codes, auth guards, TypeScript guardrails
-- **Models** — model-breakdown, usage-limits, subscriptions, mock data
+- **Dashboard** — layout, identity, link codes, auth guards, TypeScript + ESLint guardrails, render order, screenshot/visual baselines
+- **Models** — model-breakdown, usage-limits, subscriptions, mock data, leaderboard mock
+- **Share card** — `share-card-data.test.js` for the share-card data builder
 - **CI/CD** — npm-publish-workflow, release-dmg-workflow, architecture-guardrails
+- **Graph / SCIP** — `graph-auto-index-*.test.js` for the code-graph indexing pipeline
 - **Helpers** — `test/helpers/load-dashboard-module.js` for loading ESM dashboard modules in CJS tests
 
 ## OpenSpec Workflow
PATCH

echo "Gold patch applied."
