#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tycho-indexer

# Idempotency guard
if grep -qF "- For `rstest` parameterized tests, **name each case** with `#[case::descriptive" "CLAUDE.md" && grep -qF "4. Synchronizers classified as `Started | Ready | Delayed | Stale | Advanced | E" "tycho-client/CLAUDE.md" && grep -qF "- **`protocol_sim`** \u2014 `ProtocolSim` core trait (quote, price, state transition)" "tycho-common/CLAUDE.md" && grep -qF "All services depend on `rpc/` for RPC calls and on `erc20.rs` for ABI encoding. " "tycho-ethereum/CLAUDE.md" && grep -qF "runner.rs                 ExtractorRunner: drives the Substreams stream; Extract" "tycho-indexer/CLAUDE.md" && grep -qF "`chain`, `contract`, `protocol`, `entry_point`, and `extraction_state`\u2014each addi" "tycho-storage/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,17 +1,17 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+## Development Environment
+- Requires PostgreSQL (via `docker-compose up -d db`)
+- Uses Diesel for ORM and migrations
+- Uses `nextest` for parallel test execution; DB tests tagged `serial_db` run sequentially
+- Follows Conventional Commits for automated versioning (see `release.config.js`)
 
-## Commands
-
-### Build & Release
-```bash
-# Build all packages in release mode
-cargo build --release
+## Testing Conventions
+- For `rstest` parameterized tests, **name each case** with `#[case::descriptive_name(...)]` — test names should be self-documenting so failures are immediately identifiable
+- Keep test function names concise; avoid suffixes that restate what parameters already express
+- Don't nest `mod` wrappers inside `#[cfg(test)] mod test` unless there's a concrete isolation benefit
 
-# Build tycho-indexer with unstable tokio features (for production)
-RUSTFLAGS="--cfg tokio_unstable" cargo build --package tycho-indexer --release
-```
+## Commands
 
 ### Testing
 ```bash
@@ -20,6 +20,12 @@ cargo nextest run --workspace --locked --all-targets --all-features --bin tycho-
 
 # Run serial database tests (must be run separately)
 cargo nextest run --workspace --locked --all-targets --all-features --bin tycho-indexer -E 'test(serial_db)'
+
+# Run a single test by name
+cargo nextest run --workspace --locked --all-targets --all-features -E 'test(my_test_name)'
+
+# Run all tests in a specific crate
+cargo nextest run --package tycho-storage --locked --all-targets --all-features
 ```
 
 ### Code Quality
@@ -37,80 +43,80 @@ cargo +nightly clippy --locked --all --all-features --all-targets -- -D warnings
 ./check.sh
 ```
 
-### Database Operations
-```bash
-# Start PostgreSQL service
-docker-compose up -d db
-
-# Run database migrations
-diesel migration run --migration-dir ./tycho-storage/migrations
-
-# Redo last migration (useful for testing)
-diesel migration redo --migration-dir ./tycho-storage/migrations
+## Architecture Overview
 
-# Update schema.rs after migrations
-diesel print-schema --config-file ./tycho-storage/diesel.toml > ./tycho-storage/src/postgres/schema.rs
-```
+Tycho is a multi-crate Rust workspace for indexing DEX/DeFi protocol data from blockchains, streaming real-time state to solvers via WebSocket deltas and HTTP snapshots.
 
