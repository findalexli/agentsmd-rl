#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quiche

# Idempotency guard
if grep -qF "Cloudflare's QUIC and HTTP/3 implementation in Rust. Workspace of 11 crates: cor" "AGENTS.md" && grep -qF "Low-level HTTP/3 testing client. Sends arbitrary/malformed H3 frames to probe se" "h3i/AGENTS.md" && grep -qF "Visualization/analysis tool for qlog and Chrome netlog files. Parses logs into a" "qlog-dancer/AGENTS.md" && grep -qF "qlog data model for QUIC and HTTP/3 per IETF drafts (`draft-ietf-quic-qlog-main-" "qlog/AGENTS.md" && grep -qF "Low-level QUIC transport and HTTP/3 in Rust. App provides IO/timers; this crate " "quiche/AGENTS.md" && grep -qF "HTTP/3 wire protocol over QUIC. `Connection` manages H3 state (streams, QPACK, S" "quiche/src/h3/AGENTS.md" && grep -qF "- `CongestionControlAlgorithm` values: Reno=0, CUBIC=1, Bbr2Gcongestion=4. Gap i" "quiche/src/recovery/AGENTS.md" && grep -qF "Async tokio wrapper for `quiche`. Spawns per-connection IO worker tasks driven b" "tokio-quiche/AGENTS.md" && grep -qF "Async HTTP/3 driver bridging `quiche::h3::Connection` to Tokio tasks via channel" "tokio-quiche/src/http3/driver/AGENTS.md" && grep -qF "Async QUIC connection management. Splits socket into recv-half (one `InboundPack" "tokio-quiche/src/quic/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,135 @@
+# PROJECT KNOWLEDGE BASE
+
+**Generated:** 2026-02-20
+**Commit:** 89d1850f
+**Branch:** master
+
+## OVERVIEW
+
+Cloudflare's QUIC and HTTP/3 implementation in Rust. Workspace of 11 crates: core `quiche` protocol library, `tokio-quiche` async integration, CLI tools (`apps`, `h3i`), logging/analysis (`qlog`, `qlog-dancer`, `netlog`), and supporting primitives (`octets`, `buffer-pool`, `datagram-socket`, `task-killswitch`).
+
+## STRUCTURE
+
+```
+quiche/                     # Core QUIC+H3 library (C FFI, BoringSSL submodule)
+tokio-quiche/               # Async tokio wrapper (server/client drivers)
+apps/                       # CLI binaries: quiche-client, quiche-server
+h3i/                        # HTTP/3 interactive testing/debugging tool
+qlog/                       # qlog event schema (RFC draft)
+qlog-dancer/                # qlog/netlog visualization (native + wasm)
+netlog/                     # Chrome netlog parser
+octets/                     # Zero-copy byte buffer primitives
+buffer-pool/                # Sharded lock-free buffer pool
+datagram-socket/            # UDP socket abstraction (sendmmsg/recvmmsg)
+task-killswitch/            # Async task cancellation primitive
+fuzz/                       # Fuzz targets (excluded from workspace)
+tools/                      # Android build tooling, http3_test harness
+```
+
+## DEPENDENCY GRAPH
+
+```
+octets  buffer-pool  task-killswitch  qlog  netlog    (Layer 0: no workspace deps)
+  |         |              |            |      |
+  v         v              |            v      v
+quiche  datagram-socket    |        qlog-dancer        (Layer 1)
+  |   \     |              |
+  v    \    v              v
+  tokio-quiche  <----------+                           (Layer 2: depends on most)
+  |     |
+  v     v
+ h3i   apps                                           (Layer 3: end-user tools)
+```
+
+## WHERE TO LOOK
+
+| Task | Location | Notes |
+|------|----------|-------|
+| QUIC connection logic | `quiche/src/lib.rs` | 9k lines, core `Connection` struct |
+| HTTP/3 protocol | `quiche/src/h3/mod.rs` | Own `Error`/`Result` types |
+| Congestion control | `quiche/src/recovery/` | Two impls: `congestion/` (legacy) + `gcongestion/` (BBR2) |
+| TLS/crypto backends | `quiche/src/tls/`, `quiche/src/crypto/` | BoringSSL + OpenSSL, cfg-gated |
+| C FFI | `quiche/src/ffi.rs` + `quiche/include/quiche.h` | Behind `ffi` feature |
+| Async server/client | `tokio-quiche/src/` | `ApplicationOverQuic` trait is the extension point |
+| H3 async driver | `tokio-quiche/src/http3/driver/` | `DriverHooks` sealed trait, channels |
+| QUIC IO worker | `tokio-quiche/src/quic/io/worker.rs` | Connection FSM, GSO/GRO |
+| Packet routing | `tokio-quiche/src/quic/router/` | Demux by DCID |
+| Test infra | `quiche/src/test_utils.rs` | `Pipe` struct for in-memory QUIC pairs |
+| Config cascade | `tokio-quiche/src/settings/` → `quiche::Config` | `ConnectionParams` → `quiche::Config` → `h3::Config` |
+
+## CODE MAP
+
+| Symbol | Type | Location | Role |
+|--------|------|----------|------|
+| `Connection` | struct | `quiche/src/lib.rs` | Core QUIC connection |
+| `Config` | struct | `quiche/src/lib.rs` | Transport configuration |
+| `h3::Connection` | struct | `quiche/src/h3/mod.rs` | HTTP/3 over QUIC |
+| `ApplicationOverQuic` | trait | `tokio-quiche/src/quic/` | Async app lifecycle hook |
+| `H3Driver<H>` | struct | `tokio-quiche/src/http3/driver/` | Generic H3 driver |
+| `IoWorker<Tx,M,S>` | struct | `tokio-quiche/src/quic/io/worker.rs` | Per-connection IO loop |
+| `Pipe` | struct | `quiche/src/test_utils.rs` | In-memory test connection pair |
+| `BufFactory` | trait | `quiche/src/range_buf.rs` | Zero-copy buffer creation |
+| `Recovery` | enum | `quiche/src/recovery/mod.rs` | CC dispatch via enum_dispatch |
+| `RecoveryOps` | trait | `quiche/src/recovery/mod.rs` | 40+ method CC interface |
+
+## CONVENTIONS
+
+- **Line width 82** (`rustfmt.toml`), comments 80. Nightly rustfmt required.
+- **One `use` per item** (`imports_granularity = "Item"`, vertical layout).
+- **`pub(crate)`** for cross-module internals; `pub` only for true public API.
+- **BSD-2-Clause copyright header** on every `.rs` file.
+- **`#[macro_use] extern crate log`** (legacy style, no `use log::*`).
+- **Domain abbreviations**: `cid`, `scid`/`dcid`, `pkt`, `dgram`, `bidi`/`uni`, `rtt`.
+- **`mod.rs` pattern** for submodules (not inline `foo/` + `foo.rs`).
+- **Debug symbols in release** (`profile.release.debug = true`).
+- **`#![warn(missing_docs)]`** -- public items must be documented.
+
+## ANTI-PATTERNS (THIS PROJECT)
+
+- **Do not use `any` types or type assertions** -- this is Rust; no equivalent concern, but `unsafe` is restricted to FFI boundaries (`tls/`, `crypto/`, `ffi.rs`, `gso.rs`).
+- **Do not add clippy `#[allow]` without justification** -- 33 existing overrides all have documented reasons.
+- **Cognitive complexity lint disabled** (`clippy.toml: 100`) -- complex functions accepted for protocol code, but don't add new ones casually.
+- **Two `Acked` types exist** in `recovery/congestion` and `recovery/gcongestion` -- not unified, don't create a third.
+- **`connection_not_present()` returns `TlsFail`** in tokio-quiche driver -- misleading sentinel, don't propagate this pattern.
+- **`Error::Done` used as success signal** in H3 driver write path -- non-obvious, don't replicate.
+- **`transmute` of `Instant`** in `gso.rs` -- fragile, platform-dependent, don't extend.
+
+## FEATURE FLAGS
+
+```
+quiche:        default=boringssl-vendored | boringssl-boring-crate | openssl
+               qlog, gcongestion, internal, ffi, fuzzing, sfv, custom-client-dcid
+tokio-quiche:  fuzzing, quiche_internal, gcongestion, zero-copy, rpk
+               (hardcodes: quiche/boringssl-boring-crate + quiche/qlog)
+h3i:           async (enables tokio-quiche dependency)
+```
+
+## COMMANDS
+
+```bash
+# Dev
+cargo build                                           # build workspace (vendored BoringSSL)
+cargo test --all-targets --features=async,ffi,qlog --workspace  # full test suite
+cargo test --doc --features=async,ffi,qlog --workspace          # doc tests (separate!)
+
+# Lint
+cargo clippy --features=boringssl-vendored --workspace -- -D warnings
+cargo fmt -- --check                                  # nightly only
+
+# Fuzz
+cargo fuzz run packet_recv_client -- -runs=1
+
+# Docker
+make docker-build                                     # quiche-base + quiche-qns images
+```
+
+## NOTES
+
+- **Git submodules required**: `git submodule update --init --recursive` for BoringSSL.
+- **MSRV 1.85**: `rust-version` field in Cargo.toml.
+- **Doc tests are separate**: `cargo test --all-targets` does NOT run doc tests (cargo#6669).
+- **`QUICHE_BSSL_PATH`**: env var to skip vendored BoringSSL build (use pre-built).
+- **`RUSTFLAGS="-D warnings"`**: CI enforces; all warnings are errors.
+- **Cargo.lock is gitignored** (library project).
+- **Dual CI**: GitHub Actions (real) + GitLab CI (no-op stub).
+- **`cargo package` disabled**: commented out due to unpublished local crate version issues.
diff --git a/h3i/AGENTS.md b/h3i/AGENTS.md
@@ -0,0 +1,51 @@
+# h3i
+
+## OVERVIEW
+
+Low-level HTTP/3 testing client. Sends arbitrary/malformed H3 frames to probe server RFC compliance. Both library (`lib.rs`) and CLI binary (`main.rs`). Used programmatically as test driver in tokio-quiche integration tests.
+
+## STRUCTURE
+
+```
+src/
+  lib.rs              # Crate root: quiche re-export, QPACK encoding, stream type constants
+  main.rs             # CLI binary: clap arg parsing, qlog I/O, dispatches to sync/async client
+  config.rs           # Config struct (QUIC transport params, TLS, host/port) + builder
+  frame.rs            # H3iFrame enum (Headers/QuicheH3/ResetStream), EnrichedHeaders, CloseTriggerFrame
+  frame_parser.rs     # Per-stream incremental frame parser (FrameParser, FrameParseResult)
+  actions/
+    h3.rs             # Action enum: SendFrame, SendHeadersFrame, StreamBytes, SendDatagram,
+                      #   OpenUniStream, ResetStream, StopSending, ConnectionClose, Wait, FlushPackets
+  client/
+    mod.rs            # Client trait, execute_action(), parse_streams(), shared logic
+    sync_client.rs    # Blocking mio-based client: connect() -> ConnectionSummary
+    async_client.rs   # tokio-quiche-based client (behind `async` feature)
+    connection_summary.rs  # ConnectionSummary: StreamMap + Stats + PathStats + close details
+  prompts/
+    h3/               # Interactive CLI prompts (inquire crate) for building Actions
+  recordreplay/
+    qlog.rs           # Action <-> qlog event conversion; replay from qlog files
+```
+
+## WHERE TO LOOK
+
+| Task | File | Notes |
+|------|------|-------|
+| Define new action type | `actions/h3.rs` | Add variant to `Action` enum |
+| Modify frame parsing | `frame_parser.rs` | `FrameParser::try_parse_frame` |
+| Change connection output | `client/connection_summary.rs` | `ConnectionSummary`, `StreamMap` (640 lines) |
+| Add CLI flags | `main.rs` | `config_from_clap()` uses clap v3 |
+| Library config | `config.rs` | `Config` struct + builder pattern |
+| Custom frame types | `frame.rs` | `H3iFrame` enum wraps quiche frames |
+| qlog record/replay | `recordreplay/qlog.rs` | Bidirectional: Action->qlog and qlog->Action |
+| Use as library | `lib.rs` doc example | `sync_client::connect(config, actions, close_triggers)` |
+
+## NOTES
+
+- **Feature gate**: `async` feature swaps sync mio client for tokio-quiche async client. Also changes quiche re-export path (`quiche` vs `tokio_quiche::quiche`).
+- **quiche `internal` feature**: always enabled -- accesses `quiche::h3::frame::Frame` internals for raw frame construction.
+- **Stream type constants**: `HTTP3_CONTROL_STREAM_TYPE_ID` (0x0), `QPACK_ENCODER_STREAM_TYPE_ID` (0x2), `QPACK_DECODER_STREAM_TYPE_ID` (0x3) in `lib.rs`.
+- **Action execution**: `client/mod.rs::execute_action()` matches on `Action` variants, writes directly to `quiche::Connection` streams -- no H3 connection layer.
+- **ConnectionSummary**: returned from both sync/async `connect()`. Contains per-stream frame maps, QUIC stats, path stats, close reason. Custom `Serialize` impl truncates binary at 16KB.
+- **Literal header encoding**: `encode_header_block_literal()` bypasses Huffman + lowercase normalization for testing malformed headers.
+- **Close triggers**: optional `CloseTriggerFrame` list causes automatic connection close when matching frame received.
diff --git a/qlog-dancer/AGENTS.md b/qlog-dancer/AGENTS.md
@@ -0,0 +1,64 @@
+# qlog-dancer/
+
+## OVERVIEW
+
+Visualization/analysis tool for qlog and Chrome netlog files. Parses logs into a `Datastore`, extracts time-series into `SeriesStore`, renders PNG charts (native) or canvas plots (wasm). Outputs HTML/text reports with tabled summaries.
+
+Dual-target: native CLI binary (`main.rs`) + wasm-bindgen web UI (`web.rs`, `#[cfg(target_arch = "wasm32")]`). `crate-type = ["lib", "cdylib"]` -- cdylib is for wasm.
+
+## STRUCTURE
+
+```
+src/
+  main.rs              CLI entry: parse args via AppConfig, render selected plots, emit report
+  lib.rs               Public API: parse_log_file(), PacketType, type aliases
+  web.rs               wasm-bindgen exports (851 lines), canvas rendering, JS interop
+  config.rs            AppConfig (clap CLI + wasm config), plot toggles, colors
+  datastore.rs         Datastore struct (~1985 lines) -- central parsed-log representation
+  seriesstore.rs       SeriesStore: extracts plot-ready time-series from Datastore
+  wirefilter.rs        Event filtering via cloudflare/wirefilter-engine DSL
+  request_stub.rs      Stub types for request-level data
+  plots/               Chart rendering (plotters crate)
+    mod.rs             PlotParameters, ChartSize, ClampParams, output type enums
+    conn_overview.rs   Multi-panel connection overview (cwnd, bytes, rtt, streams)
+    congestion_control.rs  CC-specific plot
+    conn_flow_control.rs   Connection-level flow control
+    packet_sent.rs     Packet-number vs time scatter
+    packet_received.rs Received packet scatter
+    stream_sparks.rs   Per-stream sparkline grids
+    stream_multiplex.rs  Stream multiplexing timeline
+    pending.rs         Pending data plot
+    rtt.rs             RTT plot
+    colors.rs          Color palettes
+    minmax.rs          Axis range utilities
+  reports/             Output reports
+    mod.rs             report() dispatcher
+    html.rs            HTML report generation (table_to_html)
+    text.rs            Plain-text summary
+    events.rs          Event-level report details
+  trackers/            Stateful metric accumulators
+    stream_buffer_tracker.rs  Per-stream buffer sizes
+    stream_max_tracker.rs     Stream high-water marks
+index.html, *.js, *.css   Web UI assets (crate root, non-standard location)
+```
+
+## WHERE TO LOOK
+
+| Task | File |
+|------|------|
+| Add new plot type | `src/plots/` -- add module, wire into `main.rs` + `web.rs` |
+| Change parsed fields | `src/datastore.rs` -- all log-to-struct extraction |
+| Add series for plotting | `src/seriesstore.rs` |
+| Modify event filters | `src/wirefilter.rs` (wirefilter-engine DSL) |
+| CLI args / config | `src/config.rs` (AppConfig, clap) |
+| Wasm API surface | `src/web.rs` (`#[wasm_bindgen]` exports) |
+| Report formatting | `src/reports/` |
+
+## NOTES
+
+- Native build requires system libs: **libexpat, freetype, fontconfig** (plotters SVG/bitmap backends).
+- Wasm uses `plotters-canvas` backend -- canvas rendering, no system deps.
+- `wirefilter-engine` pinned to specific git rev, not on crates.io.
+- Log format auto-detection: tries qlog JSON, falls back to JSON-SEQ (sqlog), and vice versa.
+- `getrandom/wasm_js` feature + `.cargo/config.toml` needed for wasm randomness.
+- Web assets (`index.html`, `qlog-dancer-ui.js`, `qlog-dancer.css`) live in crate root, not `src/`.
diff --git a/qlog/AGENTS.md b/qlog/AGENTS.md
@@ -0,0 +1,43 @@
+# qlog/
+
+qlog data model for QUIC and HTTP/3 per IETF drafts (`draft-ietf-quic-qlog-main-schema`, `draft-ietf-quic-qlog-quic-events`, `draft-ietf-quic-qlog-h3-events`). Pure data types + serde serialization; no IO (deferred to consumers).
+
+## STRUCTURE
+
+```
+src/
+  lib.rs          # Core types: Qlog, QlogSeq, Trace, TraceSeq, VantagePoint, Configuration, Error
+  streamer.rs     # QlogStreamer -- streaming JSON-SEQ writer with state machine
+  reader.rs       # QlogSeqReader -- streaming JSON-SEQ reader/iterator
+  events/
+    mod.rs        # Event, EventData (giant enum), EventType, Eventable trait, EventImportance
+    quic.rs       # QUIC event types (packet_sent, packet_received, frames, etc.)
+    h3.rs         # HTTP/3 event types
+    qpack.rs      # QPACK event types
+    connectivity.rs  # Connection-level events (state changes, path updates)
+    security.rs   # TLS/crypto events
+  testing/
+    mod.rs        # Test helpers
+    event_tests.rs
+    trace_tests.rs
+```
+
+## WHERE TO LOOK
+
+| Task | File | Notes |
+|------|------|-------|
+| Add new event variant | `events/mod.rs` `EventData` enum | Add to relevant `events/*.rs`, wire into `EventData` |
+| Modify serialization | `lib.rs` | Heavy `serde_with` usage; `#[serde(rename)]` everywhere |
+| Streaming output | `streamer.rs` | `QlogStreamer` writes JSON-SEQ (RFC 7464) via `Write` trait |
+| Parse qlog files | `reader.rs` | `QlogSeqReader` iterates events from `BufRead` |
+| `Eventable` trait | `events/mod.rs:310` | Requires `importance()` and event name; impl on all event enums |
+| Two output modes | `lib.rs` | Buffered (`Qlog`/`Trace`) vs streaming (`QlogSeq`/`TraceSeq`) |
+
+## NOTES
+
+- Deps: `serde`, `serde_json` (preserve_order), `serde_with`, `smallvec`. No async, no IO beyond `Write`/`BufRead`.
+- `EventData` is a massive enum (~200 variants) spanning all protocol categories. Grep, don't scroll.
+- JSON field names follow IETF draft conventions (`snake_case`), mapped via `#[serde(rename)]`.
+- `serde_json::preserve_order` keeps field insertion order in output.
+- `HexSlice` helper for hex-encoding byte arrays in JSON.
+- No feature flags.
diff --git a/quiche/AGENTS.md b/quiche/AGENTS.md
@@ -0,0 +1,74 @@
+# quiche/ — Core QUIC + HTTP/3 Library
+
+## OVERVIEW
+
+Low-level QUIC transport and HTTP/3 in Rust. App provides IO/timers; this crate handles protocol state. Also exposes C FFI via `staticlib`/`cdylib`.
+
+## STRUCTURE
+
+```
+src/
+  lib.rs          (9k lines) Connection struct, Config, connect()/accept() entry points
+  h3/
+    mod.rs        (7.5k)     HTTP/3 connection — own Error/Result types, NOT quiche::Error
+    qpack/                   QPACK header compression
+  recovery/
+    mod.rs                   Recovery enum, RecoveryOps trait (enum_dispatch)
+    congestion/              Legacy CC (Cubic, Reno, Hystart++)
+    gcongestion/             Google-derived CC (BBR2) — behind `gcongestion` feature
+  stream/                    Stream state machine, flow control per-stream
+  tls/                       TLS backend abstraction (BoringSSL / OpenSSL)
+  crypto/                    Packet protection, key derivation
+  packet.rs       (2.3k)     Packet parsing, ConnectionId, Header
+  frame.rs                   QUIC frame encode/decode
+  path.rs                    Multi-path state, PathEvent, migration
+  pmtud.rs                   Path MTU discovery
+  cid.rs                     Connection ID management
+  ffi.rs          (2.3k)     C FFI — behind `ffi` feature
+  transport_params.rs        QUIC transport parameter encode/decode
+  flowcontrol.rs             Connection-level flow control
+  ranges.rs                  ACK range tracking
+  range_buf.rs               BufFactory/BufSplit traits for zero-copy buffer creation
+  dgram.rs                   DATAGRAM frame support
+  rand.rs                    Random number generation
+  minmax.rs                  Windowed min/max filter
+  test_utils.rs              Pipe struct for in-memory QUIC pairs (pub via `internal` feature)
+  tests.rs        (12k)      Integration tests
+  build.rs                   BoringSSL cmake build (NOTE: lives in src/, not crate root)
+include/
+  quiche.h        (1.2k)     C API header — mirrors ffi.rs
+deps/
+  boringssl/                 Git submodule
+```
+
+## WHERE TO LOOK
+
+| Task | Start here |
+|------|-----------|
+| Connection lifecycle | `lib.rs` — `Connection` struct, `recv()`, `send()` |
+| HTTP/3 streams/headers | `h3/mod.rs` — `h3::Connection` |
+| Loss detection / CC | `recovery/mod.rs` → `congestion/` or `gcongestion/` |
+| Packet parse/serialize | `packet.rs`, `frame.rs` |
+| TLS handshake | `tls/mod.rs` — cfg-gated per backend |
+| C bindings | `ffi.rs` + `include/quiche.h` |
+| Test harness | `test_utils.rs` (`Pipe` struct) |
+| Build system | `src/build.rs` — BoringSSL cmake, cross-compile params |
+
+## ANTI-PATTERNS
+
+- **h3::Error != quiche::Error** — don't mix or convert carelessly; they have different variant sets.
+- **`Error::Done` is a success signal** in many read/write loops — not a failure.
+- **Don't add new CC impls** outside `recovery/` — two parallel impls (congestion + gcongestion) already exist.
+- **`unsafe` only at FFI boundaries** — `tls/`, `crypto/`, `ffi.rs`; don't add elsewhere.
+- **`#[cfg(feature = "fuzzing")]`** disables real crypto — never accidentally gate non-test code on it.
+
+## NOTES
+
+- `build.rs` is at `src/build.rs` (Cargo.toml: `build = "src/build.rs"`), not crate root.
+- Three TLS backends: `boringssl-vendored` (default), `boringssl-boring-crate`, `openssl` — mutually exclusive features.
+- `quiche::Error` is `Copy + Clone` — intentional for hot-path ergonomics.
+- `test_utils::Pipe` exposed via `internal` feature for downstream crate integration tests.
+- Tests use `rstest` with `#[values("cubic", "bbr2_gcongestion")]` parameterization for CC coverage.
+- `QUICHE_BSSL_PATH` env var skips vendored BoringSSL build.
+- Crate-type: `lib` + `staticlib` + `cdylib` — the latter two for C consumers.
+- `BufFactory` trait (`range_buf.rs`) enables zero-copy buffer creation; `Connection<F>` is generic over it.
diff --git a/quiche/src/h3/AGENTS.md b/quiche/src/h3/AGENTS.md
@@ -0,0 +1,54 @@
+# quiche/src/h3/ — HTTP/3 Module
+
+## OVERVIEW
+
+HTTP/3 wire protocol over QUIC. `Connection` manages H3 state (streams, QPACK, SETTINGS, GOAWAY) on top of `quiche::Connection<F>`. Event-driven: caller loops `poll()` → `Event`. Own `Error`/`Result` types, separate from `quiche::Error`.
+
+## STRUCTURE
+
+```
+mod.rs       (7549 lines)  H3 Connection, Config, Error, Event, Header, NameValue, Priority
+stream.rs    (1565)        H3 stream state machine (Type, State enums; frame parsing FSM)
+frame.rs     (1337)        H3 frame encode/decode (Frame enum, settings constants)
+ffi.rs                     C FFI for H3 — behind `ffi` feature
+qpack/
+  mod.rs                   Re-exports
+  encoder.rs               QPACK encoder
+  decoder.rs               QPACK decoder
+  static_table.rs          Static header table (RFC 9204)
+```
+
+## WHERE TO LOOK
+
+| Task | Location |
+|------|----------|
+| Send/recv requests+responses | `mod.rs` — `send_request()`, `send_response()`, `poll()` |
+| Body data | `mod.rs` — `send_body()`, `recv_body()` |
+| Priority handling | `mod.rs` — `Priority` struct, `send_priority_update_for_request()` |
+| H3 stream lifecycle | `stream.rs` — `Stream` struct, `State` FSM |
+| Frame wire format | `frame.rs` — `Frame` enum, `encode()`/`decode()` |
+| QPACK header compression | `qpack/encoder.rs`, `qpack/decoder.rs` |
+| H3 C API | `ffi.rs` |
+
+## ANTI-PATTERNS
+
+- **h3::Error != quiche::Error.** 19 variants; `TransportError(quiche::Error)` wraps transport errors. Don't confuse.
+- **`Error::Done` is success** in poll/read loops. Not a failure — signals "no more work".
+- **`to_wire()` maps `BufferTooShort` → `0x999`** — non-standard wire code. Don't propagate this pattern.
+- **`to_c()` skips -12** — was previously `TransportError`. Gap is intentional for ABI stability.
+- **`to_c()` for `TransportError`:** offsets by `-1000` from underlying `quic_error.to_c()`.
+- **`send_request()` sends empty `b""` to create QUIC stream** before writing headers. Required because QUIC stream doesn't exist until first write.
+- **stream.rs `Stream` ≠ quiche::stream::Stream.** H3 stream is a frame-parsing state machine layered on top.
+
+## NOTES
+
+- Methods are generic over `F: BufFactory` (zero-copy) and `T: NameValue` (header access).
+- `NameValue` trait: `name() -> &[u8]`, `value() -> &[u8]`. Blanket impl for `(N, V)` tuples.
+- `Header` is `(Vec<u8>, Vec<u8>)` newtype implementing `NameValue`.
+- `Event` variants: `Headers`, `Data`, `Finished`, `Reset(u64)`, `PriorityUpdate`, `GoAway`.
+- Priority: RFC 9218 Extensible Priorities. `sfv` feature enables `TryFrom` parsing.
+- `PRIORITY_URGENCY_OFFSET = 124` maps external urgency 0-7 to internal quiche priority.
+- `APPLICATION_PROTOCOL = &[b"h3"]` — ALPN constant.
+- `From<quiche::Error>` converts `Done→Done`, everything else → `TransportError(e)`.
+- `From<octets::BufferTooShortError>` → `Error::BufferTooShort`.
+- All `#[cfg(feature = "qlog")]` instrumentation inline in mod.rs — heavy conditional compilation.
diff --git a/quiche/src/recovery/AGENTS.md b/quiche/src/recovery/AGENTS.md
@@ -0,0 +1,80 @@
+# recovery/ -- Loss Detection & Congestion Control
+
+## OVERVIEW
+
+QUIC loss detection and congestion control per RFC 9002. Two parallel CC
+implementations coexist: `congestion/` (legacy Reno/CUBIC) and `gcongestion/`
+(next-gen BBR2 ported from google/quiche). `Recovery` enum dispatches between
+`LegacyRecovery` and `GRecovery` via `enum_dispatch` over the `RecoveryOps`
+trait (40+ methods).
+
+## STRUCTURE
+
+```
+mod.rs              Recovery enum, RecoveryOps trait, CongestionControlAlgorithm,
+                    Sent, ReleaseTime/ReleaseDecision, RecoveryConfig, constants
+bandwidth.rs        Bandwidth newtype
+bytes_in_flight.rs  Bytes-in-flight tracking
+rtt.rs              RTT estimation
+
+congestion/         Legacy CC (Reno, CUBIC)
+  mod.rs            CongestionControlOps vtable struct, Congestion state
+  recovery.rs       LegacyRecovery impl of RecoveryOps, Acked struct
+  reno.rs           Static RENO: CongestionControlOps
+  cubic.rs          Static CUBIC: CongestionControlOps
+  delivery_rate.rs  Delivery rate sampling
+  hystart.rs        HyStart slow-start exit
+  prr.rs            Proportional Rate Reduction
+  test_sender.rs    Test-only CC sender
+
+gcongestion/        Next-gen CC (BBR2)
+  mod.rs            CongestionControl trait, Acked struct, BbrParams (#[doc(hidden)])
+  recovery.rs       GRecovery impl of RecoveryOps
+  pacer.rs          Token-bucket pacer
+  bbr2.rs           BBR2 top-level + Bbr2CongestionControl
+  bbr2/             BBR2 state machine substates
+    mode.rs         Mode enum (Startup, Drain, ProbeBw, ProbeRtt)
+    startup.rs      Startup mode
+    drain.rs        Drain mode
+    probe_bw.rs     ProbeBW mode (bandwidth probing cycles)
+    probe_rtt.rs    ProbeRTT mode (min RTT measurement)
+    network_model.rs  Bandwidth/RTT model, BbrParams application
+  bbr.rs            BBR (v1, not actively used)
+```
+
+## WHERE TO LOOK
+
+| Task | File | Notes |
+|------|------|-------|
+| Add/change CC algorithm | `congestion/mod.rs` or `gcongestion/mod.rs` | Different dispatch patterns |
+| Modify loss detection | `congestion/recovery.rs` or `gcongestion/recovery.rs` | Parallel impls |
+| Shared trait surface | `mod.rs:183-320` | `RecoveryOps` -- both impls must satisfy |
+| Algorithm selection | `mod.rs:365` | `CongestionControlAlgorithm` enum, `#[repr(C)]` for FFI |
+| BBR2 tuning | `gcongestion/bbr2/network_model.rs` | `BbrParams` applied here |
+| Pacing | `gcongestion/pacer.rs`, `mod.rs:691` | `ReleaseTime`, `ReleaseDecision` |
+| Per-packet metadata | `mod.rs:394` | `Sent` struct |
+| qlog integration | grep `#[cfg(feature = "qlog")]` | Gated throughout both impls |
+
+## ANTI-PATTERNS
+
+- **Two `Acked` structs** at `congestion/recovery.rs:1079` and `gcongestion/mod.rs:49`.
+  NOT unified. Do NOT create a third.
+- **FIXME stubs**: Some `RecoveryOps` methods only apply to one impl. Both sides
+  have `// FIXME only used by {congestion,gcongestion}` stubs that return
+  defaults. Do not proliferate; prefer narrowing the shared trait.
+- **`congestion/` uses C-like vtable** (`CongestionControlOps` with static fn
+  pointers: `RENO`, `CUBIC`). `gcongestion/` uses trait objects
+  (`CongestionControl` trait). Do not mix dispatch styles.
+- **`BbrParams` is `#[doc(hidden)]`** and experimental. Do not stabilize or
+  expose without explicit intent.
+- **Many `#[cfg(test)]` accessors** on `RecoveryOps` (lines 200-297). Test-only;
+  do not call from production code.
+
+## NOTES
+
+- Constants cite RFC 9002: `INITIAL_TIME_THRESHOLD = 9.0/8.0`, `GRANULARITY = 1ms`.
+- `CongestionControlAlgorithm` values: Reno=0, CUBIC=1, Bbr2Gcongestion=4. Gap is intentional (removed variants).
+- `Recovery::new_with_config` tries `GRecovery::new` first; falls back to `LegacyRecovery` if algo is Reno/CUBIC.
+- `bbr2/` is a deeply nested state machine -- changes require understanding all six substates.
+- `enable_relaxed_loss_threshold` experiment adjusts time thresholds dynamically on spurious loss.
+- `gcongestion/bbr.rs` is BBRv1 -- mostly vestigial alongside BBR2.
diff --git a/tokio-quiche/AGENTS.md b/tokio-quiche/AGENTS.md
@@ -0,0 +1,79 @@
+# tokio-quiche
+
+## OVERVIEW
+
+Async tokio wrapper for `quiche`. Spawns per-connection IO worker tasks driven by an `ApplicationOverQuic` trait. Ships a ready-made `H3Driver` for HTTP/3. Uses `foundations` for structured logging (slog), telemetry, and settings.
+
+## STRUCTURE
+
+```
+src/
+  lib.rs              Re-exports, listen(), capture_quiche_logs()
+  buf_factory.rs      BufFactory: tiered static pools, QuicheBuf (zero-copy feature)
+  result.rs           BoxError = Box<dyn Error+Send+Sync>, QuicResult<T>
+  settings/           ConnectionParams → quiche::Config → h3::Config cascade
+  metrics/            Metrics trait (pluggable); DefaultMetrics (foundations Prometheus)
+  socket/             Socket<Tx,Rx>, QuicListener, SocketCapabilities (GSO/GRO)
+  quic/               connect(), start_listener(), ApplicationOverQuic, IoWorker, router
+  http3/              H3Driver<H>, DriverHooks (sealed), client/server controllers
+```
+
+## WHERE TO LOOK
+
+| Task | Location |
+|------|----------|
+| Server entrypoint | `lib.rs` — `listen()`, `listen_with_capabilities()` |
+| Client entrypoint | `quic/mod.rs` — `connect()`, `connect_with_config()` |
+| Custom app trait | `quic/connection/mod.rs:663` — `ApplicationOverQuic` |
+| H3 driver (main logic) | `http3/driver/mod.rs` — `H3Driver<H>` |
+| Per-connection IO loop | `quic/io/worker.rs` — `IoWorker` |
+| Packet routing/demux | `quic/router/mod.rs` — `InboundPacketRouter` |
+| Config cascade | `settings/config.rs` — `Config::new()` |
+| Buffer pools | `buf_factory.rs` — `BufFactory`, static pools |
+| Metrics interface | `metrics/mod.rs` — `Metrics` trait |
+
+## CODE MAP
+
+| Symbol | Type | Location | Role |
+|--------|------|----------|------|
+| `ApplicationOverQuic` | trait | `quic/connection/mod.rs` | Extension point: on_conn_established, process_reads/writes, wait_for_data |
+| `H3Driver<H>` | struct | `http3/driver/mod.rs` | Implements `ApplicationOverQuic` for HTTP/3 |
+| `DriverHooks` | sealed trait | `http3/driver/hooks.rs` | Client vs server H3 behavior |
+| `IoWorker<Tx,M,S>` | struct | `quic/io/worker.rs` | Per-connection state machine (recv -> app -> send) |
+| `InboundPacketRouter` | struct | `quic/router/mod.rs` | Sole owner of socket recv; routes by DCID |
+| `ConnectionAcceptor` | struct | `quic/router/acceptor.rs` | Server RETRY + yields InitialQuicConnection |
+| `InitialQuicConnection` | struct | `quic/connection/mod.rs` | Pre-handshake handle; `.start(app)` spawns worker |
+| `QuicConnection` | struct | `quic/connection/mod.rs` | Post-handshake metadata handle (not the qconn itself) |
+| `ConnectionParams` | struct | `settings/mod.rs` | QuicSettings + TLS + Hooks + session |
+| `Config` | struct(crate) | `settings/config.rs` | Builds quiche::Config from ConnectionParams |
+| `BufFactory` | struct | `buf_factory.rs` | Handle to static tiered buffer pools |
+| `QuicheBuf` | struct | `buf_factory.rs` | Zero-copy splittable buffer (zero-copy feature) |
+| `Metrics` | trait | `metrics/mod.rs` | Pluggable telemetry; `DefaultMetrics` uses foundations |
+| `QuicCommand` | enum | `quic/connection/mod.rs` | ConnectionClose / Custom / Stats commands |
+| `BoxError` | type alias | `result.rs` | `Box<dyn Error + Send + Sync>` — deliberate choice, see docstring |
+
+## CONVENTIONS (crate-specific)
+
+- Re-exports: `pub extern crate quiche`, `pub use buffer_pool`, `pub use datagram_socket`.
+- `foundations` for logging (slog), not `log` directly. `capture_quiche_logs()` bridges quiche's `log` into slog.
+- `DriverHooks` is **sealed** — prevents external `H3Driver` variants.
+- `QuicAuditStats` (from `datagram-socket`) threaded through all connections via `Arc`.
+- Task spawning via `metrics::tokio_task::spawn()` / `spawn_with_killswitch()` — wraps `tokio::spawn` with optional schedule/poll histograms.
+- `ConnectionStage` FSM: `Handshake` -> `RunningApplication` -> `Close`.
+
+## ANTI-PATTERNS
+
+- `connection_not_present()` returns `TlsFail` in driver — misleading sentinel. Don't propagate.
+- `Error::Done` used as success signal in H3 driver write path. Don't replicate.
+- Don't add new `ApplicationOverQuic` methods without considering the worker loop order (recv -> reads -> writes -> send).
+- Don't block in `wait_for_data` — it's polled concurrently with packet recv and timers.
+
+## NOTES
+
+- Hardcodes `quiche/boringssl-boring-crate` + `quiche/qlog` in Cargo.toml deps.
+- Features: `zero-copy` implies `gcongestion`. `rpk` enables raw public keys via `boring/rpk`.
+- `--cfg capture_keylogs` (build flag, not feature) enables SSLKEYLOGFILE support.
+- `perf-quic-listener-metrics` adds handshake timing instrumentation.
+- `tokio-task-metrics` adds schedule/poll duration histograms per spawned task.
+- Linux-only: `libc`/`nix` deps for signal handling and socket options.
+- One client connection per socket — no multiplexing on client side.
diff --git a/tokio-quiche/src/http3/driver/AGENTS.md b/tokio-quiche/src/http3/driver/AGENTS.md
@@ -0,0 +1,47 @@
+# HTTP/3 Driver (`tokio-quiche/src/http3/driver/`)
+
+## OVERVIEW
+
+Async HTTP/3 driver bridging `quiche::h3::Connection` to Tokio tasks via channels. `H3Driver<H: DriverHooks>` is generic over sealed client/server hooks; users interact through `H3Controller` + typed event/command channels.
+
+## STRUCTURE
+
+| File | Role |
+|------|------|
+| `mod.rs` | `H3Driver`, `H3Controller`, `H3Event`, `H3Command`, `OutboundFrame`/`InboundFrame`, channel types, `ApplicationOverQuic` impl |
+| `hooks.rs` | `DriverHooks` trait (sealed). Defines `headers_received`, `conn_established`, `conn_command`, `wait_for_action` |
+| `client.rs` | `ClientHooks` impl, `ClientH3Driver`/`ClientH3Controller` aliases, `ClientH3Event`/`ClientH3Command` |
+| `server.rs` | `ServerHooks` impl, `ServerH3Driver`/`ServerH3Controller` aliases, `ServerH3Event`/`ServerH3Command` |
+| `streams.rs` | `StreamCtx`, `FlowCtx`, `WaitForStream` future, capacity/readiness signals |
+| `datagram.rs` | DATAGRAM/CONNECT-UDP flow handling |
+| `connection.rs` | `H3Conn` wrapper exposing `h3::Connection` operations |
+| `test_utils.rs` | `DriverTestHelper<H>` -- wraps `Pipe` + `H3Driver` for unit tests |
+| `tests.rs` | ~1500 lines of driver tests |
+
+## WHERE TO LOOK
+
+| Task | Start at |
+|------|----------|
+| Channel architecture | `mod.rs:332` (`H3Driver` struct fields: `h3_event_sender`, `cmd_recv`, `stream_map`, `waiting_streams`) |
+| `select!` loop / priority ordering | `mod.rs` `wait_for_data` impl -- uses `biased` select! |
+| Stream lifecycle | `cleanup_stream`, `shutdown_stream`, `process_h3_fin`, `process_h3_data` in `mod.rs` |
+| Per-stream backpressure | `streams.rs` -- `FuturesUnordered<WaitForStream>`, `WaitForDownstreamData`, `WaitForUpstreamCapacity` |
+| Adding endpoint-specific behavior | `hooks.rs` -- add method to `DriverHooks`, impl in `client.rs`/`server.rs` |
+| Writing tests | `test_utils.rs` for `DriverTestHelper`, `tests.rs` for examples |
+
+## ANTI-PATTERNS
+
+- **`connection_not_present()` returns `TlsFail`** -- misleading sentinel error. Do not propagate this pattern.
+- **`process_write_frame` uses `Error::Done` as success** -- non-obvious control flow, don't replicate elsewhere.
+- **`DriverHooks` is sealed** -- `mod hooks` is `pub(crate)`, trait has `#[allow(private_interfaces)]`. Do not expose.
+- **Stream cleanup is distributed** across 4+ functions (`cleanup_stream`, `shutdown_stream`, `process_h3_fin`, `process_h3_data`). Understand all paths before modifying.
+- **`STREAM_CAPACITY`** is 1 in test/debug, 16 in release. Tests exercise backpressure differently from prod.
+
+## NOTES
+
+- `H3Driver::new()` returns `(H3Driver<H>, H3Controller<H>)` -- paired at construction, connected by unbounded mpsc channels.
+- Per-stream channels are bounded (`STREAM_CAPACITY`); per-connection event/cmd channels are unbounded.
+- Datagram flows use a shared `FLOW_CAPACITY=2048` bounded channel, separate from stream channels.
+- `H3Event` variants: `IncomingSettings`, `IncomingHeaders`, `NewFlow`, `ResetStream`, `ConnectionError`, `ConnectionShutdown`, `BodyBytesReceived`, `StreamClosed`.
+- `H3Command` variants: `QuicCmd`, `GoAway`, `ShutdownStream`.
+- Type aliases (`ClientH3Driver`, `ServerH3Driver`, etc.) are the public API; `H3Driver<H>` and `DriverHooks` are internal.
diff --git a/tokio-quiche/src/quic/AGENTS.md b/tokio-quiche/src/quic/AGENTS.md
@@ -0,0 +1,65 @@
+# tokio-quiche/src/quic/
+
+## OVERVIEW
+
+Async QUIC connection management. Splits socket into recv-half (one `InboundPacketRouter` task) and send-half (shared by many `IoWorker` tasks). Entrypoints: `connect()`/`connect_with_config()` for clients, `start_listener()` for servers. `raw` submodule bypasses the router for manual packet injection.
+
+## STRUCTURE
+
+```
+mod.rs                        # Entrypoints: connect, connect_with_config, start_listener
+raw.rs                        # wrap_quiche_conn(): bypass router, manual packet feed
+hooks.rs                      # ConnectionHook trait (custom SslContextBuilder)
+addr_validation_token.rs      # RETRY token generation/validation for server
+
+connection/
+  mod.rs                      # InitialQuicConnection, QuicConnection, ApplicationOverQuic trait
+  error.rs                    # HandshakeError enum, make_handshake_result()
+  id.rs                       # ConnectionIdGenerator trait, SimpleConnectionIdGenerator
+  map.rs                      # ConnectionMap: BTreeMap<CidOwned, mpsc::Sender<Incoming>>
+
+io/
+  connection_stage.rs         # ConnectionStage trait + stages: Handshake, RunningApplication, Close
+  worker.rs                   # IoWorker<Tx,M,S>: per-connection recv→process→send loop
+  gso.rs                      # GSO/GRO send_to(), UDP_MAX_GSO_PACKET_SIZE
+  utilization_estimator.rs    # BandwidthReporter for max bandwidth/loss tracking
+
+router/
+  mod.rs                      # InboundPacketRouter: Future, demux by DCID, ConnectionMapCommand
+  acceptor.rs                 # ConnectionAcceptor: server-side InitialPacketHandler (RETRY flow)
+  connector.rs                # ClientConnector: client-side InitialPacketHandler (handshake FSM)
+```
+
+## WHERE TO LOOK
+
+| Task | File | Symbol/Line |
+|------|------|-------------|
+| Add lifecycle callback | `connection/mod.rs` | `ApplicationOverQuic` trait (~:663) |
+| Connection state machine | `io/connection_stage.rs` | `ConnectionStage` trait, `Handshake`/`RunningApplication`/`Close` |
+| Worker main loop | `io/worker.rs` | `IoWorker::work_loop()` (~:216) |
+| Packet routing/demux | `router/mod.rs` | `InboundPacketRouter::on_incoming()` (~:229) |
+| CID management | `io/worker.rs` | `fill_available_scids()`, `refresh_connection_ids()` |
+| Server accept flow | `router/acceptor.rs` | `ConnectionAcceptor::handle_initials()` |
+| Client connect flow | `router/connector.rs` | `ClientConnector::on_incoming()` |
+| Connection spawn path | `connection/mod.rs` | `InitialQuicConnection::start()` / `handshake()` / `resume()` |
+| CID-to-connection map | `connection/map.rs` | `ConnectionMap` (optimized `CidOwned` for v1 CIDs) |
+| Raw/manual connections | `raw.rs` | `wrap_quiche_conn()`, `ConnCloseReceiver` |
+
+## ANTI-PATTERNS
+
+- **`InitialQuicConnection` is `#[must_use]`** -- dropping silently discards connection. Always call `.start()`, `.handshake()`, or `.handshake_fut()`.
+- **`handshake()` spawns with `AbortOnDropHandle`** -- dropping the future kills the handshake task. Hold the handle.
+- **`fill_available_scids` sends `ConnectionMapCommand::MapCid` to router** -- silently fails if router channel dropped. Don't assume CID registration succeeded.
+- **`transmute` of `Instant` in `gso.rs`** -- fragile platform-dependent hack. Do not extend or replicate.
+- **One client connection per socket** -- `connect()` docs explicitly warn. Sharing socket loses packets.
+- **`#[cfg(feature = "zero-copy")]` gates `QuicheConnection` type alias** -- `quiche::Connection<BufFactory>` vs `quiche::Connection`. Check both paths when modifying connection creation.
+- **`wait_for_quiche` returns `TlsFail` on gather error** -- misleading sentinel error, don't propagate this pattern.
+
+## NOTES
+
+- `IoWorker` is generic: `IoWorker<Tx, M, S: ConnectionStage>`. Stage transitions consume the worker via `From<IoWorker<..>> for IoWorkerParams<..>` and construct a new `IoWorker` with the next stage.
+- `select!` in `work_loop` is **biased** -- timeout arm must stay first to prevent starvation.
+- `ConnectionMap` uses `CidOwned::Optimized([u64; 3])` for v1 CIDs (<=20 bytes) to avoid heap allocation on lookup.
+- `InboundPacketRouter` implements `Future` directly (not async fn) -- polled as a spawned task.
+- `short_dcid()` fast-path extracts DCID from short header packets without full `Header::from_slice`.
+- Router tests are `#[cfg(all(test, unix))]` in `router/mod.rs` -- not Windows-compatible.
PATCH

echo "Gold patch applied."
