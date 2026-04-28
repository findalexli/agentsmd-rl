#!/usr/bin/env bash
set -euo pipefail

cd /workspace/win-codexbar

# Idempotency guard
if grep -qF "- Be conservative with secret handling (manual cookies, API keys, token accounts" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,40 +1,55 @@
 # Repository Guidelines
 
+## Current Project State
+- This repository currently ships a Windows port of CodexBar implemented in Rust (`rust/`).
+- Many files in `docs/` and some workflows reference the upstream macOS/Swift project. Treat those as historical or
+  upstream-sync material unless the task is explicitly about upstream parity.
+- When repo docs conflict, trust the active Rust sources in `rust/src` and the Rust manifests (`rust/Cargo.toml`).
+
 ## Project Structure & Modules
-- `Sources/CodexBar`: Swift 6 menu bar app (usage/credits probes, icon renderer, settings). Keep changes small and reuse existing helpers.
-- `Tests/CodexBarTests`: XCTest coverage for usage parsing, status probes, icon patterns; mirror new logic with focused tests.
-- `Scripts`: build/package helpers (`package_app.sh`, `sign-and-notarize.sh`, `make_appcast.sh`, `build_icon.sh`, `compile_and_run.sh`).
-- `docs`: release notes and process (`docs/RELEASING.md`, screenshots). Root-level zips/appcast are generated artifacts—avoid editing except during releases.
+- `rust/src`: Main application code (CLI, providers, tray, native UI, browser cookie extraction, settings).
+- `rust/src/providers`: Provider-specific fetch/parsing/auth logic. Keep provider boundaries clean.
+- `rust/src/native_ui` and `rust/src/tray`: egui UI and tray integration.
+- `rust/src/browser`: Browser detection + cookie extraction for Windows.
+- `rust/assets`, `rust/icons`, `rust/gen`, `rust/wix`: UI assets, generated schemas, installer packaging.
+- `docs`: Mixed documentation (Windows port docs plus upstream/macOS references). Update only the relevant docs.
 
 ## Build, Test, Run
-- Dev loop: `./Scripts/compile_and_run.sh` kills old instances, runs `swift build` + `swift test`, packages, relaunches `CodexBar.app`, and confirms it stays running.
-- Quick build/test: `swift build` (debug) or `swift build -c release`; `swift test` for the full XCTest suite.
-- Package locally: `./Scripts/package_app.sh` to refresh `CodexBar.app`, then restart with `pkill -x CodexBar || pkill -f CodexBar.app || true; cd /Users/steipete/Projects/codexbar && open -n /Users/steipete/Projects/codexbar/CodexBar.app`.
-- Release flow: `./Scripts/sign-and-notarize.sh` (arm64 notarized zip) and `./Scripts/make_appcast.sh <zip> <feed-url>`; follow validation steps in `docs/RELEASING.md`.
+- Work from `rust/` for most tasks: `cd rust`.
+- Build: `cargo build` (debug) or `cargo build --release`.
+- Test: `cargo test`.
+- Run CLI locally: `cargo run -- --help`, `cargo run -- -p claude`, `cargo run -- cost`.
+- Run the tray app (Windows): `cargo run -- menubar`.
+- Format/lint before handoff when code changed: `cargo fmt --all` and `cargo clippy --all-targets -- -D warnings`
+  (or explain why not run).
+- There is no active root-level `Scripts/` build pipeline in this port. Do not rely on legacy `Scripts/*.sh` commands.
 
 ## Coding Style & Naming
-- Enforce SwiftFormat/SwiftLint: run `swiftformat Sources Tests` and `swiftlint --strict`. 4-space indent, 120-char lines, explicit `self` is intentional—do not remove.
-- Favor small, typed structs/enums; maintain existing `MARK` organization. Use descriptive symbols; match current commit tone.
+- Prefer small, typed structs/enums and focused modules; keep changes local.
+- Keep provider-specific logic inside the provider module instead of adding cross-provider branching.
+- Preserve clear error handling and user-facing diagnostics (`anyhow`/`thiserror` + friendly messages where applicable).
+- Use `tracing` for diagnostics; do not log raw secrets, cookies, or tokens.
+- Avoid adding dependencies/tooling without confirmation.
 
 ## Testing Guidelines
