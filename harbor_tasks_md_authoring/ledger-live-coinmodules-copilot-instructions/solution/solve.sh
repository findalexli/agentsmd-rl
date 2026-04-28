#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ledger-live

# Idempotency guard
if grep -qF "Prefer native dependencies from the blockchain foundation/ecosystem and well-est" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -58,6 +58,51 @@ When a flow needs new coin-specific behaviour, the fix is to **extend the contra
 
 If a PR changes the coin-framework interface (`libs/coin-framework/src/api/types.ts`), the author should also update the developer portal accordingly (repository: https://github.com/LedgerHQ/developer-portal).
 
+## coin-modules
+
+Each blockchain family lives in its own package under `libs/coin-modules/coin-<family>`. We should not create a new coin-module if it fits the ecosystem of an existing one. No packages other than coin-modules are allowed in this folder.
+
+Package name: `@ledgerhq/coin-<family>`
+
+### Module directory layout
+
+Every coin module must follow this layout:
+
+| Directory / file | Purpose |
+|---|---|
+| `api/` | Alpaca API surface — implements `AlpacaApi` from `@ledgerhq/coin-framework/api/types`, types from `@ledgerhq/types-live` are not allowed |
+| `logic/` | Core blockchain logic, agnostic of Bridge or API interfaces; only depends on `network/` and external libs, not required if only implementing Alpaca API |
+| `network/` | Communication with explorer / indexer / node |
+| `types/` | Model definitions for the coin-module, not related to network |
+| `bridge/` (legacy) | Bridge implementation (`CurrencyBridge` + `AccountBridge`), relates to types in  `@ledgerhq/types-live` package |
+| `signer/` (legacy) | Hardware wallet signer interface and device address resolver |
+
+- Unit tests: `*.unit.test.ts`, co-located with source.
+- Integration tests without network calls: `*.test.ts`.
+- Integration tests with real network calls: `*.integ.test.ts`, using separate `jest.integ.config.js`.
+
+### Dependencies
+
+Prefer native dependencies from the blockchain foundation/ecosystem and well-established open-source libraries. Avoid proprietary **third-party** SDKs or closed-source vendor packages (e.g. coin-vendor or exchange SDKs). This restriction does **not** apply to internal `@ledgerhq/*` workspace dependencies, which are allowed.
+
+### Two integration paths
+
+1. **Alpaca path** (preferred)— The coin module exports `createApi(config, currencyId)` implementing `AlpacaApi`. Families listed in the `alpacaized` map in `libs/ledger-live-common/src/bridge/impl.ts`, use `generic-alpaca` to build bridges from the API. Interface defined in `@ledgerhq/coin-framework/api/types.ts`.
+
+Methods that are not applicable may raise a "not supported"/"not applicable" error.
+
+2. **Classic JS Bridge** (legacy, should not be used) — The coin module exports `createBridges(signerContext, coinConfig)` returning `{ currencyBridge, accountBridge }`. This is wired via `libs/ledger-live-common/src/families/<family>/setup.ts`. Interface defined in `@ledgerhq/types-live`.
+
+### Integ test requirements on Alpaca API
+
+- `craftTransaction`, `estimateFees` integ tests need to cover each transaction type supported (token transfer, with memo, native transfer, delegation, ...).
+- `getBalance`, `listOperations` integ tests need to cover each asset type possible in the coin-module (for tron it would be native asset (tron), trc10 tokens, trc20 tokens)
+- `getBlockInfo`, `getBlock`, `listOperations`, `getStakes` integ tests need to compare against a reference block/operation/stake to validate metadata parsing.
+- `getValidators` needs to validate metadata against a reference validator.
+- `lastBlock` integ test needs to check that block height is higher than 0, time is a valid date and hash has the expected length.
+- `getNextSequence` needs to check that it is higher than the current nonce for a specific account.
+
+
 ## Cross-team files (team-split convention)
 
 When a PR touches a file or directory that is **owned by or relevant to multiple teams**, suggest refactoring to the **team-split convention**: splitting reduces friction between teams in CODEOWNERS by giving each team clear ownership of its files.
PATCH

echo "Gold patch applied."
