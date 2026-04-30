#!/usr/bin/env bash
set -euo pipefail

cd /workspace/volo

# Idempotency guard
if grep -qF "[Volo](https://github.com/cloudwego/volo) is a high-performance Rust RPC framewo" "CLAUDE.md" && grep -qF "Key methods: `add_service(path)`, `out_dir(path)`, `filename(name)`, `plugin(p)`" "volo-build/CLAUDE.md" && grep -qF "Batch-defines subcommand enums and auto-implements the `CliCommand` trait, simpl" "volo-cli/CLAUDE.md" && grep -qF "`volo-grpc` is the gRPC implementation of the Volo framework, providing async gR" "volo-grpc/CLAUDE.md" && grep -qF "**Handlers**: Async functions with extractors as parameters. Extractors implemen" "volo-http/CLAUDE.md" && grep -qF "`volo-macros` is a **reserved placeholder** crate for future procedural macros. " "volo-macros/CLAUDE.md" && grep -qF "`volo-thrift` is the Thrift RPC implementation of the Volo project, providing hi" "volo-thrift/CLAUDE.md" && grep -qF "Zero-downtime restarts via Unix Domain Socket. Parent passes listening socket FD" "volo/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,102 @@
+# CLAUDE.md - Volo Workspace
+
+For detailed per-crate documentation, see the CLAUDE.md in each sub-crate directory.
+
+## Project Overview
+
+[Volo](https://github.com/cloudwego/volo) is a high-performance Rust RPC framework by CloudWeGo (ByteDance). It supports Thrift, gRPC, and HTTP protocols with fully async design (Tokio), zero-copy optimizations, and middleware via Service/Layer abstractions (motore).
+
+- Rust Edition: 2024
+- MSRV: 1.85.0
+- Current Version: 0.12.x
+
+## Workspace Structure
+
+```
+volo/
+├── volo/                   # Core library
+├── volo-build/             # Code generation from IDL (Thrift/Protobuf)
+├── volo-cli/               # CLI tool (project scaffolding)
+├── volo-grpc/              # gRPC implementation
+├── volo-http/              # HTTP implementation
+├── volo-macros/            # Procedural macros (reserved)
+├── volo-thrift/            # Thrift implementation
+├── examples/               # Example code
+├── benchmark/              # Performance benchmarks
+└── tests/code-generation/  # Code generation tests
+```
+
+## Crate Dependency Graph
+
+```
+                     volo-macros (reserved)
+                          |
+                          v
+    +------------------  volo  ------------------+
+    |                     |                       |
+    v                     v                       v
+volo-thrift           volo-grpc              volo-http
+    |                     |                       |
+    +----------+----------+                       |
+               v                                  |
+          volo-build <----------------------------+
+               |
+               v
+           volo-cli
+```
+
+## Crate Overview
+
+- **volo**: Core abstractions -- service discovery (`Discover`), load balancing (`LoadBalance`), network transport (`Address`, `Conn`, TCP/Unix/TLS/ShmIPC), context (`RpcCx`, `RpcInfo`, `Endpoint`), hot restart, panic capture
+- **volo-thrift**: TTHeader/Framed transport, Binary/Compact protocols, Ping-Pong/Multiplex modes, connection pooling, ISN-based multi-service routing, BizError
+- **volo-grpc**: HTTP/2 (hyper), unary/streaming calls, compression (gzip/zlib/zstd), gRPC-Web, metadata
+- **volo-http**: Server (Router/Handler/Extractor), Client (connection pooling/DNS/proxy), JSON/Form/Multipart/WebSocket/SSE, TLS (Rustls/Native-TLS)
+- **volo-build**: Generates Rust code from Thrift/Protobuf IDL. Config: `volo.yml` / `volo.workspace.yml`
+- **volo-cli**: `volo init`, `volo http init`, `volo idl add`, `volo repo add/update`, `volo migrate`
+- **volo-macros**: Reserved. Active macros: `#[service]` (from motore), `volo_unreachable!`, `new_type!` (from volo)
+
+## Feature Flags Summary
+
+| Feature       | volo | volo-thrift | volo-grpc  | volo-http  |
+| ------------- | ---- | ----------- | ---------- | ---------- |
+| `rustls`      | Y    | -           | Y          | Y          |
+| `native-tls`  | Y    | -           | Y          | Y          |
+| `shmipc`      | Y    | Y           | -          | -          |
+| `multiplex`   | -    | Y           | -          | -          |
+| `gzip`/`zlib` | -    | -           | Y(default) | -          |
+| `zstd`        | -    | -           | Y          | -          |
+| `grpc-web`    | -    | -           | Y          | -          |
+| `json`        | -    | -           | -          | Y(default) |
+| `ws`          | -    | -           | -          | Y          |
+| `cookie`      | -    | -           | -          | Y          |
+
+## Core Abstractions
+
+All built on the `motore` crate's `Service<Cx, Request>` and `Layer<S>` traits.
+
+- **Service Discovery**: `Discover` trait (volo) -- `StaticDiscover`, `WeightedStaticDiscover`
+- **Load Balancing**: `LoadBalance` trait (volo) -- weighted random, consistent hashing
+
+## Design Patterns
+
+- **Builder**: `XxxBuilder::new().xxx().build()`
+- **Make**: `MakeXxx` trait creates `Xxx` instances
+- **Layer**: `XxxLayer` implements `motore::layer::Layer`
+- **Service**: Implements `motore::service::Service`
+- **Private features**: Prefixed with `__` (e.g., `__tls`)
+
+## Commit Conventions
+
+Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat(volo-thrift): add multi-service support`, `fix(volo-http): resolve connection pool leak`, `chore: update dependencies`
+
+## Release Order
+
+Publish in this order:
+
+1. `volo-macros`
+2. `volo`
+3. `volo-build`
+4. `volo-cli`
+5. `volo-thrift`
+6. `volo-grpc`
+7. `volo-http` (released independently)
diff --git a/volo-build/CLAUDE.md b/volo-build/CLAUDE.md
@@ -0,0 +1,78 @@
+# CLAUDE.md - volo-build
+
+## Overview
+
+`volo-build` is the code generation tool for the Volo framework, compiling Thrift and Protobuf IDL files into Rust code at build time. It is the underlying dependency of `volo-cli` and is typically used in `build.rs`.
+
+## Directory Structure
+
+```
+volo-build/src/
+├── lib.rs              # Library entry, defines Builder and public exports
+├── model.rs            # Configuration model (SingleConfig, Entry, Service, Idl, etc.)
+├── config_builder.rs   # ConfigBuilder and InitBuilder
+├── thrift_backend.rs   # Thrift code generation backend
+├── grpc_backend.rs     # gRPC/Protobuf code generation backend
+├── util.rs             # Git operations, file operations, config read/write
+├── workspace.rs        # Workspace mode support
+└── legacy/             # Legacy configuration format compatibility
+```
+
+## Builder (`lib.rs`)
+
+Main code generation builder supporting both Thrift and Protobuf protocols. Created via `Builder::thrift()` or `Builder::protobuf()`.
+
+Key methods: `add_service(path)`, `out_dir(path)`, `filename(name)`, `plugin(p)`, `ignore_unused(bool)`, `touch(items)`, `keep_unknown_fields(paths)`, `split_generated_files(bool)`, `special_namings(namings)`, `dedup(list)`, `common_crate_name(name)`, `with_descriptor(bool)`, `with_field_mask(bool)`, `with_comments(bool)`, `include_dirs(dirs)`, `write()`, `init_service()`.
+
+## ConfigBuilder (`config_builder.rs`)
+
+Configuration file-based (`volo.yml`) code generation builder. Use `ConfigBuilder::default().write()` for the default config file, or `ConfigBuilder::new(path)` for a custom one. Supports adding plugins via `.plugin(p)`.
+
+Also provides `InitBuilder` for initializing new services.
+
+## Configuration Model (`model.rs`)
+
+`SingleConfig` is the root structure. Key types: `Entry` (code generation entry), `Service` (service definition with IDL and codegen options), `Idl` (IDL file source and path), `Source` (Local or Git), `Repo` (Git repository config), `CodegenOption`, `CommonOption`.
+
+Example `volo.yml`:
+
+```yaml
+entries:
+  default:
+    filename: volo_gen.rs
+    protocol: thrift
+    repos:
+      my_repo:
+        url: https://github.com/example/idl.git
+        ref: main
+        lock: abc123
+    services:
+      - idl:
+          source: local
+          path: ./idl/service.thrift
+        codegen_option:
+          touch: ["MyService"]
+    touch_all: false
+    dedups: []
+    special_namings: []
+    split_generated_files: false
+```
+
+## Thrift Backend (`thrift_backend.rs`)
+
+Implements `pilota_build::CodegenBackend` for Thrift services. Generates: `{ServiceName}Server`, `{ServiceName}Client`, `{ServiceName}GenericClient`, `{ServiceName}OneShotClient`, `{ServiceName}ClientBuilder`, `{ServiceName}RequestSend/Recv`, `{ServiceName}ResponseSend/Recv`. Supports exception handling, oneway methods, multi-service routing, and split file generation.
+
+## gRPC Backend (`grpc_backend.rs`)
+
+Implements `pilota_build::CodegenBackend` for gRPC services. Generates the same type pattern as Thrift (`Server`, `Client`, `GenericClient`, `OneShotClient`, `ClientBuilder`, `RequestSend/Recv`, `ResponseSend/Recv`). Supports client streaming, server streaming, and bidirectional streaming.
+
+## Workspace Support (`workspace.rs`)
+
+Supports code generation for multi-crate workspaces via `volo.workspace.yml`. Use `workspace::Builder::thrift().gen()` or `workspace::Builder::protobuf().gen()`.
+
+## Notes
+
+1. **OUT_DIR**: Must be run in `build.rs`; depends on the `OUT_DIR` environment variable.
+2. **Git Operations**: Requires system `git` CLI installed.
+3. **Config Migration**: Legacy configuration formats need migration to the new format. See https://www.cloudwego.io/docs/volo/guide/config/
+4. **Split Files**: Enabling `split_generated_files` generates multiple files, suitable for large projects.
diff --git a/volo-cli/CLAUDE.md b/volo-cli/CLAUDE.md
@@ -0,0 +1,76 @@
+# CLAUDE.md - volo-cli
+
+## Project Overview
+
+`volo-cli` is the command line tool for the Volo framework, used for creating and managing Volo-based RPC and HTTP service projects from IDL files or templates.
+
+## Directory Structure
+
+```
+volo-cli/
+└── src/
+    ├── bin/
+    │   └── volo.rs         # CLI entry point (main function)
+    ├── lib.rs              # Library root, defines macros and exports modules
+    ├── command.rs          # CliCommand trait and define_commands! macro
+    ├── context.rs          # Context struct
+    ├── model.rs            # RootCommand and subcommand definitions
+    ├── init.rs             # `volo init` command implementation
+    ├── http.rs             # `volo http` command implementation
+    ├── migrate.rs          # `volo migrate` command implementation
+    ├── idl/
+    │   ├── mod.rs          # `volo idl` command entry
+    │   └── add.rs          # `volo idl add` subcommand
+    ├── repo/
+    │   ├── mod.rs          # `volo repo` command entry
+    │   ├── add.rs          # `volo repo add` subcommand
+    │   └── update.rs       # `volo repo update` subcommand
+    └── templates/          # Project template files
+        ├── thrift/         # Thrift project templates
+        ├── grpc/           # gRPC project templates
+        └── http/           # HTTP project templates
+```
+
+## Commands
+
+| Command                    | Module           | Description                                 |
+| -------------------------- | ---------------- | ------------------------------------------- |
+| `volo init <name> <idl>`   | `init.rs`        | Initialize Thrift/gRPC project              |
+| `volo http init <name>`    | `http.rs`        | Initialize HTTP project                     |
+| `volo idl add <idl>`       | `idl/add.rs`     | Add IDL file to existing project            |
+| `volo repo add -g <git>`   | `repo/add.rs`    | Add Git repository as IDL source            |
+| `volo repo update [repos]` | `repo/update.rs` | Update specified or all Git repository IDLs |
+| `volo migrate`             | `migrate.rs`     | Migrate legacy configuration to new format  |
+
+## Key Macros
+
+### `define_commands!` (`src/command.rs`)
+
+Batch-defines subcommand enums and auto-implements the `CliCommand` trait, simplifying command dispatch logic. All commands implement the `CliCommand` trait (`fn run(&self, cx: Context) -> anyhow::Result<()>`).
+
+### `templates_to_target_file!` (`src/lib.rs`)
+
+Outputs template files to a target path with parameter substitution:
+
+```rust
+templates_to_target_file!(folder, "templates/thrift/cargo_toml", "Cargo.toml", name = &name);
+```
+
+## Project Templates
+
+- **Thrift** (`templates/thrift/`): Standard Thrift RPC project with `volo-gen` sub-crate for code generation
+- **gRPC** (`templates/grpc/`): Protobuf-based gRPC project, similar structure to Thrift
+- **HTTP** (`templates/http/`): Pure HTTP project using `volo-http` Router pattern, no `volo-gen` sub-crate
+
+## Logging
+
+- Default log level is `WARN`
+- Use `-v` to raise to `INFO`, `-vv` for `DEBUG`, `-vvv` for `TRACE`
+- Version update check runs at startup; disable with env var `VOLO_DISABLE_UPDATE_CHECK`
+
+## Notes
+
+1. The init command checks if `volo.yml` already exists to avoid overwriting existing configuration
+2. IDL protocol must be consistent with existing entry configuration (cannot mix Thrift and Protobuf)
+3. After initialization, `cargo fmt --all` is automatically run to format generated code
+4. After initialization, Git repository is automatically initialized (if not already present)
diff --git a/volo-grpc/CLAUDE.md b/volo-grpc/CLAUDE.md
@@ -0,0 +1,92 @@
+# CLAUDE.md - volo-grpc
+
+## Overview
+
+`volo-grpc` is the gRPC implementation of the Volo framework, providing async gRPC client and server based on HTTP/2 (hyper). Supports unary, client streaming, server streaming, and bidirectional streaming calls with gzip/zlib/zstd compression, gRPC-Web, and TLS.
+
+**Documentation:** https://docs.rs/volo-grpc
+
+## Directory Structure
+
+```
+volo-grpc/src/
+├── lib.rs              # Public API exports
+├── body.rs             # BoxBody type
+├── codegen.rs          # Code generation helpers
+├── context.rs          # ClientContext, ServerContext (RpcInfo, stats, extensions)
+├── message.rs          # RecvEntryMessage, SendEntryMessage traits (prost::Message)
+├── request.rs          # Request<T> wrapper (metadata + message/Streaming)
+├── response.rs         # Response<T> wrapper (metadata + message/Streaming)
+├── status.rs           # gRPC Status (code, message, details, metadata) and Code enum
+├── tracing.rs          # Span provider
+├── client/             # ClientBuilder, Client ("clone and use" pattern)
+│   ├── callopt.rs      # Per-call options (CallOpt)
+│   ├── dns.rs          # DNS resolution
+│   ├── meta.rs         # MetaService (metadata handling)
+│   └── layer/timeout.rs
+├── server/             # Server, Router, ServiceBuilder, NamedService
+│   ├── router.rs       # Multi-service routing
+│   ├── service.rs      # ServiceBuilder::new(svc).build()
+│   ├── incoming.rs     # Connection acceptance
+│   ├── meta.rs         # MetaService
+│   └── layer/timeout.rs
+├── codec/              # Codec trait, encode/decode, compression (gzip/zlib/zstd)
+├── metadata/           # MetadataMap, MetadataKey, MetadataValue (binary keys use `-bin` suffix)
+├── layer/              # Shared layers: loadbalance, grpc_timeout, grpc_web, user_agent, CORS
+└── transport/          # Client transport, connection, TLS config
+```
+
+## Key Components
+
+**Client** -- `ClientBuilder` configures: `rpc_timeout`, `connect_timeout`, `discover`, `load_balance`, `layer`/`layer_front`, `compression`.
+
+**Server** -- Built on hyper HTTP/2. Methods: `add_service`, `layer`/`layer_front`/`layer_tower`, `run`/`run_with_shutdown`, `tls_config`, plus HTTP/2 tuning options.
+
+**Router** -- Supports multiple gRPC services via `add_service`:
+
+```rust
+Server::new()
+    .add_service(ServiceBuilder::new(service_a).build())
+    .add_service(ServiceBuilder::new(service_b).build())
+    .run(addr).await?;
+```
+
+**NamedService** -- Services implement this trait (provides `const NAME`) for routing.
+
+**Codec** -- Encoder/Decoder abstraction. Compression: gzip and zlib enabled by default, zstd optional.
+
+**Metadata** -- `MetadataMap` stores key-value pairs. Binary keys use `-bin` suffix.
+
+## Feature Flags
+
+| Feature               | Description              |
+| --------------------- | ------------------------ |
+| `default`             | Enables gzip and zlib    |
+| `gzip`                | gzip compression         |
+| `zlib`                | zlib compression         |
+| `zstd`                | zstd compression         |
+| `compress`            | Compression base support |
+| `rustls`              | Rustls TLS               |
+| `native-tls`          | Native TLS               |
+| `native-tls-vendored` | Vendored Native TLS      |
+| `grpc-web`            | gRPC-Web support         |
+
+## HTTP/2 Configuration Options
+
+Server HTTP/2 settings:
+
+- `http2_init_stream_window_size` / `http2_init_connection_window_size` (default 1MB)
+- `http2_adaptive_window`
+- `http2_max_concurrent_streams`
+- `http2_keepalive_interval` / `http2_keepalive_timeout` (default 20s)
+- `http2_max_frame_size`
+- `http2_max_send_buf_size`
+- `http2_max_header_list_size` (default 16MB)
+- `accept_http1`: Accept HTTP/1 (required for gRPC-Web)
+
+## Notes
+
+1. **Users should not use volo-grpc directly**: Use code generated by `volo-build`
+2. **gRPC-Web requires additional configuration**: Enable `grpc-web` feature and set `accept_http1(true)`
+3. **Compression is optional**: gzip and zlib enabled by default, zstd requires manual enabling
+4. **TLS requires backend selection**: rustls or native-tls
diff --git a/volo-http/CLAUDE.md b/volo-http/CLAUDE.md
@@ -0,0 +1,95 @@
+# volo-http
+
+High-performance async HTTP client and server framework built on the Volo ecosystem, using `motore` service abstractions and `hyper` for HTTP transport.
+
+## Directory Structure
+
+```
+volo-http/src/
+├── lib.rs              # Crate entry, module exports, prelude
+├── body.rs             # Body type (Full, Incoming, Stream, BoxBody) and BodyConversion trait
+├── request.rs          # Request type aliases and utilities
+├── response.rs         # Response type alias
+├── context/            # RPC contexts
+│   ├── client.rs       # ClientContext (target, stats, timeout)
+│   └── server.rs       # ServerContext (RpcInfo, path params, extensions)
+├── error/
+│   ├── client.rs       # ClientError
+│   └── server.rs       # ExtractBodyError
+├── utils/              # Shared utilities (consts, cookie, extension, json, macros)
+├── server/
+│   ├── mod.rs          # Server struct
+│   ├── handler.rs      # Handler trait
+│   ├── extract.rs      # FromContext, FromRequest extractors
+│   ├── middleware.rs    # from_fn, map_response
+│   ├── param.rs        # PathParams, PathParamsMap, PathParamsVec
+│   ├── panic_handler.rs
+│   ├── protocol.rs     # HTTP1/HTTP2 config
+│   ├── span_provider.rs
+│   ├── route/          # Router, MethodRouter, Route, Fallback
+│   ├── response/       # IntoResponse, Redirect, SSE
+│   ├── layer/          # BodyLimitLayer, FilterLayer, TimeoutLayer
+│   └── utils/          # client_ip, file_response, serve_dir, multipart, ws
+└── client/
+    ├── mod.rs          # Client, ClientBuilder
+    ├── request_builder.rs
+    ├── callopt.rs      # Per-request call options
+    ├── cookie.rs       # Cookie jar (feature: cookie)
+    ├── dns.rs          # DNS resolver
+    ├── loadbalance.rs
+    ├── target.rs       # Request target (address/host)
+    ├── layer/          # Timeout, Host, UserAgent, FailOnStatus, HttpProxy
+    └── transport/      # Connector, HTTP1/2, connection pool, TLS
+```
+
+## Key Components
+
+### Body
+
+`Body` wraps `Full<Bytes>`, `Incoming`, `Stream`, or `BoxBody`. The `BodyConversion` trait provides `into_bytes()`, `into_vec()`, `into_string()`, `into_faststr()`, and `into_json<T>()`.
+
+### Server
+
+**Routing**: `Router` maps paths to `MethodRouter`s. Supports `.route()`, `.nest()`, `.fallback()`. `MethodRouter` dispatches by HTTP method (`get`, `post`, etc.).
+
+**Handlers**: Async functions with extractors as parameters. Extractors implement `FromContext` (non-consuming, from context/parts) or `FromRequest` (consuming, includes body -- must be last parameter). Return types implement `IntoResponse`.
+
+**Built-in extractors**:
+
+- From context: `Uri`, `Method`, `Address`, `HeaderMap`, `PathParams<T>`, `PathParamsMap`, `PathParamsVec`, `Query<T>`, `Extension<T>`
+- From body: `Json<T>`, `Form<T>`, `Bytes`, `String`, `Vec<u8>`, `Request<B>`, `Multipart`, `WebSocketUpgrade`
+
+**Middleware**: `from_fn` wraps an async function with `(cx, req, next) -> Response` signature. `map_response` transforms responses. Apply via `.layer()` on `Router` or `MethodRouter`.
+
+**Server layers**: `BodyLimitLayer`, `FilterLayer`, `TimeoutLayer`
+
+### Client
+
+`ClientBuilder` configures and builds a `Client` with connection pooling, timeouts, and DNS resolution. `RequestBuilder` (via `client.get()`, `.post()`, etc.) builds individual requests with headers, JSON body, etc.
+
+**Client layers**: `Timeout`, `Host`, `UserAgent`, `FailOnStatus`, `HttpProxy`
+
+## Feature Flags
+
+```toml
+default = ["default-client", "default-server"]
+default-client = ["client", "http1", "json"]
+default-server = ["server", "http1", "query", "form", "json", "multipart"]
+```
+
+| Feature           | Description                                   |
+| ----------------- | --------------------------------------------- |
+| `client`          | HTTP client support                           |
+| `server`          | HTTP server support                           |
+| `http1`           | HTTP/1.1 protocol                             |
+| `http2`           | HTTP/2 protocol                               |
+| `query`           | Query string extraction (requires serde)      |
+| `form`            | Form body extraction (requires serde)         |
+| `json`            | JSON body extraction/response (uses sonic-rs) |
+| `json-utf8-lossy` | Lossy UTF-8 handling for JSON                 |
+| `cookie`          | Cookie support for client and server          |
+| `multipart`       | Multipart form data support                   |
+| `ws`              | WebSocket support                             |
+| `tls` / `rustls`  | TLS via rustls                                |
+| `native-tls`      | TLS via native-tls                            |
+| `full`            | All features enabled                          |
diff --git a/volo-macros/CLAUDE.md b/volo-macros/CLAUDE.md
@@ -0,0 +1,14 @@
+# CLAUDE.md - volo-macros
+
+## Overview
+
+`volo-macros` is a **reserved placeholder** crate for future procedural macros. It contains no active functionality.
+
+Actual macros used in the Volo ecosystem live elsewhere:
+
+- `#[service]` macro: provided by `motore`, re-exported via `volo`
+- Declarative macros (`volo_unreachable!`, `new_type!`): defined in `volo/src/macros.rs`
+
+## Release Order
+
+`volo-macros` must be published **first** when releasing new versions (see root CLAUDE.md).
diff --git a/volo-thrift/CLAUDE.md b/volo-thrift/CLAUDE.md
@@ -0,0 +1,114 @@
+# CLAUDE.md - volo-thrift
+
+`volo-thrift` is the Thrift RPC implementation of the Volo project, providing high-performance async Thrift client and server. Core features include TTHeader protocol (CloudWeGo proprietary for Volo/Kitex interop), Framed transport, Binary/Compact protocols, connection pooling, multi-service routing, BizError support, optional multiplex mode, and optional shmipc transport.
+
+## Directory Structure
+
+```
+volo-thrift/src/
+├── lib.rs              # Library entry, exports public API
+├── error.rs            # Error types (ServerError, ClientError, BizError)
+├── message.rs          # EntryMessage trait
+├── message_wrapper.rs  # ThriftMessage wrapper
+├── context.rs          # ClientContext, ServerContext, Config
+├── protocol/           # Re-exports pilota protocol types
+├── tracing.rs          # Tracing/Span provider
+├── client/
+│   ├── mod.rs          # ClientBuilder, Client, MessageService
+│   ├── callopt.rs      # Call-time options (CallOpt)
+│   └── layer/          # Client middleware (timeout)
+├── server/
+│   ├── mod.rs          # Server struct and core logic
+│   ├── router.rs       # Multi-service router (Router)
+│   ├── panic_handler.rs
+│   └── layer/          # Server middleware (biz_error)
+├── codec/
+│   ├── mod.rs          # Encoder, Decoder, MakeCodec traits
+│   └── default/        # DefaultMakeCodec, ZeroCopyEncoder/Decoder
+│       ├── thrift.rs   # Thrift protocol encoding/decoding
+│       ├── framed.rs   # Framed transport layer
+│       └── ttheader.rs # TTHeader protocol
+└── transport/
+    ├── incoming.rs     # Connection acceptance
+    ├── pingpong/       # Ping-Pong mode (default)
+    ├── multiplex/      # Multiplex mode (feature: multiplex)
+    └── pool/           # Connection pool
+```
+
+## Key Modules
+
+### Client
+
+`ClientBuilder` configures and constructs the `Client`. Key options:
+
+- `rpc_timeout` (default 1s), `connect_timeout` (default 50ms), `read_write_timeout` (default 1s)
+- `pool_config`, `discover`, `load_balance`
+- `layer_inner` / `layer_outer` for middleware
+
+`Client` is designed for clone-and-use with low clone cost. `CallOpt` overrides config per call.
+
+### Server and Router
+
+`Server` supports `layer` / `layer_front` for middleware, `multiplex` mode (requires feature), and graceful shutdown via `register_shutdown_hook`.
+
+`Router` enables multi-service hosting on a single server. Routing uses the `isn` (IDL Service Name) field in TTHeader. Services implement `NamedService` (provides `const NAME`) for routing support. The default service handles requests without a matching ISN.
+
+### Context
+
+`ClientContext` / `ServerContext` contain `RpcInfo` (caller, callee, method, config), `seq_id`, `message_type`, `stats`, `transport` info, and `idl_service_name` for routing. `Config` holds timeout settings. Both implement the `ThriftContext` trait.
+
+### Codec Stack
+
+Default codec: `TTHeader<Framed<Binary>>`
+
+Available configurations:
+- `DefaultMakeCodec::framed()` -- `Framed<Binary>`
+- `DefaultMakeCodec::ttheader_framed()` -- `TTHeader<Framed<Binary>>`
+- `DefaultMakeCodec::buffered()` -- Pure Binary (no framing)
+
+### TTHeader Protocol
+
+CloudWeGo proprietary protocol supporting:
+- Metadata propagation (persistent/transient/backward)
+- RPC timeout passing
+- Business error passing (biz-status, biz-message, biz-extra)
+- Connection reset notification (crrst)
+- IDL service name (isn) for multi-service routing
+
+### Transport Modes
+
+- **Ping-Pong (default):** One request per connection at a time; next request waits for current to complete.
+- **Multiplex (feature: `multiplex`):** Concurrent requests on a single connection, matched by sequence number. Not compatible with shmipc.
+
+### Connection Pool
+
+Based on hyper connection pool design. Defaults: `max_idle_per_key` = 10240, `timeout` = 15 seconds.
+
+### Error Types
+
+- `ServerError`: `Application(ApplicationException)` | `Biz(BizError)`
+- `ClientError`: `Application(ApplicationException)` | `Transport(TransportException)` | `Protocol(ProtocolException)` | `Biz(BizError)`
+- `BizError`: Business error with `status_code`, `status_message`, and optional `extra` map, passed via TTHeader.
+
+## Feature Flags
+
+| Feature            | Description                                                           |
+| ------------------ | --------------------------------------------------------------------- |
+| `multiplex`        | Enable multiplex mode (unstable, no backward compatibility guarantee) |
+| `unsafe-codec`     | Use unsafe codec for better performance (may cause UB)                |
+| `unsafe_unchecked` | Use `unwrap_unchecked` instead of `unwrap`                            |
+| `shmipc`           | Enable shared memory IPC transport                                    |
+
+## Architecture Layer Structure
+
+**Client:** `OuterLayers -> Timeout -> LoadBalance -> InnerLayers -> Transport`
+
+**Server:** `Layers -> BizErrorLayer -> Service`
+
+## Notes
+
+1. **Users should not use volo-thrift directly**: Use code generated by `volo-build`
+2. **TTHeader is a proprietary protocol**: Only for Volo/Kitex inter-service communication
+3. **Multiplex mode is unstable**: May change in future versions
+4. **unsafe-codec is risky**: May cause undefined behavior
+5. **shmipc does not support multiplex**: Cannot be used together
diff --git a/volo/CLAUDE.md b/volo/CLAUDE.md
@@ -0,0 +1,89 @@
+# CLAUDE.md - Volo Core Crate
+
+## Overview
+
+`volo` is the core foundation library providing shared abstractions (service discovery, load balancing, network transport, context management) used by `volo-thrift`, `volo-grpc`, and `volo-http`.
+
+## Directory Structure
+
+```
+volo/src/
+├── lib.rs              # Library entry, exports public API
+├── client.rs           # Client service trait definitions (ClientService, OneShotService, MkClient)
+├── context.rs          # RPC context and metadata (RpcCx, RpcInfo, Endpoint, Role)
+├── hack.rs             # Unsafe optimization tools (conditional compilation)
+├── macros.rs           # Utility macro definitions
+│
+├── catch_panic/        # Panic capture layer for services
+├── discovery/          # Service discovery (Discover trait, Instance, StaticDiscover)
+├── hotrestart/         # Hot restart support (Unix only)
+│
+├── loadbalance/        # Load balancing
+│   ├── mod.rs          # LoadBalance trait, LbConfig
+│   ├── layer.rs        # LoadBalanceLayer (motore Layer)
+│   ├── error.rs        # LoadBalanceError (Retry, Discover, MissRequestHash)
+│   ├── random.rs       # WeightedRandomBalance
+│   └── consistent_hash.rs  # ConsistentHashBalance (requires RequestHash)
+│
+├── net/                # Network transport layer
+│   ├── mod.rs          # Address enum (Ip, Unix, Shmipc)
+│   ├── conn.rs         # ConnStream, Conn, OwnedReadHalf/OwnedWriteHalf
+│   ├── dial.rs         # Client connection establishment (MakeTransport)
+│   ├── incoming.rs     # Server connection acceptance (MakeIncoming, Incoming)
+│   ├── ext.rs          # AsyncExt trait (check IO ready state)
+│   ├── probe.rs        # IPv4/IPv6 network probing
+│   ├── tls/            # TLS support (TlsConnector, TlsAcceptor, ClientTlsConfig, ServerTlsConfig)
+│   └── shmipc/         # Shared memory IPC transport (optional)
+│
+└── util/
+    ├── mod.rs          # Ref<'a, B> - borrowed reference or Arc
+    ├── buf_reader.rs   # BufReader with compact() and fill_buf_at_least()
+    └── remote_error.rs # Remote connection error detection
+```
+
+## Key Modules
+
+### Service Discovery (`discovery`)
+
+`Discover` trait for resolving service endpoints to instances. Built-in implementations: `StaticDiscover`, `WeightedStaticDiscover`, `DummyDiscover`.
+
+### Load Balancing (`loadbalance`)
+
+`LoadBalance` trait for selecting instances. Strategies: `WeightedRandomBalance`, `ConsistentHashBalance`. Applied via `LoadBalanceLayer`.
+
+### Context (`context`)
+
+`RpcCx<I, Config>` wraps `RpcInfo` (role, method, caller/callee endpoints). `newtype_impl_context!` macro implements the `Context` trait for newtypes.
+
+### Network (`net`)
+
+Unified transport abstraction. `Address` enum supports TCP (`Ip`), Unix sockets (`Unix`), and shared memory (`Shmipc`). `ConnStream` enum wraps all connection types.
+
+### Hot Restart (`hotrestart`, Unix only)
+
+Zero-downtime restarts via Unix Domain Socket. Parent passes listening socket FDs to child process via `SCM_RIGHTS`, then child signals parent to terminate. Global instance: `DEFAULT_HOT_RESTART`.
+
+### Panic Capture (`catch_panic`)
+
+Layer that catches panics in service calls. `Handler` trait defines custom panic handling. `PanicInfo` provides message, location, and stack trace.
+
+## Important Notes
+
+- **`VOLO_ENABLE_REMOTE_CLOSED_ERROR_LOG`**: Environment variable that controls whether remote connection closed errors are logged (see `util/remote_error.rs`).
+- **`volo_unreachable!()`**: Macro that becomes `unreachable_unchecked()` when the `unsafe_unchecked` feature is enabled; otherwise a normal `unreachable!()`.
+- **`new_type!`**: Macro for defining newtype wrappers with common trait implementations.
+- **`volo::spawn()`**: Spawns a tokio task that automatically derives `metainfo` context.
+
+## Feature Flags
+
+| Feature               | Description                                               |
+| --------------------- | --------------------------------------------------------- |
+| `unsafe_unchecked`    | Use `unwrap_unchecked` instead of `unwrap` (optimization) |
+| `tls` / `rustls`      | Equivalent to `rustls-aws-lc-rs`                          |
+| `rustls-aws-lc-rs`    | Rustls with AWS LC crypto backend                         |
+| `rustls-ring`         | Rustls with Ring crypto backend                           |
+| `native-tls`          | System native TLS (OpenSSL/Secure Transport/SChannel)     |
+| `native-tls-vendored` | Use vendored OpenSSL                                      |
+| `shmipc`              | Enable shared memory IPC transport                        |
+
+No default features are enabled.
PATCH

echo "Gold patch applied."
