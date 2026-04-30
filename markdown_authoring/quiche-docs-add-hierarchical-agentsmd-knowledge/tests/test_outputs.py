"""Behavioral checks for quiche-docs-add-hierarchical-agentsmd-knowledge (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/quiche")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "Cloudflare's QUIC and HTTP/3 implementation in Rust. Workspace of 11 crates: core `quiche` protocol library, `tokio-quiche` async integration, CLI tools (`apps`, `h3i`), logging/analysis (`qlog`, `qlo" in text, "expected to find: " + "Cloudflare's QUIC and HTTP/3 implementation in Rust. Workspace of 11 crates: core `quiche` protocol library, `tokio-quiche` async integration, CLI tools (`apps`, `h3i`), logging/analysis (`qlog`, `qlo"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Do not use `any` types or type assertions** -- this is Rust; no equivalent concern, but `unsafe` is restricted to FFI boundaries (`tls/`, `crypto/`, `ffi.rs`, `gso.rs`).' in text, "expected to find: " + '- **Do not use `any` types or type assertions** -- this is Rust; no equivalent concern, but `unsafe` is restricted to FFI boundaries (`tls/`, `crypto/`, `ffi.rs`, `gso.rs`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Cognitive complexity lint disabled** (`clippy.toml: 100`) -- complex functions accepted for protocol code, but don't add new ones casually." in text, "expected to find: " + "- **Cognitive complexity lint disabled** (`clippy.toml: 100`) -- complex functions accepted for protocol code, but don't add new ones casually."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('h3i/AGENTS.md')
    assert 'Low-level HTTP/3 testing client. Sends arbitrary/malformed H3 frames to probe server RFC compliance. Both library (`lib.rs`) and CLI binary (`main.rs`). Used programmatically as test driver in tokio-q' in text, "expected to find: " + 'Low-level HTTP/3 testing client. Sends arbitrary/malformed H3 frames to probe server RFC compliance. Both library (`lib.rs`) and CLI binary (`main.rs`). Used programmatically as test driver in tokio-q'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('h3i/AGENTS.md')
    assert '- **ConnectionSummary**: returned from both sync/async `connect()`. Contains per-stream frame maps, QUIC stats, path stats, close reason. Custom `Serialize` impl truncates binary at 16KB.' in text, "expected to find: " + '- **ConnectionSummary**: returned from both sync/async `connect()`. Contains per-stream frame maps, QUIC stats, path stats, close reason. Custom `Serialize` impl truncates binary at 16KB.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('h3i/AGENTS.md')
    assert '- **Action execution**: `client/mod.rs::execute_action()` matches on `Action` variants, writes directly to `quiche::Connection` streams -- no H3 connection layer.' in text, "expected to find: " + '- **Action execution**: `client/mod.rs::execute_action()` matches on `Action` variants, writes directly to `quiche::Connection` streams -- no H3 connection layer.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('qlog-dancer/AGENTS.md')
    assert 'Visualization/analysis tool for qlog and Chrome netlog files. Parses logs into a `Datastore`, extracts time-series into `SeriesStore`, renders PNG charts (native) or canvas plots (wasm). Outputs HTML/' in text, "expected to find: " + 'Visualization/analysis tool for qlog and Chrome netlog files. Parses logs into a `Datastore`, extracts time-series into `SeriesStore`, renders PNG charts (native) or canvas plots (wasm). Outputs HTML/'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('qlog-dancer/AGENTS.md')
    assert 'Dual-target: native CLI binary (`main.rs`) + wasm-bindgen web UI (`web.rs`, `#[cfg(target_arch = "wasm32")]`). `crate-type = ["lib", "cdylib"]` -- cdylib is for wasm.' in text, "expected to find: " + 'Dual-target: native CLI binary (`main.rs`) + wasm-bindgen web UI (`web.rs`, `#[cfg(target_arch = "wasm32")]`). `crate-type = ["lib", "cdylib"]` -- cdylib is for wasm.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('qlog-dancer/AGENTS.md')
    assert '- Native build requires system libs: **libexpat, freetype, fontconfig** (plotters SVG/bitmap backends).' in text, "expected to find: " + '- Native build requires system libs: **libexpat, freetype, fontconfig** (plotters SVG/bitmap backends).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('qlog/AGENTS.md')
    assert 'qlog data model for QUIC and HTTP/3 per IETF drafts (`draft-ietf-quic-qlog-main-schema`, `draft-ietf-quic-qlog-quic-events`, `draft-ietf-quic-qlog-h3-events`). Pure data types + serde serialization; n' in text, "expected to find: " + 'qlog data model for QUIC and HTTP/3 per IETF drafts (`draft-ietf-quic-qlog-main-schema`, `draft-ietf-quic-qlog-quic-events`, `draft-ietf-quic-qlog-h3-events`). Pure data types + serde serialization; n'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('qlog/AGENTS.md')
    assert '| Add new event variant | `events/mod.rs` `EventData` enum | Add to relevant `events/*.rs`, wire into `EventData` |' in text, "expected to find: " + '| Add new event variant | `events/mod.rs` `EventData` enum | Add to relevant `events/*.rs`, wire into `EventData` |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('qlog/AGENTS.md')
    assert '- Deps: `serde`, `serde_json` (preserve_order), `serde_with`, `smallvec`. No async, no IO beyond `Write`/`BufRead`.' in text, "expected to find: " + '- Deps: `serde`, `serde_json` (preserve_order), `serde_with`, `smallvec`. No async, no IO beyond `Write`/`BufRead`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/AGENTS.md')
    assert 'Low-level QUIC transport and HTTP/3 in Rust. App provides IO/timers; this crate handles protocol state. Also exposes C FFI via `staticlib`/`cdylib`.' in text, "expected to find: " + 'Low-level QUIC transport and HTTP/3 in Rust. App provides IO/timers; this crate handles protocol state. Also exposes C FFI via `staticlib`/`cdylib`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/AGENTS.md')
    assert '- Three TLS backends: `boringssl-vendored` (default), `boringssl-boring-crate`, `openssl` — mutually exclusive features.' in text, "expected to find: " + '- Three TLS backends: `boringssl-vendored` (default), `boringssl-boring-crate`, `openssl` — mutually exclusive features.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/AGENTS.md')
    assert "- **Don't add new CC impls** outside `recovery/` — two parallel impls (congestion + gcongestion) already exist." in text, "expected to find: " + "- **Don't add new CC impls** outside `recovery/` — two parallel impls (congestion + gcongestion) already exist."[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/src/h3/AGENTS.md')
    assert 'HTTP/3 wire protocol over QUIC. `Connection` manages H3 state (streams, QPACK, SETTINGS, GOAWAY) on top of `quiche::Connection<F>`. Event-driven: caller loops `poll()` → `Event`. Own `Error`/`Result` ' in text, "expected to find: " + 'HTTP/3 wire protocol over QUIC. `Connection` manages H3 state (streams, QPACK, SETTINGS, GOAWAY) on top of `quiche::Connection<F>`. Event-driven: caller loops `poll()` → `Event`. Own `Error`/`Result` '[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/src/h3/AGENTS.md')
    assert '- **`send_request()` sends empty `b""` to create QUIC stream** before writing headers. Required because QUIC stream doesn\'t exist until first write.' in text, "expected to find: " + '- **`send_request()` sends empty `b""` to create QUIC stream** before writing headers. Required because QUIC stream doesn\'t exist until first write.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/src/h3/AGENTS.md')
    assert "- **h3::Error != quiche::Error.** 19 variants; `TransportError(quiche::Error)` wraps transport errors. Don't confuse." in text, "expected to find: " + "- **h3::Error != quiche::Error.** 19 variants; `TransportError(quiche::Error)` wraps transport errors. Don't confuse."[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/src/recovery/AGENTS.md')
    assert '- `CongestionControlAlgorithm` values: Reno=0, CUBIC=1, Bbr2Gcongestion=4. Gap is intentional (removed variants).' in text, "expected to find: " + '- `CongestionControlAlgorithm` values: Reno=0, CUBIC=1, Bbr2Gcongestion=4. Gap is intentional (removed variants).'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/src/recovery/AGENTS.md')
    assert '- `Recovery::new_with_config` tries `GRecovery::new` first; falls back to `LegacyRecovery` if algo is Reno/CUBIC.' in text, "expected to find: " + '- `Recovery::new_with_config` tries `GRecovery::new` first; falls back to `LegacyRecovery` if algo is Reno/CUBIC.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('quiche/src/recovery/AGENTS.md')
    assert '| Add/change CC algorithm | `congestion/mod.rs` or `gcongestion/mod.rs` | Different dispatch patterns |' in text, "expected to find: " + '| Add/change CC algorithm | `congestion/mod.rs` or `gcongestion/mod.rs` | Different dispatch patterns |'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/AGENTS.md')
    assert 'Async tokio wrapper for `quiche`. Spawns per-connection IO worker tasks driven by an `ApplicationOverQuic` trait. Ships a ready-made `H3Driver` for HTTP/3. Uses `foundations` for structured logging (s' in text, "expected to find: " + 'Async tokio wrapper for `quiche`. Spawns per-connection IO worker tasks driven by an `ApplicationOverQuic` trait. Ships a ready-made `H3Driver` for HTTP/3. Uses `foundations` for structured logging (s'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/AGENTS.md')
    assert '- Task spawning via `metrics::tokio_task::spawn()` / `spawn_with_killswitch()` — wraps `tokio::spawn` with optional schedule/poll histograms.' in text, "expected to find: " + '- Task spawning via `metrics::tokio_task::spawn()` / `spawn_with_killswitch()` — wraps `tokio::spawn` with optional schedule/poll histograms.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/AGENTS.md')
    assert '| `ApplicationOverQuic` | trait | `quic/connection/mod.rs` | Extension point: on_conn_established, process_reads/writes, wait_for_data |' in text, "expected to find: " + '| `ApplicationOverQuic` | trait | `quic/connection/mod.rs` | Extension point: on_conn_established, process_reads/writes, wait_for_data |'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/src/http3/driver/AGENTS.md')
    assert 'Async HTTP/3 driver bridging `quiche::h3::Connection` to Tokio tasks via channels. `H3Driver<H: DriverHooks>` is generic over sealed client/server hooks; users interact through `H3Controller` + typed ' in text, "expected to find: " + 'Async HTTP/3 driver bridging `quiche::h3::Connection` to Tokio tasks via channels. `H3Driver<H: DriverHooks>` is generic over sealed client/server hooks; users interact through `H3Controller` + typed '[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/src/http3/driver/AGENTS.md')
    assert '- **Stream cleanup is distributed** across 4+ functions (`cleanup_stream`, `shutdown_stream`, `process_h3_fin`, `process_h3_data`). Understand all paths before modifying.' in text, "expected to find: " + '- **Stream cleanup is distributed** across 4+ functions (`cleanup_stream`, `shutdown_stream`, `process_h3_fin`, `process_h3_data`). Understand all paths before modifying.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/src/http3/driver/AGENTS.md')
    assert '- `H3Event` variants: `IncomingSettings`, `IncomingHeaders`, `NewFlow`, `ResetStream`, `ConnectionError`, `ConnectionShutdown`, `BodyBytesReceived`, `StreamClosed`.' in text, "expected to find: " + '- `H3Event` variants: `IncomingSettings`, `IncomingHeaders`, `NewFlow`, `ResetStream`, `ConnectionError`, `ConnectionShutdown`, `BodyBytesReceived`, `StreamClosed`.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/src/quic/AGENTS.md')
    assert 'Async QUIC connection management. Splits socket into recv-half (one `InboundPacketRouter` task) and send-half (shared by many `IoWorker` tasks). Entrypoints: `connect()`/`connect_with_config()` for cl' in text, "expected to find: " + 'Async QUIC connection management. Splits socket into recv-half (one `InboundPacketRouter` task) and send-half (shared by many `IoWorker` tasks). Entrypoints: `connect()`/`connect_with_config()` for cl'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/src/quic/AGENTS.md')
    assert '- `IoWorker` is generic: `IoWorker<Tx, M, S: ConnectionStage>`. Stage transitions consume the worker via `From<IoWorker<..>> for IoWorkerParams<..>` and construct a new `IoWorker` with the next stage.' in text, "expected to find: " + '- `IoWorker` is generic: `IoWorker<Tx, M, S: ConnectionStage>`. Stage transitions consume the worker via `From<IoWorker<..>> for IoWorkerParams<..>` and construct a new `IoWorker` with the next stage.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('tokio-quiche/src/quic/AGENTS.md')
    assert '- **`#[cfg(feature = "zero-copy")]` gates `QuicheConnection` type alias** -- `quiche::Connection<BufFactory>` vs `quiche::Connection`. Check both paths when modifying connection creation.' in text, "expected to find: " + '- **`#[cfg(feature = "zero-copy")]` gates `QuicheConnection` type alias** -- `quiche::Connection<BufFactory>` vs `quiche::Connection`. Check both paths when modifying connection creation.'[:80]

