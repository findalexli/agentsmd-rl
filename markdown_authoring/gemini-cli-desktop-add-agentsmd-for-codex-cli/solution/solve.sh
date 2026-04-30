#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gemini-cli-desktop

# Idempotency guard
if grep -qF "- Rust: stable toolchain, `cargo fmt` and `cargo clippy` (pedantic/nursery enabl" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,44 @@
+# Repository Guidelines
+
+## Project Structure & Module Organization
+- `crates/backend` (Rust): core logic, CLI/session orchestration; colocated unit tests in `src/**`.
+- `crates/server` (Rust): web server binary `gemini-desktop-web` serving the web UI.
+- `crates/tauri-app` (Rust): desktop app (`gemini-desktop`) built with Tauri.
+- `frontend` (TypeScript/React/Vite/Tailwind): UI source; built assets are embedded/served.
+- `assets/`: images and static assets (screenshots, icons).
+- Top-level helpers: `justfile` (tasks), `tarpaulin.toml` (coverage), `installer.iss` (Windows installer).
+
+## Build, Test, and Development Commands
+- Install deps: `just deps` (runs `pnpm install` in `frontend`).
+- Desktop dev: `just dev` (Tauri dev from `frontend/`).
+- Web dev: `just dev-web` (runs Rust server + frontend dev with `GEMINI_DESKTOP_WEB=true`).
+- Build desktop: `just build` (Tauri bundle).
+- Build web: `just build-web` (builds frontend + `crates/server` release).
+- Lint/format: `just lint`, `just fmt`, CI‑strict: `just lint-ci`, `just check-fmt`.
+- Tests: `just test` or `cargo nextest run` (e.g., `just test -p backend`).
+
+## Coding Style & Naming Conventions
+- Rust: stable toolchain, `cargo fmt` and `cargo clippy` (pedantic/nursery enabled in `tauri-app`). 4‑space indent, snake_case for modules/functions, PascalCase for types.
+- TypeScript/React: ESLint + Prettier enforced.
+  - Prettier: 2‑space indent, semicolons, width 80 (`frontend/.prettierrc`).
+  - Components: PascalCase files in `src/components/**`; hooks in `src/hooks` use `useSomething`.
+- Keep modules focused; prefer small, composable functions. Avoid unrelated changes in a single PR.
+
+## Testing Guidelines
+- Frameworks: Rust unit/integration tests (tokio, mockall, serial_test). Frontend currently relies on type/lint checks.
+- Run: `just test` or `cargo nextest run -p backend`.
+- Coverage: `cargo tarpaulin -p backend` (threshold set to 95% in `tarpaulin.toml`; HTML at `target/tarpaulin/html/`).
+- Conventions: colocate tests with code using `#[cfg(test)] mod tests { ... }`; name async tests with `#[tokio::test]`.
+
+## Commit & Pull Request Guidelines
+- Commit style: Conventional Commits with scopes (e.g., `feat(ui): ...`, `fix(backend): ...`, `refactor(...)`). Version bumps use `vX.Y.Z`.
+- Before PR: run `just lint-ci` and `just check-fmt`; ensure tests pass and coverage holds.
+- PR requirements:
+  - Clear description and rationale; link related issues (e.g., `#123`).
+  - Screenshots/GIFs for UI changes (`frontend/`), and notes for behavior changes.
+  - Small, focused changes preferred; include migration notes if config or APIs change.
+
+## Security & Configuration Tips
+- Do not commit secrets or API keys. Prefer local OS keychain/env vars.
+- Web dev/build sets `GEMINI_DESKTOP_WEB=true` (handled by `just`).
+- Cross‑platform: verify changes build on Linux/macOS/Windows when touching Tauri/runtime code.
PATCH

echo "Gold patch applied."
