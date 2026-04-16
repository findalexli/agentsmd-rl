# Fix rustls crypto provider initialization in chroma-tracing

## Symptom

The `chroma-tracing` crate panics at runtime when initializing OTLP TLS
configuration. The error message is "no crypto provider installed" or
similar. This happens because multiple dependencies in the workspace use
rustls, but no crypto provider is explicitly installed before TLS config
is built.

## Verification

The fix must satisfy ALL of the following checks:

### Build checks (pass-to-pass)

After the fix is applied, these commands must succeed:

```bash
cargo check -p chroma-tracing
cargo fmt --check --package chroma-tracing
cargo clippy --package chroma-tracing
cargo test --doc --package chroma-tracing
```

### Configuration requirements (fail-to-pass)

**Workspace Cargo.toml** must declare:
- A rustls dependency at version `0.23.37`
- With the `aws-lc-rs` feature enabled

**chroma-tracing Cargo.toml** must have:
- rustls as a workspace dependency

### Source code requirements

The source file that initializes OTLP tracing must contain:
- A function that installs a rustls crypto provider using the aws-lc-rs backend
- The API call: `rustls::crypto::aws_lc_rs::default_provider().install_default()`
- This function must be invoked before any TLS client config is built

### Required comment

The code must include a comment explaining why the provider installation
is necessary. The comment must convey that:
- Multiple dependencies in the workspace enable different rustls backends
- One must be installed explicitly before any TLS client config is built

## Notes

The crypto provider must be initialized before the OTLP tracer sets up
its TLS configuration. The exact function name and implementation approach
are flexible, but the required API call pattern and comment text must be
present.