-### Running Tycho Indexer
-```bash
-# Run indexer for all extractors in extractors.yaml
-cargo run --bin tycho-indexer -- index
-
-# Run indexer for a single extractor
-cargo run --bin tycho-indexer -- run
+### Core Crates
+- **tycho-indexer**: Main indexing engine, extractor management, RPC + WebSocket services
+- **tycho-storage**: PostgreSQL backend with Diesel ORM, versioned data, migrations
+- **tycho-common**: Shared domain types, storage/blockchain traits, DTOs
+- **tycho-client**: Consumer library — HTTP snapshot client + WebSocket delta client
+- **tycho-ethereum**: Ethereum specific implementations: RPC, token analysis, EVM account/trace extraction
+- **tycho-client-py**: Python bindings (not maintained)
 
-# Run token analyzer cronjob
-cargo run --bin tycho-indexer -- analyze-tokens
+### End-to-End Data Flow
 
-# Run only the RPC server
-cargo run --bin tycho-indexer -- rpc
+```
+── INGESTION ──────────────────────────────────────────────────────────────────
+
+  Substreams gRPC                                    Ethereum RPC
+       │                                                   │
+       ▼                                                   │
+  ProtocolExtractor                                        │
+  ├─ Deserialize BlockScopedData (protobuf)                │
+  ├─ PartialBlockBuffer: accumulate sub-block msgs         │
+  │  until full-block signal arrives                       │
+  ├─ TokenPreProcessor: for each unknown token address ────┘
+  │  fetch metadata (symbol, decimals) via eth_call
+  └─ Produce BlockChanges (tx-level state/balance/token deltas)
+       │
+       ▼
+  ReorgBuffer (extractor-owned, one per ProtocolExtractor)
+  ├─ Insert BlockChanges for every new block
+  ├─ On BlockUndoSignal: purge blocks after reverted hash,
+  │  emit revert messages (revert=true) — no DB rollback needed
+  └─ Drain to DB when count_blocks_before(finalized_block_height)
+       >= commit_batch_size  ← only finalized blocks ever reach DB
+       │
+       ▼ (drained blocks only)
+  BlockChanges → BlockAggregatedChanges
+  │  merge all tx-level deltas into one state per component/account;
+  │  new_tokens, new_protocol_components, component_balances included
+  │
+  ├─ DB write (CachedGateway → Postgres)
+  │  upsert blocks, tokens, protocol components, state, balances
+  │  sets db_committed_block_height on outgoing message
+  │
+  └─ Broadcast BlockAggregatedChanges on internal channel
+       │ (all blocks, including pending/non-committed)
+       │
+── SERVER ─────────────────────────────────────────────────────────────────────
+       │
+       ├──► WebSocket subscribers (tycho-indexer/src/services/ws.rs)
+       │    emit message directly; revert flag signals chain reorg
+       │
+       └──► PendingDeltasBuffer (tycho-indexer/src/services/deltas_buffer.rs)
+            per-extractor ReorgBuffer of BlockAggregatedChanges
+            ├─ Insert every full block (partial blocks skipped)
+            ├─ Auto-drain blocks ≤ db_committed_block_height
+            │  (they're in DB, no longer "pending")
+            └─ Used by RPC handlers: DB snapshot + pending deltas
+               = consistent view of latest state for HTTP queries
+
+── CLIENT (tycho-client) ──────────────────────────────────────────────────────
+
+  StateSynchronizer (one per extractor subscription)
+  ├─ 1. Subscribe to WebSocket stream (WsDeltasClient)
+  ├─ 2. On first message: query HTTP snapshot (HttpRPCClient)
+  │     fetches protocol_state / contract_state at that block height
+  └─ 3. Buffer WebSocket deltas received before snapshot arrives;
+        apply buffered deltas on top of snapshot to catch up
+
+  BlockSynchronizer (across all extractors)
+  ├─ Tracks state per synchronizer: Ready / Delayed / Stale
+  ├─ Delayed synchronizers consume buffered messages to catch up
+  └─ When all synchronizers reach the same block: emit FeedMessage
+     (unified view of all protocol state at that block) to consumer
 ```
 
-## Architecture Overview
-
-Tycho is a multi-crate Rust workspace designed for indexing and processing DEX/DeFi protocol data from blockchains. The system follows an extractor-service architecture where extractors process incoming blockchain data and services distribute data to clients.
-
-### Core Crates
-- **tycho-indexer**: Main indexing logic, extractor management, RPC services, and WebSocket subscriptions
-- **tycho-storage**: Database layer with PostgreSQL backend, migrations, and versioned data storage
-- **tycho-common**: Shared types, traits, and DTOs used across all crates
-- **tycho-client**: Consumer-facing client library and CLI for streaming protocol data
-- **tycho-client-py**: Python bindings for the Rust client (currently not maintained/outdated)
-- **tycho-ethereum**: Ethereum-specific blockchain integration and token analysis
-
-### Data Flow Architecture
-1. **Substreams** send fork-aware blockchain messages to tycho-indexer
-2. **Extractors** process incoming data, maintain protocol state, and emit deltas
-3. **Services** distribute real-time data via WebSocket and provide historical data via RPC
-4. **Storage** persists versioned protocol states and component data in PostgreSQL
-
-### Key Architectural Concepts
-- **Protocol Components**: Static configuration of protocol pools/contracts
-- **Protocol State**: Dynamic attributes that change per block (reserves, balances, etc.)
-- **Reorg Handling**: Automatic chain reorganization detection and revert message emission
-- **Versioning System**: Historical data tracking with valid_to timestamps
-- **Delta Streaming**: Lightweight state change messages for real-time updates
-
-### Special Attributes System
-- `manual_updates`: Controls automatic vs manual component updates
-- `update_marker`: Signals component state changes for manual update components
-- `balance_owner`: Specifies token balance ownership for components
-- `stateless_contract_addr/_code`: References to stateless contracts needed for simulations
-
-### Development Environment
-- Requires PostgreSQL (via docker-compose or local installation)
-- Uses Diesel for database migrations and ORM
-- Employs nextest for parallel test execution with special handling for database tests
-- Follows Conventional Commits format for automated versioning
-
-### Testing Strategy
-- Standard tests run in parallel
-- Database tests (`serial_db`) run sequentially to avoid interference
-- Integration tests can use tycho-client to generate test fixtures
-- Mock data available in various test directories
-
-### Testing Conventions
-- For `rstest` parameterized tests, **name each case** with `#[case::descriptive_name(...)]` instead of relying on inline comments — test names should be self-documenting so failures are immediately identifiable
-- Keep test function names concise; avoid redundant suffixes that restate what parameters already express
-- Don't nest `mod` wrappers inside `#[cfg(test)] mod test` unless there's a concrete isolation benefit
\ No newline at end of file
diff --git a/tycho-client/CLAUDE.md b/tycho-client/CLAUDE.md
@@ -0,0 +1,36 @@
+# tycho-client
+
+Consumer library implementing the snapshot + deltas pattern for real-time protocol state.
+
+## Module Map
+
+```
+rpc.rs              HTTP snapshot client — fetches protocol state at a block height
+deltas.rs           WebSocket client — streams real-time state deltas
+stream.rs           Builder entry point — wires RPC + WS clients into a TychoStream
+feed/
+  mod.rs            BlockSynchronizer — aligns N synchronizers by block, emits FeedMessage
+  synchronizer.rs   ProtocolStateSynchronizer — manages snapshot + delta sync for one extractor
+  component_tracker.rs  Filters components by TVL threshold or explicit ID list
+  block_history.rs  Validates block chain continuity; classifies incoming blocks
+cli.rs / main.rs    CLI binary for manual testing
+```
+
+## Connections
+
+```
+TychoStreamBuilder (stream.rs)
+  └─ creates ProtocolStateSynchronizer per extractor (feed/synchronizer.rs)
+       ├─ ComponentTracker (feed/component_tracker.rs) → HttpRPCClient (rpc.rs)
+       ├─ WsDeltasClient (deltas.rs) for live deltas
+       └─ StateSyncMessage → BlockSynchronizer (feed/mod.rs)
+            ├─ BlockHistory (feed/block_history.rs) for chain validation
+            └─ FeedMessage → consumer channel
+```
+
+## Sync Lifecycle
+
+1. `WsDeltasClient` subscribes; first message determines snapshot block
+2. `HttpRPCClient` fetches snapshot at that block; deltas buffer until it arrives
+3. `BlockSynchronizer` waits for all synchronizers, then emits a `FeedMessage` per block
+4. Synchronizers classified as `Started | Ready | Delayed | Stale | Advanced | Ended`; stale ones are kept but skipped
diff --git a/tycho-common/CLAUDE.md b/tycho-common/CLAUDE.md
@@ -0,0 +1,42 @@
+# tycho-common
+
+Shared domain types, storage/extraction traits, and simulation abstractions used across all crates.
+
+## Module Organisation
+
+### Primitives
+- **`hex_bytes`** — `Bytes` newtype with hex serde and Diesel support; used everywhere as the byte representation
+- **`serde_primitives`** — Hex serde helpers for maps and vecs; used by `dto` and `models`
+- **`display`** — `DisplayOption` wrapper for tracing logs
+
+### Domain Models (`models/`)
+- **`mod`** — Type aliases (`Address`, `TxHash`, …) and the `Chain` enum; imported by every other module
+- **`blockchain`** — `Block`, `Transaction`, `BlockAggregatedChanges`; the output type of the indexing pipeline
+- **`contract`** — `Account` / `AccountDelta`; versioned EVM contract state written by tycho-ethereum and persisted by tycho-storage
+- **`protocol`** — `ProtocolComponent` / `ProtocolComponentStateDelta`; DEX/lending pool state alongside `ComponentBalance`
+- **`token`** — `Token` metadata and quality scoring; populated by tycho-ethereum's `TokenAnalyzer`
+- **`error`** — `WebsocketError` for streaming subscription failures
+
+### API Layer
+- **`dto`** — JSON-serialisable mirrors of `models/` types for HTTP/WebSocket responses; used by tycho-indexer (server) and tycho-client (consumer)
+
+### Trait Abstractions
+- **`storage`** — Async gateway traits (`ProtocolGateway`, `ContractStateGateway`, …) that tycho-storage implements over Diesel/Postgres
+- **`traits`** — Async extraction traits (`AccountExtractor`, `TokenAnalyzer`, `EntryPointTracer`, …) that tycho-ethereum implements
+
+### Simulation (`simulation/`)
+- **`protocol_sim`** — `ProtocolSim` core trait (quote, price, state transition); implemented by protocol-specific simulators; To be replaced by SwapQuoter trait in the future.
+- **`swap`** — `SwapQuoter` trait and `params_with_context!` macro for quoting with block context
+- **`indicatively_priced`** — `IndicativelyPriced` extension trait for RFQ/off-chain-signed quotes
+- **`errors`** — `SimulationError` (Fatal / InvalidInput / Recoverable) and `TransitionError`
+
+## Data Flow
+
+```
+tycho-ethereum (implements traits)
+    → fills models/
+    → tycho-storage (implements storage traits) persists models/
+    → dto serialises for HTTP/WebSocket
+    → tycho-client deserialises dto
+    → simulation/ consumed by solvers via tycho-client
+```
diff --git a/tycho-ethereum/CLAUDE.md b/tycho-ethereum/CLAUDE.md
@@ -0,0 +1,47 @@
+# tycho-ethereum
+
+Ethereum-specific implementations of traits defined in `tycho-common`. Consumed exclusively by `tycho-indexer`.
+
+## Module Map
+
+```
+rpc/                    Ethereum RPC client (alloy-based) with batching + retry
+  ├─ config.rs          RPCRetryConfig, RPCBatchingConfig
+  ├─ errors.rs          Error hierarchy: RPCError → RequestError → ReqwestError
+  └─ retry.rs           Error classification (retryable vs permanent RPC codes)
+
+erc20.rs                ERC-20 ABI bindings via alloy sol! macro
+gas.rs                  BlockGasPrice / GasPrice (Legacy + EIP-1559); implements FeePriceGetter
+
+services/
+  ├─ account_extractor.rs     Fetches code, balance, storage for accounts at a block height
+  ├─ token_pre_processor.rs   Fetches symbol + decimals; gracefully handles non-standard tokens
+  ├─ token_analyzer.rs        Simulates token transfers via trace_callMany; classifies token quality
+  └─ entrypoint_tracer/
+       ├─ tracer.rs                   Traces contract execution; returns access lists + state diffs
+       ├─ slot_detector.rs            Detects ERC-20 storage slot layout via trace simulation
+       ├─ balance_slot_detector.rs    Locates balance mapping slot
+       └─ allowance_slot_detector.rs  Locates allowance mapping slot
+```
+
+## Module Dependencies
+
+All services depend on `rpc/` for RPC calls and on `erc20.rs` for ABI encoding. The entrypoint tracer's slot detectors feed into `account_extractor` when slot layout is unknown.
+
+```
+tycho-common traits
+        ↑
+  services/* ──── rpc/ ──── alloy
+        |
+      erc20.rs
+```
+
+## Trait Implementations
+
+| Module | Implements (tycho-common) |
+|---|---|
+| `account_extractor` | `AccountExtractor` |
+| `token_pre_processor` | `TokenPreProcessor` |
+| `token_analyzer` | `TokenAnalyzer` |
+| `entrypoint_tracer` | `EntryPointTracer` |
+| `gas` + `rpc` | `FeePriceGetter` |
diff --git a/tycho-indexer/CLAUDE.md b/tycho-indexer/CLAUDE.md
@@ -0,0 +1,114 @@
+# tycho-indexer
+
+Main indexing engine: connects to Substreams, processes block data, persists finalized state, and
+serves it over HTTP/WebSocket.
+
+## Module Map
+
+```
+main.rs                     CLI entry point; account initialisation; extractor startup
+cli/                        Command definitions: Index, Run, AnalyzeTokens, Rpc
+
+extractor/
+  protocol_extractor.rs     ProtocolExtractor — core message processor (see below)
+  runner.rs                 ExtractorRunner: drives the Substreams stream; ExtractorHandle for control
+  reorg_buffer.rs           ReorgBuffer — finality-aware block queue; chain-reorg purge
+  models.rs                 BlockChanges, BlockAggregatedChanges, TxWithChanges
+  protocol_cache.rs         ProtocolMemoryCache — in-process token/component metadata cache
+  chain_state.rs            ChainState — tracks current tip and finality horizon
+  token_analysis_cron.rs    Background job: token quality / tax analysis
+  protobuf_deserialisation.rs  Substreams protobuf → BlockChanges conversion
+  dynamic_contract_indexer/ DCI optional extension (see below)
+  post_processors/          Optional block-level post-processing hooks
+
+services/
+  mod.rs                    ServicesBuilder — wires extractors, gateway, and server together
+  rpc.rs                    HTTP endpoints: state snapshots, component queries
+  ws.rs                     WebSocket broadcaster — emits BlockAggregatedChanges per block
+  deltas_buffer.rs          PendingDeltasBuffer — pending-block state for RPC consistency
+  cache.rs                  HTTP response cache
+  access_control.rs         API-key authentication middleware
+
+substreams/                 gRPC client for Substreams streaming API
+pb/                         Auto-generated protobuf bindings (Substreams + Firehose)
+```
+
+## ProtocolExtractor
+
+`ProtocolExtractor<G, T, E>` is generic over gateway `G`, token pre-processor `T`, and optional
+extension `E`. It is the single point that turns raw Substreams messages into typed block data.
+
+### Normal (full-block) path
+
+1. Deserialize `BlockScopedData` → `BlockChanges` (tx-level state/balance deltas).
+2. Run post-processor if configured.
+3. Call `E::process_block_update()` (DCI — see below).
+4. Fetch metadata for any new token addresses via `T` (ERC-20 symbol / decimals over RPC).
+5. Insert `BlockChanges` into `ReorgBuffer`.
+6. When `ReorgBuffer` has `>= commit_batch_size` blocks before `finalized_block_height`, drain them
+   and schedule a DB write (see Persistence).
+7. Aggregate all tx-level deltas → `BlockAggregatedChanges`; compute TVL.
+8. Broadcast `Arc<BlockAggregatedChanges>` to subscribers.
+
+### Partial-block path
+
+Some chains (e.g. Base) emit multiple partial messages per block. While
+`partial_block_index.is_some()`, each message is merged into `PartialBlockBuffer` (a single
+`Option<BlockChanges>`). An aggregated message is broadcast immediately for WebSocket consumers,
+but the block is **not** inserted into `ReorgBuffer` or written to DB until the full-block signal
+arrives (clearing the buffer).
+
+### DCI (Dynamic Contract Indexer) — optional
+
+`ExtractorExtension::process_block_update()` is called on the accumulated `BlockChanges` before
+aggregation. The DCI uses entry-point tracing results (`trace_results`) to extract additional
+contract state and injects it back into `BlockChanges`. Two implementations exist:
+`DynamicContractIndexer` (generic EVM tracing) and a `UniswapV4Hooks`-specific variant. When no
+DCI is configured the call is a no-op.
+
+### Revert handling
+
+On `BlockUndoSignal(target_hash)` from Substreams:
+
+1. `ReorgBuffer::purge(target_hash)` removes all buffered blocks after the common ancestor.
+2. A `BlockAggregatedChanges` with `revert = true` is broadcast.
+3. **No DB rollback is needed** — only finalized blocks ever reach the DB, so the persisted state
+   is always on the canonical chain.
+
+`PendingDeltasBuffer` (RPC side) mirrors this: it uses its own `ReorgBuffer` and discards
+non-canonical pending blocks on the same broadcast.
+
+## Persistence
+
+`CachedGateway` enqueues `WriteOp` messages; `DBCacheWriteExecutor` flushes them when the next
+block batch arrives. Writes follow a fixed FK-safe order (block → tx → contracts → tokens →
+components → state → entry points → cursor). Every mutable row is versioned with `valid_from` /
+`valid_to` — historical rows are never mutated (see `tycho-storage/CLAUDE.md`).
+
+**Trigger:** `ReorgBuffer::drain_blocks_until(finalized_height)` — blocks are only committed once
+they are provably behind the finality horizon.
+
+## Why extractor messages must be broadcast to the RPC service
+
+HTTP snapshot endpoints must reflect the latest state, including blocks not yet committed to DB.
+Every `BlockAggregatedChanges` message is sent to `PendingDeltasBuffer` (in addition to WebSocket
+clients). When an RPC query arrives, the handler fetches the DB snapshot then applies in-memory
+pending deltas on top, giving a consistent view up to the chain tip. Without this feed the RPC
+would lag by however many blocks remain in `ReorgBuffer` awaiting finalization.
+
+`db_committed_block_height` on each message tells `PendingDeltasBuffer` when a block has been
+written; it auto-drains those blocks so memory usage stays bounded.
+
+## Connections
+
+```
+ExtractorRunner (runner.rs)
+  ├─ SubstreamsStream (substreams/) → ProtocolExtractor (protocol_extractor.rs)
+  │    ├─ ReorgBuffer (reorg_buffer.rs) → CachedGateway → DB
+  │    ├─ ProtocolMemoryCache (protocol_cache.rs)
+  │    └─ DCIPlugin (dynamic_contract_indexer/) [optional]
+  └─ broadcast Arc<BlockAggregatedChanges>
+       ├─ WsService (services/ws.rs) → WebSocket clients
+       └─ PendingDeltasBuffer (services/deltas_buffer.rs)
+            └─ RpcHandlers (services/rpc.rs) → HTTP responses
+```
diff --git a/tycho-storage/CLAUDE.md b/tycho-storage/CLAUDE.md
@@ -0,0 +1,53 @@
+# tycho-storage
+
+PostgreSQL backend implementing the storage traits defined in `tycho-common`.
+
+## Module Map
+
+```
+postgres/
+├── mod.rs              — PostgresGateway (internal); shared enum caches; DB init helpers
+├── builder.rs          — GatewayBuilder: configures + constructs public gateways
+├── cache.rs            — CachedGateway + DBCacheWriteExecutor: buffered write path
+├── direct.rs           — DirectGateway: unbuffered read/write path (testing, auditing)
+├── chain.rs            — block & transaction persistence
+├── contract.rs         — account, code, storage slot, and native-balance persistence
+├── protocol.rs         — protocol component, attribute, and token-balance persistence
+├── entry_point.rs      — entry point + tracing param/result persistence
+├── extraction_state.rs — extractor checkpoint (cursor, block hash) persistence
+├── versioning.rs       — VersionedRow / StoredVersionedRow traits + apply_versioning()
+├── orm.rs              — Diesel Queryable/Insertable structs for every table
+└── schema.rs           — auto-generated Diesel table! macros
+```
+
+## Architecture
+
+All public DB operations go through one of two gateway structs:
+
+- **`CachedGateway`** (normal path): sends `WriteOp` messages over an async channel to
+  `DBCacheWriteExecutor`, which batches by block and flushes in a fixed order when the next
+  block arrives. Reads bypass the cache and hit the DB directly.
+- **`DirectGateway`** (testing / low-throughput): same trait surface, no buffering.
+
+Both delegate every actual SQL call to `PostgresGateway` (unexported). Domain logic lives in
+`chain`, `contract`, `protocol`, `entry_point`, and `extraction_state`—each adding methods to
+`PostgresGateway` via `impl` blocks in their own file.
+
+`versioning` is the only module without a DB table of its own; it provides the shared traits
+and `apply_versioning()` utility consumed by `contract` and `protocol`.
+
+## Write Order
+
+`DBCacheWriteExecutor` flushes ops in this fixed sequence to satisfy FK constraints:
+
+1. `UpsertBlock` → `UpsertTx` → `InsertContract` → `UpdateContracts`
+2. `InsertTokens` → `UpdateTokens` → `InsertAccountBalances`
+3. `InsertProtocolComponents` → `InsertComponentBalances` → `UpsertProtocolState`
+4. `InsertEntryPoints` → `InsertEntryPointTracingParams` → `UpsertTracedEntryPoints`
+5. `SaveExtractionState`
+
+## Temporal Model
+
+Every mutable entity carries `valid_from` / `valid_to` timestamps enabling time-travel
+queries. `versioning::apply_versioning()` sets `valid_to` on the previous row when a new
+version is inserted. Historical rows are never mutated.
PATCH

echo "Gold patch applied."
