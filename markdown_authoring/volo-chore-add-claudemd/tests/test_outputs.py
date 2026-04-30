"""Behavioral checks for volo-chore-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/volo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '[Volo](https://github.com/cloudwego/volo) is a high-performance Rust RPC framework by CloudWeGo (ByteDance). It supports Thrift, gRPC, and HTTP protocols with fully async design (Tokio), zero-copy opt' in text, "expected to find: " + '[Volo](https://github.com/cloudwego/volo) is a high-performance Rust RPC framework by CloudWeGo (ByteDance). It supports Thrift, gRPC, and HTTP protocols with fully async design (Tokio), zero-copy opt'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **volo**: Core abstractions -- service discovery (`Discover`), load balancing (`LoadBalance`), network transport (`Address`, `Conn`, TCP/Unix/TLS/ShmIPC), context (`RpcCx`, `RpcInfo`, `Endpoint`), h' in text, "expected to find: " + '- **volo**: Core abstractions -- service discovery (`Discover`), load balancing (`LoadBalance`), network transport (`Address`, `Conn`, TCP/Unix/TLS/ShmIPC), context (`RpcCx`, `RpcInfo`, `Endpoint`), h'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(volo-thrift): add multi-service support`, `fix(volo-http): resolve connection pool leak`, `chore: update dependencies`' in text, "expected to find: " + 'Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(volo-thrift): add multi-service support`, `fix(volo-http): resolve connection pool leak`, `chore: update dependencies`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-build/CLAUDE.md')
    assert 'Key methods: `add_service(path)`, `out_dir(path)`, `filename(name)`, `plugin(p)`, `ignore_unused(bool)`, `touch(items)`, `keep_unknown_fields(paths)`, `split_generated_files(bool)`, `special_namings(n' in text, "expected to find: " + 'Key methods: `add_service(path)`, `out_dir(path)`, `filename(name)`, `plugin(p)`, `ignore_unused(bool)`, `touch(items)`, `keep_unknown_fields(paths)`, `split_generated_files(bool)`, `special_namings(n'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-build/CLAUDE.md')
    assert 'Implements `pilota_build::CodegenBackend` for Thrift services. Generates: `{ServiceName}Server`, `{ServiceName}Client`, `{ServiceName}GenericClient`, `{ServiceName}OneShotClient`, `{ServiceName}Client' in text, "expected to find: " + 'Implements `pilota_build::CodegenBackend` for Thrift services. Generates: `{ServiceName}Server`, `{ServiceName}Client`, `{ServiceName}GenericClient`, `{ServiceName}OneShotClient`, `{ServiceName}Client'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-build/CLAUDE.md')
    assert 'Implements `pilota_build::CodegenBackend` for gRPC services. Generates the same type pattern as Thrift (`Server`, `Client`, `GenericClient`, `OneShotClient`, `ClientBuilder`, `RequestSend/Recv`, `Resp' in text, "expected to find: " + 'Implements `pilota_build::CodegenBackend` for gRPC services. Generates the same type pattern as Thrift (`Server`, `Client`, `GenericClient`, `OneShotClient`, `ClientBuilder`, `RequestSend/Recv`, `Resp'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-cli/CLAUDE.md')
    assert 'Batch-defines subcommand enums and auto-implements the `CliCommand` trait, simplifying command dispatch logic. All commands implement the `CliCommand` trait (`fn run(&self, cx: Context) -> anyhow::Res' in text, "expected to find: " + 'Batch-defines subcommand enums and auto-implements the `CliCommand` trait, simplifying command dispatch logic. All commands implement the `CliCommand` trait (`fn run(&self, cx: Context) -> anyhow::Res'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-cli/CLAUDE.md')
    assert '`volo-cli` is the command line tool for the Volo framework, used for creating and managing Volo-based RPC and HTTP service projects from IDL files or templates.' in text, "expected to find: " + '`volo-cli` is the command line tool for the Volo framework, used for creating and managing Volo-based RPC and HTTP service projects from IDL files or templates.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-cli/CLAUDE.md')
    assert '- **Thrift** (`templates/thrift/`): Standard Thrift RPC project with `volo-gen` sub-crate for code generation' in text, "expected to find: " + '- **Thrift** (`templates/thrift/`): Standard Thrift RPC project with `volo-gen` sub-crate for code generation'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-grpc/CLAUDE.md')
    assert '`volo-grpc` is the gRPC implementation of the Volo framework, providing async gRPC client and server based on HTTP/2 (hyper). Supports unary, client streaming, server streaming, and bidirectional stre' in text, "expected to find: " + '`volo-grpc` is the gRPC implementation of the Volo framework, providing async gRPC client and server based on HTTP/2 (hyper). Supports unary, client streaming, server streaming, and bidirectional stre'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-grpc/CLAUDE.md')
    assert '**Server** -- Built on hyper HTTP/2. Methods: `add_service`, `layer`/`layer_front`/`layer_tower`, `run`/`run_with_shutdown`, `tls_config`, plus HTTP/2 tuning options.' in text, "expected to find: " + '**Server** -- Built on hyper HTTP/2. Methods: `add_service`, `layer`/`layer_front`/`layer_tower`, `run`/`run_with_shutdown`, `tls_config`, plus HTTP/2 tuning options.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-grpc/CLAUDE.md')
    assert '**Client** -- `ClientBuilder` configures: `rpc_timeout`, `connect_timeout`, `discover`, `load_balance`, `layer`/`layer_front`, `compression`.' in text, "expected to find: " + '**Client** -- `ClientBuilder` configures: `rpc_timeout`, `connect_timeout`, `discover`, `load_balance`, `layer`/`layer_front`, `compression`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-http/CLAUDE.md')
    assert '**Handlers**: Async functions with extractors as parameters. Extractors implement `FromContext` (non-consuming, from context/parts) or `FromRequest` (consuming, includes body -- must be last parameter' in text, "expected to find: " + '**Handlers**: Async functions with extractors as parameters. Extractors implement `FromContext` (non-consuming, from context/parts) or `FromRequest` (consuming, includes body -- must be last parameter'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-http/CLAUDE.md')
    assert '`ClientBuilder` configures and builds a `Client` with connection pooling, timeouts, and DNS resolution. `RequestBuilder` (via `client.get()`, `.post()`, etc.) builds individual requests with headers, ' in text, "expected to find: " + '`ClientBuilder` configures and builds a `Client` with connection pooling, timeouts, and DNS resolution. `RequestBuilder` (via `client.get()`, `.post()`, etc.) builds individual requests with headers, '[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-http/CLAUDE.md')
    assert '`Body` wraps `Full<Bytes>`, `Incoming`, `Stream`, or `BoxBody`. The `BodyConversion` trait provides `into_bytes()`, `into_vec()`, `into_string()`, `into_faststr()`, and `into_json<T>()`.' in text, "expected to find: " + '`Body` wraps `Full<Bytes>`, `Incoming`, `Stream`, or `BoxBody`. The `BodyConversion` trait provides `into_bytes()`, `into_vec()`, `into_string()`, `into_faststr()`, and `into_json<T>()`.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-macros/CLAUDE.md')
    assert '`volo-macros` is a **reserved placeholder** crate for future procedural macros. It contains no active functionality.' in text, "expected to find: " + '`volo-macros` is a **reserved placeholder** crate for future procedural macros. It contains no active functionality.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-macros/CLAUDE.md')
    assert '`volo-macros` must be published **first** when releasing new versions (see root CLAUDE.md).' in text, "expected to find: " + '`volo-macros` must be published **first** when releasing new versions (see root CLAUDE.md).'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-macros/CLAUDE.md')
    assert '- Declarative macros (`volo_unreachable!`, `new_type!`): defined in `volo/src/macros.rs`' in text, "expected to find: " + '- Declarative macros (`volo_unreachable!`, `new_type!`): defined in `volo/src/macros.rs`'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-thrift/CLAUDE.md')
    assert '`volo-thrift` is the Thrift RPC implementation of the Volo project, providing high-performance async Thrift client and server. Core features include TTHeader protocol (CloudWeGo proprietary for Volo/K' in text, "expected to find: " + '`volo-thrift` is the Thrift RPC implementation of the Volo project, providing high-performance async Thrift client and server. Core features include TTHeader protocol (CloudWeGo proprietary for Volo/K'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-thrift/CLAUDE.md')
    assert '`Router` enables multi-service hosting on a single server. Routing uses the `isn` (IDL Service Name) field in TTHeader. Services implement `NamedService` (provides `const NAME`) for routing support. T' in text, "expected to find: " + '`Router` enables multi-service hosting on a single server. Routing uses the `isn` (IDL Service Name) field in TTHeader. Services implement `NamedService` (provides `const NAME`) for routing support. T'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('volo-thrift/CLAUDE.md')
    assert '`ClientContext` / `ServerContext` contain `RpcInfo` (caller, callee, method, config), `seq_id`, `message_type`, `stats`, `transport` info, and `idl_service_name` for routing. `Config` holds timeout se' in text, "expected to find: " + '`ClientContext` / `ServerContext` contain `RpcInfo` (caller, callee, method, config), `seq_id`, `message_type`, `stats`, `transport` info, and `idl_service_name` for routing. `Config` holds timeout se'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('volo/CLAUDE.md')
    assert 'Zero-downtime restarts via Unix Domain Socket. Parent passes listening socket FDs to child process via `SCM_RIGHTS`, then child signals parent to terminate. Global instance: `DEFAULT_HOT_RESTART`.' in text, "expected to find: " + 'Zero-downtime restarts via Unix Domain Socket. Parent passes listening socket FDs to child process via `SCM_RIGHTS`, then child signals parent to terminate. Global instance: `DEFAULT_HOT_RESTART`.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('volo/CLAUDE.md')
    assert '`volo` is the core foundation library providing shared abstractions (service discovery, load balancing, network transport, context management) used by `volo-thrift`, `volo-grpc`, and `volo-http`.' in text, "expected to find: " + '`volo` is the core foundation library providing shared abstractions (service discovery, load balancing, network transport, context management) used by `volo-thrift`, `volo-grpc`, and `volo-http`.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('volo/CLAUDE.md')
    assert 'Unified transport abstraction. `Address` enum supports TCP (`Ip`), Unix sockets (`Unix`), and shared memory (`Shmipc`). `ConnStream` enum wraps all connection types.' in text, "expected to find: " + 'Unified transport abstraction. `Address` enum supports TCP (`Ip`), Unix sockets (`Unix`), and shared memory (`Shmipc`). `ConnStream` enum wraps all connection types.'[:80]

