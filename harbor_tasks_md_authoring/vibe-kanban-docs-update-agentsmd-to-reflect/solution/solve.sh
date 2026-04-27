#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibe-kanban

# Idempotency guard
if grep -qF "- `crates/`: Rust workspace crates \u2014 `server` (API + bins), `db` (SQLx models/mi" "AGENTS.md" && grep -qF "frontend/AGENTS.md" "frontend/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,25 +1,30 @@
 # Repository Guidelines
 
 ## Project Structure & Module Organization
-- `crates/`: Rust workspace crates — `server` (API + bins), `db` (SQLx models/migrations), `executors`, `services`, `utils`, `deployment`, `local-deployment`, `remote`.
+- `crates/`: Rust workspace crates — `server` (API + bins), `db` (SQLx models/migrations), `executors`, `services`, `utils`, `git` (Git operations), `api-types` (shared API types for local + remote), `review` (PR review tool), `deployment`, `local-deployment`, `remote`.
 - `frontend/`: React + TypeScript app (Vite, Tailwind). Source in `frontend/src`.
 - `frontend/src/components/dialogs`: Dialog components for the frontend.
 - `remote-frontend/`: Remote deployment frontend.
-- `shared/`: Generated TypeScript types (`shared/types.ts`). Do not edit directly.
+- `shared/`: Generated TypeScript types (`shared/types.ts`, `shared/remote-types.ts`) and agent tool schemas (`shared/schemas/`). Do not edit generated files directly.
 - `assets/`, `dev_assets_seed/`, `dev_assets/`: Packaged and local dev assets.
 - `npx-cli/`: Files published to the npm CLI package.
 - `scripts/`: Dev helpers (ports, DB preparation).
 - `docs/`: Documentation files.
 
 ### Crate-specific guides
 - [`crates/remote/AGENTS.md`](crates/remote/AGENTS.md) — Remote server architecture, ElectricSQL integration, mutation patterns, environment variables.
+- [`docs/AGENTS.md`](docs/AGENTS.md) — Mintlify documentation writing guidelines and component reference.
+- [`frontend/AGENTS.md`](frontend/AGENTS.md) — Frontend design system styling guidelines.
 
 ## Managing Shared Types Between Rust and TypeScript
 
 ts-rs allows you to derive TypeScript types from Rust structs/enums. By annotating your Rust types with #[derive(TS)] and related macros, ts-rs will generate .ts declaration files for those types.
 When making changes to the types, you can regenerate them using `pnpm run generate-types`
 Do not manually edit shared/types.ts, instead edit crates/server/src/bin/generate_types.rs
 
+For remote/cloud types, regenerate using `pnpm run remote:generate-types`
+Do not manually edit shared/remote-types.ts, instead edit crates/remote/src/bin/remote-generate-types.rs (see crates/remote/AGENTS.md for details).
+
 ## Build, Test, and Development Commands
 - Install: `pnpm i`
 - Run dev (frontend + backend with ports auto-assigned): `pnpm run dev`
@@ -31,6 +36,11 @@ Do not manually edit shared/types.ts, instead edit crates/server/src/bin/generat
 - Prepare SQLx (offline): `pnpm run prepare-db`
 - Prepare SQLx (remote package, postgres): `pnpm run remote:prepare-db`
 - Local NPX build: `pnpm run build:npx` then `pnpm pack` in `npx-cli/`
+- Format code: `pnpm run format` (runs `cargo fmt` + frontend Prettier)
+- Lint: `pnpm run lint` (runs frontend ESLint + `cargo clippy`)
+
+## Before Completing a Task
+- Run `pnpm run format` to format all Rust and frontend code.
 
 ## Coding Style & Naming Conventions
 - Rust: `rustfmt` enforced (`rustfmt.toml`); group imports by crate; snake_case modules, PascalCase types.
diff --git a/frontend/AGENTS.md b/frontend/AGENTS.md

PATCH

echo "Gold patch applied."
