#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotency guard
if grep -qF "**Note on typed vs untyped calls.** Skills currently uses `client.extMethod(\"_go" "ui/goose2/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui/goose2/AGENTS.md b/ui/goose2/AGENTS.md
@@ -131,16 +131,61 @@ ThemeProvider manages three axes:
 - `tauri-plugin-window-state` persists window size and position.
 - Traffic light offset: `pl-20` (80px) to accommodate macOS window controls.
 
-## Backend Architecture
+## Architecture
 
-All AI communication goes through **ACP (Agent Client Protocol)**:
-- The Tauri app starts a long-lived `goose serve` process and exposes its WebSocket URL.
-- The frontend connects directly to `goose serve` over WebSocket and handles ACP notifications in TypeScript.
+**All frontend ↔ backend communication in goose2 flows through a single path:**
 
-For non AI communication, such as configuration:
-- Use **Tauri commands** (`invoke()` from `@tauri-apps/api/core`) for request/response operations (sessions, personas, skills, projects, etc.).
-- Use **Tauri events** (`listen()` from `@tauri-apps/api/event`) for streaming data from ACP.
-- Do **not** add HTTP fetch calls to a backend server, `apiFetch` utilities, or sidecar process management.
+```
+React UI  ──►  @aaif/goose-sdk (TS)  ──►  goose-acp  (WebSocket, ACP)  ──►  goose (core)
+```
+
+- The Tauri shell spawns a long-lived `goose serve` process and exposes its WebSocket URL via the `get_goose_serve_url` Tauri command. That is essentially the only Tauri command the frontend needs for backend work — it is how the renderer discovers the ACP endpoint.
+- The frontend opens a WebSocket to `goose serve` and talks to it using `@aaif/goose-sdk` (published from `ui/sdk/`). The SDK is generated from the ACP custom-method definitions in `crates/goose-sdk/src/custom_requests.rs`, so every backend method has a typed TypeScript client method.
+- `goose-acp` (`crates/goose-acp/src/server.rs`) is the server side of the WebSocket. It implements handlers for the custom ACP methods and calls into the `goose` core crate to do the actual work (providers, config, sessions, dictation, etc.).
+- `goose` is the pure domain crate. It knows nothing about Tauri or WebSockets — it just exposes Rust APIs that `goose-acp` handlers invoke.
+
+**This is the pattern you must follow when adding any new backend-touching feature.** When you are vibecoding in this app, it is very tempting to reach for `invoke()` or add an HTTP fetch — don't. The rule is: if a feature needs to talk to `goose` core, it goes through the SDK → ACP → goose chain above.
+
+### The canonical example: skills-as-sources (PR #8675)
+
+The skills → sources migration in [#8675](https://github.com/block/goose/pull/8675) is the clearest illustration of the rule. **It deleted 319 lines of Tauri-command code in `src-tauri/src/commands/skills.rs` and replaced them with ACP custom methods.** If you find yourself wanting to add an `invoke()` command that proxies to `goose`, that PR is what "doing it the other way" looks like. Copy this shape when adding new endpoints:
+
+1. **Define the request/response in `crates/goose-sdk/src/custom_requests.rs`.** Use the `JsonRpcRequest` / `JsonRpcResponse` derives and the `#[request(method = "_goose/<area>/<action>", response = ...)]` attribute. Sources uses namespaced methods like `_goose/sources/create`, `_goose/sources/list`, `_goose/sources/update`, `_goose/sources/delete`, `_goose/sources/export`, `_goose/sources/import` with paired request/response structs (`CreateSourceRequest` / `CreateSourceResponse`, etc.).
+2. **Implement the handler in `crates/goose-acp/src/server.rs`** with `#[custom_method(YourRequest)]`. Keep it thin: unpack the request, call into the `goose` crate, wrap the result. The sources handlers are ~5 lines each — e.g. `on_list_sources` just calls `goose::sources::list_sources(...)` and returns the typed response. Errors map to `sacp::Error::invalid_params()` / `internal_error()`.
+3. **Put the real logic in the `goose` crate.** Sources lives in `crates/goose/src/sources.rs` — filesystem CRUD, frontmatter parsing, scope resolution, all of it. `goose-acp` knows nothing about where skills are stored on disk; it just forwards typed arguments. This separation is the point.
+4. **Regenerate the SDK.** The TS methods on `GooseClient` are generated into `ui/sdk/src/generated/`. Do not hand-edit generated files.
+5. **Call it from the frontend via a feature `api/` module.** See `ui/goose2/src/features/skills/api/skills.ts`. It calls `getClient()` from `acpConnection.ts` and invokes the SDK, then adapts the generic `SourceEntry` shape into a feature-friendly `SkillInfo`:
+   ```ts
+   export async function listSkills(): Promise<SkillInfo[]> {
+     const client = await getClient();
+     const raw = await client.extMethod("_goose/sources/list", { type: "skill" });
+     const sources = (raw.sources ?? []) as SourceEntry[];
+     return sources.map(toSkillInfo);
+   }
+   ```
+   Feature code (hooks, stores, UI) imports from that `api/` module — it never touches the ACP client directly.
+
+**Note on typed vs untyped calls.** Skills currently uses `client.extMethod("_goose/sources/...", ...)` (the untyped escape hatch) because it reshapes a generic `Source` API into skill-specific types. The **preferred** shape for new features is the typed generated methods — `client.goose.GooseFooBar({ ... })` — as used by dictation (`client.goose.GooseDictationTranscribe`) and the provider inventory (`client.goose.GooseProvidersList`). Reach for `extMethod()` only when you have a real reason to bypass the generated types.
+
+For a minimal frontend `api/` wrapper using the typed shape, see `ui/goose2/src/features/providers/api/inventory.ts` — ~30 lines, typed SDK calls, thin adapter. For a fully worked end-to-end feature including OS-keychain handling and progress streaming, see the voice dictation feature ([#8609](https://github.com/block/goose/pull/8609)) and `ui/goose2/src/shared/api/dictation.ts`.
+
+### When `invoke()` is still appropriate
+
+Tauri commands (`invoke()` from `@tauri-apps/api/core`) are reserved for things that genuinely belong to the desktop shell, not to `goose` core. In practice that means:
+
+- `get_goose_serve_url` — bootstrapping the ACP connection.
+- Secret storage owned by the OS keychain (e.g. `save_provider_field`, `delete_provider_config` — note dictation still uses these for writing API keys into the OS keychain, because that's a shell concern).
+- Window state, filesystem dialogs, and other Tauri-plugin-backed capabilities.
+
+If the thing you're building is "get data from goose" or "tell goose to do something," it is **not** one of these cases. Add a custom ACP method instead.
+
+### Don't
+
+- Don't add HTTP `fetch` calls to a `goose` HTTP API, or reintroduce an `apiFetch` utility. There is no HTTP API for goose2 — the backend is the ACP WebSocket.
+- Don't manage a sidecar `goose` process from the renderer. The Tauri shell owns that lifecycle.
+- Don't add a new `invoke()` command in `src-tauri/` as a proxy to `goose` core. Add an ACP custom method instead.
+- Don't hand-edit `ui/sdk/src/generated/`. Regenerate.
+- Don't call the ACP client (`getClient()`) directly from UI components or stores. Go through a `shared/api/*.ts` (or `features/<feature>/api/*.ts`) module so the SDK surface is mockable in tests.
 
 ## Tooling
 
PATCH

echo "Gold patch applied."
