#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sovereign-sdk

# Idempotency guard
if grep -qF "| Block-id and pending assumption mismatch | `#2379`, `#2391` | Wrapper assumes " "crates/full-node/sov-ethereum/AGENTS.md" && grep -qF "`sov-evm` is the source of truth for EVM execution state and EVM JSON-RPC state " "crates/module-system/module-implementations/sov-evm/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/full-node/sov-ethereum/AGENTS.md b/crates/full-node/sov-ethereum/AGENTS.md
@@ -0,0 +1,113 @@
+# AGENTS.md - sov-ethereum
+
+> See repository `AGENTS.md` for global rules. This file adds crate-specific guidance only.
+
+## Mission
+
+`sov-ethereum` is the full-node Ethereum RPC wrapper around `sov-evm`. It owns transport-facing behavior: tx submission lifecycle, log pagination, subscriptions, and unsupported-method stubs.
+
+## Ownership Boundary
+
+- Own here: `eth_sendRawTransaction*`, `realtime_sendRawTransaction`, `eth_getLogs`, `eth_getLogsWithCursor`, `eth_subscribe`/`eth_unsubscribe`, method stubs, wrapper error mapping.
+- Do not own here: canonical EVM state query logic (`eth_getBalance`, `eth_call`, `eth_estimateGas`, receipts, block assembly). Those belong in `crates/module-system/module-implementations/sov-evm`.
+
+## Shared RPC Semantics (Intentional)
+
+These are by-design repo semantics. Do not flag as bugs unless a concrete tooling workflow breaks.
+
+- `latest` and `pending` resolve to the same pending head view for block/tag resolution.
+- Pending/soft-confirmed data may appear in block/tx/receipt/log responses.
+- `safe` and `finalized` both resolve to the latest finalized block.
+- `eth_getTransactionCount(..., "latest")` may include pending-inclusive nonce effects.
+- `eth_getLogs` with `toBlock: "latest"` may include pending-head logs.
+- `newHeads` may surface synthetic/pending-head style headers.
+- `eth_blockNumber` returns latest sealed block number, not synthetic pending height.
+- `eth_gasPrice` returns current `block_env.basefee`.
+- `eth_maxPriorityFeePerGas` returns `0`.
+- `eth_call` accepts `state_overrides`/`block_overrides` but currently ignores them.
+- EIP-1898 `requireCanonical` is accepted but effectively a no-op in no-reorg semantics.
+
+## Wrapper Hotspots
+
+| Path | Why it matters |
+| --- | --- |
+| `src/lib.rs` | RPC registration, unsupported method stubs, wrapper error-code helpers |
+| `src/handlers/mod.rs` | Raw tx submission, sync timeout behavior, local signing/send flow |
+| `src/handlers/get_logs.rs` | Standard logs endpoint and response-size gate |
+| `src/handlers/get_logs/service.rs` | Filter execution, block range/hash routing, cursor behavior |
+| `src/handlers/get_logs/cursor.rs` | Cursor encoding/decoding and paging correctness |
+| `src/handlers/subscribe/*.rs` | Subscription params validation, streaming, dedup/watermark behavior |
+
+## Error Code Policy
+
+Use shared helpers in `src/lib.rs`; do not introduce ad-hoc codes in handlers.
+
+| Meaning | Code |
+| --- | --- |
+| Method not supported | `-32004` |
+| Limit exceeded | `-32005` |
+| Tx rejected | `-32003` |
+| Resource not found | `-32001` |
+| Invalid params | `-32602` |
+| Sync timeout (`eth_sendRawTransactionSync`) | `4` |
+
+## Failure Pattern Matrix (PR Lessons)
+
+| Pattern | Repeated in PR(s) | Typical root cause | What to verify before merge |
+| --- | --- | --- | --- |
+| Error-code drift | `#2378`, `#2459` | Handler-specific error conversion bypasses wrapper helpers | Invalid params / rejected tx / not-found / limit paths map to expected codes |
+| Registration or stub gaps | `#2381` | New/unsupported methods not registered or not stubbed | Every unsupported method returns wrapper “not supported” code instead of “method not found” |
+| Block-id and pending assumption mismatch | `#2379`, `#2391` | Wrapper assumes L1 selector semantics not matching module semantics | Submission/local flows calling `sov-evm` use `BlockId` intentionally and consistently |
+| Logs pagination inconsistency | `#2387` | `eth_getLogs` and cursor variant diverge in range/size behavior | Large responses return limit error plus cursor path; cursor pagination remains stable |
+| Nonce/receipt flow surprises | `#2395`, `#2458` | Submission paths do not align with pending semantics | Wallet lifecycle (`send -> lookup tx -> receipt`) is coherent in pending and sealed states |
+| Estimation/submission mismatch | `#2459` | Local `eth_sendTransaction` mutates request fields inconsistently | Nonce/chain-id/gas defaults are explicit; estimation errors propagate cleanly |
+| Fee-context confusion at wrapper boundary | `#2462`, `#2463` | Wrapper assumes fee values independent of module context | Wrapper does not override module-computed fee/receipt semantics |
+
+## Wiring Rules
+
+1. If a method is a state query, implement it in `sov-evm` first.
+2. If a method is unsupported, add or keep an explicit stub in `src/lib.rs`.
+3. Use wrapper helpers (`rpc_invalid_params`, `rpc_tx_rejected`, `rpc_limit_exceeded`, `rpc_resource_not_found`) for handler errors.
+4. Keep local-only methods behind `local` feature gates.
+5. Do not duplicate EVM business logic in wrapper handlers.
+
+## Tx Submission Guardrails
+
+1. Keep parse -> authenticate -> sequencer accept ordering stable.
+2. Preserve explicit max timeout behavior for `eth_sendRawTransactionSync`.
+3. Ensure tx-type rejection remains clear for unsupported tx types.
+4. In local signing flow, keep nonce/chain-id/gas filling explicit and deterministic.
+
+## Logs and Subscription Guardrails
+
+1. `eth_getLogs` must enforce response-size limits and direct users to cursor path when needed.
+2. Cursor path must preserve deterministic forward progress and strict cursor validation.
+3. Subscription validation must remain explicit for supported kinds (`logs`, `newHeads`) and parameter constraints.
+4. Keep shutdown and stream termination behavior graceful and deterministic.
+
+## Pre-Merge Checklist
+
+1. If touching error mapping, test each helper code path at least once.
+2. If touching registration, verify unsupported methods still return stubbed code.
+3. If touching submission, test raw send, sync send timeout, and receipt retrieval flow.
+4. If touching logs, test both no-cursor and cursor pagination paths with limits.
+5. If touching subscriptions, test `logs` and `newHeads` parameter validation and stream behavior.
+6. If touching local signing flow, verify nonce/chain-id/gas defaults and failure mapping.
+
+## Minimal Audit Notes (P0/P1)
+
+Prioritize static checks that map to real client breakage:
+
+1. Wallet flow integrity: send, estimate, poll tx, poll receipt.
+2. SDK compatibility: ethers/viem/web3 parsing and retry behavior under wrapper errors.
+3. Logs/indexer safety: bounded responses, stable cursor continuation, predictable not-found behavior.
+
+## Fast Commands
+
+```bash
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-ethereum
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_logs
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_subscribe
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_ws_watch
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_tx
+```
diff --git a/crates/module-system/module-implementations/sov-evm/AGENTS.md b/crates/module-system/module-implementations/sov-evm/AGENTS.md
@@ -0,0 +1,126 @@
+# AGENTS.md - sov-evm
+
+> See repository `AGENTS.md` for global rules. This file adds crate-specific guidance only.
+
+## Mission
+
+`sov-evm` is the source of truth for EVM execution state and EVM JSON-RPC state queries. Most production RPC correctness bugs originate here, especially around block/tag resolution, fee context, and cross-endpoint consistency.
+
+## Ownership Boundary
+
+- Own here: EVM state, block/tx/receipt/log assembly, `eth_call`, `eth_estimateGas`, `eth_feeHistory`, tracing.
+- Do not own here: transport concerns, RPC method stubs, WebSocket plumbing, sequencer submission UX wrappers. Those belong to `crates/full-node/sov-ethereum`.
+
+## Shared RPC Semantics (Intentional)
+
+These are by-design repo semantics. Do not flag as bugs unless a concrete tooling workflow breaks.
+
+- `latest` and `pending` resolve to the same pending head view for block/tag resolution.
+- Pending/soft-confirmed data may appear in block/tx/receipt/log responses.
+- `safe` and `finalized` both resolve to the latest finalized block.
+- `eth_getTransactionCount(..., "latest")` may include pending-inclusive nonce effects.
+- `eth_getLogs` with `toBlock: "latest"` may include pending-head logs.
+- `newHeads` may surface synthetic/pending-head style headers.
+- `eth_blockNumber` returns latest sealed block number, not synthetic pending height.
+- `eth_gasPrice` returns current `block_env.basefee`.
+- `eth_maxPriorityFeePerGas` returns `0`.
+- `eth_call` accepts `state_overrides`/`block_overrides` but currently ignores them.
+- EIP-1898 `requireCanonical` is accepted but effectively a no-op in no-reorg semantics.
+
+## High-Risk Hotspots
+
+| Path | Why it matters |
+| --- | --- |
+| `src/rpc/mod.rs` | Block/tag resolution, synthetic block cache, tx/receipt assembly, fee linkage |
+| `src/rpc/handlers.rs` | Public JSON-RPC method behavior and parameter types |
+| `src/rpc/fee_history.rs` | Fee history shape, validation, and base-fee progression |
+| `src/helpers.rs` | Tx response construction and `effectiveGasPrice` derivation paths |
+| `src/state_access.rs` | Historical/pending state reads and block-env lookup |
+| `src/evm/executor.rs` | EVM cfg/env flags (`disable_base_fee`, call environment) |
+| `src/rpc/trace.rs` | Debug trace parity with block/context resolution |
+
+## Critical Invariants
+
+### 1. Fee/BaseFee coherence
+
+If you touch fee context, validate all of these together:
+
+- Pending/sealed block header `base_fee_per_gas`
+- Call/trace `BlockEnv.basefee`
+- Tx response `effectiveGasPrice`
+- Receipt `effective_gas_price`
+- `eth_feeHistory` base-fee series
+
+### 2. Cross-endpoint value consistency
+
+For the same tx/block, values must agree across:
+
+- `eth_getTransactionByHash`
+- `eth_getTransactionReceipt`
+- `eth_getBlockByNumber`/`eth_getBlockByHash` (full tx mode)
+- `eth_getBlockReceipts`
+
+### 3. Block selector consistency
+
+- Prefer `BlockId` over ad-hoc string parsing.
+- Keep `BlockId::Hash` and `BlockId::Number` paths behaviorally aligned.
+- Ensure historical lookup and synthetic lookup errors are deterministic and consistent.
+
+### 4. Encoding correctness
+
+- QUANTITY: `0x` prefixed, no leading zeros.
+- DATA: fixed-width where required (for example `eth_getStorageAt` as 32-byte data).
+- Nullability must match tooling expectations for each endpoint.
+
+### 5. Determinism and replay safety
+
+- Do not introduce non-deterministic state access in module/core logic.
+- Avoid hidden behavior drift between native and proof-relevant paths.
+
+## Failure Pattern Matrix (PR Lessons)
+
+| Pattern | Repeated in PR(s) | Typical root cause | What to verify before merge |
+| --- | --- | --- | --- |
+| Error-code drift | `#2378`, `#2459` | Invalid params / rejected tx / not-found mapped inconsistently | Invalid-param, revert, and not-found paths return stable expected code families |
+| Block-id regression | `#2379`, `#2391` | Using tag strings instead of `BlockId`/EIP-1898 paths | All relevant methods accept and correctly route `BlockId` variants |
+| Missing endpoint consistency | `#2381`, `#2391` | New methods added but behavior not aligned with existing fields | New endpoint values match existing tx/receipt/block data contracts |
+| Fee history and pending surface drift | `#2387` | Base-fee or pending range assumptions diverge across endpoints | `eth_feeHistory`, block headers, and tx/receipt fee fields stay coherent |
+| Nonce/receipt lifecycle mismatch | `#2395`, `#2458` | Pending/soft-confirmed state not reflected consistently | Nonce, tx lookup, and receipt lookup agree during pending-to-sealed transitions |
+| Estimation/call behavior mismatch | `#2459` | Revert and gas estimation paths do not mirror real execution constraints | `eth_estimateGas` errors on revert with revert payload; no success value on revert |
+| Effective-gas-price mismatch | `#2462` | Fee context dropped while building tx response | `effectiveGasPrice` aligns across tx object and receipt for same tx |
+| BASEFEE opcode mismatch | `#2463` | `BlockEnv.basefee` set inconsistently in call/trace contexts | `BASEFEE` opcode result matches block header base fee in same context |
+
+## Change Workflow
+
+1. Identify whether the change is state/query logic (`sov-evm`) or wrapper/transport (`sov-ethereum`).
+2. For any RPC field change, enumerate every endpoint that returns the same conceptual value.
+3. Update behavior docs if semantics changed: `docs/rpc_inventory.md` and relevant `docs/eth_*_test_cases.md`.
+4. Add or update tests before merge for at least one pending and one sealed scenario.
+
+## Pre-Merge Checklist
+
+1. If touching fees/base fee, validate all fee surfaces in one run.
+2. If touching tx/receipt fields, cross-check all four endpoint families listed above.
+3. If touching block tags/block id, test `earliest/latest/pending/safe/finalized/number/hash` selectors.
+4. If touching `eth_call` or `eth_estimateGas`, test success, revert, and halt paths.
+5. If touching response encoding, verify QUANTITY vs DATA shape for affected fields.
+6. If adding or changing a method contract, confirm `sov-ethereum` stub/registration expectations remain correct.
+
+## Minimal Audit Notes (P0/P1)
+
+When doing static production-readiness sweeps, prioritize:
+
+1. Wallet send flow: nonce, estimation, submission, receipt polling.
+2. SDK decoding stability: ethers/viem/web3 parsing of tx/receipt/block/log shapes.
+3. Internal coherence: same tx hash gives non-contradictory fields across endpoints.
+4. Gas UX safety: no impossible fee combinations that mislead fee selection logic.
+
+## Fast Commands
+
+```bash
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-evm
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_rpc
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_fee_history
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_effective_gas_price
+SKIP_GUEST_BUILD=1 cargo nextest run -p sov-demo-rollup evm_basefee
+```
PATCH

echo "Gold patch applied."
