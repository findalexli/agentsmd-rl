#!/usr/bin/env bash
set -euo pipefail

cd /workspace/core

# Idempotency guard
if grep -qF "| `relayer` | `mero-relayer` | `crates/relayer/src/main.rs` | Blockchain relay -" ".cursorrules"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursorrules b/.cursorrules
@@ -209,39 +209,217 @@ Examples:
 /workspace/
 ├── apps/           # Example/test WebAssembly applications
 ├── crates/         # Core library crates
-│   ├── auth/       # Authentication
-│   ├── config/     # Configuration
-│   ├── context/    # Context management
+│   ├── auth/       # Authentication service (mero-auth)
+│   ├── client/     # HTTP/WS client for node communication
+│   ├── config/     # Configuration management
+│   ├── context/    # Context lifecycle and membership
 │   ├── crypto/     # Cryptography utilities
-│   ├── meroctl/    # CLI tool
-│   ├── merod/      # Node daemon
+│   ├── dag/        # DAG for causal delta tracking
+│   ├── meroctl/    # CLI tool for node management
+│   ├── merod/      # Node daemon binary
 │   ├── network/    # P2P networking (libp2p)
-│   ├── node/       # Node orchestration
+│   ├── node/       # Node orchestration and sync
 │   ├── primitives/ # Shared primitive types
+│   ├── relayer/    # Blockchain relay service
 │   ├── runtime/    # WebAssembly runtime (wasmer)
 │   ├── sdk/        # SDK for app development
