#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibesos

# Idempotency guard
if grep -qF "The real flow: the editor sends a `{ type: 'generate', ... }` WebSocket message," "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -15,6 +15,7 @@
 | Editing auth components | `.claude/rules/auth-components.md` loads automatically |
 | Editing templates or build system | `.claude/rules/template-build.md` loads automatically |
 | Working on sharing/invites | `.claude/rules/sharing-architecture.md` loads automatically |
+| Working on generate/chat/theme server flow | See "Generate Flow Routing" below before editing `handlers/` |
 
 ### TinyBase API Reference
 
@@ -119,6 +120,25 @@ For subdomain routing tests, add to `/etc/hosts`:
 ```
 Then `npm run test:e2e:server` and open `http://test-app.local:3000`.
 
+## Generate Flow Routing
+
+**Landmine warning.** The editor's "generate" action does NOT route through `scripts/server/handlers/generate.ts:handleGenerate`. That handler exists but has zero call sites — it's effectively dead code. Grep before editing.
+
+The real flow: the editor sends a `{ type: 'generate', ... }` WebSocket message, which is handled in `scripts/server/ws.ts` at `case 'generate':` (around line 328). That branch wraps the user's prompt inside a brainstorm prompt (via `buildBrainstormPrompt`) and sends it through the **persistent bridge** (`createBridge` in `scripts/server/claude-bridge.ts`) via `b.sendMessage(...)`. The persistent bridge is used — not a one-shot subprocess — because the brainstorm Q&A is multi-turn: Claude asks clarifying questions, the user answers, and eventually Claude produces the brief and starts writing. All of that must happen in a single conversation.
+
+Chat iteration (`case 'chat':`) uses the same bridge — so the bridge's per-turn state needs to be reset between generate and chat turns. That's what `bridge.setTurnMode('generate' | 'chat', initialStage?)` is for — call it before every `sendMessage`.
+
+Stream-event translation has two parallel paths:
+
+| Path | Used by | Translator | UI events emitted |
+|---|---|---|---|
+| Persistent bridge | generate, chat, theme | `translateStreamEvent` (event-translator.ts) | `tool_start`, `token`, `tool_result`, `init`, `complete`, `status` |
+| One-shot (`runOneShot`) | theme switcher, factory-assemble, riff | `dispatchStreamEvent` | `tool_detail`, `generation_stage`, `preview_reload`, `preview_reload_failed` |
+
+Direction D's staged-preview events (`generation_stage` / `preview_reload` / `reference_preview`) are emitted by the bridge's stream parser, gated by `turnMode === 'generate'`, so they fire on the real editor generate flow. If you add generate-UX events in the future, emit them from the bridge, not from `runOneShot`.
+
+Before claiming a generate-flow feature works end-to-end: verify in the browser DevTools Console that the expected event types show up in `[WS-IN]` logs. Unit tests of `runOneShot` / `dispatchStreamEvent` do NOT exercise this path.
+
 ## Non-Obvious Files
 
 | File | Why it matters |
@@ -128,6 +148,10 @@ Then `npm run test:e2e:server` and open `http://test-app.local:3000`.
 | `scripts/lib/auth-constants.js` | Hardcoded OIDC authority and client ID (shared Pocket ID instance) |
 | `scripts/lib/env-utils.js` | Shared env utilities and config |
 | `scripts/lib/paths.js` | Centralized path resolution for all plugin paths |
+| `scripts/server/ws.ts` | WebSocket router — `case 'generate':` / `case 'chat':` / `case 'theme':` dispatch. The actual generate flow lives here, not in `handlers/generate.ts`. |
+| `scripts/server/claude-bridge.ts` | Persistent stream-json bridge (`createBridge`) — used for all multi-turn flows. Holds per-turn state via `setTurnMode`. Emits Direction D staged-preview events. |
+| `scripts/server/event-translator.ts` | Translates raw stream-json into UI events for the persistent bridge (`tool_start`, etc.). Separate from `dispatchStreamEvent` which belongs to `runOneShot`. |
+| `scripts/server/handlers/generate.ts` | **Unused in production.** `handleGenerate` exists but has no call sites; the real generate flow is in `ws.ts`. Don't edit this file expecting changes to affect generation. |
 | `skills/launch/LAUNCH-REFERENCE.md` | Launch dependency graph, timing, skip modes |
 | `skills/launch/prompts/builder.md` | Builder agent prompt template with {placeholder} markers |
 | `scripts/deploy-cloudflare.js` (asset discovery) | Auto-discovers app-level `assets/` directory and includes files in deploy payload |
PATCH

echo "Gold patch applied."
