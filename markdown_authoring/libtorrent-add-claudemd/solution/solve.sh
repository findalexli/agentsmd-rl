#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libtorrent

# Idempotency guard
if grep -qF "`simulation/` contains network simulation tests that use `libsimulator` (a deter" ".claude/CLAUDE.md" && grep -qF "All messages are bencoded dicts with mandatory keys `\"t\"` (transaction id), `\"y\"" ".claude/rules/dht.md" && grep -qF "- `disk_cache` \u2014 the cache itself; holds a `boost::multi_index_container` of `ca" ".claude/rules/disk-cache.md" && grep -qF "- `info_idx` (`uint16_t`) \u2014 index into `m_block_info`; the slice `[info_idx * bl" ".claude/rules/piece-picker.md" && grep -qF "The type stub file is `bindings/python/libtorrent/__init__.pyi`. It was original" ".claude/rules/python-bindings.md" && grep -qF "`aux::strong_typedef<UnderlyingType, Tag>` wraps an integer so it is incompatibl" ".claude/rules/strong-types.md" && grep -qF "- `add_hashes()`: receives hashes + uncle proof chain, calls `merkle_validate_an" ".claude/rules/v2-torrents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -0,0 +1,235 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## Overview
+
+libtorrent-rasterbar is a C++17 BitTorrent library (version 2.1.0). It supports v1 and v2 torrents, DHT, WebTorrent (WebRTC), and optional I2P/SSL.
+
+## Build Systems
+
+The project has **two build systems**: boost-build (b2/bjam) and CMake. **Boost-build is the preferred build system** per the contributing guidelines.
+
+### Boost-build (b2) - preferred
+
+**Never add `-j` (parallel jobs) flags to b2 commands.** b2 manages parallelism on its own.
+
+Build the library (from repo root):
+```sh
+b2
+```
+
+Run unit tests:
+```sh
+cd test && b2
+```
+
+Run a single test:
+```sh
+cd test && b2 test_session
+```
+
+Run deterministic tests (no flaky networking):
+```sh
+cd test && b2 deterministic-tests
+```
+
+Run simulations:
+```sh
+cd simulation && b2
+```
+
+Build with developer options (typical for development):
+```sh
+cd test && b2 asserts=on invariant-checks=full debug-iterators=on picker-debugging=on
+```
+
+Build with sanitizers:
+```sh
+cd test && b2 address-sanitizer=norecover undefined-sanitizer=norecover asserts=on
+```
+
+Build examples, tools, fuzzers, python bindings:
+```sh
+cd examples && b2
+cd tools && b2
+cd fuzzers && b2 clang
+cd bindings/python && b2
+```
+
+### CMake — alternative
+
+```sh
+cmake -B build -DCMAKE_BUILD_TYPE=Debug -Dbuild_tests=ON
+cmake --build build
+cd build && ctest
+```
+
+Run a single test via CMake:
+```sh
+cd build && ./test/test_session
+```
+
+## Pre-commit
+
+The repo uses [pre-commit](https://pre-commit.com). Before pushing:
+```sh
+pip install pre-commit
+pre-commit install
+pre-commit run --all-files
+```
+
+Pre-commit hooks include trailing whitespace, YAML/TOML/XML checks, RST formatting, Python formatting (black, isort, flake8, mypy, autoflake), and auto-generation of:
+- `include/libtorrent/fwd.hpp` and `include/libtorrent/libtorrent.hpp` via `tools/gen_fwd.py` and `tools/gen_convenience_header.py`
+- C binding headers (`bindings/c/include/libtorrent_settings.h`, `libtorrent_alerts.h`) via `bindings/c/tools/gen_header.py` and `bindings/c/tools/gen_alert_header.py`
+
+## Key Architecture
+
+### Threading Model
+
+Three thread categories:
+1. **Main network thread** — all sockets, session/torrent/peer state, boost.asio event loop
+2. **Disk I/O thread(s)** — reads, writes, and SHA-1/SHA-256 piece verification (count controlled by `settings_pack::aio_threads`)
+3. **Resolver thread** — spawned by boost.asio for async DNS on platforms without native async getaddrinfo
+
+All interaction with session/torrent state from outside must go through the network thread (via `session_handle` and `torrent_handle`).
+
+### Core Classes
+
+- **`session`** (`include/libtorrent/session.hpp`) — public API, pimpl over `session_impl`
+- **`session_impl`** (`include/libtorrent/aux_/session_impl.hpp`) — all session state: torrent list, connection list, global rate limits, DHT state, port mapping
+- **`torrent`** (`include/libtorrent/aux_/torrent.hpp`, `src/torrent.cpp`) — all state for a single swarm: piece picker, peer connections, file storage
+- **`torrent_handle`** (`include/libtorrent/torrent_handle.hpp`) — public pimpl handle, weak reference to `torrent`; sends messages to network thread
+- **`peer_connection`** / **`bt_peer_connection`** — BitTorrent protocol implementation
+- **`piece_picker`** — download strategy (which blocks to request from which peers).  See `.claude/rules/piece-picker.md` for a detailed description.
+- **`peer_list`** — list of known (not necessarily connected) peers for a swarm
+
+### Disk I/O
+
+Three disk backends:
+- `mmap_disk_io` — mmap-based (default on 64-bit when mmap is available)
+- `posix_disk_io` — fallback single-threaded POSIX I/O (used on 32-bit or without mmap)
+- `pread_disk_io` — multi-threaded backend using `pread()`/`pwrite()`. See `.claude/rules/disk-cache.md` for a detailed description.
+
+### DHT (Kademlia)
+
+Source in `src/kademlia/`, headers in `include/libtorrent/kademlia/`. Includes ed25519 signing (`src/ed25519/`).
+
+### Extensions
+
+Protocol extensions live in `src/` and `include/libtorrent/extensions/`:
+- `ut_metadata` — magnet link metadata exchange
+- `ut_pex` — peer exchange
+- `smart_ban` — ban peers that send corrupt data
+- `i2p_pex` — peer exchange for I2P peers
+
+### WebTorrent (WebRTC)
+
+Optional feature controlled by `webtorrent=on` / `-Dwebtorrent=ON`. Uses `deps/libdatachannel` and the `rtc_stream`/`rtc_signaling` subsystem.
+
+### Python Bindings
+
+Source in `bindings/python/src/*.cpp`, built as `libtorrent.so` using boost.python. See `.claude/rules/python-bindings.md` for detailed conventions.
+
+### Simulations
+
+`simulation/` contains network simulation tests that use `libsimulator` (a deterministic virtual network). These test high-level behaviors (swarms, DHT, session management) without real network access. All simulation tests run with `invariant-checks=full`, `asserts=on`, `debug-iterators=on`.
+
+### Terminology
+
+- **piece** — SHA-1/SHA-256 verified chunk of torrent data (typically power-of-two size)
+- **block** — 16 KiB sub-unit of a piece (the transfer unit in the protocol)
+- **torrent_peer** — a known-but-not-connected peer entry
+- **peer_connection** — an active connection to a peer
+
+## Key Build Options (b2 features)
+
+| Feature | Values |
+|---------|--------|
+| `crypto` | `built-in`, `openssl`, `openssl-shared`, `wolfssl`, `gcrypt`, `gnutls`, `libcrypto` |
+| `asserts` | `on`, `off`, `production`, `system` |
+| `invariant-checks` | `off`, `on`, `full` |
+| `logging` | `on`, `off` |
+| `deprecated-functions` | `on`, `off`, `1`, `2`, `3`, `4` |
+| `webtorrent` | `on`, `off` |
+| `address-sanitizer` | `norecover`, `recover`, `off` |
+| `undefined-sanitizer` | `norecover`, `recover`, `off` |
+| `thread-sanitizer` | `norecover`, `recover`, `off` |
+| `picker-debugging` | `on`, `off` |
+| `debug-iterators` | `default`, `off`, `on`, `harden` |
+
+`deprecated-functions` selects the ABI/API version via `TORRENT_ABI_VERSION`. Different values are **link-incompatible**. Higher numbers expose a more modern interface and remove older deprecated APIs:
+
+| Value | `TORRENT_ABI_VERSION` | Corresponds to |
+|-------|-----------------------|----------------|
+| `on`  | (oldest supported)    | libtorrent 1.x |
+| `1`   | 1                     | libtorrent 1.x |
+| `2`   | 2                     | libtorrent 2.0 |
+| `3`   | 3                     | libtorrent 2.x |
+| `4`   | 4                     | libtorrent 2.1 |
+| `off` | 100 (newest)          | latest API     |
+
+## Directory Layout
+
+```
+src/                    main library source
+src/kademlia/           DHT implementation
+src/ed25519/            ed25519 signing (vendored)
+include/libtorrent/     public API headers
+include/libtorrent/aux_/  internal headers (not public API)
+include/libtorrent/kademlia/  DHT headers
+include/libtorrent/extensions/  extension headers
+test/                   unit tests (test_*.cpp)
+simulation/             network simulation tests (test_*.cpp)
+fuzzers/src/            fuzz targets
+examples/               example programs
+tools/                  utility scripts and programs
+bindings/python/        Python bindings (boost.python)
+bindings/c/             C API bindings
+deps/                   vendored dependencies
+  deps/try_signal/      signal handling
+  deps/asio-gnutls/     GnuTLS adapter for asio
+  deps/json/            nlohmann/json (for WebTorrent)
+  deps/libdatachannel/  WebRTC (for WebTorrent)
+```
+
+## Adding New Source Files
+
+When adding a new `.cpp` or `.hpp` file, it must be added to **all three** build systems:
+1. `Jamfile` (boost-build)
+2. `CMakeLists.txt`
+3. `Makefile` (if applicable)
+
+## Code-Generation Tools
+
+After modifying public API headers, regenerate the derived headers by running these scripts from the repo root:
+
+- `tools/gen_fwd.py` — regenerates `include/libtorrent/fwd.hpp` (forward declarations for all public types)
+- `tools/gen_convenience_header.py` — regenerates `include/libtorrent/libtorrent.hpp` (the convenience header that includes all public headers)
+
+These are also run automatically by the pre-commit hooks.
+
+## Coding Conventions
+
+- Comments must use ASCII characters only (no Unicode, smart quotes, em-dashes, etc.)
+- Use a single space after a period in comments (not two spaces)
+- Declare variables `const` whenever they are not reassigned after initialization
+- C++17 throughout; no C++20 features yet
+- `namespace lt = libtorrent` alias is always available
+- Asserts: use `TORRENT_ASSERT(cond)` (active when `TORRENT_USE_ASSERTS` is defined, i.e. debug builds)
+- Invariant checks: expensive checks inside `#if TORRENT_USE_INVARIANT_CHECKS`
+- Public API headers use `TORRENT_EXPORT` macro; internal symbols use hidden visibility
+- Internal functions and classes use `TORRENT_EXPORT_EXTRA` macro; to grant access to tests
+- ABI versioning via `TORRENT_VERSION_NAMESPACE_2/3/4` inline namespace macros (defined in `include/libtorrent/aux_/export.hpp`); `_2` = v1.2, `_3` = v2, `_4` = v2.1
+- Warnings are treated as errors in CI (both gcc and clang)
+- Changes to ABI (fields/ordering of public classes) must target `master`, not `RC_*` stable branches
+- `settings_pack` enum values must be appended at the end of each enum group (int, bool, string) — never inserted in the middle — to avoid changing the numeric values of existing settings and breaking ABI
+- prefer the C++ counterparts to C headers
+- do not use using-statements in header files
+- prefer to fully qualify standard types and functions
+- prefer the short lt namespace alias when fully qualifying libtorrent types
+- prefer using default member initializers over initializer list
+
+### Strong Types
+
+Avoid raw `int` for indices and flags; use `aux::strong_typedef` (`include/libtorrent/units.hpp`) and `flags::bitfield_flag` (`include/libtorrent/flags.hpp`). See `.claude/rules/strong-types.md` for details.
diff --git a/.claude/rules/dht.md b/.claude/rules/dht.md
@@ -0,0 +1,288 @@
+---
+paths:
+  - "src/kademlia/**"
+  - "include/libtorrent/kademlia/**"
+---
+
+# DHT (Kademlia) Implementation
+
+Source: `src/kademlia/`, `include/libtorrent/kademlia/`
+
+## BEP Support
+
+| BEP | Description | Status |
+|-----|-------------|--------|
+| BEP 5  | DHT Protocol (ping, find_node, get_peers, announce_peer) | Full |
+| BEP 32 | IPv6 extension (dual-stack, nodes6) | Full |
+| BEP 33 | DHT Scrape (bloom filters BFpe/BFsd) | Full |
+| BEP 42 | Node ID Verification (IP-derived IDs) | Full |
+| BEP 44 | Arbitrary data storage (immutable + mutable items, Ed25519) | Full |
+| BEP 51 | DHT Infohash Indexing (sample_infohashes) | Full |
+
+---
+
+## File Overview
+
+| File | Purpose |
+|------|---------|
+| `node.cpp` / `node.hpp` | Central DHT node — routing, dispatch, traversal lifecycle |
+| `dht_tracker.cpp` / `dht_tracker.hpp` | Session-level coordinator, one `node` per listen socket |
+| `routing_table.cpp` / `routing_table.hpp` | K-bucket routing table |
+| `rpc_manager.cpp` / `rpc_manager.hpp` | Tracks outstanding RPCs, calls observers on response/timeout |
+| `observer.hpp` | Base observer class for pending RPC state |
+| `traversal_algorithm.cpp` / `.hpp` | Base iterative search algorithm |
+| `find_data.cpp` / `.hpp` | Find-nodes traversal, base for get_peers and get_item |
+| `get_peers.cpp` / `.hpp` | BEP 5 peer lookup traversal |
+| `get_item.cpp` / `.hpp` | BEP 44 item retrieval traversal |
+| `put_data.cpp` / `.hpp` | BEP 44 item storage traversal |
+| `sample_infohashes.cpp` / `.hpp` | BEP 51 traversal |
+| `refresh.cpp` / `.hpp` | Bootstrap / bucket-refresh traversal |
+| `direct_request.hpp` | Single-message direct request |
+| `node_id.cpp` / `node_id.hpp` | `node_id` type (alias for `sha1_hash`), XOR distance, BEP 42 generation |
+| `node_entry.cpp` / `node_entry.hpp` | Single routing-table entry |
+| `item.cpp` / `item.hpp` | Mutable/immutable item type |
+| `types.hpp` | `public_key`, `secret_key`, `signature`, `sequence_number` |
+| `msg.hpp` | Incoming message structure |
+| `dht_storage.cpp` / `dht_storage.hpp` | Pure-virtual storage interface + default RAM implementation |
+| `dht_state.cpp` / `dht_state.hpp` | Persistent state (node IDs, bootstrap nodes) |
+| `dht_settings.hpp` | Per-DHT settings struct |
+| `dht_observer.hpp` | Callbacks from DHT into `session_impl` |
+| `dos_blocker.cpp` / `dos_blocker.hpp` | Per-IP rate limiting (5 pkt/s, 5-min block) |
+| `ed25519.hpp` | Ed25519 sign/verify API (vendored impl in `src/ed25519/`) |
+| `announce_flags.hpp` | Announce flags: `seed`, `implied_port`, `ssl_torrent` |
+
+---
+
+## Threading
+
+All DHT code runs on the **session network thread** (boost.asio). No locking needed inside DHT classes. `rpc_manager` uses a mutex only for its observer-pool allocator.
+
+---
+
+## Core Data Structures
+
+### `node_id`
+Type alias for `sha1_hash` (160 bits).
+
+Key functions:
+- `distance(a, b)` — XOR metric
+- `distance_exp(a, b)` — index of highest differing bit (0–160)
+- `compare_ref(a, b, ref)` — compare distances to reference
+- `generate_id(external_ip)` — BEP 42 derivation
+- `verify_id(nid, source_ip)` — BEP 42 check
+
+### `node_entry`
+One routing-table peer entry:
+- `node_id id`, `udp::endpoint endpoint`
+- `uint16_t rtt` (0xffff = unknown)
+- `uint8_t timeout_count` (0 = confirmed, 0xff = never pinged)
+- `bool verified` (BEP 42)
+- `time_point last_queried`
+
+### `routing_table`
+160 k-buckets (one per XOR distance bit). Extended routing table (default on) gives larger buckets close to us:
+
+| Bucket index | Multiplier | Max live nodes (k=20) |
+|---|---|---|
+| 0 | 16× | 320 |
+| 1 | 8× | 160 |
+| 2 | 4× | 80 |
+| 3 | 2× | 40 |
+| 4–159 | 1× | 20 (k) |
+
+Key behaviours:
+- Last (closest) bucket splits when it exceeds k entries
+- Each bucket has a **replacement cache**; candidates promoted when live node is removed
+- `ip_set` restricts one node per IP per bucket (BEP 42, `restrict_routing_ips`)
+- Periodic refresh: random query in each bucket's range every ~15 min
+
+### `item` (BEP 44)
+- **Immutable** — key is `sha1(value)`, no signature
+- **Mutable** — key is `sha1(salt || pk)`, Ed25519-signed, has `sequence_number`
+- CAS: `cas` field lets clients do compare-and-swap on sequence number
+
+### `dht_storage_interface`
+Pure-virtual; default RAM implementation (`dht_default_storage_constructor`):
+
+```
+map<sha1_hash, torrent_entry>        m_torrents       (BEP 5 peers)
+map<sha1_hash, dht_immutable_item>   m_immutable_items
+map<sha1_hash, dht_mutable_item>     m_mutable_items
+```
+
+Eviction uses distance from our node IDs — items far from us are evicted first.
+Limits: `max_torrents` (2000), `max_peers` (500), `max_dht_items` (700).
+Peer entries expire after 30 min (announce_interval).
+
+---
+
+## Key Classes
+
+### `node`
+One per listen socket. Owns `routing_table` and `rpc_manager`.
+
+Important methods:
+```cpp
+void bootstrap(endpoints, done_cb);
+void get_peers(info_hash, callback, flags);
+void announce(info_hash, port, flags, callback);
+void get_item(target, callback);           // immutable
+void get_item(pk, salt, callback);         // mutable
+void put_item(data, callback);             // immutable
+void put_item(pk, sk, salt, callback);     // mutable
+void sample_infohashes(endpoint, target, callback);
+void incoming(udp::endpoint, msg);         // dispatch received UDP
+void tick();                               // token rotation, bucket refresh
+```
+
+Write tokens: `hash(requester_ip + secret + info_hash)`. Two secrets kept; rotated periodically to allow stale tokens for one rotation period.
+
+### `dht_tracker`
+Owns `std::map<listen_socket_handle, tracker_node>` (one `node` per socket).
+Aggregates results across all nodes. Manages DOS blocking. Saves/restores `dht_state`.
+
+### `rpc_manager`
+- `invoke(entry, endpoint, observer_ptr)` — sends bencoded RPC, tracks by 2-byte transaction ID
+- `incoming(msg, &sender_id)` — looks up observer by txn-id, calls `observer::reply()`
+- `tick()` — fires `observer::timeout()` / `observer::short_timeout()` for stale requests
+- Uses an object pool for observers to reduce heap fragmentation
+
+### `observer`
+One per pending RPC. Flags:
+
+| Flag | Meaning |
+|------|---------|
+| `flag_queried` | Request sent |
+| `flag_initial` | First attempt |
+| `flag_short_timeout` | Intermediate timeout fired |
+| `flag_failed` | Node failed |
+| `flag_alive` | Response received |
+| `flag_done` | Finished, no longer tracked |
+
+Observer hierarchy:
+```
+observer
+  ├─ traversal_observer          (parses "nodes"/"nodes6" from responses)
+  │   ├─ find_data_observer
+  │   │   ├─ get_peers_observer  (also parses "values", bloom filters)
+  │   │   └─ get_item_observer   (parses v/k/sig/seq)
+  │   ├─ put_data_observer
+  │   └─ sample_infohashes_observer
+  ├─ announce_observer
+  ├─ direct_observer
+  └─ null_observer
+```
+
+---
+
+## Traversal Algorithms
+
+All searches inherit from `traversal_algorithm`. The base implements the Kademlia iterative lookup:
+
+1. Seed result set with k closest nodes from routing table
+2. Issue α (default 3) concurrent requests (`add_requests()`)
+3. Each response: add new closer nodes, sort result set
+4. Repeat until k closest nodes all responded or timeout
+5. Call `done()`
+
+| Class | BEP | RPC sent | Callback delivers |
+|-------|-----|----------|-------------------|
+| `find_data` | 5 | `find_node` | closest nodes + write tokens |
+| `get_peers` | 5 | `get_peers` | `vector<tcp::endpoint>` (peers) |
+| `get_item` | 44 | `get` | `item`, `bool authoritative` |
+| `put_data` | 44 | first `get`, then `put` | response count |
+| `sample_infohashes` | 51 | `sample_infohashes` | samples, interval, total |
+| `bootstrap` / `refresh` | 5 | `get_peers` (our own ID) | (fires bucket refresh) |
+| `direct_traversal` | — | arbitrary | single `msg` |
+
+`obfuscated_get_peers`: wraps `get_peers`, uses a random target until convergence, then switches to the real info_hash (BEP 5 privacy mode, controlled by `dht_privacy_lookups`).
+
+---
+
+## Message Format (bencode)
+
+All messages are bencoded dicts with mandatory keys `"t"` (transaction id), `"y"` (`"q"/"r"/"e"`), optional `"v"` (version), `"ip"` (external address, BEP 42), `"ro"` (read-only, BEP 5).
+
+**Queries** (`y="q"`): `"q"` = method name, `"a"` = argument dict with `"id"` (our node id, 20 bytes).
+
+**Responses** (`y="r"`): `"r"` = response dict.
+
+**Errors** (`y="e"`): `"e"` = `[error_code, "message"]`.
+
+### Method summary
+
+| Method | Key request fields | Key response fields |
+|--------|--------------------|---------------------|
+| `ping` | `id` | `id` |
+| `find_node` | `id`, `target`, `want` | `id`, `nodes`, `nodes6` |
+| `get_peers` | `id`, `info_hash`, `noseed`, `scrape`, `want` | `id`, `token`, `values`\|`nodes`, `BFpe`, `BFsd` |
+| `announce_peer` | `id`, `info_hash`, `port`, `token`, `implied_port`, `seed` | `id` |
+| `get` (BEP 44) | `id`, `target`, [`seq`] | `id`, `v`, [`k`, `sig`, `seq`] |
+| `put` (BEP 44) | `id`, `v`, [`k`, `sig`, `seq`, `salt`, `cas`] | `id` |
+| `sample_infohashes` | `id`, `target` | `id`, `samples`, `num`, `interval`, `nodes` |
+
+Compact node encoding: 26 bytes per IPv4 node (20-byte id + 4-byte IP + 2-byte port), 38 bytes for IPv6.
+
+---
+
+## Bootstrap
+
+1. Load `dht_state` (saved node IDs + endpoints)
+2. Assign node ID: saved → BEP 42 from external IP → random
+3. Add router nodes from settings (`router.bittorrent.com:6881`, etc.)
+4. Run `bootstrap` traversal against saved/configured endpoints (queries `get_peers` for own ID)
+5. On completion, refresh all non-contiguous buckets
+6. `dht_observer::get_peers()` notifies `session_impl` to query for all active torrents
+
+---
+
+## Integration with `session_impl`
+
+`session_impl` owns `shared_ptr<dht_tracker> m_dht` and implements `dht_observer`:
+
+| Observer method | When called |
+|-----------------|-------------|
+| `set_external_address()` | DHT detects our external IP via `"ip"` field |
+| `get_listen_port(socket)` | Node asks for our announce port |
+| `get_peers(info_hash, peer)` | Another node announced a peer to us |
+| `announce(info_hash, endpoint)` | We received a get_peers for one of our torrents |
+| `on_dht_request(method, msg, reply)` | Custom extension message handler |
+
+Session calls:
+- `dht_tracker::incoming_packet(socket, endpoint, buffer)` — for each received DHT UDP packet
+- `dht_tracker::new_socket(handle)` / `delete_socket(handle)` — listen port changes
+- `dht_tracker::tick()` — periodic maintenance
+
+Relevant `settings_pack` keys:
+
+| Setting | Effect |
+|---------|--------|
+| `enable_dht` | Toggle DHT |
+| `dht_search_branching` | Alpha (concurrent requests) |
+| `dht_max_peers_reply` | Peers returned per get_peers response |
+| `dht_enforce_node_id` | Reject nodes failing BEP 42 check |
+| `dht_restrict_routing_ips` | One node per /24 IPv4 per bucket |
+| `dht_restrict_search_ips` | Sybil mitigation in traversals |
+| `dht_privacy_lookups` | Enable obfuscated_get_peers |
+| `dht_read_only` | Set `ro=1` flag, don't accept queries |
+| `dht_upload_rate_limit` | Response bytes/sec cap |
+| `dht_item_lifetime` | BEP 44 item expiry (0 = never) |
+| `dht_sample_infohashes_interval` | BEP 51 cache TTL |
+
+---
+
+## Constants and Tunables
+
+| Parameter | Value | Notes |
+|-----------|-------|-------|
+| Node ID | 160 bits | SHA-1 |
+| k (bucket size) | 20 | Configurable |
+| Alpha | 3 | Concurrent requests per traversal |
+| RPC full timeout | 15 s | |
+| RPC short timeout | ~6 s | Triggers next request early |
+| Token rotation | ~7 min | Two tokens kept |
+| Bucket refresh | 15 min | Per-bucket, measured from last query |
+| Peer announce validity | 30 min | |
+| DOS block rate | 5 pkt/s | Per source IP |
+| DOS block duration | 5 min | |
+| DOS tracker size | 20 | Most-recent offenders |
diff --git a/.claude/rules/disk-cache.md b/.claude/rules/disk-cache.md
@@ -0,0 +1,44 @@
+---
+paths:
+  - "src/disk_cache*"
+  - "src/pread_disk_io*"
+  - "include/libtorrent/aux_/disk_cache*"
+---
+
+## Disk Cache (`pread_disk_io`)
+
+The disk cache (`src/disk_cache.cpp`, `include/libtorrent/aux_/disk_cache.hpp`) is used exclusively by `pread_disk_io`. It is a write-back cache for incoming blocks, deferred until pieces are complete or memory pressure forces a flush.
+
+**Data structures:**
+
+- `disk_cache` — the cache itself; holds a `boost::multi_index_container` of `cached_piece_entry` objects, protected by a single `std::mutex`. The container has five indices: by `piece_location` (ordered), by `cheap_to_flush()` (ordered descending), by `need_force_flush()` (ordered descending), by `piece_location` (hashed, for fast lookup), and by `needs_hasher_kick()` (ordered descending).
+- `cached_piece_entry` — one entry per in-flight piece. Contains an array of `cached_block_entry` (one per block), an optional `piece_hasher` (`ph`, v1 only), an optional `block_hashes` array (`sha256_hash[]`, v2 only), and the cursors/flags described below.
+- `cached_block_entry` — holds either a pending `write_job` (the buffer is owned by the job) or a `buf_holder` (buffer kept alive after the write job has executed but before hashing is done). Once both flushed and hashed, the buffer is freed.
+
+**Cursors:**
+
+- `hasher_cursor` — index of the first block not yet hashed (v1 SHA-1 only; hashing is always contiguous from block 0). Owned by the hashing thread while `hashing_flag` is set.
+- `flushed_cursor` — index of the first block not yet confirmed flushed to disk. Updated under the mutex after each flush completes.
+- `cheap_to_flush()` returns `hasher_cursor - flushed_cursor`: blocks that have been hashed but not yet flushed can be flushed without ever needing read-back.
+
+**Flags on `cached_piece_entry`:**
+
+Flags are stored in `cached_piece_flags flags` (a `bitfield_flag<uint8_t>` bitfield). The mutex must be held to read or modify flags; updates go through `view.modify()` (required by `boost::multi_index`). Once a flag is set, the owning thread may access the protected state **without the mutex**:
+
+- `hashing_flag` — set under the mutex by the thread about to hash blocks. While set, that thread has exclusive access to `ph` (the v1 `piece_hasher`) and may advance `hasher_cursor`. No other thread may touch these. Cleared under the mutex when hashing is complete.
+- `flushing_flag` — set under the mutex by the thread about to write blocks to disk. While set, that thread has exclusive access to the block buffers being flushed. No other thread will attempt to flush the same piece. Cleared under the mutex when flushing is complete.
+- `force_flush_flag` — set when the piece has all blocks populated; prioritises this piece for flushing. Cleared once all blocks are flushed.
+- `piece_hash_returned_flag` — set once the piece hash has been computed and returned to the BitTorrent engine.
+- `v1_hashes_flag` — set if this piece requires v1 SHA-1 hashing (`ph` is allocated).
+- `v2_hashes_flag` — set if this piece requires v2 SHA-256 block hashing (`block_hashes` is allocated).
+- `needs_hasher_kick_flag` — set when a block is inserted and the hasher thread should be woken; cleared when the hasher picks it up. Coalesces multiple insertions into one wakeup.
+
+In both hashing and flushing cases, the lock is **released** for the duration of the actual I/O (hashing or `pwrite()`), then re-acquired to update cursors/flags and potentially free buffers.
+
+**Deferred clear:** If `try_clear_piece()` is called while `flushing_flag` or `hashing_flag` is set, the clear job is stored in `cached_piece_entry::clear_piece` and executed by the owning thread once it clears its flag.
+
+**Flush strategy (`flush_to_disk`):**
+
+1. Force-flush pass — flush pieces with `force_flush` set (piece fully downloaded and hashed); ordered by `need_force_flush()`.
+2. Cheap flush pass — flush blocks in the range `[flushed_cursor, hasher_cursor)` (already hashed, no future read-back needed); pieces ordered by `cheap_to_flush()` descending.
+3. Expensive flush pass — flush any dirty blocks even if they haven't been hashed yet, requiring a read-back later to complete the piece hash. Used only when the cache exceeds the high-water mark.
diff --git a/.claude/rules/piece-picker.md b/.claude/rules/piece-picker.md
@@ -0,0 +1,134 @@
+---
+paths:
+  - "src/piece_picker.cpp"
+  - "include/libtorrent/aux_/piece_picker.hpp"
+  - "test/test_piece_picker.cpp"
+---
+
+## Piece Picker
+
+The piece picker (`src/piece_picker.cpp`, `include/libtorrent/aux_/piece_picker.hpp`) decides
+which blocks to request from which peers. It tracks availability (how many peers have each piece),
+per-piece priority, and the state of every block in every partially-downloaded piece.
+
+### Core data structures
+
+**`piece_pos`** — 8 bytes per piece, tightly packed:
+- `peer_count` (26 bits) — number of peers that have this piece
+- `download_state` (3 bits) — one of the `download_queue_t` constants below
+- `piece_priority` (3 bits) — 0 = filtered (dont-download), 1–7 user priority (4 = default)
+- `index` (`prio_index_t`) — position in `m_pieces`, or `we_have_index` (-1) if we have it
+
+**`m_piece_map`** — `aux::vector<piece_pos, piece_index_t>`, one entry per piece.
+
+**`m_pieces`** — flat `aux::vector<piece_index_t, prio_index_t>` of all pickable (not filtered,
+not have) pieces, sorted by effective priority. Within each priority band pieces are in random
+order (rarest-first is approximated by the priority formula, not by sorting on availability alone).
+
+**`m_priority_boundaries`** — cumulative end-indices into `m_pieces`. Priority band `p` spans
+`[m_priority_boundaries[p-1], m_priority_boundaries[p])`. Priority 0 starts at index 0.
+
+**`m_downloads`** — `aux::array` of 4 sorted `vector<downloading_piece>` (one per download
+category), indexed by `download_queue_t`:
+- `piece_downloading` (0) — some blocks still open (not yet requested)
+- `piece_full` (1) — all blocks requested, at least one not yet writing/finished
+- `piece_finished` (2) — all blocks writing or finished
+- `piece_zero_prio` (3) — downloading but priority = 0
+
+`piece_downloading_reverse` and `piece_full_reverse` are pseudo-states stored in `download_state`
+to de-prioritize pieces only requested from reverse peers; they map to the same download vectors
+as their non-reverse counterparts.
+
+**`downloading_piece`** — one per in-flight piece:
+- `info_idx` (`uint16_t`) — index into `m_block_info`; the slice `[info_idx * blocks_per_piece, (info_idx+1) * blocks_per_piece)` holds the block states for this piece
+- `finished`, `writing`, `requested` (15 bits each) — block state counters
+- `passed_hash_check` (1 bit) — hash job returned OK (piece may not yet be on disk)
+- `locked` (1 bit) — blocks cannot be picked; set during error recovery, cleared by `restore_piece()`
+- `hashing` (1 bit) — outstanding hash request in flight
+
+**`m_block_info`** — flat `aux::vector<block_info>`. Each downloading piece owns
+`blocks_per_piece()` consecutive entries identified by `info_idx`. Free ranges are recycled
+via `m_free_block_infos` (a free-list of `uint16_t` indices).
+
+**`block_info`** — per block:
+- `peer` — last peer to request/write this block
+- `num_peers` (14 bits) — peers with this block outstanding
+- `state` (2 bits) — `state_none → state_requested → state_writing → state_finished`
+
+### Priority formula
+
+`piece_pos::priority(picker)` returns -1 (not pickable) if: filtered, have, no availability
+(`peer_count + m_seeds == 0`), `piece_full`, or `piece_finished`.
+
+Otherwise:
+```
+priority = availability * (priority_levels - piece_priority) * prio_factor + adjustment
+```
+where `priority_levels = 8`, `prio_factor = 3`, and:
+- `adjustment = -3` for actively downloading pieces (non-reverse)
+- `adjustment = -2` for open pieces
+- `adjustment = -1` for reverse-downloading pieces
+
+Lower value = picked first. The `prio_factor = 3` creates three sub-levels per availability
+tier, letting downloading pieces beat open ones at the same availability.
+
+### Seeds optimization
+
+Peers with all pieces are tracked in `m_seeds` rather than incrementing every `peer_count`.
+True availability of a piece is `peer_count + m_seeds`. When a seed sends DONT_HAVE,
+`break_one_seed()` decrements `m_seeds` and increments every `piece_pos::peer_count`.
+
+### Lazy rebuild (`m_dirty`)
+
+`m_pieces` and `m_priority_boundaries` are rebuilt lazily. When `m_dirty` is true, they are
+stale; `update_pieces()` (called automatically before any pick) rebuilds them:
+1. Walk `m_piece_map`, count pieces per priority band → `m_priority_boundaries` holds deltas
+2. Make boundaries cumulative, resize `m_pieces`
+3. Fill `m_pieces` using per-piece relative offsets stored in `piece_pos::index`
+4. Shuffle each priority band randomly
+5. Fix up `piece_pos::index` to point back into the final positions in `m_pieces`
+
+Bulk operations (e.g. `inc_refcount(bitfield)` touching many pieces) set `m_dirty = true`
+rather than updating incrementally. For small bitfield changes (< 50 pieces), the picker
+updates incrementally via `update()` / `add()` / `remove()` without dirtying.
+
+### Sequential download cursors
+
+`m_cursor` — lowest piece index not yet had.
+`m_reverse_cursor` — one past the highest piece index not yet had (all pieces from here to end
+are had). `set_sequential_range(first, last)` constrains the cursor window.
+
+### Piece lifecycle
+
+```
+open → downloading → full → finished → (removed, piece_pos::have set)
+```
+
+- `mark_as_downloading(block, peer)` — block: none→requested; piece may transition open→downloading
+- `mark_as_writing(block, peer)` — block: requested→writing
+- `mark_as_finished(block, peer)` — block: writing→finished; calls `update_piece_state()` which
+  may advance the piece from downloading→full→finished
+- `piece_passed(index)` — hash check passed; sets `passed_hash_check`, calls `account_have()`,
+  calls `piece_flushed()` if all blocks are also finished
+- `piece_flushed(index)` — piece is on disk; removes from `m_downloads`, removes from `m_pieces`
+  via `remove()`, sets `piece_pos::index = we_have_index`
+- `restore_piece(index, blocks)` — after hash failure or write error; clears `locked`, optionally
+  resets specific blocks back to `state_none`, re-opens the piece for downloading
+
+### `pick_pieces` options
+
+`picker_options_t` flags passed to `pick_pieces()`:
+- `rarest_first` — pick lowest-availability pieces (the default; driven by the priority formula)
+- `reverse` — pick most-common first, or last pieces if sequential
+- `sequential` — pick within the `[m_cursor, m_reverse_cursor)` window in order
+- `on_parole` — only pick pieces exclusively requested by this peer (after suspected bad data)
+- `prioritize_partials` — prefer pieces already in `m_downloads` over fresh ones
+- `piece_extent_affinity` — create affinity for 4 MiB extents of adjacent pieces
+- `align_expanded_pieces` — align contiguous-block expansion to natural boundaries
+
+Auto partial prioritization: if `num_partials > num_peers * 3 / 2` or
+`num_partials * blocks_per_piece > 2048`, `prioritize_partials` is forced on and
+`prefer_contiguous_blocks` is set to 0 to avoid unbounded partial piece growth.
+
+`prefer_contiguous_blocks` (int, not a flag) — request this many consecutive blocks from the
+same piece; used by web peers to pipeline larger requests.
diff --git a/.claude/rules/python-bindings.md b/.claude/rules/python-bindings.md
@@ -0,0 +1,32 @@
+---
+paths:
+  - "bindings/python/**"
+---
+
+## Python Bindings
+
+Source in `bindings/python/src/*.cpp`; one `.cpp` file per exposed subsystem (e.g. `session.cpp`, `torrent_handle.cpp`, `alert.cpp`). Built as a Python extension module (`libtorrent.so`) using boost.python.
+
+**Building:**
+```sh
+cd bindings/python && b2
+```
+CMake also builds them when `-Dpython-bindings=ON` is passed.
+
+**Testing:**
+
+Tests live in `bindings/python/tests/*_test.py` and are run with pytest:
+```sh
+cd bindings/python && python -m pytest tests/
+```
+There is a roughly one-to-one correspondence between `src/foo.cpp` and `tests/foo_test.py`. Tests must be isolated — no real network access, no persistent filesystem side-effects. Use `get_isolated_settings()` from `tests/lib.py` when constructing a session, and `tempfile.TemporaryDirectory()` for any disk I/O. See `bindings/python/tests/guidelines.txt` for the full testing conventions.
+
+**Type stubs:**
+
+The type stub file is `bindings/python/libtorrent/__init__.pyi`. It was originally bootstrapped with `stubgen` but is now **maintained entirely by hand** — do not regenerate it with stubgen, as that would lose the carefully written annotations. When adding a new binding, add the corresponding type annotation to this file manually. The header comment in the file documents the conventions used (e.g. how boost.python enums, positional-only args, and the `_BoostBaseClass` metaclass are represented).
+
+**Design philosophy — classes over dicts:**
+
+Prefer exposing real C++ classes via boost.python rather than converting them to plain Python dicts. Earlier versions of the bindings returned plain `dict` objects for things like peer info and torrent status; these have been replaced with proper bound classes (`peer_info`, `torrent_status`, etc.) that mirror the C++ types. When adding new bindings, follow this pattern: expose the C++ struct/class directly rather than unpacking it into a dict.
+
+Note: boost.python strictly requires `dict` and `list` (not duck-typed `Mapping`/`Sequence` abstractions) for function arguments that cross the C++ boundary. This is a boost.python limitation and not a design choice; the type stubs reflect this with `dict` and `list` rather than `Mapping` or `Sequence`.
diff --git a/.claude/rules/strong-types.md b/.claude/rules/strong-types.md
@@ -0,0 +1,52 @@
+---
+paths:
+  - "include/libtorrent/units.hpp"
+  - "include/libtorrent/flags.hpp"
+  - "include/libtorrent/index_range.hpp"
+  - "include/libtorrent/**"
+  - "src/**"
+---
+
+## Strong Types
+
+The codebase avoids using raw `int` or bare integers for indices and flags. Instead, use the strong type and flag facilities.
+
+**Index types** (`include/libtorrent/units.hpp`):
+
+`aux::strong_typedef<UnderlyingType, Tag>` wraps an integer so it is incompatible with other integers and other strong types. Arithmetic with raw integers is not allowed; only arithmetic with the same type or its `diff_type` is permitted.
+
+To define a new index type:
+```cpp
+using my_index_t = aux::strong_typedef<std::int32_t, struct my_index_tag>;
+```
+
+To convert to/from the underlying integer, use an explicit cast:
+```cpp
+piece_index_t p{42};
+int raw = static_cast<int>(p);
+```
+
+To iterate over a range of indices, use `index_range` (`include/libtorrent/index_range.hpp`):
+```cpp
+for (piece_index_t i : index_range<piece_index_t>{begin, end}) { ... }
+```
+
+**Flag types** (`include/libtorrent/flags.hpp`):
+
+`flags::bitfield_flag<UnderlyingType, Tag>` wraps an unsigned integer as a type-safe bitfield. Flags of different types cannot be combined. Individual bit constants are defined using the `_bit` user-defined literal:
+
+```cpp
+using torrent_flags_t = flags::bitfield_flag<std::uint64_t, struct torrent_flags_tag>;
+static constexpr torrent_flags_t seed_mode = 0_bit;
+static constexpr torrent_flags_t upload_mode = 1_bit;
+```
+
+To define a new flag type:
+```cpp
+using my_flags_t = flags::bitfield_flag<std::uint32_t, struct my_flags_tag>;
+```
+
+Flag values support `|`, `&`, `^`, `~`, `|=`, `&=`, `^=`, and `operator bool()` (true if any bit is set). To test a flag:
+```cpp
+if (flags & torrent_flags::seed_mode) { ... }
+```
diff --git a/.claude/rules/v2-torrents.md b/.claude/rules/v2-torrents.md
@@ -0,0 +1,117 @@
+# BitTorrent v2 Torrents (BEP 52)
+
+## Info Dict Structure
+
+V2 uses a nested **`file tree`** dict instead of a flat `files` list:
+- Keys are filename path components; non-leaf = directory (nested dict)
+- Leaf nodes have empty-string key `""` → file metadata dict with `length`, `pieces root`, etc.
+- **`pieces root`** (32 bytes): root of the per-file merkle tree (SHA-256)
+- **`meta version`**: integer `2` identifies v2 metadata
+- **`piece layers`**: (outside info dict) maps `pieces root` → concatenated piece-layer hashes
+
+V2 torrents have a **SHA-256 info hash** (vs v1's SHA-1). `torrent_info::m_info_hash` holds both.
+
+## Per-File Merkle Tree
+
+Each file has an independent merkle tree (SHA-256, not SHA-1):
+
+```
+root (pieces root)
+  └── interior nodes
+        └── piece layer  ← hash of one piece's block subtree
+              └── block layer (leaf) ← hash of 16 KiB block
+```
+
+- **Block** = 16 KiB (fixed), the unit of transfer
+- **Piece** = `piece_length` bytes; must be a power-of-2 multiple of 16 KiB
+- Tree is **padded to a power of 2** in leaf count using `merkle_pad()` (zeros hashed up)
+- Interior nodes: `parent = SHA-256(left_child || right_child)`
+- Flat array indexing: node at layer `l`, offset `o` → index `(1 << l) - 1 + o`; parent = `(i-1)/2`
+
+Key helpers in `src/merkle.cpp`:
+- `merkle_num_leafs()`, `merkle_num_nodes()`, `merkle_num_layers()`
+- `merkle_fill_tree()` — compute interior nodes from leaves
+- `merkle_validate_and_insert_proofs()` — validate a proof chain against a known root
+- `merkle_pad()` — padding hash for odd tree levels
+
+## merkle_tree Class (`include/libtorrent/aux_/merkle_tree.hpp`)
+
+One instance per file, with four storage modes (optimization):
+
+| Mode | Stored nodes | When used |
+|------|-------------|-----------|
+| `empty_tree` | root only | single-block file, or tree completely unknown |
+| `piece_layer` | piece-layer hashes | piece hashes received, blocks not yet |
+| `block_layer` | block hashes | download complete, all blocks verified |
+| `full_tree` | all nodes | during partial verification |
+
+`m_block_verified` bitfield tracks which block hashes have been validated against their parent chain up to the known root.
+
+Key methods: `load_tree()`, `load_piece_layer()`, `add_hashes()`, `set_block()`
+
+## Hybrid Torrents (v1 + v2)
+
+A single `.torrent` file can contain both:
+- v1 info dict: `files` list + `pieces` SHA-1 concatenation
+- v2 `file tree` + `piece layers`
+
+Constraints: identical file layout, same `piece_length`. Results in two info hashes.
+`torrent_info` parsing uses `extract_files()` for v1 and `extract_files2()` for v2.
+
+## Hash Picker (`src/hash_picker.cpp`)
+
+Decides which merkle hashes to request from peers (BitTorrent v2 hash exchange protocol).
+
+**`hash_request` struct:**
+```cpp
+struct hash_request {
+  file_index_t file;
+  int base;         // tree layer (0 = block layer)
+  int index;        // starting offset in layer
+  int count;        // number of hashes (≤ 8192)
+  int proof_layers; // uncle hashes needed to prove against known root
+};
+```
+
+**Strategy:**
+1. Request piece-layer hashes in 512-piece chunks until all known
+2. On piece failure, request all block hashes for that piece (3s minimum interval)
+
+**Validation flow:**
+- `add_hashes()`: receives hashes + uncle proof chain, calls `merkle_validate_and_insert_proofs()`, inserts valid nodes, reports `pass`/`fail` per piece
+- `set_block()`: inserts a single block hash, finds largest verifiable subtree, returns pass/fail
+
+## Resume Data
+
+Merkle trees are persisted across sessions in resume data (`src/write_resume_data.cpp`, `src/read_resume_data.cpp`):
+
+```
+["merkle trees"][file_index]      → sparse tree nodes (non-zero nodes only)
+["merkle tree mask"][file_index]  → bitfield of which nodes are stored
+["verified bits"][file_index]     → m_block_verified bitfield
+["piece layers"][pieces_root]     → concatenated piece-layer hashes
+```
+
+- `write_resume_data()` uses `build_sparse_vector()` to encode only known nodes
+- `read_resume_data()` calls `load_sparse_tree()` to restore the partial tree
+- Piece layers are re-derived from the stored tree during write
+
+## Verification Flow
+
+1. File added → `merkle_tree` created with root hash from `pieces root`
+2. Block arrives → `set_block()` inserts hash, attempts validation up to root
+3. Piece complete → all block hashes in piece set; piece passes if tree validates
+4. Piece fails → clear invalid nodes; hash picker schedules block-hash requests
+5. Hashes received → `add_hashes()` validates proof chain, inserts valid nodes, marks failures
+6. Download complete → all blocks verified; block layer mode; tree fully populated
+
+## Key Files
+
+| File | Purpose |
+|------|---------|
+| `src/merkle.cpp` | Tree math, proof validation, padding |
+| `src/merkle_tree.cpp` + `include/libtorrent/aux_/merkle_tree.hpp` | Per-file tree storage |
+| `src/hash_picker.cpp` + `include/libtorrent/aux_/hash_picker.hpp` | Hash request scheduling |
+| `src/torrent_info.cpp` | Parsing `file tree`, `piece layers`, hybrid logic |
+| `src/create_torrent.cpp` | Building v2/hybrid `.torrent` files |
+| `src/write_resume_data.cpp` + `src/read_resume_data.cpp` | Persisting trees |
PATCH

echo "Gold patch applied."
