#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fcl-js

# Idempotency guard
if grep -qF "- `npm run demo` \u2014 runs emulator + dev-wallet + Vite in `packages/demo` (require" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,134 @@
+# AGENTS.md
+
+Guidance for AI coding agents (Claude Code, Codex, Cursor, Copilot, and others) working in
+this repository. Loaded into agent context automatically — keep edits concise.
+
+## Overview
+
+`fcl-js` is the TypeScript/JavaScript **Flow Client Library** monorepo: the reference client
+for connecting browser and server apps to the Flow blockchain and FCL-compatible wallets
+(`README.md`). It is a **Lerna monorepo with independent package versioning** (`lerna.json`:
+`"version": "independent"`) using **npm workspaces** (`package.json`:
+`"workspaces": ["./packages/*"]`), with releases driven by **Changesets** from the `master`
+branch (`.changeset/config.json`, `.github/workflows/release.yml`). The flagship package is
+`@onflow/fcl` (`packages/fcl/`); `@onflow/sdk` (`packages/sdk/`) is the lower-level Flow
+Access API client FCL is built on.
+
+## Build and Test Commands
+
+This repo uses **npm + Lerna**, not pnpm or yarn. There is no `pnpm-workspace.yaml`; the
+committed lockfile is `package-lock.json`.
+
+Root scripts (`package.json`):
+
+- `npm i` — install workspace dependencies (CONTRIBUTING.md). `make install` runs `npm ci`.
+- `npm run build` — `lerna run build` across all packages.
+- `npm test` — runs `jest` with `projects: ["<rootDir>/packages/*"]` (`jest.config.js`).
+- `npm start` — `npm run build && lerna run start --parallel` (per-package watch mode).
+- `npm run prettier:check` / `npm run prettier` — check/write formatting.
+- `npm run generate-all-docs` — `node docs-generator/generate-all-docs.js`; scans packages
+  that declare a `generate-docs` script and invokes each one.
+- `npm run demo` — runs emulator + dev-wallet + Vite in `packages/demo` (requires `flow` CLI).
+- `npm run demo:testnet` — same demo app pointed at testnet.
+- `npm run changeset` / `npm run release` — changeset CLI / `build && changeset publish`.
+
+Makefile wrappers (`Makefile`):
+
+- `make all` → `clean install build test`.
+- `make ci` → `clean install build`, then `npm run test -- --ci` and `npm run prettier:check`.
+  This is exactly what `.github/workflows/integrate.yml` runs on every PR.
+- `make clean` — deletes `node_modules/`, `dist/`, `types/` inside every `packages/*`.
+- `make publish` — runs `npm publish` in every package (not typical; CI uses Changesets).
+
+Per-package scripts are uniform (see `packages/fcl/package.json`, `packages/sdk/package.json`,
+etc.): `test` → `jest`, `build` → `fcl-bundle` (often preceded by `eslint .`), `start` →
+`fcl-bundle --watch`, `build:types` → `tsc` (where present). The bundler is the in-tree
+`@onflow/fcl-bundle` package (`packages/fcl-bundle/`, wraps Rollup). To work on one package,
+`cd packages/<name> && npm test` (or `npm run test:watch` where declared).
+
+CI uses **Node 18** for PRs (`integrate.yml`) and **Node 22** for releases (`release.yml`).
+No `engines` field is declared in any package.json.
+
+## Architecture
+
+Everything ships from `packages/*`. Verified packages (29):
+
+**Flagship / entry points**
+- `fcl/` — `@onflow/fcl`, the browser-first high-level client (wallet discovery, authn,
+  `query`, `mutate`, transactions, signatures).
+- `fcl-core/` — `@onflow/fcl-core`, platform-agnostic core that `fcl` and `fcl-react-native`
+  build on. Houses `wallet-provider-spec/` and `wallet-utils/`.
+- `fcl-react-native/` — `@onflow/fcl-react-native`, React Native variant of FCL.
+- `sdk/` — `@onflow/sdk`, low-level Flow Access API client (builders, interactions, encode/
+  decode, resolvers). FCL wraps this.
+
+**React kits**
+- `react-core/` — `@onflow/react-core`, platform-agnostic React hooks (TanStack Query-based).
+- `react-sdk/` — `@onflow/react-sdk`, web React bindings built on `react-core` + `fcl`.
+- `react-native-sdk/` — `@onflow/react-native-sdk`, RN bindings built on `react-core` +
+  `fcl-react-native`.
+
+**EVM / cross-VM**
+- `fcl-ethereum-provider/` — EIP-1193 Ethereum provider backed by an FCL wallet.
+- `fcl-wagmi-adapter/` — Wagmi connector built on `fcl-ethereum-provider`.
+- `fcl-rainbowkit-adapter/` — RainbowKit adapter built on `fcl-wagmi-adapter`.
+
+**Wallet connectivity**
+- `fcl-wc/` — `@onflow/fcl-wc`, WalletConnect v2 adapter for FCL.
+
+**Transports / encoding / types**
+- `transport-http/` — HTTP transport against the Flow Access API (used by `sdk`).
+- `transport-grpc/` — gRPC-Web transport. **Ignored by Changesets**
+  (`.changeset/config.json` `"ignore": ["@onflow/transport-grpc"]`) — do not add changesets
+  for it.
+- `protobuf/` — `@onflow/protobuf`, generated gRPC protobuf bindings (built via webpack,
+  not `fcl-bundle`).
+- `rlp/` — RLP encoder port (MPL-2.0; every other package is Apache-2.0).
+- `types/` — Cadence value type codecs (`t.Int`, `t.Address`, …).
+- `typedefs/` — `@onflow/typedefs`, public TypeScript definitions (see README § TypeScript).
+
+**Shared utilities** (`util-*`)
+- `util-actor`, `util-address`, `util-encode-key`, `util-invariant`, `util-logger`,
+  `util-rpc`, `util-semver`, `util-template`, `util-uid`.
+
+**Config + tooling + dev**
+- `config/` — `@onflow/config`, FCL's config store (e.g. `fcl.config({...})`).
+- `fcl-bundle/` — the internal Rollup-based bundler every publishable package uses.
+- `demo/` — `@onflow/demo` (private), Vite app for manual testing against emulator/testnet/
+  mainnet. See `packages/demo/README.md`.
+
+## Conventions and Gotchas
+
+- **Do not switch package managers.** The repo is npm + Lerna + Changesets. Switching to
+  pnpm/yarn breaks lockfile and CI.
+- **Do not add a top-level integration test.** `jest.config.js` aggregates
+  `packages/*` Jest projects; tests live inside each package next to source (`*.test.ts`).
+- **Write a changeset for any package-facing change.** Run `npx changeset` per
+  CONTRIBUTING.md. The baseBranch is `master`, not `main`.
+- **`@onflow/transport-grpc` is Changeset-ignored** — do not create a changeset entry
+  targeting it (`.changeset/config.json`).
+- **Never edit `packages/protobuf/src/generated/`** — regenerate via the package's
+  `generate` script (`protoc ...`). This path is also in `.prettierignore`.
+- **Versions are independent.** Lerna `"version": "independent"`; bumping `@onflow/fcl` does
+  not bump siblings. Cross-package imports use pinned versions — update them explicitly
+  when changing a shared util's API.
+- **Builds run lint.** Most packages define `"build": "npm run lint && fcl-bundle"`; a lint
+  error will fail `npm run build` and therefore `make ci`.
+- **`@onflow/fcl-bundle` is in-tree.** When debugging build output, edit
+  `packages/fcl-bundle/` rather than searching for it in `node_modules`.
+- **Commit message format** (CONTRIBUTING.md): `TOPIC -- [package-name] description`.
+  Topics: `PKG` (package change, needs changelog), `DOC`, `OPS`, `VSN`.
+- **Prettier config**: `semi: false`, `bracketSpacing: false`, `arrowParens: "avoid"`
+  (`.prettierrc`). CI runs `prettier --check .` as part of `make ci`.
+- **Wallet provider spec** lives in the repo at
+  `packages/fcl-core/src/wallet-provider-spec/` (active draft: `draft-v4.md`). Link here
+  rather than duplicating spec text.
+- **`@onflow/sdk` vs `@onflow/fcl`**: SDK is low-level (Access API only, no wallet).
+  FCL depends on SDK. Don't reimplement SDK primitives inside `fcl` or `fcl-core`.
+
+## Files Not to Modify
+
+- `packages/protobuf/src/generated/` — generated from `.proto` (also in `.prettierignore`).
+- `package-lock.json` — regenerate via `npm i`, don't hand-edit.
+- `packages/*/CHANGELOG.md` — managed by Changesets.
+- `packages/*/dist/`, `packages/*/types/` — build output (cleaned by `make clean`).
PATCH

echo "Gold patch applied."