-│   ├── server/     # HTTP/WebSocket server
-│   ├── storage/    # CRDT-based storage
-│   └── store/      # Key-value store abstraction
-├── tools/          # Development tools
+│   ├── server/     # HTTP/WebSocket/SSE server
+│   ├── storage/    # CRDT-based storage collections
+│   └── store/      # Key-value store abstraction (RocksDB)
+├── tools/          # Development tools (merodb, calimero-abi)
 └── workflows/      # Test workflow definitions
 ```
 
+### Key Crate Purposes and Entry Points
+
+#### Binary Crates
+
+| Crate | Binary | Entry Point | Purpose |
+|-------|--------|-------------|---------|
+| `merod` | `merod` | `crates/merod/src/main.rs` | Node daemon - orchestrates WASM apps, storage, networking, RPC |
+| `meroctl` | `meroctl` | `crates/meroctl/src/main.rs` | CLI tool - manage nodes, apps, contexts, blobs |
+| `relayer` | `mero-relayer` | `crates/relayer/src/main.rs` | Blockchain relay - forwards requests to NEAR/ETH/ICP/Starknet |
+| `auth` | `mero-auth` | `crates/auth/src/main.rs` | Authentication service - JWT, user management |
+
+#### Core Library Crates
+
+| Crate | Key Module | Purpose |
+|-------|------------|---------|
+| `calimero-node` | `crates/node/src/lib.rs` | Main node runtime - coordinates sync, storage, networking |
+| `calimero-runtime` | `crates/runtime/src/lib.rs` | WASM execution engine (wasmer) - compiles and runs apps |
+| `calimero-storage` | `crates/storage/src/lib.rs` | CRDT collections (Counter, LwwRegister, UnorderedMap, Vector) |
+| `calimero-network` | `crates/network/src/lib.rs` | P2P networking - peer discovery, gossipsub, streams |
+| `calimero-server` | `crates/server/src/lib.rs` | HTTP/WS/SSE server - Admin API, JSON-RPC, WebSocket |
+| `calimero-context` | `crates/context/src/lib.rs` | Context lifecycle - creation, membership, state sync |
+| `calimero-dag` | `crates/dag/src/lib.rs` | DAG for causal ordering of deltas |
+| `calimero-store` | `crates/store/src/lib.rs` | Key-value store abstraction over RocksDB |
+| `calimero-sdk` | `crates/sdk/src/lib.rs` | App development SDK - macros, types, CRDT helpers |
+
+#### Support Crates
+
+| Crate | Purpose |
+|-------|---------|
+| `calimero-primitives` | Shared types: ContextId, ApplicationId, PublicKey, Hash |
+| `calimero-crypto` | Cryptographic utilities |
+| `calimero-config` | Configuration parsing and management |
+| `calimero-client` | HTTP/WS client for communicating with nodes |
+
+### Development Tools
+
+| Tool | Location | Purpose |
+|------|----------|---------|
+| `merodb` | `tools/merodb/` | RocksDB debugging - schema, export, validation, DAG visualization |
+| `calimero-abi` | `tools/calimero-abi/` | ABI extraction and inspection from WASM |
+
 ### Key Patterns
 
 - **Primitives crates**: Shared types go in `*-primitives` crates (e.g., `calimero-context-primitives`)
 - **Config crates**: Configuration types often in separate `*-config` crates
 - **Each folder is conceptually separate**: Treat each crate as its own project
+- **Actix actors**: Node components use the actix actor framework for async coordination
 
 ### Common Dependencies
 
 - `borsh` - Binary serialization for storage
 - `eyre` - Error handling
 - `tokio` - Async runtime
+- `actix` - Actor framework for node coordination
 - `libp2p` - P2P networking
 - `wasmer` - WebAssembly runtime
 - `serde` / `serde_json` - JSON serialization
 - `clap` - CLI argument parsing
+- `rocksdb` - Persistent key-value storage
+
+## Testing
+
+### Test Commands
+
+```bash
+# Run all tests
+cargo test
+
+# Run tests for a specific crate
+cargo test -p calimero-node
+cargo test -p calimero-storage
+cargo test -p calimero-dag
+
+# Run tests with output
+cargo test -- --nocapture
+
+# Run a specific test
+cargo test -p calimero-dag test_dag_out_of_order -- --nocapture
+
+# Run SDK macro tests (compile-time error tests)
+cargo test -p calimero-sdk-macros
+```
+
+### Building WASM Applications
+
+```bash
+# Add WASM target
+rustup target add wasm32-unknown-unknown
+
+# Build a specific app
+cargo build -p kv-store --target wasm32-unknown-unknown --release
+
+# Build all example apps
+./scripts/build-all-apps.sh
+```
+
+### Running Local Nodes
+
+```bash
+# Initialize and run a single node
+merod --node node1 init --server-port 2428 --swarm-port 2528
+merod --node node1 run
+
+# Initialize a second node connecting to the first
+merod --node node2 init --server-port 2429 --swarm-port 2529
+merod --node node2 config --swarm-addrs /ip4/127.0.0.1/tcp/2528
+merod --node node2 run
+```
+
+### Common Debugging Workflows
+
+#### Debugging Node Issues
+
+```bash
+# Enable debug logging
+RUST_LOG=debug merod --node node1 run
+
+# Enable verbose logging for specific crates
+RUST_LOG=calimero_node=debug,calimero_network=debug merod --node node1 run
+
+# Check node configuration
+cat ~/.calimero/node1/config.toml
+
+# Verify ports are available
+lsof -i :2428
+lsof -i :2528
+```
+
+#### Debugging Storage/State Issues
+
+```bash
+# Use merodb to inspect RocksDB database
+cargo run -p merodb -- --db-path ~/.calimero/node1/data --schema
+
+# Export database contents
+cargo run -p merodb -- --db-path ~/.calimero/node1/data --export --all \
+  --wasm-file ./target/wasm32-unknown-unknown/release/my_app.wasm \
+  --output export.json
+
+# Validate database integrity
+cargo run -p merodb -- --db-path ~/.calimero/node1/data --validate
+
+# Export DAG structure for visualization
+cargo run -p merodb -- --db-path ~/.calimero/node1/data --export-dag --output dag.json
+
+# Launch interactive GUI (requires gui feature)
+cargo run -p merodb --features gui -- --gui
+```
+
+#### Debugging WASM Execution
+
+```bash
+# Enable WASM tracing
+RUST_LOG=calimero_runtime=debug merod --node node1 run
+
+# Extract ABI from WASM
+cargo run -p mero-abi -- extract ./my_app.wasm
+
+# Inspect WASM state schema
+cargo run -p mero-abi -- state ./my_app.wasm
+```
+
+#### Debugging Network Issues
+
+```bash
+# Check peer connectivity
+meroctl --node node1 peers ls
+
+# Get peer details
+meroctl --node node1 peers get <peer_id>
+
+# Enable network debug logging
+RUST_LOG=calimero_network=debug,libp2p=debug merod --node node1 run
+```
+
+#### Using meroctl for Debugging
+
+```bash
+# List contexts
+meroctl --node node1 context ls
+
+# Get context details
+meroctl --node node1 context get <context_id>
+
+# List applications
+meroctl --node node1 app ls
+
+# Call a method (for testing)
+meroctl --node node1 call <context_id> --method get_value --args '{"key": "test"}'
+```
 
 ## CI Checks
 
@@ -260,6 +438,63 @@ PRs should include:
 2. **Test plan**: How to verify the changes
 3. **Documentation update**: What docs need updating
 
+## Key Architectural Concepts
+
+### Data Flow Overview
+
+```
+Client Request → JSON-RPC Server → WASM Runtime → Storage (CRDTs)
+                                         ↓
+                              State Delta → DAG → Network (Gossipsub)
+                                         ↓
+                              Other Nodes receive & apply delta
+```
+
+### Core Concepts
+
+1. **Context**: An instance of a deployed application where members share synchronized state
+   - Identified by 32-byte `ContextId`
+   - Members can join via invitation
+   - State changes broadcast to all members
+
+2. **CRDTs (Conflict-free Replicated Data Types)**: Automatic conflict resolution
+   - `Counter`: Distributed counter (increments sum)
+   - `LwwRegister<T>`: Last-write-wins register (timestamp-based)
+   - `UnorderedMap<K,V>`: Key-value map (entry-wise merge)
+   - `Vector<T>`: Ordered list (element-wise merge)
+   - `UnorderedSet<T>`: Unique values (union)
+
+3. **DAG (Directed Acyclic Graph)**: Causal ordering of state changes
+   - Each delta references parent deltas
+   - Handles out-of-order network delivery
+   - Automatic cascade when missing parents arrive
+
+4. **Gossipsub**: P2P message broadcasting
+   - Each context is a gossip topic
+   - Deltas propagate to all subscribed peers
+
+### Request Lifecycle
+
+1. Client sends JSON-RPC request to node server
+2. Server routes to appropriate handler (query or mutate)
+3. WASM runtime executes the method
+4. Storage layer records CRDT operations as actions
+5. Actions bundled into a delta with DAG parent references
+6. Delta broadcast via gossipsub to peers
+7. Peers apply delta, triggering any waiting deltas
+
+### Storage Architecture
+
+```
+Application State → CRDT Collections → Actions → Delta → DAG → RocksDB
+                                                           ↓
+                                                    Network Sync
+```
+
+- **RocksDB columns**: Meta, Config, Identity, State, Blobs, Application, Alias, Generic
+- **State keys**: Element IDs within CRDT collections
+- **Generic column**: DAG deltas and arbitrary key-value data
+
 ## Additional Notes
 
 - Cargo.toml dependencies should be sorted alphabetically
PATCH

echo "Gold patch applied."