-- Add/extend XCTest cases under `Tests/CodexBarTests/*Tests.swift` (`FeatureNameTests` with `test_caseDescription` methods).
-- Always run `swift test` (or `./Scripts/compile_and_run.sh`) before handoff; add fixtures for new parsing/formatting scenarios.
-- After any code change, run `pnpm check` and fix all reported format/lint issues before handoff.
+- Add or extend focused Rust tests near the changed module (`#[cfg(test)]` unit tests are common in this repo).
+- For parser/fetcher changes, add deterministic samples/fixtures where practical.
+- Run `cargo test` after code changes; include any skipped checks in handoff.
+- If UI/tray behavior changed, do a manual Windows validation when possible (`codexbar menubar`).
 
 ## Commit & PR Guidelines
-- Commit messages: short imperative clauses (e.g., “Improve usage probe”, “Fix icon dimming”); keep commits scoped.
-- PRs/patches should list summary, commands run, screenshots/GIFs for UI changes, and linked issue/reference when relevant.
+- Use short imperative commit messages (for example: `Fix Claude CLI parser`, `Improve cookie import errors`).
+- Keep commits scoped to one change.
+- In PRs/patches, include:
+  - Summary of behavior changes
+  - Commands run (`cargo test`, `cargo fmt`, etc.)
+  - Screenshots/GIFs for UI changes (Windows)
+  - Linked issue/reference when relevant
 
 ## Agent Notes
-- Use the provided scripts and package manager (SwiftPM); avoid adding dependencies or tooling without confirmation.
-- Validate behavior against the freshly built bundle; restart via the pkill+open command above to avoid running stale binaries.
-- To guarantee the right bundle is running after a rebuild, use: `pkill -x CodexBar || pkill -f CodexBar.app || true; cd /Users/steipete/Projects/codexbar && open -n /Users/steipete/Projects/codexbar/CodexBar.app`.
-- After any code change that affects the app, always rebuild with `Scripts/package_app.sh` and restart the app using the command above before validating behavior.
-- If you edited code, run `scripts/compile_and_run.sh` before handoff; it kills old instances, builds, tests, packages, relaunches, and verifies the app stays running.
-- Per user request: after every edit (code or docs), rebuild and restart using `./Scripts/compile_and_run.sh` so the running app reflects the latest changes.
-- Release script: keep it in the foreground; do not background it—wait until it finishes.
-- Prefer modern SwiftUI/Observation macros: use `@Observable` models with `@State` ownership and `@Bindable` in views; avoid `ObservableObject`, `@ObservedObject`, and `@StateObject`.
-- Favor modern macOS 15+ APIs over legacy/deprecated counterparts when refactoring (Observation, new display link APIs, updated menu item styling, etc.).
-- Keep provider data siloed: when rendering usage or account info for a provider (Claude vs Codex), never display identity/plan fields sourced from a different provider.***
-- Claude CLI status line is custom + user-configurable; never rely on it for usage parsing.
-- Cookie imports: default Chrome-only when possible to avoid other browser prompts; override via browser list when needed.
+- Active implementation is the Rust Windows port. Root Swift/macOS docs and scripts are not the default workflow here.
+- Keep provider data siloed: never show identity/plan/email fields from provider A in provider B UI.
+- Claude CLI output is user-configurable; do not depend on a customizable status line for usage parsing.
+- Cookie import UX uses explicit browser selection in Preferences. Do not assume Chrome-only in general UI flows.
+- Be conservative with secret handling (manual cookies, API keys, token accounts); use existing redaction/storage helpers.
+- Prefer Windows-native validation for tray/DPAPI/browser-cookie behavior; WSL/Linux can be insufficient for those paths.
PATCH

echo "Gold patch applied."
